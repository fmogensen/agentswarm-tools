"""
Tests for HubSpot Track Deal Tool

Comprehensive test suite covering deal creation, updates, pipeline management,
stage transitions, forecasting, and batch operations.
"""

import os
from unittest.mock import Mock, patch

import pytest

from shared.errors import APIError, ValidationError
from tools.integrations.hubspot.hubspot_track_deal import HubSpotTrackDeal


class TestHubSpotTrackDeal:
    """Test suite for HubSpotTrackDeal tool."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        os.environ["USE_MOCK_APIS"] = "true"
        yield
        if "USE_MOCK_APIS" in os.environ:
            del os.environ["USE_MOCK_APIS"]

    def test_create_deal(self):
        """Test creating a new deal with standard fields."""
        tool = HubSpotTrackDeal(
            dealname="Acme Corp - Q1 Contract",
            amount=50000,
            dealstage="qualifiedtobuy",
            closedate="2024-03-31",
            dealtype="newbusiness",
            priority="high",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "created"
        assert result["dealname"] == "Acme Corp - Q1 Contract"
        assert result["amount"] == 50000
        assert "deal_id" in result
        assert "forecast_category" in result

    def test_deal_with_associations(self):
        """Test creating deal with contact and company associations."""
        tool = HubSpotTrackDeal(
            dealname="Associated Deal",
            amount=25000,
            contact_ids=["123", "456"],
            company_ids=["789"],
        )
        result = tool.run()

        assert result["success"] == True
        assert len(result["associations"]["contacts"]) == 2
        assert len(result["associations"]["companies"]) == 1

    def test_update_deal_stage(self):
        """Test updating deal stage."""
        tool = HubSpotTrackDeal(
            deal_id="987654",
            move_to_stage="presentationscheduled",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "updated"
        assert result["dealstage"] == "presentationscheduled"

    def test_win_deal(self):
        """Test marking deal as won."""
        tool = HubSpotTrackDeal(
            deal_id="123456",
            win_deal=True,
            amount=60000,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "won"
        assert result["dealstage"] == "closedwon"
        assert result["forecast_category"] == "closed_won"

    def test_lose_deal(self):
        """Test marking deal as lost with reason."""
        tool = HubSpotTrackDeal(
            deal_id="789012",
            lose_deal=True,
            loss_reason="Budget constraints",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "lost"
        assert result["dealstage"] == "closedlost"
        assert result["forecast_category"] == "closed_lost"

    def test_forecast_category_pipeline(self):
        """Test forecast category for pipeline stage."""
        tool = HubSpotTrackDeal(
            dealname="Pipeline Deal",
            amount=10000,
            dealstage="appointmentscheduled",
        )
        result = tool.run()

        assert result["forecast_category"] == "pipeline"

    def test_forecast_category_best_case(self):
        """Test forecast category for best case stage."""
        tool = HubSpotTrackDeal(
            dealname="Best Case Deal",
            amount=20000,
            dealstage="qualifiedtobuy",
        )
        result = tool.run()

        assert result["forecast_category"] == "best_case"

    def test_forecast_category_commit(self):
        """Test forecast category for commit stage."""
        tool = HubSpotTrackDeal(
            dealname="Commit Deal",
            amount=30000,
            dealstage="contractsent",
        )
        result = tool.run()

        assert result["forecast_category"] == "commit"

    def test_batch_deal_creation(self):
        """Test creating multiple deals in batch."""
        batch_deals = [
            {
                "dealname": "Deal 1",
                "amount": 10000,
                "dealstage": "appointmentscheduled",
            },
            {
                "dealname": "Deal 2",
                "amount": 20000,
                "dealstage": "qualifiedtobuy",
            },
            {
                "dealname": "Deal 3",
                "amount": 30000,
                "dealstage": "contractsent",
            },
        ]

        tool = HubSpotTrackDeal(batch_deals=batch_deals)
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "batch_processed"
        assert result["deals_created"] == 3
        assert len(result["deal_ids"]) == 3

    def test_deal_with_custom_properties(self):
        """Test creating deal with custom properties."""
        tool = HubSpotTrackDeal(
            dealname="Custom Deal",
            amount=15000,
            custom_properties={
                "contract_term": "12 months",
                "mrr": "1250",
                "implementation_fee": "5000",
            },
        )
        result = tool.run()

        assert result["success"] == True

    def test_dealtype_validation(self):
        """Test validation of deal type."""
        # Valid deal types
        for dealtype in ["newbusiness", "existingbusiness", "renewal"]:
            tool = HubSpotTrackDeal(
                dealname="Test Deal",
                amount=10000,
                dealtype=dealtype,
            )
            result = tool.run()
            assert result["success"] == True

        # Invalid deal type
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(
                dealname="Test Deal",
                amount=10000,
                dealtype="invalid_type",
            )
            tool.run()
        assert "Invalid deal type" in str(exc_info.value)

    def test_priority_validation(self):
        """Test validation of priority."""
        for priority in ["low", "medium", "high"]:
            tool = HubSpotTrackDeal(
                dealname="Test Deal",
                amount=10000,
                priority=priority,
            )
            result = tool.run()
            assert result["success"] == True

    def test_closedate_format_validation(self):
        """Test validation of close date format."""
        # Valid YYYY-MM-DD format
        tool = HubSpotTrackDeal(
            dealname="Test Deal",
            amount=10000,
            closedate="2024-12-31",
        )
        result = tool.run()
        assert result["success"] == True

        # Invalid format
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(
                dealname="Test Deal",
                amount=10000,
                closedate="invalid-date",
            )
            tool.run()
        assert "YYYY-MM-DD format" in str(exc_info.value)

    def test_missing_dealname_error(self):
        """Test that dealname is required for creation."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(
                amount=10000,
                dealstage="appointmentscheduled",
            )
            tool.run()
        assert "dealname is required" in str(exc_info.value)

    def test_update_requires_fields(self):
        """Test that update operation requires fields to update."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(deal_id="123")
            tool.run()
        assert "at least one field to update" in str(exc_info.value)

    def test_cannot_win_and_lose_simultaneously(self):
        """Test that deal cannot be won and lost at same time."""
        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(
                deal_id="123",
                win_deal=True,
                lose_deal=True,
            )
            tool.run()
        assert "Cannot win and lose" in str(exc_info.value)

    def test_batch_size_limit(self):
        """Test batch size cannot exceed 10 deals."""
        large_batch = [{"dealname": f"Deal {i}", "amount": 1000 * i} for i in range(11)]

        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(batch_deals=large_batch)
            tool.run()
        assert "cannot exceed 10" in str(exc_info.value)

    def test_batch_deal_missing_dealname(self):
        """Test that each batch deal must have dealname."""
        batch_deals = [
            {"dealname": "Deal 1", "amount": 10000},
            {"amount": 20000},  # Missing dealname
        ]

        with pytest.raises(Exception) as exc_info:
            tool = HubSpotTrackDeal(batch_deals=batch_deals)
            tool.run()
        assert "missing required 'dealname' field" in str(exc_info.value)

    def test_update_deal_amount(self):
        """Test updating deal amount."""
        tool = HubSpotTrackDeal(
            deal_id="123456",
            amount=75000,
        )
        result = tool.run()

        assert result["success"] == True
        assert result["status"] == "updated"
        assert result["amount"] == 75000

    def test_deal_with_description(self):
        """Test creating deal with description."""
        tool = HubSpotTrackDeal(
            dealname="Described Deal",
            amount=40000,
            description="This is a high-value enterprise deal with multiple stakeholders.",
        )
        result = tool.run()

        assert result["success"] == True

    def test_tool_metadata(self):
        """Test tool metadata."""
        tool = HubSpotTrackDeal(
            dealname="Test",
            amount=10000,
        )

        assert tool.tool_name == "hubspot_track_deal"
        assert tool.tool_category == "integrations"
        assert tool.rate_limit_type == "hubspot_api"

    @patch("tools.integrations.hubspot.hubspot_track_deal.requests")
    def test_api_call_structure(self, mock_requests):
        """Test API call structure (mocked)."""
        os.environ.pop("USE_MOCK_APIS", None)
        os.environ["HUBSPOT_API_KEY"] = "test_key"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "deal123",
            "properties": {
                "dealname": "Test Deal",
                "amount": "10000",
                "dealstage": "appointmentscheduled",
            },
        }
        mock_requests.post.return_value = mock_response

        tool = HubSpotTrackDeal(
            dealname="Test Deal",
            amount=10000,
        )
        result = tool.run()

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert "https://api.hubapi.com/crm/v3/objects/deals" in call_args[0][0]

        os.environ.pop("HUBSPOT_API_KEY")

    def test_pipeline_specification(self):
        """Test specifying pipeline ID."""
        tool = HubSpotTrackDeal(
            dealname="Pipeline Deal",
            amount=15000,
            pipeline="custom_pipeline_123",
        )
        result = tool.run()

        assert result["success"] == True
        assert result["pipeline"] == "custom_pipeline_123"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
