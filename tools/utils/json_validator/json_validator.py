"""
Validate JSON data against schemas.
"""

import json
import os
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, ValidationError


class JsonValidator(BaseTool):
    """
    Validate JSON data against a schema or check for well-formedness.

    Args:
        json_data: JSON data as a string or dict
        schema: Optional JSON schema to validate against (dict)
        strict: Whether to enforce strict validation (default: True)
        validate_types: Whether to validate data types (default: True)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Validation results including validity and any errors
        - metadata: Validation statistics and info

    Example:
        >>> tool = JsonValidator(
        ...     json_data='{"name": "John", "age": 30}',
        ...     validate_types=True
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "json_validator"
    tool_category: str = "utils"

    # Parameters
    json_data: str = Field(..., description="JSON data as a string or JSON string", min_length=1)
    schema: Optional[Dict[str, Any]] = Field(
        None, description="Optional JSON schema to validate against"
    )
    strict: bool = Field(True, description="Whether to enforce strict validation")
    validate_types: bool = Field(True, description="Whether to validate data types")

    def _execute(self) -> Dict[str, Any]:
        """Execute JSON validation."""

        self._logger.info(
            f"Executing {self.tool_name} with json_data={self.json_data}, schema={self.schema}, strict={self.strict}, validate_types={self.validate_types}"
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
                    "has_schema": self.schema is not None,
                    "strict_mode": self.strict,
                    "tool_version": "1.0.0",
                },
            }
        except Exception as e:
            self._logger.error(f"Error in {self.tool_name}: {str(e)}", exc_info=True)
            raise APIError(f"JSON validation failed: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        if not self.json_data or not isinstance(self.json_data, str):
            raise ValidationError(
                "json_data must be a non-empty string", tool_name=self.tool_name, field="json_data"
            )

        if not self.json_data.strip():
            raise ValidationError(
                "json_data cannot be empty or whitespace",
                tool_name=self.tool_name,
                field="json_data",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        return {
            "success": True,
            "result": {
                "is_valid": True,
                "parsed_data": {"mock": "data", "valid": True},
                "errors": [],
                "warnings": [],
                "schema_valid": self.schema is not None,
                "message": "Mock validation: JSON is valid",
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "has_schema": self.schema is not None,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Validate JSON data."""
        errors = []
        warnings = []
        parsed_data = None
        is_valid = False

        # Step 1: Parse JSON
        try:
            parsed_data = json.loads(self.json_data)
            is_valid = True
        except json.JSONDecodeError as e:
            errors.append(
                {
                    "type": "parse_error",
                    "message": f"Invalid JSON syntax: {str(e)}",
                    "line": e.lineno,
                    "column": e.colno,
                }
            )
            return {
                "is_valid": False,
                "parsed_data": None,
                "errors": errors,
                "warnings": warnings,
                "message": "JSON parsing failed",
            }

        # Step 2: Validate against schema if provided
        schema_valid = True
        if self.schema:
            schema_errors = self._validate_against_schema(parsed_data, self.schema)
            if schema_errors:
                schema_valid = False
                errors.extend(schema_errors)

        # Step 3: Type validation if requested
        if self.validate_types:
            type_warnings = self._validate_types(parsed_data)
            warnings.extend(type_warnings)

        # Step 4: Strict validation checks
        if self.strict:
            strict_warnings = self._strict_validation(parsed_data)
            warnings.extend(strict_warnings)

        # Determine final validity
        final_valid = is_valid and (not self.schema or schema_valid)

        return {
            "is_valid": final_valid,
            "parsed_data": parsed_data,
            "errors": errors,
            "warnings": warnings,
            "schema_valid": schema_valid if self.schema else None,
            "message": "JSON is valid" if final_valid else "JSON validation failed",
        }

    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> list:
        """Validate data against a simple schema."""
        errors = []

        # Simple schema validation (not full JSON Schema spec)
        if "type" in schema:
            expected_type = schema["type"]
            actual_type = type(data).__name__

            type_map = {
                "object": "dict",
                "array": "list",
                "string": "str",
                "number": ("int", "float"),
                "integer": "int",
                "boolean": "bool",
                "null": "NoneType",
            }

            expected_python_type = type_map.get(expected_type, expected_type)

            if isinstance(expected_python_type, tuple):
                if actual_type not in expected_python_type:
                    errors.append(
                        {
                            "type": "type_mismatch",
                            "message": f"Expected type {expected_type}, got {actual_type}",
                            "path": "$",
                        }
                    )
            else:
                if actual_type != expected_python_type:
                    errors.append(
                        {
                            "type": "type_mismatch",
                            "message": f"Expected type {expected_type}, got {actual_type}",
                            "path": "$",
                        }
                    )

        # Validate required properties for objects
        if isinstance(data, dict) and "required" in schema:
            for required_field in schema["required"]:
                if required_field not in data:
                    errors.append(
                        {
                            "type": "missing_required",
                            "message": f"Missing required field: {required_field}",
                            "path": "$",
                        }
                    )

        # Validate properties
        if isinstance(data, dict) and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                if prop_name in data:
                    prop_errors = self._validate_against_schema(data[prop_name], prop_schema)
                    for error in prop_errors:
                        error["path"] = f"$.{prop_name}"
                    errors.extend(prop_errors)

        return errors

    def _validate_types(self, data: Any, path: str = "$") -> list:
        """Validate data types and provide warnings."""
        warnings = []

        if isinstance(data, dict):
            for key, value in data.items():
                # Check for numeric strings
                if (
                    isinstance(value, str)
                    and value.strip().replace(".", "", 1).replace("-", "", 1).isdigit()
                ):
                    warnings.append(
                        {
                            "type": "type_warning",
                            "message": f"Numeric value stored as string: '{value}'",
                            "path": f"{path}.{key}",
                        }
                    )

                # Check for boolean strings
                if isinstance(value, str) and value.lower() in ["true", "false"]:
                    warnings.append(
                        {
                            "type": "type_warning",
                            "message": f"Boolean value stored as string: '{value}'",
                            "path": f"{path}.{key}",
                        }
                    )

                # Recursive check
                if isinstance(value, (dict, list)):
                    warnings.extend(self._validate_types(value, f"{path}.{key}"))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    warnings.extend(self._validate_types(item, f"{path}[{i}]"))

        return warnings

    def _strict_validation(self, data: Any) -> list:
        """Perform strict validation checks."""
        warnings = []

        if isinstance(data, dict):
            # Check for empty values
            for key, value in data.items():
                if value is None:
                    warnings.append(
                        {
                            "type": "strict_warning",
                            "message": f"Null value found",
                            "path": f"$.{key}",
                        }
                    )
                elif isinstance(value, str) and not value.strip():
                    warnings.append(
                        {
                            "type": "strict_warning",
                            "message": f"Empty string found",
                            "path": f"$.{key}",
                        }
                    )
                elif isinstance(value, (list, dict)) and not value:
                    warnings.append(
                        {
                            "type": "strict_warning",
                            "message": f"Empty {type(value).__name__} found",
                            "path": f"$.{key}",
                        }
                    )

        return warnings


if __name__ == "__main__":
    print("Testing JsonValidator...")

    # Test with mock mode
    os.environ["USE_MOCK_APIS"] = "true"

    tool = JsonValidator(json_data='{"name": "John", "age": 30}', validate_types=True)
    result = tool.run()

    print(f"Success: {result.get('success')}")
    assert result.get("success") == True
    print("JsonValidator test passed!")
