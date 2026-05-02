"""Fiverr API client implementation."""

import logging
import requests
from typing import Any, Dict, Optional
from ..utils.logger import get_logger
from ..utils.exceptions import APIError

logger = get_logger(__name__)


class FiverrAPIClient:
    """HTTP client for interacting with Fiverr's API endpoints.
    
    This class handles authentication, making authenticated requests,
    and processing API responses.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None
    ):
        """Initialize the Fiverr API client.
        
        Args:
            api_key: Fiverr API key for authentication.
            api_secret: Fiverr API secret for authentication.
            base_url: Base URL for the Fiverr API.
            auth_token: Pre-existing authentication token.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._base_url = base_url or "https://api.fiverr.com/v1"
        self._auth_token = auth_token
        self._session = requests.Session()
        self._logger = logger
        
        self._logger.info("FiverrAPIClient initialized")
    
    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        return self._base_url
    
    @property
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated."""
        return bool(self._auth_token)
    
    def initialize(self) -> bool:
        """Initialize the client and establish connection.
        
        Returns:
            True if initialization successful, False otherwise.
        """
        self._logger.info("Initializing FiverrAPIClient")
        
        try:
            # Set up session defaults
            self._session.headers.update({
                "Content-Type": "application/json",
                "User-Agent": "FiverrAutomationTool/0.1.0"
            })
            
            self._logger.info("FiverrAPIClient initialization complete")
            return True
        except Exception as e:
            self._logger.error(f"Client initialization failed: {e}")
            return False
    
    def authenticate(self, api_key: Optional[str] = None, 
                     api_secret: Optional[str] = None,
                     auth_token: Optional[str] = None) -> bool:
        """Authenticate with Fiverr API.
        
        Args:
            api_key: API key for authentication.
            api_secret: API secret for authentication.
            auth_token: Pre-existing authentication token.
            
        Returns:
            True if authentication successful, False otherwise.
        """
        self._logger.info("Authenticating with Fiverr API")
        
        try:
            # Use provided credentials or fall back to stored ones
            self._api_key = api_key or self._api_key
            self._api_secret = api_secret or self._api_secret
            self._auth_token = auth_token or self._auth_token
            
            if not self._auth_token and self._api_key and self._api_secret:
                # Token-based authentication would go here
                # For now, we'll use API key as token
                self._auth_token = self._api_key
            
            if self._auth_token:
                self._session.headers["Authorization"] = f"Bearer {self._auth_token}"
                self._logger.info("Authentication successful")
                return True
            else:
                self._logger.warning("No authentication credentials provided")
                return False
                
        except Exception as e:
            self._logger.error(f"Authentication failed: {e}")
            return False
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Fiverr API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: API endpoint path.
            params: Query parameters for the request.
            data: Request body data.
            timeout: Request timeout in seconds.
            
        Returns:
            Dictionary containing the API response.
            
        Raises:
            APIError: If the API request fails.
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        
        self._logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=timeout
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.Timeout as e:
            self._logger.error(f"Request timeout: {e}")
            raise APIError(f"API request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            self._logger.error(f"Connection error: {e}")
            raise APIError(f"Connection error: {e}")
        except Exception as e:
            self._logger.error(f"Request failed: {e}")
            raise APIError(f"API request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
            timeout: int = 30) -> Dict[str, Any]:
        """Make a GET request to the API.
        
        Args:
            endpoint: API endpoint path.
            params: Query parameters.
            timeout: Request timeout in seconds.
            
        Returns:
            Dictionary containing the API response.
        """
        return self.make_request("GET", endpoint, params=params, timeout=timeout)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             timeout: int = 30) -> Dict[str, Any]:
        """Make a POST request to the API.
        
        Args:
            endpoint: API endpoint path.
            data: Request body data.
            timeout: Request timeout in seconds.
            
        Returns:
            Dictionary containing the API response.
        """
        return self.make_request("POST", endpoint, data=data, timeout=timeout)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            timeout: int = 30) -> Dict[str, Any]:
        """Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint path.
            data: Request body data.
            timeout: Request timeout in seconds.
            
        Returns:
            Dictionary containing the API response.
        """
        return self.make_request("PUT", endpoint, data=data, timeout=timeout)
    
    def delete(self, endpoint: str, timeout: int = 30) -> Dict[str, Any]:
        """Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint path.
            timeout: Request timeout in seconds.
            
        Returns:
            Dictionary containing the API response.
        """
        return self.make_request("DELETE", endpoint, timeout=timeout)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return parsed data.
        
        Args:
            response: The requests.Response object.
            
        Returns:
            Dictionary containing the parsed response data.
            
        Raises:
            APIError: If the response indicates an error.
        """
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}
        
        if response.status_code >= 400:
            error_msg = response_data.get("error", response_data.get("message", "Unknown error"))
            self._logger.error(f"API error {response.status_code}: {error_msg}")
            raise APIError(f"API error {response.status_code}: {error_msg}")
        
        self._logger.debug(f"Response status: {response.status_code}")
        return response_data
