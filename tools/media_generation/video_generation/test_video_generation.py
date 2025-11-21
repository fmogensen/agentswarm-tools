"""Tests for video_generation tool."""

import pytest
from unittest.mock import patch, MagicMock
import time

from tools.media_generation.video_generation import VideoGeneration
from shared.errors import ValidationError, APIError


class TestVideoGeneration:
    """Test suite for VideoGeneration."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "Generate a short video of a waterfall"

    @pytest.fixture
    def valid_params(self) -> dict:
        return {"duration": 7}

    @pytest.fixture
    def tool(self, valid_prompt, valid_params) -> VideoGeneration:
        return VideoGeneration(prompt=valid_prompt, params=valid_params)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_prompt, valid_params):
        tool = VideoGeneration(prompt=valid_prompt, params=valid_params)
        assert tool.prompt == valid_prompt
        assert tool.params == valid_params
        assert tool.tool_name == "video_generation"
        assert tool.tool_category == "media_generation"
        assert "video clips" in tool.tool_description

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool: VideoGeneration):
        with patch("time.sleep", return_value=None):
            result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert "video_url" in result["result"]
        assert result["metadata"]["input_length"] == len(tool.prompt)

    def test_default_duration_used(self, valid_prompt):
        tool = VideoGeneration(prompt=valid_prompt)
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["result"]["duration"] == 6

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: VideoGeneration):
        result = tool.run()
        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["metadata"]["mock_mode"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool: VideoGeneration):
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["success"] is True
        assert "mock" not in result["result"]

    # ========== VALIDATION TESTS ==========

    def test_empty_prompt_validation(self):
        with pytest.raises(ValidationError):
            tool = VideoGeneration(prompt="   ", params={})
            tool.run()

    @pytest.mark.parametrize(
        "params",
        [
            123,
            "not a dict",
            None,
        ],
    )
    def test_invalid_params_type(self, valid_prompt, params):
        with pytest.raises(ValidationError):
            tool = VideoGeneration(prompt=valid_prompt, params=params)
            tool.run()

    @pytest.mark.parametrize("duration", [0, 4, 11, -1, "ten"])
    def test_invalid_duration_values(self, valid_prompt, duration):
        with pytest.raises(ValidationError):
            tool = VideoGeneration(prompt=valid_prompt, params={"duration": duration})
            tool.run()

    # ========== API ERROR TESTS ==========

    def test_api_error_propagation(self, tool: VideoGeneration):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self, valid_params):
        tool = VideoGeneration(prompt="生成一个短视频", params=valid_params)
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self, valid_params):
        tool = VideoGeneration(prompt="video @!#$%^&*() test", params=valid_params)
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["success"] is True

    def test_min_length_prompt(self, valid_params):
        tool = VideoGeneration(prompt="a", params=valid_params)
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["success"] is True

    def test_max_length_prompt(self, valid_params):
        long_prompt = "a" * 2000
        tool = VideoGeneration(prompt=long_prompt, params=valid_params)
        with patch("time.sleep", return_value=None):
            result = tool.run()
        assert result["metadata"]["input_length"] == 2000

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,params,expected_valid",
        [
            ("valid prompt", {"duration": 5}, True),
            ("valid prompt", {"duration": 10}, True),
            ("", {}, False),
            (" ", {"duration": 7}, False),
            ("valid prompt", {"duration": 11}, False),
            ("valid prompt", {"duration": 4}, False),
        ],
    )
    def test_parameter_validation(self, prompt, params, expected_valid):
        if expected_valid:
            tool = VideoGeneration(prompt=prompt, params=params)
            with patch("time.sleep", return_value=None):
                result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = VideoGeneration(prompt=prompt, params=params)
                tool.run()

    # ========== INTERNAL METHOD TESTS ==========

    def test_generate_mock_results_format(self, tool):
        result = tool._generate_mock_results()
        assert result["success"] is True
        assert "video_url" in result["result"]
        assert result["result"]["mock"] is True

    def test_should_use_mock(self, tool):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            assert tool._should_use_mock() is True
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            assert tool._should_use_mock() is False

    def test_process_returns_expected_format(self, tool):
        with patch("time.sleep", return_value=None):
            result = tool._process()
        assert "video_url" in result
        assert "duration" in result
        assert result["input_prompt"] == tool.prompt

    # ========== INTEGRATION TESTS ==========

    def test_run_handles_unexpected_internal_error(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("unexpected")):
            output = tool.run()
            assert output["success"] is False
            assert "error" in output
