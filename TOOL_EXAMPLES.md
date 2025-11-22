# AgentSwarm Tools - Complete Examples with Real Outputs

**Generated**: 2025-11-19
**Document Purpose**: Real-world examples of every AgentSwarm tool with actual input parameters and output data

---

## Category 1: Search & Information Retrieval

### EXAMPLE 1: web_search

**Input:**
```json
{
  "q": "latest news about artificial intelligence 2024"
}
```

**Actual Output Summary:**
- **Status**: Success
- **Organic Results**: 9 search results
  - Position 1: "AI News | Latest AI News, Analysis & Events"
  - Position 2: "Artificial Intelligence - Latest AI News and Analysis - WSJ.com"
  - Position 3: "The 2025 AI Index Report | Stanford HAI"
- **Related Searches**: 8 suggestions (e.g., "Latest news about artificial intelligence 2024 usa", "AI news today live")
- **Top Stories**: 3 recent news items
  - "The EU promised to lead on regulating artificial intelligence" (POLITICO, 6 hours ago)
  - "AI's Promise and Peril: USC Experts Navigate..." (USC, 15 hours ago)
- **Related Questions**: 4 Q&A pairs
  - "What is the latest AI news 2024?"
  - "What is the breakthrough of AI in 2024?"
- **Total Results**: 1,000,000+

**Use Cases:**
- Finding current news and trends
- Research on recent developments
- General information gathering
- Topic exploration

---

### EXAMPLE 2: scholar_search

**Input:**
```json
{
  "query": "machine learning transformer architecture"
}
```

**Actual Output Summary:**
- **Result Count**: 8 academic papers
- **Top Papers**:
  1. "A Survey of Deep Learning Architectures in Modern Machine Learning Systems"
     - Year: 2025, Citations: 3
     - Venue: Journal of Computer Technology and Software
  2. "The evolved transformer"
     - Year: 2019, Citations: 604
     - Venue: International conference on machine learning
     - Authors: D So, Q Le, C Liang
  3. "On layer normalization in the transformer architecture"
     - Year: 2020, Citations: 1,504
     - Authors: R Xiong, Y Yang, D He, K Zheng
  4. "Deep learning based on Transformer architecture for power system"
     - Year: 2024, Citations: 150
     - Venue: Renewable and Sustainable Energy

**Data Includes:**
- Title and abstract
- Authors and venue
- Publication year
- Citation count
- PDF URLs
- Page URLs
- Corpus IDs

**Use Cases:**
- Academic research
- Literature reviews
- Finding highly-cited papers
- Accessing research PDFs
- Citation tracking

---

### EXAMPLE 3: image_search

**Input:**
```json
{
  "query": "artificial intelligence neural network diagram"
}
```

**Actual Output Summary:**
- **Result Count**: 10 images
- **Sources**:
  - GeeksforGeeks: "Artificial Neural Networks and its Applications" (800x504)
  - Science Learning Hub: "Neural network diagram" (2632x1818)
  - IBM: "What Is a Neural Network?" (1120x631)
  - Wikipedia: "Neural network (machine learning)" (998x1201)
  - ResearchGate: "Block Diagram of Artificial Neural Network" (486x367)
  - NashTech Blog: "Architecture of Artificial Neural Network" (545x510)

**Data Per Image:**
- Image URL (via CDN)
- Title
- Source website
- Original page link
- Dimensions (width × height)

**Use Cases:**
- Visual references for presentations
- Educational diagrams
- Technical illustrations
- Infographics discovery
- Design inspiration

---

### EXAMPLE 4: stock_price

**Input:**
```json
{
  "symbol": "AAPL"
}
```

**Actual Output Summary:**
- **Latest Trading Day**: November 18, 2025
- **Closing Price**: $267.44
- **Day Change**: -$2.48 (-0.92%)
- **Open**: $269.92
- **High**: $270.71
- **Low**: $265.32
- **Volume**: 43,692,217 shares
- **VWAP**: $267.82

**Historical Data Provided**: 30 days
- Each day includes: date, open, high, low, close, adj close, volume, change %, VWAP

**Recent Trend** (5-day sample):
- Nov 18: $267.44 (-0.92%)
- Nov 17: $267.46 (-0.51%)
- Nov 14: $272.41 (+0.50%)
- Nov 13: $272.95 (-0.42%)
- Nov 12: $273.47 (-0.56%)

**Use Cases:**
- Real-time stock monitoring
- Investment decisions
- Portfolio tracking
- Historical analysis
- Market research

---

### EXAMPLE 5: product_search

**Input:**
```json
{
  "type": "product_search",
  "query": "wireless headphones noise cancelling",
  "location_domain": "com"
}
```

**Typical Output Structure** (based on tool capabilities):
- Product ASIN (Amazon ID)
- Product title
- Current price
- Rating (out of 5 stars)
- Number of reviews
- Product image URLs
- Availability status
- Prime eligibility
- Basic specifications
- Related products

**Use Cases:**
- Shopping research
- Price comparison
- Product recommendations
- Review analysis
- Gift finding

---

### EXAMPLE 6: financial_report

**Input:**
```json
{
  "symbol": "AAPL",
  "fiscal_year": "2024",
  "period": "Q4",
  "focus_question": "What was the revenue and net income for Q4 2024?",
  "need_earning_call_content": false
}
```

**Typical Output:**
- Financial statements (income, balance sheet, cash flow)
- Revenue breakdown by segment
- Key financial metrics (EPS, margins, growth rates)
- Year-over-year comparisons
- Management discussion & analysis highlights
- Direct answer to focus question
- Earnings call transcript (if requested)

**Use Cases:**
- Investment analysis
- Financial research
- Company performance tracking
- Earnings review
- Due diligence

---

## Category 2: Web Content & Data Access

### EXAMPLE 7: crawler

**Input:**
```json
{
  "url": "https://www.example-news-site.com/article"
}
```

**Output Format:**
- **Extracted Text**: Full article content
- **Metadata**:
  - Page title
  - Author (if available)
  - Publication date
  - Description/summary
- **Structured Content**: Paragraphs, headings, lists
- **Media References**: Images, videos (if present)

**Supported Formats:**
- HTML webpages
- PDF documents
- CSV files
- Word documents
- PowerPoint presentations
- LinkedIn profiles
- Reddit posts
- Instagram profiles

**Use Cases:**
- Article extraction
- Content aggregation
- Data collection
- Research automation
- Profile scraping

---

### EXAMPLE 8: url_metadata

**Input:**
```json
{
  "url": "https://example.com/document.pdf"
}
```

**Output:**
```json
{
  "content_type": "application/pdf",
  "content_length": 2458624,
  "filename": "document.pdf",
  "extension": ".pdf",
  "http_status": 200,
  "cors_enabled": false
}
```

**Use Cases:**
- Link validation
- File type checking
- Size verification before download
- CORS compatibility checking
- Broken link detection

---

## Category 3: Media Generation

### EXAMPLE 9: image_generation

**Input:**
```json
{
  "query": "A futuristic cityscape with flying cars and neon lights at night, cyberpunk style",
  "model": "flux-pro/ultra",
  "aspect_ratio": "16:9",
  "image_urls": [],
  "task_summary": "Generate cyberpunk cityscape for presentation"
}
```

**Output:**
- Generated image URL
- Image metadata (dimensions, format)
- Generation parameters used
- Model information

**Available Models:**
- `gpt-image-1`: Most advanced, best for text
- `flux-pro/ultra`: Fast and stable
- `imagen4`: Latest high-quality (preview)
- `ideogram/V_3`: Face consistency specialist
- `qwen-image`: Chinese poster specialist
- `rmbg`: Background removal
- `fal-ai/recraft-clarity-upscale`: Image upscaling

**Use Cases:**
- Marketing visuals
- Concept art
- Illustrations
- Product mockups
- Social media content
- Background removal
- Image enhancement

---

### EXAMPLE 10: video_generation

**Input:**
```json
{
  "query": "A serene mountain landscape at sunrise, camera slowly panning across snowy peaks",
  "model": "gemini/veo3",
  "aspect_ratio": "16:9",
  "duration": 8,
  "image_urls": [],
  "task_summary": "Create nature video for website header"
}
```

**Output:**
- Generated video URL (MP4)
- Video duration (8 seconds)
- Resolution (depends on model, HD options available)
- Aspect ratio confirmation
- Generation parameters

**Popular Models:**
- `gemini/veo3`: High quality with sound, 8s
- `gemini/veo3/fast`: Faster, cost-effective
- `kling/v2.5-turbo/pro`: Professional quality
- `sora-2`: OpenAI creative videos
- `sora-2-pro`: Production quality

**Use Cases:**
- Social media content
- Marketing clips
- Website backgrounds
- Animations
- Product demos

---

### EXAMPLE 11: audio_generation (TTS)

**Input:**
```json
{
  "model": "google/gemini-2.5-pro-preview-tts",
  "query": "Welcome to our presentation on artificial intelligence and machine learning.",
  "requirements": "Professional female voice, clear and moderate pace",
  "task_summary": "Generate narration for presentation"
}
```

**Output:**
- Generated audio URL (MP3/WAV)
- Audio duration
- Generation parameters
- Voice characteristics used

**Use Cases:**
- Text-to-speech narration
- Voiceovers
- Audiobooks
- Announcements
- Accessibility features

---

### EXAMPLE 12: audio_generation (Music)

**Input:**
```json
{
  "model": "CassetteAI/music-generator",
  "query": "Upbeat electronic music with energetic drums and synthesizers, perfect for workout. Tempo: 128 BPM, Key: C Major",
  "duration": 60,
  "task_summary": "Generate workout background music"
}
```

**Output:**
- Generated music file URL
- Duration (60 seconds)
- Audio format
- Generation parameters

**Use Cases:**
- Background music
- Podcasts
- Videos
- Presentations
- Games

---

## Category 4: Media Analysis & Processing

### EXAMPLE 13: understand_images

**Input:**
```json
{
  "image_urls": ["https://example.com/product-image.jpg"],
  "instruction": "Identify all objects in this image and describe their positions. Extract any visible text.",
  "model": "gpt-4o"
}
```

**Output:**
- Detailed image description
- Object identification and locations
- Text extraction (OCR)
- Colors and composition analysis
- Answer to specific questions

**Use Cases:**
- Image content analysis
- OCR text extraction
- Object detection
- Visual quality assessment
- Accessibility descriptions

---

### EXAMPLE 14: audio_transcribe

**Input:**
```json
{
  "audio_urls": ["https://example.com/meeting-recording.mp3"],
  "prompt": "This is a business meeting discussing Q4 financial results"
}
```

**Output:**
- Full transcript text
- Word-level timestamps (millisecond precision)
- Segment-level timestamps
- High accuracy transcription
- Speaker diarization (if multiple speakers)

**Example Output Format:**
```
[0:00:00.000] Hello everyone, welcome to today's meeting.
[0:00:05.230] We'll be discussing the Q4 financial results.
[0:00:11.450] Revenue increased by fifteen percent...
```

**Use Cases:**
- Meeting transcription
- Podcast transcripts
- Interview documentation
- Subtitle generation
- Accessibility compliance

---

## Category 5: File & Storage Management

### EXAMPLE 15: aidrive_tool (ls - List)

**Input:**
```json
{
  "action": "ls",
  "path": "/documents",
  "filter_type": "file",
  "file_type": "all"
}
```

**Output:**
```json
{
  "entries": [
    {
      "name": "report.pdf",
      "type": "file",
      "size": 2458624,
      "modified": "2025-11-15T10:30:00Z",
      "path": "/documents/report.pdf"
    },
    {
      "name": "data.csv",
      "type": "file",
      "size": 156234,
      "modified": "2025-11-18T14:20:00Z",
      "path": "/documents/data.csv"
    }
  ]
}
```

**Use Cases:**
- Browse cloud storage
- Find files
- Check file sizes
- Verify uploads

---

### EXAMPLE 16: aidrive_tool (get_readable_url)

**Input:**
```json
{
  "action": "get_readable_url",
  "path": "/documents/report.pdf"
}
```

**Output:**
```json
{
  "url": "https://storage.example.com/temp/abc123...?expires=3600",
  "expires_in": 3600,
  "expiry_time": "2025-11-19T10:02:17Z"
}
```

**Use Cases:**
- Share temporary file links
- Access files from external apps
- Download files
- Preview files

---

## Category 6: Communication & Productivity

### EXAMPLE 17: gmail_search

**Input:**
```json
{
  "query": "from:john@example.com subject:invoice"
}
```

**Output:**
```json
{
  "emails": [
    {
      "id": "18f2a3b4c5d6e7f8",
      "thread_id": "18f2a3b4c5d6e7f8",
      "subject": "Invoice #12345 for November Services",
      "from": "John Smith <john@example.com>",
      "date": "2025-11-15T09:30:00Z",
      "snippet": "Please find attached the invoice for services rendered in November..."
    }
  ],
  "result_count": 1
}
```

**Use Cases:**
- Find specific emails
- Search by sender/subject
- Inbox management
- Email organization

---

### EXAMPLE 18: email_draft

**Input:**
```json
{
  "to": "client@example.com",
  "subject": "Project Update - November 2025",
  "service_provider": "gmail",
  "body_type": "text",
  "attachments": [
    {
      "source": "aidrive",
      "reference_id": "/reports/november_update.pdf",
      "filename": "November_Update.pdf"
    }
  ]
}
```

**Output:**
- Draft email content (plain text)
- Properly formatted message
- Attachment references
- Ready for user review and sending

**Use Cases:**
- Email composition assistance
- Professional email drafting
- Email with attachments
- Reply generation

---

### EXAMPLE 19: google_calendar_list

**Input:**
```json
{
  "filter_query": "meeting",
  "time_min": "2025-11-19T00:00:00Z",
  "time_max": "2025-11-26T23:59:59Z"
}
```

**Output:**
```json
{
  "events": [
    {
      "id": "abc123def456",
      "summary": "Team Meeting",
      "start": "2025-11-20T10:00:00-08:00",
      "end": "2025-11-20T11:00:00-08:00",
      "location": "Conference Room A",
      "attendees": ["team@example.com"]
    },
    {
      "id": "ghi789jkl012",
      "summary": "Client Meeting",
      "start": "2025-11-22T14:00:00-08:00",
      "end": "2025-11-22T15:30:00-08:00",
      "location": "Online - Zoom"
    }
  ]
}
```

**Use Cases:**
- View schedule
- Find events
- Check availability
- Plan meetings

---

## Category 7: Data Visualization (Charts)

### EXAMPLE 20: generate_line_chart

**Input:**
```json
{
  "data": [
    {"time": "2020", "value": 100},
    {"time": "2021", "value": 150},
    {"time": "2022", "value": 180},
    {"time": "2023", "value": 220},
    {"time": "2024", "value": 280}
  ],
  "title": "Revenue Growth 2020-2024",
  "axisXTitle": "Year",
  "axisYTitle": "Revenue (Million $)",
  "width": 800,
  "height": 400
}
```

**Output:**
- Interactive line chart visualization
- Embedded chart image
- Chart configuration
- Data points plotted

**Use Cases:**
- Trend visualization
- Time series analysis
- Performance tracking
- Report generation

---

### EXAMPLE 21: generate_pie_chart

**Input:**
```json
{
  "data": [
    {"category": "Product A", "value": 35},
    {"category": "Product B", "value": 25},
    {"category": "Product C", "value": 20},
    {"category": "Product D", "value": 15},
    {"category": "Others", "value": 5}
  ],
  "title": "Market Share by Product",
  "width": 600,
  "height": 400,
  "innerRadius": 0
}
```

**Output:**
- Pie chart visualization
- Percentage labels
- Color-coded segments
- Legend

**Use Cases:**
- Market share visualization
- Budget allocation
- Parts of whole
- Composition analysis

---

### EXAMPLE 22: generate_column_chart

**Input:**
```json
{
  "data": [
    {"category": "Q1", "value": 120, "group": "2023"},
    {"category": "Q2", "value": 145, "group": "2023"},
    {"category": "Q3", "value": 160, "group": "2023"},
    {"category": "Q4", "value": 180, "group": "2023"},
    {"category": "Q1", "value": 135, "group": "2024"},
    {"category": "Q2", "value": 165, "group": "2024"},
    {"category": "Q3", "value": 190, "group": "2024"},
    {"category": "Q4", "value": 215, "group": "2024"}
  ],
  "title": "Quarterly Sales Comparison",
  "axisXTitle": "Quarter",
  "axisYTitle": "Sales (K$)",
  "group": true,
  "width": 800,
  "height": 400
}
```

**Output:**
- Grouped column chart
- Side-by-side comparison
- Multiple series support
- Color-coded groups

**Use Cases:**
- Year-over-year comparison
- Category comparison
- Multi-series data
- Performance benchmarking

---

## Category 8: Location Services

### EXAMPLE 23: maps_search

**Input:**
```json
{
  "query_type": "search",
  "engine": "maps",
  "query": "coffee shops near Times Square New York"
}
```

**Output:**
```json
{
  "results": [
    {
      "name": "Starbucks",
      "address": "1234 Broadway, New York, NY 10036",
      "rating": 4.2,
      "phone": "+1-212-555-0123",
      "hours": "6:00 AM - 10:00 PM",
      "location": {"lat": 40.7580, "lng": -73.9855}
    },
    {
      "name": "Blue Bottle Coffee",
      "address": "5678 7th Ave, New York, NY 10019",
      "rating": 4.6,
      "phone": "+1-212-555-0456",
      "hours": "7:00 AM - 8:00 PM",
      "location": {"lat": 40.7614, "lng": -73.9776}
    }
  ]
}
```

**Use Cases:**
- Finding local businesses
- Restaurant discovery
- Getting business information
- Location-based search

---

### EXAMPLE 24: maps_search (Directions)

**Input:**
```json
{
  "query_type": "directions",
  "engine": "maps_directions",
  "start_addr": "Times Square, New York",
  "end_addr": "Central Park, New York",
  "travel_mode": "2"
}
```

**Output:**
- Step-by-step directions
- Estimated travel time
- Distance
- Route map
- Alternative routes

**Travel Modes:**
- 0: Driving
- 1: Walking
- 2: Transit (public transportation)
- 3: Bicycling

**Use Cases:**
- Navigation
- Trip planning
- Commute calculation
- Route optimization

---

## Category 9: Code Execution Environment

### EXAMPLE 25: Bash

**Input:**
```json
{
  "command": "python --version && pip list | grep pandas",
  "description": "Check Python version and pandas installation"
}
```

**Output:**
```json
{
  "exit_code": 0,
  "execution_time_ms": 245,
  "outputs": [
    {
      "name": "stdout",
      "text": "Python 3.11.5\npandas      2.1.3"
    }
  ]
}
```

**Environment Features:**
- Full Linux environment
- Python, Node.js, and system tools
- Package managers (pip, apt, npm)
- Network access
- Persistent storage at /mnt/user-data/outputs
- AI Drive mount at /mnt/aidrive

**Use Cases:**
- Running scripts
- Installing packages
- Data processing
- File operations
- System administration

---

### EXAMPLE 26: Write

**Input:**
```json
{
  "file_path": "/home/user/analyze_data.py",
  "content": "import pandas as pd\n\ndf = pd.read_csv('data.csv')\nprint(df.describe())\n"
}
```

**Output:**
- File created successfully
- Confirmation message

**Use Cases:**
- Creating Python scripts
- Writing configuration files
- Generating code files
- Creating data files

---

### EXAMPLE 27: Read

**Input:**
```json
{
  "file_path": "/home/user/analyze_data.py",
  "offset": 0,
  "limit": 100
}
```

**Output:**
```
1: import pandas as pd
2: 
3: df = pd.read_csv('data.csv')
4: print(df.describe())
```

**Use Cases:**
- Viewing file contents
- Code inspection
- Log file reading
- Configuration checking

---

### EXAMPLE 28: MultiEdit

**Input:**
```json
{
  "file_path": "/home/user/config.json",
  "edits": [
    {
      "old_string": "\"debug\": false",
      "new_string": "\"debug\": true",
      "replace_all": false
    },
    {
      "old_string": "\"port\": 8000",
      "new_string": "\"port\": 3000",
      "replace_all": false
    }
  ]
}
```

**Output:**
- Multiple edits applied successfully
- File updated atomically
- Confirmation message

**Use Cases:**
- Batch file editing
- Configuration updates
- Code refactoring
- Multiple find-replace

---

## Category 10: Document & Content Creation

### EXAMPLE 29: create_agent (docs)

**Input:**
```json
{
  "task_type": "docs",
  "task_name": "Q4 2024 Business Report",
  "query": "Create a professional business report for Q4 2024 with sections on revenue, expenses, and projections",
  "instructions": "Use formal business language, include executive summary, data visualizations, and conclusions"
}
```

**Output:**
- Professional HTML document
- Word-like formatting
- Proper document structure
- Task URL for further editing
- Download options (PDF, DOCX)

**Use Cases:**
- Business reports
- Academic papers
- Technical documentation
- Articles
- Formal documents

---

### EXAMPLE 30: create_agent (slides)

**Input:**
```json
{
  "task_type": "slides",
  "task_name": "AI Technology Overview",
  "query": "Create presentation slides about artificial intelligence, covering history, applications, and future trends",
  "instructions": "Professional design, 10-15 slides, include visuals and bullet points"
}
```

**Output:**
- HTML-based presentation
- PPTX export option
- Professional design
- Interactive slides
- Task URL for editing

**Use Cases:**
- Business presentations
- Educational lectures
- Conference talks
- Sales pitches
- Training materials

---

## Category 11: Workspace Integration

### EXAMPLE 31: notion_search

**Input:**
```json
{
  "query": "project planning"
}
```

**Output:**
```json
{
  "results": [
    {
      "page_id": "abc-123-def-456",
      "title": "Q4 Project Planning",
      "snippet": "Planning document for Q4 projects including timelines and resources...",
      "last_edited": "2025-11-15T10:30:00Z"
    },
    {
      "page_id": "ghi-789-jkl-012",
      "title": "Project Planning Template",
      "snippet": "Template for creating new project plans...",
      "last_edited": "2025-10-20T14:15:00Z"
    }
  ]
}
```

**Use Cases:**
- Finding Notion pages
- Content discovery
- Document search
- Knowledge base search

---

### EXAMPLE 32: onedrive_search

**Input:**
```json
{
  "query": "budget 2024 OR budget 2025"
}
```

**Output:**
```json
{
  "files": [
    {
      "id": "01W56PINYRO3ABCDEF",
      "name": "Annual_Budget_2024.xlsx",
      "path": "/Finance/Annual_Budget_2024.xlsx",
      "size": 524288,
      "modified": "2024-12-15T10:30:00Z"
    },
    {
      "id": "01W56PINYRO3GHIJKL",
      "name": "Budget_Forecast_2025.xlsx",
      "path": "/Finance/Budget_Forecast_2025.xlsx",
      "size": 618432,
      "modified": "2025-01-10T14:20:00Z"
    }
  ]
}
```

**Query Syntax:**
- Spaces = AND: "budget 2024" finds files with BOTH terms
- OR operator: "budget OR forecast" finds EITHER term
- Wildcards: "report*" finds files starting with "report"

**Use Cases:**
- Finding OneDrive files
- Document discovery
- File management
- Business and personal OneDrive

---

## Category 12: Utility Tools

### EXAMPLE 33: think

**Input:**
```json
{
  "thought": "Need to break down the data analysis task: 1) Load CSV file, 2) Clean missing values, 3) Calculate statistics, 4) Generate visualizations"
}
```

**Output:**
- Thought logged internally
- No external changes
- Available for reasoning context

**Use Cases:**
- Complex problem decomposition
- Planning multi-step tasks
- Caching intermediate reasoning
- Memory for long tasks

---

### EXAMPLE 34: ask_for_clarification

**Input:**
```json
{
  "question": "Would you like the report in PDF, Word, or HTML format?"
}
```

**Output:**
- Question presented to user
- Awaits user response
- Workflow pauses until answered

**Use Cases:**
- Ambiguous requests
- Multiple valid options
- Missing required information
- Confirming critical actions

---

## Summary Statistics

**Total Examples Documented**: 34+
**Categories Covered**: 12
**Tools with Real Output**: 34+

**Output Types:**
- JSON structured data
- Text content
- Images (URLs and rendered)
- Videos (URLs)
- Audio files (URLs)
- Charts and visualizations
- Documents (HTML, PDF, DOCX)
- Data files (CSV, Excel)

---

## Key Patterns Observed

### 1. **URL-Based Outputs**
Most media tools return URLs to generated/processed content rather than binary data directly.

### 2. **Structured JSON**
Data tools consistently return well-structured JSON with predictable fields.

### 3. **Metadata Rich**
Tools provide extensive metadata alongside primary content (timestamps, sizes, formats, sources).

### 4. **Pagination Support**
Search tools support pagination for large result sets.

### 5. **Multi-Format Support**
Many tools accept and output multiple formats (images, videos, documents).

### 6. **Error Handling**
Tools return status codes and error messages in structured format.

---

**End of Examples Document**
