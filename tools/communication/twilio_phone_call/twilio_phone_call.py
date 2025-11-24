"""
Make AI-assisted phone calls via Twilio API with advanced call management
"""

import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from pydantic import Field, field_validator

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class TwilioPhoneCall(BaseTool):
    """
    Make AI-assisted phone calls via Twilio API with advanced call management.

    This tool enables automated phone calls with customizable AI voice instructions,
    call tracking, and cost estimation. It supports multiple voice styles and
    provides comprehensive call metadata including tracking URLs and estimated costs.

    Args:
        recipient_name: Name of the person receiving the call (for logging/tracking)
        phone_number: Phone number to call in E.164 format (e.g., +15551234567)
        call_purpose: Purpose or reason for the call (for tracking/logging)
        ai_instructions: Detailed instructions for the AI voice agent to follow
        voice_style: Voice style for the call - professional, friendly, or casual

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Call details including:
            - call_sid: Unique Twilio call identifier
            - status: Current call status
            - tracking_url: URL to track call in Twilio console
            - estimated_cost: Estimated cost of the call in USD
            - recipient_name: Name of recipient
            - call_purpose: Purpose of the call
            - duration: Call duration (if completed)
        - metadata: Additional information about the call

    Example:
        >>> tool = TwilioPhoneCall(
        ...     recipient_name="John Smith",
        ...     phone_number="+15551234567",
        ...     call_purpose="Appointment reminder",
        ...     ai_instructions="Remind the customer about their doctor appointment tomorrow at 2 PM. Ask them to confirm by saying yes or no.",
        ...     voice_style="professional"
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["call_sid"])
        >>> print(result["result"]["tracking_url"])
    """

    # Tool metadata
    tool_name: str = "twilio_phone_call"
    tool_category: str = "communication"
    rate_limit_type: str = "api_calls"
    rate_limit_cost: int = 2  # Phone calls are more expensive operations

    # Parameters
    recipient_name: str = Field(
        ...,
        description="Name of the person receiving the call (for logging and tracking purposes)",
        min_length=1,
        max_length=100,
    )

    phone_number: str = Field(
        ...,
        description="Phone number to call in E.164 format (e.g., +15551234567, +442071234567)",
        min_length=10,
        max_length=20,
    )

    call_purpose: str = Field(
        ...,
        description="Purpose or reason for the call (e.g., 'Appointment reminder', 'Follow-up call', 'Customer survey')",
        min_length=1,
        max_length=200,
    )

    ai_instructions: str = Field(
        ...,
        description="Detailed instructions for the AI voice agent to follow during the call",
        min_length=10,
        max_length=3000,
    )

    voice_style: Literal["professional", "friendly", "casual"] = Field(
        "professional",
        description="Voice style for the call: professional (formal business), friendly (warm but professional), or casual (relaxed conversation)",
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_format(cls, v):
        """Validate E.164 phone number format."""
        # E.164 format: +[country code][subscriber number]
        # Total length: 1 to 15 digits (plus the + sign)
        pattern = re.compile(r"^\+[1-9]\d{1,14}$")
        if not pattern.match(v.strip()):
            raise ValueError(
                "Phone number must be in E.164 format (e.g., +15551234567). "
                "Format: +[country code][number] with 1-15 digits total."
            )
        return v.strip()

    def _execute(self) -> Dict[str, Any]:
        """Execute phone call via Twilio."""

        self._logger.info(f"Executing {self.tool_name} with recipient_name={self.recipient_name}, phone_number={self.phone_number}, call_purpose={self.call_purpose}, ai_instructions={self.ai_instructions}, voice_style={self.voice_style}")
        # 1. VALIDATE
        self._logger.debug(f"Validating parameters for {self.tool_name}")
        self._validate_parameters()

        # 2. CHECK MOCK MODE
        if self._should_use_mock():
            self._logger.info("Using mock mode for testing")
            return self._generate_mock_results()

        # 3. EXECUTE
        if not TWILIO_AVAILABLE:
            raise APIError(
                "Twilio package not installed. Install with: pip install twilio",
                tool_name=self.tool_name,
                api_name="Twilio",
            )

        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "recipient_name": self.recipient_name,
                    "phone_number": self._mask_phone_number(self.phone_number),
                    "call_purpose": self.call_purpose,
                    "voice_style": self.voice_style,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mock_mode": False,
                },
            }
        except Exception as e:
            # Handle Twilio-specific exceptions if available
            if TWILIO_AVAILABLE:
                try:
                    if isinstance(e, TwilioRestException):
                        error_code = getattr(e, "code", None)
                        if error_code == 21211:
                            raise ValidationError(
                                f"Invalid phone number: {self.phone_number}. "
                                f"Ensure it's in E.164 format (e.g., +15551234567).",
                                tool_name=self.tool_name,
                                field="phone_number",
                            )
                        elif error_code in [20003, 20008]:
                            raise AuthenticationError(
                                "Invalid Twilio credentials. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.",
                                tool_name=self.tool_name,
                                api_name="Twilio API",
                            )
                        elif error_code == 21201:
                            raise ValidationError(
                                "No 'To' number specified. Phone number is required.",
                                tool_name=self.tool_name,
                                field="phone_number",
                            )
                        elif error_code == 21608:
                            raise ValidationError(
                                "The 'From' number is not a valid Twilio phone number.",
                                tool_name=self.tool_name,
                                field="from_number",
                            )
                        raise APIError(
                            f"Twilio API error: {e.msg}",
                            tool_name=self.tool_name,
                            api_name="Twilio API",
                            status_code=error_code,
                        )
                except NameError:
                    # TwilioRestException not defined (shouldn't happen but be safe)
                    pass

            raise APIError(
                f"Failed to make phone call: {str(e)}", tool_name=self.tool_name, api_name="Twilio"
            )

    def _validate_parameters(self) -> None:
        """Validate input parameters."""
        # Validate recipient name
        if not self.recipient_name.strip():
            raise ValidationError(
                "recipient_name cannot be empty", tool_name=self.tool_name, field="recipient_name"
            )

        # Validate phone number (additional validation beyond Pydantic)
        if not self.phone_number.strip():
            raise ValidationError(
                "phone_number cannot be empty", tool_name=self.tool_name, field="phone_number"
            )

        # Validate call purpose
        if not self.call_purpose.strip():
            raise ValidationError(
                "call_purpose cannot be empty", tool_name=self.tool_name, field="call_purpose"
            )

        # Validate AI instructions
        if not self.ai_instructions.strip():
            raise ValidationError(
                "ai_instructions cannot be empty", tool_name=self.tool_name, field="ai_instructions"
            )

        if len(self.ai_instructions.strip()) < 10:
            raise ValidationError(
                "ai_instructions must be at least 10 characters long for meaningful call guidance",
                tool_name=self.tool_name,
                field="ai_instructions",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results for testing."""
        # Generate deterministic mock call SID
        mock_call_sid = f"CA{abs(hash(self.phone_number + self.ai_instructions))}".replace("-", "")[
            :34
        ]

        # Generate mock account SID
        mock_account_sid = f"AC{abs(hash('mock_account'))}".replace("-", "")[:34]

        # Calculate mock duration based on instruction length (rough estimate)
        estimated_duration = min(120, max(30, len(self.ai_instructions) // 10))

        # Calculate estimated cost (Twilio charges ~$0.013-0.015 per minute)
        estimated_cost = round((estimated_duration / 60) * 0.014, 4)

        return {
            "success": True,
            "result": {
                "call_sid": mock_call_sid,
                "status": "completed",
                "tracking_url": f"https://www.twilio.com/console/voice/calls/{mock_call_sid}",
                "estimated_cost": f"${estimated_cost:.4f}",
                "recipient_name": self.recipient_name,
                "phone_number": self.phone_number,
                "call_purpose": self.call_purpose,
                "direction": "outbound-api",
                "duration": estimated_duration,
                "date_created": datetime.now(timezone.utc).isoformat(),
                "voice_style": self.voice_style,
                "ai_instructions_delivered": True,
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "recipient_name": self.recipient_name,
                "phone_number": self._mask_phone_number(self.phone_number),
                "call_purpose": self.call_purpose,
                "voice_style": self.voice_style,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Make phone call via Twilio API."""
        # Get Twilio credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        # Validate credentials
        if not account_sid or not auth_token:
            raise AuthenticationError(
                "Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables. "
                "Please set these variables with your Twilio credentials.",
                tool_name=self.tool_name,
                api_name="Twilio API",
            )

        if not from_number:
            raise ValidationError(
                "Missing TWILIO_PHONE_NUMBER environment variable. "
                "Please set this to your Twilio phone number in E.164 format (e.g., +15551234567).",
                tool_name=self.tool_name,
                field="from_number",
            )

        # Validate from_number format
        if not re.match(r"^\+[1-9]\d{1,14}$", from_number):
            raise ValidationError(
                f"TWILIO_PHONE_NUMBER must be in E.164 format. Got: {from_number}",
                tool_name=self.tool_name,
                field="from_number",
            )

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Generate TwiML for voice message
        twiml = self._generate_twiml()

        # Make the call
        call = client.calls.create(to=self.phone_number, from_=from_number, twiml=twiml)

        # Calculate estimated cost
        # Note: Actual cost depends on call duration and destination
        # This is a rough estimate based on typical Twilio rates
        estimated_cost = self._estimate_call_cost(self.phone_number, len(self.ai_instructions))

        # Generate tracking URL
        tracking_url = f"https://www.twilio.com/console/voice/calls/{call.sid}"

        # Return comprehensive call details
        return {
            "call_sid": call.sid,
            "status": call.status,
            "tracking_url": tracking_url,
            "estimated_cost": f"${estimated_cost:.4f}",
            "recipient_name": self.recipient_name,
            "phone_number": call.to,
            "call_purpose": self.call_purpose,
            "direction": call.direction,
            "from_number": call.from_,
            "date_created": call.date_created.isoformat() if call.date_created else None,
            "voice_style": self.voice_style,
            "ai_instructions_length": len(self.ai_instructions),
        }

    def _generate_twiml(self) -> str:
        """
        Generate TwiML (Twilio Markup Language) for the AI-assisted call.

        Maps voice styles to appropriate Twilio voices and generates
        TwiML that includes the AI instructions.

        Returns:
            TwiML XML string
        """
        # Map voice styles to Twilio voice options
        voice_map = {
            "professional": "Polly.Joanna",  # Professional female voice
            "friendly": "Polly.Matthew",  # Friendly male voice
            "casual": "alice",  # Casual neutral voice
        }

        twilio_voice = voice_map.get(self.voice_style, "Polly.Joanna")

        # Escape XML special characters in instructions
        escaped_instructions = self._escape_xml(self.ai_instructions)

        # Add greeting based on voice style
        greetings = {
            "professional": f"Hello, this is a call for {self.recipient_name}.",
            "friendly": f"Hi {self.recipient_name}, I'm calling to connect with you.",
            "casual": f"Hey {self.recipient_name}, just reaching out to you.",
        }

        greeting = self._escape_xml(greetings.get(self.voice_style, greetings["professional"]))

        # Generate comprehensive TwiML
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{twilio_voice}">{greeting}</Say>
    <Pause length="1"/>
    <Say voice="{twilio_voice}">{escaped_instructions}</Say>
    <Pause length="2"/>
    <Gather input="speech" timeout="5" speechTimeout="auto">
        <Say voice="{twilio_voice}">Please respond after the beep.</Say>
    </Gather>
    <Say voice="{twilio_voice}">Thank you for your time. Goodbye.</Say>
</Response>"""

        return twiml

    def _escape_xml(self, text: str) -> str:
        """
        Escape XML special characters.

        Args:
            text: Text to escape

        Returns:
            XML-safe text
        """
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _estimate_call_cost(self, phone_number: str, instruction_length: int) -> float:
        """
        Estimate call cost based on phone number and instruction length.

        This is a rough estimate. Actual costs depend on:
        - Call duration
        - Destination country
        - Twilio pricing tier

        Args:
            phone_number: Destination phone number
            instruction_length: Length of AI instructions

        Returns:
            Estimated cost in USD
        """
        # Estimate duration based on instruction length
        # Rough estimate: 150 words per minute, average 5 chars per word
        estimated_duration_minutes = max(1, (instruction_length / (150 * 5)))

        # Determine rate based on destination
        # US/Canada: ~$0.013/min, UK: ~$0.024/min, others: ~$0.05/min
        if phone_number.startswith("+1"):
            rate_per_minute = 0.013  # US/Canada
        elif phone_number.startswith("+44"):
            rate_per_minute = 0.024  # UK
        else:
            rate_per_minute = 0.05  # International (conservative estimate)

        estimated_cost = estimated_duration_minutes * rate_per_minute
        return round(estimated_cost, 4)

    def _mask_phone_number(self, phone: str) -> str:
        """
        Mask phone number for privacy in logs.

        Args:
            phone: Phone number to mask

        Returns:
            Masked phone number (e.g., +1***4567)
        """
        if len(phone) <= 6:
            return phone
        return phone[:3] + "***" + phone[-4:]


if __name__ == "__main__":
    print("Testing TwilioPhoneCall...")
    print("=" * 60)

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test 1: Professional appointment reminder
    print("\n[Test 1] Professional appointment reminder")
    tool1 = TwilioPhoneCall(
        recipient_name="Dr. Sarah Johnson",
        phone_number="+15551234567",
        call_purpose="Appointment confirmation",
        ai_instructions="This is a reminder about your upcoming medical appointment tomorrow at 2:30 PM with Dr. Smith. Please confirm your attendance by saying yes, or let us know if you need to reschedule by saying no.",
        voice_style="professional",
    )
    result1 = tool1.run()

    print(f"Success: {result1.get('success')}")
    print(f"Call SID: {result1.get('result', {}).get('call_sid')}")
    print(f"Status: {result1.get('result', {}).get('status')}")
    print(f"Tracking URL: {result1.get('result', {}).get('tracking_url')}")
    print(f"Estimated Cost: {result1.get('result', {}).get('estimated_cost')}")
    assert result1.get("success") == True
    assert result1.get("result", {}).get("status") == "completed"
    assert "tracking_url" in result1.get("result", {})
    assert "estimated_cost" in result1.get("result", {})
    print("[Test 1] PASSED")

    # Test 2: Friendly customer follow-up
    print("\n[Test 2] Friendly customer follow-up")
    tool2 = TwilioPhoneCall(
        recipient_name="John Smith",
        phone_number="+442071234567",
        call_purpose="Customer satisfaction survey",
        ai_instructions="We wanted to check in and see how your recent purchase is working out for you. On a scale of 1 to 5, how satisfied are you with your new product? Your feedback helps us improve our service.",
        voice_style="friendly",
    )
    result2 = tool2.run()

    print(f"Success: {result2.get('success')}")
    print(f"Recipient: {result2.get('result', {}).get('recipient_name')}")
    print(f"Purpose: {result2.get('result', {}).get('call_purpose')}")
    print(f"Voice Style: {result2.get('result', {}).get('voice_style')}")
    assert result2.get("success") == True
    assert result2.get("result", {}).get("voice_style") == "friendly"
    assert result2.get("result", {}).get("recipient_name") == "John Smith"
    print("[Test 2] PASSED")

    # Test 3: Casual reminder call
    print("\n[Test 3] Casual reminder call")
    tool3 = TwilioPhoneCall(
        recipient_name="Mike Chen",
        phone_number="+13105551234",
        call_purpose="Event reminder",
        ai_instructions="Just a quick heads up that the team meetup is happening this Friday at 6 PM at the usual spot. Hope to see you there! Let us know if you can make it.",
        voice_style="casual",
    )
    result3 = tool3.run()

    print(f"Success: {result3.get('success')}")
    print(f"Voice Style: {result3.get('result', {}).get('voice_style')}")
    assert result3.get("success") == True
    assert result3.get("result", {}).get("voice_style") == "casual"
    print("[Test 3] PASSED")

    # Test 4: Phone number validation (E.164 format)
    print("\n[Test 4] Phone number validation")
    try:
        tool4 = TwilioPhoneCall(
            recipient_name="Invalid User",
            phone_number="555-1234",  # Invalid format
            call_purpose="Test",
            ai_instructions="This should fail validation.",
        )
        result4 = tool4.run()
        print("[Test 4] FAILED - Should have raised validation error")
        assert False
    except (ValidationError, ValueError) as e:
        print(f"Validation error caught (expected): {str(e)[:100]}...")
        print("[Test 4] PASSED")

    # Test 5: Empty ai_instructions validation
    print("\n[Test 5] Empty AI instructions validation")
    try:
        tool5 = TwilioPhoneCall(
            recipient_name="Test User",
            phone_number="+15551234567",
            call_purpose="Test",
            ai_instructions="",  # Empty instructions
        )
        result5 = tool5.run()
        print("[Test 5] FAILED - Should have raised validation error")
        assert False
    except Exception as e:
        print(f"Validation error caught (expected): {str(e)[:100]}...")
        print("[Test 5] PASSED")

    # Test 6: Verify metadata
    print("\n[Test 6] Metadata verification")
    tool6 = TwilioPhoneCall(
        recipient_name="Metadata Test",
        phone_number="+19175551234",
        call_purpose="Metadata verification",
        ai_instructions="Testing that all metadata fields are properly populated in the response.",
        voice_style="professional",
    )
    result6 = tool6.run()

    metadata = result6.get("metadata", {})
    print(f"Mock Mode: {metadata.get('mock_mode')}")
    print(f"Tool Name: {metadata.get('tool_name')}")
    print(f"Recipient: {metadata.get('recipient_name')}")
    print(f"Masked Phone: {metadata.get('phone_number')}")
    print(f"Purpose: {metadata.get('call_purpose')}")
    print(f"Voice Style: {metadata.get('voice_style')}")

    assert metadata.get("mock_mode") == True
    assert metadata.get("tool_name") == "twilio_phone_call"
    assert metadata.get("recipient_name") == "Metadata Test"
    assert "***" in metadata.get("phone_number", "")  # Phone should be masked
    assert metadata.get("voice_style") == "professional"
    print("[Test 6] PASSED")

    print("\n" + "=" * 60)
    print("All TwilioPhoneCall tests passed successfully!")
    print("=" * 60)
