"""Tests for audio_generation tool."""

import pytest
from unittest.mock import patch
import uuid
from typing import Dict, Any

from tools.media_generation.audio_generation import AudioGeneration
from shared.errors import ValidationError, APIError


class TestAudioGeneration:
    """Test suite for AudioGeneration."""

    # ========== FIXTURES ==========

    @pytest.fixture
    def valid_prompt(self) -> str:
        return "Generate a calm piano melody"

    @pytest.fixture
    def valid_params(self) -> Dict[str, Any]:
        return {"voice": "female", "duration": 30}

    @pytest.fixture
    def tool(self, valid_prompt: str, valid_params: Dict[str, Any]) -> AudioGeneration:
        return AudioGeneration(prompt=valid_prompt, params=valid_params)

    @pytest.fixture
    def mock_uuid(self):
        with patch("uuid.uuid4", return_value=uuid.UUID(int=123)):
            yield

    # ========== INITIALIZATION TESTS ==========

    def test_initialization(self, valid_prompt, valid_params):
        tool = AudioGeneration(prompt=valid_prompt, params=valid_params)
        assert tool.prompt == valid_prompt
        assert tool.params == valid_params
        assert tool.tool_name == "audio_generation"
        assert tool.tool_category == "media_generation"

    # ========== HAPPY PATH TESTS ==========

    def test_execute_success(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "result" in result
        assert "audio_id" in result["result"]

    def test_metadata_correct(self, tool):
        result = tool.run()
        metadata = result["metadata"]
        assert metadata["tool_name"] == "audio_generation"
        assert metadata["params_used"] == tool.params

    def test_process_return_structure(self, tool):
        result = tool.run()["result"]
        assert "audio_id" in result
        assert "audio_url" in result
        assert "prompt_used" in result
        assert "parameters_used" in result

    # ========== MOCK MODE TESTS ==========

    @patch.dict("os.environ", {"USE_MOCK_APIS": "true"})
    def test_mock_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert result["metadata"]["mock_mode"] is True
        assert result["result"]["mock"] is True
        assert "audio_url" in result["result"]

    @patch.dict("os.environ", {"USE_MOCK_APIS": "false"})
    def test_real_mode(self, tool):
        result = tool.run()
        assert result["success"] is True
        assert "mock_mode" not in result["metadata"]

    # ========== VALIDATION TESTS ==========

    def test_invalid_prompt_empty(self):
        with pytest.raises(ValidationError):
            tool = AudioGeneration(prompt="", params={"voice": "male"})
            tool.run()

    def test_invalid_params_not_dict(self, valid_prompt):
        with pytest.raises(ValidationError):
            tool = AudioGeneration(prompt=valid_prompt, params="not_a_dict")
            tool.run()

    def test_invalid_param_key(self, valid_prompt):
        with pytest.raises(ValidationError):
            tool = AudioGeneration(prompt=valid_prompt, params={"invalid": "x"})
            tool.run()

    # ========== ERROR CASES ==========

    def test_api_error_handled(self, tool):
        with patch.object(tool, "_process", side_effect=Exception("API failed")):
            with pytest.raises(APIError):
                tool.run()

    # ========== EDGE CASES ==========

    def test_unicode_prompt(self):
        tool = AudioGeneration(prompt="生成音乐", params={})
        result = tool.run()
        assert result["success"] is True

    def test_special_characters(self):
        tool = AudioGeneration(prompt="sound @#$%^&*", params={})
        result = tool.run()
        assert result["success"] is True

    def test_empty_params_allowed(self, valid_prompt):
        tool = AudioGeneration(prompt=valid_prompt, params={})
        result = tool.run()
        assert result["success"] is True

    # ========== PARAMETRIZED TESTS ==========

    @pytest.mark.parametrize(
        "param_key", ["voice", "duration", "style", "format", "seed", "model"]
    )
    def test_valid_param_keys(self, valid_prompt, param_key):
        tool = AudioGeneration(prompt=valid_prompt, params={param_key: "x"})
        result = tool.run()
        assert result["success"] is True

    @pytest.mark.parametrize(
        "prompt,expected_valid",
        [
            ("Short prompt", True),
            ("a", True),
            ("", False),
        ],
    )
    def test_prompt_validation(self, prompt, expected_valid):
        if expected_valid:
            tool = AudioGeneration(prompt=prompt, params={})
            result = tool.run()
            assert result["success"] is True
        else:
            with pytest.raises(ValidationError):
                tool = AudioGeneration(prompt=prompt, params={})
                tool.run()

    # ========== INTEGRATION TESTS ==========

    def test_integration_process_flow(self, tool):
        result = tool.run()
        assert result["success"] is True

    def test_integration_env_toggle(self, tool):
        with patch.dict("os.environ", {"USE_MOCK_APIS": "true"}):
            mock_result = tool.run()
        with patch.dict("os.environ", {"USE_MOCK_APIS": "false"}):
            real_result = tool.run()
        assert mock_result["result"]["mock"] is True
        assert "mock" not in real_result["result"]

    def test_error_formatting_integration(self, tool):
        with patch.object(tool, "_execute", side_effect=ValueError("Test error")):
            result = tool.run()
            assert result.get("success") is False or "error" in result
