"""
Create Profile Tool - Create and manage user/agent profiles with customizable attributes
"""

from typing import Any, Dict, Optional, List
from pydantic import Field
import os
import json
from datetime import datetime

from shared.base import BaseTool
from shared.errors import ValidationError, APIError


class CreateProfile(BaseTool):
    """
    Create and manage user/agent profiles with customizable attributes.

    This tool allows creating structured profiles for users, agents, or other entities
    with flexible attributes including name, role, preferences, and metadata.

    Args:
        name: Profile name/identifier (required)
        profile_type: Type of profile (user, agent, system, custom)
        role: Role or function description
        attributes: Additional custom attributes as key-value pairs
        description: Profile description
        tags: List of tags for categorization
        metadata: Additional metadata

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Created profile data with ID and timestamp
        - metadata: Tool metadata

    Example:
        >>> tool = CreateProfile(
        ...     name="DataAnalyst",
        ...     profile_type="agent",
        ...     role="Data analysis specialist",
        ...     attributes={"specialty": "ML", "level": "expert"}
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "create_profile"
    tool_category: str = "utils"

    # Required parameters
    name: str = Field(
        ...,
        description="Profile name or identifier",
        min_length=1,
        max_length=200
    )

    # Optional parameters
    profile_type: str = Field(
        "user",
        description="Type of profile: user, agent, system, custom",
    )

    role: Optional[str] = Field(
        None,
        description="Role or function description",
        max_length=500
    )

    attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional custom attributes as key-value pairs"
    )

    description: Optional[str] = Field(
        None,
        description="Detailed profile description",
        max_length=2000
    )

    tags: Optional[List[str]] = Field(
        None,
        description="List of tags for categorization and search"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata (creation context, source, etc.)"
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the create profile tool.

        Returns:
            Dict with created profile data
        """
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            result = self._process()

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "tool_version": "1.0.0"
                },
            }
        except Exception as e:
            raise APIError(f"Failed to create profile: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """
        Validate input parameters.

        Raises:
            ValidationError: If parameters are invalid
        """
        # Validate name
        if not self.name or not isinstance(self.name, str):
            raise ValidationError(
                "Name must be a non-empty string",
                tool_name=self.tool_name,
                field="name"
            )

        if not self.name.strip():
            raise ValidationError(
                "Name cannot be empty or whitespace",
                tool_name=self.tool_name,
                field="name"
            )

        # Validate profile_type
        valid_types = ["user", "agent", "system", "custom"]
        if self.profile_type not in valid_types:
            raise ValidationError(
                f"Profile type must be one of: {', '.join(valid_types)}",
                tool_name=self.tool_name,
                field="profile_type",
                details={"provided": self.profile_type, "valid_types": valid_types}
            )

        # Validate attributes if provided
        if self.attributes is not None and not isinstance(self.attributes, dict):
            raise ValidationError(
                "Attributes must be a dictionary",
                tool_name=self.tool_name,
                field="attributes"
            )

        # Validate tags if provided
        if self.tags is not None:
            if not isinstance(self.tags, list):
                raise ValidationError(
                    "Tags must be a list",
                    tool_name=self.tool_name,
                    field="tags"
                )

            for tag in self.tags:
                if not isinstance(tag, str):
                    raise ValidationError(
                        "All tags must be strings",
                        tool_name=self.tool_name,
                        field="tags"
                    )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        profile_id = f"mock_profile_{hash(self.name) % 10000}"

        return {
            "success": True,
            "result": {
                "profile_id": profile_id,
                "name": self.name,
                "profile_type": self.profile_type,
                "role": self.role,
                "description": self.description,
                "attributes": self.attributes or {},
                "tags": self.tags or [],
                "metadata": {
                    **(self.metadata or {}),
                    "mock_mode": True
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "version": "1.0",
                "message": "[MOCK] Profile created successfully"
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name
            },
        }

    def _process(self) -> Dict[str, Any]:
        """
        Main processing logic for creating a profile.

        Returns:
            Dict containing the created profile data
        """
        # Generate unique profile ID
        import uuid
        profile_id = f"profile_{uuid.uuid4().hex[:12]}"

        # Build profile structure
        profile = {
            "profile_id": profile_id,
            "name": self.name,
            "profile_type": self.profile_type,
            "role": self.role,
            "description": self.description,
            "attributes": self.attributes or {},
            "tags": self.tags or [],
            "metadata": self.metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
            "version": "1.0"
        }

        # In a real implementation, this would:
        # 1. Store profile in database
        # 2. Index for search
        # 3. Emit events for profile creation
        # 4. Set up permissions/access control

        # For now, we simulate successful creation
        return {
            **profile,
            "message": f"Profile '{self.name}' created successfully",
            "storage": {
                "stored": True,
                "storage_type": "memory",
                "path": f"/profiles/{profile_id}.json"
            }
        }


if __name__ == "__main__":
    # Test the tool
    print("Testing CreateProfile...")

    import os
    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic profile
    print("\n=== Test 1: Basic User Profile ===")
    tool1 = CreateProfile(
        name="John Doe",
        profile_type="user"
    )
    result1 = tool1.run()
    print(f"Success: {result1.get('success')}")
    print(f"Profile ID: {result1.get('result', {}).get('profile_id')}")
    print(f"Name: {result1.get('result', {}).get('name')}")

    # Test 2: Agent profile with attributes
    print("\n=== Test 2: Agent Profile with Attributes ===")
    tool2 = CreateProfile(
        name="DataAnalyst",
        profile_type="agent",
        role="Data analysis and visualization specialist",
        description="Expert in statistical analysis and data visualization",
        attributes={
            "specialty": "Machine Learning",
            "experience_level": "expert",
            "languages": ["Python", "R", "SQL"],
            "tools": ["pandas", "scikit-learn", "matplotlib"]
        },
        tags=["AI", "ML", "data-science", "analytics"]
    )
    result2 = tool2.run()
    print(f"Success: {result2.get('success')}")
    print(f"Profile ID: {result2.get('result', {}).get('profile_id')}")
    print(f"Role: {result2.get('result', {}).get('role')}")
    print(f"Attributes: {json.dumps(result2.get('result', {}).get('attributes'), indent=2)}")
    print(f"Tags: {result2.get('result', {}).get('tags')}")

    # Test 3: Validation error
    print("\n=== Test 3: Validation Error (empty name) ===")
    try:
        tool3 = CreateProfile(name="   ", profile_type="user")
        result3 = tool3.run()
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")

    # Test 4: Invalid profile type
    print("\n=== Test 4: Validation Error (invalid type) ===")
    try:
        tool4 = CreateProfile(name="Test", profile_type="invalid_type")
        result4 = tool4.run()
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}")
        print(f"Error message: {str(e)}")

    print("\n=== All tests completed ===")
