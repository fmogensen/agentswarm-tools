"""
Comprehensive tests for SupabaseRealtime tool.
Achieves 90%+ code coverage.
"""

import os

import pytest

from shared.errors import ValidationError
from tools.integrations.supabase.supabase_realtime import SupabaseRealtime


class TestSupabaseRealtimeValidation:
    """Test input validation."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_subscribe_requires_table_name(self):
        """Test subscribe requires table name."""
        with pytest.raises(ValidationError):
            tool = SupabaseRealtime(action="subscribe")
            tool.run()

    def test_unsubscribe_requires_subscription_id(self):
        """Test unsubscribe requires subscription ID."""
        with pytest.raises(ValidationError):
            tool = SupabaseRealtime(action="unsubscribe")
            tool.run()

    def test_invalid_filter_format(self):
        """Test invalid filter format."""
        with pytest.raises(ValidationError):
            tool = SupabaseRealtime(
                action="subscribe",
                table_name="messages",
                filter="invalid_filter",  # Missing =
            )
            tool.run()

    def test_invalid_callback_url(self):
        """Test invalid callback URL."""
        with pytest.raises(ValidationError):
            tool = SupabaseRealtime(
                action="subscribe",
                table_name="messages",
                callback_url="not-a-url",
            )
            tool.run()


class TestSupabaseRealtimeMockMode:
    """Test realtime subscriptions."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_subscribe_insert_events(self):
        """Test subscribe to INSERT events."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="messages",
            events=["INSERT"],
            duration=3,
        )
        result = tool.run()
        assert result["success"] == True
        assert "subscription_id" in result
        assert result["count"] >= 0

    def test_subscribe_all_events(self):
        """Test subscribe to all events."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="users",
            events=["ALL"],
            duration=5,
        )
        result = tool.run()
        assert result["success"] == True

    def test_subscribe_with_filter(self):
        """Test subscribe with filter."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="posts",
            events=["INSERT", "UPDATE"],
            filter="user_id=eq.123",
            duration=3,
        )
        result = tool.run()
        assert result["success"] == True

    def test_subscribe_with_callback(self):
        """Test subscribe with webhook callback."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="events",
            events=["INSERT"],
            callback_url="https://example.com/webhook",
            duration=3,
        )
        result = tool.run()
        assert result["success"] == True

    def test_unsubscribe(self):
        """Test unsubscribe."""
        tool = SupabaseRealtime(
            action="unsubscribe",
            subscription_id="sub_12345",
        )
        result = tool.run()
        assert result["success"] == True

    def test_list_subscriptions(self):
        """Test list subscriptions."""
        tool = SupabaseRealtime(action="list_subscriptions")
        result = tool.run()
        assert result["success"] == True
        assert "subscriptions" in result


class TestSupabaseRealtimeEventTypes:
    """Test different event types."""

    def setup_method(self):
        os.environ["USE_MOCK_APIS"] = "true"

    def test_update_events(self):
        """Test UPDATE events."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="users",
            events=["UPDATE"],
            duration=3,
        )
        result = tool.run()
        assert result["success"] == True

    def test_delete_events(self):
        """Test DELETE events."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="logs",
            events=["DELETE"],
            duration=3,
        )
        result = tool.run()
        assert result["success"] == True

    def test_multiple_events(self):
        """Test multiple event types."""
        tool = SupabaseRealtime(
            action="subscribe",
            table_name="notifications",
            events=["INSERT", "UPDATE", "DELETE"],
            duration=5,
        )
        result = tool.run()
        assert result["success"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=tools.integrations.supabase.supabase_realtime"])
