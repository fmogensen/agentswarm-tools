"""
Generate Organization Chart - Create hierarchical organization structure visualizations
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class GenerateOrganizationChart(BaseTool):
    """
    Generate organization chart for hierarchical structure visualization.

    This tool creates visual organization charts showing reporting relationships,
    team structures, and organizational hierarchies.

    Args:
        data: Organization structure data as list of nodes with hierarchical relationships
        title: Chart title
        width: Chart width in pixels
        height: Chart height in pixels
        orientation: Chart orientation (vertical, horizontal)
        node_template: Template for node display (name, title, department, etc.)
        params: Additional chart parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Generated chart data and visualization
        - metadata: Chart metadata

    Example:
        >>> tool = GenerateOrganizationChart(
        ...     data=[
        ...         {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
        ...         {"id": "cto", "name": "CTO", "title": "Chief Technology Officer", "parent": "ceo"},
        ...         {"id": "dev1", "name": "Dev Lead", "title": "Development Lead", "parent": "cto"}
        ...     ],
        ...     title="Company Organization"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "generate_organization_chart"
    tool_category: str = "visualization"

    # Required parameters
    data: List[Dict[str, Any]] = Field(
        ..., description="List of organization nodes with id, name, title, and optional parent"
    )

    # Optional parameters
    title: Optional[str] = Field(None, description="Chart title", max_length=200)

    width: Optional[int] = Field(1200, description="Chart width in pixels", ge=400, le=4000)

    height: Optional[int] = Field(800, description="Chart height in pixels", ge=300, le=3000)

    orientation: str = Field(
        "vertical", description="Chart orientation: vertical (top-down) or horizontal (left-right)"
    )

    node_template: Optional[str] = Field(
        "standard", description="Node display template: standard, compact, detailed, custom"
    )

    params: Optional[Dict[str, Any]] = Field(
        None, description="Additional chart parameters (colors, spacing, styles, etc.)"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the organization chart generation.

        Returns:
            Dict with chart data and visualization
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "tool_version": "1.0.0",
                    "chart_type": "organization",
                    "node_count": len(self.data),
                },
            }
        except Exception as e:
            raise APIError(f"Failed to generate org chart: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate data
        if not self.data:
            raise ValidationError("Data cannot be empty", tool_name=self.tool_name, field="data")

        if not isinstance(self.data, list):
            raise ValidationError(
                "Data must be a list of node objects",
                tool_name=self.tool_name,
                field="data",
                details={"data_type": str(type(self.data))},
            )

        # Validate each node
        required_fields = ["id", "name"]
        for i, node in enumerate(self.data):
            if not isinstance(node, dict):
                raise ValidationError(
                    f"Node at index {i} must be a dictionary",
                    tool_name=self.tool_name,
                    field="data",
                    details={"node_index": i, "node_type": str(type(node))},
                )

            for field in required_fields:
                if field not in node:
                    raise ValidationError(
                        f"Node at index {i} missing required field: {field}",
                        tool_name=self.tool_name,
                        field="data",
                        details={"node_index": i, "missing_field": field, "node": node},
                    )

        # Validate orientation
        valid_orientations = ["vertical", "horizontal"]
        if self.orientation not in valid_orientations:
            raise ValidationError(
                f"Orientation must be one of: {', '.join(valid_orientations)}",
                tool_name=self.tool_name,
                field="orientation",
                details={"provided": self.orientation, "valid": valid_orientations},
            )

        # Validate node_template
        valid_templates = ["standard", "compact", "detailed", "custom"]
        if self.node_template and self.node_template not in valid_templates:
            raise ValidationError(
                f"Node template must be one of: {', '.join(valid_templates)}",
                tool_name=self.tool_name,
                field="node_template",
                details={"provided": self.node_template, "valid": valid_templates},
            )

        # Validate hierarchy consistency
        self._validate_hierarchy()

    def _validate_hierarchy(self) -> None:
        """
        Validate that the organizational hierarchy is consistent.

        Raises:
            ValidationError: If hierarchy is invalid
        """
        node_ids = {node["id"] for node in self.data}

        # Check for duplicate IDs
        if len(node_ids) != len(self.data):
            raise ValidationError(
                "Duplicate node IDs found in data", tool_name=self.tool_name, field="data"
            )

        # Validate parent references
        for node in self.data:
            if "parent" in node and node["parent"] is not None:
                if node["parent"] not in node_ids:
                    raise ValidationError(
                        f"Node '{node['id']}' references non-existent parent '{node['parent']}'",
                        tool_name=self.tool_name,
                        field="data",
                        details={"node_id": node["id"], "parent_id": node["parent"]},
                    )

        # Check for circular references
        self._check_circular_references()

    def _check_circular_references(self) -> None:
        """
        Check for circular parent-child references.

        Raises:
            ValidationError: If circular reference detected
        """

        def has_cycle(node_id: str, visited: set, parent_map: dict) -> bool:
            if node_id in visited:
                return True
            visited.add(node_id)

            parent = parent_map.get(node_id)
            if parent:
                return has_cycle(parent, visited, parent_map)

            visited.remove(node_id)
            return False

        # Build parent map
        parent_map = {}
        for node in self.data:
            if "parent" in node and node["parent"] is not None:
                parent_map[node["id"]] = node["parent"]

        # Check each node
        for node in self.data:
            if has_cycle(node["id"], set(), parent_map):
                raise ValidationError(
                    f"Circular reference detected involving node '{node['id']}'",
                    tool_name=self.tool_name,
                    field="data",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "chart_type": "organization",
                "orientation": self.orientation,
                "nodes": self.data,
                "hierarchy": self._build_hierarchy_tree(),
                "visualization": {
                    "width": self.width,
                    "height": self.height,
                    "title": self.title or "Organization Chart",
                    "template": self.node_template,
                    "url": f"mock://org-chart-{hash(str(self.data)) % 10000}.svg",
                    "format": "svg",
                },
                "statistics": {
                    "total_nodes": len(self.data),
                    "depth": self._calculate_hierarchy_depth(),
                    "root_nodes": len(
                        [n for n in self.data if "parent" not in n or n["parent"] is None]
                    ),
                },
                "message": "[MOCK] Organization chart generated successfully",
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic for organization chart generation.

        Returns:
            Dict containing the generated chart data
        """
        # Build hierarchy tree
        hierarchy = self._build_hierarchy_tree()

        # Calculate statistics
        stats = {
            "total_nodes": len(self.data),
            "depth": self._calculate_hierarchy_depth(),
            "root_nodes": len([n for n in self.data if "parent" not in n or n["parent"] is None]),
            "leaf_nodes": len(
                [
                    n
                    for n in self.data
                    if n["id"] not in {node.get("parent") for node in self.data if "parent" in node}
                ]
            ),
        }

        # In a real implementation, this would:
        # 1. Call a chart rendering library (D3.js, vis.js, etc.)
        # 2. Generate SVG or canvas output
        # 3. Apply styling based on template
        # 4. Upload to storage and return URL

        return {
            "chart_type": "organization",
            "orientation": self.orientation,
            "nodes": self.data,
            "hierarchy": hierarchy,
            "visualization": {
                "width": self.width,
                "height": self.height,
                "title": self.title or "Organization Chart",
                "template": self.node_template,
                "params": self.params or {},
                "format": "svg",
                "status": "generated",
            },
            "statistics": stats,
            "message": f"Organization chart generated successfully with {stats['total_nodes']} nodes",
        }

    def _build_hierarchy_tree(self) -> Dict[str, Any]:
        """
        Build hierarchical tree structure from flat data.

        Returns:
            Nested dictionary representing the org hierarchy
        """
        # Create node lookup
        nodes_by_id = {node["id"]: {**node, "children": []} for node in self.data}

        # Build tree
        roots = []
        for node in self.data:
            node_id = node["id"]
            parent_id = node.get("parent")

            if parent_id is None:
                roots.append(nodes_by_id[node_id])
            elif parent_id in nodes_by_id:
                nodes_by_id[parent_id]["children"].append(nodes_by_id[node_id])

        return {"roots": roots, "node_count": len(self.data)}

    def _calculate_hierarchy_depth(self) -> int:
        """
        Calculate the maximum depth of the organizational hierarchy.

        Returns:
            Maximum depth (root = 0)
        """

        def get_depth(node_id: str, parent_map: dict, memo: dict) -> int:
            if node_id in memo:
                return memo[node_id]

            parent = parent_map.get(node_id)
            if parent is None:
                depth = 0
            else:
                depth = 1 + get_depth(parent, parent_map, memo)

            memo[node_id] = depth
            return depth

        # Build parent map
        parent_map = {}
        for node in self.data:
            if "parent" in node and node["parent"] is not None:
                parent_map[node["id"]] = node["parent"]

        # Calculate max depth
        memo = {}
        max_depth = 0
        for node in self.data:
            depth = get_depth(node["id"], parent_map, memo)
            max_depth = max(max_depth, depth)

        return max_depth


if __name__ == "__main__":
    # Test the tool
    print("Testing GenerateOrganizationChart...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Simple 3-level hierarchy
    print("\n=== Test 1: Simple Organization ===")
    tool1 = GenerateOrganizationChart(
        data=[
            {"id": "ceo", "name": "Jane Smith", "title": "CEO"},
            {"id": "cto", "name": "John Doe", "title": "CTO", "parent": "ceo"},
            {"id": "cfo", "name": "Alice Johnson", "title": "CFO", "parent": "ceo"},
            {"id": "dev1", "name": "Bob Wilson", "title": "Dev Lead", "parent": "cto"},
            {"id": "dev2", "name": "Carol Brown", "title": "Senior Dev", "parent": "cto"},
        ],
        title="Tech Company Org Chart",
    )
    result1 = tool1.run()
    print(f"Success: {result1.get('success')}")
    print(f"Nodes: {result1.get('result', {}).get('statistics', {}).get('total_nodes')}")
    print(f"Depth: {result1.get('result', {}).get('statistics', {}).get('depth')}")

    # Test 2: Horizontal orientation with detailed template
    print("\n=== Test 2: Horizontal Layout ===")
    tool2 = GenerateOrganizationChart(
        data=[
            {
                "id": "head",
                "name": "Department Head",
                "title": "Head of Engineering",
                "department": "Engineering",
            },
            {
                "id": "team1",
                "name": "Team Lead 1",
                "title": "Backend Lead",
                "parent": "head",
                "department": "Backend",
            },
            {
                "id": "team2",
                "name": "Team Lead 2",
                "title": "Frontend Lead",
                "parent": "head",
                "department": "Frontend",
            },
        ],
        title="Engineering Department",
        orientation="horizontal",
        node_template="detailed",
        width=1600,
        height=600,
    )
    result2 = tool2.run()
    print(f"Success: {result2.get('success')}")
    print(f"Orientation: {result2.get('result', {}).get('orientation')}")
    print(f"Template: {result2.get('result', {}).get('visualization', {}).get('template')}")

    # Test 3: Validation error - missing required field
    print("\n=== Test 3: Validation Error (missing name) ===")
    try:
        tool3 = GenerateOrganizationChart(
            data=[
                {"id": "node1"},  # Missing required "name" field
            ]
        )
        result3 = tool3.run()
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")

    # Test 4: Validation error - circular reference
    print("\n=== Test 4: Validation Error (circular reference) ===")
    try:
        tool4 = GenerateOrganizationChart(
            data=[
                {"id": "a", "name": "Node A", "parent": "b"},
                {"id": "b", "name": "Node B", "parent": "a"},  # Circular!
            ]
        )
        result4 = tool4.run()
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")

    # Test 5: Complex multi-level organization
    print("\n=== Test 5: Complex Organization ===")
    tool5 = GenerateOrganizationChart(
        data=[
            {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
            {"id": "cto", "name": "CTO", "title": "Chief Technology Officer", "parent": "ceo"},
            {"id": "cfo", "name": "CFO", "title": "Chief Financial Officer", "parent": "ceo"},
            {"id": "coo", "name": "COO", "title": "Chief Operating Officer", "parent": "ceo"},
            {"id": "eng_vp", "name": "VP Eng", "title": "VP Engineering", "parent": "cto"},
            {"id": "prod_vp", "name": "VP Prod", "title": "VP Product", "parent": "cto"},
            {
                "id": "backend",
                "name": "Backend Lead",
                "title": "Backend Team Lead",
                "parent": "eng_vp",
            },
            {
                "id": "frontend",
                "name": "Frontend Lead",
                "title": "Frontend Team Lead",
                "parent": "eng_vp",
            },
            {
                "id": "mobile",
                "name": "Mobile Lead",
                "title": "Mobile Team Lead",
                "parent": "eng_vp",
            },
        ],
        title="Full Company Structure",
        params={"show_photos": True, "color_by_department": True},
    )
    result5 = tool5.run()
    print(f"Success: {result5.get('success')}")
    stats = result5.get("result", {}).get("statistics", {})
    print(f"Total Nodes: {stats.get('total_nodes')}")
    print(f"Hierarchy Depth: {stats.get('depth')}")
    print(f"Root Nodes: {stats.get('root_nodes')}")
    print(f"Leaf Nodes: {stats.get('leaf_nodes')}")

    print("\n=== All tests completed ===")
