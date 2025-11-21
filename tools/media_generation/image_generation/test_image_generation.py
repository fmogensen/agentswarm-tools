"""Tests for image_generation tool."""

import pytest
import os
from unittest.mock import patch, MagicMock

from tools.media_generation.image_generation import ImageGeneration
from shared.errors import ValidationError, APIError


class TestImageGeneration:
    """Test suite for ImageGeneration."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "a futuristic city"

    @pytest.fixture
    def valid_params(self) -> dict:
        return {"size": "1024x1024", "steps": 10, "model": "test-model"}

    @pytest.fixture
    def tool(self, valid_prompt, valid_params) -> ImageGeneration:
        return ImageGeneration(prompt=valid_prompt, params=valid_params)

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_prompt, valid_params):
        tool = ImageGeneration(prompt=valid_prompt, params=valid_params)
        assert tool.prompt == valid_prompt
        assert tool.params == valid_params
        assert tool.tool_name == "image_generation"
        assert tool.tool_category == "media_generation"

    # ========== HAPPY PATH TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_execute_success(self, tool: ImageGeneration):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is False
        assert "image_url" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_process_called(self, tool):
        with patch.object(
            tool, "_process", return_value={"image_url": "x"}
        ) as mock_process:
            tool.run()
            mock_process.assert_called_once()

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool: ImageGeneration):
        result = tool.run()

        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_result_format(self, tool):
        result = tool.run()

        assert result["result"]["prompt"] == tool.prompt
        assert result["result"]["params"] == tool.params

    # ========== VALIDATION TESTS ==========

    @pytest.mark.parametrize("bad_prompt", ["", " ", None])
    def test_invalid_prompts(self, bad_prompt):
        with pytest.raises(ValidationError):
            tool = ImageGeneration(prompt=bad_prompt, params={})
            tool.run()

    def test_invalid_params_type(self):
        with pytest.raises(ValidationError):
            tool = ImageGeneration(prompt="test", params="not a dict")
            tool.run()

    @pytest.mark.parametrize("size", ["1000", 123, None])
    def test_invalid_size(self, size):
        with pytest.raises(ValidationError):
            tool = ImageGeneration(prompt="test", params={"size": size})
            tool.run()

    @pytest.mark.parametrize("steps", [0, -5, "ten"])
    def test_invalid_steps(self, steps):
        with pytest.raises(ValidationError):
            tool = ImageGeneration(prompt="test", params={"steps": steps})
            tool.run()

    # ========== API ERROR TESTS ==========

    def test_api_error_raised(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASE TESTS ==========

    def test_unicode_prompt(self):
        tool = ImageGeneration(prompt="城市景观", params={"size": "512x512"})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters_prompt(self):
        tool = ImageGeneration(prompt="image @#$% generation!", params={})
        result = tool.run()
        assert result["success"] is True

    def test_empty_params(self):
        tool = ImageGeneration(prompt="simple prompt", params={})
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "prompt,params,valid",
        [
            ("test", {"size": "128x128"}, True),
            ("test", {"steps": 5}, True),
            ("", {"size": "128x128"}, False),
            ("test", {"steps": -1}, False),
            ("test", {"size": "invalid-size"}, False),
        ],
    )
    def test_param_validation_matrix(self, prompt, params, valid):
        if valid:
            tool = ImageGeneration(prompt=prompt, params=params)
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(Exception):
                tool = ImageGeneration(prompt=prompt, params=params)
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_full_workflow(self):
        tool = ImageGeneration(
            prompt="mountain landscape", params={"size": "512x512", "steps": 5}
        )
        result = tool.run()

        assert result["success"] is True
        assert "image_url" in result["result"]

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("Bad")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
