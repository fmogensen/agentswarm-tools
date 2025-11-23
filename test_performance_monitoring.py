#!/usr/bin/env python3
"""
Test script for performance monitoring implementation.
"""

import tempfile
import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from shared.monitoring import (
    PerformanceMonitor,
    PerformanceMetric,
    get_monitor,
    record_performance_metric,
)
from shared.dashboard import generate_dashboard_data, export_dashboard_html


def test_monitoring():
    """Test performance monitoring functionality."""
    print("=" * 60)
    print("Testing Performance Monitoring Implementation")
    print("=" * 60)

    # Create temp database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db = f.name

    try:
        # Test 1: Monitor initialization
        print("\n[1/8] Testing monitor initialization...")
        monitor = PerformanceMonitor(db_path=test_db, retention_days=30)
        print("✓ Monitor initialized successfully")

        # Test 2: Record metrics
        print("\n[2/8] Recording test metrics...")
        for i in range(50):
            metric = PerformanceMetric(
                tool_name=f"tool_{i % 5}",
                timestamp=datetime.utcnow(),
                duration_ms=100 + i * 10,
                success=i % 10 != 0,
                memory_mb=50.0,
                cpu_percent=10.0,
                error_type="TestError" if i % 10 == 0 else None,
            )
            monitor.record_metric(metric)
        print(f"✓ Recorded 50 metrics for 5 different tools")

        # Test 3: Get metrics
        print("\n[3/8] Retrieving aggregated metrics...")
        metrics = monitor.get_metrics("tool_0", days=1)
        print(f"  Total Requests: {metrics.total_requests}")
        success_rate = (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Avg Latency: {metrics.avg_latency_ms:.2f}ms")
        print(f"  P95 Latency: {metrics.p95_latency_ms:.2f}ms")
        assert metrics.total_requests == 10
        print("✓ Metrics retrieved successfully")

        # Test 4: Get all metrics
        print("\n[4/8] Retrieving all tool metrics...")
        all_metrics = monitor.get_all_metrics(days=1)
        print(f"  Found metrics for {len(all_metrics)} tools")
        assert len(all_metrics) == 5
        print("✓ All metrics retrieved successfully")

        # Test 5: Slowest tools
        print("\n[5/8] Finding slowest tools...")
        slowest = monitor.get_slowest_tools(days=1, limit=3)
        print(f"  Top 3 slowest tools:")
        for i, m in enumerate(slowest, 1):
            print(f"    {i}. {m.tool_name}: {m.avg_latency_ms:.2f}ms")
        assert len(slowest) == 3
        print("✓ Slowest tools identified")

        # Test 6: Most used tools
        print("\n[6/8] Finding most used tools...")
        most_used = monitor.get_most_used_tools(days=1, limit=3)
        print(f"  Top 3 most used tools:")
        for i, m in enumerate(most_used, 1):
            print(f"    {i}. {m.tool_name}: {m.total_requests} requests")
        assert len(most_used) == 3
        print("✓ Most used tools identified")

        # Test 7: Alerts
        print("\n[7/8] Detecting performance alerts...")
        alerts = monitor.detect_alerts(days=1)
        print(f"  Found {len(alerts)} alerts")
        if alerts:
            for alert in alerts[:3]:
                print(f"    [{alert['severity']}] {alert['type']}")
        print("✓ Alert detection working")

        # Test 8: Dashboard generation
        print("\n[8/8] Generating dashboard...")
        dashboard_data = generate_dashboard_data(days=1)
        print(f"  Overview:")
        print(f"    Total Tools: {dashboard_data['overview']['total_tools']}")
        print(f"    Total Requests: {dashboard_data['overview']['total_requests']}")
        print(f"    Avg Latency: {dashboard_data['overview']['avg_latency_ms']}ms")
        assert dashboard_data['overview']['total_tools'] >= 5
        print("✓ Dashboard data generated")

        # Test HTML export
        print("\n  Exporting HTML dashboard...")
        html_file = export_dashboard_html(days=1, output_file="/tmp/test_dashboard.html")
        print(f"✓ HTML dashboard exported to: {html_file}")

        # Test JSON export
        print("\n  Exporting JSON metrics...")
        json_str = monitor.export_to_json(days=1, output_file="/tmp/test_metrics.json")
        print(f"✓ JSON metrics exported ({len(json_str)} bytes)")

        # Test Prometheus export
        print("\n  Exporting Prometheus metrics...")
        prom_str = monitor.export_to_prometheus(days=1)
        assert "agentswarm_tool_requests_total" in prom_str
        print(f"✓ Prometheus metrics exported ({len(prom_str)} bytes)")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

        print("\nPerformance Overhead Test:")
        import time
        start = time.time()
        for i in range(1000):
            metric = PerformanceMetric(
                tool_name="overhead_test",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,
                success=True,
            )
            monitor.record_metric(metric)
        elapsed = time.time() - start
        avg_overhead = (elapsed / 1000) * 1000
        print(f"  1000 metrics recorded in {elapsed:.2f}s")
        print(f"  Average overhead: {avg_overhead:.2f}ms per request")
        assert avg_overhead < 5, f"Overhead {avg_overhead:.2f}ms exceeds 5ms target"
        print("✓ Performance overhead within target (<5ms)")

        print("\n📊 Sample Reports:")
        print("\nView dashboard at:")
        print(f"  file:///tmp/test_dashboard.html")
        print("\nView JSON export at:")
        print(f"  /tmp/test_metrics.json")

    finally:
        # Cleanup
        if os.path.exists(test_db):
            os.unlink(test_db)


if __name__ == "__main__":
    test_monitoring()
