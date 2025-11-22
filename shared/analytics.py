"""
Analytics and monitoring system for AgentSwarm Tools.
Tracks requests, performance, errors, and usage metrics.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import os
from pathlib import Path
import threading
from collections import defaultdict


class EventType(Enum):
    """Types of analytics events."""

    TOOL_START = "tool_start"
    TOOL_SUCCESS = "tool_success"
    TOOL_ERROR = "tool_error"
    API_CALL = "api_call"
    RATE_LIMIT = "rate_limit"
    VALIDATION_ERROR = "validation_error"


@dataclass
class AnalyticsEvent:
    """Single analytics event."""

    event_type: EventType
    tool_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: Optional[float] = None
    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ToolMetrics:
    """Aggregated metrics for a tool."""

    tool_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    error_count_by_code: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None

    @property
    def avg_duration_ms(self) -> float:
        """Average request duration."""
        return self.total_duration_ms / self.total_requests if self.total_requests > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Success rate percentage."""
        return (
            (self.successful_requests / self.total_requests * 100)
            if self.total_requests > 0
            else 0.0
        )

    @property
    def error_rate(self) -> float:
        """Error rate percentage."""
        return 100.0 - self.success_rate

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "min_duration_ms": self.min_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "success_rate": round(self.success_rate, 2),
            "error_rate": round(self.error_rate, 2),
            "error_count_by_code": dict(self.error_count_by_code),
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error.isoformat() if self.last_error else None,
        }


class AnalyticsBackend:
    """Base class for analytics backends."""

    def record_event(self, event: AnalyticsEvent) -> None:
        """Record an analytics event."""
        raise NotImplementedError

    def get_metrics(self, tool_name: str, days: int = 7) -> ToolMetrics:
        """Get metrics for a tool."""
        raise NotImplementedError

    def get_all_metrics(self, days: int = 7) -> Dict[str, ToolMetrics]:
        """Get metrics for all tools."""
        raise NotImplementedError


class InMemoryBackend(AnalyticsBackend):
    """In-memory analytics backend for development/testing."""

    def __init__(self):
        self.events: List[AnalyticsEvent] = []
        self._lock = threading.Lock()

    def record_event(self, event: AnalyticsEvent) -> None:
        """Record event in memory."""
        with self._lock:
            self.events.append(event)

    def get_metrics(self, tool_name: str, days: int = 7) -> ToolMetrics:
        """Calculate metrics from in-memory events."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        relevant_events = [
            e for e in self.events if e.tool_name == tool_name and e.timestamp >= cutoff
        ]

        metrics = ToolMetrics(tool_name=tool_name)

        for event in relevant_events:
            if event.event_type == EventType.TOOL_SUCCESS:
                metrics.successful_requests += 1
                metrics.total_requests += 1
                metrics.last_success = event.timestamp

                if event.duration_ms:
                    metrics.total_duration_ms += event.duration_ms
                    if (
                        metrics.min_duration_ms is None
                        or event.duration_ms < metrics.min_duration_ms
                    ):
                        metrics.min_duration_ms = event.duration_ms
                    if (
                        metrics.max_duration_ms is None
                        or event.duration_ms > metrics.max_duration_ms
                    ):
                        metrics.max_duration_ms = event.duration_ms

            elif event.event_type == EventType.TOOL_ERROR:
                metrics.failed_requests += 1
                metrics.total_requests += 1
                metrics.last_error = event.timestamp
                if event.error_code:
                    metrics.error_count_by_code[event.error_code] += 1

        return metrics

    def get_all_metrics(self, days: int = 7) -> Dict[str, ToolMetrics]:
        """Get metrics for all tools."""
        tool_names = set(e.tool_name for e in self.events)
        return {name: self.get_metrics(name, days) for name in tool_names}


class FileBackend(AnalyticsBackend):
    """File-based analytics backend."""

    def __init__(self, log_dir: str = ".analytics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()

    def _get_log_file(self, date: datetime) -> Path:
        """Get log file path for a date."""
        return self.log_dir / f"{date.strftime('%Y-%m-%d')}.jsonl"

    def record_event(self, event: AnalyticsEvent) -> None:
        """Record event to daily log file."""
        with self._lock:
            log_file = self._get_log_file(event.timestamp)
            with open(log_file, "a") as f:
                f.write(json.dumps(event.to_dict()) + "\n")

    def get_metrics(self, tool_name: str, days: int = 7) -> ToolMetrics:
        """Calculate metrics from log files."""
        metrics = ToolMetrics(tool_name=tool_name)
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Read events from daily log files
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            log_file = self._get_log_file(date)

            if not log_file.exists():
                continue

            with open(log_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data["tool_name"] != tool_name:
                            continue

                        event_time = datetime.fromisoformat(data["timestamp"])
                        if event_time < cutoff:
                            continue

                        event_type = EventType(data["event_type"])

                        if event_type == EventType.TOOL_SUCCESS:
                            metrics.successful_requests += 1
                            metrics.total_requests += 1
                            metrics.last_success = event_time

                            if data.get("duration_ms"):
                                duration = data["duration_ms"]
                                metrics.total_duration_ms += duration
                                if (
                                    metrics.min_duration_ms is None
                                    or duration < metrics.min_duration_ms
                                ):
                                    metrics.min_duration_ms = duration
                                if (
                                    metrics.max_duration_ms is None
                                    or duration > metrics.max_duration_ms
                                ):
                                    metrics.max_duration_ms = duration

                        elif event_type == EventType.TOOL_ERROR:
                            metrics.failed_requests += 1
                            metrics.total_requests += 1
                            metrics.last_error = event_time
                            if data.get("error_code"):
                                metrics.error_count_by_code[data["error_code"]] += 1

                    except (json.JSONDecodeError, KeyError):
                        continue

        return metrics

    def get_all_metrics(self, days: int = 7) -> Dict[str, ToolMetrics]:
        """Get metrics for all tools."""
        tool_names = set()

        # Collect all tool names from log files
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            log_file = self._get_log_file(date)

            if not log_file.exists():
                continue

            with open(log_file, "r") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        tool_names.add(data["tool_name"])
                    except (json.JSONDecodeError, KeyError):
                        continue

        return {name: self.get_metrics(name, days) for name in tool_names}


# Global analytics instance
_backend: Optional[AnalyticsBackend] = None
_enabled = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"


def get_backend() -> AnalyticsBackend:
    """Get or create analytics backend."""
    global _backend
    if _backend is None:
        backend_type = os.getenv("ANALYTICS_BACKEND", "file")
        if backend_type == "memory":
            _backend = InMemoryBackend()
        else:
            log_dir = os.getenv("ANALYTICS_LOG_DIR", ".analytics")
            _backend = FileBackend(log_dir=log_dir)
    return _backend


def record_event(event: AnalyticsEvent) -> None:
    """Record an analytics event."""
    if not _enabled:
        return

    try:
        backend = get_backend()
        backend.record_event(event)
    except Exception:
        # Never let analytics crash the tool
        pass


def get_metrics(tool_name: str, days: int = 7) -> ToolMetrics:
    """Get metrics for a tool."""
    backend = get_backend()
    return backend.get_metrics(tool_name, days)


def get_all_metrics(days: int = 7) -> Dict[str, ToolMetrics]:
    """Get metrics for all tools."""
    backend = get_backend()
    return backend.get_all_metrics(days)


def print_metrics(tool_name: Optional[str] = None, days: int = 7) -> None:
    """Print metrics in a formatted way."""
    if tool_name:
        metrics = get_metrics(tool_name, days)
        print(f"\n=== Metrics for {tool_name} (last {days} days) ===")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Successful: {metrics.successful_requests} ({metrics.success_rate:.2f}%)")
        print(f"Failed: {metrics.failed_requests} ({metrics.error_rate:.2f}%)")
        print(f"Avg Duration: {metrics.avg_duration_ms:.2f}ms")
        if metrics.error_count_by_code:
            print("\nErrors by Code:")
            for code, count in sorted(
                metrics.error_count_by_code.items(), key=lambda x: x[1], reverse=True
            ):
                print(f"  {code}: {count}")
    else:
        all_metrics = get_all_metrics(days)
        print(f"\n=== Metrics for All Tools (last {days} days) ===")
        for name, metrics in sorted(all_metrics.items()):
            print(f"\n{name}:")
            print(
                f"  Requests: {metrics.total_requests}, Success Rate: {metrics.success_rate:.2f}%"
            )
            print(f"  Avg Duration: {metrics.avg_duration_ms:.2f}ms")
