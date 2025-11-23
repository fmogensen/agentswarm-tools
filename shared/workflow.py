"""
Workflow Engine for AgentSwarm Tools Framework.

Enables chaining and composition of multiple tools with:
- Multi-step workflow execution
- Data passing between steps
- Conditional execution (if/else)
- Loop support (foreach)
- Error handling and retries
- Variable interpolation

Example:
    ```python
    from shared.workflow import WorkflowEngine

    workflow = {
        "name": "research-pipeline",
        "variables": {"topic": "AI trends"},
        "steps": [
            {
                "id": "search",
                "tool": "web_search",
                "params": {"query": "${vars.topic}"}
            },
            {
                "id": "analyze",
                "tool": "crawler",
                "params": {"urls": "${steps.search.result.urls}"},
                "condition": "${steps.search.success}"
            }
        ]
    }

    engine = WorkflowEngine(workflow)
    result = engine.execute()
    ```
"""

import re
import time
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
import json
import os
from pathlib import Path

from .registry import tool_registry
from .errors import ToolError, ValidationError, TimeoutError

# Configure logging
logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of workflow step execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowContext:
    """
    Context for workflow execution.

    Stores variables, step results, and execution state.
    """

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        self.variables = variables or {}
        self.steps: Dict[str, Dict[str, Any]] = {}
        self.env = dict(os.environ)
        self.start_time = datetime.utcnow()

    def set_step_result(self, step_id: str, result: Any, success: bool = True) -> None:
        """Store step execution result."""
        self.steps[step_id] = {
            "result": result,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_step_result(self, step_id: str) -> Optional[Dict[str, Any]]:
        """Get result from previous step."""
        return self.steps.get(step_id)

    def interpolate(self, value: Any) -> Any:
        """
        Interpolate variables in value.

        Supports:
        - ${vars.name} - Variables
        - ${steps.step_id.result} - Step results
        - ${env.VAR_NAME} - Environment variables

        Args:
            value: Value to interpolate (str, dict, list, or primitive)

        Returns:
            Interpolated value
        """
        if isinstance(value, str):
            return self._interpolate_string(value)
        elif isinstance(value, dict):
            return {k: self.interpolate(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.interpolate(item) for item in value]
        else:
            return value

    def _interpolate_string(self, text: str) -> Any:
        """Interpolate string with variable references."""
        # Find all ${...} patterns
        pattern = r'\$\{([^}]+)\}'
        matches = re.finditer(pattern, text)

        # If no matches, return as-is
        if not matches:
            return text

        # If entire string is a single variable reference, return the actual value
        full_match = re.fullmatch(pattern, text)
        if full_match:
            ref = full_match.group(1)
            return self._resolve_reference(ref)

        # Otherwise, replace all references in string
        result = text
        for match in re.finditer(pattern, text):
            ref = match.group(1)
            value = self._resolve_reference(ref)
            result = result.replace(match.group(0), str(value))

        return result

    def _resolve_reference(self, ref: str) -> Any:
        """
        Resolve a variable reference.

        Examples:
        - vars.topic -> self.variables['topic']
        - steps.search.result -> self.steps['search']['result']
        - steps.search.success -> self.steps['search']['success']
        - env.API_KEY -> os.environ['API_KEY']
        """
        parts = ref.split('.')

        if parts[0] == 'vars':
            obj = self.variables
            parts = parts[1:]
        elif parts[0] == 'steps':
            if len(parts) < 2:
                raise ValidationError(f"Invalid step reference: {ref}")
            step_id = parts[1]
            if step_id not in self.steps:
                raise ValidationError(f"Step '{step_id}' not found in context")
            obj = self.steps[step_id]
            parts = parts[2:]
        elif parts[0] == 'env':
            obj = self.env
            parts = parts[1:]
        else:
            raise ValidationError(f"Invalid reference type: {parts[0]}")

        # Navigate through nested structure
        for part in parts:
            if isinstance(obj, dict):
                if part not in obj:
                    raise ValidationError(f"Key '{part}' not found in {ref}")
                obj = obj[part]
            elif isinstance(obj, list):
                # Handle array indexing like [0] or [*]
                if part == '*':
                    # Return entire array for operations like ${steps.search.result[*].url}
                    return obj
                try:
                    index = int(part)
                    obj = obj[index]
                except (ValueError, IndexError):
                    raise ValidationError(f"Invalid array index: {part}")
            else:
                raise ValidationError(f"Cannot navigate {ref}: {part} is not a dict or list")

        return obj

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a boolean condition.

        Supports:
        - ${steps.search.success} - Boolean value
        - ${steps.search.result.length} > 5 - Comparisons
        - ${vars.count} == 10

        Args:
            condition: Condition string to evaluate

        Returns:
            Boolean result
        """
        # Interpolate variables first
        interpolated = self.interpolate(condition)

        # If it's already a boolean, return it
        if isinstance(interpolated, bool):
            return interpolated

        # If it's a string, try to evaluate as expression
        if isinstance(interpolated, str):
            # Simple comparison operators
            for op in ['>=', '<=', '==', '!=', '>', '<']:
                if op in interpolated:
                    left, right = interpolated.split(op, 1)
                    left_val = self._parse_value(left.strip())
                    right_val = self._parse_value(right.strip())

                    if op == '>':
                        return left_val > right_val
                    elif op == '<':
                        return left_val < right_val
                    elif op == '>=':
                        return left_val >= right_val
                    elif op == '<=':
                        return left_val <= right_val
                    elif op == '==':
                        return left_val == right_val
                    elif op == '!=':
                        return left_val != right_val

            # Try to parse as boolean
            lower = interpolated.lower()
            if lower in ('true', 'yes', '1'):
                return True
            elif lower in ('false', 'no', '0', ''):
                return False

        # Default to truthy evaluation
        return bool(interpolated)

    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type."""
        value = value.strip()

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value


class WorkflowEngine:
    """
    Execute multi-step workflows with tool composition.

    Features:
    - Sequential and parallel execution
    - Conditional steps (if/else)
    - Loops (foreach)
    - Error handling and retries
    - Variable interpolation
    - Step dependencies

    Example:
        ```python
        workflow = {
            "name": "research-to-document",
            "variables": {"topic": "AI trends 2024"},
            "steps": [
                {
                    "id": "search",
                    "tool": "web_search",
                    "params": {"query": "${vars.topic}"}
                },
                {
                    "id": "analyze",
                    "tool": "crawler",
                    "params": {"urls": "${steps.search.result.urls}"},
                    "condition": "${steps.search.success}"
                }
            ]
        }

        engine = WorkflowEngine(workflow)
        result = engine.execute()
        ```
    """

    def __init__(self, workflow: Dict[str, Any], context: Optional[WorkflowContext] = None):
        """
        Initialize workflow engine.

        Args:
            workflow: Workflow definition
            context: Optional execution context (for resuming)
        """
        self.workflow = workflow
        self.context = context or WorkflowContext(workflow.get('variables', {}))
        self.name = workflow.get('name', 'unnamed-workflow')
        self.description = workflow.get('description', '')
        self.steps = workflow.get('steps', [])
        self.error_handling = workflow.get('error_handling', {})

        # Execution settings
        self.max_retries = self.error_handling.get('max_retries', 3)
        self.retry_on_failure = self.error_handling.get('retry_on_failure', True)
        self.continue_on_error = self.error_handling.get('continue_on_error', False)
        self.timeout = workflow.get('timeout', 3600)  # 1 hour default

        # State
        self.step_status: Dict[str, StepStatus] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def execute(self) -> Dict[str, Any]:
        """
        Execute the workflow.

        Returns:
            Workflow execution result with:
            - success: Overall success status
            - results: Dict of step results
            - duration_ms: Execution time
            - steps_executed: Number of steps run
            - steps_failed: Number of failed steps

        Raises:
            TimeoutError: If workflow exceeds timeout
            ToolError: If workflow fails and continue_on_error is False
        """
        self.start_time = time.time()
        logger.info(f"Starting workflow: {self.name}")

        try:
            # Execute steps
            for step in self.steps:
                # Check timeout
                if time.time() - self.start_time > self.timeout:
                    raise TimeoutError(
                        f"Workflow exceeded timeout of {self.timeout}s",
                        timeout=self.timeout
                    )

                # Execute step
                self._execute_step(step)

            # Calculate final results
            self.end_time = time.time()
            return self._build_result(success=True)

        except Exception as e:
            self.end_time = time.time()
            logger.error(f"Workflow failed: {e}")

            if not self.continue_on_error:
                raise

            return self._build_result(success=False, error=str(e))

    def _execute_step(self, step: Dict[str, Any]) -> None:
        """Execute a single workflow step."""
        step_id = step.get('id', f"step_{len(self.step_status)}")
        step_type = step.get('type', 'tool')  # 'tool', 'foreach', 'parallel', 'condition'

        logger.info(f"Executing step: {step_id} (type={step_type})")
        self.step_status[step_id] = StepStatus.RUNNING

        try:
            # Check condition
            if 'condition' in step:
                condition = step['condition']
                if not self.context.evaluate_condition(condition):
                    logger.info(f"Step {step_id} skipped (condition not met)")
                    self.step_status[step_id] = StepStatus.SKIPPED
                    return

            # Execute based on type
            if step_type == 'tool':
                result = self._execute_tool_step(step)
            elif step_type == 'foreach':
                result = self._execute_foreach_step(step)
            elif step_type == 'parallel':
                result = self._execute_parallel_step(step)
            elif step_type == 'condition':
                result = self._execute_condition_step(step)
            else:
                raise ValidationError(f"Unknown step type: {step_type}")

            # Store result
            self.context.set_step_result(step_id, result, success=True)
            self.step_status[step_id] = StepStatus.SUCCESS
            logger.info(f"Step {step_id} completed successfully")

        except Exception as e:
            logger.error(f"Step {step_id} failed: {e}")
            self.step_status[step_id] = StepStatus.FAILED

            # Store error result
            self.context.set_step_result(step_id, {"error": str(e)}, success=False)

            # Handle error
            if not self.continue_on_error:
                raise

    def _execute_tool_step(self, step: Dict[str, Any]) -> Any:
        """Execute a tool step with retry logic."""
        tool_name = step['tool']
        params = step.get('params', {})

        # Interpolate parameters
        interpolated_params = self.context.interpolate(params)

        # Get tool class
        tool_class = tool_registry.get_tool(tool_name)
        if not tool_class:
            raise ValidationError(f"Tool not found: {tool_name}")

        # Execute with retries
        last_error = None
        for attempt in range(self.max_retries if self.retry_on_failure else 1):
            try:
                # Create tool instance
                tool = tool_class(**interpolated_params)

                # Execute
                result = tool.run()
                return result

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1 and self.retry_on_failure:
                    retry_delay = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {retry_delay}s")
                    time.sleep(retry_delay)
                else:
                    raise

        if last_error:
            raise last_error

    def _execute_foreach_step(self, step: Dict[str, Any]) -> List[Any]:
        """
        Execute a step for each item in a collection.

        Example:
            {
                "type": "foreach",
                "items": "${steps.search.result}",
                "step": {
                    "tool": "crawler",
                    "params": {"url": "${item.url}"}
                }
            }
        """
        items = self.context.interpolate(step['items'])
        inner_step = step['step']
        results = []

        if not isinstance(items, list):
            raise ValidationError("foreach items must be a list")

        for index, item in enumerate(items):
            # Add item to context
            original_item = self.context.variables.get('item')
            original_index = self.context.variables.get('index')

            self.context.variables['item'] = item
            self.context.variables['index'] = index

            try:
                # Execute inner step
                if inner_step.get('type') == 'tool' or 'tool' in inner_step:
                    result = self._execute_tool_step(inner_step)
                    results.append(result)
                else:
                    # Recursive step execution
                    self._execute_step(inner_step)
                    step_id = inner_step.get('id', f"foreach_{index}")
                    step_result = self.context.get_step_result(step_id)
                    if step_result:
                        results.append(step_result['result'])
            finally:
                # Restore context
                if original_item is not None:
                    self.context.variables['item'] = original_item
                else:
                    self.context.variables.pop('item', None)

                if original_index is not None:
                    self.context.variables['index'] = original_index
                else:
                    self.context.variables.pop('index', None)

        return results

    def _execute_parallel_step(self, step: Dict[str, Any]) -> List[Any]:
        """
        Execute multiple steps in parallel (simulated for now).

        Note: True parallel execution would require threading/async.
        For now, executes sequentially.
        """
        substeps = step.get('steps', [])
        results = []

        for substep in substeps:
            if substep.get('type') == 'tool' or 'tool' in substep:
                result = self._execute_tool_step(substep)
                results.append(result)
            else:
                self._execute_step(substep)
                step_id = substep.get('id')
                if step_id:
                    step_result = self.context.get_step_result(step_id)
                    if step_result:
                        results.append(step_result['result'])

        return results

    def _execute_condition_step(self, step: Dict[str, Any]) -> Any:
        """
        Execute conditional step (if/else).

        Example:
            {
                "type": "condition",
                "condition": "${steps.search.success}",
                "then": {"tool": "crawler", ...},
                "else": {"tool": "fallback", ...}
            }
        """
        condition = step['condition']
        then_step = step.get('then')
        else_step = step.get('else')

        if self.context.evaluate_condition(condition):
            if then_step:
                return self._execute_tool_step(then_step) if 'tool' in then_step else None
        else:
            if else_step:
                return self._execute_tool_step(else_step) if 'tool' in else_step else None

        return None

    def _build_result(self, success: bool, error: Optional[str] = None) -> Dict[str, Any]:
        """Build final workflow result."""
        duration_ms = (self.end_time - self.start_time) * 1000 if self.end_time else 0

        steps_executed = sum(1 for s in self.step_status.values()
                           if s in (StepStatus.SUCCESS, StepStatus.FAILED))
        steps_failed = sum(1 for s in self.step_status.values() if s == StepStatus.FAILED)

        return {
            "success": success,
            "workflow_name": self.name,
            "results": {step_id: data['result']
                       for step_id, data in self.context.steps.items()},
            "step_status": {step_id: status.value
                          for step_id, status in self.step_status.items()},
            "duration_ms": duration_ms,
            "steps_executed": steps_executed,
            "steps_failed": steps_failed,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> 'WorkflowEngine':
        """
        Load workflow from JSON file.

        Args:
            filepath: Path to workflow JSON file

        Returns:
            WorkflowEngine instance
        """
        filepath = Path(filepath)
        with open(filepath, 'r') as f:
            workflow = json.load(f)
        return cls(workflow)

    @classmethod
    def from_dict(cls, workflow: Dict[str, Any]) -> 'WorkflowEngine':
        """Create workflow from dictionary."""
        return cls(workflow)


def execute_workflow(workflow: Union[Dict[str, Any], str, Path]) -> Dict[str, Any]:
    """
    Convenience function to execute a workflow.

    Args:
        workflow: Workflow dict or path to JSON file

    Returns:
        Execution result
    """
    if isinstance(workflow, (str, Path)):
        engine = WorkflowEngine.from_file(workflow)
    else:
        engine = WorkflowEngine(workflow)

    return engine.execute()


if __name__ == "__main__":
    # Test the workflow engine
    print("Testing WorkflowEngine...")

    # Test variable interpolation
    context = WorkflowContext({"topic": "AI", "count": 10})
    assert context.interpolate("${vars.topic}") == "AI"
    assert context.interpolate("Search: ${vars.topic}") == "Search: AI"

    # Test step results
    context.set_step_result("search", {"urls": ["url1", "url2"]}, success=True)
    assert context.interpolate("${steps.search.success}") == True
    assert context.interpolate("${steps.search.result.urls}") == ["url1", "url2"]

    # Test condition evaluation
    assert context.evaluate_condition("${steps.search.success}") == True
    assert context.evaluate_condition("${vars.count} > 5") == True
    assert context.evaluate_condition("${vars.count} < 5") == False

    print("All WorkflowEngine tests passed!")
