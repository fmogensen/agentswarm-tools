"""
Edit Jupyter notebook (.ipynb) cells by replacing, inserting, or deleting
"""

import json
import os
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class NotebookEditTool(BaseTool):
    """
    Edit Jupyter notebook cells by replacing, inserting, or deleting

    Args:
        notebook_path: Absolute path to Jupyter notebook (.ipynb)
        cell_id: ID of cell to edit or insert after
        new_source: New source code or markdown for the cell
        cell_type: Cell type: code or markdown
        edit_mode: Edit mode: replace, insert, or delete

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results (edit_mode, cell_id, cell_type, cells_count, notebook_path)
        - metadata: Additional information

    Example:
        >>> tool = NotebookEditTool(
        ...     notebook_path="/path/to/notebook.ipynb",
        ...     cell_id="cell1",
        ...     new_source="print('Updated')",
        ...     edit_mode="replace"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "notebook_edit_tool"
    tool_category: str = "infrastructure"
    tool_description: str = "Edit Jupyter notebook cells by replacing, inserting, or deleting"

    # Parameters
    notebook_path: str = Field(
        ..., description="Absolute path to Jupyter notebook (.ipynb)", min_length=1
    )
    cell_id: Optional[str] = Field(None, description="ID of cell to edit or insert after")
    new_source: str = Field("", description="New source code or markdown for the cell")
    cell_type: Optional[str] = Field(None, description="Cell type: code or markdown")
    edit_mode: str = Field("replace", description="Edit mode: replace, insert, or delete")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the notebook_edit_tool tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: For invalid input
            APIError: For execution failures
        """

        self._logger.info(
            f"Executing {self.tool_name} with notebook_path={self.notebook_path}, "
            f"cell_id={self.cell_id}, edit_mode={self.edit_mode}"
        )

        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name, "tool_version": "1.0.0"},
            }
        except (ValidationError, APIError):
            # Re-raise known errors without wrapping
            raise
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate notebook_path is absolute
        if not os.path.isabs(self.notebook_path):
            raise ValidationError(
                "Notebook path must be absolute",
                tool_name=self.tool_name,
                details={"notebook_path": self.notebook_path},
            )

        # Validate file has .ipynb extension
        if not self.notebook_path.endswith(".ipynb"):
            raise ValidationError(
                "File must have .ipynb extension",
                tool_name=self.tool_name,
                details={"notebook_path": self.notebook_path},
            )

        # Validate notebook_path exists (only for non-mock mode)
        if not self._should_use_mock() and not os.path.exists(self.notebook_path):
            raise ValidationError(
                f"Notebook path does not exist: {self.notebook_path}",
                tool_name=self.tool_name,
                details={"notebook_path": self.notebook_path},
            )

        # Validate edit_mode
        valid_modes = ["replace", "insert", "delete"]
        if self.edit_mode not in valid_modes:
            raise ValidationError(
                f"Invalid edit_mode: {self.edit_mode}. Must be one of: {valid_modes}",
                tool_name=self.tool_name,
                details={"edit_mode": self.edit_mode, "valid_modes": valid_modes},
            )

        # Validate cell_type if provided
        if self.cell_type:
            valid_types = ["code", "markdown"]
            if self.cell_type not in valid_types:
                raise ValidationError(
                    f"Invalid cell_type: {self.cell_type}. Must be one of: {valid_types}",
                    tool_name=self.tool_name,
                    details={"cell_type": self.cell_type, "valid_types": valid_types},
                )

        # Validate new_source is provided for replace and insert modes
        if self.edit_mode in ["replace", "insert"] and not self.new_source:
            raise ValidationError(
                f"new_source is required for {self.edit_mode} mode",
                tool_name=self.tool_name,
                details={"edit_mode": self.edit_mode},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "mock": True,
                "edit_mode": self.edit_mode,
                "cell_id": self.cell_id or "mock_cell_id",
                "cell_type": self.cell_type or "code",
                "cells_count": 5,
                "notebook_path": self.notebook_path,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "tool_version": "1.0.0",
            },
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic: Edit Jupyter notebook cells.

        Returns:
            Dict with edit result

        Raises:
            APIError: If notebook read/write fails
            ValidationError: If cell_id not found or invalid notebook structure
        """
        try:
            # Load notebook
            with open(self.notebook_path, "r", encoding="utf-8") as f:
                notebook = json.load(f)
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse notebook JSON: {e}", tool_name=self.tool_name)
        except IOError as e:
            raise APIError(f"Failed to read/write notebook file: {e}", tool_name=self.tool_name)

        # Validate notebook structure
        if "cells" not in notebook:
            raise ValidationError(
                "Invalid notebook structure: missing 'cells' key",
                tool_name=self.tool_name,
                details={"notebook_path": self.notebook_path},
            )

        cells = notebook["cells"]

        # Perform edit based on mode
        if self.edit_mode == "replace":
            cell_index = self._find_cell_by_id(cells, self.cell_id)
            if cell_index is None:
                raise ValidationError(
                    f"Cell with id '{self.cell_id}' not found",
                    tool_name=self.tool_name,
                    details={"cell_id": self.cell_id},
                )

            # Replace cell source
            cells[cell_index]["source"] = self._format_source(self.new_source)
            result_cell_id = self.cell_id
            result_cell_type = cells[cell_index]["cell_type"]

        elif self.edit_mode == "insert":
            # Determine cell type (use provided or default to code)
            cell_type = self.cell_type or "code"

            # Create new cell
            new_cell = self._create_cell(cell_type, self.new_source)

            # Find insert position
            if self.cell_id:
                cell_index = self._find_cell_by_id(cells, self.cell_id)
                if cell_index is None:
                    raise ValidationError(
                        f"Cell with id '{self.cell_id}' not found",
                        tool_name=self.tool_name,
                        details={"cell_id": self.cell_id},
                    )
                insert_position = cell_index + 1
            else:
                # Insert at beginning if no cell_id provided
                insert_position = 0

            cells.insert(insert_position, new_cell)
            result_cell_id = new_cell["id"]
            result_cell_type = cell_type

        elif self.edit_mode == "delete":
            if not self.cell_id:
                raise ValidationError(
                    "cell_id is required for delete mode",
                    tool_name=self.tool_name,
                    details={"edit_mode": self.edit_mode},
                )

            cell_index = self._find_cell_by_id(cells, self.cell_id)
            if cell_index is None:
                raise ValidationError(
                    f"Cell with id '{self.cell_id}' not found",
                    tool_name=self.tool_name,
                    details={"cell_id": self.cell_id},
                )

            deleted_cell = cells.pop(cell_index)
            result_cell_id = self.cell_id
            result_cell_type = deleted_cell["cell_type"]

        # Save modified notebook
        try:
            with open(self.notebook_path, "w", encoding="utf-8") as f:
                json.dump(notebook, f, indent=1)
        except IOError as e:
            raise APIError(f"Failed to write notebook file: {e}", tool_name=self.tool_name)

        return {
            "edit_mode": self.edit_mode,
            "cell_id": result_cell_id,
            "cell_type": result_cell_type,
            "cells_count": len(cells),
            "notebook_path": self.notebook_path,
        }

    def _find_cell_by_id(self, cells: list, cell_id: str) -> Optional[int]:
        """
        Find cell index by cell ID.

        Args:
            cells: List of notebook cells
            cell_id: Cell ID to find

        Returns:
            Cell index or None if not found
        """
        if not cell_id:
            return None

        for i, cell in enumerate(cells):
            if cell.get("id") == cell_id:
                return i
        return None

    def _format_source(self, source: str) -> list:
        """
        Format source string into notebook cell source format.

        Jupyter notebooks store source as list of strings (one per line).

        Args:
            source: Source code or markdown as string

        Returns:
            List of strings (lines)
        """
        # Split by newlines and keep newline characters except on last line
        lines = source.split("\n")
        if len(lines) == 0:
            return []
        if len(lines) == 1:
            return [lines[0]]

        # Add newline to all but last line
        formatted = [line + "\n" for line in lines[:-1]]
        # Last line doesn't get newline
        formatted.append(lines[-1])
        return formatted

    def _create_cell(self, cell_type: str, source: str) -> Dict[str, Any]:
        """
        Create a new notebook cell.

        Args:
            cell_type: "code" or "markdown"
            source: Cell source code or markdown

        Returns:
            Cell dictionary
        """
        import uuid

        cell = {
            "cell_type": cell_type,
            "id": str(uuid.uuid4()).replace("-", "")[:8],  # Short ID
            "metadata": {},
            "source": self._format_source(source),
        }

        # Add execution-specific fields for code cells
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []

        return cell


if __name__ == "__main__":
    print("Testing NotebookEditTool...")

    import json
    import os
    import tempfile

    # Disable rate limiting for tests
    os.environ["DISABLE_RATE_LIMITING"] = "true"

    # Create test notebook
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "id": "cell1",
                "source": ["print('Hello')"],
                "metadata": {},
                "outputs": [],
                "execution_count": None,
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".ipynb") as f:
        json.dump(notebook, f)
        test_notebook = f.name

    try:
        # Test 1: Replace cell source
        print("\nTest 1: Replace cell source")
        tool = NotebookEditTool(
            notebook_path=test_notebook,
            cell_id="cell1",
            new_source="print('Updated')",
            edit_mode="replace",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["edit_mode"] == "replace"

        # Verify notebook was updated
        with open(test_notebook) as f:
            updated = json.load(f)
            assert updated["cells"][0]["source"] == ["print('Updated')"]

        print("✓ Test 1 passed: Cell replaced successfully")

        # Test 2: Insert new cell
        print("\nTest 2: Insert new cell")
        tool = NotebookEditTool(
            notebook_path=test_notebook,
            cell_id="cell1",
            new_source="print('Inserted')",
            cell_type="code",
            edit_mode="insert",
        )
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["edit_mode"] == "insert"
        assert result["result"]["cells_count"] == 2

        print("✓ Test 2 passed: Cell inserted successfully")

        # Test 3: Delete cell
        print("\nTest 3: Delete cell")
        tool = NotebookEditTool(notebook_path=test_notebook, cell_id="cell1", edit_mode="delete")
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["edit_mode"] == "delete"
        assert result["result"]["cells_count"] == 1

        print("✓ Test 3 passed: Cell deleted successfully")

        # Test 4: Validation - non-absolute path
        print("\nTest 4: Validation - non-absolute path")
        try:
            bad_tool = NotebookEditTool(
                notebook_path="relative/path.ipynb",
                cell_id="cell1",
                new_source="test",
                edit_mode="replace",
            )
            bad_tool.run()
            assert False, "Should have raised ValidationError"
        except Exception as e:
            print(f"✓ Test 4 passed: Validation working - {type(e).__name__}")

        # Test 5: Validation - invalid edit_mode
        print("\nTest 5: Validation - invalid edit_mode")
        try:
            bad_tool = NotebookEditTool(
                notebook_path=test_notebook,
                cell_id="cell1",
                new_source="test",
                edit_mode="invalid_mode",
            )
            bad_tool.run()
            assert False, "Should have raised ValidationError"
        except Exception as e:
            print(f"✓ Test 5 passed: Validation working - {type(e).__name__}")

        print("\n✅ All tests passed!")

    finally:
        os.unlink(test_notebook)
