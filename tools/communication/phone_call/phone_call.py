"""
Make AI-assisted phone calls via Twilio API
"""

import os
import re
from typing import Any, Dict, Optional

from pydantic import Field

from shared.base import BaseTool
from shared.errors import APIError, AuthenticationError, ValidationError

try:
    from twilio.base.exceptions import TwilioRestException
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class PhoneCall(BaseTool):
    """
    Make AI-assisted phone calls via Twilio API.

    Args:
        phone_number: Phone number to call (international format: +1234567890)
        message: Message to deliver via AI voice
        voice: Voice type (male, female, neutral) - optional
        language: Language code (default: en-US)
        wait_for_response: Whether to wait for caller response (default: False)

    Returns:
        Dict containing:
        - success: Boolean indicating success
        - result: Call details including call_sid, status, duration
        - metadata: Additional information about the call

    Example:
        >>> tool = PhoneCall(
        ...     phone_number="+15551234567",
        ...     message="Hello, this is a reminder about your appointment."
        ... )
        >>> result = tool.run()
        >>> print(result["result"]["call_sid"])
    """

    # Tool metadata
    tool_name: str = "phone_call"
    tool_category: str = "communication"

    # Parameters
    phone_number: str = Field(
        ...,
        description="Phone number to call in international format (e.g., +1234567890)",
        min_length=10,
        max_length=20,
    )
    message: str = Field(
        ..., description="Message to deliver via AI voice", min_length=1, max_length=2000
    )
    voice: Optional[str] = Field(None, description="Voice type: male, female, or neutral")
    language: str = Field("en-US", description="Language code (e.g., en-US, es-ES, fr-FR)")
    wait_for_response: bool = Field(False, description="Whether to wait for caller response")

    def _execute(self) -> Dict[str, Any]:
        """Execute phone call via Twilio."""

        self._logger.info(
            f"Executing {self.tool_name} with phone_number={self.phone_number}, message={self.message}, voice={self.voice}, language={self.language}, wait_for_response={self.wait_for_response}"
        )
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
                "twilio package not installed. Install with: pip install twilio",
                tool_name=self.tool_name,
            )

        try:
            result = self._process()
            self._logger.info(f"Successfully completed {self.tool_name}")

            return {
                "success": True,
                "result": result,
                "metadata": {
                    "tool_name": self.tool_name,
                    "phone_number": self._mask_phone_number(self.phone_number),
                    "language": self.language,
                    "wait_for_response": self.wait_for_response,
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
                                f"Invalid phone number: {self.phone_number}",
                                tool_name=self.tool_name,
                                field="phone_number",
                            )
                        elif error_code in [20003, 20008]:
                            raise AuthenticationError(
                                "Invalid Twilio credentials",
                                tool_name=self.tool_name,
                                api_name="Twilio API",
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

            raise APIError(f"Failed to make phone call: {e}", tool_name=self.tool_name)

    def _validate_parameters(self) -> None:
        """Validate parameters."""
        # Validate phone number
        if not self.phone_number.strip():
            raise ValidationError(
                "phone_number cannot be empty", tool_name=self.tool_name, field="phone_number"
            )

        # Check phone number format (international format)
        phone_pattern = re.compile(r"^\+\d{10,15}$")
        if not phone_pattern.match(self.phone_number.strip()):
            raise ValidationError(
                "phone_number must be in international format (e.g., +1234567890)",
                tool_name=self.tool_name,
                field="phone_number",
            )

        # Validate message
        if not self.message.strip():
            raise ValidationError(
                "message cannot be empty", tool_name=self.tool_name, field="message"
            )

        # Validate voice type if provided
        if self.voice and self.voice.lower() not in ["male", "female", "neutral"]:
            raise ValidationError(
                "voice must be one of: male, female, neutral",
                tool_name=self.tool_name,
                field="voice",
            )

        # Validate language code format
        language_pattern = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
        if not language_pattern.match(self.language):
            raise ValidationError(
                "language must be in format: xx-XX (e.g., en-US, es-ES)",
                tool_name=self.tool_name,
                field="language",
            )

    def _should_use_mock(self) -> bool:
        """Check if mock mode enabled."""
        return os.getenv("USE_MOCK_APIS", "false").lower() == "true"

    def _generate_mock_results(self) -> Dict[str, Any]:
        """Generate mock results."""
        import time

        mock_call_sid = f"CA{abs(hash(self.phone_number + self.message))}".replace("-", "")[:34]

        return {
            "success": True,
            "result": {
                "call_sid": mock_call_sid,
                "status": "completed",
                "direction": "outbound-api",
                "to": self.phone_number,
                "duration": 45,
                "price": "-0.015",
                "price_unit": "USD",
                "date_created": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message_delivered": self.message,
                "voice_used": self.voice or "neutral",
            },
            "metadata": {
                "mock_mode": True,
                "tool_name": self.tool_name,
                "phone_number": self._mask_phone_number(self.phone_number),
                "language": self.language,
                "wait_for_response": self.wait_for_response,
            },
        }

    def _process(self) -> Dict[str, Any]:
        """Make phone call via Twilio API."""
        # Get Twilio credentials
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not account_sid or not auth_token:
            raise AuthenticationError(
                "Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN environment variables",
                tool_name=self.tool_name,
                api_name="Twilio API",
            )

        if not from_number:
            raise ValidationError(
                "Missing TWILIO_PHONE_NUMBER environment variable",
                tool_name=self.tool_name,
                field="from_number",
            )

        # Create Twilio client
        client = Client(account_sid, auth_token)

        # Generate TwiML for voice message
        twiml = self._generate_twiml()

        # Make the call
        call = client.calls.create(to=self.phone_number, from_=from_number, twiml=twiml)

        # Return call details
        return {
            "call_sid": call.sid,
            "status": call.status,
            "direction": call.direction,
            "to": call.to,
            "from": call.from_,
            "date_created": call.date_created.isoformat() if call.date_created else None,
            "price": call.price,
            "price_unit": call.price_unit,
            "message_delivered": self.message,
        }

    def _generate_twiml(self) -> str:
        """
        Generate TwiML (Twilio Markup Language) for the call.

        Returns:
            TwiML XML string
        """
        # Map voice to Twilio voice options
        voice_map = {"male": "man", "female": "woman", "neutral": "alice"}

        twilio_voice = voice_map.get(self.voice.lower() if self.voice else "neutral", "alice")

        # Escape XML special characters in message
        escaped_message = (
            self.message.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

        if self.wait_for_response:
            # Include gather for response
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{twilio_voice}" language="{self.language}">{escaped_message}</Say>
    <Gather input="speech" timeout="5" action="/handle-response">
        <Say voice="{twilio_voice}" language="{self.language}">Please respond after the beep.</Say>
    </Gather>
    <Say voice="{twilio_voice}" language="{self.language}">Thank you for your response. Goodbye.</Say>
</Response>"""
        else:
            # Simple message delivery
            twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="{twilio_voice}" language="{self.language}">{escaped_message}</Say>
    <Pause length="1"/>
    <Say voice="{twilio_voice}" language="{self.language}">Goodbye.</Say>
</Response>"""

        return twiml

    def _mask_phone_number(self, phone: str) -> str:
        """
        Mask phone number for privacy in logs.

        Args:
            phone: Phone number to mask

        Returns:
            Masked phone number (e.g., +1***567890)
        """
        if len(phone) <= 6:
            return phone
        return phone[:3] + "***" + phone[-6:]


if __name__ == "__main__":
    print("Testing PhoneCall...")

    import os

    os.environ["USE_MOCK_APIS"] = "true"

    # Test basic call
    tool = PhoneCall(
        phone_number="+15551234567", message="Hello, this is a test call from AgentSwarm."
    )
    result = tool.run()

    print(f"Success: {result.get('success')}")
    print(f"Call SID: {result.get('result', {}).get('call_sid')}")
    print(f"Status: {result.get('result', {}).get('status')}")
    assert result.get("success") == True
    assert result.get("result", {}).get("status") == "completed"

    # Test with voice and language
    tool2 = PhoneCall(
        phone_number="+34612345678",
        message="Hola, esta es una llamada de prueba.",
        voice="female",
        language="es-ES",
    )
    result2 = tool2.run()

    print(f"Spanish Call Success: {result2.get('success')}")
    assert result2.get("success") == True
    assert result2.get("metadata", {}).get("language") == "es-ES"

    # Test with response waiting
    tool3 = PhoneCall(
        phone_number="+15551234567",
        message="Please confirm your appointment by saying yes or no.",
        wait_for_response=True,
    )
    result3 = tool3.run()

    print(f"Interactive Call Success: {result3.get('success')}")
    assert result3.get("success") == True
    assert result3.get("metadata", {}).get("wait_for_response") == True

    # Test phone number validation
    try:
        tool4 = PhoneCall(phone_number="123456", message="Test")  # Invalid format
        result4 = tool4.run()
        assert result4.get("success") == False
        print("Phone validation test passed (invalid number rejected)")
    except Exception:
        print("Phone validation test passed (invalid number rejected)")

    print("PhoneCall tests passed!")
