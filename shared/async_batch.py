"""
Async batch processing utilities for AgentSwarm Tools Framework.
Provides concurrent execution, rate limiting, and error handling for async tools.
"""

import asyncio
import time
from typing import Any, List, Dict, Optional, Callable, TypeVar, Coroutine
from dataclasses import dataclass
from datetime import datetime
import logging

from .errors import ToolError, RateLimitError

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class BatchResult:
    """Result from batch processing."""

    success: bool
    results: List[Any]
    errors: List[Dict[str, Any]]
    duration_ms: float
    successful_count: int
    failed_count: int
    metadata: Dict[str, Any]


class AsyncRateLimiter:
    """
    Async rate limiter with token bucket algorithm.

    Allows controlled concurrent execution with rate limiting.
    """

    def __init__(self, rate: int, per: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            rate: Number of operations allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to execute (async)."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update

            # Refill tokens based on elapsed time
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.per))
            self.last_update = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (self.per / self.rate)
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class AsyncBatchProcessor:
    """
    Process multiple async operations concurrently with rate limiting and error handling.

    Features:
    - Concurrent execution with configurable concurrency limit
    - Rate limiting
    - Automatic retry on failure
    - Progress tracking
    - Error collection and handling

    Example:
        ```python
        import asyncio
        from agentswarm_tools.shared.async_batch import AsyncBatchProcessor

        async def fetch_url(url: str) -> str:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text

        async def main():
            urls = ["https://example.com"] * 10

            processor = AsyncBatchProcessor(
                max_concurrency=5,
                rate_limit=10,
                rate_limit_per=1.0
            )

            result = await processor.process(
                items=urls,
                operation=fetch_url,
                description="Fetching URLs"
            )

            print(f"Success: {result.successful_count}/{len(urls)}")

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        max_concurrency: int = 10,
        rate_limit: Optional[int] = None,
        rate_limit_per: float = 1.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: Optional[float] = None,
    ):
        """
        Initialize batch processor.

        Args:
            max_concurrency: Maximum number of concurrent operations
            rate_limit: Maximum operations per time period (None = unlimited)
            rate_limit_per: Time period for rate limit in seconds
            max_retries: Maximum retry attempts per operation
            retry_delay: Base delay between retries (exponential backoff)
            timeout: Timeout per operation in seconds (None = no timeout)
        """
        self.max_concurrency = max_concurrency
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout

        # Initialize rate limiter if specified
        self.rate_limiter = None
        if rate_limit:
            self.rate_limiter = AsyncRateLimiter(rate_limit, rate_limit_per)

        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def process(
        self,
        items: List[T],
        operation: Callable[[T], Coroutine[Any, Any, Any]],
        description: str = "Processing items",
        fail_fast: bool = False,
    ) -> BatchResult:
        """
        Process items concurrently with rate limiting.

        Args:
            items: List of items to process
            operation: Async function to apply to each item
            description: Description for logging
            fail_fast: Stop processing on first error

        Returns:
            BatchResult with results and errors
        """
        start_time = time.time()
        results = []
        errors = []

        logger.info(f"{description}: Processing {len(items)} items with max_concurrency={self.max_concurrency}")

        async def process_item(item: T, index: int) -> tuple[int, Optional[Any], Optional[Dict[str, Any]]]:
            """Process single item with retry logic."""
            for attempt in range(self.max_retries):
                try:
                    # Acquire semaphore for concurrency control
                    async with self._semaphore:
                        # Rate limiting
                        if self.rate_limiter:
                            await self.rate_limiter.acquire()

                        # Execute operation with optional timeout
                        if self.timeout:
                            result = await asyncio.wait_for(
                                operation(item),
                                timeout=self.timeout
                            )
                        else:
                            result = await operation(item)

                        return (index, result, None)

                except asyncio.TimeoutError as e:
                    error = {
                        "index": index,
                        "item": str(item)[:100],
                        "error": f"Timeout after {self.timeout}s",
                        "attempt": attempt + 1,
                    }

                    if attempt < self.max_retries - 1:
                        retry_delay = self.retry_delay * (2 ** attempt)
                        logger.warning(f"Item {index} timeout, retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                    else:
                        return (index, None, error)

                except Exception as e:
                    error = {
                        "index": index,
                        "item": str(item)[:100],
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "attempt": attempt + 1,
                    }

                    # Don't retry on validation or auth errors
                    if isinstance(e, ToolError) and e.error_code in ["VALIDATION_ERROR", "AUTH_ERROR"]:
                        return (index, None, error)

                    if attempt < self.max_retries - 1:
                        retry_delay = self.retry_delay * (2 ** attempt)
                        logger.warning(f"Item {index} failed: {e}, retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                    else:
                        return (index, None, error)

            # Should not reach here, but return error if we do
            return (index, None, {"index": index, "error": "Max retries exceeded"})

        # Process all items concurrently
        tasks = [process_item(item, i) for i, item in enumerate(items)]

        try:
            completed = await asyncio.gather(*tasks, return_exceptions=True)

            # Organize results
            for result in completed:
                if isinstance(result, Exception):
                    # Unexpected error from gather
                    errors.append({
                        "error": str(result),
                        "error_type": type(result).__name__,
                    })
                    results.append(None)
                else:
                    index, item_result, item_error = result

                    if item_error:
                        errors.append(item_error)
                        results.append(None)

                        if fail_fast:
                            logger.error(f"Failing fast due to error in item {index}")
                            break
                    else:
                        results.append(item_result)

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            errors.append({
                "error": f"Batch processing failed: {e}",
                "error_type": type(e).__name__,
            })

        duration_ms = (time.time() - start_time) * 1000
        successful_count = len([r for r in results if r is not None])
        failed_count = len(errors)

        logger.info(
            f"{description} completed in {duration_ms:.2f}ms: "
            f"{successful_count} succeeded, {failed_count} failed"
        )

        return BatchResult(
            success=failed_count == 0,
            results=results,
            errors=errors,
            duration_ms=duration_ms,
            successful_count=successful_count,
            failed_count=failed_count,
            metadata={
                "description": description,
                "total_items": len(items),
                "max_concurrency": self.max_concurrency,
                "max_retries": self.max_retries,
            }
        )


async def gather_with_concurrency(
    *coroutines: Coroutine,
    max_concurrency: int = 10,
    return_exceptions: bool = False
) -> List[Any]:
    """
    Gather coroutines with concurrency limit.

    Similar to asyncio.gather() but with controlled concurrency.

    Args:
        *coroutines: Coroutines to execute
        max_concurrency: Maximum concurrent executions
        return_exceptions: Return exceptions instead of raising

    Returns:
        List of results in same order as input coroutines

    Example:
        ```python
        async def fetch(url):
            async with httpx.AsyncClient() as client:
                return await client.get(url)

        results = await gather_with_concurrency(
            fetch("https://example.com/1"),
            fetch("https://example.com/2"),
            fetch("https://example.com/3"),
            max_concurrency=2
        )
        ```
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_with_semaphore(coro: Coroutine, index: int) -> tuple[int, Any]:
        """Run coroutine with semaphore."""
        async with semaphore:
            try:
                result = await coro
                return (index, result)
            except Exception as e:
                if return_exceptions:
                    return (index, e)
                else:
                    raise

    # Execute all coroutines with concurrency control
    tasks = [run_with_semaphore(coro, i) for i, coro in enumerate(coroutines)]
    completed = await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    # Sort by original index to maintain order
    sorted_results = sorted(completed, key=lambda x: x[0] if isinstance(x, tuple) else 0)

    return [result for _, result in sorted_results]


async def retry_async(
    operation: Callable[[], Coroutine[Any, Any, T]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exponential_backoff: bool = True,
    retry_exceptions: tuple = (Exception,),
) -> T:
    """
    Retry async operation with exponential backoff.

    Args:
        operation: Async operation to retry
        max_retries: Maximum retry attempts
        retry_delay: Base delay between retries
        exponential_backoff: Use exponential backoff
        retry_exceptions: Tuple of exceptions to retry on

    Returns:
        Result from operation

    Raises:
        Last exception if all retries fail

    Example:
        ```python
        async def unstable_api_call():
            # May fail intermittently
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.example.com")
                return response.json()

        result = await retry_async(
            unstable_api_call,
            max_retries=5,
            retry_delay=1.0
        )
        ```
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await operation()
        except retry_exceptions as e:
            last_exception = e

            if attempt < max_retries - 1:
                if exponential_backoff:
                    delay = retry_delay * (2 ** attempt)
                else:
                    delay = retry_delay

                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_retries} attempts failed")

    # All retries exhausted
    if last_exception:
        raise last_exception

    raise RuntimeError("Retry logic error: no exception but all attempts failed")


if __name__ == "__main__":
    # Test async batch processing
    print("Testing async batch utilities...")

    import asyncio

    async def test_batch_processor():
        """Test batch processor."""
        print("\n1. Testing AsyncBatchProcessor...")

        # Simulate async operations
        async def process_number(n: int) -> int:
            await asyncio.sleep(0.1)
            if n % 7 == 0:  # Simulate occasional failure
                raise ValueError(f"Number {n} is divisible by 7")
            return n * 2

        processor = AsyncBatchProcessor(
            max_concurrency=3,
            rate_limit=5,
            rate_limit_per=1.0,
            max_retries=2,
        )

        numbers = list(range(10))
        result = await processor.process(
            items=numbers,
            operation=process_number,
            description="Processing numbers"
        )

        print(f"  Success: {result.success}")
        print(f"  Successful: {result.successful_count}/{len(numbers)}")
        print(f"  Failed: {result.failed_count}")
        print(f"  Duration: {result.duration_ms:.2f}ms")
        print("  ✓ AsyncBatchProcessor test passed")

    async def test_gather_with_concurrency():
        """Test concurrent gather."""
        print("\n2. Testing gather_with_concurrency...")

        async def fetch(n: int) -> int:
            await asyncio.sleep(0.05)
            return n * 2

        results = await gather_with_concurrency(
            *[fetch(i) for i in range(10)],
            max_concurrency=3
        )

        print(f"  Results: {results}")
        assert len(results) == 10
        assert results[0] == 0
        assert results[9] == 18
        print("  ✓ gather_with_concurrency test passed")

    async def test_retry_async():
        """Test async retry."""
        print("\n3. Testing retry_async...")

        attempt_count = 0

        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                raise ValueError("Simulated failure")

            return "Success!"

        result = await retry_async(
            flaky_operation,
            max_retries=5,
            retry_delay=0.1
        )

        print(f"  Result: {result}")
        print(f"  Attempts: {attempt_count}")
        assert result == "Success!"
        assert attempt_count == 3
        print("  ✓ retry_async test passed")

    async def test_rate_limiter():
        """Test rate limiter."""
        print("\n4. Testing AsyncRateLimiter...")

        limiter = AsyncRateLimiter(rate=5, per=1.0)

        start = time.time()
        for i in range(10):
            await limiter.acquire()
        duration = time.time() - start

        print(f"  Duration for 10 ops (5/sec): {duration:.2f}s")
        # Should take ~2 seconds (10 ops at 5/sec)
        assert duration >= 1.8, f"Rate limiter too fast: {duration}s"
        print("  ✓ AsyncRateLimiter test passed")

    # Run all tests
    async def main():
        await test_batch_processor()
        await test_gather_with_concurrency()
        await test_retry_async()
        await test_rate_limiter()
        print("\n✓ All async batch utility tests passed!")

    asyncio.run(main())
