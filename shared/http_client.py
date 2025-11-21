"""
HTTP Client Abstraction for agentswarm-tools.

Provides a singleton HTTP client with connection pooling, retry logic,
and standardized error handling.
"""

import os
import time
import logging
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from shared.errors import APIError

logger = logging.getLogger(__name__)


class HTTPClient:
    """Shared HTTP client with connection pooling and retry logic."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the HTTP session with connection pooling and retry logic."""
        self.session = requests.Session()

        # Configure retry logic with exponential backoff
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.default_timeout = 30

        logger.debug("HTTPClient initialized with connection pooling and retry logic")

    def _log_request(self, method: str, url: str, **kwargs):
        """Log outgoing request details."""
        logger.debug(f"HTTP {method} request to {url}")
        if kwargs.get("params"):
            logger.debug(f"  Query params: {kwargs['params']}")
        if kwargs.get("json"):
            logger.debug(f"  JSON body: {kwargs['json']}")

    def _log_response(self, response: requests.Response):
        """Log response details."""
        logger.debug(f"HTTP response: {response.status_code} from {response.url}")
        logger.debug(f"  Response time: {response.elapsed.total_seconds():.3f}s")

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP GET request.

        Args:
            url: The URL to request
            **kwargs: Additional arguments passed to requests.get()

        Returns:
            requests.Response object

        Raises:
            APIError: If the request fails
        """
        kwargs.setdefault("timeout", self.default_timeout)
        self._log_request("GET", url, **kwargs)

        try:
            response = self.session.get(url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
            return response
        except requests.Timeout as e:
            raise APIError(f"HTTP GET timeout for {url}: {e}")
        except requests.ConnectionError as e:
            raise APIError(f"HTTP GET connection error for {url}: {e}")
        except requests.HTTPError as e:
            raise APIError(f"HTTP GET failed with status {e.response.status_code}: {e}")
        except requests.RequestException as e:
            raise APIError(f"HTTP GET failed for {url}: {e}")

    def post(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP POST request.

        Args:
            url: The URL to request
            **kwargs: Additional arguments passed to requests.post()

        Returns:
            requests.Response object

        Raises:
            APIError: If the request fails
        """
        kwargs.setdefault("timeout", self.default_timeout)
        self._log_request("POST", url, **kwargs)

        try:
            response = self.session.post(url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
            return response
        except requests.Timeout as e:
            raise APIError(f"HTTP POST timeout for {url}: {e}")
        except requests.ConnectionError as e:
            raise APIError(f"HTTP POST connection error for {url}: {e}")
        except requests.HTTPError as e:
            raise APIError(f"HTTP POST failed with status {e.response.status_code}: {e}")
        except requests.RequestException as e:
            raise APIError(f"HTTP POST failed for {url}: {e}")

    def put(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP PUT request.

        Args:
            url: The URL to request
            **kwargs: Additional arguments passed to requests.put()

        Returns:
            requests.Response object

        Raises:
            APIError: If the request fails
        """
        kwargs.setdefault("timeout", self.default_timeout)
        self._log_request("PUT", url, **kwargs)

        try:
            response = self.session.put(url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
            return response
        except requests.Timeout as e:
            raise APIError(f"HTTP PUT timeout for {url}: {e}")
        except requests.ConnectionError as e:
            raise APIError(f"HTTP PUT connection error for {url}: {e}")
        except requests.HTTPError as e:
            raise APIError(f"HTTP PUT failed with status {e.response.status_code}: {e}")
        except requests.RequestException as e:
            raise APIError(f"HTTP PUT failed for {url}: {e}")

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        Perform an HTTP DELETE request.

        Args:
            url: The URL to request
            **kwargs: Additional arguments passed to requests.delete()

        Returns:
            requests.Response object

        Raises:
            APIError: If the request fails
        """
        kwargs.setdefault("timeout", self.default_timeout)
        self._log_request("DELETE", url, **kwargs)

        try:
            response = self.session.delete(url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
            return response
        except requests.Timeout as e:
            raise APIError(f"HTTP DELETE timeout for {url}: {e}")
        except requests.ConnectionError as e:
            raise APIError(f"HTTP DELETE connection error for {url}: {e}")
        except requests.HTTPError as e:
            raise APIError(f"HTTP DELETE failed with status {e.response.status_code}: {e}")
        except requests.RequestException as e:
            raise APIError(f"HTTP DELETE failed for {url}: {e}")


# Singleton instance for easy import
http_client = HTTPClient()


if __name__ == "__main__":
    # Test the HTTP client
    print("Testing HTTPClient...")

    # Configure logging for test output
    logging.basicConfig(level=logging.DEBUG)

    # Test singleton behavior
    client1 = HTTPClient()
    client2 = HTTPClient()
    assert client1 is client2, "Singleton pattern failed"
    print("Singleton pattern: OK")

    # Test GET request
    try:
        response = http_client.get("https://httpbin.org/get", params={"test": "value"})
        print(f"GET request: OK (status {response.status_code})")
    except APIError as e:
        print(f"GET request failed (expected if offline): {e}")

    # Test POST request
    try:
        response = http_client.post("https://httpbin.org/post", json={"key": "value"})
        print(f"POST request: OK (status {response.status_code})")
    except APIError as e:
        print(f"POST request failed (expected if offline): {e}")

    # Test error handling
    try:
        http_client.get("https://httpbin.org/status/404")
        print("Error handling: FAILED (should have raised APIError)")
    except APIError as e:
        print(f"Error handling: OK (caught APIError: {e})")

    print("\nHTTPClient tests completed.")
