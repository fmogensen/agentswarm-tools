"""
Standalone test script for OfficeSheetsTool
Run this directly without pytest to avoid dependency issues
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

os.environ["USE_MOCK_APIS"] = "true"

from shared.errors import ValidationError
from tools.document_creation.office_sheets.office_sheets import OfficeSheetsTool


def test_basic_spreadsheet():
    """Test basic spreadsheet generation"""
    print("Test 1: Basic spreadsheet...")
    tool = OfficeSheetsTool(data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]], headers=["A", "B", "C"])
    result = tool.run()
    assert result.get("success") == True
    assert result["result"]["rows"] == 3
    assert result["result"]["cols"] == 3
    print("✅ PASS")


def test_csv_export():
    """Test CSV export"""
    print("Test 2: CSV export...")
    tool = OfficeSheetsTool(data=[[1, 2], [3, 4]], output_format="csv")
    result = tool.run()
    assert result["result"]["format"] == "csv"
    print("✅ PASS")


def test_with_formulas():
    """Test with formulas"""
    print("Test 3: Formulas...")
    tool = OfficeSheetsTool(
        data=[[1, 2, 3], [4, 5, 6]], formulas={"D1": "=SUM(A1:C1)", "D2": "=SUM(A2:C2)"}
    )
    result = tool.run()
    assert result.get("success") == True
    print("✅ PASS")


def test_validation_empty_data():
    """Test validation for empty data"""
    print("Test 4: Empty data validation...")
    try:
        tool = OfficeSheetsTool(data=[])
        tool.run()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "cannot be empty" in str(e).lower()
        print("✅ PASS")


def test_validation_invalid_format():
    """Test validation for invalid format"""
    print("Test 5: Invalid format validation...")
    try:
        tool = OfficeSheetsTool(data=[[1, 2]], output_format="pdf")
        tool.run()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "output format" in str(e).lower()
        print("✅ PASS")


def test_validation_invalid_row():
    """Test validation for invalid row"""
    print("Test 6: Invalid row validation...")
    try:
        tool = OfficeSheetsTool(data=[[1, 2], "not a list", [3, 4]])
        tool.run()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "must be a list" in str(e).lower()
        print("✅ PASS")


def test_validation_headers_exceed():
    """Test validation for headers exceeding columns"""
    print("Test 7: Headers exceed columns validation...")
    try:
        tool = OfficeSheetsTool(data=[[1, 2]], headers=["A", "B", "C", "D"])
        tool.run()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "exceeds maximum columns" in str(e).lower()
        print("✅ PASS")


def test_validation_invalid_formula():
    """Test validation for invalid formula"""
    print("Test 8: Invalid formula validation...")
    try:
        tool = OfficeSheetsTool(data=[[1, 2]], formulas={"A1": "SUM(B1:B10)"})
        tool.run()
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "must be a string starting with" in str(e).lower()
        print("✅ PASS")


def test_both_formats():
    """Test both formats"""
    print("Test 9: Both formats...")
    tool = OfficeSheetsTool(data=[[1, 2], [3, 4]], output_format="both")
    result = tool.run()
    assert result.get("success") == True
    assert result["result"]["format"] == "both"
    print("✅ PASS")


def test_mixed_data_types():
    """Test mixed data types"""
    print("Test 10: Mixed data types...")
    tool = OfficeSheetsTool(data=[[1, "text", 3.14], [True, None, 100]])
    result = tool.run()
    assert result.get("success") == True
    print("✅ PASS")


def test_large_dataset():
    """Test large dataset"""
    print("Test 11: Large dataset (100x10)...")
    data = [[i * 10 + j for j in range(10)] for i in range(100)]
    tool = OfficeSheetsTool(data=data)
    result = tool.run()
    assert result["result"]["rows"] == 100
    assert result["result"]["cols"] == 10
    print("✅ PASS")


def test_with_formatting():
    """Test with formatting"""
    print("Test 12: With formatting...")
    tool = OfficeSheetsTool(
        data=[[1, 2, 3], [4, 5, 6]],
        headers=["A", "B", "C"],
        formatting={"bold_rows": [1], "highlight_cells": {"A1": "FFFF00"}},
    )
    result = tool.run()
    assert result.get("success") == True
    print("✅ PASS")


def test_worksheets():
    """Test multiple worksheets"""
    print("Test 13: Multiple worksheets...")
    tool = OfficeSheetsTool(
        data=[[1, 2]],
        worksheets={"Sales": [[100, 200], [300, 400]], "Expenses": [[50, 75], [100, 125]]},
    )
    result = tool.run()
    assert result.get("success") == True
    print("✅ PASS")


def test_mock_mode():
    """Test mock mode explicitly"""
    print("Test 14: Mock mode...")
    tool = OfficeSheetsTool(data=[[1, 2, 3]])
    result = tool.run()
    assert result["metadata"]["mock_mode"] == True
    assert "mock.example.com" in result["result"]["spreadsheet_url"]
    print("✅ PASS")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Running OfficeSheetsTool Standalone Tests")
    print("=" * 60 + "\n")

    tests = [
        test_basic_spreadsheet,
        test_csv_export,
        test_with_formulas,
        test_validation_empty_data,
        test_validation_invalid_format,
        test_validation_invalid_row,
        test_validation_headers_exceed,
        test_validation_invalid_formula,
        test_both_formats,
        test_mixed_data_types,
        test_large_dataset,
        test_with_formatting,
        test_worksheets,
        test_mock_mode,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ FAIL: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60 + "\n")

    sys.exit(0 if failed == 0 else 1)
