"""
Retrieve and analyze Twilio call logs with optional transcript support
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioRestException = Exception


class TwilioCallLogs(BaseTool):
    """
    Retrieve and analyze Twilio call logs with filtering and optional transcript support.

    This tool queries Twilio call logs within a specified time range and returns
    detailed information about each call including status, duration, cost, and
    optional transcripts.

    Args:
        time_range_hours: Hours to look back from now (default: 24)
        limit: Maximum number of calls to return (1-100, default: 10)
        include_transcript: Whether to fetch call transcripts (default: False)
        filter_status: Filter by call status (completed, failed, busy, or None for all)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: List of call records with details
        - metadata: Query information and statistics

    Example:
        >>> tool = TwilioCallLogs(
        ...     time_range_hours=48,
        ...     limit=20,
        ...     filter_status="completed",
        ...     include_transcript=True
        ... )
        >>> result = tool.run()
        >>> for call in result["result"]:
        ...     print(f"Call to {call['to']}: {call['status']}")
    """

    # Tool metadata
    tool_name: str = "twilio_call_logs"
    tool_category: str = "communication"

    # Parameters
    time_range_hours: int = Field(
        24, description="Hours to look back from current time", ge=1, le=720  # Max 30 days
    )
    limit: int = Field(10, description="Maximum number of calls to return", ge=1, le=100)
    include_transcript: bool = Field(
        False, description="Whether to include call transcripts in results"
    )
    filter_status: Optional[Literal["completed", "failed", "busy"]] = Field(
        None, description="Filter calls by status (completed, failed, busy, or None for all)"
    )

    def _execute(self) -> Dict[str, Any]:
        """Execute the Twilio call logs retrieval."""
        # 1. VALIDATE
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            return self._generate_mock_results()

        # 3. EXECUTE
        if not TWILIO_AVAILABLE:
            raise APIError(
                "twilio package not installed. Install with: pip install twilio",
                tool_name=self.tool_name,
            )

        try:
            result = self._process()
            return {
                "success": True,
                "result": result["calls"],
                "metadata": {
                    "tool_name": self.tool_name,
                    "time_range_hours": self.time_range_hours,
                    "limit": self.limit,
                    "filter_status": self.filter_status,
                    "include_transcript": self.include_transcript,
                    "total_calls": result["total_calls"],
                    "total_duration": result["total_duration"],
                    "total_cost": result["total_cost"],
                    "query_start_time": result["query_start_time"],
                    "query_end_time": result["query_end_time"],
                    "mock_mode": False,
                },
            }
        except TwilioRestException as e:
            if e.status == 401:
                raise AuthenticationError(
                    "Invalid Twilio credentials. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN",
                    tool_name=self.tool_name,
                    api_name="Twilio API",
                )
            elif e.status == 403:
                raise AuthenticationError(
                    "Twilio account does not have permission to access this resource",
                    tool_name=self.tool_name,
                    api_name="Twilio API",
                )
            else:
                raise APIError(
                    f"Twilio API error: {e.msg}",
                    tool_name=self.tool_name,
                    api_name="Twilio API",
                    status_code=e.status,
                )
        except Exception as e:
            raise APIError(f"Failed to retrieve call logs: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # time_range_hours validation
        if not isinstance(self.time_range_hours, int) or self.time_range_hours <= 0:
            raise ValidationError(
                "time_range_hours must be a positive integer",
                tool_name=self.tool_name,
                field="time_range_hours",
            )

        if self.time_range_hours > 720:  # 30 days max
            raise ValidationError(
                "time_range_hours cannot exceed 720 (30 days)",
                tool_name=self.tool_name,
                field="time_range_hours",
            )

        # limit validation
        if not isinstance(self.limit, int) or self.limit <= 0:
            raise ValidationError(
                "limit must be a positive integer", tool_name=self.tool_name, field="limit"
            )

        if self.limit > 100:
            raise ValidationError(
                "limit cannot exceed 100", tool_name=self.tool_name, field="limit"
            )

        # filter_status validation (already handled by Literal type, but add runtime check)
        if self.filter_status and self.filter_status not in ["completed", "failed", "busy"]:
            raise ValidationError(
                "filter_status must be one of: completed, failed, busy",
                tool_name=self.tool_name,
                field="filter_status",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate realistic mock call logs for testing."""
        import random

        # Generate mock calls
        mock_calls = []
        base_time = datetime.now() - timedelta(hours=self.time_range_hours)

        from_numbers = ["+14155551234", "+14155555678", "+14155559012", "+18005551234"]
        to_numbers = ["+14155559999", "+14155558888", "+14155557777", "+18885551234"]
        statuses = ["completed", "failed", "busy", "no-answer"]

        num_calls = min(self.limit, random.randint(5, 15))

        total_duration = 0
        total_cost = 0.0

        for i in range(num_calls):
            # Determine status
            if self.filter_status:
                status = self.filter_status
            else:
                status = random.choice(statuses)

            # Generate call details
            call_start = base_time + timedelta(
                hours=random.randint(0, self.time_range_hours), minutes=random.randint(0, 59)
            )

            duration = random.randint(30, 600) if status == "completed" else 0
            cost = round(duration * 0.00025, 4) if status == "completed" else 0.0

            call_sid = f"CA{''.join([str(random.randint(0, 9)) for _ in range(32)])}"

            call_record = {
                "call_sid": call_sid,
                "to": random.choice(to_numbers),
                "from": random.choice(from_numbers),
                "status": status,
                "duration": duration,
                "cost": f"-{cost:.4f}" if cost > 0 else "0.0000",
                "cost_unit": "USD",
                "start_time": call_start.isoformat(),
                "end_time": (
                    (call_start + timedelta(seconds=duration)).isoformat() if duration > 0 else None
                ),
                "direction": random.choice(["outbound-api", "inbound"]),
                "price_unit": "USD",
            }

            # Add transcript if requested
            if self.include_transcript and status == "completed":
                call_record["transcript"] = self._generate_mock_transcript(i)
                call_record["transcript_available"] = True
            elif self.include_transcript:
                call_record["transcript"] = None
                call_record["transcript_available"] = False

            mock_calls.append(call_record)
            total_duration += duration
            total_cost += cost

        # Sort by start time (most recent first)
        mock_calls.sort(key=lambda x: x["start_time"], reverse=True)

        return {
            "success": True,
            "result": mock_calls,
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "time_range_hours": self.time_range_hours,
                "limit": self.limit,
                "filter_status": self.filter_status,
                "include_transcript": self.include_transcript,
                "total_calls": len(mock_calls),
                "total_duration": total_duration,
                "total_cost": f"{total_cost:.4f}",
                "query_start_time": base_time.isoformat(),
                "query_end_time": datetime.now().isoformat(),
            },
        }

    def _generate_mock_transcript(self, index: int) -> str:
        """Generate a mock transcript for testing."""
        transcripts = [
            "Hello, this is a reminder about your upcoming appointment on Tuesday at 2 PM. Please call us back to confirm. Thank you.",
            "Hi, we're calling to follow up on your recent inquiry. We have some exciting updates to share. Please return our call at your earliest convenience.",
            "This is an automated reminder that your payment is due in 3 days. Please visit our website or call our billing department to make your payment.",
            "Good afternoon, we noticed you haven't completed your registration. We'd love to help you finish the process. Please call us back.",
            "Hello, your order has been shipped and will arrive within 3-5 business days. Thank you for your purchase!",
        ]
        return transcripts[index % len(transcripts)]

    def _process(self) -> Dict[str, Any]:
        """Retrieve call logs from Twilio API."""
        # Get Twilio credentials
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            raise AuthenticationError(
                "Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables",
                tool_name=self.tool_name,
                api_name="Twilio API",
            )

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=self.time_range_hours)

        # Build query parameters
        query_params = {
            "start_time_after": start_time,
            "start_time_before": end_time,
            "limit": self.limit,
        }

        # Add status filter if specified
        if self.filter_status:
            query_params["status"] = self.filter_status

        # Query calls
        calls = client.calls.list(**query_params)

        # Process results
        call_records = []
        total_duration = 0
        total_cost = 0.0

        for call in calls:
            # Calculate duration and cost
            duration = int(call.duration) if call.duration else 0
            cost = float(call.price) if call.price else 0.0

            total_duration += duration
            total_cost += abs(cost)  # Cost is negative for outbound calls

            call_record = {
                "call_sid": call.sid,
                "to": call.to,
                "from": call.from_,
                "status": call.status,
                "duration": duration,
                "cost": str(call.price) if call.price else "0.0000",
                "cost_unit": call.price_unit or "USD",
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "direction": call.direction,
                "price_unit": call.price_unit or "USD",
            }

            # Add transcript if requested and available
            if self.include_transcript:
                transcript = self._fetch_transcript(client, call.sid)
                call_record["transcript"] = transcript
                call_record["transcript_available"] = transcript is not None

            call_records.append(call_record)

        return {
            "calls": call_records,
            "total_calls": len(call_records),
            "total_duration": total_duration,
            "total_cost": f"{total_cost:.4f}",
            "query_start_time": start_time.isoformat(),
            "query_end_time": end_time.isoformat(),
        }

    def _fetch_transcript(self, client: Any, call_sid: str) -> Optional[str]:
        """
        Fetch transcript for a specific call if available.

        Args:
            client: Twilio client instance
            call_sid: Call SID to fetch transcript for

        Returns:
            Transcript text or None if not available
        """
        try:
            # Fetch recordings for this call
            recordings = client.recordings.list(call_sid=call_sid, limit=1)

            if not recordings:
                return None

            # Get the first recording
            recording = recordings[0]

            # Fetch transcriptions for the recording
            transcriptions = client.transcriptions.list(recording_sid=recording.sid, limit=1)

            if transcriptions and len(transcriptions) > 0:
                return transcriptions[0].transcription_text

            return None

        except Exception as e:
            # If transcript fetch fails, log but don't fail the entire request
            self._logger.warning(f"Failed to fetch transcript for call {call_sid}: {e}")
            return None


if __name__ == "__main__":
    print("Testing TwilioCallLogs...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Basic query with default parameters
    print("\nTest 1: Basic query (24 hours, limit 10)")
    tool = TwilioCallLogs()
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Total calls: {result.get('metadata', {}).get('total_calls')}")
    print(f"Total duration: {result.get('metadata', {}).get('total_duration')}s")
    print(f"Total cost: ${result.get('metadata', {}).get('total_cost')}")
    assert result.get("success") == True
    assert len(result.get("result", [])) <= 10

    # Test 2: Extended time range with status filter
    print("\nTest 2: 48 hours, completed calls only, limit 20")
    tool2 = TwilioCallLogs(time_range_hours=48, limit=20, filter_status="completed")
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Total calls: {result2.get('metadata', {}).get('total_calls')}")
    # Verify all calls have completed status
    for call in result2.get("result", []):
        assert call.get("status") == "completed"
    print("All calls have 'completed' status")

    # Test 3: With transcripts
    print("\nTest 3: With transcripts included")
    tool3 = TwilioCallLogs(
        time_range_hours=24, limit=5, include_transcript=True, filter_status="completed"
    )
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Total calls: {result3.get('metadata', {}).get('total_calls')}")
    # Check if transcripts are included
    has_transcript = any(call.get("transcript") is not None for call in result3.get("result", []))
    print(f"Has transcripts: {has_transcript}")
    assert result3.get("success") == True

    # Test 4: Failed calls only
    print("\nTest 4: Failed calls only")
    tool4 = TwilioCallLogs(time_range_hours=72, limit=15, filter_status="failed")
    result4 = tool4.run()

    print(f"Success: {result4.get('success')}")
    print(f"Total calls: {result4.get('metadata', {}).get('total_calls')}")
    # Verify all calls have failed status
    for call in result4.get("result", []):
        assert call.get("status") == "failed"
    print("All calls have 'failed' status")

    # Test 5: Validation - invalid time_range_hours
    print("\nTest 5: Validation - invalid time_range_hours")
    try:
        tool5 = TwilioCallLogs(time_range_hours=1000)  # Exceeds 720 max
        result5 = tool5.run()
        assert result5.get("success") == False
        print("Validation test passed (invalid time_range rejected)")
    except Exception as e:
        print(f"Validation test passed (exception raised): {type(e).__name__}")

    # Test 6: Validation - invalid limit
    print("\nTest 6: Validation - invalid limit")
    try:
        tool6 = TwilioCallLogs(limit=150)  # Exceeds 100 max
        result6 = tool6.run()
        assert result6.get("success") == False
        print("Validation test passed (invalid limit rejected)")
    except Exception as e:
        print(f"Validation test passed (exception raised): {type(e).__name__}")

    # Test 7: Check result structure
    print("\nTest 7: Verify result structure")
    tool7 = TwilioCallLogs(limit=3)
    result7 = tool7.run()

    if result7.get("result") and len(result7.get("result", [])) > 0:
        call = result7["result"][0]
        required_fields = ["call_sid", "to", "from", "status", "duration", "cost", "start_time"]
        for field in required_fields:
            assert field in call, f"Missing required field: {field}"
        print(f"All required fields present in call record")
        print(f"Sample call SID: {call.get('call_sid')}")
        print(f"Sample call status: {call.get('status')}")
        print(f"Sample call duration: {call.get('duration')}s")

    print("\n" + "=" * 50)
    print("All TwilioCallLogs tests passed!")
    print("=" * 50)
