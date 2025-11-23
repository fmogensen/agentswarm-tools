"""
Tests for shell completion functionality
"""

from pathlib import Path

import pytest

from cli.completion import CompletionManager


class TestCompletionManager:
    """Test CompletionManager class."""

    @pytest.fixture
    def manager(self):
        """Create CompletionManager instance."""
        return CompletionManager()

    def test_supported_shells(self, manager):
        """Test supported shells list."""
        assert "bash" in manager.supported_shells
        assert "zsh" in manager.supported_shells
        assert "fish" in manager.supported_shells

    def test_generate_bash_completion(self, manager):
        """Test bash completion script generation."""
        script = manager.generate_bash_completion()

        assert script is not None
        assert len(script) > 0
        assert "_agentswarm_completions" in script
        assert "complete -F _agentswarm_completions agentswarm" in script

        # Check for main commands
        assert "interactive" in script or "list" in script
        assert "workflow" in script
        assert "history" in script

    def test_generate_zsh_completion(self, manager):
        """Test zsh completion script generation."""
        script = manager.generate_zsh_completion()

        assert script is not None
        assert len(script) > 0
        assert "#compdef agentswarm" in script
        assert "_agentswarm" in script

        # Check for main commands
        assert "interactive" in script or "list" in script
        assert "workflow" in script

    def test_generate_fish_completion(self, manager):
        """Test fish completion script generation."""
        script = manager.generate_fish_completion()

        assert script is not None
        assert len(script) > 0
        assert "complete -c agentswarm" in script

        # Check for main commands
        assert "interactive" in script or "list" in script
        assert "workflow" in script

    def test_get_completion_script_bash(self, manager):
        """Test getting completion script for bash."""
        script = manager.get_completion_script("bash")

        assert script is not None
        assert "_agentswarm_completions" in script

    def test_get_completion_script_zsh(self, manager):
        """Test getting completion script for zsh."""
        script = manager.get_completion_script("zsh")

        assert script is not None
        assert "_agentswarm" in script

    def test_get_completion_script_fish(self, manager):
        """Test getting completion script for fish."""
        script = manager.get_completion_script("fish")

        assert script is not None
        assert "complete -c agentswarm" in script

    def test_get_completion_script_invalid_shell(self, manager):
        """Test getting completion script for invalid shell."""
        with pytest.raises(ValueError):
            manager.get_completion_script("invalid")

    def test_get_install_path_bash(self, manager):
        """Test getting install path for bash."""
        path = manager.get_install_path("bash")

        assert path is not None
        assert isinstance(path, Path)
        assert "agentswarm" in str(path)

    def test_get_install_path_zsh(self, manager):
        """Test getting install path for zsh."""
        path = manager.get_install_path("zsh")

        assert path is not None
        assert isinstance(path, Path)
        assert "_agentswarm" in str(path)
        assert ".zsh" in str(path)

    def test_get_install_path_fish(self, manager):
        """Test getting install path for fish."""
        path = manager.get_install_path("fish")

        assert path is not None
        assert isinstance(path, Path)
        assert "agentswarm.fish" in str(path)
        assert "fish/completions" in str(path)

    def test_get_install_path_invalid_shell(self, manager):
        """Test getting install path for invalid shell."""
        with pytest.raises(ValueError):
            manager.get_install_path("invalid")

    def test_detect_shell(self, manager):
        """Test shell detection."""
        shell = manager.detect_shell()

        # Should detect something or return None
        assert shell is None or shell in manager.supported_shells


def test_completion_script_has_commands():
    """Test that completion scripts include all major commands."""
    manager = CompletionManager()

    commands = ["list", "run", "test", "workflow", "history", "completion", "config"]

    # Test bash
    bash_script = manager.generate_bash_completion()
    for cmd in commands:
        assert cmd in bash_script

    # Test zsh
    zsh_script = manager.generate_zsh_completion()
    for cmd in commands:
        assert cmd in zsh_script

    # Test fish
    fish_script = manager.generate_fish_completion()
    for cmd in commands:
        assert cmd in fish_script


def test_completion_script_has_subcommands():
    """Test that completion scripts include subcommands."""
    manager = CompletionManager()

    # Workflow subcommands
    workflow_cmds = ["create", "run", "list", "delete"]

    bash_script = manager.generate_bash_completion()
    for cmd in workflow_cmds:
        assert cmd in bash_script

    # History subcommands
    history_cmds = ["list", "replay", "clear", "stats"]

    for cmd in history_cmds:
        assert cmd in bash_script


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
