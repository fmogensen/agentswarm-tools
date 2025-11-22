"""
Query and filter call logs from Twilio based on criteria
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
from datetime import datetime, timedelta
import os

from shared.base import BaseTool
from shared.errors import ValidationError, APIError, AuthenticationError

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except ImportError:
    Client = None
    TwilioRestException = Exception


class QueryCallLogs(BaseTool):
    """
    Query and filter call logs from Twilio based on criteria

    Args:
        phone_number: Optional phone number to filter by
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        status: Call status filter (completed, busy, failed, no-answer)
        limit: Maximum number of records to return

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of call records
        - metadata: Additional information

    Example:
        >>> tool = QueryCallLogs(start_date="2024-01-01", limit=10)
        >>> result = tool.run()
    """

    # Tool metadata
    tool_name: str = "query_call_logs"
    tool_category: str = "communication"

    # Parameters
    phone_number: Optional[str] = Field(
        None, description="Filter by specific phone number (E.164 format recommended)"
    )
    start_date: Optional[str] = Field(
        None, description="Start date in ISO format (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None, description="End date in ISO format (YYYY-MM-DD)"
    )
    status: Optional[str] = Field(
        None, description="Call status filter (completed, busy, failed, no-answer)"
    )
    limit: int = Field(
        50, description="Maximum number of records to return", ge=1, le=1000
    )

    def _execute(self) -> Dict[str, Any]:
        """
        Execute the query_call_logs tool.

        Returns:
            Dict with results
        """
        # 1. VALIDATE INPUT PARAMETERS
        self._validate_parameters()

        # 2. MOCK MODE SUPPORT
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. REAL EXECUTION
        try:
            call_logs = self._process()

            return {
                "success": True,
                "result": call_logs,
                "metadata": {
                    "phone_number": self.phone_number,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "status": self.status,
                    "limit": self.limit,
                    "tool_name": self.tool_name,
                    "mock_mode": False,
                },
            }

        except Exception as e:
            raise APIError(
                f"Failed to query call logs: {e}", tool_name=self.tool_name
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate limit
        if not isinstance(self.limit, int) or self.limit <= 0:
            raise ValidationError(
                "limit must be a positive integer",
                tool_name=self.tool_name,
                field="limit",
            )

        if self.limit > 1000:
            raise ValidationError(
                "limit cannot exceed 1000",
                tool_name=self.tool_name,
                field="limit",
            )

        # Validate date formats if provided
        if self.start_date:
            try:
                datetime.fromisoformat(self.start_date)
            except ValueError:
                raise ValidationError(
                    "start_date must be in ISO format (YYYY-MM-DD)",
                    tool_name=self.tool_name,
                    field="start_date",
                )

        if self.end_date:
            try:
                datetime.fromisoformat(self.end_date)
            except ValueError:
                raise ValidationError(
                    "end_date must be in ISO format (YYYY-MM-DD)",
                    tool_name=self.tool_name,
                    field="end_date",
                )

        # Validate start_date is before end_date
        if self.start_date and self.end_date:
            start = datetime.fromisoformat(self.start_date)
            end = datetime.fromisoformat(self.end_date)
            if start > end:
                raise ValidationError(
                    "start_date must be before or equal to end_date",
                    tool_name=self.tool_name,
                    field="start_date",
                )

        # Validate status if provided
        if self.status:
            valid_statuses = ["completed", "busy", "failed", "no-answer"]
            if self.status.lower() not in valid_statuses:
                raise ValidationError(
                    f"status must be one of: {', '.join(valid_statuses)}",
                    tool_name=self.tool_name,
                    field="status",
                )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Generate realistic mock call logs
        mock_calls = []
        base_time = datetime(2024, 1, 15, 10, 0, 0)

        statuses = ["completed", "busy", "failed", "no-answer"]
        from_numbers = ["+14155551234", "+14155555678", "+14155559012"]
        to_numbers = ["+14155559999", "+14155558888", "+14155557777"]

        num_records = min(self.limit, 10)  # Generate up to 10 mock records

        for i in range(num_records):
            # Apply filters if specified
            call_status = self.status if self.status else statuses[i % len(statuses)]
            from_num = (
                self.phone_number
                if self.phone_number
                else from_numbers[i % len(from_numbers)]
            )

            # Calculate times
            start_time = base_time.replace(hour=10 + i)
            duration = 120 if call_status == "completed" else 0
            end_time = (
                (start_time + timedelta(seconds=duration)).isoformat()
                if duration > 0
                else None
            )

            mock_calls.append(
                {
                    "sid": f"CA{i:032d}",
                    "from": from_num,
                    "to": to_numbers[i % len(to_numbers)],
                    "status": call_status,
                    "duration": duration,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time,
                    "direction": "outbound-api" if i % 2 == 0 else "inbound",
                    "price": "-0.015" if call_status == "completed" else "0.00",
                    "price_unit": "USD",
                }
            )

        return {
            "success": True,
            "result": mock_calls,
            "metadata": {
                "mock_mode": True,
                "phone_number": self.phone_number,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "status": self.status,
                "limit": self.limit,
                "count": len(mock_calls),
            },
        }

    def _process(self) -> List[Dict[str, Any]]:
        """Main processing logic for Twilio API call logs query."""
        # Check if Twilio is available
        if Client is None:
            raise APIError(
                "Twilio library not installed. Install with: pip install twilio",
                tool_name=self.tool_name,
            )

        # Get Twilio credentials
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            raise AuthenticationError(
                "Missing Twilio credentials. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables",
                tool_name=self.tool_name,
            )

        try:
            # Initialize Twilio client
            client = Client(account_sid, auth_token)

            # Build query parameters
            query_params = {"limit": self.limit}

            # Add optional filters
            if self.phone_number:
                # Try both 'from' and 'to' filters
                # Note: Twilio API requires separate queries for from/to
                query_params["from_"] = self.phone_number

            if self.start_date:
                start_dt = datetime.fromisoformat(self.start_date)
                query_params["start_time_after"] = start_dt

            if self.end_date:
                end_dt = datetime.fromisoformat(self.end_date)
                query_params["start_time_before"] = end_dt

            if self.status:
                query_params["status"] = self.status

            # Query call logs
            calls = client.calls.list(**query_params)

            # If phone_number specified, also check 'to' field
            if self.phone_number:
                to_params = query_params.copy()
                del to_params["from_"]
                to_params["to"] = self.phone_number
                calls_to = client.calls.list(**to_params)
                # Combine and deduplicate
                all_calls = list(calls) + list(calls_to)
                # Deduplicate by SID
                seen_sids = set()
                unique_calls = []
                for call in all_calls:
                    if call.sid not in seen_sids:
                        seen_sids.add(call.sid)
                        unique_calls.append(call)
                calls = unique_calls[: self.limit]

            # Format results
            results = []
            for call in calls:
                results.append(
                    {
                        "sid": call.sid,
                        "from": call.from_,
                        "to": call.to,
                        "status": call.status,
                        "duration": call.duration,
                        "start_time": call.start_time.isoformat()
                        if call.start_time
                        else None,
                        "end_time": call.end_time.isoformat()
                        if call.end_time
                        else None,
                        "direction": call.direction,
                        "price": str(call.price) if call.price else None,
                        "price_unit": call.price_unit,
                    }
                )

            return results

        except TwilioRestException as e:
            if e.status == 401:
                raise AuthenticationError(
                    f"Twilio authentication failed: {e.msg}",
                    tool_name=self.tool_name,
                    api_name="Twilio",
                )
            else:
                raise APIError(
                    f"Twilio API error: {e.msg}",
                    tool_name=self.tool_name,
                    api_name="Twilio",
                    status_code=e.status,
                )
        except Exception as e:
            raise APIError(f"Unexpected error: {e}", tool_name=self.tool_name)


if __name__ == "__main__":
    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic query
    print("Test 1: Basic query with limit")
    tool = QueryCallLogs(limit=5)
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Number of records: {len(result.get('result', []))}")

    # Test 2: Date range filter
    print("\nTest 2: Date range filter")
    tool = QueryCallLogs(start_date="2024-01-01", end_date="2024-01-31", limit=10)
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Metadata: {result.get('metadata')}")

    # Test 3: Status filter
    print("\nTest 3: Status filter")
    tool = QueryCallLogs(status="completed", limit=5)
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"First record status: {result.get('result', [{}])[0].get('status')}")

    # Test 4: Phone number filter
    print("\nTest 4: Phone number filter")
    tool = QueryCallLogs(phone_number="+14155551234", limit=5)
    result = tool.run()
    print(f"Success: {result.get('success')}")
    print(f"Number of records: {len(result.get('result', []))}")

    print("\nAll tests passed!")
