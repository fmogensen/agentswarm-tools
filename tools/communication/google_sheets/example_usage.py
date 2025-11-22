#!/usr/bin/env python3
"""
Example usage of the Google Sheets tool

This file demonstrates various ways to use the GoogleSheets tool
for creating and modifying Google Spreadsheets.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from tools.communication.google_sheets import GoogleSheets


def example_1_create_basic_spreadsheet():
    """Example 1: Create a basic spreadsheet"""
    print("\n" + "=" * 70)
    print("Example 1: Create Basic Spreadsheet")
    print("=" * 70)

    tool = GoogleSheets(
        mode="create",
        title="Employee Directory",
        data=[
            ["Name", "Department", "Email", "Phone"],
            ["Alice Johnson", "Engineering", "alice@company.com", "555-0100"],
            ["Bob Smith", "Marketing", "bob@company.com", "555-0101"],
            ["Carol White", "Sales", "carol@company.com", "555-0102"],
        ],
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Spreadsheet created successfully!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
        print(f"  ID: {result['result']['spreadsheet_id']}")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_2_create_with_formulas():
    """Example 2: Create spreadsheet with formulas"""
    print("\n" + "=" * 70)
    print("Example 2: Create Spreadsheet with Formulas")
    print("=" * 70)

    tool = GoogleSheets(
        mode="create",
        title="Q4 Sales Report",
        data=[
            ["Product", "Oct", "Nov", "Dec", "Total"],
            ["Product A", 1000, 1200, 1500, ""],  # Formula will go in E2
            ["Product B", 800, 900, 1100, ""],  # Formula will go in E3
            ["Product C", 1500, 1600, 1800, ""],  # Formula will go in E4
            ["Total", "", "", "", ""],  # Formulas will go in B5, C5, D5, E5
        ],
        formulas={
            # Row totals
            "E2": "=SUM(B2:D2)",
            "E3": "=SUM(B3:D3)",
            "E4": "=SUM(B4:D4)",
            # Column totals
            "B5": "=SUM(B2:B4)",
            "C5": "=SUM(C2:C4)",
            "D5": "=SUM(D2:D4)",
            "E5": "=SUM(E2:E4)",
        },
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Spreadsheet with formulas created!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
        print(f"  Formulas applied: {result['result']['formulas_applied']}")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_3_create_with_formatting():
    """Example 3: Create spreadsheet with formatting"""
    print("\n" + "=" * 70)
    print("Example 3: Create Spreadsheet with Formatting")
    print("=" * 70)

    tool = GoogleSheets(
        mode="create",
        title="Project Status Dashboard",
        data=[
            ["Project", "Status", "Progress", "Owner"],
            ["Website Redesign", "In Progress", "75%", "Alice"],
            ["Mobile App", "Planning", "25%", "Bob"],
            ["API Migration", "Completed", "100%", "Carol"],
        ],
        formatting={
            "bold_header": True,
            "background_color": {"red": 0.9, "green": 0.95, "blue": 1.0, "alpha": 1.0},
            "range": {"startRow": 0, "endRow": 1, "startCol": 0, "endCol": 4},
        },
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Formatted spreadsheet created!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_4_create_and_share():
    """Example 4: Create and share spreadsheet"""
    print("\n" + "=" * 70)
    print("Example 4: Create and Share Spreadsheet")
    print("=" * 70)

    tool = GoogleSheets(
        mode="create",
        title="Team Budget 2024",
        data=[
            ["Category", "Budget", "Spent", "Remaining"],
            ["Software", 50000, 35000, "=B2-C2"],
            ["Hardware", 30000, 28000, "=B3-C3"],
            ["Training", 20000, 15000, "=B4-C4"],
        ],
        formulas={"D2": "=B2-C2", "D3": "=B3-C3", "D4": "=B4-C4"},
        share_with=["manager@company.com", "finance@company.com"],
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Spreadsheet created and shared!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
        print(f"  Shared with: {', '.join(result['result']['shared_with'])}")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_5_modify_existing():
    """Example 5: Modify existing spreadsheet"""
    print("\n" + "=" * 70)
    print("Example 5: Modify Existing Spreadsheet")
    print("=" * 70)

    # In a real scenario, you would use an actual spreadsheet ID
    spreadsheet_id = "1ABC123XYZ_example_id"

    tool = GoogleSheets(
        mode="modify",
        spreadsheet_id=spreadsheet_id,
        data=[
            ["Updated Data", "New Values"],
            ["Row 1", 100],
            ["Row 2", 200],
            ["Row 3", 300],
        ],
        sheet_name="Sheet1",
        formulas={"B5": "=SUM(B2:B4)"},
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Spreadsheet modified successfully!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
        print(f"  Status: {result['result']['status']}")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_6_financial_report():
    """Example 6: Create comprehensive financial report"""
    print("\n" + "=" * 70)
    print("Example 6: Financial Report with Multiple Formulas")
    print("=" * 70)

    tool = GoogleSheets(
        mode="create",
        title="Monthly Financial Report - November 2024",
        data=[
            ["Category", "Amount", "% of Total", "Notes"],
            ["Revenue", 150000, "", "Total sales"],
            ["Cost of Goods", 60000, "", "Direct costs"],
            ["Gross Profit", "", "", "Revenue - COGS"],
            ["Operating Expenses", 40000, "", "Overhead"],
            ["Net Profit", "", "", "Gross - Operating"],
            ["Profit Margin", "", "", "Net / Revenue"],
        ],
        formulas={
            "B4": "=B2-B3",  # Gross Profit
            "B6": "=B4-B5",  # Net Profit
            "B7": "=B6/B2",  # Profit Margin
            "C2": "=B2/B2",  # Revenue % (100%)
            "C3": "=B3/B2",  # COGS %
            "C5": "=B5/B2",  # Operating %
            "C6": "=B6/B2",  # Net Profit %
        },
        formatting={"bold_header": True},
        share_with=["cfo@company.com", "accountant@company.com"],
    )

    result = tool.run()

    if result["success"]:
        print(f"✓ Financial report created!")
        print(f"  URL: {result['result']['spreadsheet_url']}")
        print(f"  Formulas applied: {result['result']['formulas_applied']}")
        print(f"  Shared with: {len(result['result']['shared_with'])} people")
    else:
        print(f"✗ Error: {result['error']['message']}")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n" + "=" * 70)
    print("Example 7: Error Handling")
    print("=" * 70)

    # Example of validation error - missing title in create mode
    tool = GoogleSheets(mode="create", data=[["Test"]])

    result = tool.run()

    if not result["success"]:
        print(f"✓ Error caught correctly:")
        print(f"  Error Code: {result['error']['code']}")
        print(f"  Message: {result['error']['message']}")
    else:
        print(f"✗ Should have failed validation")


def main():
    """Run all examples"""
    # Enable mock mode for demonstration
    os.environ["USE_MOCK_APIS"] = "true"

    print("\n" + "=" * 70)
    print("Google Sheets Tool - Usage Examples")
    print("=" * 70)
    print("\nNOTE: Running in MOCK mode. Set USE_MOCK_APIS=false to use real API.")
    print("      You'll also need to set GOOGLE_SHEETS_CREDENTIALS environment variable.")

    # Run all examples
    example_1_create_basic_spreadsheet()
    example_2_create_with_formulas()
    example_3_create_with_formatting()
    example_4_create_and_share()
    example_5_modify_existing()
    example_6_financial_report()
    example_7_error_handling()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nTo use with real Google Sheets API:")
    print("1. Set GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json")
    print("2. Set USE_MOCK_APIS=false")
    print("3. Run the examples again")
    print()


if __name__ == "__main__":
    main()
