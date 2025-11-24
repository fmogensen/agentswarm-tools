"""
Generate network graph for relationships between entities
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class GenerateNetworkGraph(BaseTool):
    """
    Generate network graph for relationships between entities.

    Args:
        prompt: Description of what to generate
        params: Additional generation parameters

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Tool-specific results
        - metadata: Additional information

    Example:
        >>> tool = GenerateNetworkGraph(prompt="example", params={})
        >>> result = tool.run()
    """

    tool_name: str = "generate_network_graph"
    tool_category: str = "visualization"

    prompt: str = Field(..., description="Description of what to generate")
    params: Dict[str, Any] = Field(
        default_factory=dict, description="Additional generation parameters"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the generate_network_graph tool.

        Returns:
            Dict with results

        Raises:
            ValidationError: If parameters are invalid
            APIError: If processing fails
        """

        self._logger.info(f"Executing {self.tool_name} with prompt={self.prompt}, params={self.params}")
        self._validate_parameters()

        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        try:
            result = self._process()

            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "prompt": self.prompt,
                    "params": self.params,
                },
            }

        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If prompt or params are invalid
        """
        if not self.prompt or not self.prompt.strip():
            raise ValidationError(
                "Prompt cannot be empty",
                tool_name=self.tool_name,
                details={"prompt": self.prompt},
            )

        if not isinstance(self.params, dict):
            raise ValidationError(
                "Params must be a dictionary",
                tool_name=self.tool_name,
                details={"params": self.params},
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        mock_nodes = [
            {"id": "A", "label": "Entity A"},
            {"id": "B", "label": "Entity B"},
            {"id": "C", "label": "Entity C"},
        ]

        mock_edges = [
            {"source": "A", "target": "B", "relationship": "connected_to"},
            {"source": "B", "target": "C", "relationship": "linked_to"},
        ]

        return {
            "success": True,
            "result": {"nodes": mock_nodes, "edges": mock_edges, "mock": True},
            "metadata": {"mock_mode": True, "tool_name": self.tool_name},
        }

    def _process(self) -> Any:
        """
        Main processing logic.

        This method parses the prompt and params to build
        a simple network graph representation.

        Returns:
            Dict with nodes and edges
        """
        try:
            entities: List[str] = self.params.get("entities", [])
            relationships: List[Dict[str, str]] = self.params.get("relationships", [])

            if not isinstance(entities, list) or not all(isinstance(e, str) for e in entities):
                raise ValidationError(
                    "params.entities must be a list of strings",
                    tool_name=self.tool_name,
                )

            if not isinstance(relationships, list):
                raise ValidationError(
                    "params.relationships must be a list", tool_name=self.tool_name
                )

            nodes = [{"id": e, "label": e} for e in entities]

            edges = []
            for rel in relationships:
                if not isinstance(rel, dict):
                    raise ValidationError(
                        "Each relationship must be a dictionary",
                        tool_name=self.tool_name,
                        details={"relationship": rel},
                    )

                source = rel.get("source")
                target = rel.get("target")
                rel_type = rel.get("type", "related_to")

                if source not in entities or target not in entities:
                    raise ValidationError(
                        "Relationship references unknown entities",
                        tool_name=self.tool_name,
                        details=rel,
                    )

                edges.append({"source": source, "target": target, "relationship": rel_type})

            return {"nodes": nodes, "edges": edges}

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Failed to construct network graph: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    tool = GenerateNetworkGraph(
        prompt="Team Collaboration Network",
        params={
            "entities": ["Alice", "Bob", "Charlie", "Diana"],
            "relationships": [
                {"source": "Alice", "target": "Bob", "type": "collaborates_with"},
                {"source": "Bob", "target": "Charlie", "type": "reports_to"},
                {"source": "Charlie", "target": "Diana", "type": "mentors"},
            ],
        },
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True, "Tool execution failed"
    print(f"Result: {result.get('result')}")
