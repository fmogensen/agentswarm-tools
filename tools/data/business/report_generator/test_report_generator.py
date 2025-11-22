"""Test cases for ReportGenerator tool."""

import os
import pytest
from .report_generator import ReportGenerator
from shared.errors import ValidationError


class TestReportGenerator:
    """Test suite for ReportGenerator tool."""

    def setup_method(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"

    def test_summary_report(self):
        """Test summary report generation."""
        tool = ReportGenerator(
            data={"revenue": 100000, "expenses": 60000},
            report_type="summary",
            title="Test Report"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["report_type"] == "summary"
        assert result["result"]["report_title"] == "Test Report"

    def test_detailed_report(self):
        """Test detailed report generation."""
        tool = ReportGenerator(
            data={"metric1": 100, "metric2": 200},
            report_type="detailed",
            title="Detailed Analysis"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["report_type"] == "detailed"

    def test_executive_report(self):
        """Test executive report generation."""
        tool = ReportGenerator(
            data={"kpi1": 95, "kpi2": 88},
            report_type="executive",
            title="Executive Summary"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["report_type"] == "executive"

    def test_analytics_report(self):
        """Test analytics report generation."""
        tool = ReportGenerator(
            data={"value1": 10, "value2": 20},
            report_type="analytics",
            title="Analytics Report"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["report_type"] == "analytics"

    def test_json_format(self):
        """Test JSON output format."""
        tool = ReportGenerator(
            data={"test": 123},
            report_type="summary",
            title="JSON Test",
            format="json"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "json"

    def test_markdown_format(self):
        """Test Markdown output format."""
        tool = ReportGenerator(
            data={"test": 123},
            report_type="summary",
            title="Markdown Test",
            format="markdown"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "markdown"
        assert "# Markdown Test" in result["result"]["content"]

    def test_html_format(self):
        """Test HTML output format."""
        tool = ReportGenerator(
            data={"test": 123},
            report_type="summary",
            title="HTML Test",
            format="html"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["format"] == "html"
        assert "<html>" in result["result"]["content"]

    def test_custom_sections(self):
        """Test custom sections."""
        tool = ReportGenerator(
            data={"value": 100},
            report_type="summary",
            title="Custom Sections",
            sections=["overview", "metrics"]
        )
        result = tool.run()

        assert result["success"] == True
        assert result["result"]["sections_included"] == ["overview", "metrics"]

    def test_invalid_report_type(self):
        """Test invalid report type."""
        with pytest.raises(ValidationError):
            tool = ReportGenerator(
                data={"test": 1},
                report_type="invalid",
                title="Test"
            )
            tool._validate_parameters()

    def test_invalid_format(self):
        """Test invalid format."""
        with pytest.raises(ValidationError):
            tool = ReportGenerator(
                data={"test": 1},
                report_type="summary",
                title="Test",
                format="invalid"
            )
            tool._validate_parameters()

    def test_empty_title(self):
        """Test empty title."""
        with pytest.raises(ValidationError):
            tool = ReportGenerator(
                data={"test": 1},
                report_type="summary",
                title=""
            )
            tool._validate_parameters()

    def test_mock_mode(self):
        """Test mock mode."""
        os.environ["USE_MOCK_APIS"] = "true"
        tool = ReportGenerator(
            data={"test": 1},
            report_type="summary",
            title="Mock Test"
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
