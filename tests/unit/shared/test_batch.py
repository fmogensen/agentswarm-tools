"""
Unit tests for batch processing utilities
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from shared.batch import (
    parallel_process,
    parallel_map,
    parallel_filter,
    batch_process_with_chunks,
    get_optimal_batch_size,
    get_default_max_workers,
    ExecutorType,
    BatchResult,
    DefaultProgressCallback,
    SilentProgressCallback,
)


def test_parallel_process_basic():
    """Test basic parallel processing."""
    def square(x):
        return x ** 2

    result = parallel_process(
        items=[1, 2, 3, 4, 5],
        processor=square,
        max_workers=2,
        progress_callback=SilentProgressCallback()
    )

    assert result.successful_count == 5
    assert result.failed_count == 0
    assert sorted(result.successes) == [1, 4, 9, 16, 25]
    assert result.success_rate == 100.0

    print("✓ test_parallel_process_basic passed")


def test_parallel_process_with_errors():
    """Test parallel processing with some failures."""
    def sometimes_fail(x):
        if x % 3 == 0:
            raise ValueError(f"Item {x} failed")
        return x * 2

    result = parallel_process(
        items=list(range(10)),
        processor=sometimes_fail,
        max_workers=4,
        continue_on_error=True,
        progress_callback=SilentProgressCallback()
    )

    assert result.successful_count == 6  # 1,2,4,5,7,8
    assert result.failed_count == 4  # 0,3,6,9
    assert result.success_rate == 60.0

    print("✓ test_parallel_process_with_errors passed")


def test_parallel_map():
    """Test parallel_map convenience function."""
    results = parallel_map(
        items=[1, 2, 3, 4, 5],
        processor=lambda x: x * 3,
        max_workers=2
    )

    assert sorted(results) == [3, 6, 9, 12, 15]

    print("✓ test_parallel_map passed")


def test_parallel_filter():
    """Test parallel_filter convenience function."""
    results = parallel_filter(
        items=[1, 2, 3, 4, 5, 6, 7, 8],
        predicate=lambda x: x % 2 == 0,
        max_workers=2
    )

    assert sorted(results) == [2, 4, 6, 8]

    print("✓ test_parallel_filter passed")


def test_batch_result():
    """Test BatchResult class."""
    result = BatchResult(
        total_items=10,
        successful_count=8,
        failed_count=2,
        processing_time_ms=150.5
    )

    assert result.total_items == 10
    assert result.successful_count == 8
    assert result.failed_count == 2
    assert result.success_rate == 80.0

    print("✓ test_batch_result passed")


def test_executor_type_thread():
    """Test with thread executor."""
    def io_bound_task(x):
        time.sleep(0.001)  # Simulate I/O
        return x * 2

    result = parallel_process(
        items=list(range(10)),
        processor=io_bound_task,
        max_workers=5,
        executor_type=ExecutorType.THREAD,
        progress_callback=SilentProgressCallback()
    )

    assert result.successful_count == 10
    assert result.metadata["executor_type"] == "thread"

    print("✓ test_executor_type_thread passed")


def test_get_default_max_workers():
    """Test default max_workers calculation."""
    thread_workers = get_default_max_workers(ExecutorType.THREAD)
    process_workers = get_default_max_workers(ExecutorType.PROCESS)

    assert thread_workers > 0
    assert process_workers > 0
    assert thread_workers >= process_workers  # Thread should be at least CPU count

    print(f"  Thread workers: {thread_workers}")
    print(f"  Process workers: {process_workers}")
    print("✓ test_get_default_max_workers passed")


def test_get_optimal_batch_size():
    """Test batch size recommendations."""
    api_size = get_optimal_batch_size("api_call", total_items=1000)
    file_size = get_optimal_batch_size("file_io", total_items=1000)
    compute_size = get_optimal_batch_size("computation", total_items=1000)

    assert api_size == 50
    assert file_size == 100
    assert compute_size == 20

    # Small datasets
    small_size = get_optimal_batch_size("api_call", total_items=5)
    assert small_size == 5

    print("✓ test_get_optimal_batch_size passed")


def test_progress_callback():
    """Test progress tracking."""
    class TestProgressCallback(DefaultProgressCallback):
        def __init__(self):
            super().__init__(verbose=False)
            self.started = False
            self.completed = False
            self.item_count = 0

        def on_start(self, total_items: int):
            self.started = True
            self.total = total_items

        def on_item_complete(self, item_index: int, total_items: int, success: bool):
            self.item_count += 1

        def on_complete(self, result: BatchResult):
            self.completed = True

    callback = TestProgressCallback()

    result = parallel_process(
        items=[1, 2, 3],
        processor=lambda x: x * 2,
        progress_callback=callback
    )

    assert callback.started == True
    assert callback.completed == True
    assert callback.item_count == 3
    assert callback.total == 3

    print("✓ test_progress_callback passed")


def test_batch_process_with_chunks():
    """Test chunk-based batch processing."""
    def process_chunk(items):
        # Process multiple items at once
        return [x * 2 for x in items]

    result = batch_process_with_chunks(
        items=list(range(20)),
        processor=process_chunk,
        chunk_size=5,  # 20 items / 5 per chunk = 4 chunks
        max_workers=2,
        progress_callback=SilentProgressCallback()
    )

    assert result.successful_count == 20
    assert sorted(result.successes) == list(range(0, 40, 2))
    assert result.metadata["chunk_size"] == 5
    assert result.metadata["total_chunks"] == 4

    print("✓ test_batch_process_with_chunks passed")


def test_continue_on_error_false():
    """Test stopping on first error."""
    def fail_on_five(x):
        if x == 5:
            raise ValueError("Failed on 5")
        return x * 2

    result = parallel_process(
        items=list(range(10)),
        processor=fail_on_five,
        max_workers=2,
        continue_on_error=False,
        progress_callback=SilentProgressCallback()
    )

    # Should have stopped after encountering error
    # Note: Due to parallel nature, some items after 5 might have been processed
    assert result.failed_count > 0

    print("✓ test_continue_on_error_false passed")


def test_processing_time_measurement():
    """Test that processing time is measured correctly."""
    def slow_processor(x):
        time.sleep(0.01)  # 10ms
        return x

    start = time.time()
    result = parallel_process(
        items=list(range(5)),
        processor=slow_processor,
        max_workers=5,  # All in parallel
        progress_callback=SilentProgressCallback()
    )
    elapsed = (time.time() - start) * 1000

    # Processing time should be recorded
    assert result.processing_time_ms > 0
    # Should be roughly the same as elapsed time (within tolerance)
    assert abs(result.processing_time_ms - elapsed) < 50  # 50ms tolerance

    print(f"  Processing time: {result.processing_time_ms:.2f}ms")
    print("✓ test_processing_time_measurement passed")


def test_empty_items_list():
    """Test handling of empty items list."""
    result = parallel_process(
        items=[],
        processor=lambda x: x,
        progress_callback=SilentProgressCallback()
    )

    assert result.total_items == 0
    assert result.successful_count == 0
    assert result.failed_count == 0

    print("✓ test_empty_items_list passed")


def test_metadata():
    """Test metadata is included in results."""
    custom_metadata = {"test_key": "test_value", "run_id": "123"}

    result = parallel_process(
        items=[1, 2, 3],
        processor=lambda x: x * 2,
        batch_metadata=custom_metadata,
        progress_callback=SilentProgressCallback()
    )

    assert "test_key" in result.metadata
    assert result.metadata["test_key"] == "test_value"
    assert result.metadata["run_id"] == "123"

    print("✓ test_metadata passed")


def test_performance_improvement():
    """Test that parallel processing is faster than sequential."""
    def slow_task(x):
        time.sleep(0.01)  # 10ms per item
        return x

    items = list(range(10))

    # Sequential (simulated)
    sequential_time = len(items) * 0.01 * 1000  # 100ms

    # Parallel
    start = time.time()
    result = parallel_process(
        items=items,
        processor=slow_task,
        max_workers=10,  # All items at once
        progress_callback=SilentProgressCallback()
    )
    parallel_time = (time.time() - start) * 1000

    # Parallel should be significantly faster
    speedup = sequential_time / parallel_time
    print(f"  Sequential (est): {sequential_time:.2f}ms")
    print(f"  Parallel: {parallel_time:.2f}ms")
    print(f"  Speedup: {speedup:.1f}x")

    # Should be at least 2x faster (conservative check due to overhead)
    assert speedup > 2

    print("✓ test_performance_improvement passed")


if __name__ == "__main__":
    print("Running batch processing unit tests...\n")

    test_parallel_process_basic()
    test_parallel_process_with_errors()
    test_parallel_map()
    test_parallel_filter()
    test_batch_result()
    test_executor_type_thread()
    test_get_default_max_workers()
    test_get_optimal_batch_size()
    test_progress_callback()
    test_batch_process_with_chunks()
    test_continue_on_error_false()
    test_processing_time_measurement()
    test_empty_items_list()
    test_metadata()
    test_performance_improvement()

    print("\n" + "=" * 50)
    print("✓ All batch processing tests passed!")
    print("=" * 50)
