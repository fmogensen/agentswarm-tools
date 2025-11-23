"""
Async version of understand_images - read and analyze image content with non-blocking I/O
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field

try:
    import httpx
except ImportError:
    httpx = None

from shared.async_base import AsyncBaseTool
from shared.errors import APIError, ValidationError
from shared.logging import get_logger

logger = get_logger(__name__)


class AsyncUnderstandImages(AsyncBaseTool):
    """
    Async image analysis - read and analyze image content with non-blocking I/O

    This async version allows multiple image analyses to run concurrently without blocking.
    Use this when you need to analyze many images in parallel or in async contexts.

    Args:
        media_urls: List of URLs or AI Drive paths to analyze
        instruction: What to analyze or extract

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Analysis results for all images
        - metadata: Additional information

    Example (async):
        >>> import asyncio
        >>> async def analyze():
        ...     tool = AsyncUnderstandImages(
        ...         media_urls=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
        ...         instruction="Describe the main objects"
        ...     )
        ...     result = await tool.run_async()
        ...     return result
        >>> asyncio.run(analyze())

    Example (sync wrapper):
        >>> tool = AsyncUnderstandImages(
        ...     media_urls=["https://example.com/image.jpg"],
        ...     instruction="Describe the image"
        ... )
        >>> result = tool.run()  # Automatically handles async execution
    """

    # Tool metadata
    tool_name: str = "async_understand_images"
    tool_category: str = "media"

    # Parameters
    media_urls: List[str] = Field(..., description="List of media URLs to analyze")
    instruction: Optional[str] = Field(None, description="What to analyze or extract from images")

    async def _execute(self) -> Dict[str, Any]:
        """
        Execute the async image analysis.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE (async)
        try:
            results = await self._process()

            return {
                "success": True,
                "result": results,
                "metadata": {
                    "tool_name": self.tool_name,
                    "instruction": self.instruction,
                    "image_count": len(self.media_urls),
                    "async": True,
                },
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.media_urls or not isinstance(self.media_urls, list):
            raise ValidationError(
                "media_urls must be a non-empty list",
                tool_name=self.tool_name,
                details={"media_urls": self.media_urls},
            )

        for url in self.media_urls:
            if not isinstance(url, str):
                raise ValidationError(
                    "All media_urls must be strings",
                    tool_name=self.tool_name,
                    details={"invalid_url": url},
                )

            if not (
                url.startswith("http://")
                or url.startswith("https://")
                or url.startswith("aidrive://")
            ):
                raise ValidationError(
                    "Each media_url must be an http/https URL or an AI Drive path",
                    tool_name=self.tool_name,
                    details={"invalid_url": url},
                )

        if self.instruction is not None and not isinstance(self.instruction, str):
            raise ValidationError(
                "instruction must be a string if provided",
                tool_name=self.tool_name,
                details={"instruction": self.instruction},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_results = [
            {
                "media_url": url,
                "instruction": self.instruction or "No instruction provided",
                "description": f"This is a mock async analysis response for {url}.",
                "objects": ["object1", "object2", "object3"],
                "confidence": 0.95,
            }
            for url in self.media_urls
        ]

        return {
            "success": True,
            "result": mock_results,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "async": True,
            },
        }

    async def _process(self) -> List[Dict[str, Any]]:
        """Main async processing logic."""
        if httpx is None:
            raise APIError(
                "httpx library is required for async image analysis. Install with: pip install httpx",
                tool_name=self.tool_name,
            )

        # Process all images concurrently
        import asyncio

        tasks = [self._analyze_single_image(url) for url in self.media_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any errors
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "media_url": self.media_urls[i],
                        "error": str(result),
                        "success": False,
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _analyze_single_image(self, media_url: str) -> Dict[str, Any]:
        """
        Analyze a single image asynchronously.

        Args:
            media_url: URL or AI Drive path of the image

        Returns:
            Analysis result for the image
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Simple retrieval for demonstration
                if media_url.startswith("aidrive://"):
                    # Placeholder for AI Drive logic
                    # Real implementation would interface with the AI Drive system
                    image_bytes = b"FAKE_AIDRIVE_IMAGE_DATA"
                else:
                    response = await client.get(media_url)
                    response.raise_for_status()
                    image_bytes = response.content

                size_bytes = len(image_bytes)

                # In a real implementation, this would call an AI vision model
                analysis = {
                    "media_url": media_url,
                    "image_size_bytes": size_bytes,
                    "instruction_applied": bool(self.instruction),
                    "instruction": self.instruction or "No instruction provided",
                    "success": True,
                }

                return analysis

        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to fetch image from {media_url}: HTTP {e.response.status_code}",
                tool_name=self.tool_name,
            )
        except httpx.RequestError as e:
            raise APIError(
                f"Error retrieving image from {media_url}: {e}",
                tool_name=self.tool_name,
            )


if __name__ == "__main__":
    # Test the async understand_images tool
    print("Testing AsyncUnderstandImages tool...")

    import asyncio
    import time

    async def test_async():
        """Test async execution."""
        print("\n1. Testing async execution...")

        os.environ["USE_MOCK_APIS"] = "true"

        tool = AsyncUnderstandImages(
            media_urls=[
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
            ],
            instruction="Describe the main objects in these images",
        )
        result = await tool.run_async()

        print(f"  Success: {result.get('success')}")
        print(f"  Images analyzed: {len(result.get('result', []))}")
        print(
            f"  First result: {result.get('result', [{}])[0] if result.get('result') else 'None'}"
        )
        assert result.get("success") == True
        assert len(result.get("result", [])) == 2
        print("  ✓ Async execution test passed")

    async def test_concurrent():
        """Test concurrent analysis."""
        print("\n2. Testing concurrent image analysis...")

        os.environ["USE_MOCK_APIS"] = "true"

        # Create multiple analysis tasks
        tools = [
            AsyncUnderstandImages(
                media_urls=[f"https://example.com/image{i}.jpg"], instruction="Analyze this image"
            )
            for i in range(5)
        ]

        # Execute concurrently
        start = time.time()
        results = await asyncio.gather(*[tool.run_async() for tool in tools])
        duration = time.time() - start

        print(f"  Completed {len(results)} analyses in {duration:.3f}s")
        print(f"  All successful: {all(r.get('success') for r in results)}")
        assert all(r.get("success") for r in results)
        print("  ✓ Concurrent analysis test passed")

    async def test_batch_images():
        """Test analyzing multiple images in one call."""
        print("\n3. Testing batch image analysis...")

        os.environ["USE_MOCK_APIS"] = "true"

        image_urls = [f"https://example.com/batch/image{i}.jpg" for i in range(10)]

        tool = AsyncUnderstandImages(
            media_urls=image_urls, instruction="Extract text from these images"
        )

        start = time.time()
        result = await tool.run_async()
        duration = time.time() - start

        print(f"  Analyzed {len(image_urls)} images in {duration:.3f}s")
        print(f"  Success: {result.get('success')}")
        print(f"  Results: {len(result.get('result', []))}")
        assert result.get("success") == True
        assert len(result.get("result", [])) == 10
        print("  ✓ Batch analysis test passed")

    def test_sync_wrapper():
        """Test sync wrapper."""
        logger.info("\n4. Testing sync wrapper...")

        os.environ["USE_MOCK_APIS"] = "true"

        tool = AsyncUnderstandImages(
            media_urls=["https://example.com/sync-test.jpg"], instruction="Sync wrapper test"
        )
        result = tool.run()  # Sync wrapper

        logger.info(f"  Success: {result.get('success')}")
        logger.info(f"  Results: {len(result.get('result', []))}")
        assert result.get("success") == True
        logger.info("  ✓ Sync wrapper test passed")

    async def test_with_batch_processor():
        """Test with AsyncBatchProcessor."""
        logger.info("\n5. Testing with AsyncBatchProcessor...")

        os.environ["USE_MOCK_APIS"] = "true"

        from shared.async_batch import AsyncBatchProcessor

        async def analyze_image(url: str) -> Dict[str, Any]:
            tool = AsyncUnderstandImages(media_urls=[url], instruction="Analyze this image")
            return await tool.run_async()

        processor = AsyncBatchProcessor(max_concurrency=3, rate_limit=5, rate_limit_per=1.0)

        urls = [f"https://example.com/batch-proc/img{i}.jpg" for i in range(8)]
        batch_result = await processor.process(
            items=urls, operation=analyze_image, description="Batch image analysis"
        )

        logger.info(f"  Successful: {batch_result.successful_count}/{len(urls)}")
        logger.info(f"  Duration: {batch_result.duration_ms:.2f}ms")
        assert batch_result.successful_count == len(urls)
        logger.info("  ✓ AsyncBatchProcessor test passed")

    # Run tests
    async def main():
        await test_async()
        await test_concurrent()
        await test_batch_images()
        test_sync_wrapper()
        await test_with_batch_processor()
        logger.info("\n✓ All AsyncUnderstandImages tests passed!")

    asyncio.run(main())
