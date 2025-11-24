"""
Generate business reports from structured data.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class ReportGenerator(BaseTool):
    """
    Generate business reports from structured data with various formats.

    Args:
        data: Data to include in the report (dict or list format)
        report_type: Type of report (summary, detailed, executive, analytics)
        title: Report title
        sections: Optional list of sections to include
        format: Output format (json, markdown, html)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Generated report content and metadata
        - metadata: Report info, generation time, and statistics

    Example:
        >>> tool = ReportGenerator(
        ...     data={"revenue": 100000, "expenses": 60000},
        ...     report_type="summary",
        ...     title="Q4 Financial Report"
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "report_generator"
    tool_category: str = "data"

    # Parameters
    data: Dict[str, Any] = Field(..., description="Data to include in the report")
    report_type: str = Field(
        ..., description="Type of report: summary, detailed, executive, analytics"
    )
    title: str = Field(..., description="Report title", min_length=1)
    sections: Optional[List[str]] = Field(
        None,
        description="Optional list of sections to include (e.g., ['overview', 'metrics', 'recommendations'])",
    )
    format: str = Field("json", description="Output format: json, markdown, html")

    def _execute(self) -> Dict[str, Any]:
        """Execute report generation."""

        self._logger.info(
            f"Executing {self.tool_name} with data={self.data}, report_type={self.report_type}, title={self.title}, sections={self.sections}, format={self.format}"
        )
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "report_type": self.report_type,
                    "format": self.format,
                    "generated_at": datetime.utcnow().isoformat(),
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Report generation failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_types = ["summary", "detailed", "executive", "analytics"]
        valid_formats = ["json", "markdown", "html"]

        if self.report_type not in valid_types:
            raise ValidationError(
                f"report_type must be one of {valid_types}",
                tool_name=self.tool_name,
                field="report_type",
            )

        if self.format not in valid_formats:
            raise ValidationError(
                f"format must be one of {valid_formats}", tool_name=self.tool_name, field="format"
            )

        if not self.title.strip():
            raise ValidationError("title cannot be empty", tool_name=self.tool_name, field="title")

        if not isinstance(self.data, dict):
            raise ValidationError(
                "data must be a dictionary", tool_name=self.tool_name, field="data"
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        mock_content = self._format_report_content(
            {
                "overview": "This is a mock report overview.",
                "metrics": {"total": 100, "average": 50},
                "summary": "Mock summary of key findings.",
            }
        )

        return {
            "success": True,
            "result": {
                "report_title": self.title,
                "report_type": self.report_type,
                "content": mock_content,
                "format": self.format,
                "sections_included": self.sections or ["overview", "metrics", "summary"],
                "data_points": len(self.data),
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Generate the report."""
        # Determine sections to include
        if self.sections:
            sections_to_include = self.sections
        else:
            # Default sections based on report type
            sections_map = {
                "summary": ["overview", "key_metrics", "summary"],
                "detailed": [
                    "overview",
                    "detailed_analysis",
                    "metrics",
                    "trends",
                    "recommendations",
                ],
                "executive": ["executive_summary", "key_findings", "action_items"],
                "analytics": [
                    "data_overview",
                    "statistical_analysis",
                    "insights",
                    "visualizations",
                ],
            }
            sections_to_include = sections_map.get(self.report_type, ["overview", "data"])

        # Build report content
        report_content = self._build_report_content(sections_to_include)

        # Format the content
        formatted_content = self._format_report_content(report_content)

        return {
            "report_title": self.title,
            "report_type": self.report_type,
            "content": formatted_content,
            "format": self.format,
            "sections_included": sections_to_include,
            "data_points": len(self.data),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _build_report_content(self, sections: List[str]) -> Dict[str, Any]:
        """Build report content based on sections."""
        content = {}

        for section in sections:
            if section in ["overview", "executive_summary", "data_overview"]:
                content[section] = f"Report overview for: {self.title}"
                content[section] += f"\nReport Type: {self.report_type}"
                content[section] += f"\nData Points: {len(self.data)}"

            elif section in ["key_metrics", "metrics", "statistical_analysis"]:
                content[section] = self._extract_metrics()

            elif section in ["summary", "key_findings"]:
                content[section] = self._generate_summary()

            elif section in ["detailed_analysis", "insights"]:
                content[section] = self._generate_detailed_analysis()

            elif section in ["recommendations", "action_items"]:
                content[section] = self._generate_recommendations()

            elif section in ["trends", "visualizations"]:
                content[section] = "Trend analysis and visualizations would appear here"

        return content

    def _extract_metrics(self) -> Dict[str, Any]:
        """Extract metrics from data."""
        metrics = {}

        # Extract numeric values
        for key, value in self.data.items():
            if isinstance(value, (int, float)):
                metrics[key] = value

        # Add count
        metrics["total_fields"] = len(self.data)

        return metrics

    def _generate_summary(self) -> str:
        """Generate summary text."""
        summary_parts = [
            f"Summary for {self.title}:",
            f"- Total data fields: {len(self.data)}",
        ]

        # Add key insights
        numeric_fields = [k for k, v in self.data.items() if isinstance(v, (int, float))]
        if numeric_fields:
            summary_parts.append(f"- Numeric fields analyzed: {len(numeric_fields)}")

        return "\n".join(summary_parts)

    def _generate_detailed_analysis(self) -> str:
        """Generate detailed analysis."""
        analysis = []
        analysis.append(f"Detailed analysis of {self.title}:")

        for key, value in self.data.items():
            analysis.append(f"- {key}: {value} ({type(value).__name__})")

        return "\n".join(analysis)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations."""
        return [
            "Review all data points for accuracy",
            "Consider additional data sources",
            "Monitor trends over time",
            "Update report periodically",
        ]

    def _format_report_content(self, content: Dict[str, Any]) -> str:
        """Format report content based on output format."""
        if self.format == "json":
            return json.dumps(content, indent=2)

        elif self.format == "markdown":
            md_lines = [f"# {self.title}\n"]
            for section, data in content.items():
                md_lines.append(f"## {section.replace('_', ' ').title()}\n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        md_lines.append(f"- **{key}**: {value}")
                elif isinstance(data, list):
                    for item in data:
                        md_lines.append(f"- {item}")
                else:
                    md_lines.append(str(data))
                md_lines.append("")
            return "\n".join(md_lines)

        elif self.format == "html":
            html_parts = [f"<html><body><h1>{self.title}</h1>"]
            for section, data in content.items():
                html_parts.append(f"<h2>{section.replace('_', ' ').title()}</h2>")
                if isinstance(data, dict):
                    html_parts.append("<ul>")
                    for key, value in data.items():
                        html_parts.append(f"<li><strong>{key}</strong>: {value}</li>")
                    html_parts.append("</ul>")
                elif isinstance(data, list):
                    html_parts.append("<ul>")
                    for item in data:
                        html_parts.append(f"<li>{item}</li>")
                    html_parts.append("</ul>")
                else:
                    html_parts.append(f"<p>{data}</p>")
            html_parts.append("</body></html>")
            return "\n".join(html_parts)

        return json.dumps(content, indent=2)


if __name__ == "__main__":
    print("Testing ReportGenerator...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = ReportGenerator(
        data={"revenue": 100000, "expenses": 60000, "profit": 40000},
        report_type="summary",
        title="Q4 Financial Report",
        format="markdown",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("ReportGenerator test passed!")
