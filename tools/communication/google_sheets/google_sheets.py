"""
Create and modify Google Sheets using the Google Sheets API v4

DEPRECATED: This tool is now a backward compatibility wrapper around UnifiedGoogleWorkspace.
For new code, use UnifiedGoogleWorkspace with workspace_type="sheets" instead.
This wrapper will be maintained for backward compatibility but may be removed in a future version.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import warnings

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError


class GoogleSheets(BaseTool):
    """
    Create and modify Google Sheets using the Google Sheets API v4

    DEPRECATED: Use UnifiedGoogleWorkspace with workspace_type="sheets" instead.

    Args:
        mode: Operation mode - "create" or "modify"
        data: List of lists representing rows and columns
        title: Spreadsheet title (required for create mode)
        spreadsheet_id: Google Sheets ID (required for modify mode)
        sheet_name: Worksheet name (default: "Sheet1")
        formulas: Dict mapping cell references to formulas (e.g., {"A1": "=SUM(B1:B10)"})
        formatting: Dict with formatting options (colors, bold, number formats)
        share_with: List of email addresses to share the spreadsheet with

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Dict with spreadsheet_id, spreadsheet_url, and operation details
        - metadata: Additional information including tool name and mode

    Example:
        >>> # Create new spreadsheet
        >>> tool = GoogleSheets(
        ...     mode="create",
        ...     title="Sales Report Q4",
        ...     data=[["Product", "Sales"], ["Widget A", 1000], ["Widget B", 1500]],
        ...     share_with=["user@example.com"]
        ... )
        >>> result = tool.run()

        >>> # Modify existing spreadsheet
        >>> tool = GoogleSheets(
        ...     mode="modify",
        ...     spreadsheet_id="1ABC...",
        ...     data=[["Updated", "Data"]],
        ...     sheet_name="Sheet1",
        ...     formulas={"C1": "=SUM(B2:B10)"}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_sheets"
    tool_category: str = "communication"

    # Parameters
    mode: str = Field(
        ...,
        description='Operation mode: "create" to create new spreadsheet or "modify" to update existing',
    )
    data: List[List[Any]] = Field(
        ...,
        description="List of lists representing rows and columns of data to write",
    )
    title: Optional[str] = Field(
        None,
        description="Spreadsheet title (required for create mode)",
    )
    spreadsheet_id: Optional[str] = Field(
        None,
        description="Google Sheets ID (required for modify mode)",
    )
    sheet_name: str = Field(
        "Sheet1",
        description="Worksheet name within the spreadsheet",
    )
    formulas: Optional[Dict[str, str]] = Field(
        None,
        description='Dictionary mapping cell references to formulas (e.g., {"A1": "=SUM(B1:B10)"})',
    )
    formatting: Optional[Dict[str, Any]] = Field(
        None,
        description="Dictionary with formatting options (colors, bold, number formats)",
    )
    share_with: Optional[List[str]] = Field(
        None,
        description="List of email addresses to share the spreadsheet with",
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_sheets tool by delegating to UnifiedGoogleWorkspace.

        Returns:
            Dict with results

        Raises:
            ValidationError: If input is invalid
            APIError: If processing fails
        """
        # Emit deprecation warning
        warnings.warn(
            "GoogleSheets is deprecated. Use UnifiedGoogleWorkspace with workspace_type='sheets' instead. "
            "This wrapper will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import here to avoid circular dependency
        from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

        # Create unified tool with equivalent parameters
        unified_tool = UnifiedGoogleWorkspace(
            workspace_type="sheets",
            mode=self.mode,
            title=self.title,
            spreadsheet_id=self.spreadsheet_id,
            data=self.data,
            sheet_name=self.sheet_name,
            formulas=self.formulas,
            formatting=self.formatting,
            share_with=self.share_with,
        )

        # Execute and get result
        result = unified_tool._execute()

        # Preserve original tool name in metadata for backward compatibility
        if "metadata" in result:
            result["metadata"]["tool_name"] = self.tool_name
            result["metadata"]["deprecated"] = True
            result["metadata"]["delegate_to"] = "unified_google_workspace"

        return result

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Note: Validation is now handled by UnifiedGoogleWorkspace,
        but we keep this method for backward compatibility.
        """
        pass

    def _should_use_mock(self) -> bool:
        """
        Check if mock mode is enabled.

        Returns:
            True if USE_MOCK_APIS=true, otherwise False
        """
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """
        Generate mock results for testing.

        Note: Now delegated to UnifiedGoogleWorkspace.
        """
        pass

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic for Google Sheets operations.

        Note: Now delegated to UnifiedGoogleWorkspace.
        """
        pass


if __name__ == "__main__":
    # Test the tool
    print("Testing GoogleSheets tool (backward compatibility wrapper)...\n")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create mode
    print("=" * 60)
    print("Test 1: Create new spreadsheet")
    print("=" * 60)

    tool1 = GoogleSheets(
        mode="create",
        title="Sales Report Q4 2024",
        data=[
            ["Product", "Q1 Sales", "Q2 Sales", "Q3 Sales", "Q4 Sales"],
            ["Widget A", 1000, 1200, 1100, 1500],
            ["Widget B", 800, 900, 950, 1000],
            ["Widget C", 1200, 1100, 1300, 1400],
        ],
        sheet_name="Sales Data",
        formulas={"F2": "=SUM(B2:E2)", "F3": "=SUM(B3:E3)", "F4": "=SUM(B4:E4)"},
        formatting={"bold_header": True},
        share_with=["user1@example.com", "user2@example.com"],
    )

    result1 = tool1.run()
    print(f"Success: {result1.get('success')}")
    print(f"Spreadsheet ID: {result1.get('result', {}).get('spreadsheet_id')}")
    print(f"Spreadsheet URL: {result1.get('result', {}).get('spreadsheet_url')}")
    print(f"Status: {result1.get('result', {}).get('status')}")
    print(f"Deprecated: {result1.get('metadata', {}).get('deprecated')}")

    assert result1.get("success") == True
    assert result1.get("result", {}).get("status") == "created"
    assert result1.get("result", {}).get("rows_written") == 4
    assert result1.get("metadata", {}).get("deprecated") == True
    print("\n✓ Test 1 passed!\n")

    # Test 2: Modify mode
    print("=" * 60)
    print("Test 2: Modify existing spreadsheet")
    print("=" * 60)

    tool2 = GoogleSheets(
        mode="modify",
        spreadsheet_id="1ABC123XYZ",
        data=[
            ["Updated Product", "New Value"],
            ["Widget D", 2000],
            ["Widget E", 2500],
        ],
        sheet_name="Sheet1",
        formulas={"C1": "=SUM(B2:B3)"},
    )

    result2 = tool2.run()
    print(f"Success: {result2.get('success')}")
    print(f"Spreadsheet ID: {result2.get('result', {}).get('spreadsheet_id')}")
    print(f"Status: {result2.get('result', {}).get('status')}")
    print(f"Rows written: {result2.get('result', {}).get('rows_written')}")

    assert result2.get("success") == True
    assert result2.get("result", {}).get("status") == "modified"
    print("\n✓ Test 2 passed!\n")

    # Test 3: Validation error - missing title in create mode
    print("=" * 60)
    print("Test 3: Validation error - missing title in create mode")
    print("=" * 60)

    try:
        tool3 = GoogleSheets(mode="create", data=[["Test"]])
        result3 = tool3.run()
        print(f"Error handled: Should have thrown exception")
        assert False
    except Exception as e:
        print(f"Expected validation error: {e}")
        print("✓ Test 3 passed!\n")

    print("=" * 60)
    print("All backward compatibility tests passed!")
    print("Note: This wrapper delegates to UnifiedGoogleWorkspace")
    print("=" * 60)
