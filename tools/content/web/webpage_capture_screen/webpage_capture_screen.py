"""
Capture screenshot of a webpage as visual representation
"""

from typing import Any, Dict
from pydantic import Field, HttpUrl
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class WebpageCaptureScreen(BaseTool):
    """
    Capture screenshot of a webpage as visual representation

    Args:
        input: Primary input parameter

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = WebpageCaptureScreen(input="https://example.com")
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "webpage_capture_screen"
    tool_category: str = "content"

    # Parameters
    input: HttpUrl = Field(..., description="Primary input parameter")

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the webpage_capture_screen tool.

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
        """Validate input parameters."""
        if not self.input:
            raise ValidationError(
                "Input URL cannot be empty",
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
            "result": {"mock": True, "screenshot": "mock_screenshot.png"},
            "metadata": {"mock_mode": True},
        }

    def _process(self) -> Any:
        """Main processing logic."""
        try:
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.get(self.input)
            screenshot_path = "/tmp/screenshot.png"
            driver.save_screenshot(screenshot_path)
            driver.quit()
            return {"screenshot_path": screenshot_path}
        except Exception as e:
            raise APIError(f"Failed to capture screenshot: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = WebpageCaptureScreen(input="https://example.com")
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
