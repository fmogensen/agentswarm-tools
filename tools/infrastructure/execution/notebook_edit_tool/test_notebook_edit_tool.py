"""
Comprehensive tests for NotebookEditTool
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from shared.errors import ValidationError
from tools.infrastructure.execution.notebook_edit_tool.notebook_edit_tool import (
    NotebookEditTool,
)


@pytest.fixture(autouse=True)
def disable_mock_apis():
    """Disable mock APIs for actual execution tests"""
    old_value = os.environ.get("USE_MOCK_APIS")
    os.environ["USE_MOCK_APIS"] = "false"
    yield
    if old_value is not None:
        os.environ["USE_MOCK_APIS"] = old_value
    else:
        os.environ.pop("USE_MOCK_APIS", None)


@pytest.fixture
def sample_notebook():
    """Create a sample notebook for testing"""
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "id": "cell1",
                "source": ["print('Hello World')"],
                "metadata": {},
                "outputs": [],
                "execution_count": None,
            },
            {
                "cell_type": "markdown",
                "id": "cell2",
                "source": ["# Markdown Header"],
                "metadata": {},
            },
            {
                "cell_type": "code",
                "id": "cell3",
                "source": ["x = 42\n", "print(x)"],
                "metadata": {},
                "outputs": [],
                "execution_count": None,
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    return notebook


@pytest.fixture
def temp_notebook(sample_notebook):
    """Create a temporary notebook file"""
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".ipynb"
    ) as f:
        json.dump(sample_notebook, f)
        notebook_path = f.name

    yield notebook_path

    # Cleanup
    if os.path.exists(notebook_path):
        os.unlink(notebook_path)


@pytest.fixture
def empty_notebook():
    """Create an empty notebook"""
    notebook = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".ipynb"
    ) as f:
        json.dump(notebook, f)
        notebook_path = f.name

    yield notebook_path

    # Cleanup
    if os.path.exists(notebook_path):
        os.unlink(notebook_path)


class TestNotebookEditToolReplace:
    """Tests for replace mode"""

    def test_replace_cell_source(self, temp_notebook):
        """Test replacing cell source"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="print('Updated')",
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["edit_mode"] == "replace"
        assert result["result"]["cell_id"] == "cell1"
        assert result["result"]["cell_type"] == "code"

        # Verify notebook was updated
        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][0]["source"] == ["print('Updated')"]

    def test_replace_multiline_source(self, temp_notebook):
        """Test replacing with multiline source"""
        new_source = "import os\nimport sys\n\nprint('Multi-line code')"
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell3",
            new_source=new_source,
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True

        # Verify multiline formatting
        with open(temp_notebook) as f:
            notebook = json.load(f)
            cell = notebook["cells"][2]
            assert cell["source"] == [
                "import os\n",
                "import sys\n",
                "\n",
                "print('Multi-line code')",
            ]

    def test_replace_markdown_cell(self, temp_notebook):
        """Test replacing markdown cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell2",
            new_source="## Updated Header\n\nNew content",
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cell_type"] == "markdown"

        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][1]["source"] == [
                "## Updated Header\n",
                "\n",
                "New content",
            ]

    def test_replace_nonexistent_cell(self, temp_notebook):
        """Test replacing non-existent cell raises error"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="nonexistent",
            new_source="print('test')",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "not found" in str(exc_info.value).lower()

    def test_replace_empty_source(self, temp_notebook):
        """Test replacing with empty source fails validation"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "required" in str(exc_info.value).lower()


class TestNotebookEditToolInsert:
    """Tests for insert mode"""

    def test_insert_code_cell_after(self, temp_notebook):
        """Test inserting code cell after specific cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="print('Inserted')",
            cell_type="code",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["edit_mode"] == "insert"
        assert result["result"]["cell_type"] == "code"
        assert result["result"]["cells_count"] == 4

        # Verify insertion position
        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][1]["source"] == ["print('Inserted')"]
            assert notebook["cells"][1]["cell_type"] == "code"

    def test_insert_markdown_cell(self, temp_notebook):
        """Test inserting markdown cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell2",
            new_source="# New Section",
            cell_type="markdown",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cell_type"] == "markdown"

        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][2]["cell_type"] == "markdown"
            assert notebook["cells"][2]["source"] == ["# New Section"]

    def test_insert_at_beginning(self, temp_notebook):
        """Test inserting at beginning (no cell_id)"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            new_source="# First Cell",
            cell_type="markdown",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cells_count"] == 4

        # Verify inserted at beginning
        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][0]["source"] == ["# First Cell"]

    def test_insert_defaults_to_code_type(self, temp_notebook):
        """Test insert defaults to code cell type when not specified"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="x = 10",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cell_type"] == "code"

        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][1]["cell_type"] == "code"

    def test_insert_multiline_content(self, temp_notebook):
        """Test inserting multiline content"""
        new_source = "def hello():\n    print('Hello')\n    return True"
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source=new_source,
            cell_type="code",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True

        with open(temp_notebook) as f:
            notebook = json.load(f)
            cell = notebook["cells"][1]
            assert cell["source"] == [
                "def hello():\n",
                "    print('Hello')\n",
                "    return True",
            ]

    def test_insert_empty_source_fails(self, temp_notebook):
        """Test inserting empty source fails validation"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="",
            edit_mode="insert",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "required" in str(exc_info.value).lower()

    def test_insert_after_nonexistent_cell(self, temp_notebook):
        """Test inserting after non-existent cell raises error"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="nonexistent",
            new_source="print('test')",
            edit_mode="insert",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "not found" in str(exc_info.value).lower()


class TestNotebookEditToolDelete:
    """Tests for delete mode"""

    def test_delete_cell(self, temp_notebook):
        """Test deleting a cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook, cell_id="cell2", edit_mode="delete"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["edit_mode"] == "delete"
        assert result["result"]["cell_id"] == "cell2"
        assert result["result"]["cells_count"] == 2

        # Verify cell was deleted
        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert len(notebook["cells"]) == 2
            # Verify cell2 is gone
            cell_ids = [cell["id"] for cell in notebook["cells"]]
            assert "cell2" not in cell_ids

    def test_delete_first_cell(self, temp_notebook):
        """Test deleting first cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook, cell_id="cell1", edit_mode="delete"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cells_count"] == 2

        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][0]["id"] == "cell2"

    def test_delete_last_cell(self, temp_notebook):
        """Test deleting last cell"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook, cell_id="cell3", edit_mode="delete"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cells_count"] == 2

    def test_delete_without_cell_id_fails(self, temp_notebook):
        """Test deleting without cell_id fails validation"""
        tool = NotebookEditTool(notebook_path=temp_notebook, edit_mode="delete")

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "required" in str(exc_info.value).lower()

    def test_delete_nonexistent_cell(self, temp_notebook):
        """Test deleting non-existent cell raises error"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook, cell_id="nonexistent", edit_mode="delete"
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "not found" in str(exc_info.value).lower()


class TestNotebookEditToolValidation:
    """Tests for parameter validation"""

    def test_non_absolute_path_fails(self, temp_notebook):
        """Test non-absolute path fails validation"""
        tool = NotebookEditTool(
            notebook_path="relative/path.ipynb",
            cell_id="cell1",
            new_source="test",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "absolute" in str(exc_info.value).lower()

    def test_non_ipynb_extension_fails(self):
        """Test non-.ipynb extension fails validation"""
        tool = NotebookEditTool(
            notebook_path="/tmp/test.txt",
            cell_id="cell1",
            new_source="test",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert ".ipynb" in str(exc_info.value).lower()

    def test_nonexistent_file_fails(self):
        """Test non-existent file fails validation"""
        tool = NotebookEditTool(
            notebook_path="/tmp/nonexistent_notebook.ipynb",
            cell_id="cell1",
            new_source="test",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "does not exist" in str(exc_info.value).lower()

    def test_invalid_edit_mode_fails(self, temp_notebook):
        """Test invalid edit_mode fails validation"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="test",
            edit_mode="invalid_mode",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "invalid edit_mode" in str(exc_info.value).lower()

    def test_invalid_cell_type_fails(self, temp_notebook):
        """Test invalid cell_type fails validation"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="test",
            cell_type="invalid_type",
            edit_mode="replace",
        )

        with pytest.raises(ValidationError) as exc_info:
            tool.run()

        assert "invalid cell_type" in str(exc_info.value).lower()


class TestNotebookEditToolEdgeCases:
    """Tests for edge cases"""

    def test_empty_notebook_insert(self, empty_notebook):
        """Test inserting into empty notebook"""
        tool = NotebookEditTool(
            notebook_path=empty_notebook,
            new_source="print('First cell')",
            cell_type="code",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["cells_count"] == 1

        with open(empty_notebook) as f:
            notebook = json.load(f)
            assert len(notebook["cells"]) == 1
            assert notebook["cells"][0]["source"] == ["print('First cell')"]

    def test_single_line_source(self, temp_notebook):
        """Test single line source formatting"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="x = 5",
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True

        with open(temp_notebook) as f:
            notebook = json.load(f)
            assert notebook["cells"][0]["source"] == ["x = 5"]

    def test_source_with_trailing_newline(self, temp_notebook):
        """Test source with trailing newline"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="print('test')\n",
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True

        with open(temp_notebook) as f:
            notebook = json.load(f)
            # Should have two elements: content and empty string
            assert notebook["cells"][0]["source"] == ["print('test')\n", ""]

    def test_json_formatting_preserved(self, temp_notebook):
        """Test that JSON formatting is preserved"""
        # Read original notebook
        with open(temp_notebook) as f:
            original = json.load(f)

        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="print('test')",
            edit_mode="replace",
        )
        tool.run()

        # Read modified notebook
        with open(temp_notebook) as f:
            modified = json.load(f)

        # Verify metadata is preserved
        assert modified["metadata"] == original["metadata"]
        assert modified["nbformat"] == original["nbformat"]
        assert modified["nbformat_minor"] == original["nbformat_minor"]

    def test_cell_id_generation_for_insert(self, temp_notebook):
        """Test that inserted cells get valid IDs"""
        tool = NotebookEditTool(
            notebook_path=temp_notebook,
            cell_id="cell1",
            new_source="print('test')",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        new_cell_id = result["result"]["cell_id"]
        assert new_cell_id  # Should have an ID
        assert len(new_cell_id) > 0

        # Verify ID exists in notebook
        with open(temp_notebook) as f:
            notebook = json.load(f)
            cell_ids = [cell["id"] for cell in notebook["cells"]]
            assert new_cell_id in cell_ids


class TestNotebookEditToolMockMode:
    """Tests for mock mode"""

    @pytest.fixture(autouse=True)
    def enable_mock_apis(self):
        """Enable mock APIs for these specific tests"""
        old_value = os.environ.get("USE_MOCK_APIS")
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        if old_value is not None:
            os.environ["USE_MOCK_APIS"] = old_value
        else:
            os.environ.pop("USE_MOCK_APIS", None)

    def test_mock_mode_replace(self):
        """Test mock mode for replace operation"""
        tool = NotebookEditTool(
            notebook_path="/tmp/test.ipynb",
            cell_id="cell1",
            new_source="print('test')",
            edit_mode="replace",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["edit_mode"] == "replace"
        assert result["metadata"]["mock_mode"] is True

    def test_mock_mode_insert(self):
        """Test mock mode for insert operation"""
        tool = NotebookEditTool(
            notebook_path="/tmp/test.ipynb",
            new_source="print('test')",
            cell_type="code",
            edit_mode="insert",
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["edit_mode"] == "insert"

    def test_mock_mode_delete(self):
        """Test mock mode for delete operation"""
        tool = NotebookEditTool(
            notebook_path="/tmp/test.ipynb", cell_id="cell1", edit_mode="delete"
        )
        result = tool.run()

        assert result["success"] is True
        assert result["result"]["mock"] is True
        assert result["result"]["edit_mode"] == "delete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
