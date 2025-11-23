"""
Simple performance benchmark comparing sync vs async tool execution.

This benchmark demonstrates the performance benefits of async tools for I/O-bound operations
without requiring external dependencies.
"""

import asyncio
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock mode for benchmarking
os.environ["USE_MOCK_APIS"] = "true"

from pydantic import Field

from shared.async_base import AsyncBaseTool
from shared.async_batch import AsyncBatchProcessor
from shared.base import BaseTool


# Create simple test tools
class SyncTestTool(BaseTool):
    """Sync test tool simulating I/O operation."""

    tool_name: str = "sync_test"
    tool_category: str = "test"

    delay: float = Field(0.1, description="Simulated I/O delay")
    data: str = Field(..., description="Test data")

    def _execute(self) -> Dict[str, Any]:
        """Execute with simulated I/O delay."""
        time.sleep(self.delay)  # Simulate blocking I/O
        return {
            "success": True,
            "data": self.data,
            "delay": self.delay,
        }


class AsyncTestTool(AsyncBaseTool):
    """Async test tool simulating I/O operation."""

    tool_name: str = "async_test"
    tool_category: str = "test"

    delay: float = Field(0.1, description="Simulated I/O delay")
    data: str = Field(..., description="Test data")

    async def _execute(self) -> Dict[str, Any]:
        """Execute with simulated async I/O delay."""
        await asyncio.sleep(self.delay)  # Simulate non-blocking I/O
        return {
            "success": True,
            "data": self.data,
            "delay": self.delay,
        }


@dataclass
class BenchmarkResult:
    """Result from a benchmark run."""

    name: str
    operation_count: int
    total_time: float
    avg_time_per_op: float
    ops_per_second: float
    success_count: int
    metadata: Dict[str, Any]


def benchmark_sync_sequential(operations: int, delay: float = 0.1) -> BenchmarkResult:
    """
    Benchmark sync tools running sequentially.

    Args:
        operations: Number of operations to run
        delay: Simulated I/O delay in seconds

    Returns:
        BenchmarkResult
    """
    print(f"\n{'='*70}")
    print(f"Benchmark: Sync Sequential ({operations} operations)")
    print(f"{'='*70}")

    start_time = time.time()
    success_count = 0

    for i in range(operations):
        tool = SyncTestTool(delay=delay, data=f"item_{i}")
        result = tool.run()

        if result.get("success"):
            success_count += 1

        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {i + 1}/{operations} operations ({elapsed:.2f}s)")

    total_time = time.time() - start_time
    avg_time = total_time / operations
    ops_per_sec = operations / total_time

    result = BenchmarkResult(
        name="Sync Sequential",
        operation_count=operations,
        total_time=total_time,
        avg_time_per_op=avg_time,
        ops_per_second=ops_per_sec,
        success_count=success_count,
        metadata={
            "tool": "SyncTestTool",
            "execution": "sequential",
            "delay": delay,
        },
    )

    print_result(result)
    return result


async def benchmark_async_concurrent(
    operations: int, delay: float = 0.1, concurrency: int = 10
) -> BenchmarkResult:
    """
    Benchmark async tools running concurrently.

    Args:
        operations: Number of operations to run
        delay: Simulated I/O delay in seconds
        concurrency: Maximum concurrent operations

    Returns:
        BenchmarkResult
    """
    print(f"\n{'='*70}")
    print(f"Benchmark: Async Concurrent ({operations} ops, max {concurrency} concurrent)")
    print(f"{'='*70}")

    start_time = time.time()
    success_count = 0

    async def run_operation(i: int) -> Dict[str, Any]:
        """Run single async operation."""
        tool = AsyncTestTool(delay=delay, data=f"item_{i}")
        result = await tool.run_async()
        return result

    # Create batches to show progress
    batch_size = min(concurrency, operations)
    batches = [
        list(range(i, min(i + batch_size, operations))) for i in range(0, operations, batch_size)
    ]

    for batch_idx, batch in enumerate(batches):
        tasks = [run_operation(i) for i in batch]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result.get("success"):
                success_count += 1

        elapsed = time.time() - start_time
        completed = (batch_idx + 1) * batch_size
        print(f"  Progress: {min(completed, operations)}/{operations} operations ({elapsed:.2f}s)")

    total_time = time.time() - start_time
    avg_time = total_time / operations
    ops_per_sec = operations / total_time

    result = BenchmarkResult(
        name="Async Concurrent",
        operation_count=operations,
        total_time=total_time,
        avg_time_per_op=avg_time,
        ops_per_second=ops_per_sec,
        success_count=success_count,
        metadata={
            "tool": "AsyncTestTool",
            "execution": "concurrent",
            "max_concurrency": concurrency,
            "delay": delay,
        },
    )

    print_result(result)
    return result


async def benchmark_batch_processor(
    operations: int, delay: float = 0.1, concurrency: int = 10
) -> BenchmarkResult:
    """
    Benchmark using AsyncBatchProcessor.

    Args:
        operations: Number of operations to run
        delay: Simulated I/O delay in seconds
        concurrency: Maximum concurrent operations

    Returns:
        BenchmarkResult
    """
    print(f"\n{'='*70}")
    print(f"Benchmark: AsyncBatchProcessor ({operations} ops, max {concurrency} concurrent)")
    print(f"{'='*70}")

    async def process_item(data: str) -> Dict[str, Any]:
        """Process single item."""
        tool = AsyncTestTool(delay=delay, data=data)
        return await tool.run_async()

    processor = AsyncBatchProcessor(
        max_concurrency=concurrency,
        max_retries=2,
    )

    items = [f"item_{i}" for i in range(operations)]

    start_time = time.time()
    batch_result = await processor.process(
        items=items, operation=process_item, description="Batch processing"
    )
    total_time = time.time() - start_time

    avg_time = total_time / operations
    ops_per_sec = operations / total_time

    result = BenchmarkResult(
        name="AsyncBatchProcessor",
        operation_count=operations,
        total_time=total_time,
        avg_time_per_op=avg_time,
        ops_per_second=ops_per_sec,
        success_count=batch_result.successful_count,
        metadata={
            "tool": "AsyncTestTool",
            "execution": "batch_processor",
            "max_concurrency": concurrency,
            "delay": delay,
            "failed_count": batch_result.failed_count,
        },
    )

    print_result(result)
    return result


def print_result(result: BenchmarkResult) -> None:
    """Print benchmark result."""
    print(f"\nResults:")
    print(f"  Total Time: {result.total_time:.3f}s")
    print(f"  Avg Time/Op: {result.avg_time_per_op*1000:.2f}ms")
    print(f"  Throughput: {result.ops_per_second:.2f} ops/sec")
    print(
        f"  Success Rate: {result.success_count}/{result.operation_count} ({100*result.success_count/result.operation_count:.1f}%)"
    )


def print_comparison(results: List[BenchmarkResult]) -> None:
    """
    Print comparison table of results.

    Args:
        results: List of benchmark results
    """
    print(f"\n{'='*70}")
    print("PERFORMANCE COMPARISON")
    print(f"{'='*70}\n")

    # Print table header
    print(f"{'Method':<25} {'Time':<12} {'Ops/Sec':<12} {'Speedup':<10}")
    print(f"{'-'*25} {'-'*12} {'-'*12} {'-'*10}")

    # Find baseline (slowest)
    baseline_time = max(r.total_time for r in results)

    # Print each result
    for result in results:
        speedup = baseline_time / result.total_time
        speedup_str = f"{speedup:.2f}x" if speedup > 1 else "-"

        print(
            f"{result.name:<25} {result.total_time:>10.3f}s {result.ops_per_second:>10.2f} {speedup_str:>10}"
        )

    # Print detailed comparison
    sync_result = next((r for r in results if "Sync" in r.name), None)
    async_result = next((r for r in results if "Async Concurrent" in r.name), None)

    if sync_result and async_result:
        speedup = sync_result.total_time / async_result.total_time
        time_saved = sync_result.total_time - async_result.total_time

        print(f"\n{'='*70}")
        print("KEY FINDINGS")
        print(f"{'='*70}")
        print(f"Async is {speedup:.2f}x faster than sync")
        print(
            f"Time saved: {time_saved:.2f}s ({100*time_saved/sync_result.total_time:.1f}% reduction)"
        )
        print(
            f"Throughput improvement: {async_result.ops_per_second/sync_result.ops_per_second:.2f}x"
        )


async def run_benchmarks():
    """Run all benchmarks."""
    print("=" * 70)
    print("ASYNC VS SYNC PERFORMANCE BENCHMARK")
    print("=" * 70)
    print("\nSimulating I/O-bound operations with 100ms delay each")
    print("Mock mode: Enabled (no actual API calls)")
    print()

    results = []
    delay = 0.1  # 100ms simulated I/O delay

    # Benchmark 1: Sync Sequential (baseline)
    result_sync = benchmark_sync_sequential(operations=20, delay=delay)
    results.append(result_sync)

    # Benchmark 2: Async Concurrent
    result_async = await benchmark_async_concurrent(operations=20, delay=delay, concurrency=10)
    results.append(result_async)

    # Benchmark 3: AsyncBatchProcessor
    result_batch = await benchmark_batch_processor(operations=20, delay=delay, concurrency=10)
    results.append(result_batch)

    # Print comparison
    print_comparison(results)

    # Additional test: Large scale
    print(f"\n{'='*70}")
    print("LARGE SCALE TEST (100 operations)")
    print(f"{'='*70}")

    result_large_async = await benchmark_async_concurrent(
        operations=100, delay=delay, concurrency=20
    )
    print(f"\nProjected sync time: {100 * delay:.2f}s")
    print(f"Actual async time: {result_large_async.total_time:.2f}s")
    print(f"Speedup: {(100 * delay) / result_large_async.total_time:.2f}x")


def main():
    """Main entry point."""
    print("\nStarting benchmarks...\n")

    # Run async benchmarks
    asyncio.run(run_benchmarks())

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)
    print("\nConclusion:")
    print("✓ Async tools provide significant speedup for I/O-bound operations")
    print("✓ Concurrent execution scales well with operation count")
    print("✓ AsyncBatchProcessor provides easy-to-use concurrency management")
    print("✓ Use async tools when performing multiple I/O operations in parallel")
    print()


if __name__ == "__main__":
    main()
