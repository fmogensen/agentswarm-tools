# LinearAssignTeam Tool

Assign Linear issues to teams and users with capacity planning, workload distribution, and cycle management.

## Overview

Comprehensive team assignment with:
- Team and user assignment
- Cycle/sprint planning
- Capacity and workload management
- Auto-assignment strategies
- Batch operations
- Story point tracking

## Quick Start

```python
from tools.integrations.linear import LinearAssignTeam

tool = LinearAssignTeam(
    issue_ids=["issue_1", "issue_2", "issue_3"],
    team_id="team_xyz",
    cycle_id="cycle_current_sprint",
    auto_assign=True,  # Distribute by workload
    estimate=3.0
)

result = tool.run()
print(f"Assigned {result['assigned_count']} issues")
print(f"Capacity: {result['capacity_summary']['utilization']:.1%}")
```

## Parameters

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `issue_ids` | List[str] | Issue IDs to assign (min 1) |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `team_id` | str | None | Team ID |
| `assignee_id` | str | None | User ID to assign to |
| `cycle_id` | str | None | Cycle/sprint ID |
| `estimate` | float | None | Story points for all issues |
| `auto_assign` | bool | False | Assign to lowest workload member |
| `distribute_evenly` | bool | False | Round-robin distribution |
| `start_date` | str | None | Start date (ISO 8601) |
| `due_date` | str | None | Due date (ISO 8601) |

Note: `auto_assign` and `distribute_evenly` are mutually exclusive.

## Return Value

```python
{
    "success": True,
    "assigned_count": 3,
    "assignments": [
        {
            "issue_id": "issue_1",
            "issue_identifier": "ENG-100",
            "assigned_to": "Alice",
            "assignee_id": "user_123",
            "team": "team_xyz",
            "cycle": "Sprint 12",
            "estimate": 3.0
        }
    ],
    "team_info": {
        "team_id": "team_xyz",
        "team_name": "Engineering",
        "member_count": 5
    },
    "cycle_info": {
        "cycle_id": "cycle_123",
        "cycle_name": "Sprint 12",
        "start_date": "2025-12-01",
        "end_date": "2025-12-14",
        "progress": 0.35
    },
    "capacity_summary": {
        "total_capacity": 50.0,
        "allocated": 25.0,
        "remaining": 25.0,
        "utilization": 0.5,
        "team_size": 5,
        "average_workload": 5.0
    }
}
```

## Examples

### Basic Assignment

```python
tool = LinearAssignTeam(
    issue_ids=["issue_abc123"],
    team_id="team_eng",
    assignee_id="user_alice"
)
```

### Sprint Planning

```python
# Assign backlog to sprint with even distribution
tool = LinearAssignTeam(
    issue_ids=["issue_1", "issue_2", "issue_3", "issue_4", "issue_5"],
    team_id="team_eng",
    cycle_id="cycle_sprint_13",
    distribute_evenly=True,
    estimate=5.0
)

result = tool.run()
print(f"Sprint utilization: {result['capacity_summary']['utilization']:.0%}")
```

### Auto-Assignment (Lowest Workload)

```python
# Automatically assign to member with least work
tool = LinearAssignTeam(
    issue_ids=["urgent_bug_123"],
    team_id="team_eng",
    auto_assign=True
)

result = tool.run()
print(f"Assigned to: {result['assignments'][0]['assigned_to']}")
```

### Batch Assignment with Estimates

```python
issues_with_estimates = [
    ("issue_1", 3.0),
    ("issue_2", 5.0),
    ("issue_3", 2.0)
]

for issue_id, estimate in issues_with_estimates:
    tool = LinearAssignTeam(
        issue_ids=[issue_id],
        team_id="team_eng",
        cycle_id="current_sprint",
        estimate=estimate,
        auto_assign=True
    )
    tool.run()
```

### Capacity-Aware Assignment

```python
def assign_with_capacity_check(issues, team_id, cycle_id):
    tool = LinearAssignTeam(
        issue_ids=issues,
        team_id=team_id,
        cycle_id=cycle_id,
        auto_assign=True
    )

    result = tool.run()

    if result['capacity_summary']['utilization'] > 0.9:
        print("⚠️ Team at 90%+ capacity!")
    elif result['capacity_summary']['utilization'] > 1.0:
        print("🚨 Team over-allocated!")

    return result

assign_with_capacity_check(["issue_1", "issue_2"], "team_eng", "sprint_13")
```

## Assignment Strategies

### Manual Assignment

```python
# Specific assignee
tool = LinearAssignTeam(
    issue_ids=["issue_1"],
    assignee_id="user_alice"
)
```

### Auto-Assign (Workload-Based)

Assigns to team member with lowest current workload:

```python
tool = LinearAssignTeam(
    issue_ids=["issue_1"],
    team_id="team_eng",
    auto_assign=True
)
```

### Even Distribution (Round-Robin)

Distributes issues evenly across team:

```python
tool = LinearAssignTeam(
    issue_ids=[f"issue_{i}" for i in range(10)],
    team_id="team_eng",
    distribute_evenly=True
)
```

## Capacity Planning

The tool calculates team capacity based on:
- Team size (members)
- Current workload (assigned estimates)
- Assumed capacity: 10 points per member per sprint

```python
capacity_summary = {
    "total_capacity": 50.0,      # 5 members × 10 points
    "allocated": 35.0,           # Currently assigned
    "remaining": 15.0,           # Available capacity
    "utilization": 0.7,          # 70% utilized
    "team_size": 5,
    "average_workload": 7.0      # Per member
}
```

## Best Practices

1. **Monitor Capacity**: Keep utilization under 90% for flexibility
2. **Set Estimates**: Always provide estimates for accurate planning
3. **Use Cycles**: Organize work into time-boxed sprints
4. **Balance Workload**: Use auto-assign or distribute_evenly
5. **Review Assignments**: Check capacity_summary after bulk operations

## Workflow Examples

### Sprint Planning Workflow

```python
from tools.integrations.linear import LinearGetRoadmap, LinearAssignTeam

# 1. Get planned work
roadmap = LinearGetRoadmap(
    team_id="team_eng",
    status_filter="planned",
    sort_by="priority",
    limit=20
)
backlog = roadmap.run()

# 2. Select top priority items
top_issues = [p['id'] for p in backlog['projects'][:10]]

# 3. Assign to sprint with capacity check
assign = LinearAssignTeam(
    issue_ids=top_issues,
    team_id="team_eng",
    cycle_id="next_sprint",
    distribute_evenly=True
)
result = assign.run()

# 4. Verify capacity
if result['capacity_summary']['utilization'] > 0.8:
    print("⚠️ Sprint is at 80%+ capacity")
```

## See Also

- [LinearCreateIssue](./linear_create_issue_README.md) - Create issues
- [LinearGetRoadmap](./linear_get_roadmap_README.md) - View roadmap
- [Main README](./README.md) - Complete Linear integration guide
