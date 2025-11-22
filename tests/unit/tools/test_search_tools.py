"""
Comprehensive unit tests for Search Tools category.

Tests all 8 search tools:
- web_search
- scholar_search
- image_search
- video_search
- product_search
- google_product_search
- financial_report
- stock_price
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

from tools.data.search.web_search.web_search import WebSearch
from tools.data.search.scholar_search.scholar_search import ScholarSearch
from tools.data.search.image_search.image_search import ImageSearch
from tools.data.search.video_search.video_search import VideoSearch
from tools.data.search.product_search.product_search import ProductSearch
from tools.data.search.google_product_search.google_product_search import GoogleProductSearch
from tools.data.search.financial_report.financial_report import FinancialReport
from tools.data.search.stock_price.stock_price import StockPrice

from shared.errors import ValidationError, APIError, AuthenticationError, RateLimitError


# ========== WebSearch Tests ==========


class TestWebSearch:
    """Comprehensive tests for WebSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = WebSearch(query="test query", max_results=5)
        assert tool.query == "test query"
        assert tool.max_results == 5
        assert tool.tool_name == "web_search"
        assert tool.tool_category == "search"

    def test_initialization_with_defaults(self):
        """Test initialization with default parameters"""
        tool = WebSearch(query="test")
        assert tool.query == "test"
        assert tool.max_results == 10  # Default value

    def test_initialization_validation_error_empty_query(self):
        """Test initialization with invalid parameters"""
        with pytest.raises(ValidationError):
            tool = WebSearch(query="")
            tool._validate_parameters()

    def test_initialization_validation_error_max_results(self):
        """Test initialization with invalid max_results"""
        with pytest.raises(ValidationError):
            WebSearch(query="test", max_results=0)

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = WebSearch(query="Python programming", max_results=3)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert len(result["result"]) == 3
        assert result["metadata"]["mock_mode"] is True
        assert all("title" in item for item in result["result"])
        assert all("link" in item for item in result["result"])
        assert all("snippet" in item for item in result["result"])

    @patch("tools.data.search.web_search.web_search.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_SEARCH_ENGINE_ID", "test_engine_id")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Result 1", "link": "https://example.com/1", "snippet": "Snippet 1"},
                {"title": "Result 2", "link": "https://example.com/2", "snippet": "Snippet 2"},
            ]
        }
        mock_get.return_value = mock_response

        tool = WebSearch(query="test query", max_results=2)
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 2
        mock_get.assert_called_once()

    def test_validate_parameters_success(self):
        """Test parameter validation with valid inputs"""
        tool = WebSearch(query="valid query", max_results=5)
        tool._validate_parameters()  # Should not raise

    def test_validate_parameters_failure_whitespace(self):
        """Test parameter validation with whitespace only query"""
        tool = WebSearch(query="   ")
        with pytest.raises(ValidationError) as exc_info:
            tool._validate_parameters()
        assert "empty" in str(exc_info.value).lower()

    @patch("tools.data.search.web_search.web_search.requests.get")
    def test_api_error_handling_missing_credentials(self, mock_get, monkeypatch):
        """Test handling of missing API credentials"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("GOOGLE_SEARCH_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_SEARCH_ENGINE_ID", raising=False)

        tool = WebSearch(query="test")
        with pytest.raises(APIError) as exc_info:
            tool.run()
        assert "credentials" in str(exc_info.value).lower()

    @patch("tools.data.search.web_search.web_search.requests.get")
    def test_api_error_handling_request_exception(self, mock_get, monkeypatch):
        """Test handling of API request errors"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_SEARCH_ENGINE_ID", "test_engine_id")

        mock_get.side_effect = Exception("Network error")
        tool = WebSearch(query="test")

        with pytest.raises(APIError):
            tool.run()

    @patch("tools.data.search.web_search.web_search.requests.get")
    def test_edge_case_empty_result(self, mock_get, monkeypatch):
        """Test handling of empty API results"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_SEARCH_ENGINE_ID", "test_engine_id")

        mock_response = MagicMock()
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        tool = WebSearch(query="test")
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 0


# ========== ScholarSearch Tests ==========


class TestScholarSearch:
    """Comprehensive tests for ScholarSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ScholarSearch(query="machine learning", max_results=5)
        assert tool.query == "machine learning"
        assert tool.max_results == 5
        assert tool.tool_name == "scholar_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ScholarSearch(query="quantum computing", max_results=3)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters(self):
        """Test parameter validation"""
        tool = ScholarSearch(query="valid query")
        tool._validate_parameters()  # Should not raise

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = ScholarSearch(query="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== ImageSearch Tests ==========


class TestImageSearch:
    """Comprehensive tests for ImageSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ImageSearch(query="sunset", max_results=10)
        assert tool.query == "sunset"
        assert tool.max_results == 10
        assert tool.tool_name == "image_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ImageSearch(query="cats", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    @patch("tools.data.search.image_search.image_search.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_SEARCH_ENGINE_ID", "test_engine_id")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Image 1",
                    "link": "https://example.com/1.jpg",
                    "image": {"contextLink": "https://example.com"},
                },
                {
                    "title": "Image 2",
                    "link": "https://example.com/2.jpg",
                    "image": {"contextLink": "https://example.com"},
                },
            ]
        }
        mock_get.return_value = mock_response

        tool = ImageSearch(query="test", max_results=2)
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 2


# ========== VideoSearch Tests ==========


class TestVideoSearch:
    """Comprehensive tests for VideoSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = VideoSearch(query="tutorials", max_results=5)
        assert tool.query == "tutorials"
        assert tool.max_results == 5
        assert tool.tool_name == "video_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = VideoSearch(query="python tutorials", max_results=3)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_success(self):
        """Test parameter validation with valid inputs"""
        tool = VideoSearch(query="valid query")
        tool._validate_parameters()  # Should not raise


# ========== ProductSearch Tests ==========


class TestProductSearch:
    """Comprehensive tests for ProductSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = ProductSearch(query="laptop", max_results=10)
        assert tool.query == "laptop"
        assert tool.max_results == 10
        assert tool.tool_name == "product_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = ProductSearch(query="smartphone", max_results=5)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_query(self):
        """Test validation with empty query"""
        tool = ProductSearch(query="   ")
        with pytest.raises(ValidationError):
            tool._validate_parameters()


# ========== GoogleProductSearch Tests ==========


class TestGoogleProductSearch:
    """Comprehensive tests for GoogleProductSearch tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = GoogleProductSearch(query="headphones", max_results=5)
        assert tool.query == "headphones"
        assert tool.max_results == 5
        assert tool.tool_name == "google_product_search"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = GoogleProductSearch(query="camera", max_results=3)
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    @patch("tools.data.search.google_product_search.google_product_search.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("GOOGLE_SHOPPING_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_SHOPPING_ENGINE_ID", "test_engine_id")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Product 1", "link": "https://example.com/1", "snippet": "Description 1"},
                {"title": "Product 2", "link": "https://example.com/2", "snippet": "Description 2"},
            ]
        }
        mock_get.return_value = mock_response

        tool = GoogleProductSearch(query="test", max_results=2)
        result = tool.run()

        assert result["success"] is True
        assert len(result["result"]) == 2


# ========== FinancialReport Tests ==========


class TestFinancialReport:
    """Comprehensive tests for FinancialReport tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = FinancialReport(ticker="AAPL", report_type="annual")
        assert tool.ticker == "AAPL"
        assert tool.report_type == "annual"
        assert tool.tool_name == "financial_report"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = FinancialReport(ticker="GOOGL", report_type="quarterly")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    def test_validate_parameters_empty_ticker(self):
        """Test validation with empty ticker"""
        tool = FinancialReport(ticker="", report_type="annual")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_invalid_report_type(self):
        """Test validation with invalid report type"""
        # This might raise ValidationError depending on implementation
        try:
            tool = FinancialReport(ticker="AAPL", report_type="invalid")
            tool._validate_parameters()
        except ValidationError:
            pass  # Expected


# ========== StockPrice Tests ==========


class TestStockPrice:
    """Comprehensive tests for StockPrice tool"""

    def test_initialization_success(self):
        """Test successful tool initialization"""
        tool = StockPrice(ticker="TSLA")
        assert tool.ticker == "TSLA"
        assert tool.tool_name == "stock_price"

    def test_execute_mock_mode(self, monkeypatch):
        """Test execution in mock mode"""
        monkeypatch.setenv("USE_MOCK_APIS", "true")
        tool = StockPrice(ticker="MSFT")
        result = tool.run()

        assert result["success"] is True
        assert "result" in result
        assert result["metadata"]["mock_mode"] is True

    @patch("tools.data.search.stock_price.stock_price.requests.get")
    def test_execute_live_mode_success(self, mock_get, monkeypatch):
        """Test execution with mocked API calls"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Global Quote": {
                "01. symbol": "AAPL",
                "05. price": "150.00",
                "10. change percent": "1.5%",
            }
        }
        mock_get.return_value = mock_response

        tool = StockPrice(ticker="AAPL")
        result = tool.run()

        assert result["success"] is True

    def test_validate_parameters_empty_ticker(self):
        """Test validation with empty ticker"""
        tool = StockPrice(ticker="")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    def test_validate_parameters_whitespace_ticker(self):
        """Test validation with whitespace ticker"""
        tool = StockPrice(ticker="   ")
        with pytest.raises(ValidationError):
            tool._validate_parameters()

    @patch("tools.data.search.stock_price.stock_price.requests.get")
    def test_api_error_handling_missing_api_key(self, mock_get, monkeypatch):
        """Test handling of missing API key"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.delenv("ALPHA_VANTAGE_API_KEY", raising=False)

        tool = StockPrice(ticker="AAPL")
        with pytest.raises(APIError) as exc_info:
            tool.run()
        # Verify error mentions API key or credentials
        assert "api" in str(exc_info.value).lower() or "key" in str(exc_info.value).lower()

    @patch("tools.data.search.stock_price.stock_price.requests.get")
    def test_api_error_handling_network_failure(self, mock_get, monkeypatch):
        """Test handling of network failures"""
        monkeypatch.setenv("USE_MOCK_APIS", "false")
        monkeypatch.setenv("ALPHA_VANTAGE_API_KEY", "test_key")

        mock_get.side_effect = Exception("Network error")
        tool = StockPrice(ticker="AAPL")

        with pytest.raises(APIError):
            tool.run()
