#!/usr/bin/env python3
"""
Standalone test runner for Google Sheets tool
Does not require pytest - can run directly
"""

import os
import sys

# Set mock mode
os.environ["USE_MOCK_APIS"] = "true"

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from tools.communication.google_sheets.google_sheets import GoogleSheets


def test_create_spreadsheet_mock():
    """Test creating a new spreadsheet in mock mode"""
    print("Test 1: Create spreadsheet (mock mode)...")

    tool = GoogleSheets(
        mode="create",
        title="Test Spreadsheet",
        data=[["Header1", "Header2"], ["Value1", "Value2"]],
        sheet_name="Sheet1",
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"
    assert result["metadata"]["mock_mode"] == True, "Expected mock_mode=True"
    assert result["result"]["mode"] == "create", "Expected mode=create"
    assert result["result"]["title"] == "Test Spreadsheet", "Title mismatch"
    assert result["result"]["status"] == "created", "Expected status=created"
    assert result["result"]["rows_written"] == 2, "Expected 2 rows"
    assert result["result"]["columns_written"] == 2, "Expected 2 columns"
    assert "spreadsheet_id" in result["result"], "Missing spreadsheet_id"
    assert "spreadsheet_url" in result["result"], "Missing spreadsheet_url"

    print("✓ Test 1 passed!")
    return True


def test_modify_spreadsheet_mock():
    """Test modifying existing spreadsheet in mock mode"""
    print("\nTest 2: Modify spreadsheet (mock mode)...")

    tool = GoogleSheets(
        mode="modify",
        spreadsheet_id="1ABC123",
        data=[["Updated1", "Updated2"]],
        sheet_name="Sheet1",
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"
    assert result["metadata"]["mock_mode"] == True, "Expected mock_mode=True"
    assert result["result"]["mode"] == "modify", "Expected mode=modify"
    assert result["result"]["status"] == "modified", "Expected status=modified"
    assert result["result"]["spreadsheet_id"] == "1ABC123", "Spreadsheet ID mismatch"

    print("✓ Test 2 passed!")
    return True


def test_create_with_formulas_mock():
    """Test creating spreadsheet with formulas"""
    print("\nTest 3: Create with formulas...")

    tool = GoogleSheets(
        mode="create",
        title="Budget",
        data=[["Item", "Cost"], ["Item1", 100], ["Item2", 200]],
        formulas={"B4": "=SUM(B2:B3)"},
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"
    assert result["result"]["formulas_applied"] == 1, "Expected 1 formula"

    print("✓ Test 3 passed!")
    return True


def test_create_with_sharing_mock():
    """Test creating spreadsheet with sharing"""
    print("\nTest 4: Create with sharing...")

    tool = GoogleSheets(
        mode="create",
        title="Shared Sheet",
        data=[["Data"]],
        share_with=["user1@example.com", "user2@example.com"],
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"
    assert len(result["result"]["shared_with"]) == 2, "Expected 2 shared users"

    print("✓ Test 4 passed!")
    return True


def test_invalid_mode():
    """Test validation error for invalid mode"""
    print("\nTest 5: Invalid mode validation...")

    tool = GoogleSheets(mode="invalid", data=[["Test"]], title="Test")
    result = tool.run()

    assert result["success"] == False, "Expected success=False"
    assert result["error"]["code"] == "VALIDATION_ERROR", "Expected VALIDATION_ERROR"
    assert "Invalid mode" in result["error"]["message"], "Error message mismatch"

    print("✓ Test 5 passed!")
    return True


def test_missing_title_create_mode():
    """Test validation error for missing title in create mode"""
    print("\nTest 6: Missing title in create mode...")

    tool = GoogleSheets(mode="create", data=[["Test"]])
    result = tool.run()

    assert result["success"] == False, "Expected success=False"
    assert result["error"]["code"] == "VALIDATION_ERROR", "Expected VALIDATION_ERROR"
    assert "Title is required" in result["error"]["message"], "Error message mismatch"

    print("✓ Test 6 passed!")
    return True


def test_missing_spreadsheet_id_modify_mode():
    """Test validation error for missing spreadsheet_id in modify mode"""
    print("\nTest 7: Missing spreadsheet_id in modify mode...")

    tool = GoogleSheets(mode="modify", data=[["Test"]])
    result = tool.run()

    assert result["success"] == False, "Expected success=False"
    assert result["error"]["code"] == "VALIDATION_ERROR", "Expected VALIDATION_ERROR"
    assert "Spreadsheet ID is required" in result["error"]["message"], "Error message mismatch"

    print("✓ Test 7 passed!")
    return True


def test_invalid_email_in_share_with():
    """Test validation error for invalid email"""
    print("\nTest 8: Invalid email validation...")

    tool = GoogleSheets(mode="create", title="Test", data=[["Data"]], share_with=["invalid-email"])
    result = tool.run()

    assert result["success"] == False, "Expected success=False"
    assert result["error"]["code"] == "VALIDATION_ERROR", "Expected VALIDATION_ERROR"
    assert "Invalid email" in result["error"]["message"], "Error message mismatch"

    print("✓ Test 8 passed!")
    return True


def test_large_dataset_mock():
    """Test handling large dataset"""
    print("\nTest 9: Large dataset (100 rows)...")

    # Create 100 rows of data
    data = [["Col1", "Col2", "Col3"]]
    for i in range(1, 100):
        data.append([f"Row{i}", i * 10, i * 20])

    tool = GoogleSheets(mode="create", title="Large Dataset", data=data)
    result = tool.run()

    assert result["success"] == True, "Expected success=True"
    assert result["result"]["rows_written"] == 100, "Expected 100 rows"

    print("✓ Test 9 passed!")
    return True


def test_multiple_formulas_mock():
    """Test multiple formulas"""
    print("\nTest 10: Multiple formulas...")

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

    assert result["success"] == True, "Expected success=True"
    assert result["result"]["formulas_applied"] == 4, "Expected 4 formulas"

    print("✓ Test 10 passed!")
    return True


def test_unicode_characters():
    """Test with unicode characters"""
    print("\nTest 11: Unicode characters...")

    tool = GoogleSheets(
        mode="create",
        title="Unicode Test 你好",
        data=[["Hello", "世界"], ["Emoji", "😀🎉"]],
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"

    print("✓ Test 11 passed!")
    return True


def test_mixed_data_types():
    """Test with mixed data types"""
    print("\nTest 12: Mixed data types...")

    tool = GoogleSheets(
        mode="create",
        title="Mixed Types",
        data=[["String", 123, 45.67, True, None], ["Another", 456, 78.90, False, ""]],
    )

    result = tool.run()

    assert result["success"] == True, "Expected success=True"

    print("✓ Test 12 passed!")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("Google Sheets Tool - Test Suite")
    print("=" * 70)

    tests = [
        test_create_spreadsheet_mock,
        test_modify_spreadsheet_mock,
        test_create_with_formulas_mock,
        test_create_with_sharing_mock,
        test_invalid_mode,
        test_missing_title_create_mode,
        test_missing_spreadsheet_id_modify_mode,
        test_invalid_email_in_share_with,
        test_large_dataset_mock,
        test_multiple_formulas_mock,
        test_unicode_characters,
        test_mixed_data_types,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
