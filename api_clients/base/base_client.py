"""
Base API Client for all API integrations
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import requests
import logging
from datetime import datetime, timedelta
import time
import json

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Abstract base class for API clients"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 1,
        **kwargs
    ):
        """
        Initialize the base API client
        
        Args:
            api_key: API authentication key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.additional_config = kwargs
        
        # Set up session headers
        self._setup_headers()
        
        # Rate limiting attributes
        self.rate_limit_calls = kwargs.get('rate_limit_calls', 60)
        self.rate_limit_period = kwargs.get('rate_limit_period', 60)  # seconds
        self.call_timestamps: List[datetime] = []
        
    def _setup_headers(self):
        """Set up common headers for the session"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'API-Client/1.0'
        })
        
        if self.api_key:
            self._set_auth_header(self.api_key)
    
    @abstractmethod
    def _set_auth_header(self, api_key: str):
        """
        Set authentication header - must be implemented by subclasses
        
        Args:
            api_key: API key for authentication
        """
        pass
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.rate_limit_period)
        
        # Remove old timestamps
        self.call_timestamps = [ts for ts in self.call_timestamps if ts > cutoff]
        
        # Check if we've hit the rate limit
        if len(self.call_timestamps) >= self.rate_limit_calls:
            # Calculate wait time
            oldest = min(self.call_timestamps)
            wait_time = (oldest + timedelta(seconds=self.rate_limit_period) - now).total_seconds()
            if wait_time > 0:
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
        
        # Record this call
        self.call_timestamps.append(now)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (will be appended to base_url)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response object
            
        Raises:
            requests.RequestException: If request fails after all retries
        """
        # Check rate limit
        self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
        
        # Merge headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Attempt request with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check for rate limit headers
                self._handle_rate_limit_headers(response)
                
                # Raise exception for bad status codes
                response.raise_for_status()
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
                # Check if we should retry
                if attempt < self.max_retries - 1:
                    if self._should_retry(e, response if 'response' in locals() else None):
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        break
        
        # All retries exhausted
        logger.error(f"All retry attempts failed for {url}")
        raise last_exception
    
    def _should_retry(self, exception: Exception, response: Optional[requests.Response] = None) -> bool:
        """
        Determine if a request should be retried
        
        Args:
            exception: The exception that occurred
            response: The response object (if available)
            
        Returns:
            True if request should be retried, False otherwise
        """
        # Retry on connection errors
        if isinstance(exception, requests.exceptions.ConnectionError):
            return True
        
        # Retry on timeout
        if isinstance(exception, requests.exceptions.Timeout):
            return True
        
        # Retry on specific HTTP status codes
        if response and response.status_code in [429, 500, 502, 503, 504]:
            return True
        
        return False
    
    def _handle_rate_limit_headers(self, response: requests.Response):
        """
        Handle rate limit headers from the response
        
        Args:
            response: The response object
        """
        # Check for common rate limit headers
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining == 0 and 'X-RateLimit-Reset' in response.headers:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = reset_time - time.time()
                if wait_time > 0:
                    logger.info(f"Rate limit hit. Waiting {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a GET request
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request('GET', endpoint, params=params, **kwargs)
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a POST request
        
        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request('POST', endpoint, data=data, **kwargs)
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Make a PUT request
        
        Args:
            endpoint: API endpoint
            data: Request body data
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request('PUT', endpoint, data=data, **kwargs)
        return response.json()
    
    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make a DELETE request
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            JSON response as dictionary
        """
        response = self._make_request('DELETE', endpoint, **kwargs)
        return response.json()
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate the API connection - must be implemented by subclasses
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    def close(self):
        """Close the session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()