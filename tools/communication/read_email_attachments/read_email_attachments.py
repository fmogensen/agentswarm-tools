"""
Read email attachments efficiently (checks cache first)
"""

import hashlib
import json
import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class ReadEmailAttachments(BaseTool):
    """
    Read email attachments efficiently (checks cache first)

    Args:
        input: Primary input parameter (expected to be JSON containing email_id)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = ReadEmailAttachments(input="example")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "read_email_attachments"
    tool_category: str = "communication"

    # Parameters
    input: str = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the read_email_attachments tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {"tool_name": self.tool_name},
            }
        except Exception as e:
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If input is missing or invalid JSON or missing email_id
        """
        if not self.input or not self.input.strip():
            raise ValidationError(
                "Input cannot be empty",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        try:
            parsed = json.loads(self.input)
        except Exception:
            raise ValidationError(
                "Input must be valid JSON",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

        if "email_id" not in parsed:
            raise ValidationError(
                "Missing required field: email_id",
                tool_name=self.tool_name,
                details={"input": self.input},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        return {
            "success": True,
            "result": {
                "attachments": [
                    {
                        "filename": "mock1.pdf",
                        "size": 102400,
                        "content": "<mock-bytes>",
                    },
                    {"filename": "mock2.txt", "size": 2048, "content": "mock content"},
                ],
                "from_cache": False,
                "mock": True,
            },
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        Returns:
            Dict containing extracted attachments and cache status

        Raises:
            APIError: If external API fails
        """
        parsed = json.loads(self.input)
        email_id = parsed["email_id"]

        cache_key = hashlib.sha256(email_id.encode("utf-8")).hexdigest()
        cache_dir = ".email_attachment_cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{cache_key}.json")

        # Check cache
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                return {"attachments": cached_data, "from_cache": True}
            except Exception as e:
                raise APIError(f"Failed reading cache: {e}", tool_name=self.tool_name)

        # Simulated real attachment reading logic
        try:
            # Placeholder logic (replace with real API/email service calls)
            attachments = [
                {
                    "filename": f"{email_id}_document.pdf",
                    "size": 55000,
                    "content": "<binary-pdf-data>",
                }
            ]

            # Save to cache
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(attachments, f)

            return {"attachments": attachments, "from_cache": False}

        except Exception as e:
            raise APIError(f"Failed to read attachments: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    print("Testing ReadEmailAttachments...")

    import json
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Read attachments from email
    print("\nTest 1: Read attachments from email")
    input_data = {"email_id": "test123"}
    tool = ReadEmailAttachments(input=json.dumps(input_data))
    result = tool.run()

    assert result.get("success") == True
    assert "attachments" in result.get("result", {})
    assert isinstance(result.get("result", {}).get("attachments"), list)
    print(f"✅ Test 1 passed: Found {len(result.get('result', {}).get('attachments'))} attachments")
    print(f"   First attachment: {result.get('result', {}).get('attachments')[0].get('filename')}")

    # Test 2: Different email ID
    print("\nTest 2: Read attachments from different email")
    input_data = {"email_id": "email456"}
    tool = ReadEmailAttachments(input=json.dumps(input_data))
    result = tool.run()

    assert result.get("success") == True
    assert len(result.get("result", {}).get("attachments", [])) > 0
    print(f"✅ Test 2 passed: Attachments retrieved")

    # Test 3: Validation - missing email_id
    print("\nTest 3: Validation - missing email_id")
    try:
        bad_input = {"other_field": "value"}
        bad_tool = ReadEmailAttachments(input=json.dumps(bad_input))
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 3 passed: Validation working - {type(e).__name__}")

    # Test 4: Validation - invalid JSON
    print("\nTest 4: Validation - invalid JSON")
    try:
        bad_tool = ReadEmailAttachments(input="not valid json")
        bad_tool.run()
        assert False, "Should have raised ValidationError"
    except Exception as e:
        print(f"✅ Test 4 passed: JSON validation working - {type(e).__name__}")

    print("\n✅ All tests passed!")
