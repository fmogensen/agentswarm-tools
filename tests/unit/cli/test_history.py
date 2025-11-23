"""
Tests for command history functionality
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from cli.history import CommandHistory


class TestCommandHistory:
    """Test CommandHistory class."""

    @pytest.fixture
    def temp_history(self):
        """Create temporary history instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history = CommandHistory()
            history.history_dir = Path(tmpdir)
            history.history_file = history.history_dir / "history.json"
            history.history = []
            yield history

    def test_add_command(self, temp_history):
        """Test adding command to history."""
        history = temp_history

        history.add_command(
            command="run", tool="web_search", params={"query": "test"}, success=True, duration=1.5
        )

        assert len(history.history) == 1
        entry = history.history[0]
        assert entry["command"] == "run"
        assert entry["tool"] == "web_search"
        assert entry["success"] is True
        assert entry["duration"] == 1.5

    def test_add_multiple_commands(self, temp_history):
        """Test adding multiple commands."""
        history = temp_history

        for i in range(5):
            history.add_command(command="run", tool=f"tool_{i}", success=True)

        assert len(history.history) == 5

    def test_get_history_with_limit(self, temp_history):
        """Test getting history with limit."""
        history = temp_history

        # Add 10 commands
        for i in range(10):
            history.add_command(command="run", tool=f"tool_{i}")

        # Get last 5
        recent = history.get_history(limit=5)

        assert len(recent) == 5

    def test_get_history_with_filter(self, temp_history):
        """Test getting history with command filter."""
        history = temp_history

        # Add different commands
        history.add_command(command="run", tool="tool1")
        history.add_command(command="test", tool="tool2")
        history.add_command(command="run", tool="tool3")

        # Filter by command
        run_commands = history.get_history(command_filter="run")

        assert len(run_commands) == 2
        assert all(e["command"] == "run" for e in run_commands)

    def test_get_history_success_only(self, temp_history):
        """Test getting only successful commands."""
        history = temp_history

        # Add commands with mixed success
        history.add_command(command="run", tool="tool1", success=True)
        history.add_command(command="run", tool="tool2", success=False)
        history.add_command(command="run", tool="tool3", success=True)

        # Get successful only
        successful = history.get_history(success_only=True)

        assert len(successful) == 2
        assert all(e["success"] for e in successful)

    def test_get_by_id(self, temp_history):
        """Test getting entry by ID."""
        history = temp_history

        # Add commands
        history.add_command(command="run", tool="tool1")
        history.add_command(command="run", tool="tool2")

        # Get by ID
        entry = history.get_by_id(1)

        assert entry is not None
        assert entry["id"] == 1
        assert entry["tool"] == "tool1"

    def test_get_by_invalid_id(self, temp_history):
        """Test getting entry by invalid ID."""
        history = temp_history

        entry = history.get_by_id(999)

        assert entry is None

    def test_clear_history(self, temp_history):
        """Test clearing history."""
        history = temp_history

        # Add commands
        for i in range(5):
            history.add_command(command="run", tool=f"tool_{i}")

        assert len(history.history) == 5

        # Clear
        history.clear()

        assert len(history.history) == 0

    def test_replay_command(self, temp_history):
        """Test getting command for replay."""
        history = temp_history

        # Add command
        history.add_command(command="run", tool="web_search", params={"query": "test"})

        # Get for replay
        replay_info = history.replay_command(1)

        assert replay_info is not None
        assert replay_info["command"] == "run"
        assert replay_info["tool"] == "web_search"
        assert replay_info["params"]["query"] == "test"

    def test_get_statistics(self, temp_history):
        """Test getting usage statistics."""
        history = temp_history

        # Add commands
        history.add_command(command="run", tool="web_search", success=True)
        history.add_command(command="run", tool="web_search", success=True)
        history.add_command(command="run", tool="image_search", success=False)
        history.add_command(command="test", tool="web_search", success=True)

        # Get statistics
        stats = history.get_statistics()

        assert stats["total_commands"] == 4
        assert stats["successful_commands"] == 3
        assert stats["failed_commands"] == 1
        assert stats["success_rate"] == 75.0

        # Check most used tools
        most_used = stats["most_used_tools"]
        assert len(most_used) > 0
        assert most_used[0]["tool"] == "web_search"
        assert most_used[0]["count"] == 3

    def test_history_max_entries(self, temp_history):
        """Test that history respects max entries limit."""
        history = temp_history

        # Add more than max entries (1000)
        for i in range(1050):
            history.add_command(command="run", tool=f"tool_{i}")

        # Should keep only last 1000
        assert len(history.history) <= 1000

    def test_save_and_load_history(self, temp_history):
        """Test saving and loading history."""
        history = temp_history

        # Add commands
        history.add_command(command="run", tool="tool1", success=True)
        history.add_command(command="run", tool="tool2", success=False)

        # Save
        history._save_history()

        # Create new instance and load
        new_history = CommandHistory()
        new_history.history_file = history.history_file
        new_history.history = new_history._load_history()

        assert len(new_history.history) == 2
        assert new_history.history[0]["tool"] == "tool1"


def test_history_entry_structure():
    """Test that history entries have correct structure."""
    history = CommandHistory()

    history.add_command(
        command="run",
        tool="web_search",
        params={"query": "test"},
        success=True,
        error=None,
        duration=1.5,
    )

    entry = history.history[0]

    # Verify all required fields
    assert "id" in entry
    assert "timestamp" in entry
    assert "command" in entry
    assert "tool" in entry
    assert "params" in entry
    assert "success" in entry
    assert "error" in entry
    assert "duration" in entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
