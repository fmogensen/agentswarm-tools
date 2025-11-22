# AgentSwarm Tools - Complete Documentation

**Generated**: 2025-11-19
**Total Tool Count**: 80+ tools across 15 categories

---

## Table of Contents

1. [Search & Information Retrieval](#search--information-retrieval)
2. [Web Content & Data Access](#web-content--data-access)
3. [Media Generation](#media-generation)
4. [Media Analysis & Processing](#media-analysis--processing)
5. [File & Storage Management](#file--storage-management)
6. [Communication & Productivity](#communication--productivity)
7. [Data Visualization](#data-visualization)
8. [Location Services](#location-services)
9. [Code Execution Environment](#code-execution-environment)
10. [Document & Content Creation](#document--content-creation)
11. [Workspace Integration](#workspace-integration)
12. [Utility Tools](#utility-tools)

---

## Search & Information Retrieval

### 1. web_search

**Purpose**: Performs web search with Google and returns comprehensive results

**Parameters**:
- `q` (string, required): Search query (max 20 words, no line breaks)

**Returns**:
- `search_metadata`: Status, timestamps, Google URL
- `search_parameters`: Engine, query, location, language settings
- `organic_results`: Array of search results with:
  - `position`: Result ranking
  - `title`: Page title
  - `link`: URL
  - `snippet`: Description/excerpt
  - `date`: Publication date (if available)
  - `source`: Source name
- `related_searches`: Array of related query suggestions
- `top_stories`: Recent news articles (title, link, source, date)
- `related_questions`: "People Also Ask" questions with answers
- `search_information`: Total results count

**Usage Example**: See test results below

**Best For**: 
- General web searches
- News and current events
- Quick fact-finding
- Fallback when specialized tools don't work

---

### 2. scholar_search

**Purpose**: Search scholarly articles, academic papers, and research publications

**Parameters**:
- `query` (string, required): Academic search query

**Returns**:
- Academic papers with citations
- Author information
- Publication venues
- Abstract/snippets
- Citation counts

**Best For**:
- Academic research
- Scientific papers
- Literature reviews
- Citation tracking

---

### 3. image_search

**Purpose**: Search for existing images on the internet

**Parameters**:
- `query` (string, required): Image search terms

**Returns**:
- Array of image results with:
  - Image URLs
  - Thumbnails
  - Source pages
  - Image metadata (dimensions, format)
  - Context/descriptions

**Best For**:
- Finding existing photos/illustrations
- Visual reference material
- Stock images
- Diagrams and infographics

---

### 4. video_search

**Purpose**: Search for videos on YouTube platform

**Parameters**:
- `query` (string, required): Video search query

**Returns**:
- Video results with:
  - Video ID
  - Title
  - Channel name
  - View count
  - Duration
  - Upload date
  - Thumbnail URLs
  - Description snippet

**Best For**:
- Tutorials and how-to guides
- Educational content
- Product reviews
- Visual demonstrations

---

### 5. product_search

**Purpose**: Search and recommend products from Amazon with detailed information

**Parameters**:
- `type` (string, required): 'product_search' or 'product_detail'
- `query` (string, optional): Search query for product_search
- `ASIN` (string, optional): Amazon product ID for product_detail
- `location_domain` (string, optional): Domain ('com' for US)

**Returns**:
**For product_search**:
- Product listings with:
  - ASIN
  - Title
  - Price
  - Rating
  - Review count
  - Image URLs
  - Availability
  - Prime status

**For product_detail**:
- Detailed product information:
  - Full description
  - Specifications
  - Customer reviews
  - Q&A
  - Related products
  - Pricing history

**Best For**:
- Shopping research
- Price comparisons
- Product recommendations
- Review analysis

---

### 6. google_product_search

**Purpose**: Search products using Google Shopping for price comparison

**Parameters**:
- `query` (string, required): Product search query
- `num` (integer, optional): Number of results (default: 100, max: 100)
- `page` (integer, optional): Page number for pagination (default: 0)

**Returns**:
- Product results from multiple retailers:
  - Product name
  - Price
  - Merchant/store
  - Product URL
  - Image
  - Shipping info
  - Reviews/ratings

**Best For**:
- Multi-store price comparison
- Finding best deals
- Checking product availability
- Comparing retailers

---

### 7. financial_report

**Purpose**: Search official financial reports, earnings, statements for public companies

**Parameters**:
- `symbol` (string, required): Stock ticker (e.g., 'AAPL', 'MSFT')
- `fiscal_year` (string, required): 4-digit year (e.g., '2024')
- `period` (string, required): 'Q1', 'Q2', 'Q3', 'Q4', or 'FY'
- `focus_question` (string, required): Specific question about the report
- `company_name` (string, optional): Full company name
- `need_earning_call_content` (boolean, optional): Include earnings call transcript

**Returns**:
- Financial statements (income, balance sheet, cash flow)
- Key metrics and ratios
- Management discussion & analysis
- Earnings call transcript (if requested)
- Answer to focus question

**Best For**:
- Investment research
- Financial analysis
- Earnings reports
- Company performance tracking

---

### 8. stock_price

**Purpose**: Retrieve current stock price information for a company

**Parameters**:
- `symbol` (string, required): Stock ticker symbol (e.g., 'AAPL')

**Returns**:
- Current price
- Price change ($ and %)
- Day range (high/low)
- Volume
- Market cap
- Previous close
- Opening price

**Best For**:
- Real-time stock prices
- Market monitoring
- Quick price checks
- Portfolio tracking

---

## Web Content & Data Access

### 9. crawler

**Purpose**: Retrieves and converts content from URLs into readable format

**Parameters**:
- `url` (string, required): HTTP/HTTPS URL (max 2048 chars)

**Supports**:
- Webpages (HTML)
- PDF documents
- CSV files
- Office documents (Word, PowerPoint)
- LinkedIn profiles (company, person)
- Reddit posts
- Instagram profiles

**Returns**:
- Extracted text content
- Structured data
- Metadata (title, author, date)
- Images (if applicable)

**Best For**:
- Article extraction
- Document parsing
- Content scraping
- Data collection

**Note**: Cannot process Excel files directly

---

### 10. summarize_large_document

**Purpose**: Fetch and summarize text-based documents, answering specific questions

**Parameters**:
- `url` (string, required): Document URL
- `question` (string, required): Specific question about the content

**Supports**:
- Web pages
- PDFs
- Academic papers
- Reports
- Office documents (Word, PowerPoint)

**Returns**:
- Targeted answer to the question
- Relevant excerpts
- Context and citations

**Best For**:
- Long document analysis
- Research papers
- Technical documentation
- Extracting specific information

**Note**: Cannot process Excel files

---

### 11. url_metadata

**Purpose**: Check URL metadata without downloading content

**Parameters**:
- `url` (string or array, required): Single URL or list (max 5 URLs)

**Returns**:
- Content-Type
- Content-Length (file size)
- Filename
- File extension
- CORS support (for images)
- HTTP status

**Best For**:
- Validating links
- Checking file types
- Verifying file sizes
- CORS checking for images

---

### 12. webpage_capture_screen

**Purpose**: Captures a screenshot of a webpage

**Parameters**:
- `url` (string, required): HTTP/HTTPS URL (max 2048 chars)
- `viewport` (object, optional): 
  - `width` (integer): Default 1366
  - `height` (integer): Default 768, max 2500

**Returns**:
- Screenshot image
- Rendered visual representation

**Best For**:
- Visual webpage previews
- When crawling fails (robots.txt)
- UI/design documentation
- Archiving webpage appearance

---

### 13. resource_discovery

**Purpose**: Detect and catalog downloadable media resources from web pages

**Parameters**:
- `url` (string, required): Web page URL
- `resource_types` (array, optional): Types to detect
  - Options: 'images', 'videos', 'documents', 'audios', 'archives', 'all'
  - Default: ['all']

**Detects**:
- Images: JPG, PNG, WebP (≥300x300px)
- Videos: MP4, AVI, MOV
- Documents: PDF, DOC, XLS, PPT
- Audio: MP3, WAV, OGG
- Archives: ZIP, RAR, 7Z

**Returns**:
- Resource URLs
- File metadata (size, dimensions, duration)
- Resource type
- Max 30 resources

**Best For**:
- Resource inventory
- Download planning
- Media asset discovery
- Content auditing

**Limitations**: 30s timeout, max 30 resources, images must be ≥300x300px

---

## Media Generation

### 14. image_generation

**Purpose**: Generate new images from text descriptions or reference images

**Parameters**:
- `query` (string, required): Detailed image description
- `model` (enum, required): 
  - `gpt-image-1`: Most advanced, best for text in images
  - `flux-pro/ultra`: Fast and stable generation
  - `imagen4`: Latest high-quality model (preview)
  - `flux-pro/kontext/pro`: SOTA editing model
  - `recraft-v3`: Realistic images
  - `fal-ai/bytedance/seedream/v4`: 2K resolution, text layout
  - `ideogram/V_3`: Face consistency specialist
  - `qwen-image`: Chinese poster specialist
  - `fal-ai/nano-banana`: Gemini 2.5 Flash, multi-image fusion
  - `bbox-segment`: Extract subjects by region
  - `rmbg`: Remove background specialist
  - `fal-ai/recraft-clarity-upscale`: Upscale images
  - `flux-pro/outpaint`: Expand images
- `image_urls` (array, optional): Reference images (default: [])
- `aspect_ratio` (enum, required): '1:1', '4:3', '16:9', '9:16', '3:4', '2:3', '3:2', 'auto'
- `task_summary` (string, required): Brief task description
- `bbox` (array, optional): Bounding box coordinates for segmentation

**Returns**:
- Generated image URL(s)
- Image metadata
- Generation parameters

**Best For**:
- Custom illustrations
- Marketing visuals
- Concept art
- Image editing
- Background removal
- Upscaling

**Note**: Requires user confirmation before processing (costs credits/time)

---

### 15. video_generation

**Purpose**: Generate 5-10 second video clips from text or reference images

**Parameters**:
- `query` (string, required): Detailed video description
- `model` (enum, required):
  - `kling/v2.5-turbo/pro`: Latest, professional quality
  - `gemini/veo2`: Advanced, fast (80s), supports i2v
  - `gemini/veo3`: High quality with sound, 8s length
  - `gemini/veo3/fast`: Faster, cost-effective version
  - `gemini/veo3.1`: Latest with fast/HD modes
  - `gemini/veo3.1/reference-to-video`: Multiple reference images
  - `gemini/veo3.1/first-last-frame-to-video`: First/last frame control
  - `minimax/video-01-subject-reference`: Subject extraction (i2v only)
  - `minimax/hailuo-2.3/standard`: High quality, first/last frame
  - `wan/v2.5`: 1080p with audio integration
  - `vidu/q2`: Enhanced quality, fast turbo
  - `hunyuan`: High quality but slow
  - `runway/gen4_turbo`: High quality, fast (i2v only)
  - `official/pixverse/v5`: High quality, fast, expensive
  - `fal-ai/bytedance/seedance/v1/pro`: 1080p HD
  - `sora-2`: OpenAI Sora for creative videos
  - `sora-2-pro`: Production-quality Sora
  - `fal-ai/bytedance-upscaler/upscale/video`: Upscale existing videos
- `image_urls` (array, optional): Reference key frames (default: [])
- `aspect_ratio` (enum, required): '16:9', '9:16', '4:3', '1:1', '9:21'
- `duration` (number, optional): Seconds (default: 5)
- `task_summary` (string, required): Brief task description
- `audio_url` (string, optional): Audio for Wan v2.5 or OmniHuman
- `video_url` (string, optional): Input video for upscaling
- `fast_mode` (boolean, optional): Faster generation (Veo 3.1 only)
- `hd_mode` (boolean, optional): 1080p quality (Veo 3.1 only, 2x cost)
- `file_name` (string, optional): Output filename

**Returns**:
- Generated video URL
- Video metadata
- Duration and resolution info

**Best For**:
- Short video content
- Animations
- Marketing clips
- Social media content
- Video transitions

**Note**: Requires user confirmation (costs credits/time)

---

### 16. audio_generation

**Purpose**: Generate audio: TTS, sound effects, music, voice cloning

**Parameters**:
- `model` (enum, required):
  - `google/gemini-2.5-pro-preview-tts`: Best TTS, multi-speaker
  - `elevenlabs/v3-tts`: Advanced multilingual, emotional
  - `fal-ai/elevenlabs/tts/multilingual-v2`: High-quality multilingual
  - `fal-ai/minimax/speech-2.6-hd`: Best for Chinese/Japanese/Korean
  - `elevenlabs/sound-effects`: Sound effects (0.1-22s)
  - `elevenlabs/voice-clone`: Clone voice from samples
  - `elevenlabs/voice-changer`: Transform voice
  - `CassetteAI/music-generator`: Background music (10-180s)
  - `mureka/song-generator`: Songs with lyrics (up to 180s)
  - `mureka/instrumental-generator`: Instrumental music (up to 180s)
  - `fal-ai/lyria2`: Google Lyria 2 music (max 30s)
  - `fal-ai/minimax-music/v2`: Songs with structured lyrics
- `query` (string, optional): Text or description
- `task_summary` (string, required): Brief task description
- `duration` (number, optional): Duration in seconds (default: 0)
- `requirements` (string, optional): Voice characteristics, emotion, pacing
- `lyrics` (string, optional): Lyrics for song generation
- `custom_voice_id` (string, optional): Voice ID from cloning
- `voice_files` (array, optional): Sample files for voice cloning
- `source_audio_file` (string, optional): Audio for voice changer
- `previous_audio_params` (object, optional): Parameters from previous generation
- `script_url` (string, optional): Script file URL (Gemini TTS)
- `file_name` (string, optional): Output filename
- `image_urls` (array, optional): Reference images (default: [])

**Returns**:
- Generated audio URL
- Audio parameters
- Metadata

**Best For**:
- Text-to-speech
- Narration
- Sound effects
- Background music
- Voice cloning
- Audio production

**Note**: Requires user confirmation

---

## Media Analysis & Processing

### 17. understand_images

**Purpose**: Read and analyze image content from URLs or AI Drive

**Parameters**:
- `image_urls` (array, required): Image URLs or AI Drive paths
- `instruction` (string, required): Detailed analysis instructions
- `model` (enum, optional): 'gpt-4o' (default) or 'gemini-flash'

**Returns**:
- Image analysis
- Extracted information
- Object detection
- Text recognition (OCR)
- Visual descriptions

**Best For**:
- Image understanding
- OCR/text extraction
- Object identification
- Visual analysis
- Content moderation

---

### 18. understand_video

**Purpose**: Extract transcript from YouTube videos

**Parameters**:
- `video_id` (string, required): YouTube video ID
- `provide_download_link` (boolean, required): Whether to provide download link

**Returns**:
- Video transcript
- Timestamps
- Download link (if requested)

**Best For**:
- Video transcription
- Content extraction
- Subtitle generation
- Video analysis

---

### 19. batch_understand_videos

**Purpose**: Process multiple videos to answer specific questions efficiently

**Parameters**:
- `jobs` (array, required): Array of video jobs
  - `video_id` (string): YouTube video ID
  - `questions_to_answer` (array): List of questions for this video

**Returns**:
- Answers in markdown format
- Organized by video
- Timestamped responses

**Best For**:
- Bulk video analysis
- Research across multiple videos
- Comparative video analysis

---

### 20. analyze_media_content

**Purpose**: Deep analysis of images, audio, and video with specified requirements

**Parameters**:
- `media_urls` (array, required): Media URLs or AI Drive paths
- `requirements` (string, optional): Detailed analysis requirements (in English)
- `analyze_type` (enum, optional): '' (default) or 'video_style_replication'

**Returns**:
- Comprehensive media analysis
- Extracted information
- Style analysis (for video_style_replication)

**Best For**:
- Deep content analysis
- Style extraction
- Multi-format analysis
- Custom analysis requirements

---

### 21. audio_transcribe

**Purpose**: Precisely transcribe audio to text with word-level timestamps

**Parameters**:
- `audio_urls` (array, required): Audio file URLs or AI Drive paths
- `prompt` (string, optional): Context to improve transcription

**Supports**: mp3, mp4, mpeg, mpga, m4a, wav, webm

**Returns**:
- Full transcript
- Word-level timestamps
- Segment-level timestamps
- High accuracy transcription

**Best For**:
- Audio transcription
- Podcast transcripts
- Meeting notes
- Subtitle creation

---

### 22. merge_audio

**Purpose**: Merge multiple audio clips into one file

**Parameters**:
- `original_audio_path` (string, optional): Base audio URL or AI Drive path
- `audio_clips` (array, required): Clips to merge
  - `ai_drive_path` (string): Clip location
  - `start_time` (integer): Start in milliseconds
  - `end_time` (integer): End in milliseconds
  - `insert_position` (integer): Where to insert (ms)
  - `merge_type` (enum): 'insert', 'parallel', or 'concat'
  - `volume` (number): 0.0-1.0 (default: 1)
  - `fade_type` (enum): 'none', 'fadein', 'fadeout', 'fadein_out'
  - `fade_duration` (number): Fade seconds (default: 1)

**Returns**:
- Merged audio URL
- Public blob storage URL

**Best For**:
- Audio editing
- Podcast production
- Clip compilation
- Audio mixing

---

### 23. extract_audio_from_video

**Purpose**: Extract audio track from video files

**Parameters**:
- `video_urls` (array, required): Video URLs or AI Drive paths
- `output_aidrive_path` (string, required): Where to save audio
- `audio_bitrate` (string, optional): Default '128k'
- `audio_sample_rate` (integer, optional): Default 16000

**Returns**:
- Extracted audio files (MP3)
- Saved to AI Drive

**Best For**:
- Audio extraction
- Converting video to audio
- Podcast creation
- Audio processing

---

## File & Storage Management

### 24. aidrive_tool

**Purpose**: AI Drive cloud storage management

**Actions**:
- `ls`: List directory contents
- `mkdir`: Create directories
- `rm`: Move to trash (recoverable)
- `move`: Relocate/rename files
- `get_readable_url`: Generate 1-hour temporary URLs
- `download_video`: Download videos from platforms
- `download_audio`: Download audio from platforms
- `download_file`: Download files from URLs
- `compress`: Compress folder to ZIP
- `decompress`: Decompress archive to folder

**Parameters** (vary by action):
- `action` (enum, required): Action to perform
- `path` (string): File/folder path
- `target_path` (string): Destination for move
- `target_folder` (string): Destination for downloads
- `video_url` (string): URL for video download
- `audio_url` (string): URL for audio download
- `file_url` (string): URL for file download
- `file_name` (string): Custom filename for downloads
- `filter_type` (enum): 'all', 'file', 'directory'
- `file_type` (enum): 'all', 'audio', 'video', 'image'

**Returns**:
- Directory listings
- Operation status
- Temporary URLs (1-hour expiry)
- Download results

**Best For**:
- Cloud file management
- Media downloads
- File organization
- Temporary access links

---

### 25. file_format_converter

**Purpose**: Convert files between different formats

**Parameters**:
- `file_url` (string, required): Source file URL
- `from_format` (string, required): Source format
- `to_format` (string, required): Target format

**Returns**:
- Converted file URL
- Conversion status

**Best For**:
- Format conversion
- Document transformation
- Media format changes

**Note**: Requires user confirmation (costs credits/time)

---

### 26. onedrive_search

**Purpose**: Search files and folders in Microsoft OneDrive

**Parameters**:
- `query` (string, required): Search query
  - Multiple terms = AND operation
  - Use 'OR' for alternatives
  - Empty string = list all files
  - Supports wildcards

**Returns**:
- Matching files/folders
- File metadata
- OneDrive paths
- File IDs

**Best For**:
- OneDrive file search
- Personal and Business OneDrive
- File discovery

---

### 27. onedrive_file_read

**Purpose**: Read and process OneDrive/SharePoint files, answer questions

**Parameters**:
- `file_id` (string, required): File ID or OneDrive/SharePoint URL
- `question` (string, required): Question about file content

**Supports**:
- OneDrive files
- SharePoint driveItems
- Teams message attachments

**Returns**:
- File content analysis
- Answer to question
- Extracted information

**Best For**:
- Document analysis
- Content extraction
- Teams attachment reading
- Detailed file processing

---

## Communication & Productivity

### 28. gmail_search

**Purpose**: Search and list emails from Gmail

**Parameters**:
- `query` (string, required): Gmail search query
- `next_page_token` (string, optional): For pagination

**Returns**:
- Email results
- Email IDs
- Subjects
- Senders
- Dates
- Snippets

**Best For**:
- Email search
- Inbox management
- Email organization

**Note**: Some queries are invalid (e.g., 'is:recent')

---

### 29. gmail_read

**Purpose**: Read specific email from Gmail by ID

**Parameters**:
- `id` (string, required): Email ID
- `title` (string, optional): Email title
- `question` (string, optional): Question to answer about email
- `download_attachments` (boolean, optional): Download attachments
- `aidrive_path` (string, optional): Where to save attachments (default: /gmail_attachments/)

**Returns**:
- Email content
- Sender/recipient info
- Attachments
- Answer to question (if provided)

**Best For**:
- Reading emails
- Extracting information
- Downloading attachments
- Email analysis

---

### 30. read_email_attachments

**Purpose**: Read email attachments efficiently (checks cache first)

**Parameters**:
- `email_id` (string, required): Email ID
- `filename` (string, optional): Specific attachment (or all if omitted)
- `platform` (enum, optional): 'gmail' or 'outlook' (default: 'gmail')

**Returns**:
- Attachment content
- File analysis
- Cached data (if available)

**Best For**:
- Fast attachment access
- Cached attachment retrieval
- Efficient file reading

---

### 31. email_draft

**Purpose**: Generate email content for drafting

**Parameters**:
- `to` (string, required): Recipient email(s)
- `subject` (string, required): Email subject
- `service_provider` (enum, required): 'gmail' or 'outlook'
- `body_type` (enum, optional): 'text' (default) or 'html'
- `cc` (string, optional): CC recipients
- `bcc` (string, optional): BCC recipients
- `type` (enum, optional): 'draft', 'reply', 'forward'
- `thread_id` (string, optional): Thread ID for replies
- `original_email_id` (string, optional): Original email for reply/forward
- `attachments` (array, optional): Files to attach
  - `source`: 'project' or 'aidrive'
  - `reference_id`: Filename or path
  - `filename`: Display name

**Returns**:
- Draft email content
- Formatted message

**Best For**:
- Email composition
- Reply generation
- Email with attachments

**Note**: Default is plain text unless HTML explicitly requested

---

### 32. google_calendar_list

**Purpose**: Search and retrieve Google Calendar events

**Parameters**:
- `filter_query` (string, optional): Text filter (empty = all events)
- `time_min` (string, optional): Start time (RFC3339)
- `time_max` (string, optional): End time (RFC3339)

**Returns**:
- Calendar events
- Event details (time, location, attendees)
- Event IDs

**Best For**:
- Calendar management
- Event search
- Schedule viewing

---

### 33. google_calendar_create_event_draft

**Purpose**: Create or modify calendar event draft (requires user confirmation)

**Parameters**:
- `summary` (string, required): Event title
- `start_time` (string, required): Start (ISO 8601 with timezone)
- `end_time` (string, required): End (ISO 8601 with timezone)
- `time_zone_name` (string, required): Timezone name (e.g., 'America/Los_Angeles')
- `time_zone` (string, required): Timezone offset (e.g., 'GMT-07:00')
- `calendar_id` (string, optional): Calendar ID ('primary' or specific)
- `location` (string, optional): Event location
- `description` (string, optional): Details (supports safe HTML subset)
- `attendees` (array, optional): Email addresses
- `recurrence` (array, optional): Recurrence rules
- `send_notifications` (boolean, optional): Email notifications
- `event_id` (string, optional): For modifying existing events

**Returns**:
- Event draft
- Event details

**Best For**:
- Creating calendar events
- Scheduling meetings
- Event management

---

### 34. phone_call

**Purpose**: Create AI-assisted phone call card (call initiated when user clicks button)

**Parameters**:
- `recipient` (string, required): Name or business to call
- `contact_type` (enum, required): 'personal' or 'business'
- `purpose` (string, required): Reason for call
- `phone_number` (string, optional): Phone with country code

**Returns**:
- Call card UI with button
- Recipient information
- Call purpose

**Best For**:
- Phone call assistance
- Business inquiries
- Appointment booking
- Information gathering

**Note**: 
- Personal contacts require phone_number
- Business contacts search Google Maps automatically
- User clicks button to initiate call
- Supports most countries globally

---

### 35. query_call_logs

**Purpose**: Query call history with optional filtering

**Parameters**:
- `time_range_hours` (integer, optional): Hours to look back
- `limit` (integer, optional): Max results (default: 3)
- `include_transcript` (boolean, optional): Include full transcripts (default: false)

**Returns**:
- Call logs (reverse chronological)
- Call metadata
- Transcripts (if requested)

**Best For**:
- Call history review
- Checking past conversations
- Call analytics

---

## Data Visualization (Chart Server MCP)

All chart tools follow similar patterns with these common parameters:
- `data` (array/object, required): Chart data
- `title` (string, optional): Chart title
- `width` (number, optional): Width in pixels (default: 600)
- `height` (number, optional): Height in pixels (default: 400)
- `axisXTitle` (string, optional): X-axis label
- `axisYTitle` (string, optional): Y-axis label

### 36. generate_area_chart

**Data Format**: `[{ time: '2018', value: 99.9, group: 'optional' }]`

**Additional Parameters**:
- `stack` (boolean, optional): Enable stacking (requires 'group' field)

**Best For**: Trends over time, cumulative data

---

### 37. generate_bar_chart

**Data Format**: `[{ category: 'Category 1', value: 10, group: 'optional' }]`

**Additional Parameters**:
- `group` (boolean, optional): Enable grouping (default: false)
- `stack` (boolean, optional): Enable stacking (default: true)

**Best For**: Horizontal comparisons, categorical data

---

### 38. generate_column_chart

**Data Format**: `[{ category: 'Beijing', value: 825, group: 'Gas Car' }]`

**Additional Parameters**:
- `group` (boolean, optional): Enable grouping (default: true)
- `stack` (boolean, optional): Enable stacking (default: false)

**Best For**: Vertical comparisons, categorical data

---

### 39. generate_dual_axes_chart

**Data Format**:
```json
{
  "categories": ["2015", "2016", "2017"],
  "series": [
    { "type": "column", "data": [91.9, 99.1, 101.6], "axisYTitle": "Quantity" },
    { "type": "line", "data": [0.055, 0.06, 0.062], "axisYTitle": "Ratio" }
  ]
}
```

**Best For**: Combining trends and comparisons, dual metrics

---

### 40. generate_fishbone_diagram

**Data Format**: Hierarchical with children
```json
{
  "name": "main topic",
  "children": [
    { "name": "topic 1", "children": [{ "name": "subtopic 1-1" }] }
  ]
}
```

**Best For**: Cause-effect analysis, problem decomposition

---

### 41. generate_flow_diagram

**Data Format**:
```json
{
  "nodes": [{ "name": "node1" }, { "name": "node2" }],
  "edges": [{ "source": "node1", "target": "node2", "name": "edge1" }]
}
```

**Best For**: Process flows, workflows, decision trees

---

### 42. generate_histogram_chart

**Data Format**: `[78, 88, 60, 100, 95]` (array of numbers)

**Additional Parameters**:
- `binNumber` (number, optional): Number of intervals

**Best For**: Frequency distribution, data distribution patterns

---

### 43. generate_line_chart

**Data Format**: `[{ time: '2015', value: 23, group: 'optional' }]`

**Additional Parameters**:
- `stack` (boolean, optional): Enable stacking (default: false)

**Best For**: Trends over time, time series data

---

### 44. generate_mind_map

**Data Format**: Hierarchical with children
```json
{
  "name": "main topic",
  "children": [
    { "name": "topic 1", "children": [{ "name": "subtopic 1-1" }] }
  ]
}
```

**Best For**: Brainstorming, hierarchical information, idea organization

---

### 45. generate_network_graph

**Data Format**:
```json
{
  "nodes": [{ "name": "node1" }, { "name": "node2" }],
  "edges": [{ "source": "node1", "target": "node2", "name": "edge1" }]
}
```

**Best For**: Relationships, social networks, connections

---

### 46. generate_pie_chart

**Data Format**: `[{ category: 'Category 1', value: 27 }]`

**Additional Parameters**:
- `innerRadius` (number, optional): 0-1, creates donut chart (e.g., 0.6)

**Best For**: Proportions, parts of whole, market share

---

### 47. generate_radar_chart

**Data Format**: `[{ name: 'Design', value: 70, group: 'optional' }]`

**Best For**: Multidimensional comparisons (4+ dimensions), performance metrics

---

### 48. generate_scatter_chart

**Data Format**: `[{ x: 10, y: 15 }]`

**Best For**: Correlations, relationships between variables, data distribution

---

### 49. generate_treemap_chart

**Data Format**: Hierarchical with values
```json
[
  { 
    "name": "Design", 
    "value": 70, 
    "children": [{ "name": "Tech", "value": 20 }] 
  }
]
```

**Best For**: Hierarchical data, disk usage, proportional visualization

---

### 50. generate_word_cloud_chart

**Data Format**: `[{ text: 'word', value: 4.272 }]`

**Best For**: Word frequency, text analysis, keyword visualization

---

## Location Services

### 51. maps_search

**Purpose**: Search for geographical information, places, and businesses

**Parameters**:
- `query_type` (enum, required): 'search', 'place', 'distances', 'directions'
- `engine` (enum, required): 'maps' or 'maps_directions'
- `query` (string, conditional): Search query (required if engine='maps')
- `start_addr` (string, conditional): Start address (required if engine='maps_directions')
- `end_addr` (string, conditional): End address (required if engine='maps_directions')
- `travel_mode` (enum, optional): '0'-'9' (driving, walking, transit, etc.)
- `avoid` (enum, optional): 'highways', 'tolls', 'ferries'
- `prefer` (enum, optional): 'bus', 'subway', 'train', 'tram_light_rail'

**Returns**:
- Location information
- Business details
- Distances
- Directions/routes
- Map data

**Best For**:
- Finding locations
- Getting directions
- Distance calculations
- Local business info

**Note**: ONLY for geographic/location queries, not general information

---

## Code Execution Environment

### 52. Bash

**Purpose**: Execute bash commands in sandboxed Linux environment

**Parameters**:
- `command` (string, required): Bash command to execute
- `description` (string, optional): Clear description of what command does
- `timeout` (integer, optional): Timeout in ms (default: 120000, max: 600000)

**Environment**:
- Shared across all code tools (Bash, Read, Write, MultiEdit)
- Full Linux with development tools
- Network access
- Package managers (pip, apt, npm)
- Session persistence
- AI Drive mount at `/mnt/aidrive`
- Persistent storage at `/mnt/user-data/outputs`

**Returns**:
- Command output (stdout/stderr)
- Exit code
- Execution time

**Best For**:
- Running scripts
- Installing packages
- File operations
- System commands
- Data processing

**Important**:
- Always use non-interactive mode (`-y`, `--no-input`)
- Never use inline Python (create .py files instead)
- Use `nohup` for long-running processes
- Work locally first, then copy to persistent storage
- Share files via `computer://` links

---

### 53. Read

**Purpose**: Read files from sandboxed environment

**Parameters**:
- `file_path` (string, required): Absolute file path
- `offset` (number, optional): Line number to start from
- `limit` (number, optional): Number of lines to read

**Supports**:
- Text files (with line numbers)
- Images (displayed as multimodal content)
- Up to 2000 lines by default
- Lines truncated at 2000 chars

**Returns**:
- File content
- Line-by-line format
- Images rendered visually

**Best For**:
- Viewing files
- Code inspection
- Log reading
- Verification

**Note**: For Jupyter notebooks, use NotebookRead instead

---

### 54. Write

**Purpose**: Create or overwrite files in sandboxed environment

**Parameters**:
- `file_path` (string, required): Absolute file path
- `content` (string, required): File content

**Returns**:
- File creation confirmation

**Best For**:
- Creating code files
- Writing scripts
- Generating config files

**Important**:
- Always Read before overwriting
- Use MultiEdit for modifications
- Only create when explicitly needed
- Parent directories created automatically

---

### 55. MultiEdit

**Purpose**: Perform multiple sequential edits to a single file

**Parameters**:
- `file_path` (string, required): Absolute file path
- `edits` (array, required): Array of edit operations
  - `old_string` (string): Text to replace
  - `new_string` (string): Replacement text
  - `replace_all` (boolean, optional): Replace all occurrences (default: false)

**Returns**:
- Edit confirmation
- Updated file

**Best For**:
- Batch file edits
- Refactoring
- Multiple find-replace operations
- Configuration updates

**Important**:
- Edits are atomic (all succeed or none)
- Sequential processing (each operates on previous result)
- Always Read first
- Exact string matching (including whitespace)

---

### 56. DownloadFileWrapper

**Purpose**: Download file wrapper URLs to sandbox

**Parameters**:
- `file_wrapper_url` (string, required): File wrapper URL
- `destination_directory` (string, optional): Save location (default: './')
- `filename` (string, optional): Custom filename

**Supports**:
- `https://www.genspark.ai/api/files/v1/...`
- `https://www.genspark.ai/api/files/s/{short_url_id}`

**Returns**:
- Downloaded file path
- File metadata

**Best For**:
- Custom Python/Bash processing in sandbox
- User-requested sandbox downloads

**When NOT to use**:
- Image understanding → use understand_images
- Audio transcription → use audio_transcribe
- File conversion → use file_format_converter

---

## Document & Content Creation

### 57. create_agent

**Purpose**: Create specialized agents for complex content tasks

**Parameters**:
- `task_type` (enum, required):
  - `podcasts`: Audio podcasts with AI characters
  - `docs`: HTML/Markdown documents (professional formatting)
  - `slides`: Presentation slides (HTML format, PPTX export)
  - `sheets`: Spreadsheets
  - `deep_research`: Deep research on topics
  - `website`: Professional websites/web pages
  - `clip_genius`: Video editor (long to short clips)
- `task_name` (string, required): Project name
- `query` (string, required): Task query/request
- `instructions` (string, required): Detailed instructions (system prompt)
- `session_id` (string, optional): For agent reuse (not supported yet)

**Returns**:
- Agent session
- Generated content URL
- Task ID

**Best For**:
- Professional documents
- Presentations
- Research projects
- Websites
- Podcasts
- Video editing

**Important**:
- Docs: Word-like formatting, not web design
- Slides: Takes minutes, ask user first
- Usually requires time, confirm with user
- Further edits done at task URL (/agents?id=xxx)

---

## Workspace Integration

### 58. notion_search

**Purpose**: Search Notion workspace for pages and content

**Parameters**:
- `query` (string, optional): Search query (empty = list all documents)

**Returns**:
- Notion pages
- Snippets
- Page IDs
- Titles and metadata

**Best For**:
- Finding Notion content
- Document discovery
- Workspace search

---

### 59. notion_read

**Purpose**: Retrieve and summarize full Notion page content

**Parameters**:
- `page_id` (string, required): Notion page ID

**Returns**:
- Full page content
- Structured data
- Summary

**Best For**:
- Reading Notion pages
- Content extraction
- Detailed page analysis

---

## Utility Tools

### 60. think

**Purpose**: Internal reasoning and memory (no external effects)

**Parameters**:
- `thought` (string, required): Thought to record

**Returns**:
- Logged thought

**Best For**:
- Complex reasoning
- Memory caching
- Planning
- Problem decomposition

**Note**: Does not obtain new information or change databases

---

### 61. ask_for_clarification

**Purpose**: Request additional information from user

**Parameters**:
- `question` (string, required): Clarification question

**Returns**:
- Awaits user response

**Best For**:
- Ambiguous requests
- Missing information
- Confirming assumptions
- Multiple valid approaches

---

## Summary Statistics

**Total Tools**: 61+ documented
**Categories**: 12 major categories
**Tool Types**:
- Search & Discovery: 8 tools
- Content Generation: 3 tools
- Content Analysis: 8 tools
- File Management: 4 tools
- Communication: 8 tools
- Visualization: 15 tools
- Code Execution: 5 tools
- Integration: 2 tools
- Utilities: 2 tools
- Others: 6 tools

---

**End of Documentation**
