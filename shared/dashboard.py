"""
Performance dashboard data generation for AgentSwarm Tools.

Generates dashboard-ready JSON data for visualizing performance metrics.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from .monitoring import get_monitor, AggregatedMetrics


def generate_dashboard_data(days: int = 7) -> Dict[str, Any]:
    """
    Generate comprehensive dashboard data.

    Args:
        days: Number of days to look back

    Returns:
        Dictionary with dashboard data including:
        - overview: System-wide metrics
        - tools: Per-tool metrics
        - slowest_tools: Top 10 slowest tools
        - most_used_tools: Top 10 most used tools
        - alerts: Active performance alerts
        - trends: Time-series data for charts
    """
    monitor = get_monitor()

    # Get all metrics
    all_metrics = monitor.get_all_metrics(days=days)

    # Calculate system-wide overview
    overview = _calculate_overview(all_metrics)

    # Get slowest tools
    slowest_tools = monitor.get_slowest_tools(days=days, limit=10)

    # Get most used tools
    most_used_tools = monitor.get_most_used_tools(days=days, limit=10)

    # Detect alerts
    alerts = monitor.detect_alerts(days=1)

    # Generate trends data
    trends = _generate_trends(days=days)

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "period_days": days,
        "overview": overview,
        "tools": {name: metrics.to_dict() for name, metrics in all_metrics.items()},
        "slowest_tools": [m.to_dict() for m in slowest_tools],
        "most_used_tools": [m.to_dict() for m in most_used_tools],
        "alerts": alerts,
        "trends": trends,
    }


def _calculate_overview(all_metrics: Dict[str, AggregatedMetrics]) -> Dict[str, Any]:
    """Calculate system-wide overview metrics."""
    total_requests = sum(m.total_requests for m in all_metrics.values())
    successful_requests = sum(m.successful_requests for m in all_metrics.values())
    failed_requests = sum(m.failed_requests for m in all_metrics.values())

    # Calculate average latency across all tools (weighted by requests)
    if total_requests > 0:
        weighted_latency = sum(
            m.avg_latency_ms * m.total_requests for m in all_metrics.values()
        )
        avg_latency = weighted_latency / total_requests
    else:
        avg_latency = 0.0

    # Calculate overall p95 latency
    all_p95 = [m.p95_latency_ms for m in all_metrics.values() if m.p95_latency_ms]
    p95_latency = max(all_p95) if all_p95 else 0.0

    # Error rate
    error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0

    # Cache hit rate (if available)
    cache_metrics = [
        m for m in all_metrics.values() if m.cache_hit_rate_percent is not None
    ]
    if cache_metrics:
        weighted_cache_rate = sum(
            m.cache_hit_rate_percent * m.total_requests for m in cache_metrics
        )
        total_cache_requests = sum(m.total_requests for m in cache_metrics)
        cache_hit_rate = (
            weighted_cache_rate / total_cache_requests if total_cache_requests > 0 else 0.0
        )
    else:
        cache_hit_rate = None

    # Throughput (requests per minute)
    throughput = sum(m.requests_per_minute for m in all_metrics.values())

    return {
        "total_tools": len(all_metrics),
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": round(
            (successful_requests / total_requests * 100) if total_requests > 0 else 0.0, 2
        ),
        "error_rate": round(error_rate, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "cache_hit_rate": round(cache_hit_rate, 2) if cache_hit_rate is not None else None,
        "throughput_rpm": round(throughput, 2),
    }


def _generate_trends(days: int = 7) -> Dict[str, Any]:
    """
    Generate time-series trends data for charts.

    Returns daily aggregated metrics for the past N days.
    """
    monitor = get_monitor()
    trends = {
        "daily_requests": [],
        "daily_errors": [],
        "daily_avg_latency": [],
        "daily_p95_latency": [],
    }

    # Generate data for each day
    for i in range(days, 0, -1):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        # Get metrics for this specific day
        day_metrics = monitor.get_all_metrics(days=1)

        # Aggregate for the day
        total_requests = sum(m.total_requests for m in day_metrics.values())
        total_errors = sum(m.failed_requests for m in day_metrics.values())

        # Calculate weighted average latency
        if total_requests > 0:
            weighted_latency = sum(
                m.avg_latency_ms * m.total_requests for m in day_metrics.values()
            )
            avg_latency = weighted_latency / total_requests
        else:
            avg_latency = 0.0

        # Get max p95 latency for the day
        all_p95 = [m.p95_latency_ms for m in day_metrics.values() if m.p95_latency_ms]
        p95_latency = max(all_p95) if all_p95 else 0.0

        trends["daily_requests"].append({"date": date_str, "value": total_requests})
        trends["daily_errors"].append({"date": date_str, "value": total_errors})
        trends["daily_avg_latency"].append(
            {"date": date_str, "value": round(avg_latency, 2)}
        )
        trends["daily_p95_latency"].append(
            {"date": date_str, "value": round(p95_latency, 2)}
        )

    return trends


def export_dashboard_json(days: int = 7, output_file: str = "dashboard.json") -> str:
    """
    Export dashboard data to JSON file.

    Args:
        days: Number of days to look back
        output_file: Output file path

    Returns:
        Path to exported file
    """
    data = generate_dashboard_data(days=days)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    return output_file


def export_dashboard_html(days: int = 7, output_file: str = "dashboard.html") -> str:
    """
    Export dashboard data as HTML with embedded charts.

    Args:
        days: Number of days to look back
        output_file: Output file path

    Returns:
        Path to exported file
    """
    data = generate_dashboard_data(days=days)

    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentSwarm Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .metric-card.error {{
            border-left-color: #dc3545;
        }}
        .metric-card.success {{
            border-left-color: #28a745;
        }}
        .metric-card.warning {{
            border-left-color: #ffc107;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .metric-value {{
            color: #333;
            font-size: 28px;
            font-weight: bold;
        }}
        .metric-unit {{
            color: #999;
            font-size: 16px;
            margin-left: 5px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
        }}
        .chart-title {{
            color: #333;
            font-size: 18px;
            margin-bottom: 15px;
            font-weight: 600;
        }}
        .alerts {{
            margin-top: 30px;
        }}
        .alert {{
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 4px solid;
        }}
        .alert.HIGH {{
            background: #fff3cd;
            border-left-color: #dc3545;
        }}
        .alert.MEDIUM {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        .alert.LOW {{
            background: #d1ecf1;
            border-left-color: #17a2b8;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AgentSwarm Performance Dashboard</h1>
        <p class="subtitle">Generated: {generated_at} | Period: {period_days} days</p>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{total_requests}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{success_rate}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card {error_class}">
                <div class="metric-label">Error Rate</div>
                <div class="metric-value">{error_rate}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Latency</div>
                <div class="metric-value">{avg_latency}<span class="metric-unit">ms</span></div>
            </div>
            <div class="metric-card {p95_class}">
                <div class="metric-label">P95 Latency</div>
                <div class="metric-value">{p95_latency}<span class="metric-unit">ms</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tools</div>
                <div class="metric-value">{total_tools}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">Daily Requests Trend</div>
                <canvas id="requestsChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Daily Average Latency</div>
                <canvas id="latencyChart"></canvas>
            </div>
        </div>

        {alerts_section}

        <h2 style="margin-top: 40px; margin-bottom: 20px;">Slowest Tools (Top 10)</h2>
        <table>
            <thead>
                <tr>
                    <th>Tool Name</th>
                    <th>Avg Latency (ms)</th>
                    <th>P95 Latency (ms)</th>
                    <th>Total Requests</th>
                    <th>Error Rate (%)</th>
                </tr>
            </thead>
            <tbody>
                {slowest_tools_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 40px; margin-bottom: 20px;">Most Used Tools (Top 10)</h2>
        <table>
            <thead>
                <tr>
                    <th>Tool Name</th>
                    <th>Total Requests</th>
                    <th>Success Rate (%)</th>
                    <th>Avg Latency (ms)</th>
                    <th>P95 Latency (ms)</th>
                </tr>
            </thead>
            <tbody>
                {most_used_tools_rows}
            </tbody>
        </table>
    </div>

    <script>
        const trendsData = {trends_data};

        // Requests Chart
        new Chart(document.getElementById('requestsChart'), {{
            type: 'line',
            data: {{
                labels: trendsData.daily_requests.map(d => d.date),
                datasets: [{{
                    label: 'Requests',
                    data: trendsData.daily_requests.map(d => d.value),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.3
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});

        // Latency Chart
        new Chart(document.getElementById('latencyChart'), {{
            type: 'line',
            data: {{
                labels: trendsData.daily_avg_latency.map(d => d.date),
                datasets: [
                    {{
                        label: 'Avg Latency',
                        data: trendsData.daily_avg_latency.map(d => d.value),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.3
                    }},
                    {{
                        label: 'P95 Latency',
                        data: trendsData.daily_p95_latency.map(d => d.value),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.3
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{ legend: {{ position: 'bottom' }} }}
            }}
        }});
    </script>
</body>
</html>
"""

    # Format overview metrics
    overview = data["overview"]
    error_class = "error" if overview["error_rate"] > 10 else "success"
    p95_class = "warning" if overview["p95_latency_ms"] > 1000 else "success"

    # Format alerts section
    if data["alerts"]:
        alerts_html = '<div class="alerts"><h2>Active Alerts</h2>'
        for alert in data["alerts"]:
            alerts_html += f'<div class="alert {alert["severity"]}">{alert["message"]}</div>'
        alerts_html += "</div>"
    else:
        alerts_html = ""

    # Format slowest tools rows
    slowest_rows = ""
    for tool in data["slowest_tools"]:
        slowest_rows += f"""
            <tr>
                <td>{tool['tool_name']}</td>
                <td>{tool['avg_latency_ms']:.2f}</td>
                <td>{tool['p95_latency_ms'] or 'N/A'}</td>
                <td>{tool['total_requests']}</td>
                <td>{tool['error_rate_percent']:.2f}</td>
            </tr>
        """

    # Format most used tools rows
    most_used_rows = ""
    for tool in data["most_used_tools"]:
        success_rate = (tool['successful_requests'] / tool['total_requests'] * 100) if tool['total_requests'] > 0 else 0
        most_used_rows += f"""
            <tr>
                <td>{tool['tool_name']}</td>
                <td>{tool['total_requests']}</td>
                <td>{success_rate:.2f}</td>
                <td>{tool['avg_latency_ms']:.2f}</td>
                <td>{tool['p95_latency_ms'] or 'N/A'}</td>
            </tr>
        """

    # Populate template
    html = html_template.format(
        generated_at=data["generated_at"],
        period_days=data["period_days"],
        total_requests=overview["total_requests"],
        success_rate=overview["success_rate"],
        error_rate=overview["error_rate"],
        error_class=error_class,
        avg_latency=overview["avg_latency_ms"],
        p95_latency=overview["p95_latency_ms"],
        p95_class=p95_class,
        total_tools=overview["total_tools"],
        alerts_section=alerts_html,
        slowest_tools_rows=slowest_rows,
        most_used_tools_rows=most_used_rows,
        trends_data=json.dumps(data["trends"]),
    )

    with open(output_file, "w") as f:
        f.write(html)

    return output_file


if __name__ == "__main__":
    # Test dashboard generation
    print("Testing Dashboard Generation...")

    import tempfile
    import os

    # Create test data
    from .monitoring import PerformanceMonitor, PerformanceMetric

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db = f.name

    monitor = PerformanceMonitor(db_path=test_db, retention_days=30)

    # Record some test metrics
    for i in range(50):
        metric = PerformanceMetric(
            tool_name=f"test_tool_{i % 5}",
            timestamp=datetime.utcnow(),
            duration_ms=100 + i * 5,
            success=i % 10 != 0,
            memory_mb=50.0,
            cpu_percent=10.0,
            error_type="TestError" if i % 10 == 0 else None,
        )
        monitor.record_metric(metric)

    # Generate dashboard data
    dashboard_data = generate_dashboard_data(days=7)
    print(f"\nOverview:")
    print(f"  Total Tools: {dashboard_data['overview']['total_tools']}")
    print(f"  Total Requests: {dashboard_data['overview']['total_requests']}")
    print(f"  Success Rate: {dashboard_data['overview']['success_rate']}%")
    print(f"  Avg Latency: {dashboard_data['overview']['avg_latency_ms']}ms")

    print(f"\nSlowest Tools:")
    for tool in dashboard_data["slowest_tools"][:3]:
        print(f"  {tool['tool_name']}: {tool['avg_latency_ms']}ms")

    print(f"\nAlerts: {len(dashboard_data['alerts'])}")

    # Export to JSON
    json_file = export_dashboard_json(days=7, output_file="/tmp/dashboard.json")
    print(f"\nExported JSON to: {json_file}")

    # Export to HTML
    html_file = export_dashboard_html(days=7, output_file="/tmp/dashboard.html")
    print(f"Exported HTML to: {html_file}")

    # Cleanup
    os.unlink(test_db)
    print("\n✓ Dashboard generation test complete!")
