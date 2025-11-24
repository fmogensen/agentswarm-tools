"""
Tests for HubSpot Create Contact Tool

Comprehensive test suite covering contact creation, updates, batch operations,
custom properties, list management, and error handling.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from shared.errors import APIError, AuthenticationError, ValidationError
from tools.integrations.hubspot.hubspot_create_contact import HubSpotCreateContact


class TestHubSpotCreateContact:
    """Test suite for HubSpotCreateContact tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        # Cleanup
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_single_contact_creation(self):
        """Test creating a single contact with all standard fields."""
        tool = HubSpotCreateContact(
            email="john.doe@example.com",
            firstname="John",
            lastname="Doe",
            company="Acme Corp",
            jobtitle="CEO",
            phone="+1-555-1234",
            website="https://acme.example.com",
            lifecyclestage="lead",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["email"] == "john.doe@example.com"
        assert result["status"] == "created"
        assert "contact_id" in result
        assert result["contact_id"].startswith("vid_mock_")
        assert "properties" in result
        assert result["properties"]["email"] == "john.doe@example.com"

    def test_contact_with_custom_properties(self):
        """Test creating contact with custom properties."""
        tool = HubSpotCreateContact(
            email="jane.smith@tech.com",
            firstname="Jane",
            lastname="Smith",
            custom_properties={
                "industry": "Technology",
                "employee_count": "50-100",
                "annual_revenue": "1000000",
                "lead_source": "Website",
            },
        )
        result = tool.run()

        assert result["success"] == True
        assert "industry" in result["properties"]
        assert result["properties"]["industry"] == "Technology"
        assert "employee_count" in result["properties"]

    def test_contact_with_list_assignments(self):
        """Test creating contact and adding to lists."""
        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="Test",
            lastname="User",
            lists=["123", "456", "789"],
        )
        result = tool.run()

        assert result["success"] == True
        assert "lists_added" in result
        assert len(result["lists_added"]) == 3

    def test_batch_contact_creation(self):
        """Test creating multiple contacts in batch."""
        batch_contacts = [
            {
                "email": "alice@example.com",
                "firstname": "Alice",
                "lastname": "Smith",
                "company": "TechCorp",
            },
            {
                "email": "bob@example.com",
                "firstname": "Bob",
                "lastname": "Jones",
                "jobtitle": "VP Sales",
            },
            {
                "email": "carol@example.com",
                "firstname": "Carol",
                "lastname": "White",
                "lifecyclestage": "customer",
            },
        ]

        tool = HubSpotCreateContact(batch_contacts=batch_contacts)
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "batch_processed"
        assert result["contacts_created"] == 3
        assert len(result["contact_ids"]) == 3

    def test_lifecycle_stage_validation(self):
        """Test validation of lifecycle stage values."""
        # Valid lifecycle stage
        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="Test",
            lifecyclestage="marketingqualifiedlead",
        )
        result = tool.run()
        assert result["success"] == True

        # Invalid lifecycle stage - should raise ValidationError
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotCreateContact(
                email="test@example.com",
                firstname="Test",
                lifecyclestage="invalid_stage",
            )
            tool.run()

        assert "Invalid lifecycle stage" in str(exc_info.value)

    def test_email_validation(self):
        """Test email format validation."""
        # Valid email
        tool = HubSpotCreateContact(
            email="valid.email@domain.com",
            firstname="Valid",
        )
        result = tool.run()
        assert result["success"] == True

        # Missing email in single mode - should raise error
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotCreateContact(firstname="No", lastname="Email")
            tool.run()

        assert "email is required" in str(exc_info.value).lower()

    def test_batch_size_limit(self):
        """Test batch size cannot exceed 10 contacts."""
        large_batch = [
            {"email": f"user{i}@example.com", "firstname": f"User{i}"} for i in range(11)
        ]

        with pytest.raises(Exception) as exc_info:
            tool = HubSpotCreateContact(batch_contacts=large_batch)
            tool.run()

        assert "cannot exceed 10" in str(exc_info.value)

    def test_batch_contact_email_validation(self):
        """Test that each batch contact must have email."""
        batch_contacts = [
            {"email": "user1@example.com", "firstname": "User1"},
            {"firstname": "User2"},  # Missing email
        ]

        with pytest.raises(Exception) as exc_info:
            tool = HubSpotCreateContact(batch_contacts=batch_contacts)
            tool.run()

        assert "missing required 'email' field" in str(exc_info.value)

    def test_update_if_exists_flag(self):
        """Test update_if_exists behavior."""
        tool = HubSpotCreateContact(
            email="existing@example.com",
            firstname="Updated",
            lastname="Name",
            update_if_exists=True,
        )
        result = tool.run()

        assert result["success"] == True
        assert "update_if_exists" in result["metadata"]
        assert result["metadata"]["update_if_exists"] == True

    def test_properties_building(self):
        """Test that properties are correctly built from inputs."""
        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="John",
            lastname="Doe",
            phone="+1-555-1234",
            company="Acme",
            website="https://acme.com",
            jobtitle="CEO",
            lifecyclestage="customer",
            custom_properties={"score": "90", "source": "referral"},
        )
        result = tool.run()

        props = result["properties"]
        assert props["email"] == "test@example.com"
        assert props["firstname"] == "John"
        assert props["lastname"] == "Doe"
        assert props["phone"] == "+1-555-1234"
        assert props["company"] == "Acme"
        assert props["website"] == "https://acme.com"
        assert props["jobtitle"] == "CEO"
        assert props["lifecyclestage"] == "customer"
        assert props["score"] == "90"
        assert props["source"] == "referral"

    def test_mock_mode_enabled(self):
        """Test that mock mode generates realistic results."""
        os.environ["USE_MOCK_APIS"] = "true"

        tool = HubSpotCreateContact(
            email="mock@example.com",
            firstname="Mock",
            lastname="User",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["metadata"]["mock_mode"] == True
        assert "contact_id" in result

    def test_tool_metadata(self):
        """Test that tool metadata is correctly set."""
        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="Test",
        )

        assert tool.tool_name == "hubspot_create_contact"
        assert tool.tool_category == "integrations"
        assert tool.rate_limit_type == "hubspot_api"
        assert tool.rate_limit_cost == 1

    @patch("tools.integrations.hubspot.hubspot_create_contact.requests")
    def test_api_call_with_real_mode(self, mock_requests):
        """Test actual API call structure (mocked)."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "test_api_key"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "12345",
            "properties": {
                "email": "test@example.com",
                "firstname": "Test",
            },
        }
        mock_requests.post.return_value = mock_response

        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="Test",
        )
        result = tool.run()

        # Verify API call was made
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args

        assert "https://api.hubapi.com/crm/v3/objects/contacts" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_api_key"
        assert "properties" in call_args[1]["json"]

        # Cleanup
        os.environ.pop("HUBSPOT_API_KEY")

    @patch("tools.integrations.hubspot.hubspot_create_contact.requests")
    def test_authentication_error(self, mock_requests):
        """Test handling of authentication errors."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "invalid_key"

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b'{"message": "Unauthorized"}'
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_requests.post.return_value = mock_response
        mock_requests.post.return_value.raise_for_status.side_effect = __import__(
            "requests"
        ).exceptions.HTTPError(response=mock_response)

        tool = HubSpotCreateContact(
            email="test@example.com",
            firstname="Test",
        )

        # Tool wraps AuthenticationError in APIError, so check for APIError
        with pytest.raises(APIError) as exc_info:
            tool.run()

        # Verify the error message contains authentication info
        assert "auth" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

        # Cleanup
        os.environ.pop("HUBSPOT_API_KEY")

    def test_empty_batch_validation(self):
        """Test that empty batch raises error."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotCreateContact(batch_contacts=[])
            tool.run()

        assert "non-empty list" in str(exc_info.value)

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        tool = HubSpotCreateContact(
            email="minimal@example.com",
            firstname="Min",
        )
        result = tool.run()

        assert result["success"] == True
        props = result["properties"]
        assert "email" in props
        assert "firstname" in props
        # Optional fields should not be present if not provided
        assert props.get("lastname") is None

    def test_contact_id_generation_consistency(self):
        """Test that contact IDs are consistently generated."""
        tool1 = HubSpotCreateContact(
            email="same@example.com",
            firstname="Same",
        )
        result1 = tool1.run()

        tool2 = HubSpotCreateContact(
            email="same@example.com",
            firstname="Same",
        )
        result2 = tool2.run()

        # Same email should generate same mock ID
        assert result1["contact_id"] == result2["contact_id"]

    def test_batch_with_custom_properties(self):
        """Test batch creation with custom properties per contact."""
        batch_contacts = [
            {
                "email": "user1@example.com",
                "firstname": "User1",
                "custom_properties": {"score": "80", "segment": "A"},
            },
            {
                "email": "user2@example.com",
                "firstname": "User2",
                "custom_properties": {"score": "95", "segment": "VIP"},
            },
        ]

        tool = HubSpotCreateContact(batch_contacts=batch_contacts)
        result = tool.run()

        assert result["success"] == True
        assert result["contacts_created"] == 2


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
