"""
Base renderer interface for chart and diagram generation.
Provides shared functionality and interface for all chart renderers.
"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import base64
import io


class BaseRenderer(ABC):
    """
    Abstract base class for all chart and diagram renderers.

    Provides common functionality for:
    - Matplotlib setup and teardown
    - Image encoding to base64
    - Parameter validation
    - Error handling
    """

    @abstractmethod
    def render(
        self,
        data: Any,
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Render the chart or diagram.

        Args:
            data: Chart data (format varies by renderer)
            title: Chart title
            width: Chart width in pixels
            height: Chart height in pixels
            options: Additional rendering options

        Returns:
            Dict with image_base64 and metadata
        """
        pass

    @abstractmethod
    def validate_data(self, data: Any) -> None:
        """
        Validate data format for this renderer.

        Args:
            data: Data to validate

        Raises:
            ValidationError: If data format is invalid
        """
        pass

    def create_figure(self, width: int = 800, height: int = 600) -> tuple:
        """
        Create a matplotlib figure with specified dimensions.

        Args:
            width: Figure width in pixels
            height: Figure height in pixels

        Returns:
            Tuple of (figure, axes)
        """
        # Convert pixels to inches (assuming 100 dpi)
        fig_width = width / 100
        fig_height = height / 100

        return plt.subplots(figsize=(fig_width, fig_height))

    def encode_figure(self, fig) -> str:
        """
        Encode matplotlib figure to base64 PNG.

        Args:
            fig: Matplotlib figure

        Returns:
            Base64 encoded PNG image
        """
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        encoded = base64.b64encode(buffer.read()).decode("utf-8")
        return encoded

    def cleanup_figure(self, fig) -> None:
        """
        Clean up matplotlib figure to free memory.

        Args:
            fig: Matplotlib figure to close
        """
        if fig is not None:
            plt.close(fig)

    def safe_render(
        self,
        render_func,
        data: Any,
        title: str = "",
        width: int = 800,
        height: int = 600,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Safely execute rendering with proper cleanup.

        Args:
            render_func: Function to execute rendering
            data: Chart data
            title: Chart title
            width: Chart width
            height: Chart height
            options: Additional options

        Returns:
            Dict with image_base64 and metadata

        Raises:
            Exception: Any rendering errors
        """
        fig = None
        try:
            fig = render_func(data, title, width, height, options or {})
            encoded = self.encode_figure(fig)

            return {"image_base64": encoded, "width": width, "height": height, "title": title}
        finally:
            self.cleanup_figure(fig)
