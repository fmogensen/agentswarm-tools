"""
Diagram renderers for specialized diagram types.
Consolidates rendering logic for fishbone, flow, mind map, and organization charts.
"""

from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from .base_renderer import BaseRenderer
from shared.errors import ValidationError


class FishboneDiagramRenderer(BaseRenderer):
    """Renderer for fishbone (Ishikawa) diagrams."""

    def validate_data(self, data: Any) -> None:
        """Validate fishbone diagram data format."""
        if not isinstance(data, dict):
            raise ValidationError("Fishbone data must be a dict")
        if "effect" not in data:
            raise ValidationError("Fishbone data must have 'effect' field")
        if "causes" not in data or not isinstance(data["causes"], dict):
            raise ValidationError("Fishbone data must have 'causes' dict")

    def render(
        self,
        data: Dict[str, Any],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render fishbone diagram."""
        self.validate_data(data)
        options = options or {}

        # Return structured data representation
        # Note: Full matplotlib fishbone rendering is complex
        # For now, return structured data that can be rendered client-side
        result = {
            "diagram_type": "fishbone",
            "effect": data["effect"],
            "causes": data["causes"],
            "title": title or "Fishbone Diagram",
        }

        return result


class FlowDiagramRenderer(BaseRenderer):
    """Renderer for flow diagrams."""

    def validate_data(self, data: Any) -> None:
        """Validate flow diagram data format."""
        if not isinstance(data, dict):
            raise ValidationError("Flow diagram data must be a dict")
        if "nodes" not in data or not isinstance(data["nodes"], list):
            raise ValidationError("Flow diagram must have 'nodes' list")
        if "edges" not in data or not isinstance(data["edges"], list):
            raise ValidationError("Flow diagram must have 'edges' list")

    def render(
        self,
        data: Dict[str, List],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render flow diagram."""
        self.validate_data(data)
        options = options or {}

        # Return structured data representation
        result = {
            "diagram_type": "flow",
            "nodes": data["nodes"],
            "edges": data["edges"],
            "title": title or "Flow Diagram",
            "orientation": options.get("orientation", "TB"),
        }

        return result


class MindMapRenderer(BaseRenderer):
    """Renderer for mind maps."""

    def validate_data(self, data: Any) -> None:
        """Validate mind map data format."""
        if not isinstance(data, dict):
            raise ValidationError("Mind map data must be a dict")
        if "root" not in data:
            raise ValidationError("Mind map must have 'root' node")
        if "children" not in data.get("root", {}):
            data["root"]["children"] = []

    def render(
        self,
        data: Dict[str, Any],
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render mind map."""
        self.validate_data(data)
        options = options or {}

        # Return structured data representation
        result = {
            "diagram_type": "mindmap",
            "root": data["root"],
            "title": title or "Mind Map",
            "layout": options.get("layout", "radial"),
        }

        return result


class OrganizationChartRenderer(BaseRenderer):
    """Renderer for organization charts."""

    def validate_data(self, data: Any) -> None:
        """Validate organization chart data format."""
        if not isinstance(data, list):
            raise ValidationError("Organization chart data must be a list of nodes")
        if len(data) == 0:
            raise ValidationError("Organization chart cannot be empty")

        for node in data:
            if not isinstance(node, dict):
                raise ValidationError("Each node must be a dict")
            if "id" not in node:
                raise ValidationError("Each node must have an 'id' field")

    def render(
        self,
        data: List[Dict[str, Any]],
        title: str = "",
        width: int = 1200,
        height: int = 800,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Render organization chart."""
        self.validate_data(data)
        options = options or {}

        def _render(data, title, width, height, opts):
            """
            Simple organization chart rendering using matplotlib.
            For complex org charts, recommend using specialized libraries.
            """
            fig, ax = self.create_figure(width, height)

            # Build hierarchy
            nodes_by_level = self._build_hierarchy(data)

            # Calculate positions
            positions = self._calculate_positions(nodes_by_level, width, height)

            # Draw nodes and connections
            for node_id, (x, y) in positions.items():
                node = next(n for n in data if n["id"] == node_id)

                # Draw node box
                box = mpatches.FancyBboxPatch(
                    (x - 40, y - 20),
                    80,
                    40,
                    boxstyle="round,pad=5",
                    facecolor="lightblue",
                    edgecolor="black",
                    linewidth=1,
                )
                ax.add_patch(box)

                # Add text
                name = node.get("name", node_id)
                ax.text(x, y, name, ha="center", va="center", fontsize=8)

                # Draw connection to parent
                parent_id = node.get("parent")
                if parent_id and parent_id in positions:
                    parent_x, parent_y = positions[parent_id]
                    ax.plot([parent_x, x], [parent_y - 20, y + 20], "k-", linewidth=1)

            ax.set_xlim(-10, width + 10)
            ax.set_ylim(-10, height + 10)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title(title or "Organization Chart", pad=20)

            return fig

        return self.safe_render(_render, data, title, width, height, options)

    def _build_hierarchy(self, data: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """Build hierarchy levels from flat node list."""
        # Find root nodes (no parent)
        roots = [n["id"] for n in data if "parent" not in n or n["parent"] is None]

        if not roots:
            # If no root, use first node
            roots = [data[0]["id"]]

        levels = {0: roots}
        node_to_level = {r: 0 for r in roots}

        # Build parent-child mapping
        children_map = {}
        for node in data:
            parent = node.get("parent")
            if parent:
                if parent not in children_map:
                    children_map[parent] = []
                children_map[parent].append(node["id"])

        # BFS to assign levels
        current_level = 0
        while current_level in levels:
            next_level_nodes = []
            for node_id in levels[current_level]:
                if node_id in children_map:
                    next_level_nodes.extend(children_map[node_id])

            if next_level_nodes:
                next_level = current_level + 1
                levels[next_level] = next_level_nodes
                for n in next_level_nodes:
                    node_to_level[n] = next_level

            current_level += 1

        return levels

    def _calculate_positions(
        self, levels: Dict[int, List[str]], width: int, height: int
    ) -> Dict[str, tuple]:
        """Calculate x, y positions for each node."""
        positions = {}
        num_levels = len(levels)

        for level_num, nodes in levels.items():
            y = height - (level_num * (height / (num_levels + 1)))
            num_nodes = len(nodes)

            for i, node_id in enumerate(nodes):
                x = (i + 1) * (width / (num_nodes + 1))
                positions[node_id] = (x, y)

        return positions


# Diagram renderer registry
DIAGRAM_RENDERERS = {
    "fishbone": FishboneDiagramRenderer(),
    "flow": FlowDiagramRenderer(),
    "mindmap": MindMapRenderer(),
    "org_chart": OrganizationChartRenderer(),
}
