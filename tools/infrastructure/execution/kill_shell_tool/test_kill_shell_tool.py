"""
Comprehensive tests for KillShellTool
"""

import os
import signal
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from shared.errors import APIError, ValidationError
from tools.infrastructure.execution.kill_shell_tool.kill_shell_tool import (
    KillShellTool,
    _SHELL_REGISTRY,
    get_shell_info,
    list_shells,
    register_shell,
    update_shell_status,
)


@pytest.fixture
def mock_mode():
    """Enable mock mode for testing."""
    original_value = os.getenv("USE_MOCK_APIS")
    os.environ["USE_MOCK_APIS"] = "true"
    yield
    if original_value:
        os.environ["USE_MOCK_APIS"] = original_value
    else:
        os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def clean_registry():
    """Clean shell registry before and after each test."""
    _SHELL_REGISTRY.clear()
    yield
    _SHELL_REGISTRY.clear()


class TestKillShellToolValidation:
    """Test input validation."""

    def test_empty_shell_id(self, mock_mode):
        """Test that empty shell_id raises ValidationError."""
        # Pydantic raises validation error during model initialization
        with pytest.raises(Exception) as exc_info:
            tool = KillShellTool(shell_id="")

        # Either our ValidationError or Pydantic's validation error is acceptable
        assert "shell_id" in str(exc_info.value).lower()

    def test_whitespace_shell_id(self, mock_mode):
        """Test that whitespace-only shell_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            tool = KillShellTool(shell_id="   ")
            tool.run()

        assert "shell_id cannot be empty" in str(exc_info.value)

    def test_negative_timeout(self, mock_mode):
        """Test that negative timeout raises ValidationError."""
        # Pydantic raises validation error during model initialization
        with pytest.raises(Exception) as exc_info:
            tool = KillShellTool(shell_id="test_shell", timeout=-5)

        # Either our ValidationError or Pydantic's validation error is acceptable
        assert "timeout" in str(exc_info.value).lower()

    def test_valid_parameters(self, mock_mode):
        """Test that valid parameters pass validation."""
        tool = KillShellTool(shell_id="test_shell_123", force=False, timeout=5)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["shell_id"] == "test_shell_123"


class TestKillShellToolMockMode:
    """Test mock mode behavior."""

    def test_graceful_termination_mock(self, mock_mode):
        """Test graceful termination in mock mode."""
        tool = KillShellTool(shell_id="mock_shell_001", force=False, timeout=5)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["shell_id"] == "mock_shell_001"
        assert result["result"]["terminated"] == True
        assert result["result"]["signal_used"] == "SIGTERM"
        assert result["result"]["exit_code"] == 0
        assert result["result"]["cleanup_performed"] == True
        assert result["result"]["mock"] == True

    def test_force_termination_mock(self, mock_mode):
        """Test force termination in mock mode."""
        tool = KillShellTool(shell_id="mock_shell_002", force=True)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["signal_used"] == "SIGKILL"
        assert result["result"]["exit_code"] == -9
        assert result["result"]["terminated"] == True

    def test_zero_timeout_mock(self, mock_mode):
        """Test zero timeout (immediate force kill) in mock mode."""
        tool = KillShellTool(shell_id="mock_shell_003", timeout=0)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["signal_used"] == "SIGKILL"

    def test_large_timeout_mock(self, mock_mode):
        """Test large timeout value in mock mode."""
        tool = KillShellTool(shell_id="mock_shell_004", timeout=3600)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["terminated"] == True


class TestKillShellToolRealMode:
    """Test real mode behavior with mocked process operations."""

    def test_non_existent_shell_id(self, clean_registry):
        """Test terminating a non-existent shell raises APIError."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            with pytest.raises(APIError) as exc_info:
                tool = KillShellTool(shell_id="nonexistent_shell")
                tool.run()

            assert "not found in tracking system" in str(exc_info.value)
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_graceful_termination_success(self, clean_registry):
        """Test successful graceful termination."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            # Register a mock shell
            test_pid = 99999
            shell_id = "test_shell_graceful"
            register_shell(shell_id, test_pid, "echo test")

            with patch("os.kill") as mock_kill:
                # Simulate process terminating after SIGTERM
                mock_kill.side_effect = [None, ProcessLookupError()]

                tool = KillShellTool(shell_id=shell_id, force=False, timeout=2)
                result = tool.run()

                assert result["success"] == True
                assert result["result"]["terminated"] == True
                assert result["result"]["signal_used"] == "SIGTERM"
                assert result["result"]["exit_code"] == 0
                assert result["result"]["cleanup_performed"] == True

                # Verify shell was removed from registry
                assert shell_id not in _SHELL_REGISTRY
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_force_termination_immediate(self, clean_registry):
        """Test immediate force termination."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            test_pid = 99998
            shell_id = "test_shell_force"
            register_shell(shell_id, test_pid, "sleep 100")

            with patch("os.kill") as mock_kill:
                tool = KillShellTool(shell_id=shell_id, force=True)
                result = tool.run()

                assert result["success"] == True
                assert result["result"]["signal_used"] == "SIGKILL"
                assert result["result"]["exit_code"] == -9

                # Verify SIGKILL was sent
                mock_kill.assert_called_with(test_pid, signal.SIGKILL)
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_timeout_fallback_to_sigkill(self, clean_registry):
        """Test fallback to SIGKILL when timeout expires."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            test_pid = 99997
            shell_id = "test_shell_timeout"
            register_shell(shell_id, test_pid, "sleep 1000")

            with patch("os.kill") as mock_kill:
                # Process keeps running after SIGTERM
                mock_kill.return_value = None

                with patch("time.sleep"):  # Speed up test
                    tool = KillShellTool(shell_id=shell_id, force=False, timeout=1)
                    result = tool.run()

                    assert result["success"] == True
                    assert "SIGKILL" in result["result"]["signal_used"]
                    assert result["result"]["exit_code"] == -9

                    # Verify both SIGTERM and SIGKILL were sent
                    assert mock_kill.call_count >= 2
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_already_terminated_shell(self, clean_registry):
        """Test terminating a shell that's already terminated."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            test_pid = 99996
            shell_id = "test_shell_terminated"
            register_shell(shell_id, test_pid, "echo done")
            update_shell_status(shell_id, "terminated", exit_code=0)

            tool = KillShellTool(shell_id=shell_id)
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["terminated"] == True
            assert result["result"]["previous_status"] == "terminated"
            assert result["result"]["cleanup_performed"] == True

            # Verify cleanup happened
            assert shell_id not in _SHELL_REGISTRY
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_stopped_shell(self, clean_registry):
        """Test terminating a stopped shell."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            shell_id = "test_shell_stopped"
            register_shell(shell_id, 99995, "stopped_process")
            update_shell_status(shell_id, "stopped")

            tool = KillShellTool(shell_id=shell_id)
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["previous_status"] == "stopped"
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_zombie_shell(self, clean_registry):
        """Test terminating a zombie shell."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            shell_id = "test_shell_zombie"
            register_shell(shell_id, 99994, "zombie_process")
            update_shell_status(shell_id, "zombie")

            tool = KillShellTool(shell_id=shell_id)
            result = tool.run()

            assert result["success"] == True
            assert result["result"]["previous_status"] == "zombie"
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_permission_error(self, clean_registry):
        """Test handling permission error when killing process."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            shell_id = "test_shell_no_permission"
            register_shell(shell_id, 1, "root_process")  # PID 1 usually requires root

            with patch("os.kill") as mock_kill:
                mock_kill.side_effect = PermissionError("Permission denied")

                with pytest.raises(APIError) as exc_info:
                    tool = KillShellTool(shell_id=shell_id)
                    tool.run()

                assert "Permission denied" in str(exc_info.value)
        finally:
            os.environ["USE_MOCK_APIS"] = "true"

    def test_process_not_found(self, clean_registry):
        """Test handling ProcessLookupError (process already gone)."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            shell_id = "test_shell_gone"
            register_shell(shell_id, 99993, "already_gone")

            with patch("os.kill") as mock_kill:
                mock_kill.side_effect = ProcessLookupError()

                tool = KillShellTool(shell_id=shell_id)
                result = tool.run()

                assert result["success"] == True
                assert "process not found" in result["result"]["signal_used"].lower()
        finally:
            os.environ["USE_MOCK_APIS"] = "true"


class TestShellRegistryHelpers:
    """Test shell registry helper functions."""

    def test_register_shell(self, clean_registry):
        """Test registering a new shell."""
        shell_id = "helper_test_001"
        pid = 12345
        command = "echo hello"

        register_shell(shell_id, pid, command)

        assert shell_id in _SHELL_REGISTRY
        shell_info = _SHELL_REGISTRY[shell_id]
        assert shell_info["pid"] == pid
        assert shell_info["command"] == command
        assert shell_info["status"] == "running"
        assert "started_at" in shell_info

    def test_update_shell_status(self, clean_registry):
        """Test updating shell status."""
        shell_id = "helper_test_002"
        register_shell(shell_id, 12346, "test")

        update_shell_status(shell_id, "completed", exit_code=0)

        shell_info = _SHELL_REGISTRY[shell_id]
        assert shell_info["status"] == "completed"
        assert shell_info["exit_code"] == 0

    def test_get_shell_info(self, clean_registry):
        """Test getting shell information."""
        shell_id = "helper_test_003"
        register_shell(shell_id, 12347, "test command")

        info = get_shell_info(shell_id)
        assert info is not None
        assert info["pid"] == 12347
        assert info["command"] == "test command"

        # Non-existent shell
        assert get_shell_info("nonexistent") is None

    def test_list_shells(self, clean_registry):
        """Test listing all shells."""
        register_shell("shell_1", 1001, "cmd1")
        register_shell("shell_2", 1002, "cmd2")
        register_shell("shell_3", 1003, "cmd3")

        shells = list_shells()
        assert len(shells) == 3
        assert "shell_1" in shells
        assert "shell_2" in shells
        assert "shell_3" in shells


class TestMultipleConsecutiveKills:
    """Test multiple consecutive kill operations."""

    def test_kill_multiple_shells_sequentially(self, clean_registry, mock_mode):
        """Test killing multiple shells one after another."""
        shell_ids = [f"shell_{i}" for i in range(5)]

        for shell_id in shell_ids:
            tool = KillShellTool(shell_id=shell_id, force=False)
            result = tool.run()
            assert result["success"] == True

    def test_kill_same_shell_twice(self, clean_registry):
        """Test attempting to kill the same shell twice."""
        os.environ["USE_MOCK_APIS"] = "false"
        try:
            shell_id = "double_kill_test"
            register_shell(shell_id, 99992, "test")

            with patch("os.kill"):
                # First kill
                tool1 = KillShellTool(shell_id=shell_id)
                result1 = tool1.run()
                assert result1["success"] == True

            # Second kill should fail (not in registry anymore)
            with pytest.raises(APIError) as exc_info:
                tool2 = KillShellTool(shell_id=shell_id)
                tool2.run()

            assert "not found" in str(exc_info.value)
        finally:
            os.environ["USE_MOCK_APIS"] = "true"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_shell_id_with_special_characters(self, mock_mode):
        """Test shell_id with special characters."""
        tool = KillShellTool(shell_id="shell-123_test.v1", force=False)
        result = tool.run()
        assert result["success"] == True

    def test_very_long_shell_id(self, mock_mode):
        """Test very long shell_id."""
        long_id = "a" * 1000
        tool = KillShellTool(shell_id=long_id)
        result = tool.run()
        assert result["success"] == True

    def test_zero_timeout_with_force_false(self, mock_mode):
        """Test zero timeout results in immediate SIGKILL even with force=False."""
        tool = KillShellTool(shell_id="zero_timeout_test", force=False, timeout=0)
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["signal_used"] == "SIGKILL"

    def test_max_timeout_value(self, mock_mode):
        """Test maximum timeout value."""
        tool = KillShellTool(shell_id="max_timeout_test", timeout=86400)  # 1 day
        result = tool.run()
        assert result["success"] == True


class TestResultStructure:
    """Test result structure and metadata."""

    def test_result_contains_required_fields(self, mock_mode):
        """Test that result contains all required fields."""
        tool = KillShellTool(shell_id="result_test", force=False, timeout=5)
        result = tool.run()

        assert "success" in result
        assert "result" in result
        assert "metadata" in result

        result_data = result["result"]
        assert "shell_id" in result_data
        assert "terminated" in result_data
        assert "exit_code" in result_data
        assert "signal_used" in result_data
        assert "cleanup_performed" in result_data

    def test_metadata_structure(self, mock_mode):
        """Test metadata structure."""
        tool = KillShellTool(shell_id="metadata_test")
        result = tool.run()

        metadata = result["metadata"]
        assert "mock_mode" in metadata
        assert metadata["tool_name"] == "kill_shell_tool"

    def test_exit_codes(self, mock_mode):
        """Test different exit codes."""
        # Graceful termination
        tool1 = KillShellTool(shell_id="exit_code_1", force=False)
        result1 = tool1.run()
        assert result1["result"]["exit_code"] == 0

        # Force termination
        tool2 = KillShellTool(shell_id="exit_code_2", force=True)
        result2 = tool2.run()
        assert result2["result"]["exit_code"] == -9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
