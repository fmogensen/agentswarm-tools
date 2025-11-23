"""
Performance monitoring and metrics collection for AgentSwarm Tools.

Provides:
- Performance metrics collection (latency, throughput, error rates)
- Automatic timing decorators
- Resource usage tracking (CPU, memory)
- Metrics export (JSON, Prometheus format)
- Alert thresholds
- SQLite-based persistent storage with minimal overhead
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from functools import wraps
import time
import os
import sqlite3
import threading
from pathlib import Path
import json
import statistics

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# Performance thresholds (configurable via environment variables)
SLOW_QUERY_THRESHOLD_MS = int(os.getenv("SLOW_QUERY_THRESHOLD_MS", "1000"))
HIGH_MEMORY_THRESHOLD_MB = int(os.getenv("HIGH_MEMORY_THRESHOLD_MB", "500"))
ERROR_RATE_THRESHOLD_PERCENT = float(os.getenv("ERROR_RATE_THRESHOLD_PERCENT", "10.0"))


@dataclass
class PerformanceMetric:
    """Single performance measurement."""

    tool_name: str
    timestamp: datetime
    duration_ms: float
    success: bool
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    api_calls: int = 0
    cache_hit: bool = False
    error_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class AggregatedMetrics:
    """Aggregated performance metrics for a tool."""

    tool_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    total_duration_ms: float
    error_rate_percent: float
    avg_memory_mb: Optional[float] = None
    avg_cpu_percent: Optional[float] = None
    cache_hit_rate_percent: Optional[float] = None
    error_types: Dict[str, int] = field(default_factory=dict)
    slow_queries: int = 0
    requests_per_minute: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["first_seen"] = self.first_seen.isoformat() if self.first_seen else None
        data["last_seen"] = self.last_seen.isoformat() if self.last_seen else None
        return data


class PerformanceMonitor:
    """
    Performance monitoring system with SQLite storage.

    Features:
    - Automatic metrics collection
    - Percentile calculations (p50, p95, p99)
    - Resource usage tracking
    - Alert detection
    - Metrics export (JSON, Prometheus)
    - Automatic cleanup of old data
    """

    def __init__(self, db_path: Optional[str] = None, retention_days: int = 30):
        """
        Initialize performance monitor.

        Args:
            db_path: Path to SQLite database (default: ~/.agentswarm/metrics.db)
            retention_days: How many days to retain metrics (default: 30)
        """
        if db_path is None:
            home = Path.home()
            agentswarm_dir = home / ".agentswarm"
            agentswarm_dir.mkdir(exist_ok=True)
            db_path = str(agentswarm_dir / "metrics.db")

        self.db_path = db_path
        self.retention_days = retention_days
        self._lock = threading.Lock()
        self._process = psutil.Process() if PSUTIL_AVAILABLE else None
        self._init_db()
        self._cleanup_old_data()

    def _init_db(self) -> None:
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    success INTEGER NOT NULL,
                    memory_mb REAL,
                    cpu_percent REAL,
                    api_calls INTEGER DEFAULT 0,
                    cache_hit INTEGER DEFAULT 0,
                    error_type TEXT,
                    metadata TEXT
                )
            """
            )

            # Create indexes for faster queries
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_tool_timestamp
                ON performance_metrics(tool_name, timestamp)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON performance_metrics(timestamp)
            """
            )

            conn.commit()

    def _cleanup_old_data(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        cutoff_str = cutoff.isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff_str,)
            )
            conn.commit()

    def record_metric(self, metric: PerformanceMetric) -> None:
        """
        Record a performance metric.

        Args:
            metric: PerformanceMetric instance
        """
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_metrics
                    (tool_name, timestamp, duration_ms, success, memory_mb, cpu_percent,
                     api_calls, cache_hit, error_type, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric.tool_name,
                        metric.timestamp.isoformat(),
                        metric.duration_ms,
                        1 if metric.success else 0,
                        metric.memory_mb,
                        metric.cpu_percent,
                        metric.api_calls,
                        1 if metric.cache_hit else 0,
                        metric.error_type,
                        json.dumps(metric.metadata),
                    ),
                )
                conn.commit()

    def get_metrics(
        self, tool_name: str, days: int = 7, include_percentiles: bool = True
    ) -> AggregatedMetrics:
        """
        Get aggregated metrics for a tool.

        Args:
            tool_name: Tool name
            days: Number of days to look back
            include_percentiles: Whether to calculate percentiles (slower)

        Returns:
            AggregatedMetrics instance
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT duration_ms, success, memory_mb, cpu_percent,
                       cache_hit, error_type, timestamp
                FROM performance_metrics
                WHERE tool_name = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """,
                (tool_name, cutoff_str),
            )

            rows = cursor.fetchall()

        if not rows:
            # Return empty metrics
            return AggregatedMetrics(
                tool_name=tool_name,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                p99_latency_ms=0.0,
                min_latency_ms=0.0,
                max_latency_ms=0.0,
                total_duration_ms=0.0,
                error_rate_percent=0.0,
            )

        # Extract data
        durations = [row[0] for row in rows]
        successes = [row[1] for row in rows]
        memories = [row[2] for row in rows if row[2] is not None]
        cpus = [row[3] for row in rows if row[3] is not None]
        cache_hits = [row[4] for row in rows]
        error_types = [row[5] for row in rows if row[5] is not None]
        timestamps = [datetime.fromisoformat(row[6]) for row in rows]

        # Calculate metrics
        total_requests = len(rows)
        successful_requests = sum(successes)
        failed_requests = total_requests - successful_requests

        # Calculate percentiles
        if include_percentiles:
            p50 = statistics.median(durations)
            p95 = self._percentile(durations, 95)
            p99 = self._percentile(durations, 99)
        else:
            p50 = p95 = p99 = 0.0

        # Error types
        error_type_counts = {}
        for error_type in error_types:
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1

        # Slow queries
        slow_queries = sum(1 for d in durations if d > SLOW_QUERY_THRESHOLD_MS)

        # Requests per minute
        if timestamps:
            time_span_minutes = (timestamps[-1] - timestamps[0]).total_seconds() / 60
            requests_per_minute = (
                total_requests / time_span_minutes if time_span_minutes > 0 else 0.0
            )
        else:
            requests_per_minute = 0.0

        return AggregatedMetrics(
            tool_name=tool_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_latency_ms=statistics.mean(durations),
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            min_latency_ms=min(durations),
            max_latency_ms=max(durations),
            total_duration_ms=sum(durations),
            error_rate_percent=(failed_requests / total_requests * 100)
            if total_requests > 0
            else 0.0,
            avg_memory_mb=statistics.mean(memories) if memories else None,
            avg_cpu_percent=statistics.mean(cpus) if cpus else None,
            cache_hit_rate_percent=(sum(cache_hits) / len(cache_hits) * 100)
            if cache_hits
            else None,
            error_types=error_type_counts,
            slow_queries=slow_queries,
            requests_per_minute=requests_per_minute,
            first_seen=timestamps[0] if timestamps else None,
            last_seen=timestamps[-1] if timestamps else None,
        )

    def get_all_metrics(self, days: int = 7) -> Dict[str, AggregatedMetrics]:
        """
        Get metrics for all tools.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary mapping tool names to AggregatedMetrics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT DISTINCT tool_name
                FROM performance_metrics
                WHERE timestamp >= ?
            """,
                (cutoff_str,),
            )

            tool_names = [row[0] for row in cursor.fetchall()]

        return {name: self.get_metrics(name, days) for name in tool_names}

    def get_slowest_tools(self, days: int = 7, limit: int = 10) -> List[AggregatedMetrics]:
        """
        Get slowest tools by average latency.

        Args:
            days: Number of days to look back
            limit: Maximum number of tools to return

        Returns:
            List of AggregatedMetrics sorted by avg_latency_ms descending
        """
        all_metrics = self.get_all_metrics(days)
        sorted_metrics = sorted(
            all_metrics.values(), key=lambda m: m.avg_latency_ms, reverse=True
        )
        return sorted_metrics[:limit]

    def get_most_used_tools(self, days: int = 7, limit: int = 10) -> List[AggregatedMetrics]:
        """
        Get most frequently used tools.

        Args:
            days: Number of days to look back
            limit: Maximum number of tools to return

        Returns:
            List of AggregatedMetrics sorted by total_requests descending
        """
        all_metrics = self.get_all_metrics(days)
        sorted_metrics = sorted(
            all_metrics.values(), key=lambda m: m.total_requests, reverse=True
        )
        return sorted_metrics[:limit]

    def detect_alerts(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        Detect performance issues and anomalies.

        Args:
            days: Number of days to analyze

        Returns:
            List of alert dictionaries
        """
        alerts = []
        all_metrics = self.get_all_metrics(days)

        for tool_name, metrics in all_metrics.items():
            # High error rate alert
            if metrics.error_rate_percent > ERROR_RATE_THRESHOLD_PERCENT:
                alerts.append(
                    {
                        "type": "HIGH_ERROR_RATE",
                        "tool": tool_name,
                        "severity": "HIGH",
                        "message": f"Error rate {metrics.error_rate_percent:.2f}% exceeds threshold {ERROR_RATE_THRESHOLD_PERCENT}%",
                        "value": metrics.error_rate_percent,
                        "threshold": ERROR_RATE_THRESHOLD_PERCENT,
                    }
                )

            # Slow queries alert
            if metrics.slow_queries > 0:
                slow_query_rate = (metrics.slow_queries / metrics.total_requests * 100)
                if slow_query_rate > 10:  # More than 10% slow queries
                    alerts.append(
                        {
                            "type": "SLOW_QUERIES",
                            "tool": tool_name,
                            "severity": "MEDIUM",
                            "message": f"{metrics.slow_queries} slow queries detected ({slow_query_rate:.1f}% of requests)",
                            "value": metrics.slow_queries,
                            "rate": slow_query_rate,
                        }
                    )

            # High memory usage alert
            if metrics.avg_memory_mb and metrics.avg_memory_mb > HIGH_MEMORY_THRESHOLD_MB:
                alerts.append(
                    {
                        "type": "HIGH_MEMORY",
                        "tool": tool_name,
                        "severity": "MEDIUM",
                        "message": f"Average memory usage {metrics.avg_memory_mb:.2f}MB exceeds threshold {HIGH_MEMORY_THRESHOLD_MB}MB",
                        "value": metrics.avg_memory_mb,
                        "threshold": HIGH_MEMORY_THRESHOLD_MB,
                    }
                )

        return alerts

    def export_to_json(self, days: int = 7, output_file: Optional[str] = None) -> str:
        """
        Export metrics to JSON format.

        Args:
            days: Number of days to export
            output_file: Optional file path to save to

        Returns:
            JSON string
        """
        all_metrics = self.get_all_metrics(days)
        data = {
            "export_time": datetime.utcnow().isoformat(),
            "days": days,
            "tools": {name: metrics.to_dict() for name, metrics in all_metrics.items()},
        }

        json_str = json.dumps(data, indent=2)

        if output_file:
            with open(output_file, "w") as f:
                f.write(json_str)

        return json_str

    def export_to_prometheus(self, days: int = 1) -> str:
        """
        Export metrics to Prometheus text format.

        Args:
            days: Number of days to export

        Returns:
            Prometheus-formatted metrics string
        """
        all_metrics = self.get_all_metrics(days)
        lines = []

        for tool_name, metrics in all_metrics.items():
            # Request count
            lines.append(
                f'# HELP agentswarm_tool_requests_total Total requests for tool'
            )
            lines.append(f'# TYPE agentswarm_tool_requests_total counter')
            lines.append(
                f'agentswarm_tool_requests_total{{tool="{tool_name}"}} {metrics.total_requests}'
            )

            # Success count
            lines.append(
                f'agentswarm_tool_requests_success{{tool="{tool_name}"}} {metrics.successful_requests}'
            )

            # Failure count
            lines.append(
                f'agentswarm_tool_requests_failed{{tool="{tool_name}"}} {metrics.failed_requests}'
            )

            # Latency metrics
            lines.append(f'# HELP agentswarm_tool_latency_ms Tool latency in milliseconds')
            lines.append(f'# TYPE agentswarm_tool_latency_ms summary')
            lines.append(
                f'agentswarm_tool_latency_ms{{tool="{tool_name}",quantile="0.5"}} {metrics.p50_latency_ms}'
            )
            lines.append(
                f'agentswarm_tool_latency_ms{{tool="{tool_name}",quantile="0.95"}} {metrics.p95_latency_ms}'
            )
            lines.append(
                f'agentswarm_tool_latency_ms{{tool="{tool_name}",quantile="0.99"}} {metrics.p99_latency_ms}'
            )

            # Error rate
            lines.append(f'# HELP agentswarm_tool_error_rate Error rate percentage')
            lines.append(f'# TYPE agentswarm_tool_error_rate gauge')
            lines.append(
                f'agentswarm_tool_error_rate{{tool="{tool_name}"}} {metrics.error_rate_percent}'
            )

        return "\n".join(lines)

    def get_resource_usage(self) -> Dict[str, float]:
        """
        Get current resource usage.

        Returns:
            Dictionary with memory_mb and cpu_percent
        """
        if not PSUTIL_AVAILABLE or not self._process:
            return {"memory_mb": 0.0, "cpu_percent": 0.0}

        try:
            memory_info = self._process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            cpu_percent = self._process.cpu_percent(interval=0.1)

            return {"memory_mb": memory_mb, "cpu_percent": cpu_percent}
        except Exception:
            return {"memory_mb": 0.0, "cpu_percent": 0.0}

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of a list."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None
_enabled = os.getenv("PERFORMANCE_MONITORING_ENABLED", "true").lower() == "true"


def get_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor."""
    global _monitor
    if _monitor is None:
        db_path = os.getenv("PERFORMANCE_DB_PATH")
        retention_days = int(os.getenv("PERFORMANCE_RETENTION_DAYS", "30"))
        _monitor = PerformanceMonitor(db_path=db_path, retention_days=retention_days)
    return _monitor


def track_performance(func: Callable) -> Callable:
    """
    Decorator to automatically track performance of a function.

    Usage:
        @track_performance
        def my_function():
            # Implementation
            pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _enabled:
            return func(*args, **kwargs)

        monitor = get_monitor()
        start_time = time.time()
        resource_before = monitor.get_resource_usage()
        success = False
        error_type = None

        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_type = e.__class__.__name__
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            resource_after = monitor.get_resource_usage()

            # Determine tool name
            tool_name = "unknown"
            if args and hasattr(args[0], "tool_name"):
                tool_name = args[0].tool_name
            elif hasattr(func, "__self__") and hasattr(func.__self__, "tool_name"):
                tool_name = func.__self__.tool_name

            metric = PerformanceMetric(
                tool_name=tool_name,
                timestamp=datetime.utcnow(),
                duration_ms=duration_ms,
                success=success,
                memory_mb=resource_after["memory_mb"] - resource_before["memory_mb"],
                cpu_percent=resource_after["cpu_percent"],
                error_type=error_type,
            )

            monitor.record_metric(metric)

    return wrapper


def record_performance_metric(
    tool_name: str,
    duration_ms: float,
    success: bool = True,
    error_type: Optional[str] = None,
    api_calls: int = 0,
    cache_hit: bool = False,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Manually record a performance metric.

    Args:
        tool_name: Name of the tool
        duration_ms: Duration in milliseconds
        success: Whether the operation succeeded
        error_type: Type of error if failed
        api_calls: Number of API calls made
        cache_hit: Whether cache was hit
        metadata: Additional metadata
    """
    if not _enabled:
        return

    monitor = get_monitor()
    resources = monitor.get_resource_usage()

    metric = PerformanceMetric(
        tool_name=tool_name,
        timestamp=datetime.utcnow(),
        duration_ms=duration_ms,
        success=success,
        memory_mb=resources["memory_mb"],
        cpu_percent=resources["cpu_percent"],
        api_calls=api_calls,
        cache_hit=cache_hit,
        error_type=error_type,
        metadata=metadata or {},
    )

    monitor.record_metric(metric)


if __name__ == "__main__":
    # Test performance monitoring
    print("Testing Performance Monitoring...")

    # Create test monitor
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db = f.name

    monitor = PerformanceMonitor(db_path=test_db, retention_days=30)

    # Record some test metrics
    for i in range(100):
        metric = PerformanceMetric(
            tool_name="test_tool",
            timestamp=datetime.utcnow(),
            duration_ms=100 + i * 10,
            success=i % 10 != 0,  # 10% failure rate
            memory_mb=50.0 + i * 0.5,
            cpu_percent=10.0 + i * 0.2,
            api_calls=1,
            cache_hit=i % 3 == 0,
            error_type="TestError" if i % 10 == 0 else None,
        )
        monitor.record_metric(metric)

    # Get aggregated metrics
    metrics = monitor.get_metrics("test_tool", days=1)
    print(f"\nAggregated Metrics for 'test_tool':")
    print(f"  Total Requests: {metrics.total_requests}")
    print(f"  Success Rate: {100 - metrics.error_rate_percent:.2f}%")
    print(f"  Avg Latency: {metrics.avg_latency_ms:.2f}ms")
    print(f"  P50 Latency: {metrics.p50_latency_ms:.2f}ms")
    print(f"  P95 Latency: {metrics.p95_latency_ms:.2f}ms")
    print(f"  P99 Latency: {metrics.p99_latency_ms:.2f}ms")
    print(f"  Slow Queries: {metrics.slow_queries}")

    # Detect alerts
    alerts = monitor.detect_alerts(days=1)
    print(f"\nAlerts: {len(alerts)}")
    for alert in alerts:
        print(f"  [{alert['severity']}] {alert['type']}: {alert['message']}")

    # Export to JSON
    json_export = monitor.export_to_json(days=1)
    print(f"\nJSON Export (first 500 chars):\n{json_export[:500]}...")

    # Cleanup
    os.unlink(test_db)
    print("\n✓ Performance monitoring test complete!")
