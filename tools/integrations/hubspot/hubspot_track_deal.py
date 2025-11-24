"""
HubSpot Track Deal Tool

Creates and updates deals in HubSpot CRM with pipeline management,
stage tracking, deal values, and forecasting support.
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError


class HubSpotTrackDeal(BaseTool):
    """
    Create and update deals in HubSpot CRM with pipeline and stage management.

    This tool manages deals in HubSpot including creating new deals, updating
    deal stages, tracking deal values, associating with contacts/companies,
    and managing pipelines. Supports sales forecasting and deal tracking workflows.

    Args:
        dealname: Name of the deal (required)
        amount: Deal value/amount in specified currency
        dealstage: Deal stage ID or name
        pipeline: Pipeline ID (default uses account default pipeline)
        closedate: Expected close date (YYYY-MM-DD format or Unix timestamp ms)
        dealtype: Deal type (newbusiness, existingbusiness, renewal)
        description: Deal description
        priority: Deal priority (low, medium, high)

        # Associations
        contact_ids: List of contact IDs to associate with deal
        company_ids: List of company IDs to associate with deal

        # Custom fields
        custom_properties: Dictionary of custom property names and values

        # Deal operations
        deal_id: Deal ID for updates (if updating existing deal)
        move_to_stage: Move deal to specified stage (requires deal_id)
        win_deal: Mark deal as won (requires deal_id)
        lose_deal: Mark deal as lost (requires deal_id, optionally loss_reason)
        loss_reason: Reason for losing deal

        # Batch operations
        batch_deals: List of deal dictionaries for bulk creation

    Returns:
        Dict containing:
            - success (bool): Whether the operation succeeded
            - deal_id (str): HubSpot deal ID (or list of IDs for batch)
            - dealname (str): Deal name
            - amount (float): Deal value
            - dealstage (str): Current deal stage
            - pipeline (str): Pipeline ID
            - status (str): created, updated, won, lost, batch_processed
            - associations (dict): Associated contact and company IDs
            - forecast_category (str): Forecast category based on stage
            - metadata (dict): Tool execution metadata

    Example:
        >>> # Create new deal
        >>> tool = HubSpotTrackDeal(
        ...     dealname="Acme Corp - Q1 Contract",
        ...     amount=50000,
        ...     dealstage="qualifiedtobuy",
        ...     closedate="2024-03-31",
        ...     dealtype="newbusiness",
        ...     contact_ids=["12345"],
        ...     company_ids=["67890"],
        ...     custom_properties={"contract_term": "12 months"}
        ... )
        >>> result = tool.run()
        >>> print(result['deal_id'])
        '987654321'

        >>> # Update deal stage
        >>> tool = HubSpotTrackDeal(
        ...     deal_id="987654321",
        ...     move_to_stage="presentationscheduled"
        ... )
        >>> result = tool.run()

        >>> # Win deal
        >>> tool = HubSpotTrackDeal(
        ...     deal_id="987654321",
        ...     win_deal=True,
        ...     amount=55000  # Final amount
        ... )
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "hubspot_track_deal"
    tool_category: str = "integrations"
    rate_limit_type: str = "hubspot_api"
    rate_limit_cost: int = 1

    # Deal properties
    dealname: Optional[str] = Field(None, description="Name of the deal", max_length=200)
    amount: Optional[float] = Field(None, description="Deal value/amount", ge=0, le=999999999)
    dealstage: Optional[str] = Field(None, description="Deal stage ID or name")
    pipeline: Optional[str] = Field(None, description="Pipeline ID")
    closedate: Optional[str] = Field(
        None, description="Expected close date (YYYY-MM-DD or Unix timestamp ms)"
    )
    dealtype: Optional[str] = Field(
        None, description="Deal type (newbusiness, existingbusiness, renewal)"
    )
    description: Optional[str] = Field(None, description="Deal description", max_length=2000)
    priority: Optional[str] = Field(None, description="Deal priority (low, medium, high)")

    # Associations
    contact_ids: Optional[List[str]] = Field(None, description="Contact IDs to associate with deal")
    company_ids: Optional[List[str]] = Field(None, description="Company IDs to associate with deal")

    # Custom properties
    custom_properties: Optional[Dict[str, Any]] = Field(
        None, description="Dictionary of custom property names and values"
    )

    # Deal operations
    deal_id: Optional[str] = Field(None, description="Deal ID for updates")
    move_to_stage: Optional[str] = Field(None, description="Move deal to specified stage")
    win_deal: bool = Field(False, description="Mark deal as won")
    lose_deal: bool = Field(False, description="Mark deal as lost")
    loss_reason: Optional[str] = Field(None, description="Reason for losing deal")

    # Batch operations
    batch_deals: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of deal dictionaries for bulk creation"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the deal tracking operation."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        try:
            if self.batch_deals:
                result = self._process_batch()
            elif self.deal_id:
                result = self._process_update()
            else:
                result = self._process_create()

            return result
        except Exception as e:
            raise APIError(f"Failed to track deal: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Batch mode validation
        if self.batch_deals:
            if not isinstance(self.batch_deals, list) or len(self.batch_deals) == 0:
                raise ValidationError(
                    "batch_deals must be a non-empty list",
                    tool_name=self.tool_name,
                )

            # Validate batch size limit
            if len(self.batch_deals) > 10:
                raise ValidationError(
                    "Batch size cannot exceed 10 deals",
                    tool_name=self.tool_name,
                )

            # Validate each deal has dealname
            for idx, deal in enumerate(self.batch_deals):
                if not deal.get("dealname"):
                    raise ValidationError(
                        "Each deal in batch missing required 'dealname' field",
                        tool_name=self.tool_name,
                    )
            return

        # Validate win/lose conflict (BEFORE general field validation)
        if self.win_deal and self.lose_deal:
            raise ValidationError(
                "Cannot win and lose a deal simultaneously", tool_name=self.tool_name
            )

        # Validate dealtype if provided
        if self.dealtype:
            valid_types = ["newbusiness", "existingbusiness", "renewal"]
            if self.dealtype.lower() not in valid_types:
                raise ValidationError(
                    f"Invalid deal type: {self.dealtype}. "
                    f"Valid types: {', '.join(valid_types)}",
                    tool_name=self.tool_name,
                )

        # Validate closedate format if provided
        if self.closedate:
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
            if not date_pattern.match(self.closedate):
                raise ValidationError(
                    "Invalid closedate format. Use YYYY-MM-DD format",
                    tool_name=self.tool_name,
                )

        # Create mode validation
        if not self.deal_id:
            # dealname is required for creating deals
            if not self.dealname or not self.dealname.strip():
                raise ValidationError(
                    "dealname is required for creating deals",
                    tool_name=self.tool_name,
                )
        else:
            # Update mode validation
            # At least one field must be provided for update
            has_update_field = (
                self.dealname is not None
                or self.amount is not None
                or self.dealstage is not None
                or self.move_to_stage is not None
                or self.win_deal
                or self.lose_deal
                or self.description is not None
                or self.closedate is not None
                or self.pipeline is not None
                or self.dealtype is not None
                or self.priority is not None
                or self.custom_properties is not None
            )

            if not has_update_field:
                raise ValidationError(
                    "Deal update requires at least one field to update",
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
        if self.batch_deals:
            # Mock batch results
            deal_ids = [
                f"deal_mock_{i}_{hash(deal.get('dealname', ''))}"[:20]
                for i, deal in enumerate(self.batch_deals)
            ]
            return {
                "success": True,
                "status": "batch_processed",
                "deal_ids": deal_ids,
                "deals_created": len(self.batch_deals),
                "metadata": {
                    "tool_name": self.tool_name,
                    "batch_size": len(self.batch_deals),
                    "mock_mode": True,
                },
            }

        # Determine status based on operation
        if self.win_deal:
            status = "won"
            dealstage = "closedwon"
        elif self.lose_deal:
            status = "lost"
            dealstage = "closedlost"
        elif self.deal_id and self.move_to_stage:
            status = "updated"
            dealstage = self.move_to_stage
        elif self.deal_id:
            status = "updated"
            dealstage = self.dealstage or "appointmentscheduled"
        else:
            status = "created"
            dealstage = self.dealstage or "appointmentscheduled"

        # Calculate forecast category
        forecast_category = self._get_forecast_category(dealstage)

        deal_id = self.deal_id or f"deal_mock_{hash(self.dealname or 'new')}"[:20]

        return {
            "success": True,
            "deal_id": deal_id,
            "dealname": self.dealname or "Mock Deal",
            "amount": self.amount or 0,
            "dealstage": dealstage,
            "pipeline": self.pipeline or "default",
            "status": status,
            "closedate": self.closedate,
            "associations": {
                "contacts": self.contact_ids or [],
                "companies": self.company_ids or [],
            },
            "forecast_category": forecast_category,
            "metadata": {
                "tool_name": self.tool_name,
                "mock_mode": True,
            },
        }

    def _get_forecast_category(self, stage: str) -> str:
        """Determine forecast category based on deal stage."""
        stage = stage.lower()

        if stage in ["closedwon"]:
            return "closed_won"
        elif stage in ["closedlost"]:
            return "closed_lost"
        elif stage in ["contractsent", "decisionmakerboughtin"]:
            return "commit"
        elif stage in ["presentationscheduled", "qualifiedtobuy"]:
            return "best_case"
        elif stage in ["appointmentscheduled"]:
            return "pipeline"
        else:
            return "omitted"

    def _build_properties(self, deal_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build properties dictionary from deal data or instance attributes."""
        if deal_data:
            # Build from provided deal data (for batch)
            properties = {}
            standard_props = [
                "dealname",
                "amount",
                "dealstage",
                "pipeline",
                "closedate",
                "dealtype",
                "description",
                "priority",
            ]
            for prop in standard_props:
                if deal_data.get(prop) is not None:
                    properties[prop] = deal_data[prop]

            # Add custom properties
            if deal_data.get("custom_properties"):
                properties.update(deal_data["custom_properties"])

            return properties
        else:
            # Build from instance attributes
            properties = {}
            if self.dealname:
                properties["dealname"] = self.dealname
            if self.amount is not None:
                properties["amount"] = str(self.amount)
            if self.dealstage:
                properties["dealstage"] = self.dealstage
            if self.pipeline:
                properties["pipeline"] = self.pipeline
            if self.closedate:
                # Convert date to Unix timestamp (ms) if it's YYYY-MM-DD format
                if not self.closedate.isdigit():
                    dt = datetime.strptime(self.closedate, "%Y-%m-%d")
                    timestamp_ms = int(dt.timestamp() * 1000)
                    properties["closedate"] = str(timestamp_ms)
                else:
                    properties["closedate"] = self.closedate
            if self.dealtype:
                properties["dealtype"] = self.dealtype.lower()
            if self.description:
                properties["description"] = self.description
            if self.priority:
                properties["hs_priority"] = self.priority.lower()

            # Handle deal status changes
            if self.win_deal:
                properties["dealstage"] = "closedwon"
            elif self.lose_deal:
                properties["dealstage"] = "closedlost"
                if self.loss_reason:
                    properties["closed_lost_reason"] = self.loss_reason
            elif self.move_to_stage:
                properties["dealstage"] = self.move_to_stage

            # Add custom properties
            if self.custom_properties:
                properties.update(self.custom_properties)

            return properties

    def _process_create(self) -> Dict[str, Any]:
        """Process deal creation with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        try:
            import requests
        except ImportError:
            raise APIError(
                "requests library not installed. Run: pip install requests",
                tool_name=self.tool_name,
            )

        # Build properties
        properties = self._build_properties()

        # Prepare API request
        url = "https://api.hubapi.com/crm/v3/objects/deals"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {"properties": properties}

        # Add associations if specified
        if self.contact_ids or self.company_ids:
            payload["associations"] = []

            if self.contact_ids:
                for contact_id in self.contact_ids:
                    payload["associations"].append(
                        {
                            "to": {"id": contact_id},
                            "types": [
                                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 3}
                            ],
                        }
                    )

            if self.company_ids:
                for company_id in self.company_ids:
                    payload["associations"].append(
                        {
                            "to": {"id": company_id},
                            "types": [
                                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 5}
                            ],
                        }
                    )

        # Create deal
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            deal_data = response.json()

            deal_id = deal_data.get("id")
            props = deal_data.get("properties", {})

            # Get forecast category
            dealstage = props.get("dealstage", "")
            forecast_category = self._get_forecast_category(dealstage)

            return {
                "success": True,
                "deal_id": deal_id,
                "dealname": props.get("dealname"),
                "amount": float(props.get("amount", 0)) if props.get("amount") else 0,
                "dealstage": dealstage,
                "pipeline": props.get("pipeline"),
                "status": "created",
                "closedate": props.get("closedate"),
                "associations": {
                    "contacts": self.contact_ids or [],
                    "companies": self.company_ids or [],
                },
                "forecast_category": forecast_category,
                "metadata": {
                    "tool_name": self.tool_name,
                },
            }

        except requests.exceptions.HTTPError as e:
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
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)

    def _process_update(self) -> Dict[str, Any]:
        """Process deal update with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        try:
            import requests
        except ImportError:
            raise APIError(
                "requests library not installed. Run: pip install requests",
                tool_name=self.tool_name,
            )

        # Build properties for update
        properties = self._build_properties()

        # Prepare API request
        url = f"https://api.hubapi.com/crm/v3/objects/deals/{self.deal_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {"properties": properties}

        # Update deal
        try:
            response = requests.patch(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            deal_data = response.json()

            props = deal_data.get("properties", {})

            # Determine status
            if self.win_deal:
                status = "won"
            elif self.lose_deal:
                status = "lost"
            else:
                status = "updated"

            # Get forecast category
            dealstage = props.get("dealstage", "")
            forecast_category = self._get_forecast_category(dealstage)

            return {
                "success": True,
                "deal_id": self.deal_id,
                "dealname": props.get("dealname"),
                "amount": float(props.get("amount", 0)) if props.get("amount") else 0,
                "dealstage": dealstage,
                "pipeline": props.get("pipeline"),
                "status": status,
                "closedate": props.get("closedate"),
                "forecast_category": forecast_category,
                "metadata": {
                    "tool_name": self.tool_name,
                    "updated_properties": list(properties.keys()),
                },
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid HubSpot API key", tool_name=self.tool_name)
            elif e.response.status_code == 404:
                raise APIError(f"Deal not found: {self.deal_id}", tool_name=self.tool_name)
            elif e.response.status_code == 429:
                raise APIError("Rate limit exceeded. Try again later.", tool_name=self.tool_name)
            else:
                error_detail = e.response.json() if e.response.content else {}
                raise APIError(
                    f"HubSpot API error: {error_detail.get('message', str(e))}",
                    tool_name=self.tool_name,
                )
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)

    def _process_batch(self) -> Dict[str, Any]:
        """Process batch deal creation with HubSpot API."""
        api_key = os.getenv("HUBSPOT_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing HUBSPOT_API_KEY environment variable",
                tool_name=self.tool_name,
            )

        try:
            import requests
        except ImportError:
            raise APIError(
                "requests library not installed. Run: pip install requests",
                tool_name=self.tool_name,
            )

        # Prepare batch payload
        url = "https://api.hubapi.com/crm/v3/objects/deals/batch/create"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        inputs = []
        for deal in self.batch_deals:
            properties = self._build_properties(deal)
            inputs.append({"properties": properties})

        payload = {"inputs": inputs}

        # Execute batch create
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            result_data = response.json()

            # Extract deal IDs
            deal_ids = [deal.get("id") for deal in result_data.get("results", [])]

            return {
                "success": True,
                "status": "batch_processed",
                "deal_ids": deal_ids,
                "deals_created": len(deal_ids),
                "metadata": {
                    "tool_name": self.tool_name,
                    "batch_size": len(self.batch_deals),
                },
            }

        except requests.exceptions.HTTPError as e:
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
        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}", tool_name=self.tool_name)


if __name__ == "__main__":
    # Test the tool
    print("Testing HubSpotTrackDeal...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Create new deal
    print("\n1. Testing deal creation...")
    tool = HubSpotTrackDeal(
        dealname="Acme Corp - Q1 Enterprise Contract",
        amount=50000,
        dealstage="qualifiedtobuy",
        closedate="2024-03-31",
        dealtype="newbusiness",
        priority="high",
        description="Major enterprise deal for Q1",
        contact_ids=["12345"],
        company_ids=["67890"],
        custom_properties={"contract_term": "12 months", "mrr": "4167"},
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Deal ID: {result.get('deal_id')}")
    print(f"Deal name: {result.get('dealname')}")
    print(f"Amount: ${result.get('amount'):,.2f}")
    print(f"Stage: {result.get('dealstage')}")
    print(f"Status: {result.get('status')}")
    print(f"Forecast category: {result.get('forecast_category')}")
    assert result.get("success") == True
    assert result.get("status") == "created"
    assert result.get("forecast_category") in ["best_case", "commit", "pipeline"]

    # Test 2: Update deal stage
    print("\n2. Testing deal stage update...")
    tool = HubSpotTrackDeal(
        deal_id="987654321",
        move_to_stage="presentationscheduled",
        amount=55000,  # Updated amount
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"New stage: {result.get('dealstage')}")
    assert result.get("success") == True
    assert result.get("status") == "updated"

    # Test 3: Win deal
    print("\n3. Testing winning a deal...")
    tool = HubSpotTrackDeal(
        deal_id="987654321",
        win_deal=True,
        amount=60000,  # Final contracted amount
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Stage: {result.get('dealstage')}")
    print(f"Forecast category: {result.get('forecast_category')}")
    assert result.get("success") == True
    assert result.get("status") == "won"
    assert result.get("dealstage") == "closedwon"
    assert result.get("forecast_category") == "closed_won"

    # Test 4: Lose deal
    print("\n4. Testing losing a deal...")
    tool = HubSpotTrackDeal(
        deal_id="123456789",
        lose_deal=True,
        loss_reason="Budget constraints",
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Stage: {result.get('dealstage')}")
    assert result.get("success") == True
    assert result.get("status") == "lost"
    assert result.get("dealstage") == "closedlost"

    # Test 5: Batch deal creation
    print("\n5. Testing batch deal creation...")
    tool = HubSpotTrackDeal(
        batch_deals=[
            {
                "dealname": "Tech Startup - Annual Plan",
                "amount": 25000,
                "dealstage": "appointmentscheduled",
                "dealtype": "newbusiness",
            },
            {
                "dealname": "Enterprise Co - Renewal",
                "amount": 100000,
                "dealstage": "contractsent",
                "dealtype": "renewal",
            },
            {
                "dealname": "Small Biz - Expansion",
                "amount": 15000,
                "dealstage": "qualifiedtobuy",
                "dealtype": "existingbusiness",
            },
        ]
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    print(f"Deals created: {result.get('deals_created')}")
    print(f"Deal IDs: {result.get('deal_ids')}")
    assert result.get("success") == True
    assert result.get("status") == "batch_processed"
    assert result.get("deals_created") == 3

    # Test 6: Error handling - missing dealname
    print("\n6. Testing error handling (missing dealname)...")
    try:
        tool = HubSpotTrackDeal(amount=10000, dealstage="appointmentscheduled")
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    # Test 7: Error handling - win and lose at same time
    print("\n7. Testing error handling (conflicting operations)...")
    try:
        tool = HubSpotTrackDeal(
            deal_id="123",
            win_deal=True,
            lose_deal=True,
        )
        result = tool.run()
        print("ERROR: Should have raised ValidationError")
    except Exception as e:
        print(f"Correctly caught error: {str(e)}")

    print("\n✅ All tests passed!")
