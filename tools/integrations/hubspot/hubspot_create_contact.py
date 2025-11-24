"""
HubSpot Create Contact Tool

Creates and updates contacts in HubSpot CRM with custom properties,
list assignments, and bulk operations support.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
from pydantic import Field
from requests.exceptions import HTTPError, RequestException, Timeout

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class HubSpotCreateContact(BaseTool):
    """
    Create or update contacts in HubSpot CRM with custom properties and list management.

    This tool creates new contacts or updates existing ones in HubSpot, supporting
    custom properties, list assignments, and bulk operations. Ideal for CRM data
    management, lead capture, and contact enrichment workflows.

    Args:
        email: Contact's email address (required, primary identifier)
        firstname: Contact's first name
        lastname: Contact's last name
        phone: Contact's phone number
        company: Company name
        website: Website URL
        jobtitle: Job title
        lifecyclestage: Contact lifecycle stage (subscriber, lead, marketingqualifiedlead,
            salesqualifiedlead, opportunity, customer, evangelist, other)
        custom_properties: Dictionary of custom property names and values
        lists: List IDs to add contact to
        update_if_exists: Update contact if email already exists (default: True)
        batch_contacts: List of contact dictionaries for bulk creation (overrides single contact)

    Returns:
        Dict containing:
            - success (bool): Whether the operation succeeded
            - contact_id (str): HubSpot contact VID (or list of VIDs for batch)
            - email (str): Contact email
            - status (str): created, updated, or batch_processed
            - properties (dict): Contact properties that were set
            - lists_added (list): List IDs the contact was added to
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Create single contact
        >>> tool = HubSpotCreateContact(
        ...     email="john.doe@example.com",
        ...     firstname="John",
        ...     lastname="Doe",
        ...     company="Acme Corp",
        ...     jobtitle="CEO",
        ...     lifecyclestage="lead",
        ...     custom_properties={"industry": "Technology", "employee_count": "50-100"},
        ...     lists=["123", "456"]
        ... )
        >>> result = tool.run()
        >>> print(result['contact_id'])
        '12345'

        >>> # Batch create contacts
        >>> tool = HubSpotCreateContact(
        ...     batch_contacts=[
        ...         {"email": "contact1@example.com", "firstname": "Alice", "lastname": "Smith"},
        ...         {"email": "contact2@example.com", "firstname": "Bob", "lastname": "Jones"}
        ...     ]
        ... )
        >>> result = tool.run()
        >>> print(len(result['contact_ids']))
        2
    """

    # Tool metadata
    tool_name: str = "hubspot_create_contact"
    tool_category: str = "integrations"
    rate_limit_type: str = "hubspot_api"
    rate_limit_cost: int = 1

    # Required parameters
    email: Optional[str] = Field(
        None,
        description="Contact's email address (primary identifier)",
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
    )

    # Optional contact properties
    firstname: Optional[str] = Field(None, description="Contact's first name", max_length=100)
    lastname: Optional[str] = Field(None, description="Contact's last name", max_length=100)
    phone: Optional[str] = Field(None, description="Contact's phone number", max_length=50)
    company: Optional[str] = Field(None, description="Company name", max_length=200)
    website: Optional[str] = Field(None, description="Website URL", max_length=500)
    jobtitle: Optional[str] = Field(None, description="Job title", max_length=100)
    lifecyclestage: Optional[str] = Field(
        None,
        description="Lifecycle stage (subscriber, lead, marketingqualifiedlead, etc.)",
    )

    # Advanced options
    custom_properties: Optional[Dict[str, Any]] = Field(
        None, description="Dictionary of custom property names and values"
    )
    lists: Optional[List[str]] = Field(None, description="List IDs to add contact to")
    update_if_exists: bool = Field(True, description="Update contact if email already exists")

    # Batch operations
    batch_contacts: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of contact dictionaries for bulk creation"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the contact creation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            if self.batch_contacts:
                result = self._process_batch()
            else:
                result = self._process_single()

            return result
        except Exception as e:
            raise APIError(f"Failed to create contact: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Check if batch or single mode
        if self.batch_contacts is not None:
            # Validate batch contacts is not empty
            if not isinstance(self.batch_contacts, list):
                raise ValidationError(
                    "batch_contacts must be a list",
                    tool_name=self.tool_name,
                )

            if len(self.batch_contacts) == 0:
                raise ValidationError(
                    "batch_contacts must be a non-empty list",
                    tool_name=self.tool_name,
                )

            # Validate batch size limit (10 contacts per batch per requirements)
            if len(self.batch_contacts) > 10:
                raise ValidationError(
                    "Batch size cannot exceed 10 contacts",
                    tool_name=self.tool_name,
                )

            # Validate each contact has email
            for idx, contact in enumerate(self.batch_contacts):
                if not contact.get("email"):
                    raise ValidationError(
                        "Each contact in batch missing required 'email' field",
                        tool_name=self.tool_name,
                    )
        else:
            # Single contact mode - email is required
            if not self.email:
                raise ValidationError(
                    "email is required for single contact creation",
                    tool_name=self.tool_name,
                )

            # Validate email format if provided
            if self.email and "@" not in self.email:
                raise ValidationError(
                    "Invalid email format",
                    tool_name=self.tool_name,
                )

        # Validate lifecycle stage if provided
        if self.lifecyclestage:
            valid_stages = [
                "subscriber",
                "lead",
                "marketingqualifiedlead",
                "salesqualifiedlead",
                "opportunity",
                "customer",
                "evangelist",
                "other",
            ]
            if self.lifecyclestage.lower() not in valid_stages:
                raise ValidationError(
                    f"Invalid lifecycle stage: {self.lifecyclestage}. Must be one of: {', '.join(valid_stages)}",
                    tool_name=self.tool_name,
                )

        # API key check - only if NOT in mock mode
        if not self._should_use_mock():
            api_key = os.getenv("HUBSPOT_API_KEY")
            if not api_key:
                raise AuthenticationError(
                    "Missing HUBSPOT_API_KEY environment variable",
                    tool_name=self.tool_name,
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode is enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        if self.batch_contacts:
            # Mock batch results
            contact_ids = [
                f"vid_mock_{i}_{''.join([str(ord(c)) for c in contact.get('email', '')])}"[:20]
                for i, contact in enumerate(self.batch_contacts)
            ]
            return {
                "success": True,
                "status": "batch_processed",
                "contact_ids": contact_ids,
                "contacts_created": len(self.batch_contacts),
                "contacts_updated": 0,
                "metadata": {
                    "tool_name": self.tool_name,
                    "batch_size": len(self.batch_contacts),
                    "mock_mode": True,
                },
            }
        else:
            # Mock single contact result
            contact_id = f"vid_mock_{''.join([str(ord(c)) for c in self.email])}"[:20]
            return {
                "success": True,
                "contact_id": contact_id,
                "email": self.email,
                "status": "created",
                "properties": self._build_properties(),
                "lists_added": self.lists or [],
                "metadata": {
                    "tool_name": self.tool_name,
                    "update_if_exists": self.update_if_exists,
                    "mock_mode": True,
                },
            }

    def _build_properties(self, contact_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build properties dictionary from contact data or instance attributes."""
        if contact_data:
            # Build from provided contact data (for batch)
            properties = {}
            standard_props = [
                "email",
                "firstname",
                "lastname",
                "phone",
                "company",
                "website",
                "jobtitle",
                "lifecyclestage",
            ]
            for prop in standard_props:
                if contact_data.get(prop):
                    properties[prop] = contact_data[prop]

            # Add custom properties
            if contact_data.get("custom_properties"):
                properties.update(contact_data["custom_properties"])

            return properties
        else:
            # Build from instance attributes
            properties = {}
            if self.email:
                properties["email"] = self.email
            if self.firstname:
                properties["firstname"] = self.firstname
            if self.lastname:
                properties["lastname"] = self.lastname
            if self.phone:
                properties["phone"] = self.phone
            if self.company:
                properties["company"] = self.company
            if self.website:
                properties["website"] = self.website
            if self.jobtitle:
                properties["jobtitle"] = self.jobtitle
            if self.lifecyclestage:
                properties["lifecyclestage"] = self.lifecyclestage.lower()

            # Add custom properties
            if self.custom_properties:
                properties.update(self.custom_properties)

            return properties

    def _process_single(self) -> Dict[str, Any]:
        """Process single contact creation with HubSpot API."""
        # Get API key
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        # Import requests
        # Build properties
        properties = self._build_properties()

        # Prepare API request
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {"properties": properties}

        # Create or update contact
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Handle existing contact (409 conflict)
            if response.status_code == 409 and self.update_if_exists:
                # Get contact ID from error message or search by email
                contact_id = self._get_contact_by_email(api_key, self.email)
                if contact_id:
                    # Update existing contact
                    update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                    update_response = requests.patch(
                        update_url, headers=headers, json=payload, timeout=30
                    )
                    update_response.raise_for_status()
                    contact_data = update_response.json()
                    status = "updated"
                else:
                    raise APIError(
                        "Contact exists but could not retrieve ID",
                        tool_name=self.tool_name,
                    )
            elif response.status_code == 409:
                raise APIError(
                    f"Contact with email {self.email} already exists",
                    tool_name=self.tool_name,
                )
            else:
                response.raise_for_status()
                contact_data = response.json()
                status = "created"

            contact_id = contact_data.get("id")

            # Add to lists if specified
            lists_added = []
            if self.lists and contact_id:
                lists_added = self._add_to_lists(api_key, contact_id, self.lists)

            return {
                "success": True,
                "contact_id": contact_id,
                "email": self.email,
                "status": status,
                "properties": properties,
                "lists_added": lists_added,
                "metadata": {
                    "tool_name": self.tool_name,
                    "update_if_exists": self.update_if_exists,
                },
            }

        except HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid HubSpot API key", tool_name=self.tool_name)
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded. Try again later.", tool_name=self.tool_name)
            else:
                error_detail = e.response.json() if e.response.content else {}
                raise APIError(
                    f"HubSpot API error: {error_detail.get('message', str(e))}",
                    tool_name=self.tool_name,
                )
        except Timeout:
            raise APIError(
                "Request timed out. HubSpot API may be slow.",
                tool_name=self.tool_name,
            )
        except RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)

    def _process_batch(self) -> Dict[str, Any]:
        """Process batch contact creation with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        # Prepare batch payload
        url = "https://api.hubapi.com/crm/v3/objects/contacts/batch/create"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        inputs = []
        for contact in self.batch_contacts:
            properties = self._build_properties(contact)
            inputs.append({"properties": properties})

        payload = {"inputs": inputs}

        # Execute batch create
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result_data = response.json()

            # Extract contact IDs
            contact_ids = [contact.get("id") for contact in result_data.get("results", [])]
            contacts_created = len(contact_ids)

            return {
                "success": True,
                "status": "batch_processed",
                "contact_ids": contact_ids,
                "contacts_created": contacts_created,
                "contacts_updated": 0,
                "metadata": {
                    "tool_name": self.tool_name,
                    "batch_size": len(self.batch_contacts),
                },
            }

        except HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid HubSpot API key", tool_name=self.tool_name)
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded. Try again later.", tool_name=self.tool_name)
            else:
                error_detail = e.response.json() if e.response.content else {}
                raise APIError(
                    f"HubSpot batch API error: {error_detail.get('message', str(e))}",
                    tool_name=self.tool_name,
                )
        except Timeout:
            raise APIError(
                "Batch request timed out. Try smaller batch size.",
                tool_name=self.tool_name,
            )
        except RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)

    def _get_contact_by_email(self, api_key: str, email: str) -> Optional[str]:
        """Get contact ID by email address."""
        try:
            url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email,
                            }
                        ]
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if results:
                return results[0].get("id")
            return None

        except Exception:
            return None

    def _add_to_lists(self, api_key: str, contact_id: str, list_ids: List[str]) -> List[str]:
        """Add contact to specified lists."""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            added_lists = []
            for list_id in list_ids:
                url = f"https://api.hubapi.com/contacts/v1/lists/{list_id}/add"
                payload = {"vids": [int(contact_id)]}

                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    if response.status_code == 200:
                        added_lists.append(list_id)
                except Exception:
                    # Continue adding to other lists even if one fails
                    continue

            return added_lists

        except Exception:
            return []


if __name__ == "__main__":
    # Test the tool
    print("Testing HubSpotCreateContact...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create single contact
    print("\n1. Testing single contact creation...")
    tool = HubSpotCreateContact(
        email="john.doe@example.com",
        firstname="John",
        lastname="Doe",
        company="Acme Corp",
        jobtitle="CEO",
        phone="+1-555-1234",
        website="https://acme.example.com",
        lifecyclestage="lead",
        custom_properties={"industry": "Technology", "employee_count": "50-100"},
        lists=["123", "456"],
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Contact ID: {result.get('contact_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Email: {result.get('email')}")
    print(f"Lists added: {result.get('lists_added')}")
    assert result.get("success") == True
    assert result.get("contact_id") is not None
    assert result.get("status") == "created"

    # Test 2: Batch contact creation
    print("\n2. Testing batch contact creation...")
    tool = HubSpotCreateContact(
        batch_contacts=[
            {
                "email": "alice.smith@example.com",
                "firstname": "Alice",
                "lastname": "Smith",
                "company": "TechCorp",
                "lifecyclestage": "lead",
            },
            {
                "email": "bob.jones@example.com",
                "firstname": "Bob",
                "lastname": "Jones",
                "company": "InnovateCo",
                "lifecyclestage": "marketingqualifiedlead",
            },
            {
                "email": "carol.white@example.com",
                "firstname": "Carol",
                "lastname": "White",
                "jobtitle": "VP Sales",
            },
        ]
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Contacts created: {result.get('contacts_created')}")
    print(f"Contact IDs: {result.get('contact_ids')}")
    assert result.get("success") == True
    assert result.get("status") == "batch_processed"
    assert result.get("contacts_created") == 3

    # Test 3: Contact with custom properties
    print("\n3. Testing contact with custom properties...")
    tool = HubSpotCreateContact(
        email="jane.doe@startup.com",
        firstname="Jane",
        lastname="Doe",
        custom_properties={
            "annual_revenue": "1000000",
            "number_of_employees": "25",
            "industry": "SaaS",
            "lead_source": "Website",
            "lead_score": "85",
        },
        update_if_exists=True,
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Properties set: {len(result.get('properties', {}))}")
    assert result.get("success") == True
    assert "annual_revenue" in result.get("properties", {})

    # Test 4: Error handling - missing email in single mode
    print("\n4. Testing error handling (missing email)...")
    try:
        tool = HubSpotCreateContact(firstname="Test", lastname="User")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    # Test 5: Error handling - batch too large
    print("\n5. Testing error handling (batch too large)...")
    try:
        large_batch = [
            {"email": f"user{i}@example.com", "firstname": f"User{i}"} for i in range(11)
        ]
        tool = HubSpotCreateContact(batch_contacts=large_batch)
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
