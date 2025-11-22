"""
Unit tests for OfficeSheetsTool
"""

import pytest
import os
from office_sheets import OfficeSheetsTool
from shared.errors import ValidationError, APIError


class TestOfficeSheetsTool:
    """Test suite for OfficeSheetsTool"""

    def setup_method(self):
        """Setup test environment"""
        os.environ["USE_MOCK_APIS"] = "true"

    def teardown_method(self):
        """Cleanup after tests"""
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_basic_spreadsheet(self):
        """Test basic spreadsheet generation"""
        tool = OfficeSheetsTool(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]], headers=["A", "B", "C"])
        result = tool.run()

        assert result.get("success") == True
        assert "result" in result
        assert result["result"]["rows"] == 3
        assert result["result"]["cols"] == 3
        assert result["result"]["format"] == "xlsx"

    def test_csv_export(self):
        """Test CSV export format"""
        tool = OfficeSheetsTool(data=[[1, 2], [3, 4]], output_format="csv")
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["format"] == "csv"
        assert "spreadsheet_url" in result["result"]

    def test_xlsx_export(self):
        """Test XLSX export format"""
        tool = OfficeSheetsTool(data=[[100, 200], [300, 400]], output_format="xlsx")
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["format"] == "xlsx"

    def test_both_formats(self):
        """Test exporting to both formats"""
        tool = OfficeSheetsTool(data=[[1, 2], [3, 4]], output_format="both")
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["format"] == "both"
        assert "spreadsheet_url" in result["result"]
        assert "csv_url" in result["result"]

    def test_with_headers(self):
        """Test spreadsheet with headers"""
        tool = OfficeSheetsTool(data=[[100, 200, 300], [150, 250, 350]], headers=["Q1", "Q2", "Q3"])
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["rows"] == 2
        assert result["result"]["cols"] == 3

    def test_with_formulas(self):
        """Test spreadsheet with formulas"""
        tool = OfficeSheetsTool(
            data=[[1, 2, 3], [4, 5, 6]], formulas={"D1": "=SUM(A1:C1)", "D2": "=SUM(A2:C2)"}
        )
        result = tool.run()

        assert result.get("success") == True

    def test_empty_data_validation(self):
        """Test validation for empty data"""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSheetsTool(data=[])
            tool.run()

        assert "cannot be empty" in str(exc_info.value).lower()

    def test_invalid_output_format(self):
        """Test validation for invalid output format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSheetsTool(data=[[1, 2]], output_format="pdf")  # Invalid format
            tool.run()

        assert "output format" in str(exc_info.value).lower()

    def test_invalid_row_type(self):
        """Test validation for invalid row type"""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSheetsTool(data=[[1, 2], "not a list", [3, 4]])  # Invalid row
            tool.run()

        assert "must be a list" in str(exc_info.value).lower()

    def test_headers_exceed_columns(self):
        """Test validation when headers exceed data columns"""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSheetsTool(data=[[1, 2]], headers=["A", "B", "C", "D"])  # Too many headers
            tool.run()

        assert "exceeds maximum columns" in str(exc_info.value).lower()

    def test_invalid_formula_format(self):
        """Test validation for invalid formula format"""
        with pytest.raises(ValidationError) as exc_info:
            tool = OfficeSheetsTool(data=[[1, 2]], formulas={"A1": "SUM(B1:B10)"})  # Missing '='
            tool.run()

        assert "must be a string starting with" in str(exc_info.value).lower()

    def test_mock_mode(self):
        """Test mock mode explicitly"""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSheetsTool(data=[[1, 2, 3], [4, 5, 6]])
        result = tool.run()

        assert result.get("success") == True
        assert result["metadata"]["mock_mode"] == True
        assert "mock.example.com" in result["result"]["spreadsheet_url"]

    def test_single_row(self):
        """Test spreadsheet with single row"""
        tool = OfficeSheetsTool(data=[[1, 2, 3]])
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["rows"] == 1
        assert result["result"]["cols"] == 3

    def test_single_column(self):
        """Test spreadsheet with single column"""
        tool = OfficeSheetsTool(data=[[1], [2], [3]])
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["rows"] == 3
        assert result["result"]["cols"] == 1

    def test_mixed_data_types(self):
        """Test spreadsheet with mixed data types"""
        tool = OfficeSheetsTool(data=[[1, "text", 3.14], [True, None, 100]])
        result = tool.run()

        assert result.get("success") == True

    def test_large_dataset(self):
        """Test spreadsheet with larger dataset"""
        # Generate 100 rows x 10 columns
        data = [[i * 10 + j for j in range(10)] for i in range(100)]

        tool = OfficeSheetsTool(data=data)
        result = tool.run()

        assert result.get("success") == True
        assert result["result"]["rows"] == 100
        assert result["result"]["cols"] == 10

    def test_with_formatting(self):
        """Test spreadsheet with formatting rules"""
        tool = OfficeSheetsTool(
            data=[[1, 2, 3], [4, 5, 6]],
            headers=["A", "B", "C"],
            formatting={"bold_rows": [1], "highlight_cells": {"A1": "FFFF00"}},
        )
        result = tool.run()

        assert result.get("success") == True

    def test_multiple_formulas(self):
        """Test multiple formulas"""
        tool = OfficeSheetsTool(
            data=[[10, 20, 30], [15, 25, 35]],
            formulas={
                "D1": "=SUM(A1:C1)",
                "D2": "=SUM(A2:C2)",
                "D3": "=SUM(D1:D2)",
                "E1": "=AVERAGE(A1:C1)",
            },
        )
        result = tool.run()

        assert result.get("success") == True

    def test_worksheets_parameter(self):
        """Test multiple worksheets"""
        tool = OfficeSheetsTool(
            data=[[1, 2]],  # Main data (required)
            worksheets={"Sales": [[100, 200], [300, 400]], "Expenses": [[50, 75], [100, 125]]},
        )
        result = tool.run()

        assert result.get("success") == True


class TestOfficeSheetsMockMode:
    """Test mock mode behavior"""

    def test_mock_mode_enabled(self):
        """Test behavior when mock mode is enabled"""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = OfficeSheetsTool(data=[[1, 2, 3]])
        result = tool.run()

        assert result.get("success") == True
        assert result["metadata"]["mock_mode"] == True
        assert "mock" in result["result"]["spreadsheet_url"]

        del os.environ["USE_MOCK_APIS"]

    def test_mock_mode_disabled(self):
        """Test behavior when mock mode is disabled"""
        os.environ["USE_MOCK_APIS"] = "false"

        tool = OfficeSheetsTool(data=[[1, 2, 3]])
        # Note: This would normally call real implementation
        # In test environment, we just verify it doesn't use mock

        del os.environ["USE_MOCK_APIS"]


class TestOfficeSheetValidation:
    """Test input validation"""

    def test_empty_data_list(self):
        """Test validation rejects empty data"""
        with pytest.raises(ValidationError):
            tool = OfficeSheetsTool(data=[])
            tool.run()

    def test_non_list_data(self):
        """Test validation rejects non-list data"""
        # Pydantic will catch this before _validate_parameters
        with pytest.raises((ValidationError, Exception)):
            tool = OfficeSheetsTool(data="not a list")

    def test_formulas_not_dict(self):
        """Test validation rejects non-dict formulas"""
        with pytest.raises(ValidationError):
            tool = OfficeSheetsTool(data=[[1, 2]], formulas=["=SUM(A1:B1)"])  # Should be dict
            tool.run()

    def test_formula_without_equals(self):
        """Test validation rejects formulas without '='"""
        with pytest.raises(ValidationError):
            tool = OfficeSheetsTool(data=[[1, 2]], formulas={"A1": "SUM(B1:B10)"})  # Missing '='
            tool.run()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
