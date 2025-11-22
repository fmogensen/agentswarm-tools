# twilio_phone_call

Make AI-assisted phone calls via Twilio API with advanced call management and tracking.

## Category

Communication & Productivity

## Parameters

- **recipient_name** (str, required): Name of the person receiving the call (for logging and tracking purposes)
- **phone_number** (str, required): Phone number to call in E.164 format (e.g., +15551234567, +442071234567)
- **call_purpose** (str, required): Purpose or reason for the call (e.g., "Appointment reminder", "Follow-up call")
- **ai_instructions** (str, required): Detailed instructions for the AI voice agent to follow during the call (10-3000 characters)
- **voice_style** (Literal["professional", "friendly", "casual"], optional): Voice style for the call (default: "professional")

## Returns

Returns a dictionary with:
- `success` (bool): Whether the operation succeeded
- `result` (dict): Call details including:
  - `call_sid`: Unique Twilio call identifier
  - `status`: Current call status
  - `tracking_url`: URL to track call in Twilio console
  - `estimated_cost`: Estimated cost of the call in USD
  - `recipient_name`: Name of recipient
  - `call_purpose`: Purpose of the call
  - `duration`: Call duration (if completed)
- `metadata` (dict): Additional information including recipient_name, masked phone_number, call_purpose, voice_style, and timestamp

## Environment Variables Required

- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio authentication token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number in E.164 format (e.g., +15551234567)

## Usage Example

```python
from tools.communication.twilio_phone_call import TwilioPhoneCall

# Professional appointment reminder
tool = TwilioPhoneCall(
    recipient_name="Dr. Sarah Johnson",
    phone_number="+15551234567",
    call_purpose="Appointment confirmation",
    ai_instructions="This is a reminder about your upcoming medical appointment tomorrow at 2:30 PM with Dr. Smith. Please confirm your attendance by saying yes, or let us know if you need to reschedule by saying no.",
    voice_style="professional"
)

# Run the tool
result = tool.run()

# Check result
if result["success"]:
    print(f"Call SID: {result['result']['call_sid']}")
    print(f"Status: {result['result']['status']}")
    print(f"Tracking URL: {result['result']['tracking_url']}")
    print(f"Estimated Cost: {result['result']['estimated_cost']}")
else:
    print(f"Error: {result.get('error')}")
```

## Voice Styles

- **professional**: Formal business voice (Polly.Joanna) - best for professional communications
- **friendly**: Warm but professional voice (Polly.Matthew) - good for customer service
- **casual**: Relaxed conversational voice (Alice) - appropriate for informal reminders

## Phone Number Format (E.164)

All phone numbers must be in E.164 format:
- Start with `+`
- Followed by country code
- Then subscriber number
- No spaces, dashes, or parentheses
- Examples:
  - US: `+15551234567`
  - UK: `+442071234567`
  - International: `+33123456789`

## Cost Estimation

The tool provides estimated costs based on:
- Call duration (estimated from instruction length)
- Destination country
- Typical Twilio rates:
  - US/Canada: ~$0.013/minute
  - UK: ~$0.024/minute
  - Other international: ~$0.05/minute

**Note:** Actual costs may vary based on actual call duration and current Twilio pricing.

## Testing

Run tests with mock mode:
```bash
# Set environment variable for mock mode
export USE_MOCK_APIS=true

# Run the tool's built-in tests
python tools/communication/twilio_phone_call/twilio_phone_call.py

# Run with pytest
pytest tools/communication/twilio_phone_call/test_twilio_phone_call.py -v
```

## Features

- **E.164 Validation**: Automatic validation of phone number format
- **Multiple Voice Styles**: Choose between professional, friendly, or casual
- **Cost Estimation**: Automatic cost estimation based on destination and duration
- **Call Tracking**: Provides Twilio console URL for call monitoring
- **Comprehensive Error Handling**: Detailed error messages for common issues
- **Privacy Protection**: Phone numbers are masked in logs
- **Mock Mode Support**: Full testing without making actual calls

## Documentation

- [Tool Index](../../../TOOLS_INDEX.md)
- [Complete Documentation](../../../genspark_tools_documentation.md)
- [Examples](../../../tool_examples_complete.md)
- [Category Overview](../README.md)
