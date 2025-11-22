"""Tests for generate_histogram_chart tool."""

import pytest
import os
from unittest.mock import patch
import numpy as np

from pydantic import ValidationError as PydanticValidationError

from tools.visualization.generate_histogram_chart import GenerateHistogramChart
from shared.errors import ValidationError, APIError


class TestGenerateHistogramChart:
    """Test suite for GenerateHistogramChart."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_params(self):
        return {"data": [1, 2, 3, 4, 5], "bins": 3}

    @pytest.fixture
    def tool(self, valid_params):
        return GenerateHistogramChart(prompt="test histogram", params=valid_params)

    @pytest.fixture
    def mock_data(self):
        return [1, 2, 2, 3, 4, 5, 5]

    # ========== INITIALIZATION TESTS ==========

    def test_tool_initialization(self, valid_params):
        tool = GenerateHistogramChart(prompt="example prompt", params=valid_params)
        assert tool.prompt == "example prompt"
        assert tool.params == valid_params
        assert tool.tool_name == "generate_histogram_chart"
        assert tool.tool_category == "visualization"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "bins" in result["result"]
        assert "counts" in result["result"]
        assert "metadata" in result
        assert result["metadata"]["tool_name"] == "generate_histogram_chart"

    def test_process_histogram_output(self, valid_params):
        tool = GenerateHistogramChart(prompt="test", params=valid_params)
        output = tool._process()
        assert isinstance(output["bins"], list)
        assert isinstance(output["counts"], list)
        assert output["total_points"] == len(valid_params["data"])

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert "bins" in result["result"]
        assert "counts" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"].get("mock_mode") is not True

    # ========== VALIDATION TESTS ==========

    def test_empty_prompt_raises_error(self):
        """Empty prompt raises PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateHistogramChart(prompt="", params={"data": [1, 2]})

    def test_non_dict_params_raises_error(self):
        """Non-dict params raise PydanticValidationError during instantiation."""
        with pytest.raises(PydanticValidationError):
            GenerateHistogramChart(prompt="test", params="not-a-dict")

    def test_missing_data_param_raises_error(self):
        """Missing data param fails custom validation and returns error dict."""
        tool = GenerateHistogramChart(prompt="test", params={})
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize(
        "bad_data",
        [
            None,
            "string",
            [1, "a", 3],
            [None, 1.5],
        ],
    )
    def test_invalid_data_types(self, bad_data):
        """Invalid data types fail custom validation and return error dict."""
        tool = GenerateHistogramChart(prompt="test", params={"data": bad_data})
        result = tool.run()
        assert result["success"] is False

    @pytest.mark.parametrize("bins", [0, -1, 2.5, "ten"])
    def test_invalid_bins(self, bins):
        """Invalid bins fail custom validation and return error dict."""
        tool = GenerateHistogramChart(prompt="test", params={"data": [1, 2, 3], "bins": bins})
        result = tool.run()
        assert result["success"] is False

    # ========== ERROR CASES ==========

    @patch.dict(os.environ, {"USE_MOCK_APIS": "false"})
    def test_api_error_handled(self, tool):
        """Process failure returns error dict."""
        with patch.object(tool, "_process", side_effect=Exception("Histogram failed")):
            result = tool.run()
            assert result["success"] is False

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_np_error(self):
        """Numpy error returns error dict."""
        with patch("numpy.histogram", side_effect=Exception("np error")):
            tool = GenerateHistogramChart(prompt="test", params={"data": [1, 2, 3]})
            result = tool.run()
            assert result["success"] is False

    # ========== EDGE CASES ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_single_value_data(self):
        tool = GenerateHistogramChart(prompt="test", params={"data": [5], "bins": 1})
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["total_points"] == 1

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_large_dataset(self):
        data = list(range(10000))
        tool = GenerateHistogramChart(prompt="test", params={"data": data, "bins": 20})
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["total_points"] == 10000

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_unicode_prompt(self):
        tool = GenerateHistogramChart(prompt="テスト", params={"data": [1, 2, 3]})
        result = tool.run()
        assert result["metadata"]["prompt"] == "テスト"

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,data,bins,valid,pydantic_error",
        [
            ("ok", [1, 2, 3], 5, True, False),
            ("ok", [1], None, True, False),
            ("", [1, 2], 3, False, True),
            ("ok", "not-list", 3, False, False),
            ("ok", [1, 2], 0, False, False),
        ],
    )
    def test_param_validation(self, prompt, data, bins, valid, pydantic_error):
        params = {"data": data}
        if bins is not None:
            params["bins"] = bins

        if pydantic_error:
            with pytest.raises(PydanticValidationError):
                GenerateHistogramChart(prompt=prompt, params=params)
        else:
            tool = GenerateHistogramChart(prompt=prompt, params=params)
            result = tool.run()
            if valid:
                assert result["success"] is True
            else:
                assert result["success"] is False

    # ========== INTEGRATION TESTS ==========

    def test_integration_run_full(self, valid_params):
        tool = GenerateHistogramChart(prompt="integrate", params=valid_params)
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["tool_name"] == "generate_histogram_chart"

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("format error")):
            out = tool.run()
            assert out.get("success") is False or "error" in out
