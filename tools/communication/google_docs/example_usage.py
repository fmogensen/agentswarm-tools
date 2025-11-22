#!/usr/bin/env python3
"""
Example usage of GoogleDocs tool.
Demonstrates practical use cases.
"""

import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Enable mock mode for examples
os.environ["USE_MOCK_APIS"] = "true"

from tools.communication.google_docs.google_docs import GoogleDocs


def example_1_simple_document():
    """Example 1: Create a simple document."""
    print("\n" + "="*70)
    print("Example 1: Create a Simple Document")
    print("="*70)

    tool = GoogleDocs(
        mode="create",
        title="Meeting Notes",
        content="# Team Meeting\n\nDiscussed Q4 goals and objectives."
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Document ID: {result['result']['document_id']}")
    print(f"Link: {result['result']['shareable_link']}")


def example_2_formatted_document():
    """Example 2: Create document with rich formatting."""
    print("\n" + "="*70)
    print("Example 2: Create Document with Rich Formatting")
    print("="*70)

    content = """
# Project Proposal

## Executive Summary
This project aims to improve **customer satisfaction** by implementing
a new *feedback system*.

## Key Objectives
- Increase response rate
- Reduce processing time
- Improve analytics

## Timeline
### Phase 1
Initial development and testing.

### Phase 2
Rollout and monitoring.

## Next Steps
Follow up meeting scheduled for next week.
"""

    tool = GoogleDocs(
        mode="create",
        title="Project Proposal - Customer Feedback System",
        content=content
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Document: {result['result']['title']}")
    print(f"Preview: {result['result']['content_preview'][:80]}...")


def example_3_shared_document():
    """Example 3: Create and share a document."""
    print("\n" + "="*70)
    print("Example 3: Create and Share Document")
    print("="*70)

    tool = GoogleDocs(
        mode="create",
        title="Team Collaboration Doc",
        content="# Welcome Team\n\nPlease add your input below.",
        share_with=[
            "alice@company.com",
            "bob@company.com",
            "charlie@company.com"
        ]
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Document: {result['result']['title']}")
    print(f"Shared with {len(result['result']['shared_with'])} people:")
    for email in result['result']['shared_with']:
        print(f"  - {email}")


def example_4_organized_in_folder():
    """Example 4: Create document in specific folder."""
    print("\n" + "="*70)
    print("Example 4: Create Document in Folder")
    print("="*70)

    tool = GoogleDocs(
        mode="create",
        title="Q4 Report",
        content="# Q4 Financial Report\n\n[Report content here]",
        folder_id="finance-reports-folder-123"
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Document: {result['result']['title']}")
    print(f"Folder: {result['result']['folder_id']}")


def example_5_append_content():
    """Example 5: Append content to existing document."""
    print("\n" + "="*70)
    print("Example 5: Append Content to Existing Document")
    print("="*70)

    # First create a document (in real scenario, you'd have an existing doc ID)
    create_tool = GoogleDocs(
        mode="create",
        title="Running Notes",
        content="# Daily Notes\n\n## Monday\nProject kickoff meeting."
    )
    create_result = create_tool.run()
    doc_id = create_result['result']['document_id']

    print(f"Created document: {doc_id}")

    # Now append new content
    append_tool = GoogleDocs(
        mode="modify",
        document_id=doc_id,
        content="\n## Tuesday\nReviewed design mockups.",
        modify_action="append"
    )
    append_result = append_tool.run()

    print(f"Status: {'Success' if append_result['success'] else 'Failed'}")
    print(f"Action: {append_result['result']['modify_action']}")
    print("Content appended successfully!")


def example_6_replace_content():
    """Example 6: Replace entire document content."""
    print("\n" + "="*70)
    print("Example 6: Replace Document Content")
    print("="*70)

    # Simulate updating a template
    tool = GoogleDocs(
        mode="modify",
        document_id="template-doc-456",
        content="""
# Updated Template

## New Structure
This is the updated template with revised content.

## Instructions
Follow these new guidelines.
""",
        modify_action="replace"
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Action: {result['result']['modify_action']}")
    print("Content replaced successfully!")


def example_7_insert_content():
    """Example 7: Insert content at specific position."""
    print("\n" + "="*70)
    print("Example 7: Insert Content at Beginning")
    print("="*70)

    tool = GoogleDocs(
        mode="modify",
        document_id="existing-doc-789",
        content="**URGENT UPDATE**\n\n",
        modify_action="insert",
        insert_index=1
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Action: {result['result']['modify_action']}")
    print("Urgent update inserted at beginning!")


def example_8_meeting_minutes():
    """Example 8: Real-world use case - Meeting minutes."""
    print("\n" + "="*70)
    print("Example 8: Real-World - Meeting Minutes")
    print("="*70)

    # Generate meeting minutes
    date = "2024-01-15"
    attendees = ["Alice", "Bob", "Charlie", "Diana"]
    topics = [
        "Q4 Results Review",
        "Q1 Planning",
        "Budget Allocation"
    ]

    content = f"""
# Team Meeting Minutes
**Date:** {date}

## Attendees
{chr(10).join(f'- {name}' for name in attendees)}

## Agenda
{chr(10).join(f'{i+1}. {topic}' for i, topic in enumerate(topics))}

## Discussion Notes

### Q4 Results Review
**Presented by:** Alice

Key highlights:
- Revenue exceeded targets by **15%**
- Customer satisfaction at *all-time high*
- Successful product launches

### Q1 Planning
**Presented by:** Bob

Priorities for next quarter:
- Feature development
- Market expansion
- Team growth

### Budget Allocation
**Presented by:** Charlie

Budget approved for:
- Engineering: $500K
- Marketing: $300K
- Operations: $200K

## Action Items
- [ ] Alice: Finalize Q4 report by Friday
- [ ] Bob: Share Q1 roadmap by Monday
- [ ] Charlie: Process budget approvals
- [ ] Diana: Schedule follow-up meeting

## Next Meeting
**Date:** {date} + 1 week
**Location:** Conference Room B
"""

    tool = GoogleDocs(
        mode="create",
        title=f"Team Meeting Minutes - {date}",
        content=content,
        share_with=[f"{name.lower()}@company.com" for name in attendees],
        folder_id="meeting-minutes-2024"
    )
    result = tool.run()

    print(f"Status: {'Success' if result['success'] else 'Failed'}")
    print(f"Document: {result['result']['title']}")
    print(f"Shared with: {', '.join(result['result']['shared_with'][:3])}...")
    print(f"Folder: {result['result'].get('folder_id', 'N/A')}")
    print(f"Link: {result['result']['shareable_link']}")


def example_9_error_handling():
    """Example 9: Proper error handling."""
    print("\n" + "="*70)
    print("Example 9: Error Handling")
    print("="*70)

    # Example of handling validation error
    tool = GoogleDocs(
        mode="create",
        title="Test",
        content="Content",
        share_with=["invalid-email"]  # This will cause validation error
    )
    result = tool.run()

    if result['success']:
        print("Document created successfully!")
    else:
        error = result['error']
        print(f"Error occurred: {error['code']}")
        print(f"Message: {error['message']}")
        print("Please fix the issue and try again.")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("  GoogleDocs Tool - Usage Examples")
    print("="*70)
    print("\nNote: Running in MOCK MODE for demonstration")
    print("Set real credentials to use with actual Google Docs API")

    example_1_simple_document()
    example_2_formatted_document()
    example_3_shared_document()
    example_4_organized_in_folder()
    example_5_append_content()
    example_6_replace_content()
    example_7_insert_content()
    example_8_meeting_minutes()
    example_9_error_handling()

    print("\n" + "="*70)
    print("  All Examples Completed!")
    print("="*70)
    print("\nTo use with real Google Docs:")
    print("1. Get service account credentials from Google Cloud Console")
    print("2. Set GOOGLE_DOCS_CREDENTIALS environment variable")
    print("3. Remove or set USE_MOCK_APIS=false")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
