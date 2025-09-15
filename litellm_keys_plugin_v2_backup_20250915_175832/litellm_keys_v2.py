"""
LiteLLM Keys Router V2 - API-Based Implementation

This module provides API endpoints for managing LiteLLM API keys through
LiteLLM's existing API, eliminating the need for database storage.

Author: LiteLLM Key Management Plugin
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from open_webui.models.users import UserModel
from open_webui.models.groups import Groups
from open_webui.utils.auth import get_verified_user, get_admin_user
from open_webui.utils.litellm_client import litellm_client
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


############################
# Pydantic Models
############################

class LiteLLMKeyCreateForm(BaseModel):
    """Form model for creating new LiteLLM keys."""
    key_name: str
    groups: Optional[List[str]] = None
    description: Optional[str] = None


class LiteLLMKeyUpdateForm(BaseModel):
    """Form model for updating existing LiteLLM keys."""
    key_name: Optional[str] = None
    groups: Optional[List[str]] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class LiteLLMKeyResponse(BaseModel):
    """Response model for LiteLLM key data."""
    id: str
    user_id: str
    key_name: str
    api_key: str  # This will be masked in responses
    groups: List[str]
    is_active: bool
    description: Optional[str] = None
    created_at: float
    updated_at: Optional[float] = None
    last_used_at: Optional[float] = None
    is_shared: Optional[bool] = False


class LiteLLMKeyListResponse(BaseModel):
    """Response model for listing LiteLLM keys."""
    keys: List[LiteLLMKeyResponse]
    total: int


class LiteLLMKeyStatusResponse(BaseModel):
    """Response model for key status information."""
    id: str
    is_active: bool
    usage_count: int
    last_used: Optional[str] = None
    expires_at: Optional[str] = None
    budget_used: float
    budget_limit: Optional[float] = None


############################
# Helper Functions
############################

def check_litellm_access(user: UserModel) -> bool:
    """
    Check if user has access to LiteLLM key management.
    
    Args:
        user: The user to check access for
        
    Returns:
        bool: True if user has access, False otherwise
    """
    # For now, allow all authenticated users
    # In production, you might want to check specific permissions or groups
    return user.role in ["admin", "user"]


def get_user_groups(user: UserModel) -> List[str]:
    """
    Get the group IDs that a user belongs to.
    
    Args:
        user: The user to get groups for
        
    Returns:
        List[str]: List of group IDs
    """
    try:
        user_groups = Groups.get_user_groups(user.id)
        return [group.id for group in user_groups]
    except Exception as e:
        log.warning(f"Failed to get user groups for user {user.id}: {e}")
        return []


############################
# API Endpoints
############################

@router.get("/", response_model=LiteLLMKeyListResponse)
async def get_litellm_keys(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get all LiteLLM keys for the authenticated user.
    
    Args:
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyListResponse: List of keys and total count
        
    Raises:
        HTTPException: If user doesn't have access or other error occurs
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        keys = await litellm_client.get_user_keys(user.id)
        
        # Convert to response format
        key_responses = []
        for key in keys:
            key_responses.append(LiteLLMKeyResponse(
                id=key.get("id", ""),
                user_id=key.get("user_id", user.id),
                key_name=key.get("key_name", ""),
                api_key=key.get("api_key", ""),  # Already masked by client
                groups=key.get("groups", []),
                is_active=key.get("is_active", True),
                description=key.get("description", ""),
                created_at=key.get("created_at", 0),
                updated_at=key.get("updated_at"),
                last_used_at=key.get("last_used_at"),
                is_shared=False
            ))
        
        return LiteLLMKeyListResponse(keys=key_responses, total=len(key_responses))
        
    except Exception as e:
        log.error(f"Error getting LiteLLM keys for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve LiteLLM keys"
        )


@router.get("/{key_id}", response_model=LiteLLMKeyResponse)
async def get_litellm_key(
    key_id: str,
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get a specific LiteLLM key by ID.
    
    Args:
        key_id: ID of the key to retrieve
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyResponse: The requested key
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Get user's keys and find the specific one
        keys = await litellm_client.get_user_keys(user.id)
        key = next((k for k in keys if k.get("id") == key_id), None)
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LiteLLM key not found"
            )
        
        return LiteLLMKeyResponse(
            id=key.get("id", ""),
            user_id=key.get("user_id", user.id),
            key_name=key.get("key_name", ""),
            api_key=key.get("api_key", ""),  # Already masked
            groups=key.get("groups", []),
            is_active=key.get("is_active", True),
            description=key.get("description", ""),
            created_at=key.get("created_at", 0),
            updated_at=key.get("updated_at"),
            last_used_at=key.get("last_used_at"),
            is_shared=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting LiteLLM key {key_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve LiteLLM key"
        )


@router.post("/", response_model=LiteLLMKeyResponse)
async def create_litellm_key(
    key_data: LiteLLMKeyCreateForm,
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Create a new LiteLLM key.
    
    Args:
        key_data: Key creation data
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyResponse: The created key (with actual API key shown once)
        
    Raises:
        HTTPException: If user doesn't have access or validation fails
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Validate group access if groups are provided
        if key_data.groups:
            user_groups = get_user_groups(user)
            invalid_groups = [gid for gid in key_data.groups if gid not in user_groups]
            if invalid_groups:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User is not a member of groups: {', '.join(invalid_groups)}"
                )
        
        # Create the key through LiteLLM API
        key = await litellm_client.create_user_key(
            user_id=user.id,
            key_name=key_data.key_name,
            groups=key_data.groups or []
        )
        
        return LiteLLMKeyResponse(
            id=key.get("id", ""),
            user_id=key.get("user_id", user.id),
            key_name=key.get("key_name", ""),
            api_key=key.get("api_key", ""),  # This is the actual key (shown once)
            groups=key.get("groups", []),
            is_active=key.get("is_active", True),
            description=key.get("description", ""),
            created_at=key.get("created_at", 0),
            updated_at=key.get("updated_at"),
            last_used_at=key.get("last_used_at"),
            is_shared=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating LiteLLM key for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create LiteLLM key: {str(e)}"
        )


@router.put("/{key_id}", response_model=LiteLLMKeyResponse)
async def update_litellm_key(
    key_id: str,
    update_data: LiteLLMKeyUpdateForm,
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Update an existing LiteLLM key.
    
    Args:
        key_id: ID of the key to update
        update_data: Update data
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyResponse: The updated key (without actual API key)
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Validate group access if groups are provided
        if update_data.groups:
            user_groups = get_user_groups(user)
            invalid_groups = [gid for gid in update_data.groups if gid not in user_groups]
            if invalid_groups:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User is not a member of groups: {', '.join(invalid_groups)}"
                )
        
        # Update the key through LiteLLM API
        key = await litellm_client.update_user_key(
            key_id=key_id,
            user_id=user.id,
            updates=update_data.dict(exclude_unset=True)
        )
        
        return LiteLLMKeyResponse(
            id=key.get("id", ""),
            user_id=key.get("user_id", user.id),
            key_name=key.get("key_name", ""),
            api_key=key.get("api_key", ""),  # This will be masked
            groups=key.get("groups", []),
            is_active=key.get("is_active", True),
            description=key.get("description", ""),
            created_at=key.get("created_at", 0),
            updated_at=key.get("updated_at"),
            last_used_at=key.get("last_used_at"),
            is_shared=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating LiteLLM key {key_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update LiteLLM key: {str(e)}"
        )


@router.delete("/{key_id}")
async def delete_litellm_key(
    key_id: str,
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Delete a LiteLLM key.
    
    Args:
        key_id: ID of the key to delete
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        success = await litellm_client.delete_user_key(key_id, user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LiteLLM key not found"
            )
        
        return {"message": "LiteLLM key deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error deleting LiteLLM key {key_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete LiteLLM key: {str(e)}"
        )


@router.get("/{key_id}/status", response_model=LiteLLMKeyStatusResponse)
async def get_litellm_key_status(
    key_id: str,
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get the current status of a LiteLLM key.
    
    Args:
        key_id: ID of the key to get status for
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyStatusResponse: Key status information
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Verify user owns the key
        keys = await litellm_client.get_user_keys(user.id)
        if not any(k.get("id") == key_id for k in keys):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LiteLLM key not found"
            )
        
        status_info = await litellm_client.get_key_status(key_id)
        
        return LiteLLMKeyStatusResponse(
            id=status_info.get("id", key_id),
            is_active=status_info.get("is_active", True),
            usage_count=status_info.get("usage_count", 0),
            last_used=status_info.get("last_used"),
            expires_at=status_info.get("expires_at"),
            budget_used=status_info.get("budget_used", 0),
            budget_limit=status_info.get("budget_limit")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting status for LiteLLM key {key_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get key status"
        )


@router.get("/groups/accessible", response_model=LiteLLMKeyListResponse)
async def get_accessible_litellm_keys(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get LiteLLM keys accessible through user's groups.
    
    Args:
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        LiteLLMKeyListResponse: List of accessible keys
        
    Raises:
        HTTPException: If user doesn't have access or other error occurs
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        user_groups = get_user_groups(user)
        keys = await litellm_client.get_accessible_keys(user.id, user_groups)
        
        # Convert to response format
        key_responses = []
        for key in keys:
            key_responses.append(LiteLLMKeyResponse(
                id=key.get("id", ""),
                user_id=key.get("user_id", ""),
                key_name=key.get("key_name", ""),
                api_key=key.get("api_key", ""),  # Already masked
                groups=key.get("groups", []),
                is_active=key.get("is_active", True),
                description=key.get("description", ""),
                created_at=key.get("created_at", 0),
                updated_at=key.get("updated_at"),
                last_used_at=key.get("last_used_at"),
                is_shared=key.get("is_shared", False)
            ))
        
        return LiteLLMKeyListResponse(keys=key_responses, total=len(key_responses))
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting accessible LiteLLM keys for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accessible LiteLLM keys"
        )


@router.get("/health/connection")
async def test_litellm_connection(
    request: Request,
    user: UserModel = Depends(get_admin_user)
):
    """
    Test the connection to LiteLLM API (admin only).
    
    Args:
        request: FastAPI request object
        user: Admin user
        
    Returns:
        dict: Connection status
        
    Raises:
        HTTPException: If user is not admin
    """
    try:
        is_connected = await litellm_client.test_connection()
        
        return {
            "connected": is_connected,
            "base_url": litellm_client.base_url,
            "enabled": litellm_client.enabled,
            "master_key_configured": bool(litellm_client.master_key)
        }
        
    except Exception as e:
        log.error(f"Error testing LiteLLM connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test LiteLLM connection"
        )