"""
Performance command implementation.

Show performance metrics, reports, and dashboards for all tools.
"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

from ...shared.dashboard import (
    export_dashboard_html,
    export_dashboard_json,
    generate_dashboard_data,
)
from ...shared.monitoring import get_monitor


def execute(args) -> int:
    """Execute the performance command."""
    try:
        monitor = get_monitor()

        if args.subcommand == "report":
            return _show_report(monitor, args)
        elif args.subcommand == "slowest":
            return _show_slowest(monitor, args)
        elif args.subcommand == "most-used":
            return _show_most_used(monitor, args)
        elif args.subcommand == "tool":
            return _show_tool_metrics(monitor, args)
        elif args.subcommand == "alerts":
            return _show_alerts(monitor, args)
        elif args.subcommand == "export":
            return _export_metrics(monitor, args)
        elif args.subcommand == "dashboard":
            return _generate_dashboard(args)
        else:
            # Default: show overview
            return _show_overview(monitor, args)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _show_overview(monitor, args) -> int:
    """Show system-wide performance overview."""
    days = args.days
    all_metrics = monitor.get_all_metrics(days=days)

    if not all_metrics:
        print(f"No performance metrics found for the last {days} days.")
        return 0

    # Calculate totals
    total_requests = sum(m.total_requests for m in all_metrics.values())
    total_success = sum(m.successful_requests for m in all_metrics.values())
    total_failed = sum(m.failed_requests for m in all_metrics.values())

    # Calculate weighted average latency
    if total_requests > 0:
        weighted_latency = sum(m.avg_latency_ms * m.total_requests for m in all_metrics.values())
        avg_latency = weighted_latency / total_requests
    else:
        avg_latency = 0.0

    # Get max p95
    all_p95 = [m.p95_latency_ms for m in all_metrics.values() if m.p95_latency_ms]
    p95_latency = max(all_p95) if all_p95 else 0.0

    print(f"\n=== AgentSwarm Performance Overview (Last {days} Days) ===\n")
    print(f"Total Tools:        {len(all_metrics)}")
    print(f"Total Requests:     {total_requests:,}")
    print(f"Successful:         {total_success:,} ({total_success/total_requests*100:.2f}%)")
    print(f"Failed:             {total_failed:,} ({total_failed/total_requests*100:.2f}%)")
    print(f"\nPerformance:")
    print(f"  Avg Latency:      {avg_latency:.2f}ms")
    print(f"  P95 Latency:      {p95_latency:.2f}ms")

    # Show top 5 slowest and most used
    print(f"\n=== Top 5 Slowest Tools ===")
    slowest = monitor.get_slowest_tools(days=days, limit=5)
    for i, m in enumerate(slowest, 1):
        print(
            f"{i}. {m.tool_name:<30} {m.avg_latency_ms:>8.2f}ms (p95: {m.p95_latency_ms or 0:.2f}ms)"
        )

    print(f"\n=== Top 5 Most Used Tools ===")
    most_used = monitor.get_most_used_tools(days=days, limit=5)
    for i, m in enumerate(most_used, 1):
        print(
            f"{i}. {m.tool_name:<30} {m.total_requests:>6,} requests ({m.success_rate:.1f}% success)"
        )

    # Show alerts if any
    alerts = monitor.detect_alerts(days=1)
    if alerts:
        print(f"\n=== Active Alerts ({len(alerts)}) ===")
        for alert in alerts[:5]:
            severity_icon = "🔴" if alert["severity"] == "HIGH" else "🟡"
            print(f"{severity_icon} [{alert['type']}] {alert['message']}")

    return 0


def _show_report(monitor, args) -> int:
    """Show detailed performance report."""
    days = args.days
    all_metrics = monitor.get_all_metrics(days=days)

    if not all_metrics:
        print(f"No performance metrics found for the last {days} days.")
        return 0

    print(f"\n=== Performance Report (Last {days} Days) ===\n")

    # Sort by total requests
    sorted_tools = sorted(all_metrics.items(), key=lambda x: x[1].total_requests, reverse=True)

    # Print table header
    print(
        f"{'Tool':<30} {'Requests':>10} {'Success':>8} {'Avg (ms)':>10} {'P95 (ms)':>10} {'P99 (ms)':>10} {'Errors':>8}"
    )
    print("-" * 100)

    for tool_name, metrics in sorted_tools:
        print(
            f"{tool_name:<30} "
            f"{metrics.total_requests:>10,} "
            f"{metrics.success_rate:>7.1f}% "
            f"{metrics.avg_latency_ms:>10.2f} "
            f"{metrics.p95_latency_ms or 0:>10.2f} "
            f"{metrics.p99_latency_ms or 0:>10.2f} "
            f"{metrics.failed_requests:>8,}"
        )

    return 0


def _show_slowest(monitor, args) -> int:
    """Show slowest tools."""
    days = args.days
    limit = args.limit if hasattr(args, "limit") else 10

    slowest = monitor.get_slowest_tools(days=days, limit=limit)

    if not slowest:
        print(f"No performance metrics found for the last {days} days.")
        return 0

    print(f"\n=== {len(slowest)} Slowest Tools (Last {days} Days) ===\n")
    print(
        f"{'Rank':<6} {'Tool':<30} {'Avg (ms)':>10} {'P95 (ms)':>10} {'P99 (ms)':>10} {'Requests':>10}"
    )
    print("-" * 80)

    for i, metrics in enumerate(slowest, 1):
        print(
            f"{i:<6} "
            f"{metrics.tool_name:<30} "
            f"{metrics.avg_latency_ms:>10.2f} "
            f"{metrics.p95_latency_ms or 0:>10.2f} "
            f"{metrics.p99_latency_ms or 0:>10.2f} "
            f"{metrics.total_requests:>10,}"
        )

    return 0


def _show_most_used(monitor, args) -> int:
    """Show most used tools."""
    days = args.days
    limit = args.limit if hasattr(args, "limit") else 10

    most_used = monitor.get_most_used_tools(days=days, limit=limit)

    if not most_used:
        print(f"No performance metrics found for the last {days} days.")
        return 0

    print(f"\n=== {len(most_used)} Most Used Tools (Last {days} Days) ===\n")
    print(
        f"{'Rank':<6} {'Tool':<30} {'Requests':>10} {'Success':>8} {'Avg (ms)':>10} {'Errors':>8}"
    )
    print("-" * 80)

    for i, metrics in enumerate(most_used, 1):
        print(
            f"{i:<6} "
            f"{metrics.tool_name:<30} "
            f"{metrics.total_requests:>10,} "
            f"{metrics.success_rate:>7.1f}% "
            f"{metrics.avg_latency_ms:>10.2f} "
            f"{metrics.failed_requests:>8,}"
        )

    return 0


def _show_tool_metrics(monitor, args) -> int:
    """Show detailed metrics for a specific tool."""
    tool_name = args.tool
    days = args.days

    metrics = monitor.get_metrics(tool_name, days=days)

    if metrics.total_requests == 0:
        print(f"No metrics found for tool '{tool_name}' in the last {days} days.")
        return 0

    print(f"\n=== Performance Metrics for '{tool_name}' (Last {days} Days) ===\n")

    print("Requests:")
    print(f"  Total:            {metrics.total_requests:,}")
    print(f"  Successful:       {metrics.successful_requests:,} ({metrics.success_rate:.2f}%)")
    print(f"  Failed:           {metrics.failed_requests:,} ({metrics.error_rate_percent:.2f}%)")

    print("\nLatency:")
    print(f"  Min:              {metrics.min_latency_ms:.2f}ms")
    print(f"  Avg:              {metrics.avg_latency_ms:.2f}ms")
    print(f"  P50 (Median):     {metrics.p50_latency_ms or 0:.2f}ms")
    print(f"  P95:              {metrics.p95_latency_ms or 0:.2f}ms")
    print(f"  P99:              {metrics.p99_latency_ms or 0:.2f}ms")
    print(f"  Max:              {metrics.max_latency_ms:.2f}ms")

    print("\nPerformance:")
    print(
        f"  Slow Queries:     {metrics.slow_queries} ({metrics.slow_queries/metrics.total_requests*100:.1f}%)"
    )
    print(f"  Throughput:       {metrics.requests_per_minute:.2f} req/min")

    if metrics.avg_memory_mb:
        print(f"\nResource Usage:")
        print(f"  Avg Memory:       {metrics.avg_memory_mb:.2f}MB")
        print(f"  Avg CPU:          {metrics.avg_cpu_percent:.2f}%")

    if metrics.cache_hit_rate_percent is not None:
        print(f"\nCaching:")
        print(f"  Cache Hit Rate:   {metrics.cache_hit_rate_percent:.2f}%")

    if metrics.error_types:
        print(f"\nError Breakdown:")
        for error_type, count in sorted(
            metrics.error_types.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {error_type:<20} {count:>5} ({count/metrics.failed_requests*100:.1f}%)")

    if metrics.first_seen and metrics.last_seen:
        print(f"\nActivity:")
        print(f"  First Seen:       {metrics.first_seen.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Seen:        {metrics.last_seen.strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


def _show_alerts(monitor, args) -> int:
    """Show performance alerts."""
    days = args.days
    alerts = monitor.detect_alerts(days=days)

    if not alerts:
        print(f"No performance alerts detected in the last {days} days.")
        return 0

    print(f"\n=== Performance Alerts (Last {days} Days) ===\n")

    # Group by severity
    high = [a for a in alerts if a["severity"] == "HIGH"]
    medium = [a for a in alerts if a["severity"] == "MEDIUM"]
    low = [a for a in alerts if a["severity"] == "LOW"]

    if high:
        print(f"🔴 HIGH SEVERITY ({len(high)}):")
        for alert in high:
            print(f"   [{alert['type']}] {alert['tool']}: {alert['message']}")
        print()

    if medium:
        print(f"🟡 MEDIUM SEVERITY ({len(medium)}):")
        for alert in medium:
            print(f"   [{alert['type']}] {alert['tool']}: {alert['message']}")
        print()

    if low:
        print(f"🟢 LOW SEVERITY ({len(low)}):")
        for alert in low:
            print(f"   [{alert['type']}] {alert['tool']}: {alert['message']}")

    return 0


def _export_metrics(monitor, args) -> int:
    """Export metrics to file."""
    days = args.days
    format = args.format
    output = args.output

    if format == "json":
        json_data = monitor.export_to_json(days=days, output_file=output)
        print(f"Exported metrics to {output}")

    elif format == "prometheus":
        prom_data = monitor.export_to_prometheus(days=days)
        if output:
            with open(output, "w") as f:
                f.write(prom_data)
            print(f"Exported Prometheus metrics to {output}")
        else:
            print(prom_data)

    elif format == "csv":
        all_metrics = monitor.get_all_metrics(days=days)
        output = output or "performance_metrics.csv"

        with open(output, "w", newline="") as csvfile:
            fieldnames = [
                "tool_name",
                "total_requests",
                "successful_requests",
                "failed_requests",
                "success_rate",
                "error_rate",
                "avg_latency_ms",
                "p50_latency_ms",
                "p95_latency_ms",
                "p99_latency_ms",
                "min_latency_ms",
                "max_latency_ms",
                "slow_queries",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for tool_name, metrics in all_metrics.items():
                row = metrics.to_dict()
                # Keep only the fields we want
                filtered_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(filtered_row)

        print(f"Exported metrics to {output}")

    return 0


def _generate_dashboard(args) -> int:
    """Generate dashboard HTML."""
    days = args.days
    output = args.output or "dashboard.html"

    html_file = export_dashboard_html(days=days, output_file=output)
    print(f"\nDashboard generated: {html_file}")
    print(f"\nOpen in browser:")
    print(f"  file://{Path(html_file).absolute()}")

    return 0


if __name__ == "__main__":
    # Test the performance command
    print("Testing performance command...")

    class Args:
        subcommand = None
        days = 7
        limit = 10
        tool = "test_tool"
        format = "json"
        output = None

    args = Args()

    # Test overview
    print("\n--- Testing Overview ---")
    args.subcommand = None
    execute(args)

    print("\n✓ Performance command test complete!")
