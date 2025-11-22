# Twilio Integration Guide for AgentSwarm

**Version:** 1.0
**Date:** November 22, 2025
**Purpose:** AI-powered phone calling via Twilio partnership

---

## Overview

Instead of building phone calling infrastructure from scratch (6+ months, $200K+), AgentSwarm partners with **Twilio** for AI-powered phone calls. This guide shows you how to integrate Twilio's AI voice capabilities with AgentSwarm tools.

### Why Twilio?

| Approach | Time | Cost | Maintenance |
|----------|------|------|-------------|
| **Build from scratch** | 6+ months | $200K+ | High complexity |
| **Twilio partnership** | 1 week | $0.02/min | Zero maintenance |

**Decision:** Partner with Twilio ✅

---

## Architecture

```
User Request
    ↓
twilio_phone_call tool
    ↓
Twilio API
    ↓
AI Voice Agent (Twilio)
    ↓
Phone Call Execution
    ↓
twilio_call_logs tool
    ↓
Call History & Transcripts
```

---

## Features

### What You Get

✅ **AI-Powered Calling**
- Natural conversation AI
- Context-aware responses
- Multi-language support (40+ languages)
- Voice customization

✅ **Global Coverage**
- 200+ countries supported
- Local number provisioning
- International calling

✅ **Call Management**
- Real-time call monitoring
- Call recording
- Transcription (speech-to-text)
- Sentiment analysis

✅ **Analytics**
- Call duration tracking
- Success/failure metrics
- Cost tracking
- Quality monitoring

---

## Setup

### Step 1: Create Twilio Account

```bash
# Sign up at twilio.com
# Get your credentials:
# - Account SID
# - Auth Token
# - Phone Number
```

### Step 2: Set Environment Variables

```bash
# Add to your .env file
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
```

### Step 3: Install Dependencies

```bash
pip install twilio>=8.10.0
```

---

## Usage

### Making AI Phone Calls

```python
from agency_swarm import Agent
from tools.communication.twilio_phone_call import TwilioPhoneCall

# Create agent with phone calling capability
assistant = Agent(
    name="PhoneAssistant",
    tools=[TwilioPhoneCall]
)

# Make a phone call
result = TwilioPhoneCall(
    recipient_name="John Doe",
    phone_number="+1-555-123-4567",
    call_purpose="Schedule appointment",
    ai_instructions="Ask for preferred appointment times this week. Be friendly and professional.",
    voice_style="professional"
).run()

print(result)
# {
#   "success": True,
#   "call_sid": "CAxxxxxxxxxxxxxxxxxxxxx",
#   "status": "initiated",
#   "tracking_url": "https://console.twilio.com/...",
#   "estimated_cost": "$0.02/min"
# }
```

### Retrieving Call Logs

```python
from tools.communication.twilio_call_logs import TwilioCallLogs

# Get recent call history
logs = TwilioCallLogs(
    time_range_hours=24,
    limit=10,
    include_transcript=True
).run()

print(logs)
# {
#   "success": True,
#   "calls": [
#     {
#       "call_sid": "CAxxxxx",
#       "to": "+1-555-123-4567",
#       "from": "+1-555-987-6543",
#       "status": "completed",
#       "duration": 127,  # seconds
#       "cost": "$0.04",
#       "start_time": "2025-11-22T10:30:00Z",
#       "end_time": "2025-11-22T10:32:07Z",
#       "transcript": "Hello, this is the appointment scheduling assistant...",
#       "summary": "Appointment scheduled for Nov 25 at 2pm"
#     }
#   ]
# }
```

---

## Advanced Use Cases

### 1. Business Phone Support

```python
TwilioPhoneCall(
    recipient_name="Support Inquiry",
    phone_number="+1-555-SUPPORT",
    call_purpose="Customer support inquiry",
    ai_instructions="""
    You are a helpful customer support agent.

    1. Greet the customer warmly
    2. Ask how you can help
    3. Collect issue details
    4. Provide solution or escalate
    5. Confirm resolution

    Be empathetic and solution-focused.
    """,
    voice_style="friendly"
)
```

### 2. Appointment Scheduling

```python
TwilioPhoneCall(
    recipient_name="Dr. Smith's Office",
    phone_number="+1-555-DOCTOR",
    call_purpose="Schedule medical appointment",
    ai_instructions="""
    Call Dr. Smith's office and schedule an appointment.

    Patient: John Doe
    Reason: Annual checkup
    Preferred times: Weekday mornings
    Insurance: Blue Cross (Policy #12345)

    Confirm appointment date, time, and any prep instructions.
    """,
    voice_style="professional"
)
```

### 3. Survey/Feedback Collection

```python
TwilioPhoneCall(
    recipient_name="Customer Feedback",
    phone_number="+1-555-CUSTOMER",
    call_purpose="Product feedback survey",
    ai_instructions="""
    Conduct a brief 3-question product satisfaction survey:

    1. How satisfied are you with our product? (1-10)
    2. What feature do you use most?
    3. Any suggestions for improvement?

    Be concise and thank them for their time.
    """,
    voice_style="friendly"
)
```

### 4. Delivery/Status Updates

```python
TwilioPhoneCall(
    recipient_name="Package Recipient",
    phone_number="+1-555-DELIVERY",
    call_purpose="Delivery notification",
    ai_instructions="""
    Notify customer about package delivery:

    Tracking: 1Z999AA10123456784
    Status: Out for delivery
    Expected: Today between 2-6pm

    Ask if they'll be home or prefer alternative delivery location.
    """,
    voice_style="professional"
)
```

---

## Configuration Options

### Voice Customization

```python
# Available voice styles
voice_style = "professional"  # Clear, business-like
voice_style = "friendly"      # Warm, conversational
voice_style = "casual"        # Relaxed, informal
```

### Language Support

```python
# Twilio supports 40+ languages
TwilioPhoneCall(
    # ... other params
    ai_instructions="Speak in Spanish. Greeting: 'Hola, ¿cómo puedo ayudarte hoy?'",
    language="es-ES"  # Spanish (Spain)
)
```

### Call Recording

```python
# All calls are automatically recorded
# Access via call logs:
TwilioCallLogs(
    include_transcript=True,  # Get full transcript
    include_recording_url=True  # Get audio recording URL
)
```

---

## Cost Structure

### Pricing (Twilio)

| Service | Cost |
|---------|------|
| **Outbound calls (US)** | $0.013/min |
| **Inbound calls (US)** | $0.0085/min |
| **Phone number** | $1/month |
| **Recording** | $0.0005/min |
| **Transcription** | $0.05/min |

### Example Costs

**Scenario 1:** 100 outbound calls, 2 minutes each
```
100 calls × 2 min × $0.013/min = $2.60
Transcription: 200 min × $0.05/min = $10.00
Total: $12.60/month
```

**Scenario 2:** Customer support line (200 inbound calls/month, avg 5 min)
```
200 calls × 5 min × $0.0085/min = $8.50
Phone number: $1/month
Recording: 1000 min × $0.0005/min = $0.50
Transcription: 1000 min × $0.05/min = $50.00
Total: $60/month
```

### vs Building from Scratch

| Metric | Twilio | Custom Build |
|--------|--------|--------------|
| **Initial cost** | $0 | $200K+ |
| **Dev time** | 1 week | 6+ months |
| **Monthly cost** | $60-500 | $5K-20K (infrastructure) |
| **Maintenance** | Zero | High |
| **Scaling** | Automatic | Manual |

**ROI:** Twilio saves $200K+ upfront and $5K-20K/month in infrastructure costs

---

## Best Practices

### 1. Clear AI Instructions

❌ **Bad:**
```python
ai_instructions="Call and ask about appointment"
```

✅ **Good:**
```python
ai_instructions="""
You are calling Dr. Smith's office to schedule an appointment.

Context:
- Patient: John Doe
- Reason: Annual physical exam
- Preferred: Weekday mornings next week

Steps:
1. Greet: "Hello, I'm calling to schedule an appointment for John Doe"
2. Explain: "He needs an annual physical exam"
3. Suggest: "Do you have any openings next week, preferably mornings?"
4. Confirm: Repeat appointment date, time, and any special instructions
5. Thank: "Thank you, we'll see you then"

Be polite, professional, and patient.
"""
```

### 2. Phone Number Validation

```python
import re

def validate_phone(phone: str) -> bool:
    """Validate E.164 format: +1-555-123-4567"""
    pattern = r'^\+\d{1,3}-\d{3,14}$'
    return bool(re.match(pattern, phone))

# Always validate before calling
if validate_phone(phone_number):
    TwilioPhoneCall(...)
else:
    raise ValueError("Invalid phone number format")
```

### 3. Error Handling

```python
try:
    result = TwilioPhoneCall(...).run()
    if result["success"]:
        print(f"Call initiated: {result['call_sid']}")
    else:
        print(f"Call failed: {result['error']}")
except Exception as e:
    print(f"Error: {e}")
    # Log to monitoring system
    # Retry with exponential backoff
```

### 4. Rate Limiting

```python
# Twilio default limits:
# - 10 concurrent calls (free tier)
# - 100 concurrent calls (paid tier)

# Implement queue for high volume
from queue import Queue
import time

call_queue = Queue()

def process_calls():
    while not call_queue.empty():
        call_params = call_queue.get()
        TwilioPhoneCall(**call_params).run()
        time.sleep(6)  # Rate limit: 10 calls/min
```

### 5. Privacy & Compliance

```python
# Always get consent before calling
def check_consent(phone: str) -> bool:
    """Check if user consented to calls"""
    # Query database for consent record
    return consent_database.has_consent(phone)

if check_consent(phone_number):
    TwilioPhoneCall(...)
else:
    raise PermissionError("User has not consented to phone calls")
```

---

## Monitoring & Analytics

### Call Metrics Dashboard

```python
from tools.communication.twilio_call_logs import TwilioCallLogs

# Get last 7 days of calls
logs = TwilioCallLogs(
    time_range_hours=168,  # 7 days
    limit=1000
).run()

# Analyze
total_calls = len(logs["calls"])
completed = [c for c in logs["calls"] if c["status"] == "completed"]
success_rate = len(completed) / total_calls * 100

avg_duration = sum(c["duration"] for c in completed) / len(completed)
total_cost = sum(float(c["cost"].replace("$", "")) for c in logs["calls"])

print(f"""
Call Analytics (Last 7 Days)
============================
Total Calls: {total_calls}
Completed: {len(completed)}
Success Rate: {success_rate:.1f}%
Avg Duration: {avg_duration:.0f} seconds
Total Cost: ${total_cost:.2f}
""")
```

---

## Troubleshooting

### Common Issues

**Issue 1: Call Not Connecting**
```python
# Check phone number format
# Must be E.164: +[country code]-[number]
# ✅ Correct: +1-555-123-4567
# ❌ Wrong: 555-123-4567
```

**Issue 2: Poor Call Quality**
```python
# Twilio automatically selects best route
# If quality issues persist:
# 1. Check internet connectivity
# 2. Verify Twilio service status
# 3. Contact Twilio support
```

**Issue 3: Transcription Errors**
```python
# Improve transcription accuracy:
# 1. Speak clearly in AI instructions
# 2. Avoid background noise
# 3. Use professional voice style
# 4. Specify language explicitly
```

---

## Integration with Agency-Swarm

### Multi-Agent Phone System

```python
from agency_swarm import Agency, Agent

# Receptionist agent handles incoming calls
receptionist = Agent(
    name="Receptionist",
    instructions="Answer phone calls and route to appropriate department",
    tools=[TwilioPhoneCall, TwilioCallLogs]
)

# Sales agent makes outbound calls
sales_agent = Agent(
    name="SalesAgent",
    instructions="Make sales calls and follow up with leads",
    tools=[TwilioPhoneCall, TwilioCallLogs]
)

# Support agent handles support calls
support_agent = Agent(
    name="SupportAgent",
    instructions="Provide customer support via phone",
    tools=[TwilioPhoneCall, TwilioCallLogs]
)

# Create agency
agency = Agency(
    [receptionist, sales_agent, support_agent],
    shared_instructions="Professional phone communication"
)
```

---

## Next Steps

1. ✅ Sign up for Twilio account
2. ✅ Get API credentials
3. ✅ Set environment variables
4. ✅ Test with sample call
5. ✅ Build your phone automation workflow
6. ✅ Monitor and optimize

---

## Resources

- **Twilio Docs:** https://www.twilio.com/docs
- **Voice API:** https://www.twilio.com/docs/voice
- **AI Voice:** https://www.twilio.com/docs/voice/ai
- **Pricing:** https://www.twilio.com/pricing
- **Support:** https://support.twilio.com

---

## Summary

**Twilio Integration Benefits:**
- ✅ Zero infrastructure cost
- ✅ 1-week integration vs 6-month build
- ✅ $0.02/min vs $200K+ upfront
- ✅ Global coverage (200+ countries)
- ✅ Zero maintenance
- ✅ Auto-scaling

**Result:** Professional AI phone calling at fraction of the cost of building from scratch. 🎯
