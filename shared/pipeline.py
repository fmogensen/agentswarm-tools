"""
Pipeline Builder for AgentSwarm Tools Framework.

Provides fluent API for building tool pipelines with:
- Method chaining
- Data transformation between steps
- Parallel execution support
- Error handling
- Pipeline composition

Example:
    ```python
    from shared.pipeline import Pipeline

    # Fluent API
    result = (
        Pipeline("research-pipeline")
        .add_step("search", web_search, query="AI trends")
        .add_step("analyze", lambda data: process(data))
        .add_step("document", create_agent, agent_type="docs")
        .on_error(lambda e: logger.error(e))
        .execute()
    )

    # Or using decorator
    @pipeline_builder
    def research_workflow(topic: str):
        results = web_search(query=topic)
        analysis = crawler(urls=results['urls'])
        document = create_agent(content=analysis)
        return document
    ```
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from datetime import datetime
import time
import inspect

from .registry import tool_registry
from .base import BaseTool
from .errors import ToolError, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


class PipelineStep:
    """Represents a single step in a pipeline."""

    def __init__(
        self,
        name: str,
        func: Union[Callable, type, str],
        params: Optional[Dict[str, Any]] = None,
        transform: Optional[Callable] = None,
    ):
        """
        Initialize pipeline step.

        Args:
            name: Step name
            func: Function, tool class, or tool name to execute
            params: Parameters to pass to function/tool
            transform: Optional transformation function for output
        """
        self.name = name
        self.func = func
        self.params = params or {}
        self.transform = transform
        self.result: Optional[Any] = None
        self.success: bool = False
        self.error: Optional[str] = None
        self.duration_ms: Optional[float] = None

    def execute(self, previous_result: Any = None) -> Any:
        """
        Execute this step.

        Args:
            previous_result: Result from previous step (injected if function accepts it)

        Returns:
            Step result

        Raises:
            ToolError: If execution fails
        """
        start_time = time.time()

        try:
            # Merge previous result into params if needed
            exec_params = self.params.copy()

            # If function accepts 'data' parameter, pass previous result
            if callable(self.func) and previous_result is not None:
                sig = inspect.signature(self.func)
                if 'data' in sig.parameters:
                    exec_params['data'] = previous_result

            # Execute based on type
            if isinstance(self.func, str):
                # Tool name - get from registry
                result = self._execute_tool_by_name(self.func, exec_params)
            elif isinstance(self.func, type) and issubclass(self.func, BaseTool):
                # Tool class
                result = self._execute_tool_class(self.func, exec_params)
            elif callable(self.func):
                # Regular function
                result = self._execute_function(self.func, exec_params)
            else:
                raise ValidationError(f"Invalid step function type: {type(self.func)}")

            # Apply transformation if provided
            if self.transform:
                result = self.transform(result)

            # Store result
            self.result = result
            self.success = True
            self.duration_ms = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            self.error = str(e)
            self.success = False
            self.duration_ms = (time.time() - start_time) * 1000
            raise

    def _execute_tool_by_name(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute tool by name from registry."""
        tool_class = tool_registry.get_tool(tool_name)
        if not tool_class:
            raise ValidationError(f"Tool not found in registry: {tool_name}")
        return self._execute_tool_class(tool_class, params)

    def _execute_tool_class(self, tool_class: type, params: Dict[str, Any]) -> Any:
        """Execute tool class."""
        tool = tool_class(**params)
        return tool.run()

    def _execute_function(self, func: Callable, params: Dict[str, Any]) -> Any:
        """Execute regular function."""
        sig = inspect.signature(func)

        # Filter params to only include those accepted by function
        filtered_params = {
            k: v for k, v in params.items()
            if k in sig.parameters
        }

        return func(**filtered_params)


class Pipeline:
    """
    Fluent pipeline builder for tool composition.

    Features:
    - Method chaining for readable pipeline definition
    - Automatic data passing between steps
    - Error handling and recovery
    - Parallel execution support
    - Pipeline composition
    - Conditional execution

    Example:
        ```python
        pipeline = (
            Pipeline("data-processing")
            .add_step("fetch", web_search, query="data")
            .add_step("process", lambda data: clean_data(data))
            .add_step("visualize", generate_chart)
            .on_error(lambda e: handle_error(e))
            .execute()
        )
        ```
    """

    def __init__(self, name: str = "unnamed-pipeline"):
        """
        Initialize pipeline.

        Args:
            name: Pipeline name for logging/tracking
        """
        self.name = name
        self.steps: List[PipelineStep] = []
        self.error_handlers: List[Callable] = []
        self.continue_on_error = False
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def add_step(
        self,
        name: str,
        func: Union[Callable, type, str],
        transform: Optional[Callable] = None,
        **params
    ) -> 'Pipeline':
        """
        Add a step to the pipeline.

        Args:
            name: Step name
            func: Function, tool class, or tool name
            transform: Optional transformation function
            **params: Parameters to pass to function/tool

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.add_step("search", web_search, query="AI")
            pipeline.add_step("filter", lambda data: [x for x in data if x['score'] > 0.8])
            ```
        """
        step = PipelineStep(name, func, params, transform)
        self.steps.append(step)
        return self

    def add_tool(self, name: str, tool_name: str, **params) -> 'Pipeline':
        """
        Add a tool step by name.

        Args:
            name: Step name
            tool_name: Name of tool in registry
            **params: Tool parameters

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.add_tool("search", "web_search", query="AI trends")
            ```
        """
        return self.add_step(name, tool_name, **params)

    def add_function(
        self,
        name: str,
        func: Callable,
        **params
    ) -> 'Pipeline':
        """
        Add a function step.

        Args:
            name: Step name
            func: Function to execute
            **params: Function parameters

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.add_function("process", process_data, threshold=0.5)
            ```
        """
        return self.add_step(name, func, **params)

    def map(
        self,
        name: str,
        func: Callable,
        **params
    ) -> 'Pipeline':
        """
        Map a function over previous results (if list).

        Args:
            name: Step name
            func: Function to map
            **params: Additional parameters

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.map("extract_urls", lambda item: item['url'])
            ```
        """
        def mapper(data):
            if isinstance(data, list):
                return [func(item, **params) for item in data]
            else:
                return func(data, **params)

        return self.add_step(name, mapper)

    def filter(
        self,
        name: str,
        predicate: Callable,
    ) -> 'Pipeline':
        """
        Filter previous results (if list).

        Args:
            name: Step name
            predicate: Filter function (returns bool)

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.filter("high_score", lambda item: item['score'] > 0.8)
            ```
        """
        def filterer(data):
            if isinstance(data, list):
                return [item for item in data if predicate(item)]
            else:
                return data if predicate(data) else None

        return self.add_step(name, filterer)

    def reduce(
        self,
        name: str,
        func: Callable,
        initial: Any = None,
    ) -> 'Pipeline':
        """
        Reduce previous results (if list).

        Args:
            name: Step name
            func: Reduce function (acc, item) -> acc
            initial: Initial accumulator value

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.reduce("combine", lambda acc, item: acc + item, initial=[])
            ```
        """
        def reducer(data):
            if isinstance(data, list):
                from functools import reduce as py_reduce
                return py_reduce(func, data, initial)
            else:
                return data

        return self.add_step(name, reducer)

    def conditional(
        self,
        name: str,
        condition: Callable,
        then_step: Callable,
        else_step: Optional[Callable] = None,
    ) -> 'Pipeline':
        """
        Add conditional step.

        Args:
            name: Step name
            condition: Condition function (returns bool)
            then_step: Function to execute if condition is true
            else_step: Optional function to execute if condition is false

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.conditional(
                "check_results",
                lambda data: len(data) > 0,
                then_step=process_results,
                else_step=lambda: "No results"
            )
            ```
        """
        def conditional_func(data):
            if condition(data):
                return then_step(data)
            elif else_step:
                return else_step(data)
            else:
                return data

        return self.add_step(name, conditional_func)

    def on_error(self, handler: Callable) -> 'Pipeline':
        """
        Add error handler.

        Args:
            handler: Error handler function (receives exception)

        Returns:
            Self for chaining

        Example:
            ```python
            pipeline.on_error(lambda e: logger.error(f"Pipeline failed: {e}"))
            ```
        """
        self.error_handlers.append(handler)
        return self

    def continue_on_error_mode(self, enabled: bool = True) -> 'Pipeline':
        """
        Enable/disable continue on error mode.

        Args:
            enabled: Whether to continue on error

        Returns:
            Self for chaining
        """
        self.continue_on_error = enabled
        return self

    def execute(self, initial_data: Any = None) -> Dict[str, Any]:
        """
        Execute the pipeline.

        Args:
            initial_data: Optional initial data to pass to first step

        Returns:
            Pipeline execution result with:
            - success: Overall success
            - result: Final result
            - steps: List of step results
            - duration_ms: Total execution time

        Raises:
            ToolError: If pipeline fails and continue_on_error is False
        """
        self.start_time = time.time()
        logger.info(f"Executing pipeline: {self.name} ({len(self.steps)} steps)")

        current_data = initial_data
        step_results = []

        try:
            for i, step in enumerate(self.steps):
                logger.info(f"Step {i+1}/{len(self.steps)}: {step.name}")

                try:
                    # Execute step
                    current_data = step.execute(current_data)

                    # Track result
                    step_results.append({
                        "name": step.name,
                        "success": True,
                        "duration_ms": step.duration_ms,
                    })

                except Exception as e:
                    logger.error(f"Step {step.name} failed: {e}")

                    # Track error
                    step_results.append({
                        "name": step.name,
                        "success": False,
                        "error": str(e),
                        "duration_ms": step.duration_ms,
                    })

                    # Call error handlers
                    for handler in self.error_handlers:
                        try:
                            handler(e)
                        except Exception as handler_error:
                            logger.error(f"Error handler failed: {handler_error}")

                    # Stop or continue?
                    if not self.continue_on_error:
                        raise

            # Success
            self.end_time = time.time()
            return self._build_result(
                success=True,
                result=current_data,
                step_results=step_results
            )

        except Exception as e:
            self.end_time = time.time()
            return self._build_result(
                success=False,
                error=str(e),
                step_results=step_results
            )

    def _build_result(
        self,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        step_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build pipeline execution result."""
        duration_ms = (self.end_time - self.start_time) * 1000 if self.end_time else 0

        return {
            "success": success,
            "pipeline_name": self.name,
            "result": result,
            "error": error,
            "steps": step_results or [],
            "total_steps": len(self.steps),
            "steps_completed": sum(1 for s in step_results or [] if s.get('success')),
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def __call__(self, initial_data: Any = None) -> Dict[str, Any]:
        """Allow pipeline to be called as a function."""
        return self.execute(initial_data)


def pipeline_builder(func: Callable) -> Callable:
    """
    Decorator to convert a function into a pipeline.

    The decorated function should call tools/functions sequentially,
    and the decorator will automatically handle errors and tracking.

    Example:
        ```python
        @pipeline_builder
        def research_pipeline(topic: str):
            # Search for content
            results = web_search(query=topic)

            # Analyze results
            analysis = crawler(urls=results['urls'])

            # Create document
            document = create_agent(
                agent_type="docs",
                content=analysis
            )

            return document

        result = research_pipeline("AI trends")
        ```
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        pipeline_name = func.__name__
        start_time = time.time()

        logger.info(f"Executing pipeline function: {pipeline_name}")

        try:
            result = func(*args, **kwargs)

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"Pipeline {pipeline_name} completed in {duration_ms:.2f}ms")

            return {
                "success": True,
                "pipeline_name": pipeline_name,
                "result": result,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Pipeline {pipeline_name} failed after {duration_ms:.2f}ms: {e}")

            return {
                "success": False,
                "pipeline_name": pipeline_name,
                "error": str(e),
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }

    return wrapper


class ParallelPipeline:
    """
    Execute multiple pipelines in parallel (simulated).

    Note: Currently simulates parallel execution by running sequentially.
    True parallel execution would require threading/async.
    """

    def __init__(self, name: str = "parallel-pipeline"):
        """Initialize parallel pipeline."""
        self.name = name
        self.pipelines: List[Pipeline] = []

    def add_pipeline(self, pipeline: Pipeline) -> 'ParallelPipeline':
        """Add a pipeline to execute in parallel."""
        self.pipelines.append(pipeline)
        return self

    def execute(self, initial_data: Any = None) -> Dict[str, Any]:
        """
        Execute all pipelines in parallel.

        Args:
            initial_data: Data to pass to all pipelines

        Returns:
            Combined results from all pipelines
        """
        start_time = time.time()
        results = []

        for pipeline in self.pipelines:
            try:
                result = pipeline.execute(initial_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Parallel pipeline {pipeline.name} failed: {e}")
                results.append({
                    "success": False,
                    "pipeline_name": pipeline.name,
                    "error": str(e)
                })

        duration_ms = (time.time() - start_time) * 1000

        return {
            "success": all(r.get('success', False) for r in results),
            "parallel_pipeline_name": self.name,
            "results": results,
            "total_pipelines": len(self.pipelines),
            "successful_pipelines": sum(1 for r in results if r.get('success')),
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    # Test the pipeline builder
    print("Testing Pipeline...")

    # Mock tool for testing
    def mock_search(query: str) -> Dict[str, Any]:
        return {
            "success": True,
            "results": [
                {"url": "https://example.com/1", "score": 0.9},
                {"url": "https://example.com/2", "score": 0.7},
                {"url": "https://example.com/3", "score": 0.5},
            ]
        }

    def mock_process(data: Dict[str, Any]) -> List[str]:
        return [item['url'] for item in data.get('results', [])]

    # Test basic pipeline
    pipeline = (
        Pipeline("test-pipeline")
        .add_step("search", mock_search, query="test")
        .add_step("process", mock_process)
    )

    result = pipeline.execute()
    assert result['success'], "Pipeline should succeed"
    assert len(result['result']) == 3, "Should have 3 URLs"
    print(f"Basic pipeline: {result}")

    # Test map/filter/reduce
    pipeline2 = (
        Pipeline("transform-pipeline")
        .add_step("search", mock_search, query="test")
        .add_function("extract", lambda data: data['results'])
        .filter("high_score", lambda item: item['score'] > 0.6)
        .map("get_urls", lambda item: item['url'])
    )

    result2 = pipeline2.execute()
    assert result2['success'], "Transform pipeline should succeed"
    assert len(result2['result']) == 2, "Should have 2 high-score URLs"
    print(f"Transform pipeline: {result2}")

    # Test error handling
    def failing_step(data):
        raise ValueError("Intentional error")

    pipeline3 = (
        Pipeline("error-pipeline")
        .add_step("search", mock_search, query="test")
        .add_step("fail", failing_step)
        .on_error(lambda e: print(f"Handled error: {e}"))
        .continue_on_error_mode(True)
    )

    result3 = pipeline3.execute()
    assert not result3['success'], "Error pipeline should fail"
    print(f"Error pipeline: {result3}")

    # Test decorator
    @pipeline_builder
    def my_workflow(query: str):
        results = mock_search(query)
        urls = mock_process(results)
        return urls

    result4 = my_workflow("test query")
    assert result4['success'], "Decorator pipeline should succeed"
    print(f"Decorator pipeline: {result4}")

    print("\nAll Pipeline tests passed!")
