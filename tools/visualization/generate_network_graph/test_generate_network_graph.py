"""Tests for generate_network_graph tool."""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any
import os

from tools.visualization.generate_network_graph import GenerateNetworkGraph
from shared.errors import ValidationError, APIError


class TestGenerateNetworkGraph:
    """Test suite for GenerateNetworkGraph."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self) -> Dict[str, Any]:
        """Valid params fixture."""
        return {
            "entities": ["A", "B", "C"],
            "relationships": [
                {"source": "A", "target": "B", "type": "connected_to"},
                {"source": "B", "target": "C", "type": "related_to"},
            ],
        }

    @pytest.fixture
    def tool(self, valid_params: Dict[str, Any]) -> GenerateNetworkGraph:
        """Create valid tool instance."""
        return GenerateNetworkGraph(prompt="Test graph", params=valid_params)

    @pytest.fixture
    def mock_entities(self):
        return ["A", "B"]

    @pytest.fixture
    def mock_relationships(self):
        return [{"source": "A", "target": "B", "type": "test_rel"}]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_params):
        tool = GenerateNetworkGraph(prompt="Hello", params=valid_params)
        assert tool.prompt == "Hello"
        assert tool.params == valid_params
        assert tool.tool_name == "generate_network_graph"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: GenerateNetworkGraph):
        result = tool.run()
        assert result["success"] is True
        assert "nodes" in result["result"]
        assert "edges" in result["result"]
        assert result["metadata"]["prompt"] == "Test graph"

    def test_process_builds_correct_graph(self, tool):
        result = tool._process()
        assert len(result["nodes"]) == 3
        assert len(result["edges"]) == 2
        assert result["nodes"][0]["id"] == "A"

    # ========== MOCK MODE TESTS ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: GenerateNetworkGraph):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: GenerateNetworkGraph):
        result = tool.run()
        assert result["success"] is True
        assert "mock" not in result["result"]

    # ========== VALIDATION ERROR TESTS ==========

    def test_empty_prompt_raises_validation_error(self):
        with pytest.raises(ValidationError):
            tool = GenerateNetworkGraph(prompt="", params={})
            tool.run()

    def test_params_not_dict_raises_validation_error(self):
        with pytest.raises(ValidationError):
            tool = GenerateNetworkGraph(prompt="Valid", params="not-a-dict")
            tool.run()

    def test_entities_invalid_type(self):
        params = {"entities": "not-a-list", "relationships": []}
        tool = GenerateNetworkGraph(prompt="Test", params=params)
        with pytest.raises(ValidationError):
            tool.run()

    def test_relationship_invalid_type(self):
        params = {"entities": ["A", "B"], "relationships": "invalid"}
        tool = GenerateNetworkGraph(prompt="Test", params=params)
        with pytest.raises(ValidationError):
            tool.run()

    def test_relationship_references_unknown_entity(self):
        params = {"entities": ["A"], "relationships": [{"source": "A", "target": "B"}]}
        tool = GenerateNetworkGraph(prompt="Test", params=params)
        with pytest.raises(ValidationError):
            tool.run()

    # ========== API ERROR TESTS ==========

    def test_api_error_propagates(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("fail")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self, valid_params):
        tool = GenerateNetworkGraph(prompt="测试图", params=valid_params)
        result = tool.run()
        assert result["success"]

    def test_special_characters_prompt(self, valid_params):
        tool = GenerateNetworkGraph(prompt="@#*&$ graph!", params=valid_params)
        result = tool.run()
        assert result["success"]

    def test_empty_entities_and_relationships(self):
        tool = GenerateNetworkGraph(
            prompt="Empty test", params={"entities": [], "relationships": []}
        )
        result = tool.run()
        assert result["success"]
        assert result["result"]["nodes"] == []
        assert result["result"]["edges"] == []

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "entities,relationships,valid",
        [
            (["A"], [], True),
            (["A", "B"], [{"source": "A", "target": "B"}], True),
            ("A", [], False),
            (["A"], "bad-rel", False),
            (["A"], [{"source": "A", "target": "Z"}], False),
        ],
    )
    def test_parameterized_validation(self, entities, relationships, valid):
        params = {"entities": entities, "relationships": relationships}
        if valid:
            tool = GenerateNetworkGraph(prompt="Test", params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = GenerateNetworkGraph(prompt="Test", params=params).run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_run(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "metadata" in result

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("Oops")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
