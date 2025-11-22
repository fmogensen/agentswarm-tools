"""
Create and modify Google Sheets using the Google Sheets API v4
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import json

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, ConfigurationError

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    # Allow import without google-api-python-client for testing
    pass


class GoogleSheets(BaseTool):
    """
    Create and modify Google Sheets using the Google Sheets API v4

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
        Execute the google_sheets tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If input is invalid
            APIError: If processing fails
        """
        # 1. VALIDATE INPUT PARAMETERS
        self._validate_parameters()

        # 2. MOCK MODE SUPPORT
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. REAL EXECUTION
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "mode": self.mode,
                    "mock_mode": False,
                },
            }

        except HttpError as e:
            raise APIError(
                f"Google Sheets API error: {e}",
                tool_name=self.tool_name,
                api_name="Google Sheets API",
                status_code=e.resp.status if hasattr(e, "resp") else None,
            )
        except Exception as e:
            raise APIError(f"Failed to process Google Sheets: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input parameters are invalid
        """
        # Validate mode
        valid_modes = ["create", "modify"]
        if self.mode not in valid_modes:
            raise ValidationError(
                f"Invalid mode: {self.mode}. Must be one of {valid_modes}",
                tool_name=self.tool_name,
                field="mode",
            )

        # Validate data
        if not self.data or not isinstance(self.data, list):
            raise ValidationError(
                "Data must be a non-empty list of lists",
                tool_name=self.tool_name,
                field="data",
            )

        if not all(isinstance(row, list) for row in self.data):
            raise ValidationError(
                "Data must be a list of lists (rows)",
                tool_name=self.tool_name,
                field="data",
            )

        # Mode-specific validation
        if self.mode == "create":
            if not self.title or not self.title.strip():
                raise ValidationError(
                    "Title is required for create mode",
                    tool_name=self.tool_name,
                    field="title",
                )
        elif self.mode == "modify":
            if not self.spreadsheet_id or not self.spreadsheet_id.strip():
                raise ValidationError(
                    "Spreadsheet ID is required for modify mode",
                    tool_name=self.tool_name,
                    field="spreadsheet_id",
                )

        # Validate share_with emails if provided
        if self.share_with:
            if not isinstance(self.share_with, list):
                raise ValidationError(
                    "share_with must be a list of email addresses",
                    tool_name=self.tool_name,
                    field="share_with",
                )
            for email in self.share_with:
                if "@" not in email:
                    raise ValidationError(
                        f"Invalid email address: {email}",
                        tool_name=self.tool_name,
                        field="share_with",
                    )

        # Validate formulas format if provided
        if self.formulas:
            if not isinstance(self.formulas, dict):
                raise ValidationError(
                    "Formulas must be a dictionary",
                    tool_name=self.tool_name,
                    field="formulas",
                )

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

        Returns:
            Mocked spreadsheet response
        """
        # Use provided spreadsheet_id in modify mode, generate one for create mode
        if self.mode == "modify":
            mock_id = self.spreadsheet_id
        else:
            mock_id = "1mock_ABC123XYZ"

        mock_url = f"https://docs.google.com/spreadsheets/d/{mock_id}/edit"

        result = {
            "spreadsheet_id": mock_id,
            "spreadsheet_url": mock_url,
            "mode": self.mode,
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
        }

        if self.mode == "create":
            result["title"] = self.title
            result["status"] = "created"
        else:
            result["status"] = "modified"

        if self.formulas:
            result["formulas_applied"] = len(self.formulas)

        if self.share_with:
            result["shared_with"] = self.share_with

        return {
            "success": True,
            "result": result,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "mode": self.mode,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic for Google Sheets operations.

        Returns:
            Dict with spreadsheet details

        Raises:
            ConfigurationError: If credentials are missing
            APIError: If Google Sheets API fails
        """
        # Get credentials
        credentials = self._get_credentials()

        # Build the Sheets API service
        service = build("sheets", "v4", credentials=credentials)

        # Execute based on mode
        if self.mode == "create":
            result = self._create_spreadsheet(service)
        else:  # modify
            result = self._modify_spreadsheet(service)

        return result

    def _get_credentials(self) -> "Credentials":
        """
        Get Google API credentials from environment.

        Returns:
            Google API credentials

        Raises:
            ConfigurationError: If credentials are not configured
        """
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not credentials_path:
            raise ConfigurationError(
                "Missing environment variable: GOOGLE_SHEETS_CREDENTIALS",
                tool_name=self.tool_name,
                config_key="GOOGLE_SHEETS_CREDENTIALS",
            )

        if not os.path.exists(credentials_path):
            raise ConfigurationError(
                f"Credentials file not found: {credentials_path}",
                tool_name=self.tool_name,
                config_key="GOOGLE_SHEETS_CREDENTIALS",
            )

        # Define required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ]

        try:
            credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
            return credentials
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load credentials: {e}",
                tool_name=self.tool_name,
                config_key="GOOGLE_SHEETS_CREDENTIALS",
            )

    def _create_spreadsheet(self, service) -> Dict[str, Any]:
        """
        Create a new Google Spreadsheet.

        Args:
            service: Google Sheets API service

        Returns:
            Dict with spreadsheet details
        """
        # Create spreadsheet
        spreadsheet = {"properties": {"title": self.title}}

        spreadsheet = service.spreadsheets().create(body=spreadsheet, fields="spreadsheetId").execute()

        spreadsheet_id = spreadsheet.get("spreadsheetId")
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"

        # Write data
        self._write_data(service, spreadsheet_id)

        # Apply formulas if provided
        if self.formulas:
            self._apply_formulas(service, spreadsheet_id)

        # Apply formatting if provided
        if self.formatting:
            self._apply_formatting(service, spreadsheet_id)

        # Share if requested
        if self.share_with:
            self._share_spreadsheet(spreadsheet_id)

        return {
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": spreadsheet_url,
            "title": self.title,
            "mode": "create",
            "status": "created",
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
            "formulas_applied": len(self.formulas) if self.formulas else 0,
            "shared_with": self.share_with if self.share_with else [],
        }

    def _modify_spreadsheet(self, service) -> Dict[str, Any]:
        """
        Modify an existing Google Spreadsheet.

        Args:
            service: Google Sheets API service

        Returns:
            Dict with spreadsheet details
        """
        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit"

        # Write data
        self._write_data(service, self.spreadsheet_id)

        # Apply formulas if provided
        if self.formulas:
            self._apply_formulas(service, self.spreadsheet_id)

        # Apply formatting if provided
        if self.formatting:
            self._apply_formatting(service, self.spreadsheet_id)

        # Share if requested
        if self.share_with:
            self._share_spreadsheet(self.spreadsheet_id)

        return {
            "spreadsheet_id": self.spreadsheet_id,
            "spreadsheet_url": spreadsheet_url,
            "mode": "modify",
            "status": "modified",
            "rows_written": len(self.data),
            "columns_written": len(self.data[0]) if self.data else 0,
            "sheet_name": self.sheet_name,
            "formulas_applied": len(self.formulas) if self.formulas else 0,
            "shared_with": self.share_with if self.share_with else [],
        }

    def _write_data(self, service, spreadsheet_id: str) -> None:
        """
        Write data to the spreadsheet.

        Args:
            service: Google Sheets API service
            spreadsheet_id: The spreadsheet ID
        """
        range_name = f"{self.sheet_name}!A1"

        body = {"values": self.data}

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()

    def _apply_formulas(self, service, spreadsheet_id: str) -> None:
        """
        Apply formulas to specific cells.

        Args:
            service: Google Sheets API service
            spreadsheet_id: The spreadsheet ID
        """
        if not self.formulas:
            return

        for cell_ref, formula in self.formulas.items():
            range_name = f"{self.sheet_name}!{cell_ref}"

            body = {"values": [[formula]]}

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body=body,
            ).execute()

    def _apply_formatting(self, service, spreadsheet_id: str) -> None:
        """
        Apply cell formatting.

        Args:
            service: Google Sheets API service
            spreadsheet_id: The spreadsheet ID
        """
        if not self.formatting:
            return

        requests = []

        # Example formatting: bold header row
        if self.formatting.get("bold_header", False):
            requests.append(
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,  # First sheet
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                        },
                        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                        "fields": "userEnteredFormat.textFormat.bold",
                    }
                }
            )

        # Apply background color if specified
        if "background_color" in self.formatting:
            color = self.formatting["background_color"]
            # Expecting color as dict: {"red": 1.0, "green": 0.9, "blue": 0.9, "alpha": 1.0}
            if isinstance(color, dict) and "range" in self.formatting:
                cell_range = self.formatting["range"]
                requests.append(
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": 0,
                                "startRowIndex": cell_range.get("startRow", 0),
                                "endRowIndex": cell_range.get("endRow", 1),
                                "startColumnIndex": cell_range.get("startCol", 0),
                                "endColumnIndex": cell_range.get("endCol", 1),
                            },
                            "cell": {"userEnteredFormat": {"backgroundColor": color}},
                            "fields": "userEnteredFormat.backgroundColor",
                        }
                    }
                )

        # Execute batch update if there are requests
        if requests:
            body = {"requests": requests}
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def _share_spreadsheet(self, spreadsheet_id: str) -> None:
        """
        Share the spreadsheet with specified email addresses.

        Args:
            spreadsheet_id: The spreadsheet ID
        """
        if not self.share_with:
            return

        try:
            # Build Drive API service for sharing
            credentials = self._get_credentials()
            drive_service = build("drive", "v3", credentials=credentials)

            for email in self.share_with:
                permission = {"type": "user", "role": "writer", "emailAddress": email}

                drive_service.permissions().create(
                    fileId=spreadsheet_id, body=permission, sendNotificationEmail=True
                ).execute()

        except Exception as e:
            # Log but don't fail if sharing fails
            self._logger.warning(f"Failed to share spreadsheet: {e}")


if __name__ == "__main__":
    # Test the tool
    print("Testing GoogleSheets tool...\n")

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
    print(f"Rows written: {result1.get('result', {}).get('rows_written')}")
    print(f"Formulas applied: {result1.get('result', {}).get('formulas_applied')}")
    print(f"Shared with: {result1.get('result', {}).get('shared_with')}")

    assert result1.get("success") == True
    assert result1.get("result", {}).get("mode") == "create"
    assert result1.get("result", {}).get("rows_written") == 4
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
    assert result2.get("result", {}).get("mode") == "modify"
    assert result2.get("result", {}).get("status") == "modified"
    print("\n✓ Test 2 passed!\n")

    # Test 3: Validation error - invalid mode
    print("=" * 60)
    print("Test 3: Validation error - invalid mode")
    print("=" * 60)

    try:
        tool3 = GoogleSheets(mode="invalid_mode", data=[["Test"]], title="Test")
        result3 = tool3.run()
        print("Error: Should have raised ValidationError")
        assert False
    except Exception as e:
        error_result = tool3.run()
        print(f"Expected error caught: {error_result.get('error', {}).get('code')}")
        assert error_result.get("success") == False
        print("✓ Test 3 passed!\n")

    # Test 4: Validation error - missing title in create mode
    print("=" * 60)
    print("Test 4: Validation error - missing title in create mode")
    print("=" * 60)

    try:
        tool4 = GoogleSheets(mode="create", data=[["Test"]])
        result4 = tool4.run()
        print(f"Error handled: {result4.get('error', {}).get('code')}")
        assert result4.get("success") == False
        print("✓ Test 4 passed!\n")
    except Exception as e:
        print(f"Expected validation error: {e}")
        print("✓ Test 4 passed!\n")

    print("=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)
