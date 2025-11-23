# LinearGetRoadmap Tool

Retrieve Linear roadmap, projects, milestones, and progress tracking with comprehensive filtering and analytics.

## Overview

Get roadmap data with support for:
- Project listing and filtering
- Milestone tracking
- Progress analytics
- Timeline visualization
- Status and health metrics
- Team and cycle associations

## Quick Start

```python
from tools.integrations.linear import LinearGetRoadmap

tool = LinearGetRoadmap(
    team_id="team_xyz",
    status_filter="started",
    include_milestones=True,
    include_progress=True
)

result = tool.run()
print(f"Active projects: {result['roadmap_summary']['total_projects']}")
for project in result['projects']:
    print(f"  {project['name']}: {project['progress']:.0%} complete")
```

## Parameters

All parameters are optional:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `team_id` | str | None | Filter by team ID |
| `status_filter` | str | None | Filter by status (planned, started, paused, completed, canceled) |
| `include_archived` | bool | False | Include archived projects |
| `include_milestones` | bool | True | Include milestone data |
| `include_progress` | bool | True | Calculate progress metrics |
| `date_range_start` | str | None | Filter by start date (ISO 8601) |
| `date_range_end` | str | None | Filter by end date (ISO 8601) |
| `sort_by` | str | "startDate" | Sort by: name, startDate, targetDate, progress |
| `limit` | int | 50 | Max projects (1-100) |

## Return Value

```python
{
    "success": True,
    "projects": [
        {
            "id": "proj_abc123",
            "name": "Q4 Platform Improvements",
            "description": "Major enhancements for Q4",
            "status": "started",
            "progress": 0.65,
            "start_date": "2025-10-01",
            "target_date": "2025-12-31",
            "lead": {"id": "user_123", "name": "Alice"},
            "team": {"id": "team_xyz", "name": "Engineering"},
            "health": "onTrack",
            "issue_count": 23,
            "completed_issues": 15,
            "milestones": [
                {
                    "id": "milestone_1",
                    "name": "Alpha Release",
                    "date": "2025-11-15",
                    "sort_order": 1
                }
            ]
        }
    ],
    "milestones": [
        {
            "id": "milestone_1",
            "name": "Alpha Release",
            "date": "2025-11-15",
            "project_id": "proj_abc123",
            "project_name": "Q4 Platform Improvements"
        }
    ],
    "roadmap_summary": {
        "total_projects": 5,
        "by_status": {
            "started": 3,
            "planned": 2,
            "completed": 0
        },
        "by_health": {
            "onTrack": 3,
            "atRisk": 1,
            "offTrack": 1
        },
        "average_progress": 0.42,
        "total_issues": 87,
        "completed_issues": 35,
        "completion_rate": 0.40
    },
    "timeline": {
        "start_date": "2025-01-01",
        "end_date": "2026-12-31",
        "project_count": 5,
        "milestones_count": 12
    }
}
```

## Examples

### Get All Projects

```python
tool = LinearGetRoadmap()
result = tool.run()

for project in result['projects']:
    print(f"{project['name']}: {project['progress']:.0%}")
```

### Filter by Team and Status

```python
tool = LinearGetRoadmap(
    team_id="team_engineering",
    status_filter="started"
)

result = tool.run()
print(f"Active projects: {result['roadmap_summary']['total_projects']}")
```

### Get Project Milestones

```python
tool = LinearGetRoadmap(
    include_milestones=True,
    sort_by="targetDate"
)

result = tool.run()
for milestone in result['milestones']:
    print(f"{milestone['date']}: {milestone['name']} ({milestone['project_name']})")
```

### Filter by Date Range

```python
tool = LinearGetRoadmap(
    date_range_start="2025-01-01",
    date_range_end="2025-12-31",
    sort_by="progress"
)

result = tool.run()
for project in result['projects']:
    print(f"{project['name']}: {project['progress']:.0%} complete")
```

### Health Dashboard

```python
tool = LinearGetRoadmap(team_id="team_xyz")
result = tool.run()

summary = result['roadmap_summary']
print("Project Health:")
print(f"  ✅ On Track: {summary['by_health']['onTrack']}")
print(f"  ⚠️  At Risk: {summary['by_health']['atRisk']}")
print(f"  🚨 Off Track: {summary['by_health']['offTrack']}")
```

## Status Values

| Status | Description |
|--------|-------------|
| `planned` | Not yet started |
| `started` | In progress |
| `paused` | Temporarily halted |
| `completed` | Finished |
| `canceled` | Not proceeding |

## Health Values

| Health | Indicator |
|--------|-----------|
| `onTrack` | Progressing as planned |
| `atRisk` | May miss targets |
| `offTrack` | Behind schedule |

## Sorting Options

| Sort By | Description |
|---------|-------------|
| `name` | Alphabetical |
| `startDate` | Earliest first |
| `targetDate` | Due date |
| `progress` | Completion percentage |

## Use Cases

### Release Planning

```python
def get_release_status(release_date):
    tool = LinearGetRoadmap(
        date_range_end=release_date,
        include_milestones=True,
        sort_by="progress"
    )

    result = tool.run()

    at_risk = [p for p in result['projects'] if p['health'] == 'atRisk']
    off_track = [p for p in result['projects'] if p['health'] == 'offTrack']

    if off_track:
        print(f"🚨 {len(off_track)} projects off track!")
    elif at_risk:
        print(f"⚠️ {len(at_risk)} projects at risk")
    else:
        print("✅ All projects on track")

    return result

get_release_status("2025-12-31")
```

### Progress Reporting

```python
def generate_progress_report(team_id):
    tool = LinearGetRoadmap(
        team_id=team_id,
        include_progress=True
    )

    result = tool.run()
    summary = result['roadmap_summary']

    print(f"Team Progress Report")
    print(f"Total Projects: {summary['total_projects']}")
    print(f"Average Progress: {summary['average_progress']:.0%}")
    print(f"Completion Rate: {summary['completion_rate']:.0%}")
    print(f"\nIssues: {summary['completed_issues']}/{summary['total_issues']}")

    return result

generate_progress_report("team_eng")
```

### Milestone Tracking

```python
def upcoming_milestones(days=30):
    from datetime import datetime, timedelta

    end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    tool = LinearGetRoadmap(
        include_milestones=True,
        date_range_end=end_date
    )

    result = tool.run()
    milestones = sorted(result['milestones'], key=lambda m: m['date'])

    print(f"Upcoming Milestones (next {days} days):")
    for m in milestones:
        print(f"  {m['date']}: {m['name']} ({m['project_name']})")

    return milestones

upcoming_milestones(30)
```

## Best Practices

1. **Regular Reviews**: Check roadmap weekly for health status
2. **Filter Appropriately**: Use team/status filters to focus
3. **Track Milestones**: Monitor critical dates
4. **Monitor Health**: Address at-risk projects proactively
5. **Analyze Progress**: Use metrics for sprint retrospectives

## See Also

- [LinearCreateIssue](./linear_create_issue_README.md) - Create issues
- [LinearAssignTeam](./linear_assign_team_README.md) - Team assignment
- [Main README](./README.md) - Complete Linear integration guide
