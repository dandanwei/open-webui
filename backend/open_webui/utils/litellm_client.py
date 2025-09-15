"""
LiteLLM API Client

This module provides a client for interacting with LiteLLM's API to manage
API keys without requiring database storage. It uses a master API key to
manage user keys through LiteLLM's existing API.

Author: LiteLLM Key Management Plugin
"""

import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from open_webui.config import LITELLM_MASTER_API_KEY, LITELLM_BASE_URL, LITELLM_ENABLED
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS.get("LITELLM_CLIENT", "INFO"))


class LiteLLMClient:
    """
    Client for interacting with LiteLLM API for key management.
    
    This client uses a master API key to manage user keys through LiteLLM's
    existing API endpoints, eliminating the need for database storage.
    """
    
    def __init__(self, base_url: str = None, master_key: str = None):
        """
        Initialize the LiteLLM client.
        
        Args:
            base_url: LiteLLM server base URL
            master_key: Master API key for authentication
        """
        self.base_url = base_url or LITELLM_BASE_URL
        self.master_key = master_key or LITELLM_MASTER_API_KEY
        self.enabled = LITELLM_ENABLED
        
        if not self.enabled:
            log.warning("LiteLLM integration is disabled")
        
        if not self.master_key:
            log.warning("LiteLLM master API key is not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.master_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the LiteLLM API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            Exception: If request fails
        """
        if not self.enabled:
            raise Exception("LiteLLM integration is disabled")
        
        if not self.master_key:
            raise Exception("LiteLLM master API key is not configured")
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = response_data.get("detail", f"HTTP {response.status}")
                        raise Exception(f"LiteLLM API error: {error_msg}")
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            log.error(f"LiteLLM API request failed: {e}")
            raise Exception(f"Failed to connect to LiteLLM API: {e}")
        except Exception as e:
            log.error(f"LiteLLM API error: {e}")
            raise
    
    async def get_user_keys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all API keys for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user's API keys
        """
        try:
            # LiteLLM API endpoint for getting user keys
            # This assumes LiteLLM has an endpoint like /key/info or /user/{user_id}/keys
            response = await self._make_request("GET", f"/key/info")
            
            # Filter keys for the specific user
            user_keys = []
            for key_info in response.get("data", []):
                if key_info.get("user_id") == user_id:
                    # Mask the key for security
                    key_info["api_key"] = self._mask_key(key_info.get("api_key", ""))
                    user_keys.append(key_info)
            
            return user_keys
            
        except Exception as e:
            log.error(f"Failed to get user keys for {user_id}: {e}")
            return []
    
    async def create_user_key(self, user_id: str, key_name: str, groups: List[str] = None) -> Dict[str, Any]:
        """
        Create a new API key for a user.
        
        Args:
            user_id: User identifier
            key_name: Name for the key
            groups: List of groups the key belongs to
            
        Returns:
            Created key information (including the actual key)
        """
        try:
            # LiteLLM API endpoint for creating keys
            key_data = {
                "user_id": user_id,
                "key_name": key_name,
                "groups": groups or [],
                "duration": None,  # No expiration
                "models": [],  # Allow all models
                "max_budget": None,  # No budget limit
                "metadata": {
                    "created_by": "open_webui_plugin",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            response = await self._make_request("POST", "/key/generate", key_data)
            
            # Return the key info with the actual key (only shown once)
            return {
                "id": response.get("key_id"),
                "user_id": user_id,
                "key_name": key_name,
                "api_key": response.get("key"),  # This is the actual key
                "groups": groups or [],
                "created_at": datetime.utcnow().timestamp(),
                "is_active": True,
                "description": f"Key created for {key_name}"
            }
            
        except Exception as e:
            log.error(f"Failed to create key for user {user_id}: {e}")
            raise Exception(f"Failed to create API key: {e}")
    
    async def update_user_key(self, key_id: str, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing API key.
        
        Args:
            key_id: Key identifier
            user_id: User identifier
            updates: Updates to apply
            
        Returns:
            Updated key information
        """
        try:
            # LiteLLM API endpoint for updating keys
            update_data = {
                "key_id": key_id,
                "user_id": user_id,
                **updates
            }
            
            response = await self._make_request("PUT", f"/key/update", update_data)
            
            # Return updated key info (without the actual key)
            return {
                "id": key_id,
                "user_id": user_id,
                "key_name": updates.get("key_name", ""),
                "api_key": self._mask_key(""),  # Never return the actual key on updates
                "groups": updates.get("groups", []),
                "updated_at": datetime.utcnow().timestamp(),
                "is_active": updates.get("is_active", True)
            }
            
        except Exception as e:
            log.error(f"Failed to update key {key_id} for user {user_id}: {e}")
            raise Exception(f"Failed to update API key: {e}")
    
    async def delete_user_key(self, key_id: str, user_id: str) -> bool:
        """
        Delete an API key.
        
        Args:
            key_id: Key identifier
            user_id: User identifier
            
        Returns:
            True if successful
        """
        try:
            # LiteLLM API endpoint for deleting keys
            await self._make_request("DELETE", f"/key/delete", {
                "key_id": key_id,
                "user_id": user_id
            })
            
            return True
            
        except Exception as e:
            log.error(f"Failed to delete key {key_id} for user {user_id}: {e}")
            raise Exception(f"Failed to delete API key: {e}")
    
    async def get_key_status(self, key_id: str) -> Dict[str, Any]:
        """
        Get the current status of an API key.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key status information
        """
        try:
            # LiteLLM API endpoint for getting key status
            response = await self._make_request("GET", f"/key/info/{key_id}")
            
            return {
                "id": key_id,
                "is_active": response.get("is_active", True),
                "usage_count": response.get("usage_count", 0),
                "last_used": response.get("last_used"),
                "expires_at": response.get("expires_at"),
                "budget_used": response.get("budget_used", 0),
                "budget_limit": response.get("budget_limit")
            }
            
        except Exception as e:
            log.error(f"Failed to get status for key {key_id}: {e}")
            return {
                "id": key_id,
                "is_active": False,
                "error": str(e)
            }
    
    async def get_accessible_keys(self, user_id: str, user_groups: List[str]) -> List[Dict[str, Any]]:
        """
        Get keys accessible to a user through group membership.
        
        Args:
            user_id: User identifier
            user_groups: List of groups the user belongs to
            
        Returns:
            List of accessible keys
        """
        try:
            # Get all keys and filter by group membership
            response = await self._make_request("GET", "/key/info")
            
            accessible_keys = []
            for key_info in response.get("data", []):
                key_groups = key_info.get("groups", [])
                
                # Check if user has access through group membership
                if (key_info.get("user_id") == user_id or 
                    any(group in user_groups for group in key_groups)):
                    
                    # Mask the key for security
                    key_info["api_key"] = self._mask_key(key_info.get("api_key", ""))
                    key_info["is_shared"] = key_info.get("user_id") != user_id
                    accessible_keys.append(key_info)
            
            return accessible_keys
            
        except Exception as e:
            log.error(f"Failed to get accessible keys for user {user_id}: {e}")
            return []
    
    def _mask_key(self, api_key: str) -> str:
        """
        Mask an API key for display purposes.
        
        Args:
            api_key: The API key to mask
            
        Returns:
            Masked API key
        """
        if not api_key or len(api_key) <= 12:
            return "*" * (len(api_key) if api_key else 8)
        
        return api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
    
    async def test_connection(self) -> bool:
        """
        Test the connection to LiteLLM API.
        
        Returns:
            True if connection is successful
        """
        try:
            await self._make_request("GET", "/health")
            return True
        except Exception as e:
            log.error(f"LiteLLM connection test failed: {e}")
            return False


# Global client instance
litellm_client = LiteLLMClient()