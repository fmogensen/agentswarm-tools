"""
Process multiple items in batch operations.
"""

import os
import time
from typing import Any, Callable, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.batch import DefaultProgressCallback, ExecutorType, parallel_process
from shared.errors import APIError, ValidationError


class BatchProcessor(BaseTool):
    """
    Process multiple items in batch with various operations.

    Args:
        items: List of items to process
        operation: Operation to perform (transform, filter, validate, aggregate)
        operation_config: Configuration for the operation
        batch_size: Number of items to process per batch (default: 10)
        continue_on_error: Whether to continue processing if an item fails (default: True)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Processed items and statistics
        - metadata: Processing info and performance metrics

    Example:
        >>> tool = BatchProcessor(
        ...     items=["item1", "item2", "item3"],
        ...     operation="transform",
        ...     operation_config={"method": "uppercase"}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "batch_processor"
    tool_category: str = "utils"

    # Parameters
    items: List[Any] = Field(..., description="List of items to process", min_length=1)
    operation: str = Field(
        ..., description="Operation to perform: transform, filter, validate, aggregate, count"
    )
    operation_config: Optional[Dict[str, Any]] = Field(
        None, description="Configuration for the operation (e.g., {'method': 'uppercase'})"
    )
    batch_size: int = Field(10, description="Number of items to process per batch", ge=1, le=100)
    continue_on_error: bool = Field(
        True, description="Whether to continue processing if an item fails"
    )
    max_workers: int = Field(10, description="Maximum number of parallel workers", ge=1, le=50)
    use_parallel: bool = Field(
        True, description="Whether to use parallel processing (vs sequential)"
    )
    show_progress: bool = Field(True, description="Whether to show progress information")

    def _execute(self) -> Dict[str, Any]:
        """Execute batch processing."""

        self._logger.info(f"Executing {self.tool_name} with items={self.items}, operation={self.operation}, operation_config={self.operation_config}, ...")
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
                    "operation": self.operation,
                    "total_items": len(self.items),
                    "batch_size": self.batch_size,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"Batch processing failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        valid_operations = ["transform", "filter", "validate", "aggregate", "count"]

        if self.operation not in valid_operations:
            raise ValidationError(
                f"operation must be one of {valid_operations}",
                tool_name=self.tool_name,
                field="operation",
            )

        if not self.items or len(self.items) == 0:
            raise ValidationError("items cannot be empty", tool_name=self.tool_name, field="items")

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        return {
            "success": True,
            "result": {
                "processed_items": [
                    "[MOCK] processed_item_" + str(i) for i in range(min(5, len(self.items)))
                ],
                "total_processed": len(self.items),
                "successful": len(self.items),
                "failed": 0,
                "batches_completed": (len(self.items) + self.batch_size - 1) // self.batch_size,
                "processing_time_ms": 100.0,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "operation": self.operation,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Process items in batches with optional parallel execution."""
        if self.use_parallel:
            return self._process_parallel()
        else:
            return self._process_sequential()

    def _process_parallel(self) -> Dict[str, Any]:
        """Process items using parallel execution."""
        progress_callback = (
            DefaultProgressCallback(verbose=self.show_progress)
            if self.show_progress
            else DefaultProgressCallback(verbose=False)
        )

        # Use parallel processing from shared.batch
        batch_result = parallel_process(
            items=self.items,
            processor=self._process_item,
            max_workers=self.max_workers,
            executor_type=ExecutorType.THREAD,  # I/O-bound operations
            progress_callback=progress_callback,
            continue_on_error=self.continue_on_error,
        )

        return {
            "processed_items": batch_result.successes,
            "total_processed": batch_result.successful_count,
            "successful": batch_result.successful_count,
            "failed": batch_result.failed_count,
            "failed_items": [f["item"] for f in batch_result.failures],
            "errors": batch_result.failures,
            "batches_completed": 1,  # Parallel processes all at once
            "total_batches": 1,
            "processing_time_ms": round(batch_result.processing_time_ms, 2),
            "parallel_execution": True,
            "max_workers": self.max_workers,
            "success_rate": batch_result.success_rate,
        }

    def _process_sequential(self) -> Dict[str, Any]:
        """Process items sequentially in batches (original implementation)."""
        start_time = time.time()

        processed_items = []
        failed_items = []
        errors = []

        # Split items into batches
        num_batches = (len(self.items) + self.batch_size - 1) // self.batch_size

        for batch_idx in range(num_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(self.items))
            batch = self.items[start_idx:end_idx]

            # Process batch
            batch_results = self._process_batch(batch, start_idx)
            processed_items.extend(batch_results["processed"])
            failed_items.extend(batch_results["failed"])
            errors.extend(batch_results["errors"])

            # If not continuing on error and we have failures, stop
            if not self.continue_on_error and len(failed_items) > 0:
                break

        processing_time_ms = (time.time() - start_time) * 1000

        return {
            "processed_items": processed_items,
            "total_processed": len(processed_items),
            "successful": len(processed_items),
            "failed": len(failed_items),
            "failed_items": failed_items,
            "errors": errors,
            "batches_completed": min(batch_idx + 1, num_batches),
            "total_batches": num_batches,
            "processing_time_ms": round(processing_time_ms, 2),
            "parallel_execution": False,
        }

    def _process_batch(self, batch: List[Any], start_idx: int) -> Dict[str, Any]:
        """Process a single batch."""
        processed = []
        failed = []
        errors = []

        for idx, item in enumerate(batch):
            try:
                result = self._process_item(item)
                processed.append(result)
            except Exception as e:
                failed.append(item)
                errors.append(
                    {
                        "item_index": start_idx + idx,
                        "item": str(item)[:100],  # Limit item representation
                        "error": str(e),
                    }
                )

        return {"processed": processed, "failed": failed, "errors": errors}

    def _process_item(self, item: Any) -> Any:
        """Process a single item based on operation."""
        if self.operation == "transform":
            return self._transform_item(item)

        elif self.operation == "filter":
            return self._filter_item(item)

        elif self.operation == "validate":
            return self._validate_item(item)

        elif self.operation == "aggregate":
            # For aggregate, just return the item (actual aggregation happens at batch level)
            return item

        elif self.operation == "count":
            # For count, return 1 for each item
            return 1

        return item

    def _transform_item(self, item: Any) -> Any:
        """Transform an item."""
        if not self.operation_config:
            return item

        method = self.operation_config.get("method", "none")

        if isinstance(item, str):
            if method == "uppercase":
                return item.upper()
            elif method == "lowercase":
                return item.lower()
            elif method == "title":
                return item.title()
            elif method == "reverse":
                return item[::-1]
            elif method == "strip":
                return item.strip()

        elif isinstance(item, (int, float)):
            if method == "double":
                return item * 2
            elif method == "square":
                return item**2
            elif method == "negate":
                return -item

        return item

    def _filter_item(self, item: Any) -> Any:
        """Filter an item (returns item if it passes filter, raises exception otherwise)."""
        if not self.operation_config:
            return item

        condition = self.operation_config.get("condition", "all")

        if condition == "non_empty" and isinstance(item, str):
            if not item.strip():
                raise ValueError("Item is empty")

        elif condition == "positive" and isinstance(item, (int, float)):
            if item <= 0:
                raise ValueError("Item is not positive")

        elif condition == "non_null":
            if item is None:
                raise ValueError("Item is null")

        return item

    def _validate_item(self, item: Any) -> Dict[str, Any]:
        """Validate an item and return validation result."""
        validation_result = {"item": item, "valid": True, "errors": []}

        if not self.operation_config:
            return validation_result

        rules = self.operation_config.get("rules", [])

        for rule in rules:
            rule_type = rule.get("type")

            if rule_type == "type_check":
                expected_type = rule.get("expected_type")
                if expected_type == "string" and not isinstance(item, str):
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Expected string, got {type(item).__name__}"
                    )

                elif expected_type == "number" and not isinstance(item, (int, float)):
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Expected number, got {type(item).__name__}"
                    )

            elif rule_type == "min_length" and isinstance(item, str):
                min_len = rule.get("value", 0)
                if len(item) < min_len:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Length {len(item)} is less than minimum {min_len}"
                    )

            elif rule_type == "max_length" and isinstance(item, str):
                max_len = rule.get("value", float("inf"))
                if len(item) > max_len:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Length {len(item)} exceeds maximum {max_len}"
                    )

        if not validation_result["valid"]:
            raise ValueError(f"Validation failed: {validation_result['errors']}")

        return validation_result


if __name__ == "__main__":
    print("Testing BatchProcessor...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = BatchProcessor(
        items=["item1", "item2", "item3", "item4", "item5"],
        operation="transform",
        operation_config={"method": "uppercase"},
        batch_size=2,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("BatchProcessor test passed!")
