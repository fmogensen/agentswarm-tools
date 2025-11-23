"""
Comprehensive tests for Pipeline Builder.

Tests:
- Pipeline construction
- Step execution
- Data transformation
- Error handling
- Pipeline decorator
- Parallel pipelines
"""

from unittest.mock import Mock

import pytest
from pydantic import Field

from shared.base import BaseTool
from shared.errors import ToolError, ValidationError
from shared.pipeline import ParallelPipeline, Pipeline, PipelineStep, pipeline_builder


# Mock functions for testing
def mock_search(query: str, max_results: int = 10):
    """Mock search function."""
    return {
        "success": True,
        "results": [
            {"url": f"https://example.com/{i}", "score": 0.9 - i * 0.1} for i in range(max_results)
        ],
    }


def mock_process(data):
    """Mock processing function."""
    if isinstance(data, dict) and "results" in data:
        return [item["url"] for item in data["results"]]
    return data


def failing_function(data):
    """Function that always fails."""
    raise ValueError("Intentional failure")


# Mock tools for testing
class MockSearchTool(BaseTool):
    """Mock search tool."""

    tool_name = "mock_search"
    tool_category = "test"

    query: str = Field(..., description="Search query")
    max_results: int = Field(10, description="Max results")

    def _execute(self):
        return mock_search(self.query, self.max_results)


class TestPipelineStep:
    """Test PipelineStep functionality."""

    def test_execute_function(self):
        """Test executing a regular function."""
        step = PipelineStep("test", mock_search, {"query": "AI", "max_results": 5})
        result = step.execute()

        assert step.success == True
        assert result["success"] == True
        assert len(result["results"]) == 5

    def test_execute_with_previous_result(self):
        """Test passing previous result to function."""

        def process_data(data, threshold=0.5):
            return [item for item in data if item["score"] > threshold]

        # First step
        step1 = PipelineStep("search", mock_search, {"query": "AI"})
        search_result = step1.execute()

        # Second step with data from first
        step2 = PipelineStep("filter", process_data, {"threshold": 0.7})
        filtered = step2.execute(search_result["results"])

        assert len(filtered) < len(search_result["results"])

    def test_execute_with_transform(self):
        """Test step with transformation function."""
        transform = lambda result: result["results"][:5]
        step = PipelineStep("search", mock_search, {"query": "AI"}, transform=transform)
        result = step.execute()

        assert len(result) == 5

    def test_execute_tool_class(self):
        """Test executing tool class."""
        step = PipelineStep("search", MockSearchTool, {"query": "AI", "max_results": 3})
        result = step.execute()

        assert result["success"] == True
        assert len(result["results"]) == 3

    def test_error_handling(self):
        """Test step error handling."""
        step = PipelineStep("fail", failing_function, {})

        with pytest.raises(ValueError):
            step.execute()

        assert step.success == False
        assert step.error is not None


class TestPipeline:
    """Test Pipeline functionality."""

    def test_create_pipeline(self):
        """Test creating a pipeline."""
        pipeline = Pipeline("test-pipeline")
        assert pipeline.name == "test-pipeline"
        assert len(pipeline.steps) == 0

    def test_add_step(self):
        """Test adding steps to pipeline."""
        pipeline = Pipeline("test")
        pipeline.add_step("search", mock_search, query="AI")
        pipeline.add_step("process", mock_process)

        assert len(pipeline.steps) == 2
        assert pipeline.steps[0].name == "search"
        assert pipeline.steps[1].name == "process"

    def test_add_function(self):
        """Test add_function method."""
        pipeline = Pipeline("test")
        pipeline.add_function("search", mock_search, query="AI", max_results=5)

        assert len(pipeline.steps) == 1

    def test_add_tool(self):
        """Test add_tool method."""
        from shared.registry import tool_registry

        tool_registry.register(MockSearchTool)

        pipeline = Pipeline("test")
        pipeline.add_tool("search", "mock_search", query="AI")

        assert len(pipeline.steps) == 1

        tool_registry.unregister("mock_search")

    def test_execute_simple_pipeline(self):
        """Test executing a simple pipeline."""
        pipeline = (
            Pipeline("test")
            .add_step("search", mock_search, query="AI", max_results=5)
            .add_step("process", mock_process)
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert len(result["result"]) == 5
        assert result["total_steps"] == 2
        assert result["steps_completed"] == 2

    def test_data_flow_between_steps(self):
        """Test data flowing between steps."""

        def extract_urls(data):
            if isinstance(data, dict) and "results" in data:
                return [item["url"] for item in data["results"]]
            return data

        def count_items(data):
            return len(data)

        pipeline = (
            Pipeline("data-flow")
            .add_step("search", mock_search, query="AI")
            .add_step("extract", extract_urls)
            .add_step("count", count_items)
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert isinstance(result["result"], int)
        assert result["result"] == 10  # Default max_results

    def test_map_operation(self):
        """Test map transformation."""
        pipeline = (
            Pipeline("map-test")
            .add_step("search", mock_search, query="AI", max_results=3)
            .add_function("extract", lambda data: data["results"])
            .map("get_urls", lambda item: item["url"])
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert len(result["result"]) == 3
        assert all(isinstance(url, str) for url in result["result"])

    def test_filter_operation(self):
        """Test filter transformation."""
        pipeline = (
            Pipeline("filter-test")
            .add_step("search", mock_search, query="AI")
            .add_function("extract", lambda data: data["results"])
            .filter("high_score", lambda item: item["score"] > 0.7)
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert len(result["result"]) < 10  # Less than original

    def test_reduce_operation(self):
        """Test reduce transformation."""
        pipeline = (
            Pipeline("reduce-test")
            .add_step("search", mock_search, query="AI", max_results=5)
            .add_function("extract", lambda data: data["results"])
            .map("scores", lambda item: item["score"])
            .reduce("sum", lambda acc, score: acc + score, initial=0)
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert isinstance(result["result"], (int, float))
        assert result["result"] > 0

    def test_conditional_step(self):
        """Test conditional execution."""

        def check_results(data):
            return len(data.get("results", [])) > 0

        def process_results(data):
            return "Processed"

        def no_results(data):
            return "No results"

        pipeline = (
            Pipeline("conditional")
            .add_step("search", mock_search, query="AI", max_results=5)
            .conditional(
                "check", condition=check_results, then_step=process_results, else_step=no_results
            )
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert result["result"] == "Processed"

    def test_error_handling(self):
        """Test error handling in pipeline."""
        error_handled = []

        def error_handler(e):
            error_handled.append(str(e))

        pipeline = Pipeline("error-test").add_step("fail", failing_function).on_error(error_handler)

        result = pipeline.execute()

        assert result["success"] == False
        assert len(error_handled) == 1
        assert "Intentional failure" in error_handled[0]

    def test_continue_on_error(self):
        """Test continue on error mode."""
        pipeline = (
            Pipeline("resilient")
            .continue_on_error_mode(True)
            .add_step("fail", failing_function)
            .add_step("search", mock_search, query="AI")
        )

        result = pipeline.execute()

        # Overall fails but second step runs
        assert result["success"] == False
        assert result["total_steps"] == 2
        # First step failed, second succeeded
        assert result["steps"][0]["success"] == False
        assert result["steps"][1]["success"] == True

    def test_multiple_error_handlers(self):
        """Test multiple error handlers."""
        errors = []

        pipeline = (
            Pipeline("multi-error")
            .on_error(lambda e: errors.append("handler1"))
            .on_error(lambda e: errors.append("handler2"))
            .on_error(lambda e: errors.append("handler3"))
            .add_step("fail", failing_function)
        )

        result = pipeline.execute()

        assert len(errors) == 3

    def test_pipeline_as_callable(self):
        """Test using pipeline as callable."""
        pipeline = Pipeline("callable").add_step("search", mock_search, query="AI")

        result = pipeline()  # Call directly

        assert result["success"] == True

    def test_initial_data(self):
        """Test passing initial data to pipeline."""

        def use_initial(data):
            return data["value"] * 2

        pipeline = Pipeline("initial").add_step("process", use_initial)

        result = pipeline.execute(initial_data={"value": 5})

        assert result["success"] == True
        assert result["result"] == 10


class TestPipelineDecorator:
    """Test pipeline_builder decorator."""

    def test_simple_decorated_function(self):
        """Test decorating a simple function."""

        @pipeline_builder
        def my_workflow(query: str):
            results = mock_search(query, max_results=5)
            urls = mock_process(results)
            return urls

        result = my_workflow("AI")

        assert result["success"] == True
        assert result["pipeline_name"] == "my_workflow"
        assert len(result["result"]) == 5

    def test_decorated_function_with_error(self):
        """Test decorator error handling."""

        @pipeline_builder
        def failing_workflow():
            raise ValueError("Workflow error")

        result = failing_workflow()

        assert result["success"] == False
        assert "Workflow error" in result["error"]

    def test_decorated_function_metadata(self):
        """Test decorator preserves function metadata."""

        @pipeline_builder
        def documented_workflow(x: int):
            """This is documentation."""
            return x * 2

        assert documented_workflow.__name__ == "documented_workflow"
        assert documented_workflow.__doc__ == "This is documentation."


class TestParallelPipeline:
    """Test ParallelPipeline functionality."""

    def test_create_parallel_pipeline(self):
        """Test creating parallel pipeline."""
        parallel = ParallelPipeline("test")
        assert parallel.name == "test"
        assert len(parallel.pipelines) == 0

    def test_add_pipelines(self):
        """Test adding pipelines to parallel execution."""
        pipeline1 = Pipeline("p1").add_step("search1", mock_search, query="AI")
        pipeline2 = Pipeline("p2").add_step("search2", mock_search, query="ML")

        parallel = ParallelPipeline("multi").add_pipeline(pipeline1).add_pipeline(pipeline2)

        assert len(parallel.pipelines) == 2

    def test_execute_parallel(self):
        """Test executing parallel pipelines."""
        pipeline1 = Pipeline("web").add_step("search", mock_search, query="AI", max_results=5)

        pipeline2 = Pipeline("scholar").add_step("search", mock_search, query="ML", max_results=3)

        parallel = ParallelPipeline("multi-search").add_pipeline(pipeline1).add_pipeline(pipeline2)

        result = parallel.execute()

        assert result["success"] == True
        assert result["total_pipelines"] == 2
        assert result["successful_pipelines"] == 2
        assert len(result["results"]) == 2

    def test_parallel_with_failure(self):
        """Test parallel execution with one failing pipeline."""
        pipeline1 = Pipeline("success").add_step("search", mock_search, query="AI")
        pipeline2 = Pipeline("fail").add_step("fail", failing_function)

        parallel = ParallelPipeline("mixed").add_pipeline(pipeline1).add_pipeline(pipeline2)

        result = parallel.execute()

        assert result["success"] == False  # Overall fails
        assert result["successful_pipelines"] == 1  # One succeeded


class TestComplexPipelines:
    """Test complex pipeline scenarios."""

    def test_chained_transformations(self):
        """Test multiple chained transformations."""
        pipeline = (
            Pipeline("complex")
            .add_step("search", mock_search, query="AI", max_results=10)
            .add_function("extract", lambda data: data["results"])
            .filter("high_score", lambda item: item["score"] > 0.6)
            .map("urls", lambda item: item["url"])
            .reduce("join", lambda acc, url: acc + "\n" + url if acc else url, initial="")
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert isinstance(result["result"], str)
        assert "example.com" in result["result"]

    def test_nested_pipeline_pattern(self):
        """Test nested pipeline-like pattern."""

        @pipeline_builder
        def inner_workflow(query: str):
            results = mock_search(query, max_results=3)
            return results

        @pipeline_builder
        def outer_workflow(topic: str):
            data = inner_workflow(topic)
            urls = mock_process(data["result"])
            return urls

        result = outer_workflow("AI")

        assert result["success"] == True

    def test_data_aggregation_pipeline(self):
        """Test data aggregation pattern."""
        topics = ["AI", "ML", "DL"]

        pipeline = (
            Pipeline("aggregate")
            .add_function("set_topics", lambda: topics)
            .map("search_each", lambda topic: mock_search(topic, max_results=2))
            .add_function(
                "flatten",
                lambda results: [item for sublist in results for item in sublist["results"]],
            )
            .filter("unique", lambda item: True)  # Would filter duplicates in real impl
        )

        result = pipeline.execute()

        assert result["success"] == True
        assert len(result["result"]) == 6  # 3 topics × 2 results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
