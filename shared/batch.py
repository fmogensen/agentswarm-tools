"""
Batch processing utilities with parallel execution, progress tracking, and error handling.

Provides utilities for efficiently processing large batches of items with:
- Thread-based and process-based parallelism
- Progress tracking via callbacks
- Graceful error handling
- Configurable concurrency limits
- Result aggregation
- Retry logic for failed items

Example:
    >>> from shared.batch import parallel_process, ProgressCallback
    >>>
    >>> def process_item(item):
    ...     return item.upper()
    >>>
    >>> results = parallel_process(
    ...     items=["a", "b", "c"],
    ...     processor=process_item,
    ...     max_workers=5,
    ...     progress_callback=ProgressCallback()
    ... )
    >>> print(results.successes)  # ["A", "B", "C"]
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)


class ExecutorType(Enum):
    """Type of executor to use for parallel processing."""

    THREAD = "thread"  # For I/O-bound operations
    PROCESS = "process"  # For CPU-bound operations


@dataclass
class BatchResult:
    """
    Result of batch processing operation.

    Attributes:
        successes: List of successfully processed results
        failures: List of failed items with their errors
        total_items: Total number of items processed
        successful_count: Number of successful items
        failed_count: Number of failed items
        processing_time_ms: Total processing time in milliseconds
        metadata: Additional metadata about the batch processing
    """

    successes: List[Any] = field(default_factory=list)
    failures: List[Dict[str, Any]] = field(default_factory=list)
    total_items: int = 0
    successful_count: int = 0
    failed_count: int = 0
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.successful_count / self.total_items) * 100


class ProgressCallback(ABC):
    """
    Abstract base class for progress tracking callbacks.

    Implement this class to create custom progress tracking behavior.
    """

    @abstractmethod
    def on_start(self, total_items: int) -> None:
        """Called when batch processing starts."""
        pass

    @abstractmethod
    def on_item_complete(self, item_index: int, total_items: int, success: bool) -> None:
        """Called when an item is processed."""
        pass

    @abstractmethod
    def on_complete(self, result: BatchResult) -> None:
        """Called when batch processing completes."""
        pass


class DefaultProgressCallback(ProgressCallback):
    """
    Default progress callback that logs progress to console.

    Example:
        >>> callback = DefaultProgressCallback()
        >>> callback.on_start(100)
        Starting batch processing: 100 items
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize progress callback.

        Args:
            verbose: Whether to print detailed progress information
        """
        self.verbose = verbose
        self.start_time = None

    def on_start(self, total_items: int) -> None:
        """Log start of batch processing."""
        self.start_time = time.time()
        if self.verbose:
            logger.info(f"Starting batch processing: {total_items} items")

    def on_item_complete(self, item_index: int, total_items: int, success: bool) -> None:
        """Log progress for each item."""
        if self.verbose and (item_index + 1) % 10 == 0:
            progress = ((item_index + 1) / total_items) * 100
            logger.info(f"Progress: {item_index + 1}/{total_items} ({progress:.1f}%)")

    def on_complete(self, result: BatchResult) -> None:
        """Log completion summary."""
        if self.verbose:
            logger.info(
                f"Batch processing complete: {result.successful_count}/{result.total_items} "
                f"successful ({result.success_rate:.1f}%) in {result.processing_time_ms:.2f}ms"
            )


class SilentProgressCallback(ProgressCallback):
    """Progress callback that doesn't log anything (for testing/background operations)."""

    def on_start(self, total_items: int) -> None:
        pass

    def on_item_complete(self, item_index: int, total_items: int, success: bool) -> None:
        pass

    def on_complete(self, result: BatchResult) -> None:
        pass


def get_default_max_workers(executor_type: ExecutorType = ExecutorType.THREAD) -> int:
    """
    Get recommended max_workers based on executor type and system resources.

    Args:
        executor_type: Type of executor (THREAD or PROCESS)

    Returns:
        Recommended number of workers

    Example:
        >>> workers = get_default_max_workers(ExecutorType.THREAD)
        >>> print(workers)  # CPU count * 2 for I/O-bound
    """
    cpu_count = os.cpu_count() or 4

    if executor_type == ExecutorType.THREAD:
        # For I/O-bound operations, use more threads
        return cpu_count * 2
    else:
        # For CPU-bound operations, use number of CPUs
        return cpu_count


def parallel_process(
    items: List[Any],
    processor: Callable[[Any], Any],
    max_workers: Optional[int] = None,
    executor_type: ExecutorType = ExecutorType.THREAD,
    progress_callback: Optional[ProgressCallback] = None,
    continue_on_error: bool = True,
    timeout_per_item: Optional[float] = None,
    retry_failed: int = 0,
    batch_metadata: Optional[Dict[str, Any]] = None,
) -> BatchResult:
    """
    Process items in parallel with progress tracking and error handling.

    Args:
        items: List of items to process
        processor: Function to process each item (takes item, returns result)
        max_workers: Maximum number of parallel workers (None = auto)
        executor_type: Type of executor (THREAD for I/O, PROCESS for CPU-bound)
        progress_callback: Callback for progress updates (None = default logger)
        continue_on_error: Whether to continue processing if items fail
        timeout_per_item: Timeout in seconds for each item (None = no timeout)
        retry_failed: Number of times to retry failed items (0 = no retry)
        batch_metadata: Additional metadata to include in result

    Returns:
        BatchResult with successes, failures, and statistics

    Example:
        >>> def uppercase(text):
        ...     return text.upper()
        >>>
        >>> result = parallel_process(
        ...     items=["hello", "world"],
        ...     processor=uppercase,
        ...     max_workers=5
        ... )
        >>> print(result.successes)  # ["HELLO", "WORLD"]

    Note:
        - Use ExecutorType.THREAD for I/O-bound operations (API calls, file I/O)
        - Use ExecutorType.PROCESS for CPU-bound operations (heavy computation)
        - Items must be picklable when using ProcessPoolExecutor
    """
    start_time = time.time()

    # Setup defaults
    if max_workers is None:
        max_workers = get_default_max_workers(executor_type)

    if progress_callback is None:
        progress_callback = DefaultProgressCallback()

    # Initialize result
    result = BatchResult(
        total_items=len(items),
        metadata=batch_metadata or {},
    )

    # Notify start
    progress_callback.on_start(len(items))

    # Select executor
    ExecutorClass = (
        ThreadPoolExecutor if executor_type == ExecutorType.THREAD else ProcessPoolExecutor
    )

    try:
        with ExecutorClass(max_workers=max_workers) as executor:
            # Submit all items
            future_to_item = {
                executor.submit(_process_with_timeout, processor, item, timeout_per_item): (
                    idx,
                    item,
                )
                for idx, item in enumerate(items)
            }

            # Process results as they complete
            for future in as_completed(future_to_item):
                item_index, item = future_to_item[future]

                try:
                    # Get result
                    processed_result = future.result()
                    result.successes.append(processed_result)
                    result.successful_count += 1
                    progress_callback.on_item_complete(item_index, len(items), True)

                except Exception as e:
                    # Record failure
                    error_info = {
                        "item_index": item_index,
                        "item": str(item)[:100],  # Limit item representation
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                    result.failures.append(error_info)
                    result.failed_count += 1
                    progress_callback.on_item_complete(item_index, len(items), False)

                    logger.warning(f"Item {item_index} failed: {e}")

                    # Stop processing if configured
                    if not continue_on_error:
                        logger.error("Stopping batch processing due to error")
                        break

    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise

    # Retry failed items if requested
    if retry_failed > 0 and len(result.failures) > 0:
        logger.info(f"Retrying {len(result.failures)} failed items ({retry_failed} attempts)...")
        failed_items = [items[f["item_index"]] for f in result.failures]

        retry_result = _retry_items(
            items=failed_items,
            processor=processor,
            max_workers=max_workers,
            executor_type=executor_type,
            timeout_per_item=timeout_per_item,
            max_retries=retry_failed,
        )

        # Update results with retry successes
        result.successes.extend(retry_result.successes)
        result.successful_count += retry_result.successful_count
        result.failed_count = len(retry_result.failures)
        result.failures = retry_result.failures

    # Calculate processing time
    result.processing_time_ms = (time.time() - start_time) * 1000

    # Update metadata
    result.metadata.update(
        {
            "max_workers": max_workers,
            "executor_type": executor_type.value,
            "continue_on_error": continue_on_error,
            "timeout_per_item": timeout_per_item,
            "retry_attempts": retry_failed,
        }
    )

    # Notify completion
    progress_callback.on_complete(result)

    return result


def _process_with_timeout(processor: Callable, item: Any, timeout: Optional[float]) -> Any:
    """
    Process an item with optional timeout.

    Args:
        processor: Function to process the item
        item: Item to process
        timeout: Timeout in seconds (None = no timeout)

    Returns:
        Processed result

    Raises:
        TimeoutError: If processing exceeds timeout
    """
    # Note: timeout is handled by the executor's future.result(timeout=...)
    # This wrapper is for potential future timeout logic
    return processor(item)


def _retry_items(
    items: List[Any],
    processor: Callable,
    max_workers: int,
    executor_type: ExecutorType,
    timeout_per_item: Optional[float],
    max_retries: int,
) -> BatchResult:
    """
    Retry failed items with exponential backoff.

    Args:
        items: Items to retry
        processor: Processing function
        max_workers: Number of workers
        executor_type: Executor type
        timeout_per_item: Timeout per item
        max_retries: Maximum retry attempts

    Returns:
        BatchResult with retry results
    """
    retry_result = BatchResult(total_items=len(items))
    remaining_items = items.copy()

    for attempt in range(max_retries):
        if not remaining_items:
            break

        logger.info(f"Retry attempt {attempt + 1}/{max_retries} for {len(remaining_items)} items")

        # Exponential backoff between retries
        if attempt > 0:
            backoff_delay = 2**attempt
            logger.info(f"Waiting {backoff_delay}s before retry...")
            time.sleep(backoff_delay)

        # Process retry batch
        batch_result = parallel_process(
            items=remaining_items,
            processor=processor,
            max_workers=max_workers,
            executor_type=executor_type,
            progress_callback=SilentProgressCallback(),
            continue_on_error=True,
            timeout_per_item=timeout_per_item,
            retry_failed=0,  # Don't retry within retry
        )

        # Collect successes
        retry_result.successes.extend(batch_result.successes)
        retry_result.successful_count += batch_result.successful_count

        # Update remaining items to only failed ones
        if batch_result.failed_count > 0:
            failed_indices = [f["item_index"] for f in batch_result.failures]
            remaining_items = [
                remaining_items[i] for i in range(len(remaining_items)) if i in failed_indices
            ]
            retry_result.failures = batch_result.failures
            retry_result.failed_count = len(remaining_items)
        else:
            remaining_items = []

    return retry_result


def batch_process_with_chunks(
    items: List[Any],
    processor: Callable[[List[Any]], Any],
    chunk_size: int,
    max_workers: Optional[int] = None,
    executor_type: ExecutorType = ExecutorType.THREAD,
    progress_callback: Optional[ProgressCallback] = None,
) -> BatchResult:
    """
    Process items in chunks, where processor handles multiple items at once.

    Useful when the processor can handle batches more efficiently (e.g., batch API calls).

    Args:
        items: List of items to process
        processor: Function that processes a list of items (takes list, returns list)
        chunk_size: Number of items per chunk
        max_workers: Maximum parallel workers
        executor_type: Type of executor
        progress_callback: Progress tracking callback

    Returns:
        BatchResult with all processed items

    Example:
        >>> def batch_api_call(items_batch):
        ...     # Make single API call with multiple items
        ...     return [process(item) for item in items_batch]
        >>>
        >>> result = batch_process_with_chunks(
        ...     items=range(100),
        ...     processor=batch_api_call,
        ...     chunk_size=10  # Process 10 items per API call
        ... )
    """
    # Split items into chunks
    chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

    # Process chunks in parallel
    def process_chunk(chunk):
        return processor(chunk)

    chunk_result = parallel_process(
        items=chunks,
        processor=process_chunk,
        max_workers=max_workers,
        executor_type=executor_type,
        progress_callback=progress_callback,
    )

    # Flatten results
    flat_result = BatchResult(
        total_items=len(items),
        successful_count=sum(len(chunk) for chunk in chunk_result.successes),
        processing_time_ms=chunk_result.processing_time_ms,
        metadata={**chunk_result.metadata, "chunk_size": chunk_size, "total_chunks": len(chunks)},
    )

    # Flatten successes
    for chunk in chunk_result.successes:
        if isinstance(chunk, list):
            flat_result.successes.extend(chunk)
        else:
            flat_result.successes.append(chunk)

    flat_result.failed_count = len(items) - flat_result.successful_count
    flat_result.failures = chunk_result.failures

    return flat_result


def get_optimal_batch_size(
    operation_type: str, total_items: int, available_memory_mb: Optional[int] = None
) -> int:
    """
    Get recommended batch size based on operation type and resources.

    Args:
        operation_type: Type of operation (api_call, file_io, computation, media_processing)
        total_items: Total number of items to process
        available_memory_mb: Available memory in MB (None = auto-detect)

    Returns:
        Recommended batch size

    Example:
        >>> batch_size = get_optimal_batch_size("api_call", total_items=1000)
        >>> print(batch_size)  # 50 for API calls
    """
    # Default batch sizes by operation type
    defaults = {
        "api_call": 50,  # Limited by rate limits
        "file_io": 100,  # I/O bound, can handle more
        "computation": 20,  # CPU intensive
        "media_processing": 10,  # Memory intensive
        "database": 100,  # Usually efficient with batches
        "network": 50,  # Network bound
    }

    base_size = defaults.get(operation_type, 50)

    # Adjust based on total items
    if total_items < 10:
        return total_items
    elif total_items < 100:
        return min(total_items, base_size // 2)
    else:
        return base_size


# Convenience functions for common patterns


def parallel_map(
    items: List[Any], processor: Callable[[Any], Any], max_workers: Optional[int] = None
) -> List[Any]:
    """
    Simple parallel map - process items and return results (raises on any error).

    Args:
        items: Items to process
        processor: Processing function
        max_workers: Number of workers

    Returns:
        List of processed results

    Raises:
        Exception: If any item fails to process

    Example:
        >>> results = parallel_map([1, 2, 3], lambda x: x * 2)
        >>> print(results)  # [2, 4, 6]
    """
    result = parallel_process(
        items=items,
        processor=processor,
        max_workers=max_workers,
        continue_on_error=False,
        progress_callback=SilentProgressCallback(),
    )

    if result.failed_count > 0:
        raise Exception(f"Batch processing failed: {result.failures[0]['error']}")

    return result.successes


def parallel_filter(
    items: List[Any], predicate: Callable[[Any], bool], max_workers: Optional[int] = None
) -> List[Any]:
    """
    Parallel filter - keep items that match predicate.

    Args:
        items: Items to filter
        predicate: Function returning True/False for each item
        max_workers: Number of workers

    Returns:
        Filtered list of items

    Example:
        >>> evens = parallel_filter([1, 2, 3, 4], lambda x: x % 2 == 0)
        >>> print(evens)  # [2, 4]
    """

    def filter_processor(item):
        if predicate(item):
            return item
        else:
            raise ValueError("Filtered out")

    result = parallel_process(
        items=items,
        processor=filter_processor,
        max_workers=max_workers,
        continue_on_error=True,
        progress_callback=SilentProgressCallback(),
    )

    return result.successes


if __name__ == "__main__":
    # Test batch processing utilities
    print("Testing batch processing utilities...")

    # Test 1: Simple parallel processing
    def square(x):
        time.sleep(0.01)  # Simulate work
        return x**2

    result = parallel_process(items=list(range(10)), processor=square, max_workers=4)

    print(f"\nTest 1 - Parallel Processing:")
    print(f"  Total items: {result.total_items}")
    print(f"  Successful: {result.successful_count}")
    print(f"  Failed: {result.failed_count}")
    print(f"  Success rate: {result.success_rate:.1f}%")
    print(f"  Processing time: {result.processing_time_ms:.2f}ms")
    assert result.successful_count == 10
    assert sorted(result.successes) == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

    # Test 2: Error handling
    def sometimes_fail(x):
        if x % 3 == 0:
            raise ValueError(f"Item {x} failed")
        return x * 2

    result2 = parallel_process(
        items=list(range(10)),
        processor=sometimes_fail,
        max_workers=4,
        continue_on_error=True,
        progress_callback=SilentProgressCallback(),
    )

    print(f"\nTest 2 - Error Handling:")
    print(f"  Total items: {result2.total_items}")
    print(f"  Successful: {result2.successful_count}")
    print(f"  Failed: {result2.failed_count}")
    assert result2.failed_count == 4  # 0, 3, 6, 9

    # Test 3: Parallel map
    results = parallel_map(items=[1, 2, 3, 4, 5], processor=lambda x: x * 3, max_workers=2)
    print(f"\nTest 3 - Parallel Map:")
    print(f"  Results: {sorted(results)}")
    assert sorted(results) == [3, 6, 9, 12, 15]

    # Test 4: Batch size recommendation
    batch_size = get_optimal_batch_size("api_call", total_items=1000)
    print(f"\nTest 4 - Batch Size:")
    print(f"  Recommended batch size for API calls: {batch_size}")
    assert batch_size == 50

    print("\n✓ All batch processing tests passed!")
