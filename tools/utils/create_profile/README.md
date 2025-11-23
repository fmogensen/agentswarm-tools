# create_profile

Create and manage user/agent profiles with customizable attributes.

## Category

Utilities

## Parameters

- **name** (str): Profile name or identifier - **Required**
- **profile_type** (str): Type of profile: user, agent, system, custom - Optional
- **role** (str): Role or function description - Optional
- **attributes** (Dict[str, Any): Additional custom attributes as key-value pairs - Optional
- **description** (str): Detailed profile description - Optional
- **tags** (List[str): List of tags for categorization and search - Optional
- **metadata** (Dict[str, Any): No description - Optional

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Tool-specific results
- `metadata` (dict): Additional information about the operation

## Usage Example

```python
from tools.utils.create_profile import CreateProfile

# Initialize the tool
tool = CreateProfile(
    name="example_value",
    profile_type="example_value",  # Optional
    role="example_value"  # Optional
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(result["result"])
else:
    print(f"Error: {result.get('error')}")
```

## Testing

Run tests with:
```bash
python create_profile.py  # Run standalone test
```

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
