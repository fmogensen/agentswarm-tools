"""
Unit tests for performance monitoring system.
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from shared.monitoring import (
    AggregatedMetrics,
    PerformanceMetric,
    PerformanceMonitor,
    get_monitor,
    record_performance_metric,
    track_performance,
)


class TestPerformanceMetric:
    """Test PerformanceMetric dataclass."""

    def test_metric_creation(self):
        """Test creating a performance metric."""
        metric = PerformanceMetric(
            tool_name="test_tool",
            timestamp=datetime.utcnow(),
            duration_ms=150.5,
            success=True,
            memory_mb=100.0,
            cpu_percent=25.5,
            api_calls=3,
            cache_hit=True,
        )

        assert metric.tool_name == "test_tool"
        assert metric.duration_ms == 150.5
        assert metric.success is True
        assert metric.memory_mb == 100.0
        assert metric.cpu_percent == 25.5
        assert metric.api_calls == 3
        assert metric.cache_hit is True

    def test_metric_to_dict(self):
        """Test converting metric to dictionary."""
        timestamp = datetime.utcnow()
        metric = PerformanceMetric(
            tool_name="test_tool",
            timestamp=timestamp,
            duration_ms=150.5,
            success=True,
        )

        data = metric.to_dict()
        assert data["tool_name"] == "test_tool"
        assert data["duration_ms"] == 150.5
        assert data["success"] is True
        assert data["timestamp"] == timestamp.isoformat()


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def monitor(self, temp_db):
        """Create a PerformanceMonitor instance."""
        return PerformanceMonitor(db_path=temp_db, retention_days=30)

    def test_monitor_initialization(self, monitor, temp_db):
        """Test monitor initialization."""
        assert monitor.db_path == temp_db
        assert monitor.retention_days == 30
        assert os.path.exists(temp_db)

    def test_record_metric(self, monitor):
        """Test recording a performance metric."""
        metric = PerformanceMetric(
            tool_name="test_tool",
            timestamp=datetime.utcnow(),
            duration_ms=100.0,
            success=True,
        )

        monitor.record_metric(metric)

        # Verify metric was recorded
        metrics = monitor.get_metrics("test_tool", days=1)
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1

    def test_multiple_metrics(self, monitor):
        """Test recording multiple metrics."""
        for i in range(10):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100 + i * 10,
                success=i % 5 != 0,  # 20% failure rate
            )
            monitor.record_metric(metric)

        metrics = monitor.get_metrics("test_tool", days=1)
        assert metrics.total_requests == 10
        assert metrics.successful_requests == 8
        assert metrics.failed_requests == 2
        assert metrics.success_rate == 80.0
        assert metrics.error_rate_percent == 20.0

    def test_percentile_calculation(self, monitor):
        """Test percentile calculations."""
        # Create metrics with known distribution
        for i in range(100):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=float(i + 1),  # 1ms to 100ms
                success=True,
            )
            monitor.record_metric(metric)

        metrics = monitor.get_metrics("test_tool", days=1, include_percentiles=True)

        assert metrics.total_requests == 100
        assert metrics.min_latency_ms == 1.0
        assert metrics.max_latency_ms == 100.0
        assert 49 <= metrics.p50_latency_ms <= 51  # Median around 50
        assert 94 <= metrics.p95_latency_ms <= 96  # P95 around 95
        assert 98 <= metrics.p99_latency_ms <= 100  # P99 around 99

    def test_slow_query_detection(self, monitor):
        """Test slow query detection."""
        # Record fast queries
        for i in range(50):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,  # Fast
                success=True,
            )
            monitor.record_metric(metric)

        # Record slow queries
        for i in range(10):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=2000.0,  # Slow (> 1000ms threshold)
                success=True,
            )
            monitor.record_metric(metric)

        metrics = monitor.get_metrics("test_tool", days=1)
        assert metrics.total_requests == 60
        assert metrics.slow_queries == 10

    def test_error_tracking(self, monitor):
        """Test error type tracking."""
        # Record various errors
        for i in range(20):
            success = i % 4 != 0
            error_type = None if success else ["ValidationError", "APIError", "TimeoutError"][i % 3]

            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,
                success=success,
                error_type=error_type,
            )
            monitor.record_metric(metric)

        metrics = monitor.get_metrics("test_tool", days=1)
        assert metrics.failed_requests == 5
        assert len(metrics.error_types) > 0

    def test_get_all_metrics(self, monitor):
        """Test getting metrics for all tools."""
        # Record metrics for multiple tools
        for tool_id in range(5):
            for i in range(10):
                metric = PerformanceMetric(
                    tool_name=f"tool_{tool_id}",
                    timestamp=datetime.utcnow(),
                    duration_ms=100.0 + tool_id * 50,
                    success=True,
                )
                monitor.record_metric(metric)

        all_metrics = monitor.get_all_metrics(days=1)
        assert len(all_metrics) == 5
        for tool_id in range(5):
            tool_name = f"tool_{tool_id}"
            assert tool_name in all_metrics
            assert all_metrics[tool_name].total_requests == 10

    def test_slowest_tools(self, monitor):
        """Test getting slowest tools."""
        # Create tools with different latencies
        latencies = [100, 200, 300, 400, 500]
        for i, latency in enumerate(latencies):
            for j in range(10):
                metric = PerformanceMetric(
                    tool_name=f"tool_{i}",
                    timestamp=datetime.utcnow(),
                    duration_ms=float(latency),
                    success=True,
                )
                monitor.record_metric(metric)

        slowest = monitor.get_slowest_tools(days=1, limit=3)
        assert len(slowest) == 3
        # Should be ordered by latency descending
        assert slowest[0].avg_latency_ms == 500.0
        assert slowest[1].avg_latency_ms == 400.0
        assert slowest[2].avg_latency_ms == 300.0

    def test_most_used_tools(self, monitor):
        """Test getting most used tools."""
        # Create tools with different request counts
        request_counts = [10, 20, 30, 40, 50]
        for i, count in enumerate(request_counts):
            for j in range(count):
                metric = PerformanceMetric(
                    tool_name=f"tool_{i}",
                    timestamp=datetime.utcnow(),
                    duration_ms=100.0,
                    success=True,
                )
                monitor.record_metric(metric)

        most_used = monitor.get_most_used_tools(days=1, limit=3)
        assert len(most_used) == 3
        # Should be ordered by request count descending
        assert most_used[0].total_requests == 50
        assert most_used[1].total_requests == 40
        assert most_used[2].total_requests == 30

    def test_detect_alerts(self, monitor):
        """Test alert detection."""
        # Create tool with high error rate
        for i in range(100):
            metric = PerformanceMetric(
                tool_name="error_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,
                success=i >= 20,  # 20% error rate
                error_type="TestError" if i < 20 else None,
            )
            monitor.record_metric(metric)

        # Create tool with slow queries
        for i in range(100):
            metric = PerformanceMetric(
                tool_name="slow_tool",
                timestamp=datetime.utcnow(),
                duration_ms=2000.0 if i < 15 else 100.0,  # 15% slow queries
                success=True,
            )
            monitor.record_metric(metric)

        alerts = monitor.detect_alerts(days=1)
        assert len(alerts) > 0

        # Check for high error rate alert
        error_alerts = [a for a in alerts if a["type"] == "HIGH_ERROR_RATE"]
        assert len(error_alerts) > 0

        # Check for slow queries alert
        slow_alerts = [a for a in alerts if a["type"] == "SLOW_QUERIES"]
        assert len(slow_alerts) > 0

    def test_export_to_json(self, monitor, tmp_path):
        """Test JSON export."""
        # Record some metrics
        for i in range(10):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,
                success=True,
            )
            monitor.record_metric(metric)

        output_file = tmp_path / "metrics.json"
        json_str = monitor.export_to_json(days=1, output_file=str(output_file))

        assert output_file.exists()
        assert len(json_str) > 0
        assert "test_tool" in json_str

    def test_export_to_prometheus(self, monitor):
        """Test Prometheus export."""
        # Record some metrics
        for i in range(10):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=100.0,
                success=True,
            )
            monitor.record_metric(metric)

        prom_str = monitor.export_to_prometheus(days=1)
        assert "agentswarm_tool_requests_total" in prom_str
        assert "agentswarm_tool_latency_ms" in prom_str
        assert 'tool="test_tool"' in prom_str

    def test_retention_cleanup(self, monitor):
        """Test automatic cleanup of old data."""
        # Record old metric (outside retention period)
        old_timestamp = datetime.utcnow() - timedelta(days=35)
        old_metric = PerformanceMetric(
            tool_name="test_tool",
            timestamp=old_timestamp,
            duration_ms=100.0,
            success=True,
        )
        monitor.record_metric(old_metric)

        # Trigger cleanup
        monitor._cleanup_old_data()

        # Old metric should be gone
        metrics = monitor.get_metrics("test_tool", days=40)
        assert metrics.total_requests == 0

    def test_cache_hit_tracking(self, monitor):
        """Test cache hit rate tracking."""
        # Record metrics with cache hits
        for i in range(100):
            metric = PerformanceMetric(
                tool_name="test_tool",
                timestamp=datetime.utcnow(),
                duration_ms=10.0 if i < 30 else 100.0,
                success=True,
                cache_hit=i < 30,  # 30% cache hit rate
            )
            monitor.record_metric(metric)

        metrics = monitor.get_metrics("test_tool", days=1)
        assert metrics.cache_hit_rate_percent == pytest.approx(30.0, abs=1.0)


class TestDecorator:
    """Test track_performance decorator."""

    def test_decorator_basic(self, monkeypatch):
        """Test basic decorator functionality."""
        # Enable monitoring
        monkeypatch.setenv("PERFORMANCE_MONITORING_ENABLED", "true")

        call_count = 0

        @track_performance
        def test_function():
            nonlocal call_count
            call_count += 1
            return "result"

        result = test_function()
        assert result == "result"
        assert call_count == 1

    def test_decorator_with_exception(self, monkeypatch):
        """Test decorator with exception."""
        monkeypatch.setenv("PERFORMANCE_MONITORING_ENABLED", "true")

        @track_performance
        def test_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            test_function()


class TestManualRecording:
    """Test manual performance metric recording."""

    def test_record_performance_metric(self, monkeypatch):
        """Test manual metric recording."""
        monkeypatch.setenv("PERFORMANCE_MONITORING_ENABLED", "true")

        record_performance_metric(
            tool_name="manual_tool",
            duration_ms=150.0,
            success=True,
            api_calls=5,
            cache_hit=False,
            metadata={"custom": "data"},
        )

        # Verify metric was recorded
        monitor = get_monitor()
        metrics = monitor.get_metrics("manual_tool", days=1)
        assert metrics.total_requests >= 1


class TestResourceUsageTracking:
    """Test resource usage tracking."""

    def test_get_resource_usage(self, monitor):
        """Test getting resource usage."""
        usage = monitor.get_resource_usage()
        assert "memory_mb" in usage
        assert "cpu_percent" in usage
        assert usage["memory_mb"] >= 0
        assert usage["cpu_percent"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
