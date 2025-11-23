# Performance Monitoring Guide

This guide explains how to use the comprehensive performance monitoring and metrics collection system in AgentSwarm Tools Framework.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [CLI Commands](#cli-commands)
- [Programmatic Usage](#programmatic-usage)
- [Metrics Explained](#metrics-explained)
- [Dashboard](#dashboard)
- [Alert System](#alert-system)
- [Best Practices](#best-practices)

## Overview

The performance monitoring system tracks execution metrics for all tools, providing insights into:
- Latency and throughput
- Error rates and types
- Resource usage (CPU, memory)
- Cache hit rates
- Slow query detection
- Percentile metrics (P50, P95, P99)

All metrics are stored in SQLite for minimal overhead (< 5ms per request) and retained for 30 days by default.

## Features

### Automatic Tracking
- All tools automatically track performance metrics
- Integrated into `BaseTool.run()` method
- Zero configuration required

### Comprehensive Metrics
- **Latency**: Min, max, avg, median, P95, P99
- **Throughput**: Requests per minute
- **Error Rates**: Success/failure percentages by error type
- **Resource Usage**: Memory and CPU consumption
- **Cache Performance**: Hit rates and efficiency

### Storage & Export
- SQLite database: `~/.agentswarm/metrics.db`
- Export formats: JSON, CSV, Prometheus
- Automatic data retention and cleanup

### Visualization
- HTML dashboard with interactive charts
- CLI reports and tables
- Real-time alerts

## Quick Start

### View Performance Overview

```bash
agentswarm performance
```

Output:
```
=== AgentSwarm Performance Overview (Last 7 Days) ===

Total Tools:        42
Total Requests:     1,234
Successful:         1,180 (95.62%)
Failed:             54 (4.38%)

Performance:
  Avg Latency:      125.34ms
  P95 Latency:      342.18ms

=== Top 5 Slowest Tools ===
1. video_generation            1234.56ms (p95: 2345.67ms)
2. image_generation            892.34ms (p95: 1456.78ms)
3. audio_transcribe            456.78ms (p95: 890.12ms)
...
```

### Generate Dashboard

```bash
agentswarm performance dashboard -o dashboard.html
```

Open `dashboard.html` in your browser for an interactive visualization.

### View Tool-Specific Metrics

```bash
agentswarm performance tool web_search
```

Output:
```
=== Performance Metrics for 'web_search' (Last 7 Days) ===

Requests:
  Total:            456
  Successful:       440 (96.49%)
  Failed:           16 (3.51%)

Latency:
  Min:              45.23ms
  Avg:              123.45ms
  P50 (Median):     110.67ms
  P95:              234.56ms
  P99:              345.67ms
  Max:              567.89ms

Performance:
  Slow Queries:     5 (1.1%)
  Throughput:       2.3 req/min
```

## Configuration

### Environment Variables

```bash
# Enable/disable performance monitoring (default: true)
export PERFORMANCE_MONITORING_ENABLED=true

# Database path (default: ~/.agentswarm/metrics.db)
export PERFORMANCE_DB_PATH=/custom/path/metrics.db

# Data retention in days (default: 30)
export PERFORMANCE_RETENTION_DAYS=30

# Slow query threshold in milliseconds (default: 1000)
export SLOW_QUERY_THRESHOLD_MS=1000

# High memory threshold in MB (default: 500)
export HIGH_MEMORY_THRESHOLD_MB=500

# Error rate alert threshold in percent (default: 10.0)
export ERROR_RATE_THRESHOLD_PERCENT=10.0
```

### Disable Monitoring

To disable performance monitoring entirely:

```bash
export PERFORMANCE_MONITORING_ENABLED=false
```

Note: Analytics will still be collected separately.

## CLI Commands

### Overview

```bash
agentswarm performance [-d DAYS]
```

Show system-wide performance overview.

### Detailed Report

```bash
agentswarm performance report [-d DAYS]
```

Show detailed table of all tools with metrics.

### Slowest Tools

```bash
agentswarm performance slowest [-d DAYS] [-n LIMIT]
```

Show the slowest tools by average latency.

Example:
```bash
agentswarm performance slowest -d 30 -n 20
```

### Most Used Tools

```bash
agentswarm performance most-used [-d DAYS] [-n LIMIT]
```

Show the most frequently used tools.

### Tool Metrics

```bash
agentswarm performance tool TOOL_NAME [-d DAYS]
```

Show detailed metrics for a specific tool.

Example:
```bash
agentswarm performance tool web_search -d 7
```

### Alerts

```bash
agentswarm performance alerts [-d DAYS]
```

Show active performance alerts (high error rates, slow queries, etc.).

Output:
```
=== Performance Alerts (Last 1 Days) ===

🔴 HIGH SEVERITY (2):
   [HIGH_ERROR_RATE] video_generation: Error rate 15.23% exceeds threshold 10%
   [HIGH_MEMORY] image_generation: Average memory usage 650.45MB exceeds threshold 500MB

🟡 MEDIUM SEVERITY (3):
   [SLOW_QUERIES] crawler: 45 slow queries detected (12.3% of requests)
   ...
```

### Export Metrics

Export to JSON:
```bash
agentswarm performance export -f json -o metrics.json
```

Export to CSV:
```bash
agentswarm performance export -f csv -o metrics.csv
```

Export to Prometheus format:
```bash
agentswarm performance export -f prometheus -o metrics.prom
```

### Dashboard

Generate HTML dashboard:
```bash
agentswarm performance dashboard -d 7 -o dashboard.html
```

## Programmatic Usage

### Using the Monitor Directly

```python
from shared.monitoring import get_monitor

# Get the global monitor instance
monitor = get_monitor()

# Get metrics for a specific tool
metrics = monitor.get_metrics("web_search", days=7)

print(f"Total Requests: {metrics.total_requests}")
print(f"Avg Latency: {metrics.avg_latency_ms}ms")
print(f"P95 Latency: {metrics.p95_latency_ms}ms")
print(f"Success Rate: {metrics.success_rate}%")

# Get all metrics
all_metrics = monitor.get_all_metrics(days=7)
for tool_name, metrics in all_metrics.items():
    print(f"{tool_name}: {metrics.avg_latency_ms}ms")

# Get slowest tools
slowest = monitor.get_slowest_tools(days=7, limit=10)
for metrics in slowest:
    print(f"{metrics.tool_name}: {metrics.avg_latency_ms}ms")

# Detect alerts
alerts = monitor.detect_alerts(days=1)
for alert in alerts:
    print(f"[{alert['severity']}] {alert['message']}")
```

### Manual Metric Recording

```python
from shared.monitoring import record_performance_metric

# Record a performance metric manually
record_performance_metric(
    tool_name="custom_tool",
    duration_ms=150.5,
    success=True,
    api_calls=3,
    cache_hit=False,
    metadata={"custom_field": "value"}
)
```

### Using the Decorator

```python
from shared.monitoring import track_performance

@track_performance
def my_expensive_function():
    # Your code here
    return result
```

The decorator automatically:
- Times the function execution
- Records success/failure
- Tracks resource usage
- Stores metrics in the database

### Dashboard Data Generation

```python
from shared.dashboard import generate_dashboard_data, export_dashboard_html

# Generate dashboard data
data = generate_dashboard_data(days=7)

print(f"Total Tools: {data['overview']['total_tools']}")
print(f"Total Requests: {data['overview']['total_requests']}")

# Export to HTML
html_file = export_dashboard_html(days=7, output_file="dashboard.html")
print(f"Dashboard: {html_file}")
```

## Metrics Explained

### Latency Metrics

- **Min/Max**: Fastest and slowest request times
- **Average**: Mean latency across all requests
- **P50 (Median)**: 50% of requests complete faster than this
- **P95**: 95% of requests complete faster than this (key SLA metric)
- **P99**: 99% of requests complete faster than this (tail latency)

### Slow Queries

Requests exceeding the slow query threshold (default: 1000ms).

Tracked as:
- **Count**: Number of slow queries
- **Percentage**: Slow queries / total requests

### Error Metrics

- **Total Errors**: Number of failed requests
- **Error Rate**: Percentage of failed requests
- **Error Types**: Breakdown by error code (ValidationError, APIError, etc.)

### Resource Usage

- **Memory (MB)**: Average memory consumption per request
- **CPU (%)**: Average CPU usage during execution

### Cache Performance

- **Cache Hit Rate**: Percentage of requests served from cache
- **Cache Impact**: Latency difference between cached and uncached requests

## Dashboard

The HTML dashboard provides:

### Overview Section
- Total requests, success rate, error rate
- Average and P95 latency
- Total tools tracked

### Charts
- Daily requests trend
- Daily latency trend (avg and P95)
- Error rate over time

### Top Tools Tables
- Slowest tools (by avg latency)
- Most used tools (by request count)

### Alerts Section
- Active performance issues
- Color-coded by severity (High/Medium/Low)

### Generate Dashboard

```bash
agentswarm performance dashboard -o dashboard.html
open dashboard.html  # macOS
xdg-open dashboard.html  # Linux
```

## Alert System

The monitoring system automatically detects:

### High Error Rate
Triggered when error rate exceeds threshold (default: 10%)

**Example:**
```
[HIGH_ERROR_RATE] video_generation: Error rate 15.23% exceeds threshold 10%
```

### Slow Queries
Triggered when >10% of requests exceed slow query threshold

**Example:**
```
[SLOW_QUERIES] crawler: 45 slow queries detected (12.3% of requests)
```

### High Memory Usage
Triggered when average memory exceeds threshold (default: 500MB)

**Example:**
```
[HIGH_MEMORY] image_generation: Average memory usage 650.45MB exceeds threshold 500MB
```

### Configuring Thresholds

```bash
# Slow query threshold
export SLOW_QUERY_THRESHOLD_MS=2000

# High memory threshold
export HIGH_MEMORY_THRESHOLD_MB=1000

# Error rate threshold
export ERROR_RATE_THRESHOLD_PERCENT=5.0
```

## Best Practices

### 1. Regular Monitoring

Check performance dashboard weekly:
```bash
agentswarm performance dashboard
```

### 2. Set Up Alerts

Review alerts daily:
```bash
agentswarm performance alerts
```

### 3. Investigate Slow Tools

Identify and optimize slow tools:
```bash
agentswarm performance slowest -n 10
agentswarm performance tool <slow_tool_name>
```

### 4. Monitor Error Patterns

Track error types:
```bash
agentswarm performance tool <tool_name>
# Review "Error Breakdown" section
```

### 5. Optimize Cache Usage

Tools with high latency may benefit from caching:

```python
class MyTool(BaseTool):
    enable_cache = True
    cache_ttl = 3600  # 1 hour
```

### 6. Track Trends

Export metrics regularly for trend analysis:
```bash
agentswarm performance export -f csv -o metrics_$(date +%Y%m%d).csv
```

### 7. Set Appropriate Thresholds

Adjust thresholds based on your requirements:
- API-heavy tools: Higher latency acceptable
- Local tools: Lower latency expected
- Critical tools: Lower error rate threshold

### 8. Use Percentiles, Not Averages

P95/P99 latency is more representative of user experience than average:
```bash
agentswarm performance tool web_search
# Focus on P95 latency, not avg
```

### 9. Monitor Resource Usage

Track memory-intensive tools:
```bash
agentswarm performance report | grep -E "(image|video|audio)"
```

### 10. Export for External Monitoring

Integrate with monitoring systems:
```bash
# Prometheus
agentswarm performance export -f prometheus -o /var/metrics/agentswarm.prom

# Grafana, Datadog, etc.
agentswarm performance export -f json -o /var/metrics/agentswarm.json
```

## Troubleshooting

### No Metrics Displayed

Check if monitoring is enabled:
```bash
echo $PERFORMANCE_MONITORING_ENABLED
```

Verify database exists:
```bash
ls -lh ~/.agentswarm/metrics.db
```

### High Overhead

Performance monitoring adds < 5ms per request. If experiencing higher overhead:

1. Check database size:
```bash
du -h ~/.agentswarm/metrics.db
```

2. Reduce retention period:
```bash
export PERFORMANCE_RETENTION_DAYS=7
```

3. Disable resource tracking (psutil):
```bash
pip uninstall psutil
```

### Missing Historical Data

Data older than retention period is automatically deleted:
```bash
export PERFORMANCE_RETENTION_DAYS=90  # Increase retention
```

### Database Corruption

Reset the database:
```bash
rm ~/.agentswarm/metrics.db
# Database will be recreated on next tool execution
```

## Advanced Usage

### Custom Metrics Storage

Use a custom database location:
```python
from shared.monitoring import PerformanceMonitor

monitor = PerformanceMonitor(
    db_path="/custom/path/metrics.db",
    retention_days=60
)
```

### Batch Export

Export metrics for multiple periods:
```bash
for days in 1 7 30; do
    agentswarm performance export -f json -d $days -o "metrics_${days}d.json"
done
```

### Integration with CI/CD

Add performance checks to CI pipeline:
```bash
#!/bin/bash
# Check error rate threshold
error_rate=$(agentswarm performance export -f json | jq '.overview.error_rate')
if (( $(echo "$error_rate > 5.0" | bc -l) )); then
    echo "ERROR: Error rate $error_rate% exceeds threshold"
    exit 1
fi
```

## Examples

### Example 1: Daily Performance Report

```bash
#!/bin/bash
# daily_report.sh - Send daily performance summary

agentswarm performance report > /tmp/perf_report.txt
agentswarm performance alerts >> /tmp/perf_report.txt

# Send via email or Slack
mail -s "AgentSwarm Daily Performance Report" admin@example.com < /tmp/perf_report.txt
```

### Example 2: Monitoring Specific Tools

```python
from shared.monitoring import get_monitor

monitor = get_monitor()

# Monitor critical tools
critical_tools = ["web_search", "image_generation", "video_generation"]

for tool_name in critical_tools:
    metrics = monitor.get_metrics(tool_name, days=1)

    if metrics.error_rate_percent > 5.0:
        print(f"ALERT: {tool_name} error rate: {metrics.error_rate_percent}%")

    if metrics.p95_latency_ms > 2000:
        print(f"ALERT: {tool_name} P95 latency: {metrics.p95_latency_ms}ms")
```

### Example 3: Performance Comparison

```python
from shared.monitoring import get_monitor

monitor = get_monitor()

# Compare this week vs last week
this_week = monitor.get_metrics("web_search", days=7)
last_week = monitor.get_metrics("web_search", days=14)

latency_change = (this_week.avg_latency_ms - last_week.avg_latency_ms) / last_week.avg_latency_ms * 100

print(f"Latency change: {latency_change:+.1f}%")
```

## Summary

The performance monitoring system provides:
- ✅ Automatic metric collection (< 5ms overhead)
- ✅ Comprehensive latency metrics (P50, P95, P99)
- ✅ Error tracking and analysis
- ✅ Resource usage monitoring
- ✅ Interactive HTML dashboards
- ✅ CLI tools for quick analysis
- ✅ Multiple export formats
- ✅ Intelligent alert detection
- ✅ 30-day data retention

Use `agentswarm performance --help` for full command reference.

For more information, see:
- [Analytics Guide](./ANALYTICS.md)
- [Caching Guide](./CACHING.md)
- [Configuration Guide](./CONFIGURATION.md)
