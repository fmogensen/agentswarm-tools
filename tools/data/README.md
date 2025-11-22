# Data Tools

Tools for search, business intelligence, and AI-powered research and analysis.

## Subcategories

### Search (`search/`)
Search and retrieve information from various sources.

**Tools:**
- `web_search` - Search the web with Google/Bing
- `scholar_search` - Search academic papers and research
- `image_search` - Search for images across the web
- `video_search` - Search for videos on YouTube and other platforms
- `product_search` - Search for products and shopping results
- `google_product_search` - Specialized Google Shopping search
- `financial_report` - Retrieve financial reports and data
- `stock_price` - Get real-time and historical stock prices

### Business (`business/`)
Business analytics and reporting tools.

**Tools:**
- `data_aggregator` - Aggregate data from multiple sources
- `report_generator` - Generate business reports
- `trend_analyzer` - Analyze trends in data and metrics

### Intelligence (`intelligence/`)
AI-powered research and analysis tools.

**Tools:**
- `rag_pipeline` - Retrieval-Augmented Generation for Q&A
- `deep_research_agent` - Conduct deep research on topics

## Category Identifier

All tools in this category have:
```python
tool_category: str = "data"
```

## Usage Examples

### Search the web:
```python
from tools.data.search.web_search import WebSearch

tool = WebSearch(
    query="latest AI developments 2024",
    max_results=10
)
result = tool.run()
```

### Get stock data:
```python
from tools.data.search.stock_price import StockPrice

tool = StockPrice(
    symbol="AAPL",
    timeframe="1d"
)
result = tool.run()
```

### Conduct deep research:
```python
from tools.data.intelligence.deep_research_agent import DeepResearchAgent

tool = DeepResearchAgent(
    topic="Quantum Computing Applications in Drug Discovery",
    depth="comprehensive"
)
result = tool.run()
```

### Analyze business trends:
```python
from tools.data.business.trend_analyzer import TrendAnalyzer

tool = TrendAnalyzer(
    data_source="sales_data.csv",
    metrics=["revenue", "customer_count"],
    time_period="last_quarter"
)
result = tool.run()
```
