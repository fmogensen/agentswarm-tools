"""
Live integration tests for Utility tools.

These tests validate utility tools that don't require external APIs.
"""

import os

import pytest

pytestmark = [
    pytest.mark.integration,
]


@pytest.fixture(autouse=True)
def reset_rate_limiter_for_test():
    """Reset rate limiter before each test by giving buckets full tokens."""
    from datetime import datetime

    from shared.security import get_rate_limiter

    limiter = get_rate_limiter()
    # Clear all buckets
    limiter._buckets.clear()
    # Pre-populate common tool buckets with full tokens
    # Use naive datetime to match the code's datetime.utcnow()
    for tool in [
        "think:anonymous",
        "ask_for_clarification:anonymous",
        "write_tool:anonymous",
        "read_tool:anonymous",
    ]:
        limiter._buckets[tool] = {"tokens": 60, "last_update": datetime.utcnow()}  # Full bucket
    yield


class TestThinkTool:
    """Tests for Think utility tool."""

    def test_basic_thought(self):
        """Test recording a basic thought."""
        from tools.utils.think import Think

        tool = Think(thought="This is a test thought for analysis.")
        result = tool.run()

        assert result.get("success") is True

    def test_complex_thought(self):
        """Test recording a complex multi-line thought."""
        from tools.utils.think import Think

        thought = """
        Step 1: Analyze the user's request
        Step 2: Break down into subtasks
        Step 3: Execute each subtask
        Step 4: Validate results
        """
        tool = Think(thought=thought)
        result = tool.run()

        assert result.get("success") is True


class TestAskForClarification:
    """Tests for AskForClarification utility tool."""

    def test_basic_question(self):
        """Test asking a basic clarification question."""
        from tools.utils.ask_for_clarification import AskForClarification

        tool = AskForClarification(question="What specific format do you want?")
        result = tool.run()

        assert result.get("success") is True

    def test_multiple_choice_question(self):
        """Test asking a multiple choice question."""
        from tools.utils.ask_for_clarification import AskForClarification

        question = "Which option do you prefer: A) Fast B) Accurate C) Both?"
        tool = AskForClarification(question=question)
        result = tool.run()

        assert result.get("success") is True


class TestCodeExecutionTools:
    """Tests for code execution tools."""

    def test_write_and_read_file(self, tmp_path):
        """Test writing and reading a file."""
        from tools.infrastructure.execution.read_tool import ReadTool
        from tools.infrastructure.execution.write_tool import WriteTool

        test_file = str(tmp_path / "test.txt")
        test_content = "Hello, World!"

        # Write file
        write_tool = WriteTool(file_path=test_file, content=test_content)
        write_result = write_tool.run()

        assert write_result.get("success") is True or "error" not in write_result

        # Read file
        read_tool = ReadTool(file_path=test_file)
        read_result = read_tool.run()

        assert read_result.get("success") is True or "error" not in read_result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
