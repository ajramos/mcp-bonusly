"""
Bonusly API client for making HTTP requests to the Bonusly API.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import httpx
from dateutil.parser import parse as parse_date

from .models import (
    Bonus, BonusListResponse, BonusResponse, 
    CreateBonusRequest, ListBonusesRequest, GetBonusRequest
)
from .exceptions import (
    BonuslyError, BonuslyAuthenticationError, BonuslyAPIError,
    BonuslyNotFoundError, BonuslyRateLimitError, BonuslyConfigurationError
)

logger = logging.getLogger(__name__)


class BonuslyClient:
    """Client for interacting with the Bonusly API."""
    
    BASE_URL = "https://bonus.ly/api/v1"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Bonusly client.
        
        Args:
            api_token: Bonusly API token. If not provided, will try to get from environment.
        """
        self.api_token = api_token or os.getenv("BONUSLY_API_TOKEN")
        if not self.api_token:
            raise BonuslyConfigurationError(
                "Bonusly API token is required. Set BONUSLY_API_TOKEN environment variable "
                "or pass api_token parameter."
            )
        
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            timeout=30.0,
            headers={
                "User-Agent": "mcp-bonusly/1.1.1",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Bonusly API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON data for POST requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            BonuslyAuthenticationError: If authentication fails
            BonuslyAPIError: If API returns an error
            BonuslyRateLimitError: If rate limit is exceeded
            BonuslyNotFoundError: If resource is not found
        """
        # API token is sent via Authorization header (configured in client initialization)
        if params is None:
            params = {}
        
        try:
            logger.debug(f"Making {method} request to {endpoint} with params: {params}")
            
            response = self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 401:
                raise BonuslyAuthenticationError("Invalid API token")
            elif response.status_code == 404:
                raise BonuslyNotFoundError("Resource not found")
            elif response.status_code == 429:
                raise BonuslyRateLimitError("API rate limit exceeded")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", f"API error: {response.status_code}")
                except:
                    error_message = f"API error: {response.status_code}"
                
                raise BonuslyAPIError(
                    error_message, 
                    status_code=response.status_code,
                    response_data=error_data if 'error_data' in locals() else None
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise BonuslyError(f"Network error: {e}")
    
    def list_bonuses(self, request: ListBonusesRequest) -> List[Bonus]:
        """
        List bonuses with optional filtering.
        
        Args:
            request: Request parameters for listing bonuses
            
        Returns:
            List of Bonus objects
        """
        params = {"limit": request.limit}
        
        # Add optional filters
        if request.start_date:
            params["start_time"] = f"{request.start_date}T00:00:00Z"
        if request.end_date:
            params["end_time"] = f"{request.end_date}T23:59:59Z"
        if request.giver_email:
            params["giver_email"] = request.giver_email
        if request.receiver_email:
            params["receiver_email"] = request.receiver_email
        if request.user_email:
            params["user_email"] = request.user_email
        if request.hashtag:
            # Ensure hashtag starts with #
            hashtag = request.hashtag
            if not hashtag.startswith("#"):
                hashtag = f"#{hashtag}"
            params["hashtag"] = hashtag
        if request.include_children:
            params["include_children"] = "true"
        
        response_data = self._make_request("GET", "/bonuses", params=params)
        
        # Parse response
        bonuses = []
        for bonus_data in response_data.get("result", []):
            try:
                bonus = Bonus(**bonus_data)
                bonuses.append(bonus)
            except Exception as e:
                logger.warning(f"Failed to parse bonus data: {e}")
                continue
        
        return bonuses
    
    def create_bonus(self, request: CreateBonusRequest) -> Bonus:
        """
        Create a new bonus.
        
        Args:
            request: Request parameters for creating a bonus
            
        Returns:
            Created Bonus object
        """
        json_data = {
            "reason": request.reason
        }
        
        # Only include giver_email if specified (admin feature)
        if request.giver_email:
            json_data["giver_email"] = request.giver_email
        
        if request.parent_bonus_id:
            json_data["parent_bonus_id"] = request.parent_bonus_id
        
        response_data = self._make_request("POST", "/bonuses", json_data=json_data)
        
        # Parse response
        bonus_data = response_data.get("result")
        if not bonus_data:
            raise BonuslyAPIError("Invalid response format: missing result")
        
        return Bonus(**bonus_data)
    
    def get_bonus(self, request: GetBonusRequest) -> Bonus:
        """
        Get a specific bonus by ID.
        
        Args:
            request: Request parameters for getting a bonus
            
        Returns:
            Bonus object
        """
        response_data = self._make_request("GET", f"/bonuses/{request.bonus_id}")
        
        # Parse response
        bonus_data = response_data.get("result")
        if not bonus_data:
            raise BonuslyAPIError("Invalid response format: missing result")
        
        return Bonus(**bonus_data)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 