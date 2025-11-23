"""
Unit tests for GenerateOrganizationChart tool
"""

import os

import pytest

from shared.errors import ValidationError

from .generate_organization_chart import GenerateOrganizationChart


@pytest.fixture(autouse=True)
def setup_mock_mode():
    """Enable mock mode for all tests."""
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    os.environ.pop("USE_MOCK_APIS", None)


class TestGenerateOrganizationChart:
    """Test suite for GenerateOrganizationChart tool."""

    def test_simple_two_level_hierarchy(self):
        """Test creating a simple two-level org chart."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "ceo", "name": "CEO"},
                {"id": "cto", "name": "CTO", "parent": "ceo"},
                {"id": "cfo", "name": "CFO", "parent": "ceo"},
            ],
            title="Simple Org",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["statistics"]["total_nodes"] == 3
        assert result["result"]["statistics"]["depth"] == 1
        assert result["result"]["statistics"]["root_nodes"] == 1

    def test_complex_multi_level_hierarchy(self):
        """Test creating a complex multi-level org chart."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "ceo", "name": "CEO", "title": "Chief Executive Officer"},
                {"id": "cto", "name": "CTO", "title": "CTO", "parent": "ceo"},
                {"id": "vp_eng", "name": "VP Engineering", "parent": "cto"},
                {"id": "team_lead", "name": "Team Lead", "parent": "vp_eng"},
            ]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["statistics"]["total_nodes"] == 4
        assert result["result"]["statistics"]["depth"] == 3

    def test_horizontal_orientation(self):
        """Test generating chart with horizontal orientation."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "head", "name": "Department Head"},
                {"id": "member1", "name": "Member 1", "parent": "head"},
            ],
            orientation="horizontal",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["orientation"] == "horizontal"

    def test_vertical_orientation(self):
        """Test generating chart with vertical orientation."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "head", "name": "Department Head"},
                {"id": "member1", "name": "Member 1", "parent": "head"},
            ],
            orientation="vertical",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["orientation"] == "vertical"

    def test_custom_dimensions(self):
        """Test generating chart with custom dimensions."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "node1", "name": "Node 1"},
            ],
            width=1600,
            height=1000,
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["visualization"]["width"] == 1600
        assert result["result"]["visualization"]["height"] == 1000

    def test_node_templates(self):
        """Test different node templates."""
        templates = ["standard", "compact", "detailed"]

        for template in templates:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "node1", "name": "Node 1"},
                ],
                node_template=template,
            )
            result = tool.run()

            assert result["success"] is True
            assert result["result"]["visualization"]["template"] == template

    def test_empty_data_validation_error(self):
        """Test that empty data raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(data=[])
            tool.run()

        assert "empty" in str(exc_info.value).lower()

    def test_missing_required_field(self):
        """Test that missing required field raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "node1"},  # Missing "name"
                ]
            )
            tool.run()

        assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()

    def test_invalid_orientation(self):
        """Test that invalid orientation raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "node1", "name": "Node 1"},
                ],
                orientation="diagonal",  # Invalid
            )
            tool.run()

        assert "orientation" in str(exc_info.value).lower()

    def test_duplicate_node_ids(self):
        """Test that duplicate node IDs raise ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "same", "name": "Node 1"},
                    {"id": "same", "name": "Node 2"},  # Duplicate ID
                ]
            )
            tool.run()

        assert "duplicate" in str(exc_info.value).lower()

    def test_invalid_parent_reference(self):
        """Test that invalid parent reference raises ValidationError."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "node1", "name": "Node 1", "parent": "nonexistent"},
                ]
            )
            tool.run()

        assert "parent" in str(exc_info.value).lower() or "reference" in str(exc_info.value).lower()

    def test_circular_reference_detection(self):
        """Test that circular references are detected."""
        with pytest.raises(Exception) as exc_info:
            tool = GenerateOrganizationChart(
                data=[
                    {"id": "a", "name": "Node A", "parent": "b"},
                    {"id": "b", "name": "Node B", "parent": "a"},  # Circular
                ]
            )
            tool.run()

        assert "circular" in str(exc_info.value).lower()

    def test_multiple_root_nodes(self):
        """Test org chart with multiple root nodes."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "root1", "name": "Root 1"},
                {"id": "root2", "name": "Root 2"},
                {"id": "child1", "name": "Child 1", "parent": "root1"},
            ]
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["statistics"]["root_nodes"] == 2

    def test_hierarchy_tree_building(self):
        """Test that hierarchy tree is correctly built."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "ceo", "name": "CEO"},
                {"id": "cto", "name": "CTO", "parent": "ceo"},
                {"id": "cfo", "name": "CFO", "parent": "ceo"},
            ]
        )
        result = tool.run()

        hierarchy = result["result"]["hierarchy"]
        assert "roots" in hierarchy
        assert hierarchy["node_count"] == 3
        assert len(hierarchy["roots"]) == 1
        assert len(hierarchy["roots"][0]["children"]) == 2

    def test_additional_node_attributes(self):
        """Test that additional node attributes are preserved."""
        tool = GenerateOrganizationChart(
            data=[
                {
                    "id": "ceo",
                    "name": "Jane Smith",
                    "title": "CEO",
                    "department": "Executive",
                    "email": "jane@company.com",
                    "custom_field": "custom_value",
                },
            ]
        )
        result = tool.run()

        assert result["success"] is True
        node = result["result"]["nodes"][0]
        assert node["title"] == "CEO"
        assert node["department"] == "Executive"
        assert node["email"] == "jane@company.com"
        assert node["custom_field"] == "custom_value"

    def test_params_passed_through(self):
        """Test that additional params are passed through to visualization."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "node1", "name": "Node 1"},
            ],
            params={"color_scheme": "blue", "show_photos": True},
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["visualization"]["params"]["color_scheme"] == "blue"
        assert result["result"]["visualization"]["params"]["show_photos"] is True

    def test_mock_mode_indicator(self):
        """Test that mock mode is indicated in results."""
        tool = GenerateOrganizationChart(
            data=[
                {"id": "node1", "name": "Node 1"},
            ]
        )
        result = tool.run()

        assert result["metadata"]["mock_mode"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
