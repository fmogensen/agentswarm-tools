# AgentSwarm Tools - Complete Catalog

**Total Tools**: 101 production-ready tools
**Date**: November 22, 2025
**Repository**: agentswarm-tools

This catalog provides a complete reference of all tools organized by category with descriptions and example usage patterns.

---

## Table of Contents

1. [Agent Management](#agent-management) (2 tools)
2. [AI Intelligence](#ai-intelligence) (2 tools)
3. [Business Intelligence](#business-intelligence) (3 tools)
4. [Code Execution](#code-execution) (5 tools)
5. [Communication](#communication) (20 tools)
6. [Content Creation](#content-creation) (1 tool)
7. [Document Creation](#document-creation) (4 tools)
8. [Location Services](#location-services) (1 tool)
9. [Media Analysis](#media-analysis) (10 tools)
10. [Media Generation](#media-generation) (7 tools)
11. [Media Processing](#media-processing) (3 tools)
12. [Search & Information Retrieval](#search--information-retrieval) (8 tools)
13. [Storage & File Management](#storage--file-management) (4 tools)
14. [Utilities](#utilities) (8 tools)
15. [Visualization](#visualization) (16 tools)
16. [Web](#web) (1 tool)
17. [Web Content](#web-content) (4 tools)
18. [Workspace Integration](#workspace-integration) (5 tools)
19. [Examples](#examples) (1 tool)

---

## Agent Management

### 1. AgentStatus
**File**: `tools/agent_management/agent_status/agent_status.py`

**Description**: Monitor and retrieve the status of running agents including execution state, progress, and performance metrics.

**Key Parameters**:
- `agent_id`: Unique identifier for the agent
- `include_metrics`: Include performance metrics

**Example Usage**:
```python
from tools.agent_management.agent_status import AgentStatus

tool = AgentStatus(agent_id="agent_123", include_metrics=True)
result = tool.run()
# Returns: {"status": "running", "progress": 75, "metrics": {...}}
```

### 2. TaskQueueManager
**File**: `tools/agent_management/task_queue_manager/task_queue_manager.py`

**Description**: Manage task queues for agent workflows including adding, removing, prioritizing, and monitoring tasks.

**Key Parameters**:
- `action`: Operation to perform (add, remove, list, prioritize)
- `task_id`: Task identifier
- `priority`: Task priority level

**Example Usage**:
```python
from tools.agent_management.task_queue_manager import TaskQueueManager

tool = TaskQueueManager(action="add", task_id="task_456", priority="high")
result = tool.run()
# Returns: {"success": True, "queue_position": 1}
```

---

## AI Intelligence

### 1. RAGPipeline
**File**: `tools/ai_intelligence/rag_pipeline/rag_pipeline.py`

**Description**: Build and query vector databases for Retrieval-Augmented Generation (RAG) workflows. Supports multiple vector database backends including Pinecone, Chroma, Weaviate, Qdrant, and Milvus.

**Key Parameters**:
- `action`: Operation to perform (index, query, delete, list)
- `vector_db`: Vector database backend (pinecone, chroma, weaviate, qdrant, milvus)
- `collection_name`: Name of the vector collection
- `documents`: List of documents to index (for index action)
- `query_text`: Search query text (for query action)
- `top_k`: Number of results to return (default: 5)
- `metadata_filter`: Optional metadata filters for queries
- `embedding_model`: Embedding model to use (default: text-embedding-3-small)
- `chunk_size`: Document chunk size for indexing (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)

**Returns**:
```python
{
    "success": True,
    "result": {
        "action": "query",
        "matches": [
            {
                "id": "doc_123",
                "score": 0.92,
                "text": "Relevant passage...",
                "metadata": {"source": "file.pdf", "page": 5}
            }
        ],
        "total_results": 10
    },
    "metadata": {
        "vector_db": "pinecone",
        "collection": "knowledge_base",
        "processing_time": 0.45
    }
}
```

**Example Usage**:
```python
from tools.ai_intelligence.rag_pipeline import RAGPipeline

# Index documents into vector database
tool = RAGPipeline(
    action="index",
    vector_db="pinecone",
    collection_name="company_docs",
    documents=[
        {"text": "Company policy on remote work...", "metadata": {"source": "hr_policy.pdf"}},
        {"text": "Product specifications and features...", "metadata": {"source": "product_guide.pdf"}}
    ],
    chunk_size=500,
    embedding_model="text-embedding-3-small"
)
result = tool.run()

# Query the vector database
tool = RAGPipeline(
    action="query",
    vector_db="pinecone",
    collection_name="company_docs",
    query_text="What is the remote work policy?",
    top_k=5,
    metadata_filter={"source": "hr_policy.pdf"}
)
result = tool.run()
# Returns: Top 5 most relevant document chunks with similarity scores

# List all collections
tool = RAGPipeline(
    action="list",
    vector_db="chroma"
)
result = tool.run()
```

**Supported Vector Databases**:
- **Pinecone**: Fully managed, highly scalable vector database
- **Chroma**: Open-source embedding database
- **Weaviate**: Cloud-native vector search engine
- **Qdrant**: High-performance vector similarity search
- **Milvus**: Open-source vector database built for scale

### 2. DeepResearchAgent
**File**: `tools/ai_intelligence/deep_research_agent/deep_research_agent.py`

**Description**: Conduct comprehensive research across multiple sources including web search, academic papers, news, and documents. Automatically synthesizes findings into structured reports with citations.

**Key Parameters**:
- `research_query`: Research question or topic (required)
- `sources`: List of source types to search (web, scholar, news, documents)
- `depth`: Research depth (quick, standard, comprehensive)
- `max_sources`: Maximum sources to analyze (default: 20)
- `output_format`: Report format (markdown, pdf, docx, html)
- `include_citations`: Include source citations (default: True)
- `focus_areas`: Specific aspects to focus on
- `time_range`: Time filter for sources (day, week, month, year, all)
- `language`: Language for sources (default: en)

**Returns**:
```python
{
    "success": True,
    "result": {
        "report_url": "computer:///mnt/user-data/outputs/research_report.pdf",
        "summary": "Brief executive summary...",
        "key_findings": [
            "Finding 1: ...",
            "Finding 2: ..."
        ],
        "sources_analyzed": 25,
        "word_count": 3500,
        "sections": ["Introduction", "Methodology", "Findings", "Conclusions", "References"]
    },
    "metadata": {
        "research_duration": 45.2,
        "sources_by_type": {
            "web": 15,
            "scholar": 8,
            "news": 2
        },
        "quality_score": 8.5
    }
}
```

**Example Usage**:
```python
from tools.ai_intelligence.deep_research_agent import DeepResearchAgent

# Quick research on a topic
tool = DeepResearchAgent(
    research_query="What are the latest developments in quantum computing?",
    sources=["web", "scholar"],
    depth="quick",
    max_sources=10,
    output_format="markdown",
    time_range="month"
)
result = tool.run()

# Comprehensive research with specific focus
tool = DeepResearchAgent(
    research_query="Impact of artificial intelligence on healthcare diagnostics",
    sources=["web", "scholar", "news"],
    depth="comprehensive",
    max_sources=30,
    output_format="pdf",
    include_citations=True,
    focus_areas=[
        "diagnostic accuracy",
        "cost effectiveness",
        "patient outcomes",
        "regulatory challenges"
    ],
    time_range="year"
)
result = tool.run()
# Returns: 20+ page research report with citations and analysis

# Research with document integration
tool = DeepResearchAgent(
    research_query="Market analysis for electric vehicles in Europe",
    sources=["web", "scholar", "documents"],
    depth="standard",
    max_sources=20,
    output_format="docx",
    time_range="year"
)
result = tool.run()
```

**Research Depth Levels**:
- **quick**: 5-10 sources, 1000-2000 words, 5-10 minutes
- **standard**: 10-20 sources, 2000-4000 words, 15-30 minutes
- **comprehensive**: 20-50 sources, 4000-8000 words, 30-60 minutes

---

## Business Intelligence

### 3. DataAggregator
**File**: `tools/business/data_aggregator/data_aggregator.py`

**Description**: Aggregate data from multiple sources, perform calculations, and generate business insights.

**Key Parameters**:
- `data_sources`: List of data source URLs or paths
- `aggregation_method`: Method to use (sum, average, count, etc.)
- `group_by`: Fields to group results by

**Example Usage**:
```python
from tools.business.data_aggregator import DataAggregator

tool = DataAggregator(
    data_sources=["sales_q1.csv", "sales_q2.csv"],
    aggregation_method="sum",
    group_by=["region", "product"]
)
result = tool.run()
```

### 4. ReportGenerator
**File**: `tools/business/report_generator/report_generator.py`

**Description**: Generate comprehensive business reports with charts, tables, and analysis.

**Key Parameters**:
- `data`: Input data for the report
- `report_type`: Type of report (financial, sales, performance)
- `include_charts`: Include visualizations

**Example Usage**:
```python
from tools.business.report_generator import ReportGenerator

tool = ReportGenerator(
    data=sales_data,
    report_type="sales",
    include_charts=True
)
result = tool.run()
```

### 5. TrendAnalyzer
**File**: `tools/business/trend_analyzer/trend_analyzer.py`

**Description**: Analyze trends in time-series data, identify patterns, and forecast future values.

**Key Parameters**:
- `time_series_data`: Historical data points
- `analysis_type`: Type of analysis (trend, seasonal, forecast)
- `forecast_periods`: Number of periods to forecast

**Example Usage**:
```python
from tools.business.trend_analyzer import TrendAnalyzer

tool = TrendAnalyzer(
    time_series_data=monthly_sales,
    analysis_type="forecast",
    forecast_periods=6
)
result = tool.run()
```

---

## Code Execution

### 8. BashTool
**File**: `tools/code_execution/bash_tool/bash_tool.py`

**Description**: Execute bash commands in a secure sandbox environment with full system access.

**Key Parameters**:
- `command`: Bash command to execute
- `timeout`: Maximum execution time
- `working_directory`: Directory to execute from

**Example Usage**:
```python
from tools.code_execution.bash_tool import BashTool

tool = BashTool(command="ls -la /mnt/aidrive", timeout=30)
result = tool.run()
```

### 9. DownloadFileWrapper
**File**: `tools/code_execution/downloadfilewrapper_tool/downloadfilewrapper_tool.py`

**Description**: Download files from URLs and save to specified locations in the sandbox.

**Key Parameters**:
- `url`: URL to download from
- `destination`: Local path to save file
- `verify_ssl`: Verify SSL certificates

**Example Usage**:
```python
from tools.code_execution.downloadfilewrapper_tool import DownloadFileWrapper

tool = DownloadFileWrapper(
    url="https://example.com/data.csv",
    destination="/mnt/aidrive/data.csv"
)
result = tool.run()
```

### 10. MultiEdit
**File**: `tools/code_execution/multiedit_tool/multiedit_tool.py`

**Description**: Perform multiple file edits in a single operation with atomic transaction support.

**Key Parameters**:
- `edits`: List of edit operations
- `files`: Files to edit
- `atomic`: Ensure all edits succeed or rollback

**Example Usage**:
```python
from tools.code_execution.multiedit_tool import MultiEdit

tool = MultiEdit(
    edits=[
        {"file": "config.py", "old": "DEBUG = False", "new": "DEBUG = True"},
        {"file": "settings.py", "old": "LOG_LEVEL = 'ERROR'", "new": "LOG_LEVEL = 'DEBUG'"}
    ],
    atomic=True
)
result = tool.run()
```

### 11. Read
**File**: `tools/code_execution/read_tool/read_tool.py`

**Description**: Read file contents from the sandbox environment with support for various encodings.

**Key Parameters**:
- `file_path`: Path to file to read
- `encoding`: File encoding (default: utf-8)
- `max_lines`: Maximum lines to read

**Example Usage**:
```python
from tools.code_execution.read_tool import Read

tool = Read(file_path="/mnt/aidrive/data.txt", max_lines=100)
result = tool.run()
```

### 12. Write
**File**: `tools/code_execution/write_tool/write_tool.py`

**Description**: Write content to files in the sandbox environment with automatic directory creation.

**Key Parameters**:
- `file_path`: Path to file to write
- `content`: Content to write
- `mode`: Write mode (write, append)

**Example Usage**:
```python
from tools.code_execution.write_tool import Write

tool = Write(
    file_path="/mnt/user-data/outputs/report.txt",
    content="Analysis complete",
    mode="write"
)
result = tool.run()
```

---

## Communication

### 13. EmailDraft
**File**: `tools/communication/email_draft/email_draft.py`

**Description**: Create draft emails in Gmail with attachments and rich formatting.

**Key Parameters**:
- `to`: Recipient email addresses
- `subject`: Email subject
- `body`: Email body (supports HTML)
- `attachments`: List of file paths to attach

**Example Usage**:
```python
from tools.communication.email_draft import EmailDraft

tool = EmailDraft(
    to=["colleague@company.com"],
    subject="Q4 Report",
    body="Please review the attached report.",
    attachments=["/mnt/aidrive/q4_report.pdf"]
)
result = tool.run()
```

### 14. EmailSend
**File**: `tools/communication/email_send/email_send.py`

**Description**: Send emails directly via Gmail API with delivery confirmation.

**Key Parameters**:
- `to`: Recipient email addresses
- `subject`: Email subject
- `body`: Email body
- `cc`: CC recipients
- `bcc`: BCC recipients

**Example Usage**:
```python
from tools.communication.email_send import EmailSend

tool = EmailSend(
    to=["user@example.com"],
    subject="Meeting reminder",
    body="Don't forget our meeting tomorrow at 10 AM"
)
result = tool.run()
```

### 15. GmailRead
**File**: `tools/communication/gmail_read/gmail_read.py`

**Description**: Read email messages from Gmail with full content and metadata.

**Key Parameters**:
- `message_id`: Gmail message ID
- `include_attachments`: Download attachments
- `format`: Response format (full, metadata, minimal)

**Example Usage**:
```python
from tools.communication.gmail_read import GmailRead

tool = GmailRead(message_id="18c2f8a3b4d5e6f7", include_attachments=True)
result = tool.run()
```

### 16. GmailSearch
**File**: `tools/communication/gmail_search/gmail_search.py`

**Description**: Search Gmail messages using Gmail query syntax with advanced filtering.

**Key Parameters**:
- `query`: Gmail search query
- `max_results`: Maximum messages to return
- `label_ids`: Filter by labels

**Example Usage**:
```python
from tools.communication.gmail_search import GmailSearch

tool = GmailSearch(
    query="from:boss@company.com subject:urgent",
    max_results=10
)
result = tool.run()
```

### 17. GoogleCalendarCreateEventDraft
**File**: `tools/communication/google_calendar_create_event_draft/google_calendar_create_event_draft.py`

**Description**: Create draft calendar events in Google Calendar.

**Key Parameters**:
- `summary`: Event title
- `start_time`: Event start time
- `end_time`: Event end time
- `attendees`: List of attendee emails

**Example Usage**:
```python
from tools.communication.google_calendar_create_event_draft import GoogleCalendarCreateEventDraft

tool = GoogleCalendarCreateEventDraft(
    summary="Team Standup",
    start_time="2025-11-23T10:00:00Z",
    end_time="2025-11-23T10:30:00Z",
    attendees=["team@company.com"]
)
result = tool.run()
```

### 18. GoogleCalendarDeleteEvent
**File**: `tools/communication/google_calendar_delete_event/google_calendar_delete_event.py`

**Description**: Delete events from Google Calendar.

**Key Parameters**:
- `event_id`: Calendar event ID
- `calendar_id`: Calendar identifier

**Example Usage**:
```python
from tools.communication.google_calendar_delete_event import GoogleCalendarDeleteEvent

tool = GoogleCalendarDeleteEvent(event_id="abc123xyz", calendar_id="primary")
result = tool.run()
```

### 19. GoogleCalendarList
**File**: `tools/communication/google_calendar_list/google_calendar_list.py`

**Description**: List calendar events from Google Calendar with filtering options.

**Key Parameters**:
- `time_min`: Start of time range
- `time_max`: End of time range
- `max_results`: Maximum events to return

**Example Usage**:
```python
from tools.communication.google_calendar_list import GoogleCalendarList

tool = GoogleCalendarList(
    time_min="2025-11-22T00:00:00Z",
    time_max="2025-11-30T23:59:59Z",
    max_results=50
)
result = tool.run()
```

### 20. GoogleCalendarUpdateEvent
**File**: `tools/communication/google_calendar_update_event/google_calendar_update_event.py`

**Description**: Update existing Google Calendar events.

**Key Parameters**:
- `event_id`: Event to update
- `updates`: Dictionary of fields to update

**Example Usage**:
```python
from tools.communication.google_calendar_update_event import GoogleCalendarUpdateEvent

tool = GoogleCalendarUpdateEvent(
    event_id="event123",
    updates={"summary": "Updated Meeting Title"}
)
result = tool.run()
```

### 21. TwilioPhoneCall
**File**: `tools/communication/twilio_phone_call/twilio_phone_call.py`

**Description**: Initiate AI-powered phone calls using Twilio with natural voice synthesis, interactive responses, and call recording capabilities.

**Key Parameters**:
- `to_number`: Phone number to call (required, E.164 format: +1234567890)
- `from_number`: Twilio phone number to call from (required)
- `message`: Message to deliver or conversation script
- `voice`: Voice to use (alice, man, woman, google_female, google_male, amazon_polly)
- `language`: Language code (en-US, es-ES, fr-FR, de-DE, etc.)
- `enable_recording`: Record the call (default: False)
- `enable_transcription`: Transcribe call audio (default: False)
- `wait_for_response`: Wait for user response/interaction (default: False)
- `response_timeout`: Timeout for user response in seconds (default: 10)
- `max_call_duration`: Maximum call duration in seconds (default: 300)
- `callback_url`: URL for call status updates

**Returns**:
```python
{
    "success": True,
    "result": {
        "call_sid": "CA1234567890abcdef",
        "status": "initiated",
        "to_number": "+14155551234",
        "from_number": "+14155559876",
        "duration": None,  # Populated after call completes
        "recording_url": None,  # If recording enabled
        "transcription": None,  # If transcription enabled
        "cost": "0.015"
    },
    "metadata": {
        "provider": "twilio",
        "voice": "google_female",
        "language": "en-US",
        "timestamp": "2025-11-22T10:30:00Z"
    }
}
```

**Example Usage**:
```python
from tools.communication.twilio_phone_call import TwilioPhoneCall

# Simple reminder call
tool = TwilioPhoneCall(
    to_number="+14155551234",
    from_number="+14155559876",
    message="This is a reminder about your appointment tomorrow at 2 PM.",
    voice="google_female",
    language="en-US"
)
result = tool.run()

# Interactive call with recording
tool = TwilioPhoneCall(
    to_number="+14155551234",
    from_number="+14155559876",
    message="Hello! This is a customer satisfaction survey. Please rate your experience from 1 to 5.",
    voice="alice",
    enable_recording=True,
    enable_transcription=True,
    wait_for_response=True,
    response_timeout=15,
    max_call_duration=180
)
result = tool.run()

# Multi-language call
tool = TwilioPhoneCall(
    to_number="+34912345678",
    from_number="+14155559876",
    message="Hola, esta es una llamada de recordatorio sobre su cita.",
    voice="google_male",
    language="es-ES",
    enable_recording=True
)
result = tool.run()
```

**Supported Voices**:
- **alice**: Natural female voice (Twilio standard)
- **man**: Male voice (Twilio standard)
- **woman**: Female voice (Twilio standard)
- **google_female**: Google AI female voice (higher quality)
- **google_male**: Google AI male voice (higher quality)
- **amazon_polly**: Amazon Polly neural voices

**Use Cases**:
- Appointment reminders and confirmations
- Customer satisfaction surveys
- Payment reminders
- Service outage notifications
- Emergency alerts
- Two-factor authentication (2FA) calls

### 22. TwilioCallLogs
**File**: `tools/communication/twilio_call_logs/twilio_call_logs.py`

**Description**: Retrieve and analyze Twilio phone call history with transcriptions, recordings, and detailed metrics. Query call logs by date range, status, duration, and more.

**Key Parameters**:
- `action`: Operation to perform (list, get_details, get_recording, get_transcription)
- `date_start`: Start date for query (YYYY-MM-DD format)
- `date_end`: End date for query (YYYY-MM-DD format)
- `call_sid`: Specific call SID for details/recording/transcription
- `status`: Filter by call status (queued, initiated, ringing, in-progress, completed, busy, failed, no-answer, canceled)
- `from_number`: Filter by caller number
- `to_number`: Filter by recipient number
- `max_results`: Maximum calls to return (default: 50, max: 1000)
- `include_recordings`: Include recording URLs in results (default: False)
- `include_transcriptions`: Include transcriptions in results (default: False)
- `min_duration`: Minimum call duration in seconds
- `max_duration`: Maximum call duration in seconds

**Returns**:
```python
{
    "success": True,
    "result": {
        "total_calls": 125,
        "calls": [
            {
                "call_sid": "CA1234567890abcdef",
                "from_number": "+14155559876",
                "to_number": "+14155551234",
                "status": "completed",
                "duration": 185,
                "start_time": "2025-11-22T10:30:00Z",
                "end_time": "2025-11-22T10:33:05Z",
                "direction": "outbound-api",
                "cost": "0.015",
                "recording_url": "https://api.twilio.com/recordings/RE123...",
                "transcription": "Hello, this is a reminder...",
                "answered_by": "human"
            }
        ],
        "statistics": {
            "total_duration": 15420,
            "total_cost": 2.35,
            "avg_duration": 123.36,
            "completed_calls": 110,
            "failed_calls": 8,
            "no_answer": 7
        }
    },
    "metadata": {
        "date_range": "2025-11-01 to 2025-11-22",
        "filter_applied": "completed",
        "query_time": 0.45
    }
}
```

**Example Usage**:
```python
from tools.communication.twilio_call_logs import TwilioCallLogs

# List recent calls
tool = TwilioCallLogs(
    action="list",
    date_start="2025-11-01",
    date_end="2025-11-22",
    max_results=50
)
result = tool.run()

# Get calls with recordings and transcriptions
tool = TwilioCallLogs(
    action="list",
    date_start="2025-11-15",
    date_end="2025-11-22",
    status="completed",
    include_recordings=True,
    include_transcriptions=True,
    min_duration=60
)
result = tool.run()

# Get specific call details
tool = TwilioCallLogs(
    action="get_details",
    call_sid="CA1234567890abcdef"
)
result = tool.run()

# Get call recording
tool = TwilioCallLogs(
    action="get_recording",
    call_sid="CA1234567890abcdef"
)
result = tool.run()
# Returns: Recording URL and metadata

# Get call transcription
tool = TwilioCallLogs(
    action="get_transcription",
    call_sid="CA1234567890abcdef"
)
result = tool.run()
# Returns: Full transcription text

# Filter by phone numbers
tool = TwilioCallLogs(
    action="list",
    from_number="+14155559876",
    date_start="2025-11-01",
    date_end="2025-11-22",
    status="completed"
)
result = tool.run()

# Analyze failed calls
tool = TwilioCallLogs(
    action="list",
    date_start="2025-11-01",
    date_end="2025-11-22",
    status="failed",
    max_results=100
)
result = tool.run()
```

**Call Status Types**:
- **queued**: Call is queued and waiting to be initiated
- **initiated**: Call has been initiated
- **ringing**: Call is currently ringing
- **in-progress**: Call is currently active
- **completed**: Call completed successfully
- **busy**: Recipient was busy
- **failed**: Call failed to connect
- **no-answer**: Call was not answered
- **canceled**: Call was canceled before completion

**Use Cases**:
- Call center analytics and reporting
- Customer interaction tracking
- Call quality monitoring
- Billing and cost analysis
- Compliance and record keeping
- Customer satisfaction surveys analysis
- Campaign performance tracking

### 23. ReadEmailAttachments
**File**: `tools/communication/read_email_attachments/read_email_attachments.py`

**Description**: Extract and read attachments from Gmail messages.

**Key Parameters**:
- `message_id`: Gmail message ID
- `attachment_id`: Specific attachment to read
- `save_path`: Where to save attachment

**Example Usage**:
```python
from tools.communication.read_email_attachments import ReadEmailAttachments

tool = ReadEmailAttachments(
    message_id="msg123",
    save_path="/mnt/aidrive/attachments/"
)
result = tool.run()
```

### 24. SlackReadMessages
**File**: `tools/communication/slack_read_messages/slack_read_messages.py`

**Description**: Read messages from Slack channels and DMs.

**Key Parameters**:
- `channel_id`: Slack channel ID
- `limit`: Number of messages to retrieve
- `oldest`: Oldest timestamp to include

**Example Usage**:
```python
from tools.communication.slack_read_messages import SlackReadMessages

tool = SlackReadMessages(channel_id="C123ABC456", limit=50)
result = tool.run()
```

### 25. SlackSendMessage
**File**: `tools/communication/slack_send_message/slack_send_message.py`

**Description**: Send messages to Slack channels or users.

**Key Parameters**:
- `channel`: Channel or user ID
- `text`: Message text
- `attachments`: Rich message attachments

**Example Usage**:
```python
from tools.communication.slack_send_message import SlackSendMessage

tool = SlackSendMessage(
    channel="#general",
    text="Deployment complete!"
)
result = tool.run()
```

### 26. TeamsSendMessage
**File**: `tools/communication/teams_send_message/teams_send_message.py`

**Description**: Send messages to Microsoft Teams channels.

**Key Parameters**:
- `channel_id`: Teams channel ID
- `message`: Message content
- `mentions`: Users to mention

**Example Usage**:
```python
from tools.communication.teams_send_message import TeamsSendMessage

tool = TeamsSendMessage(
    channel_id="team_channel_123",
    message="Meeting starts in 5 minutes"
)
result = tool.run()
```

### 27. GoogleDocs
**File**: `tools/communication/google_docs/google_docs.py`

**Description**: Create and modify Google Docs using Google Docs API v1 with markdown support.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `content`: Document content (supports markdown)
- `title`: Document title (required for create mode)
- `document_id`: Existing document ID (required for modify mode)
- `share_with`: Optional list of email addresses for sharing
- `modify_action`: Action for modify mode ("append", "replace", "insert")

**Example Usage**:
```python
from tools.communication.google_docs import GoogleDocs

# Create new document
tool = GoogleDocs(
    mode="create",
    title="Q4 Business Report",
    content="# Executive Summary\n\nThis is **important** information.",
    share_with=["team@company.com"]
)
result = tool.run()

# Modify existing document
tool = GoogleDocs(
    mode="modify",
    document_id="abc123",
    content="## New Section\n\nAppended content here.",
    modify_action="append"
)
result = tool.run()
```

### 28. GoogleSheets
**File**: `tools/communication/google_sheets/google_sheets.py`

**Description**: Create and modify Google Sheets spreadsheets with data manipulation capabilities.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `title`: Spreadsheet title
- `spreadsheet_id`: Existing spreadsheet ID (required for modify mode)
- `data`: Data to write (2D array format)
- `range`: Cell range (e.g., "Sheet1!A1:C10")
- `share_with`: Optional list of email addresses

**Example Usage**:
```python
from tools.communication.google_sheets import GoogleSheets

# Create new spreadsheet
tool = GoogleSheets(
    mode="create",
    title="Sales Data Q4",
    data=[
        ["Product", "Units", "Revenue"],
        ["Product A", 100, 5000],
        ["Product B", 150, 7500]
    ],
    range="Sheet1!A1:C3"
)
result = tool.run()
```

### 29. GoogleSlides
**File**: `tools/communication/google_slides/google_slides.py`

**Description**: Create and modify Google Slides presentations programmatically.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `title`: Presentation title
- `presentation_id`: Existing presentation ID (required for modify mode)
- `slides`: List of slide content dictionaries
- `share_with`: Optional list of email addresses

**Example Usage**:
```python
from tools.communication.google_slides import GoogleSlides

# Create new presentation
tool = GoogleSlides(
    mode="create",
    title="Q4 Review Presentation",
    slides=[
        {"title": "Welcome", "content": "Q4 Business Review"},
        {"title": "Revenue Growth", "content": "Up 15% YoY"}
    ]
)
result = tool.run()
```

### 30. MeetingNotesAgent
**File**: `tools/communication/meeting_notes/meeting_notes.py`

**Description**: Transcribe meeting audio and generate structured notes with action items and key decisions.

**Key Parameters**:
- `audio_url`: URL to meeting audio file
- `export_formats`: List of export formats (notion, pdf, markdown)
- `include_transcript`: Whether to include full transcript
- `extract_action_items`: Whether to extract action items
- `identify_speakers`: Whether to identify different speakers
- `meeting_title`: Optional meeting title

**Example Usage**:
```python
from tools.communication.meeting_notes import MeetingNotesAgent

tool = MeetingNotesAgent(
    audio_url="https://example.com/meeting-2025-11-22.mp3",
    export_formats=["notion", "markdown"],
    extract_action_items=True,
    identify_speakers=True,
    meeting_title="Q4 Planning Meeting"
)
result = tool.run()
# Returns: notes_url, transcript_url, action_items count, duration
```

---

## Content Creation

### 31. WebsiteBuilder
**File**: `tools/content_creation/website_builder/website_builder.py`

**Description**: Generate professional, responsive websites from text descriptions or templates. Supports multi-page sites, custom styling, SEO optimization, and deployment to hosting platforms.

**Key Parameters**:
- `site_description`: Description of the website to build (required)
- `site_type`: Type of website (landing_page, portfolio, blog, business, ecommerce, documentation)
- `pages`: List of pages to create (default: ["home"])
- `color_scheme`: Color theme (light, dark, blue, green, custom)
- `custom_colors`: Custom color palette (primary, secondary, accent)
- `include_contact_form`: Add contact form (default: False)
- `include_blog`: Include blog functionality (default: False)
- `include_seo`: Optimize for SEO (default: True)
- `responsive`: Make mobile-responsive (default: True)
- `template`: Pre-built template to use (minimal, modern, creative, professional)
- `deploy`: Auto-deploy to hosting (default: False)
- `domain`: Custom domain for deployment

**Returns**:
```python
{
    "success": True,
    "result": {
        "website_url": "computer:///mnt/user-data/outputs/website/index.html",
        "preview_url": "https://preview.example.com/abc123",
        "deployment_url": "https://mysite.example.com",  # If deployed
        "pages": ["home", "about", "services", "contact"],
        "total_pages": 4,
        "assets": {
            "html_files": 4,
            "css_files": 2,
            "js_files": 3,
            "images": 8
        },
        "seo_score": 92,
        "mobile_responsive": True,
        "load_time": 1.2
    },
    "metadata": {
        "site_type": "business",
        "template": "modern",
        "build_time": 8.5,
        "technologies": ["HTML5", "CSS3", "JavaScript", "Bootstrap"]
    }
}
```

**Example Usage**:
```python
from tools.content_creation.website_builder import WebsiteBuilder

# Simple landing page
tool = WebsiteBuilder(
    site_description="A landing page for a SaaS product that helps teams collaborate better",
    site_type="landing_page",
    pages=["home"],
    color_scheme="blue",
    include_contact_form=True,
    template="modern"
)
result = tool.run()

# Full business website
tool = WebsiteBuilder(
    site_description="Professional website for a digital marketing agency",
    site_type="business",
    pages=["home", "services", "portfolio", "about", "contact"],
    color_scheme="custom",
    custom_colors={
        "primary": "#2C3E50",
        "secondary": "#E74C3C",
        "accent": "#3498DB"
    },
    include_contact_form=True,
    include_blog=True,
    include_seo=True,
    responsive=True,
    template="professional"
)
result = tool.run()

# Portfolio website with deployment
tool = WebsiteBuilder(
    site_description="Personal portfolio for a freelance graphic designer showcasing recent work",
    site_type="portfolio",
    pages=["home", "portfolio", "about", "contact"],
    color_scheme="dark",
    include_contact_form=True,
    template="creative",
    deploy=True,
    domain="myportfolio.com"
)
result = tool.run()
# Returns: Live website URL after deployment
```

**Site Types**:
- **landing_page**: Single-page marketing site
- **portfolio**: Showcase work and projects
- **blog**: Content-focused site with articles
- **business**: Multi-page company website
- **ecommerce**: Online store (basic)
- **documentation**: Technical documentation site

**Templates**:
- **minimal**: Clean, simple design
- **modern**: Contemporary with animations
- **creative**: Bold, artistic layouts
- **professional**: Corporate, business-focused

---

## Document Creation

### 32. CreateAgent
**File**: `tools/document_creation/create_agent/create_agent.py`

**Description**: Create comprehensive documents, presentations, spreadsheets, podcasts, websites, and more using AI.

**Key Parameters**:
- `task_type`: Type of content (docs, slides, sheets, podcast, deep_research, website, video_editing)
- `title`: Document title
- `content`: Content or instructions
- `format`: Output format

**Example Usage**:
```python
from tools.document_creation.create_agent import CreateAgent

# Create presentation
tool = CreateAgent(
    task_type="slides",
    title="Q4 Business Review",
    content="Create 10 slides covering sales performance, market trends, and 2026 strategy"
)
result = tool.run()

# Generate podcast
tool = CreateAgent(
    task_type="podcast",
    title="Tech Innovation Weekly",
    content="Discuss latest AI developments and their business impact"
)
result = tool.run()
```

### 33. OfficeDocsTool
**File**: `tools/document_creation/office_docs/office_docs.py`

**Description**: Generate or modify professional Word documents (.docx) from structured content with markdown support.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `content`: Document content (supports markdown)
- `template`: Template type (report, proposal, memo, letter, blank)
- `title`: Document title
- `include_toc`: Whether to include table of contents
- `font_name`: Font family (Calibri, Arial, Times New Roman)
- `font_size`: Base font size in points (default: 11)
- `output_format`: Output format (docx, pdf, both)
- `existing_file_url`: URL to existing document (for modify mode)

**Example Usage**:
```python
from tools.document_creation.office_docs import OfficeDocsTool

# Create new report
tool = OfficeDocsTool(
    mode="create",
    content="# Executive Summary\n\n## Key Findings\n\n- Revenue up 15%\n- Costs down 8%",
    template="report",
    title="Q4 2024 Financial Report",
    include_toc=True,
    output_format="pdf"
)
result = tool.run()

# Modify existing document
tool = OfficeDocsTool(
    mode="modify",
    existing_file_url="computer:///path/to/report.docx",
    content="\n\n# Appendix\n\nAdditional data...",
    title="Updated Q4 Report"
)
result = tool.run()
```

### 34. OfficeSlidesTool
**File**: `tools/document_creation/office_slides/office_slides.py`

**Description**: Create or modify PowerPoint presentations (.pptx) with structured content and layouts.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `title`: Presentation title
- `slides`: List of slide dictionaries with title and content
- `template`: Template style (business, modern, minimal, creative)
- `existing_file_url`: URL to existing presentation (for modify mode)

**Example Usage**:
```python
from tools.document_creation.office_slides import OfficeSlidesTool

# Create new presentation
tool = OfficeSlidesTool(
    mode="create",
    title="Q4 Business Review",
    slides=[
        {"title": "Welcome", "content": "Q4 2024 Performance", "layout": "title"},
        {"title": "Revenue Growth", "content": "Up 15% YoY\n- Product A: +20%\n- Product B: +12%", "layout": "content"},
        {"title": "Next Steps", "content": "1. Expand market\n2. Launch new product", "layout": "bullets"}
    ],
    template="business"
)
result = tool.run()
```

### 35. OfficeSheetsTool
**File**: `tools/document_creation/office_sheets/office_sheets.py`

**Description**: Generate or modify Excel spreadsheets (.xlsx) with data, formulas, and formatting.

**Key Parameters**:
- `mode`: Operation mode ("create" or "modify")
- `title`: Spreadsheet title
- `data`: 2D array of spreadsheet data
- `sheet_name`: Name of worksheet
- `include_formulas`: Whether to include auto-calculated formulas
- `existing_file_url`: URL to existing spreadsheet (for modify mode)

**Example Usage**:
```python
from tools.document_creation.office_sheets import OfficeSheetsTool

# Create new spreadsheet
tool = OfficeSheetsTool(
    mode="create",
    title="Sales Data Q4",
    data=[
        ["Product", "Q1", "Q2", "Q3", "Q4", "Total"],
        ["Product A", 1000, 1200, 1100, 1400, "=SUM(B2:E2)"],
        ["Product B", 800, 950, 900, 1100, "=SUM(B3:E3)"],
        ["Total", "=SUM(B2:B3)", "=SUM(C2:C3)", "=SUM(D2:D3)", "=SUM(E2:E3)", "=SUM(F2:F3)"]
    ],
    sheet_name="Q4 Sales",
    include_formulas=True
)
result = tool.run()
```

---

## Location Services

### 36. MapsSearch
**File**: `tools/location/maps_search/maps_search.py`

**Description**: Search for locations, get directions, and retrieve place information using Google Maps.

**Key Parameters**:
- `query`: Search query (address, business name, etc.)
- `location_bias`: Bias results to location
- `radius`: Search radius in meters

**Example Usage**:
```python
from tools.location.maps_search import MapsSearch

tool = MapsSearch(
    query="coffee shops near Times Square",
    radius=500
)
result = tool.run()
```

---

## Media Analysis

### 37. AnalyzeMediaContent
**File**: `tools/media_analysis/analyze_media_content/analyze_media_content.py`

**Description**: Analyze media files (images, videos, audio) for content, quality, and metadata.

**Key Parameters**:
- `media_urls`: URLs of media to analyze
- `analysis_type`: Type of analysis (content, quality, metadata)
- `instruction`: Specific analysis instructions

**Example Usage**:
```python
from tools.media_analysis.analyze_media_content import AnalyzeMediaContent

tool = AnalyzeMediaContent(
    media_urls=["https://example.com/video.mp4"],
    analysis_type="content",
    instruction="Identify all objects and activities in the video"
)
result = tool.run()
```

### 38. AudioEffects
**File**: `tools/media_analysis/audio_effects/audio_effects.py`

**Description**: Apply audio effects like reverb, echo, pitch shift, and equalization.

**Key Parameters**:
- `audio_url`: URL of audio file
- `effects`: List of effects to apply
- `output_format`: Output audio format

**Example Usage**:
```python
from tools.media_analysis.audio_effects import AudioEffects

tool = AudioEffects(
    audio_url="https://example.com/audio.mp3",
    effects=["reverb", "bass_boost"]
)
result = tool.run()
```

### 39. AudioTranscribe
**File**: `tools/media_analysis/audio_transcribe/audio_transcribe.py`

**Description**: Transcribe audio and video files to text with speaker identification and timestamps.

**Key Parameters**:
- `audio_url`: URL of audio/video file
- `language`: Language code
- `include_timestamps`: Add timestamps to transcript

**Example Usage**:
```python
from tools.media_analysis.audio_transcribe import AudioTranscribe

tool = AudioTranscribe(
    audio_url="https://example.com/meeting.mp3",
    language="en",
    include_timestamps=True
)
result = tool.run()
```

### 40. BatchUnderstandVideos
**File**: `tools/media_analysis/batch_understand_videos/batch_understand_videos.py`

**Description**: Analyze multiple videos in batch for efficient processing.

**Key Parameters**:
- `video_urls`: List of video URLs
- `instruction`: Analysis instructions
- `parallel`: Process in parallel

**Example Usage**:
```python
from tools.media_analysis.batch_understand_videos import BatchUnderstandVideos

tool = BatchUnderstandVideos(
    video_urls=["video1.mp4", "video2.mp4", "video3.mp4"],
    instruction="Summarize each video in 2 sentences",
    parallel=True
)
result = tool.run()
```

### 41. BatchVideoAnalysis
**File**: `tools/media_analysis/batch_video_analysis/batch_video_analysis.py`

**Description**: Perform detailed analysis on multiple videos including scene detection and object tracking.

**Key Parameters**:
- `videos`: List of video sources
- `analysis_tasks`: Tasks to perform
- `output_format`: Format of analysis results

**Example Usage**:
```python
from tools.media_analysis.batch_video_analysis import BatchVideoAnalysis

tool = BatchVideoAnalysis(
    videos=["commercial1.mp4", "commercial2.mp4"],
    analysis_tasks=["scene_detection", "object_tracking", "text_extraction"]
)
result = tool.run()
```

### 42. ExtractAudioFromVideo
**File**: `tools/media_analysis/extract_audio_from_video/extract_audio_from_video.py`

**Description**: Extract audio tracks from video files.

**Key Parameters**:
- `video_url`: URL of video file
- `output_format`: Audio format (mp3, wav, aac)
- `quality`: Audio quality setting

**Example Usage**:
```python
from tools.media_analysis.extract_audio_from_video import ExtractAudioFromVideo

tool = ExtractAudioFromVideo(
    video_url="https://example.com/interview.mp4",
    output_format="mp3",
    quality="high"
)
result = tool.run()
```

### 43. MergeAudio
**File**: `tools/media_analysis/merge_audio/merge_audio.py`

**Description**: Merge multiple audio files into a single file with crossfading support.

**Key Parameters**:
- `audio_urls`: List of audio file URLs
- `crossfade_duration`: Crossfade duration in seconds
- `output_format`: Output format

**Example Usage**:
```python
from tools.media_analysis.merge_audio import MergeAudio

tool = MergeAudio(
    audio_urls=["intro.mp3", "main.mp3", "outro.mp3"],
    crossfade_duration=2.0,
    output_format="mp3"
)
result = tool.run()
```

### 44. UnderstandImages
**File**: `tools/media_analysis/understand_images/understand_images.py`

**Description**: Analyze images for content, objects, text, faces, and context.

**Key Parameters**:
- `image_urls`: URLs of images to analyze
- `instruction`: What to look for in images
- `detail_level`: Level of detail (low, medium, high)

**Example Usage**:
```python
from tools.media_analysis.understand_images import UnderstandImages

tool = UnderstandImages(
    image_urls=["https://example.com/product.jpg"],
    instruction="Describe the product features and identify the brand",
    detail_level="high"
)
result = tool.run()
```

### 45. UnderstandVideo
**File**: `tools/media_analysis/understand_video/understand_video.py`

**Description**: Analyze video content for scenes, actions, objects, and context.

**Key Parameters**:
- `video_url`: URL of video to analyze
- `instruction`: Analysis instructions
- `sample_rate`: How often to sample frames

**Example Usage**:
```python
from tools.media_analysis.understand_video import UnderstandVideo

tool = UnderstandVideo(
    video_url="https://example.com/tutorial.mp4",
    instruction="Summarize the main steps shown in this tutorial",
    sample_rate="every_5_seconds"
)
result = tool.run()
```

### 46. VideoMetadataExtractor
**File**: `tools/media_analysis/video_metadata_extractor/video_metadata_extractor.py`

**Description**: Extract technical metadata from video files (duration, resolution, codec, bitrate).

**Key Parameters**:
- `video_url`: URL of video file
- `include_audio`: Include audio metadata
- `include_subtitles`: Extract subtitle tracks

**Example Usage**:
```python
from tools.media_analysis.video_metadata_extractor import VideoMetadataExtractor

tool = VideoMetadataExtractor(
    video_url="https://example.com/movie.mp4",
    include_audio=True,
    include_subtitles=True
)
result = tool.run()
```

---

## Media Generation

### 47. AudioGeneration
**File**: `tools/media_generation/audio_generation/audio_generation.py`

**Description**: Generate audio content including music, sound effects, and voice synthesis.

**Key Parameters**:
- `model`: AI model to use (google/gemini-2.5-pro-preview-tts, elevenlabs/v3-tts, CassetteAI/music-generator)
- `query`: Description of audio to generate
- `duration`: Length in seconds
- `task_summary`: User-facing task description

**Example Usage**:
```python
from tools.media_generation.audio_generation import AudioGeneration

# Generate music
tool = AudioGeneration(
    model="CassetteAI/music-generator",
    query="upbeat jazz piano background music",
    duration=60,
    task_summary="Creating background music for presentation"
)
result = tool.run()

# Generate voice
tool = AudioGeneration(
    model="google/gemini-2.5-pro-preview-tts",
    query="Welcome to our podcast. Today we'll discuss AI innovations.",
    task_summary="Generating podcast intro"
)
result = tool.run()
```

### 48. ImageGeneration
**File**: `tools/media_generation/image_generation/image_generation.py`

**Description**: Generate images from text descriptions using various AI models.

**Key Parameters**:
- `model`: Model to use (flux-pro, gpt-image-1, imagen4, ideogram/V_3, rmbg)
- `query`: Image description
- `aspect_ratio`: Image dimensions
- `task_summary`: User-facing description

**Example Usage**:
```python
from tools.media_generation.image_generation import ImageGeneration

tool = ImageGeneration(
    model="imagen4",
    query="A modern office workspace with large windows, natural light, and plants",
    aspect_ratio="16:9",
    task_summary="Generating office environment image"
)
result = tool.run()
```

### 49. ImageStyleTransfer
**File**: `tools/media_generation/image_style_transfer/image_style_transfer.py`

**Description**: Apply artistic styles to images using neural style transfer.

**Key Parameters**:
- `source_image`: Image to transform
- `style`: Style to apply (impressionist, watercolor, etc.)
- `intensity`: Style intensity (0-100)

**Example Usage**:
```python
from tools.media_generation.image_style_transfer import ImageStyleTransfer

tool = ImageStyleTransfer(
    source_image="https://example.com/photo.jpg",
    style="impressionist",
    intensity=75
)
result = tool.run()
```

### 50. PodcastGenerator
**File**: `tools/media_generation/podcast_generator/podcast_generator.py`

**Description**: Generate multi-speaker AI podcasts with natural conversations, background music, sound effects, and professional production quality. Supports scripted or AI-generated dialogue.

**Key Parameters**:
- `topic`: Podcast topic or theme (required)
- `script`: Pre-written dialogue script (optional, AI generates if not provided)
- `speakers`: List of speaker configurations
  - `name`: Speaker name
  - `voice`: Voice model (google_female, google_male, elevenlabs/professional, etc.)
  - `personality`: Speaking style (energetic, calm, authoritative, friendly)
- `duration`: Target duration in minutes (default: 10)
- `include_intro`: Add podcast intro music (default: True)
- `include_outro`: Add podcast outro music (default: True)
- `background_music`: Background music type (none, ambient, upbeat, corporate)
- `music_volume`: Background music volume 0-100 (default: 20)
- `sound_effects`: Include sound effects (default: False)
- `format`: Output format (mp3, wav, m4a)
- `quality`: Audio quality (standard, high, ultra)
- `export_transcript`: Export text transcript (default: True)

**Returns**:
```python
{
    "success": True,
    "result": {
        "audio_url": "computer:///mnt/user-data/outputs/podcast_episode_001.mp3",
        "transcript_url": "computer:///mnt/user-data/outputs/transcript.txt",
        "duration": 600,  # seconds
        "file_size": "15.2 MB",
        "speakers": ["Alex", "Jordan"],
        "segments": 15,
        "music_tracks": ["intro", "outro", "background"],
        "quality_score": 9.2
    },
    "metadata": {
        "topic": "AI in Healthcare",
        "generation_time": 45.3,
        "voices_used": ["google_female", "elevenlabs/professional_male"],
        "total_words": 1500,
        "format": "mp3",
        "bitrate": "192kbps"
    }
}
```

**Example Usage**:
```python
from tools.media_generation.podcast_generator import PodcastGenerator

# AI-generated podcast conversation
tool = PodcastGenerator(
    topic="The future of electric vehicles and sustainable transportation",
    speakers=[
        {"name": "Alex", "voice": "google_female", "personality": "enthusiastic"},
        {"name": "Jordan", "voice": "elevenlabs/professional_male", "personality": "analytical"}
    ],
    duration=15,
    include_intro=True,
    include_outro=True,
    background_music="ambient",
    music_volume=15,
    format="mp3",
    quality="high"
)
result = tool.run()

# Scripted podcast with custom dialogue
script = """
[Alex]: Welcome to Tech Talk Today! I'm Alex.
[Jordan]: And I'm Jordan. Today we're discussing artificial intelligence in healthcare.
[Alex]: Jordan, what excites you most about AI in medicine?
[Jordan]: The diagnostic capabilities are revolutionary. AI can now detect diseases earlier than human doctors in many cases.
[Alex]: That's incredible! Can you give us an example?
[Jordan]: Sure! AI models analyzing medical imaging can detect certain cancers months before traditional methods.
"""

tool = PodcastGenerator(
    topic="AI in Healthcare",
    script=script,
    speakers=[
        {"name": "Alex", "voice": "google_female", "personality": "friendly"},
        {"name": "Jordan", "voice": "google_male", "personality": "authoritative"}
    ],
    include_intro=True,
    include_outro=True,
    background_music="corporate",
    music_volume=20,
    sound_effects=True,
    format="mp3",
    quality="ultra",
    export_transcript=True
)
result = tool.run()

# Quick interview-style podcast
tool = PodcastGenerator(
    topic="Startup founder interview about building a successful SaaS company",
    speakers=[
        {"name": "Host", "voice": "elevenlabs/professional_female", "personality": "friendly"},
        {"name": "Guest", "voice": "google_male", "personality": "energetic"}
    ],
    duration=20,
    background_music="upbeat",
    music_volume=10,
    format="mp3"
)
result = tool.run()
```

**Voice Options**:
- **google_female**: Natural Google AI female voice
- **google_male**: Natural Google AI male voice
- **elevenlabs/professional_female**: High-quality professional female
- **elevenlabs/professional_male**: High-quality professional male
- **elevenlabs/energetic**: Energetic, dynamic voice
- **elevenlabs/calm**: Calm, soothing voice

**Personality Styles**:
- **energetic**: Upbeat, fast-paced delivery
- **calm**: Relaxed, measured speaking
- **authoritative**: Confident, expert tone
- **friendly**: Warm, conversational tone
- **analytical**: Thoughtful, precise delivery

**Background Music Types**:
- **ambient**: Soft, atmospheric background
- **upbeat**: Energetic, positive music
- **corporate**: Professional, neutral tones
- **none**: No background music

**Use Cases**:
- Educational podcast series
- Marketing and brand storytelling
- Interview simulations
- Training and onboarding content
- Book summaries and reviews
- News commentary and analysis
- Product launch announcements

### 51. TextToSpeechAdvanced
**File**: `tools/media_generation/text_to_speech_advanced/text_to_speech_advanced.py`

**Description**: Convert text to speech with advanced voice control and emotional expression.

**Key Parameters**:
- `text`: Text to convert
- `voice`: Voice to use
- `emotion`: Emotional tone
- `speed`: Speech rate

**Example Usage**:
```python
from tools.media_generation.text_to_speech_advanced import TextToSpeechAdvanced

tool = TextToSpeechAdvanced(
    text="Thank you for your purchase. Your order will arrive tomorrow.",
    voice="professional_female",
    emotion="friendly",
    speed=1.0
)
result = tool.run()
```

### 52. VideoEffects
**File**: `tools/media_generation/video_effects/video_effects.py`

**Description**: Apply visual effects to videos including filters, transitions, and color grading.

**Key Parameters**:
- `video_url`: Source video
- `effects`: Effects to apply
- `output_resolution`: Output resolution

**Example Usage**:
```python
from tools.media_generation.video_effects import VideoEffects

tool = VideoEffects(
    video_url="https://example.com/raw_footage.mp4",
    effects=["color_grade", "stabilization", "slow_motion"],
    output_resolution="1080p"
)
result = tool.run()
```

### 53. VideoGeneration
**File**: `tools/media_generation/video_generation/video_generation.py`

**Description**: Generate videos from text descriptions using AI.

**Key Parameters**:
- `model`: Model to use (gemini/veo3, kling/v2.5-turbo, kling/v2.5-pro, sora-2)
- `query`: Video description
- `duration`: Video length
- `aspect_ratio`: Video dimensions
- `task_summary`: User-facing description

**Example Usage**:
```python
from tools.media_generation.video_generation import VideoGeneration

tool = VideoGeneration(
    model="gemini/veo3",
    query="A peaceful sunset over ocean waves with seagulls flying",
    duration=10,
    aspect_ratio="16:9",
    task_summary="Generating nature video for presentation"
)
result = tool.run()
```

---

## Media Processing

### 54. PhotoEditorTool
**File**: `tools/media_processing/photo_editor/photo_editor.py`

**Description**: Perform advanced photo editing operations on existing images including resize, crop, filters, and effects.

**Key Parameters**:
- `image_url`: URL to source image
- `operations`: List of editing operations to apply
- `output_format`: Output format (png, jpg, webp)
- `quality`: Output quality 1-100 (for jpg)

**Supported Operations**:
- **resize**: Change image dimensions
- **crop**: Crop to specific region
- **rotate**: Rotate by degrees
- **flip**: Flip horizontal or vertical
- **filter**: Apply filters (brightness, contrast, saturation, blur, sharpen)
- **background_remove**: Remove image background

**Example Usage**:
```python
from tools.media_processing.photo_editor import PhotoEditorTool

# Resize and enhance photo
tool = PhotoEditorTool(
    image_url="https://example.com/photo.jpg",
    operations=[
        {"type": "resize", "width": 1920, "height": 1080},
        {"type": "filter", "name": "brightness", "value": 1.2},
        {"type": "filter", "name": "contrast", "value": 1.1},
        {"type": "filter", "name": "sharpen", "amount": 1.3}
    ],
    output_format="jpg",
    quality=95
)
result = tool.run()

# Crop and apply artistic filter
tool = PhotoEditorTool(
    image_url="https://example.com/landscape.jpg",
    operations=[
        {"type": "crop", "x": 0, "y": 0, "width": 800, "height": 600},
        {"type": "filter", "name": "saturation", "value": 1.5},
        {"type": "filter", "name": "blur", "radius": 2}
    ],
    output_format="png"
)
result = tool.run()
```

### 55. VideoClipper
**File**: `tools/media_processing/video_clipper/video_clipper.py`

**Description**: AI-powered video highlight extraction that automatically identifies and clips the most engaging, important, or relevant segments from long-form videos. Perfect for creating social media clips, trailers, summaries, and promotional content.

**Key Parameters**:
- `video_url`: URL to source video (required)
- `clip_strategy`: Strategy for selecting clips (highlights, action, dialogue, topic_based, time_based, custom)
- `target_duration`: Total duration of output clips in seconds (default: 60)
- `num_clips`: Number of separate clips to generate (default: 1)
- `clip_length`: Individual clip length in seconds (default: 15)
- `criteria`: Custom criteria for clip selection
  - `keywords`: Keywords to focus on
  - `min_motion`: Minimum motion threshold (0-100)
  - `min_audio_energy`: Minimum audio energy (0-100)
  - `face_presence`: Require faces in clips
  - `scene_changes`: Include scene transitions
- `output_format`: Output format (mp4, mov, webm)
- `resolution`: Output resolution (1080p, 720p, 480p, original)
- `add_transitions`: Add transitions between clips (default: False)
- `add_captions`: Auto-generate captions (default: False)
- `quality`: Output quality (low, medium, high, ultra)

**Returns**:
```python
{
    "success": True,
    "result": {
        "clips": [
            {
                "clip_url": "computer:///mnt/user-data/outputs/highlight_1.mp4",
                "start_time": 125.5,
                "end_time": 140.5,
                "duration": 15.0,
                "score": 9.2,
                "reason": "High action and dialogue intensity",
                "thumbnail": "computer:///mnt/user-data/outputs/thumb_1.jpg"
            },
            {
                "clip_url": "computer:///mnt/user-data/outputs/highlight_2.mp4",
                "start_time": 340.0,
                "end_time": 355.0,
                "duration": 15.0,
                "score": 8.8,
                "reason": "Key topic discussion",
                "thumbnail": "computer:///mnt/user-data/outputs/thumb_2.jpg"
            }
        ],
        "merged_clip_url": "computer:///mnt/user-data/outputs/all_highlights.mp4",
        "total_clips": 2,
        "total_duration": 30.0,
        "original_duration": 1800.0,
        "compression_ratio": "1.67%"
    },
    "metadata": {
        "strategy": "highlights",
        "processing_time": 125.4,
        "scenes_analyzed": 145,
        "algorithm": "AI-motion-audio-analysis"
    }
}
```

**Example Usage**:
```python
from tools.media_processing.video_clipper import VideoClipper

# Extract top highlights automatically
tool = VideoClipper(
    video_url="https://example.com/webinar_recording.mp4",
    clip_strategy="highlights",
    num_clips=5,
    clip_length=15,
    output_format="mp4",
    resolution="1080p",
    add_captions=True
)
result = tool.run()
# Returns: 5 best 15-second clips with captions

# Extract action-packed moments
tool = VideoClipper(
    video_url="https://example.com/sports_game.mp4",
    clip_strategy="action",
    target_duration=60,
    num_clips=4,
    criteria={
        "min_motion": 70,
        "scene_changes": True
    },
    add_transitions=True,
    quality="ultra"
)
result = tool.run()

# Topic-based clip extraction
tool = VideoClipper(
    video_url="https://example.com/conference_talk.mp4",
    clip_strategy="topic_based",
    num_clips=3,
    clip_length=30,
    criteria={
        "keywords": ["artificial intelligence", "machine learning", "future trends"],
        "face_presence": True,
        "min_audio_energy": 60
    },
    add_captions=True,
    resolution="720p"
)
result = tool.run()
# Returns: 3 clips focused on AI/ML discussion

# Custom time-based clips
tool = VideoClipper(
    video_url="https://example.com/interview.mp4",
    clip_strategy="time_based",
    num_clips=3,
    criteria={
        "time_ranges": [
            {"start": "00:02:15", "end": "00:02:45"},
            {"start": "00:15:30", "end": "00:16:00"},
            {"start": "00:28:00", "end": "00:28:30"}
        ]
    },
    add_transitions=True,
    output_format="mp4"
)
result = tool.run()

# Dialogue-focused clips
tool = VideoClipper(
    video_url="https://example.com/podcast_video.mp4",
    clip_strategy="dialogue",
    num_clips=5,
    clip_length=20,
    criteria={
        "min_audio_energy": 50,
        "keywords": ["startup", "funding", "growth"],
        "face_presence": True
    },
    add_captions=True
)
result = tool.run()
```

**Clip Strategies**:
- **highlights**: AI identifies most engaging moments (motion + audio + scene analysis)
- **action**: High-motion, dynamic segments
- **dialogue**: Segments with active speaking and conversation
- **topic_based**: Clips matching specific keywords/topics
- **time_based**: Extract specific time ranges
- **custom**: User-defined criteria combination

**Use Cases**:
- Social media content from long videos
- Video trailers and teasers
- Meeting and webinar highlights
- Sports game highlights
- Tutorial key moments extraction
- Podcast video snippets
- Product demo key features
- Customer testimonial clips

### 56. VideoEditorTool
**File**: `tools/media_processing/video_editor/video_editor.py`

**Description**: Edit videos using FFmpeg including trim, merge, add audio, apply effects, and format conversion.

**Key Parameters**:
- `video_url`: URL to source video
- `operations`: List of editing operations
- `output_format`: Output format (mp4, avi, mov, webm)
- `quality`: Output quality preset (low, medium, high, ultra)

**Supported Operations**:
- **trim**: Cut video to specific time range
- **merge**: Combine multiple videos
- **add_audio**: Add or replace audio track
- **resize**: Change video resolution
- **speed**: Adjust playback speed
- **watermark**: Add watermark overlay
- **effects**: Apply visual effects

**Example Usage**:
```python
from tools.media_processing.video_editor import VideoEditorTool

# Trim and resize video
tool = VideoEditorTool(
    video_url="https://example.com/video.mp4",
    operations=[
        {"type": "trim", "start_time": "00:00:10", "end_time": "00:02:30"},
        {"type": "resize", "width": 1280, "height": 720},
        {"type": "speed", "factor": 1.5}
    ],
    output_format="mp4",
    quality="high"
)
result = tool.run()

# Add watermark and audio
tool = VideoEditorTool(
    video_url="https://example.com/raw_video.mp4",
    operations=[
        {"type": "watermark", "image_url": "https://example.com/logo.png", "position": "bottom-right"},
        {"type": "add_audio", "audio_url": "https://example.com/background.mp3", "volume": 0.3}
    ],
    output_format="mp4"
)
result = tool.run()
```

---

## Search & Information Retrieval

### 57. FinancialReport
**File**: `tools/search/financial_report/financial_report.py`

**Description**: Retrieve financial reports and SEC filings for public companies.

**Key Parameters**:
- `symbol`: Stock ticker symbol
- `report_type`: Type of report (10-K, 10-Q, 8-K)
- `year`: Report year

**Example Usage**:
```python
from tools.search.financial_report import FinancialReport

tool = FinancialReport(
    symbol="AAPL",
    report_type="10-K",
    year=2024
)
result = tool.run()
```

### 58. GoogleProductSearch
**File**: `tools/search/google_product_search/google_product_search.py`

**Description**: Search for products using Google Shopping with price comparison.

**Key Parameters**:
- `query`: Product search query
- `max_results`: Maximum results to return
- `price_range`: Price filter

**Example Usage**:
```python
from tools.search.google_product_search import GoogleProductSearch

tool = GoogleProductSearch(
    query="wireless headphones",
    max_results=20,
    price_range={"min": 50, "max": 200}
)
result = tool.run()
```

### 59. ImageSearch
**File**: `tools/search/image_search/image_search.py`

**Description**: Search for images across the web with filtering options.

**Key Parameters**:
- `query`: Image search query
- `max_results`: Maximum images to return
- `image_type`: Type filter (photo, clipart, line_drawing)

**Example Usage**:
```python
from tools.search.image_search import ImageSearch

tool = ImageSearch(
    query="mountain landscapes",
    max_results=10,
    image_type="photo"
)
result = tool.run()
```

### 60. ProductSearch
**File**: `tools/search/product_search/product_search.py`

**Description**: Search for products across e-commerce platforms.

**Key Parameters**:
- `query`: Product search query
- `category`: Product category
- `sort_by`: Sort order (price, rating, relevance)

**Example Usage**:
```python
from tools.search.product_search import ProductSearch

tool = ProductSearch(
    query="laptop stand",
    category="office_supplies",
    sort_by="rating"
)
result = tool.run()
```

### 61. ScholarSearch
**File**: `tools/search/scholar_search/scholar_search.py`

**Description**: Search academic papers and research publications using Google Scholar.

**Key Parameters**:
- `query`: Research query
- `year_min`: Minimum publication year
- `max_results`: Maximum papers to return

**Example Usage**:
```python
from tools.search.scholar_search import ScholarSearch

tool = ScholarSearch(
    query="machine learning in healthcare",
    year_min=2020,
    max_results=10
)
result = tool.run()
```

### 62. StockPrice
**File**: `tools/search/stock_price/stock_price.py`

**Description**: Get real-time and historical stock price data.

**Key Parameters**:
- `symbol`: Stock ticker symbol
- `time_range`: Time period (1d, 1w, 1m, 1y)
- `include_metrics`: Include financial metrics

**Example Usage**:
```python
from tools.search.stock_price import StockPrice

tool = StockPrice(
    symbol="TSLA",
    time_range="1m",
    include_metrics=True
)
result = tool.run()
```

### 63. VideoSearch
**File**: `tools/search/video_search/video_search.py`

**Description**: Search for videos across platforms like YouTube with metadata.

**Key Parameters**:
- `query`: Video search query
- `max_results`: Maximum videos to return
- `duration`: Video length filter

**Example Usage**:
```python
from tools.search.video_search import VideoSearch

tool = VideoSearch(
    query="python tutorial for beginners",
    max_results=10,
    duration="medium"
)
result = tool.run()
```

### 64. WebSearch
**File**: `tools/search/web_search/web_search.py`

**Description**: Perform web searches with comprehensive results including snippets and metadata.

**Key Parameters**:
- `query`: Search query
- `max_results`: Maximum results
- `time_range`: Time filter (day, week, month, year)

**Example Usage**:
```python
from tools.search.web_search import WebSearch

tool = WebSearch(
    query="latest AI developments 2025",
    max_results=10,
    time_range="week"
)
result = tool.run()
```

---

## Storage & File Management

### 65. AIDriveTool
**File**: `tools/storage/aidrive_tool/aidrive_tool.py`

**Description**: Manage files in AI Drive cloud storage with upload, download, list, and delete operations.

**Key Parameters**:
- `action`: Operation (upload, download, list, delete, search)
- `path`: File path in AI Drive
- `local_path`: Local file path

**Example Usage**:
```python
from tools.storage.aidrive_tool import AIDriveTool

# Upload file
tool = AIDriveTool(
    action="upload",
    local_path="/tmp/report.pdf",
    path="/documents/report.pdf"
)
result = tool.run()

# List files
tool = AIDriveTool(action="list", path="/documents")
result = tool.run()
```

### 66. FileFormatConverter
**File**: `tools/storage/file_format_converter/file_format_converter.py`

**Description**: Convert files between formats (PDF, DOCX, images, audio, video).

**Key Parameters**:
- `source_file`: Input file path or URL
- `target_format`: Desired output format
- `options`: Conversion options

**Example Usage**:
```python
from tools.storage.file_format_converter import FileFormatConverter

tool = FileFormatConverter(
    source_file="/mnt/aidrive/document.docx",
    target_format="pdf",
    options={"quality": "high"}
)
result = tool.run()
```

### 67. OneDriveFileRead
**File**: `tools/storage/onedrive_file_read/onedrive_file_read.py`

**Description**: Read file contents from Microsoft OneDrive.

**Key Parameters**:
- `file_id`: OneDrive file ID
- `encoding`: File encoding
- `range`: Byte range to read

**Example Usage**:
```python
from tools.storage.onedrive_file_read import OneDriveFileRead

tool = OneDriveFileRead(
    file_id="01ABCDEF123456789",
    encoding="utf-8"
)
result = tool.run()
```

### 68. OneDriveSearch
**File**: `tools/storage/onedrive_search/onedrive_search.py`

**Description**: Search for files in Microsoft OneDrive.

**Key Parameters**:
- `query`: Search query
- `folder`: Specific folder to search
- `file_type`: Filter by file type

**Example Usage**:
```python
from tools.storage.onedrive_search import OneDriveSearch

tool = OneDriveSearch(
    query="quarterly report",
    folder="/Documents",
    file_type="pdf"
)
result = tool.run()
```

---

## Utilities

### 69. AskForClarification
**File**: `tools/utils/ask_for_clarification/ask_for_clarification.py`

**Description**: Request clarification from users when requirements are ambiguous.

**Key Parameters**:
- `question`: Question to ask
- `options`: Multiple choice options (optional)
- `context`: Background context

**Example Usage**:
```python
from tools.utils.ask_for_clarification import AskForClarification

tool = AskForClarification(
    question="Which format would you prefer for the report?",
    options=["PDF", "PowerPoint", "Word Document"],
    context="Preparing quarterly business review"
)
result = tool.run()
```

### 70. BatchProcessor
**File**: `tools/utils/batch_processor/batch_processor.py`

**Description**: Process multiple items in batch with parallel execution support.

**Key Parameters**:
- `items`: List of items to process
- `operation`: Operation to perform
- `parallel`: Use parallel processing
- `batch_size`: Items per batch

**Example Usage**:
```python
from tools.utils.batch_processor import BatchProcessor

tool = BatchProcessor(
    items=["file1.txt", "file2.txt", "file3.txt"],
    operation="analyze",
    parallel=True,
    batch_size=10
)
result = tool.run()
```

### 71. CreateProfile
**File**: `tools/utils/create_profile/create_profile.py`

**Description**: Create user or entity profiles with structured data.

**Key Parameters**:
- `profile_type`: Type of profile (user, company, product)
- `data`: Profile information
- `template`: Profile template to use

**Example Usage**:
```python
from tools.utils.create_profile import CreateProfile

tool = CreateProfile(
    profile_type="company",
    data={
        "name": "Acme Corp",
        "industry": "Technology",
        "employees": 500
    }
)
result = tool.run()
```

### 72. JSONValidator
**File**: `tools/utils/json_validator/json_validator.py`

**Description**: Validate JSON data against schemas and fix common errors.

**Key Parameters**:
- `json_data`: JSON to validate
- `schema`: JSON schema (optional)
- `auto_fix`: Attempt to fix errors

**Example Usage**:
```python
from tools.utils.json_validator import JSONValidator

tool = JSONValidator(
    json_data='{"name": "test", "value": 123}',
    schema={"type": "object", "required": ["name", "value"]},
    auto_fix=True
)
result = tool.run()
```

### 73. TextFormatter
**File**: `tools/utils/text_formatter/text_formatter.py`

**Description**: Format text with various transformations (case, spacing, line breaks).

**Key Parameters**:
- `text`: Text to format
- `operations`: List of formatting operations
- `output_format`: Desired format

**Example Usage**:
```python
from tools.utils.text_formatter import TextFormatter

tool = TextFormatter(
    text="hello world",
    operations=["title_case", "trim", "remove_extra_spaces"]
)
result = tool.run()
```

### 74. Think
**File**: `tools/utils/think/think.py`

**Description**: Internal reasoning tool for complex problem-solving and planning.

**Key Parameters**:
- `thought`: Reasoning or analysis to perform
- `context`: Contextual information
- `output_plan`: Generate action plan

**Example Usage**:
```python
from tools.utils.think import Think

tool = Think(
    thought="How should I approach creating a comprehensive marketing strategy?",
    context="Tech startup in healthcare AI space",
    output_plan=True
)
result = tool.run()
```

### 75. FactChecker
**File**: `tools/utils/fact_checker/fact_checker.py`

**Description**: Verify claims using web search and academic sources with confidence scoring and source analysis.

**Key Parameters**:
- `claim`: The claim or statement to verify (required)
- `sources`: Optional list of specific source URLs to check
- `use_scholar`: Whether to include academic sources via scholar search
- `max_sources`: Maximum number of sources to analyze (default: 10)

**Returns**:
- `confidence_score`: Score from 0-100 (0=false, 100=true)
- `verdict`: "SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"
- `supporting_sources`: List of sources supporting the claim
- `contradicting_sources`: List of sources contradicting the claim
- `neutral_sources`: List of neutral/informational sources
- `analysis_summary`: Brief explanation of the verdict

**Example Usage**:
```python
from tools.utils.fact_checker import FactChecker

# Check a claim using web and academic sources
tool = FactChecker(
    claim="Electric vehicles produce lower lifetime emissions than gasoline cars",
    use_scholar=True,
    max_sources=15
)
result = tool.run()
print(f"Verdict: {result['result']['verdict']}")
print(f"Confidence: {result['result']['confidence_score']}/100")
print(f"Supporting sources: {len(result['result']['supporting_sources'])}")
print(f"Analysis: {result['result']['analysis_summary']}")

# Check with specific sources
tool = FactChecker(
    claim="Python is the most popular programming language in 2024",
    sources=["https://www.tiobe.com", "https://survey.stackoverflow.co"],
    max_sources=5
)
result = tool.run()
```

### 76. Translation
**File**: `tools/utils/translation/translation.py`

**Description**: Multi-language translation with format preservation supporting 100+ languages via Google Translate or DeepL.

**Key Parameters**:
- `text`: Text to translate (required, max 10,000 characters)
- `source_lang`: Source language code (auto-detect if None)
- `target_lang`: Target language code (required, e.g., 'es', 'fr', 'de', 'ja', 'zh')
- `preserve_formatting`: Whether to preserve markdown/HTML formatting
- `api_provider`: Which API to use ('google' or 'deepl', default: 'google')

**Supported Languages** (examples):
- English: 'en', Spanish: 'es', French: 'fr', German: 'de'
- Italian: 'it', Portuguese: 'pt', Russian: 'ru'
- Japanese: 'ja', Korean: 'ko', Chinese: 'zh'/'zh-CN'/'zh-TW'
- Arabic: 'ar', Hindi: 'hi', and 90+ more languages

**Example Usage**:
```python
from tools.utils.translation import Translation

# Basic translation
tool = Translation(
    text="Hello, world! How are you today?",
    target_lang="es",
    preserve_formatting=False
)
result = tool.run()
print(result['result']['translated_text'])  # "¡Hola, mundo! ¿Cómo estás hoy?"

# Auto-detect source language
tool = Translation(
    text="Bonjour, comment allez-vous?",
    target_lang="en"
)
result = tool.run()
print(f"Detected: {result['result']['detected_language']}")  # "fr"
print(result['result']['translated_text'])  # "Hello, how are you?"

# Preserve markdown formatting
tool = Translation(
    text="**Important**: This is a *test* with [a link](https://example.com)",
    target_lang="de",
    preserve_formatting=True
)
result = tool.run()

# Use DeepL API for higher quality
tool = Translation(
    text="The quick brown fox jumps over the lazy dog.",
    target_lang="ja",
    api_provider="deepl"
)
result = tool.run()
```

---

## Visualization

### 77. GenerateAreaChart
**File**: `tools/visualization/generate_area_chart/generate_area_chart.py`

**Description**: Create area charts for showing cumulative trends over time.

**Key Parameters**:
- `data`: Data points [{x, y}]
- `title`: Chart title
- `width`: Chart width
- `height`: Chart height

**Example Usage**:
```python
from tools.visualization.generate_area_chart import GenerateAreaChart

tool = GenerateAreaChart(
    data=[{"x": "Jan", "y": 100}, {"x": "Feb", "y": 150}, {"x": "Mar", "y": 200}],
    title="Revenue Growth"
)
result = tool.run()
```

### 78. GenerateBarChart
**File**: `tools/visualization/generate_bar_chart/generate_bar_chart.py`

**Description**: Create bar charts for comparing values across categories.

**Key Parameters**:
- `data`: Data points [{category, value}]
- `title`: Chart title
- `orientation`: Horizontal or vertical

**Example Usage**:
```python
from tools.visualization.generate_bar_chart import GenerateBarChart

tool = GenerateBarChart(
    data=[{"category": "Q1", "value": 1000}, {"category": "Q2", "value": 1200}],
    title="Quarterly Sales"
)
result = tool.run()
```

### 79. GenerateColumnChart
**File**: `tools/visualization/generate_column_chart/generate_column_chart.py`

**Description**: Create column charts (vertical bars) for time-series or category comparisons.

**Key Parameters**:
- `data`: Data series
- `title`: Chart title
- `stacked`: Stack columns

**Example Usage**:
```python
from tools.visualization.generate_column_chart import GenerateColumnChart

tool = GenerateColumnChart(
    data=[{"month": "Jan", "sales": 5000, "costs": 3000}],
    title="Monthly Performance",
    stacked=True
)
result = tool.run()
```

### 80. GenerateDualAxesChart
**File**: `tools/visualization/generate_dual_axes_chart/generate_dual_axes_chart.py`

**Description**: Create charts with two Y-axes for comparing different scales.

**Key Parameters**:
- `left_data`: Data for left Y-axis
- `right_data`: Data for right Y-axis
- `title`: Chart title

**Example Usage**:
```python
from tools.visualization.generate_dual_axes_chart import GenerateDualAxesChart

tool = GenerateDualAxesChart(
    left_data=[{"x": "Jan", "y": 1000}],
    right_data=[{"x": "Jan", "y": 50}],
    title="Revenue vs Profit Margin"
)
result = tool.run()
```

### 81. GenerateFishboneDiagram
**File**: `tools/visualization/generate_fishbone_diagram/generate_fishbone_diagram.py`

**Description**: Create fishbone (Ishikawa) diagrams for root cause analysis.

**Key Parameters**:
- `problem`: Central problem statement
- `causes`: Dictionary of cause categories and items
- `title`: Diagram title

**Example Usage**:
```python
from tools.visualization.generate_fishbone_diagram import GenerateFishboneDiagram

tool = GenerateFishboneDiagram(
    problem="Customer Complaints",
    causes={
        "People": ["Training", "Communication"],
        "Process": ["Delays", "Errors"]
    },
    title="Root Cause Analysis"
)
result = tool.run()
```

### 82. GenerateFlowDiagram
**File**: `tools/visualization/generate_flow_diagram/generate_flow_diagram.py`

**Description**: Create flowcharts for process visualization.

**Key Parameters**:
- `nodes`: List of process steps
- `connections`: Flow connections
- `title`: Diagram title

**Example Usage**:
```python
from tools.visualization.generate_flow_diagram import GenerateFlowDiagram

tool = GenerateFlowDiagram(
    nodes=[{"id": "start", "label": "Begin"}, {"id": "process", "label": "Process"}],
    connections=[{"from": "start", "to": "process"}],
    title="Order Processing Flow"
)
result = tool.run()
```

### 83. GenerateHistogramChart
**File**: `tools/visualization/generate_histogram_chart/generate_histogram_chart.py`

**Description**: Create histograms for showing data distribution.

**Key Parameters**:
- `data`: Array of values
- `bins`: Number of bins
- `title`: Chart title

**Example Usage**:
```python
from tools.visualization.generate_histogram_chart import GenerateHistogramChart

tool = GenerateHistogramChart(
    data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
    bins=5,
    title="Score Distribution"
)
result = tool.run()
```

### 84. GenerateLineChart
**File**: `tools/visualization/generate_line_chart/generate_line_chart.py`

**Description**: Create line charts for showing trends over time.

**Key Parameters**:
- `data`: Data points [{x, y}]
- `title`: Chart title
- `multiple_series`: Support multiple lines

**Example Usage**:
```python
from tools.visualization.generate_line_chart import GenerateLineChart

tool = GenerateLineChart(
    data=[{"x": "Jan", "y": 100}, {"x": "Feb", "y": 120}],
    title="Monthly Trend"
)
result = tool.run()
```

### 85. GenerateMindMap
**File**: `tools/visualization/generate_mind_map/generate_mind_map.py`

**Description**: Create mind maps for brainstorming and concept visualization.

**Key Parameters**:
- `central_idea`: Main topic
- `branches`: Dictionary of branches and sub-topics
- `title`: Mind map title

**Example Usage**:
```python
from tools.visualization.generate_mind_map import GenerateMindMap

tool = GenerateMindMap(
    central_idea="Product Launch",
    branches={
        "Marketing": ["Social Media", "PR", "Events"],
        "Development": ["Features", "Testing", "Deployment"]
    },
    title="Launch Strategy"
)
result = tool.run()
```

### 86. GenerateNetworkGraph
**File**: `tools/visualization/generate_network_graph/generate_network_graph.py`

**Description**: Create network graphs for showing relationships and connections.

**Key Parameters**:
- `nodes`: List of network nodes
- `edges`: List of connections
- `title`: Graph title

**Example Usage**:
```python
from tools.visualization.generate_network_graph import GenerateNetworkGraph

tool = GenerateNetworkGraph(
    nodes=[{"id": "A", "label": "Person A"}, {"id": "B", "label": "Person B"}],
    edges=[{"source": "A", "target": "B", "weight": 5}],
    title="Social Network"
)
result = tool.run()
```

### 87. GenerateOrganizationChart
**File**: `tools/visualization/generate_organization_chart/generate_organization_chart.py`

**Description**: Create organization charts for showing hierarchical structures.

**Key Parameters**:
- `data`: Hierarchical data structure
- `title`: Chart title
- `orientation`: Layout direction

**Example Usage**:
```python
from tools.visualization.generate_organization_chart import GenerateOrganizationChart

tool = GenerateOrganizationChart(
    data={
        "name": "CEO",
        "children": [
            {"name": "CTO"},
            {"name": "CFO"}
        ]
    },
    title="Company Structure"
)
result = tool.run()
```

### 88. GeneratePieChart
**File**: `tools/visualization/generate_pie_chart/generate_pie_chart.py`

**Description**: Create pie charts for showing proportions and percentages.

**Key Parameters**:
- `data`: Data slices [{label, value}]
- `title`: Chart title
- `show_percentages`: Display percentage labels

**Example Usage**:
```python
from tools.visualization.generate_pie_chart import GeneratePieChart

tool = GeneratePieChart(
    data=[{"label": "Product A", "value": 40}, {"label": "Product B", "value": 60}],
    title="Market Share",
    show_percentages=True
)
result = tool.run()
```

### 89. GenerateRadarChart
**File**: `tools/visualization/generate_radar_chart/generate_radar_chart.py`

**Description**: Create radar (spider) charts for multi-dimensional comparisons.

**Key Parameters**:
- `data`: Data points for each axis
- `axes`: List of axis labels
- `title`: Chart title

**Example Usage**:
```python
from tools.visualization.generate_radar_chart import GenerateRadarChart

tool = GenerateRadarChart(
    data=[{"axis": "Speed", "value": 8}, {"axis": "Quality", "value": 9}],
    axes=["Speed", "Quality", "Cost", "Reliability"],
    title="Product Comparison"
)
result = tool.run()
```

### 90. GenerateScatterChart
**File**: `tools/visualization/generate_scatter_chart/generate_scatter_chart.py`

**Description**: Create scatter plots for showing correlations and distributions.

**Key Parameters**:
- `data`: Data points [{x, y}]
- `title`: Chart title
- `regression_line`: Show trend line

**Example Usage**:
```python
from tools.visualization.generate_scatter_chart import GenerateScatterChart

tool = GenerateScatterChart(
    data=[{"x": 1, "y": 2}, {"x": 2, "y": 4}, {"x": 3, "y": 5}],
    title="Correlation Analysis",
    regression_line=True
)
result = tool.run()
```

### 91. GenerateTreemapChart
**File**: `tools/visualization/generate_treemap_chart/generate_treemap_chart.py`

**Description**: Create treemap charts for showing hierarchical data as nested rectangles.

**Key Parameters**:
- `data`: Hierarchical data structure
- `title`: Chart title
- `color_scheme`: Color mapping

**Example Usage**:
```python
from tools.visualization.generate_treemap_chart import GenerateTreemapChart

tool = GenerateTreemapChart(
    data=[
        {"category": "Sales", "subcategory": "Q1", "value": 1000},
        {"category": "Sales", "subcategory": "Q2", "value": 1200}
    ],
    title="Revenue by Category"
)
result = tool.run()
```

### 92. GenerateWordCloudChart
**File**: `tools/visualization/generate_word_cloud_chart/generate_word_cloud_chart.py`

**Description**: Create word clouds from text data with frequency-based sizing.

**Key Parameters**:
- `text`: Input text or word frequency data
- `title`: Chart title
- `max_words`: Maximum words to display
- `color_scheme`: Color palette

**Example Usage**:
```python
from tools.visualization.generate_word_cloud_chart import GenerateWordCloudChart

tool = GenerateWordCloudChart(
    text="innovation technology future AI machine learning data science",
    title="Tech Keywords",
    max_words=50
)
result = tool.run()
```

---

## Web

### 93. ResourceDiscovery
**File**: `tools/web/resource_discovery/resource_discovery.py`

**Description**: Discover web resources including APIs, datasets, and documentation.

**Key Parameters**:
- `resource_type`: Type of resource to find
- `keywords`: Search keywords
- `filters`: Additional filters

**Example Usage**:
```python
from tools.web.resource_discovery import ResourceDiscovery

tool = ResourceDiscovery(
    resource_type="api",
    keywords=["weather", "forecast"],
    filters={"free": True}
)
result = tool.run()
```

---

## Web Content

### 94. Crawler
**File**: `tools/web_content/crawler/crawler.py`

**Description**: Crawl websites and extract content systematically.

**Key Parameters**:
- `url`: Starting URL
- `max_pages`: Maximum pages to crawl
- `depth`: Crawl depth
- `extract_type`: Type of content to extract

**Example Usage**:
```python
from tools.web_content.crawler import Crawler

tool = Crawler(
    url="https://example.com",
    max_pages=10,
    depth=2,
    extract_type="text"
)
result = tool.run()
```

### 95. SummarizeLargeDocument
**File**: `tools/web_content/summarize_large_document/summarize_large_document.py`

**Description**: Summarize large documents and web pages using AI.

**Key Parameters**:
- `url`: Document URL
- `summary_length`: Desired summary length
- `focus_areas`: Specific topics to focus on

**Example Usage**:
```python
from tools.web_content.summarize_large_document import SummarizeLargeDocument

tool = SummarizeLargeDocument(
    url="https://example.com/long-article.html",
    summary_length="medium",
    focus_areas=["key findings", "recommendations"]
)
result = tool.run()
```

### 96. URLMetadata
**File**: `tools/web_content/url_metadata/url_metadata.py`

**Description**: Extract metadata from URLs including title, description, images, and Open Graph data.

**Key Parameters**:
- `url`: URL to analyze
- `include_social`: Include social media metadata
- `include_images`: Extract image URLs

**Example Usage**:
```python
from tools.web_content.url_metadata import URLMetadata

tool = URLMetadata(
    url="https://example.com/article",
    include_social=True,
    include_images=True
)
result = tool.run()
```

### 97. WebpageCaptureScreen
**File**: `tools/web_content/webpage_capture_screen/webpage_capture_screen.py`

**Description**: Capture screenshots of web pages in various resolutions and formats.

**Key Parameters**:
- `url`: URL to capture
- `viewport`: Screen resolution
- `full_page`: Capture full scrollable page
- `format`: Image format (png, jpg)

**Example Usage**:
```python
from tools.web_content.webpage_capture_screen import WebpageCaptureScreen

tool = WebpageCaptureScreen(
    url="https://example.com",
    viewport={"width": 1920, "height": 1080},
    full_page=True,
    format="png"
)
result = tool.run()
```

---

## Workspace Integration

### 98. NotionRead
**File**: `tools/workspace/notion_read/notion_read.py`

**Description**: Read pages and content from Notion workspaces.

**Key Parameters**:
- `page_id`: Notion page ID
- `include_children`: Include child pages
- `format`: Output format

**Example Usage**:
```python
from tools.workspace.notion_read import NotionRead

tool = NotionRead(
    page_id="abc123def456",
    include_children=True,
    format="markdown"
)
result = tool.run()
```

### 99. NotionSearch
**File**: `tools/workspace/notion_search/notion_search.py`

**Description**: Search Notion workspaces for pages, databases, and content.

**Key Parameters**:
- `query`: Search query
- `filter_type`: Filter by page type
- `max_results`: Maximum results to return

**Example Usage**:
```python
from tools.workspace.notion_search import NotionSearch

tool = NotionSearch(
    query="project documentation",
    filter_type="page",
    max_results=20
)
result = tool.run()
```

### 100. GoogleDocs (Workspace)
**File**: `tools/communication/google_docs/google_docs.py`

**Description**: Create and modify Google Docs using Google Docs API v1 (also listed in Communication category).

**Key Parameters**:
- `mode`: "create" or "modify"
- `content`: Document content (markdown supported)
- `title`: Document title
- `document_id`: For modify mode
- `share_with`: Email addresses to share with

**Example Usage**:
```python
from tools.communication.google_docs import GoogleDocs

tool = GoogleDocs(
    mode="create",
    title="Team Meeting Notes",
    content="# Agenda\n\n1. Project updates\n2. Next steps",
    share_with=["team@company.com"]
)
result = tool.run()
```

### 101. GoogleSheets (Workspace)
**File**: `tools/communication/google_sheets/google_sheets.py`

**Description**: Create and modify Google Sheets spreadsheets (also listed in Communication category).

**Key Parameters**:
- `mode`: "create" or "modify"
- `title`: Spreadsheet title
- `data`: 2D array of data
- `range`: Cell range
- `share_with`: Email addresses

**Example Usage**:
```python
from tools.communication.google_sheets import GoogleSheets

tool = GoogleSheets(
    mode="create",
    title="Team Budget",
    data=[["Item", "Cost"], ["Software", 1000], ["Hardware", 2000]],
    range="Sheet1!A1:B3"
)
result = tool.run()
```

### 102. GoogleSlides (Workspace)
**File**: `tools/communication/google_slides/google_slides.py`

**Description**: Create and modify Google Slides presentations (also listed in Communication category).

**Key Parameters**:
- `mode`: "create" or "modify"
- `title`: Presentation title
- `slides`: List of slide content
- `share_with`: Email addresses

**Example Usage**:
```python
from tools.communication.google_slides import GoogleSlides

tool = GoogleSlides(
    mode="create",
    title="Project Kickoff",
    slides=[
        {"title": "Welcome", "content": "Project Kickoff Meeting"},
        {"title": "Goals", "content": "Q4 objectives and milestones"}
    ]
)
result = tool.run()
```

---

## Examples

### 103. DemoTool
**File**: `tools/_examples/demo_tool/demo_tool.py`

**Description**: Example tool demonstrating the Agency Swarm tool development pattern.

**Key Parameters**:
- `param1`: Example parameter
- `param2`: Another example parameter

**Example Usage**:
```python
from tools._examples.demo_tool import DemoTool

tool = DemoTool(param1="value1", param2="value2")
result = tool.run()
```

---

## Quick Reference by Use Case

### Data Analysis & Reporting
- `DataAggregator`, `ReportGenerator`, `TrendAnalyzer`
- `StockPrice`, `FinancialReport`
- All visualization tools (16 total)

### Content Creation
- `CreateAgent` (docs, slides, sheets, podcasts, websites)
- `ImageGeneration`, `VideoGeneration`, `AudioGeneration`
- `TextToSpeechAdvanced`

### Research & Information Gathering
- `WebSearch`, `ScholarSearch`, `VideoSearch`, `ImageSearch`
- `Crawler`, `SummarizeLargeDocument`
- `NotionSearch`, `GmailSearch`

### Media Processing
- `UnderstandImages`, `UnderstandVideo`, `AudioTranscribe`
- `ExtractAudioFromVideo`, `MergeAudio`
- `ImageStyleTransfer`, `VideoEffects`

### Communication & Collaboration
- `EmailDraft`, `EmailSend`, `GmailRead`
- `SlackSendMessage`, `TeamsSendMessage`
- `GoogleCalendar*` tools, `PhoneCall`

### File & Storage Management
- `AIDriveTool`, `OneDriveSearch`, `OneDriveFileRead`
- `FileFormatConverter`
- `Read`, `Write`, `MultiEdit`

---

## Tool Development Guidelines

All tools in this catalog follow the **Agency Swarm** development standards:

1. **BaseTool Inheritance**: All tools extend `BaseTool`
2. **Required Methods**: `_execute()`, `_validate_parameters()`, `_should_use_mock()`, `_generate_mock_results()`, `_process()`
3. **Pydantic Fields**: All parameters use `Field()` with descriptions
4. **Environment Variables**: All secrets via `os.getenv()`
5. **Test Blocks**: Each tool has `if __name__ == "__main__":` test block
6. **Mock Mode**: Support `USE_MOCK_APIS` environment variable
7. **Error Handling**: Use `ValidationError` and `APIError`
8. **Documentation**: Clear docstrings and inline comments

---

## Additional Resources

- **Complete Documentation**: `genspark_tools_documentation.md`
- **Real Examples**: `tool_examples_complete.md`
- **Quick Index**: `TOOLS_INDEX.md`
- **Project Overview**: `README.md`
- **Development Guide**: `CLAUDE.md`

---

**Catalog Version**: 1.1.0
**Last Updated**: November 22, 2025
**Total Tools**: 101 production-ready tools
**Repository**: agentswarm-tools

## New Tools Summary (v1.1.0)

**AI Intelligence** (2 new tools):
- RAGPipeline: Vector database RAG workflows (Pinecone, Chroma, Weaviate, Qdrant, Milvus)
- DeepResearchAgent: Comprehensive multi-source research with auto-generated reports

**Communication** (2 new tools):
- TwilioPhoneCall: AI-powered phone calls with Twilio integration
- TwilioCallLogs: Call history analytics with recordings and transcriptions

**Content Creation** (1 new tool):
- WebsiteBuilder: Professional website generation with SEO and deployment

**Media Generation** (1 new tool):
- PodcastGenerator: Multi-speaker AI podcasts with music and effects

**Media Processing** (1 new tool):
- VideoClipper: AI-powered highlight extraction from long videos
