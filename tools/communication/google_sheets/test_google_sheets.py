"""
Unit tests for Google Sheets tool
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from shared.errors import APIError, ConfigurationError, ValidationError
from tools.communication.google_sheets.google_sheets import GoogleSheets


class TestGoogleSheets:
    """Test suite for GoogleSheets tool"""

    def setup_method(self):
        """Setup test environment"""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after tests"""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    # ===========================
    # MOCK MODE TESTS
    # ===========================

    def test_create_spreadsheet_mock(self):
        """Test creating a new spreadsheet in mock mode"""
        tool = GoogleSheets(
            mode="create",
            title="Test Spreadsheet",
            data=[["Header1", "Header2"], ["Value1", "Value2"]],
            sheet_name="Sheet1",
        )

        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True
        assert result["result"]["mode"] == "create"
        assert result["result"]["title"] == "Test Spreadsheet"
        assert result["result"]["status"] == "created"
        assert result["result"]["rows_written"] == 2
        assert result["result"]["columns_written"] == 2
        assert "spreadsheet_id" in result["result"]
        assert "spreadsheet_url" in result["result"]

    def test_modify_spreadsheet_mock(self):
        """Test modifying existing spreadsheet in mock mode"""
        tool = GoogleSheets(
            mode="modify",
            spreadsheet_id="1ABC123",
            data=[["Updated1", "Updated2"]],
            sheet_name="Sheet1",
        )

        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True
        assert result["result"]["mode"] == "modify"
        assert result["result"]["status"] == "modified"
        assert result["result"]["spreadsheet_id"] == "1ABC123"

    def test_create_with_formulas_mock(self):
        """Test creating spreadsheet with formulas"""
        tool = GoogleSheets(
            mode="create",
            title="Budget",
            data=[["Item", "Cost"], ["Item1", 100], ["Item2", 200]],
            formulas={"B4": "=SUM(B2:B3)"},
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formulas_applied"] == 1

    def test_create_with_sharing_mock(self):
        """Test creating spreadsheet with sharing"""
        tool = GoogleSheets(
            mode="create",
            title="Shared Sheet",
            data=[["Data"]],
            share_with=["user1@example.com", "user2@example.com"],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["shared_with"] == ["user1@example.com", "user2@example.com"]

    def test_create_with_formatting_mock(self):
        """Test creating spreadsheet with formatting"""
        tool = GoogleSheets(
            mode="create",
            title="Formatted Sheet",
            data=[["Header"], ["Data"]],
            formatting={"bold_header": True},
        )

        result = tool.run()

        assert result["success"] == True

    # ===========================
    # VALIDATION TESTS
    # ===========================

    def test_invalid_mode(self):
        """Test validation error for invalid mode"""
        tool = GoogleSheets(mode="invalid", data=[["Test"]], title="Test")

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "Invalid mode" in result["error"]["message"]

    def test_missing_title_create_mode(self):
        """Test validation error for missing title in create mode"""
        tool = GoogleSheets(mode="create", data=[["Test"]])

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "Title is required" in result["error"]["message"]

    def test_missing_spreadsheet_id_modify_mode(self):
        """Test validation error for missing spreadsheet_id in modify mode"""
        tool = GoogleSheets(mode="modify", data=[["Test"]])

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "Spreadsheet ID is required" in result["error"]["message"]

    def test_invalid_data_not_list(self):
        """Test validation error for invalid data type"""
        tool = GoogleSheets(mode="create", title="Test", data="not a list")

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_data_not_list_of_lists(self):
        """Test validation error for data not being list of lists"""
        tool = GoogleSheets(mode="create", title="Test", data=["not", "list", "of", "lists"])

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_email_in_share_with(self):
        """Test validation error for invalid email"""
        tool = GoogleSheets(
            mode="create", title="Test", data=[["Data"]], share_with=["invalid-email"]
        )

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"
        assert "Invalid email" in result["error"]["message"]

    def test_empty_data(self):
        """Test validation error for empty data"""
        tool = GoogleSheets(mode="create", title="Test", data=[])

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    def test_formulas_not_dict(self):
        """Test validation error for formulas not being a dict"""
        tool = GoogleSheets(
            mode="create", title="Test", data=[["Data"]], formulas=["not", "a", "dict"]
        )

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "VALIDATION_ERROR"

    # ===========================
    # COMPLEX SCENARIOS
    # ===========================

    def test_large_dataset_mock(self):
        """Test handling large dataset"""
        # Create 100 rows of data
        data = [["Col1", "Col2", "Col3"]]
        for i in range(1, 100):
            data.append([f"Row{i}", i * 10, i * 20])

        tool = GoogleSheets(mode="create", title="Large Dataset", data=data)

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["rows_written"] == 100

    def test_multiple_formulas_mock(self):
        """Test multiple formulas"""
        formulas = {
            "D2": "=SUM(B2:C2)",
            "D3": "=SUM(B3:C3)",
            "D4": "=SUM(B4:C4)",
            "D5": "=AVERAGE(D2:D4)",
        }

        tool = GoogleSheets(
            mode="create",
            title="Multi Formula",
            data=[["A", "B", "C"], [1, 2, 3], [4, 5, 6], [7, 8, 9]],
            formulas=formulas,
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["formulas_applied"] == 4

    def test_complex_formatting_mock(self):
        """Test complex formatting options"""
        formatting = {
            "bold_header": True,
            "background_color": {"red": 1.0, "green": 0.9, "blue": 0.9, "alpha": 1.0},
            "range": {"startRow": 0, "endRow": 1, "startCol": 0, "endCol": 3},
        }

        tool = GoogleSheets(
            mode="create", title="Formatted", data=[["H1", "H2", "H3"]], formatting=formatting
        )

        result = tool.run()

        assert result["success"] == True

    def test_modify_with_all_options_mock(self):
        """Test modify mode with all options"""
        tool = GoogleSheets(
            mode="modify",
            spreadsheet_id="1ABC123",
            data=[["Updated", "Data"]],
            sheet_name="UpdatedSheet",
            formulas={"C1": "=A1+B1"},
            formatting={"bold_header": True},
            share_with=["new.user@example.com"],
        )

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["mode"] == "modify"
        assert result["result"]["sheet_name"] == "UpdatedSheet"
        assert result["result"]["formulas_applied"] == 1
        assert len(result["result"]["shared_with"]) == 1

    # ===========================
    # EDGE CASES
    # ===========================

    def test_single_cell_data(self):
        """Test with single cell of data"""
        tool = GoogleSheets(mode="create", title="Single Cell", data=[["Single Value"]])

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["rows_written"] == 1
        assert result["result"]["columns_written"] == 1

    def test_empty_string_values(self):
        """Test with empty string values in data"""
        tool = GoogleSheets(
            mode="create", title="Empty Values", data=[["", "Value"], ["Value", ""]]
        )

        result = tool.run()

        assert result["success"] == True

    def test_mixed_data_types(self):
        """Test with mixed data types"""
        tool = GoogleSheets(
            mode="create",
            title="Mixed Types",
            data=[["String", 123, 45.67, True, None], ["Another", 456, 78.90, False, ""]],
        )

        result = tool.run()

        assert result["success"] == True

    def test_unicode_characters(self):
        """Test with unicode characters"""
        tool = GoogleSheets(
            mode="create",
            title="Unicode Test 你好",
            data=[["Hello", "世界"], ["Emoji", "😀🎉"]],
        )

        result = tool.run()

        assert result["success"] == True

    def test_special_characters_in_title(self):
        """Test with special characters in title"""
        tool = GoogleSheets(
            mode="create",
            title="Report: Q4 [2024] - Sales & Revenue (Final)",
            data=[["Data"]],
        )

        result = tool.run()

        assert result["success"] == True

    # ===========================
    # REAL API TESTS (with mocking)
    # ===========================

    @patch("tools.communication.google_sheets.google_sheets.build")
    @patch("tools.communication.google_sheets.google_sheets.Credentials")
    def test_create_real_api_call(self, mock_credentials, mock_build):
        """Test real API call for create (mocked)"""
        # Disable mock mode
        os.environ["USE_MOCK_APIS"] = "false"
        os.environ["GOOGLE_SHEETS_CREDENTIALS"] = "/tmp/fake_credentials.json"

        # Mock the API responses
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        mock_spreadsheet = {"spreadsheetId": "real_id_123"}
        mock_service.spreadsheets().create().execute.return_value = mock_spreadsheet
        mock_service.spreadsheets().values().update().execute.return_value = {}

        # Mock credentials
        mock_creds = MagicMock()
        mock_credentials.from_service_account_file.return_value = mock_creds

        # Create mock credentials file
        with open("/tmp/fake_credentials.json", "w") as f:
            f.write("{}")

        tool = GoogleSheets(mode="create", title="API Test", data=[["Test"]])

        result = tool.run()

        assert result["success"] == True
        assert result["result"]["spreadsheet_id"] == "real_id_123"

        # Cleanup
        os.remove("/tmp/fake_credentials.json")
        os.environ["USE_MOCK_APIS"] = "true"
        del os.environ["GOOGLE_SHEETS_CREDENTIALS"]

    def test_missing_credentials_env(self):
        """Test error when credentials environment variable is missing"""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = GoogleSheets(mode="create", title="Test", data=[["Data"]])

        result = tool.run()

        assert result["success"] == False
        assert result["error"]["code"] == "CONFIG_ERROR"

        os.environ["USE_MOCK_APIS"] = "true"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
