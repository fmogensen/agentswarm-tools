"""Tests for generate_pie_chart tool."""

import pytest
from unittest.mock import patch, MagicMock
import base64
import os

from tools.visualization.generate_pie_chart import GeneratePieChart
from shared.errors import ValidationError, APIError


class TestGeneratePieChart:
    """Test suite for GeneratePieChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self):
        return {
            "labels": ["A", "B", "C"],
            "values": [10, 20, 30],
            "title": "Test Chart",
        }

    @pytest.fixture
    def tool(self, valid_params) -> GeneratePieChart:
        return GeneratePieChart(prompt="test prompt", params=valid_params)

    @pytest.fixture
    def mock_matplotlib(self):
        with patch("tools.visualization.generate_pie_chart.plt") as mock_plt:
            fig = MagicMock()
            ax = MagicMock()
            mock_plt.subplots.return_value = (fig, ax)
            mock_plt.savefig = MagicMock()
            return mock_plt, fig, ax

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization_success(self, valid_params):
        tool = GeneratePieChart(prompt="hello", params=valid_params)
        assert tool.prompt == "hello"
        assert tool.params == valid_params

    def test_tool_metadata(self, tool):
        assert tool.tool_name == "generate_pie_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH ==========

    def test_execute_success(self, tool, mock_matplotlib):
        mock_plt, _, _ = mock_matplotlib
        mock_plt.savefig.side_effect = lambda *args, **kwargs: args[0].write(b"fakepng")

        result = tool.run()
        assert result["success"] is True
        assert "image_base64" in result["result"]
        decoded = base64.b64decode(result["result"]["image_base64"])
        assert decoded == b"fakepng"

    def test_process_returns_expected_fields(self, tool, mock_matplotlib):
        mock_plt, _, _ = mock_matplotlib
        mock_plt.savefig.side_effect = lambda *args, **kwargs: args[0].write(b"abc")

        result = tool.run()
        assert result["result"]["labels"] == ["A", "B", "C"]
        assert result["result"]["values"] == [10, 20, 30]
        assert result["result"]["title"] == "Test Chart"

    # ========== MOCK MODE ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode_returns_mock_results(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode_runs_process(self, tool, mock_matplotlib):
        mock_plt, _, _ = mock_matplotlib
        mock_plt.savefig.side_effect = lambda *args, **kwargs: args[0].write(b"xyz")

        result = tool.run()
        assert result["success"] is True
        assert "xyz" in base64.b64decode(result["result"]["image_base64"])

    # ========== VALIDATION TESTS ==========

    def test_empty_prompt_raises_error(self, valid_params):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(prompt="", params=valid_params)
            tool.run()

    def test_params_must_be_dict(self):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(prompt="test", params="not a dict")
            tool.run()

    @pytest.mark.parametrize(
        "params",
        [
            {},
            {"labels": ["A"]},
            {"values": [1]},
        ],
    )
    def test_missing_labels_or_values(self, params):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(prompt="x", params=params)
            tool.run()

    def test_labels_and_values_must_be_lists(self):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(prompt="x", params={"labels": "a", "values": "b"})
            tool.run()

    def test_length_mismatch(self):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(
                prompt="x", params={"labels": ["A"], "values": [1, 2]}
            )
            tool.run()

    def test_values_not_numeric(self):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(
                prompt="x", params={"labels": ["A"], "values": ["bad"]}
            )
            tool.run()

    def test_sum_of_values_zero(self):
        with pytest.raises(ValidationError):
            tool = GeneratePieChart(prompt="x", params={"labels": ["A"], "values": [0]})
            tool.run()

    # ========== ERROR HANDLING TESTS ==========

    def test_api_error_wrapped(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("fail")):
            with pytest.raises(APIError):
                tool.run()

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "labels,values,valid",
        [
            (["A"], [1], True),
            (["A", "B"], [10, -10], False),
            (["A"], [0], False),
            ([], [], False),
        ],
    )
    def test_parameter_validation(self, labels, values, valid):
        params = {"labels": labels, "values": values}
        if valid:
            tool = GeneratePieChart(prompt="ok", params=params)
            assert tool.prompt == "ok"
        else:
            with pytest.raises(Exception):
                tool = GeneratePieChart(prompt="ok", params=params)
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self, valid_params):
        tool = GeneratePieChart(prompt="Pie图", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self, valid_params):
        tool = GeneratePieChart(prompt="@#$ Pie!", params=valid_params)
        result = tool.run()
        assert result["success"] is True

    def test_large_values(self, valid_params, mock_matplotlib):
        valid_params["values"] = [1e12, 2e12, 3e12]
        tool = GeneratePieChart(prompt="big", params=valid_params)

        mock_plt, _, _ = mock_matplotlib
        mock_plt.savefig.side_effect = lambda *args, **kwargs: args[0].write(b"big")

        result = tool.run()
        assert result["success"] is True

    # ========== INTEGRATION TESTS ==========

    def test_environment_mock_integration(self, tool):
        with patch.dict(os.environ, {"USE_MOCK_APIS": "true"}):
            result = tool.run()
            assert result["success"] is True
            assert result["result"]["mock"] is True

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("bad")):
            result = tool.run()
            assert "error" in result or result.get("success") is False
