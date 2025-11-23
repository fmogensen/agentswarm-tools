"""
Google Slides Tool - Create and modify Google Slides presentations using Google Slides API v1

DEPRECATED: This tool is now a backward compatibility wrapper around UnifiedGoogleWorkspace.
For new code, use UnifiedGoogleWorkspace with workspace_type="slides" instead.
This wrapper will be maintained for backward compatibility but may be removed in a future version.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
import os
import warnings

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError


class GoogleSlides(BaseTool):
    """
    Create and modify Google Slides presentations using Google Slides API v1.

    DEPRECATED: Use UnifiedGoogleWorkspace with workspace_type="slides" instead.

    This tool supports creating new presentations, modifying existing ones,
    adding slides with various layouts, inserting text and images, applying themes,
    and sharing presentations with specific users.

    Args:
        mode: Operation mode - "create" or "modify"
        slides: List of slide definitions with layout, title, content, and images
        title: Presentation title (required for create mode)
        presentation_id: Google Slides presentation ID (required for modify mode)
        theme: Theme name to apply (optional): "default", "simple", "modern", "colorful"
        share_with: List of email addresses to share the presentation with (optional)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Presentation data including presentation_id, url, and slide_count
        - metadata: Additional information including mock mode indicator

    Example:
        >>> # Create a new presentation
        >>> tool = GoogleSlides(
        ...     mode="create",
        ...     title="Q4 Sales Report",
        ...     slides=[
        ...         {
        ...             "layout": "title",
        ...             "title": "Q4 Sales Report",
        ...             "subtitle": "2024 Performance Overview"
        ...         },
        ...         {
        ...             "layout": "title_and_body",
        ...             "title": "Key Metrics",
        ...             "content": "Revenue increased by 25%"
        ...         }
        ...     ],
        ...     theme="modern",
        ...     share_with=["team@example.com"]
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "google_slides"
    tool_category: str = "communication"

    # Parameters
    mode: str = Field(
        ...,
        description="Operation mode: 'create' to create new presentation or 'modify' to update existing",
        pattern="^(create|modify)$",
    )

    slides: List[Dict[str, Any]] = Field(
        ...,
        description=(
            "List of slide definitions. Each slide should have:\n"
            "- layout: 'title', 'title_and_body', 'section_header', 'two_columns', 'blank'\n"
            "- title: Slide title (optional for blank layout)\n"
            "- subtitle: Subtitle text (for title layout)\n"
            "- content: Main body content (for title_and_body layout)\n"
            "- left_content: Left column content (for two_columns layout)\n"
            "- right_content: Right column content (for two_columns layout)\n"
            "- image_url: URL to image to insert (optional)\n"
            "- notes: Speaker notes (optional)"
        ),
        min_length=1,
    )

    title: Optional[str] = Field(
        None,
        description="Presentation title (required for create mode)",
        min_length=1,
        max_length=255,
    )

    presentation_id: Optional[str] = Field(
        None, description="Google Slides presentation ID (required for modify mode)", min_length=1
    )

    theme: Optional[str] = Field(
        "default",
        description="Theme to apply: 'default', 'simple', 'modern', 'colorful'",
        pattern="^(default|simple|modern|colorful)$",
    )

    share_with: Optional[List[str]] = Field(
        None, description="List of email addresses to share the presentation with (view access)"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the google_slides tool by delegating to UnifiedGoogleWorkspace.

        Returns:
            Dict with success status, presentation data, and metadata

        Raises:
            ValidationError: If input parameters are invalid
            APIError: If Google Slides API call fails
            AuthenticationError: If credentials are missing or invalid
        """
        # Emit deprecation warning
        warnings.warn(
            "GoogleSlides is deprecated and will be removed in v3.0.0. "
            "Use UnifiedGoogleWorkspace with workspace_type='slides' instead. "
            "See docs/guides/MIGRATION_GUIDE.md for migration instructions.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Import here to avoid circular dependency
        from tools.communication.unified_google_workspace import UnifiedGoogleWorkspace

        # Create unified tool with equivalent parameters
        unified_tool = UnifiedGoogleWorkspace(
            workspace_type="slides",
            mode=self.mode,
            title=self.title,
            presentation_id=self.presentation_id,
            slides=self.slides,
            theme=self.theme,
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


# Test block
if __name__ == "__main__":
    print("Testing GoogleSlides Tool (backward compatibility wrapper)...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create new presentation
    print("\nTest 1: Create new presentation")
    print("-" * 60)

    tool1 = GoogleSlides(
        mode="create",
        title="Q4 Sales Report 2024",
        slides=[
            {
                "layout": "title",
                "title": "Q4 Sales Report",
                "subtitle": "2024 Performance Overview",
            },
            {
                "layout": "title_and_body",
                "title": "Key Metrics",
                "content": "Revenue: $10M (+25%)\nCustomers: 5,000 (+40%)",
            },
        ],
        theme="modern",
        share_with=["team@example.com", "exec@example.com"],
    )

    result1 = tool1.run()
    print(f"Success: {result1.get('success')}")
    print(f"Presentation ID: {result1['result']['presentation_id']}")
    print(f"URL: {result1['result']['url']}")
    print(f"Slide Count: {result1['result']['slide_count']}")
    print(f"Deprecated: {result1['metadata']['deprecated']}")

    assert result1.get("success") == True
    assert result1["result"]["slide_count"] == 2
    assert result1["metadata"]["deprecated"] == True
    print("✓ Test 1 passed")

    # Test 2: Modify existing presentation
    print("\nTest 2: Modify existing presentation")
    print("-" * 60)

    tool2 = GoogleSlides(
        mode="modify",
        presentation_id="1abc123def456",
        slides=[
            {
                "layout": "title_and_body",
                "title": "Additional Insights",
                "content": "Market analysis shows positive trends",
            }
        ],
    )

    result2 = tool2.run()
    print(f"Success: {result2.get('success')}")
    print(f"Presentation ID: {result2['result']['presentation_id']}")
    print(f"Slides Added: {result2['result']['slides_added']}")

    assert result2.get("success") == True
    assert result2["result"]["slides_added"] == 1
    print("✓ Test 2 passed")

    # Test 3: Validation - missing title in create mode
    print("\nTest 3: Validation - missing title in create mode")
    print("-" * 60)

    try:
        tool3 = GoogleSlides(mode="create", slides=[{"layout": "blank"}])
        result3 = tool3.run()
        print("Error: Should have raised validation error")
        assert False
    except Exception as e:
        print(f"Expected validation error: {str(e)}")
        print("✓ Test 3 passed")

    # Test 4: Validation - missing presentation_id in modify mode
    print("\nTest 4: Validation - missing presentation_id in modify mode")
    print("-" * 60)

    try:
        tool4 = GoogleSlides(mode="modify", slides=[{"layout": "blank"}])
        result4 = tool4.run()
        print("Error: Should have raised validation error")
        assert False
    except Exception as e:
        print(f"Expected validation error: {str(e)}")
        print("✓ Test 4 passed")

    print("\n" + "=" * 60)
    print("All backward compatibility tests passed!")
    print("Note: This wrapper delegates to UnifiedGoogleWorkspace")
    print("=" * 60)
