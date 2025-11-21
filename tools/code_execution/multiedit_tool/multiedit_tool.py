"""
Perform multiple sequential edits to a single file atomically
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json
import tempfile
import shutil

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class MultieditTool(BaseTool):
    """
    Perform multiple sequential edits to a single file atomically

    Args:
        input: Primary input parameter containing a JSON string defining:
               {
                 "file_path": "<path>",
                 "edits": [
                    {"action": "replace", "search": "...", "replace": "..."},
                    {"action": "insert", "line": 10, "text": "..."},
                    {"action": "delete", "line": 5}
               ]}

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = MultieditTool(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "multiedit_tool"
    tool_category: str = "code_execution"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the multiedit_tool tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                field="param",
            )

        try:
            data = json.loads(self.input)
        except Exception:
            raise ValidationError(
                "Input must be valid JSON",
                tool_name=self.tool_name,
                field="param",
            )

        if "file_path" not in data or not isinstance(data["file_path"], str):
            raise ValidationError(
                "Missing or invalid file_path", tool_name=self.tool_name, field="file_path"
            )

        if "edits" not in data or not isinstance(data["edits"], list):
            raise ValidationError(
                "Missing or invalid edits list", tool_name=self.tool_name, field="edits"
            )

        for edit in data["edits"]:
            if "action" not in edit:
                raise ValidationError(
                    "Each edit must contain an action",
                    tool_name=self.tool_name,
                    details=edit,
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {"mock": True},
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        data = json.loads(self.input)
        file_path = data["file_path"]
        edits = data["edits"]

        if not os.path.exists(file_path):
            raise APIError(
                f"File does not exist: {file_path}", tool_name=self.tool_name
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            orig_content = "".join(lines)

            for edit in edits:
                action = edit["action"]

                if action == "replace":
                    search = edit.get("search", "")
                    replace = edit.get("replace", "")
                    new_content = orig_content.replace(search, replace)
                    orig_content = new_content

                elif action == "insert":
                    line_idx = edit.get("line")
                    text = edit.get("text", "")
                    if not isinstance(line_idx, int) or line_idx < 0:
                        raise ValidationError(
                            "Invalid line index for insert",
                            tool_name=self.tool_name,
                            details=edit,
                        )
                    split = orig_content.splitlines(keepends=True)
                    if line_idx >= len(split):
                        split.append(text + "\n")
                    else:
                        split.insert(line_idx, text + "\n")
                    orig_content = "".join(split)

                elif action == "delete":
                    line_idx = edit.get("line")
                    if not isinstance(line_idx, int) or line_idx < 0:
                        raise ValidationError(
                            "Invalid line index for delete",
                            tool_name=self.tool_name,
                            details=edit,
                        )
                    split = orig_content.splitlines(keepends=True)
                    if line_idx < len(split):
                        del split[line_idx]
                    orig_content = "".join(split)

                else:
                    raise ValidationError(
                        f"Unknown edit action: {action}",
                        tool_name=self.tool_name,
                        details=edit,
                    )

            temp_fd, temp_path = tempfile.mkstemp()
            os.close(temp_fd)

            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(orig_content)

            shutil.move(temp_path, file_path)

            return {"message": "Edits applied successfully"}

        except ValidationError:
            raise
        except Exception as e:
            raise APIError(f"Failed to apply edits: {e}", tool_name=self.tool_name)
