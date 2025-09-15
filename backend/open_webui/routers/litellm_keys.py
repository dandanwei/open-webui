"""
LiteLLM Keys Router

This module provides API endpoints for managing LiteLLM API keys in Open WebUI.
It includes functionality for creating, reading, updating, and deleting API keys
with proper authentication and access control.

Author: LiteLLM Key Management Plugin
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from open_webui.models.litellm_keys import (
    LiteLLMKeys,
    LiteLLMKeyCreateForm,
    LiteLLMKeyUpdateForm,
    LiteLLMKeyListResponse,
    LiteLLMKeyModel
)
from open_webui.models.users import UserModel
from open_webui.models.groups import Groups
from open_webui.utils.auth import get_verified_user, get_admin_user
from open_webui.utils.access_control import has_permission
from open_webui.constants import ERROR_MESSAGES
from open_webui.env import SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


############################
# Helper Functions
############################

def check_litellm_access(user: UserModel) -> bool:
    """
    Check if user has access to LiteLLM key management.
    
    This function can be extended to implement more sophisticated access control
    based on user groups, roles, or other criteria.
    
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
    skip: int = 0,
    limit: int = 100,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get all LiteLLM keys for the authenticated user.
    
    Args:
        request: FastAPI request object
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
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
        
        result = LiteLLMKeys.get_keys_by_user_id(user.id, skip=skip, limit=limit)
        return result
        
    except Exception as e:
        log.error(f"Error getting LiteLLM keys for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve LiteLLM keys"
        )


@router.get("/{key_id}", response_model=LiteLLMKeyModel)
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
        LiteLLMKeyModel: The requested key
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        key = LiteLLMKeys.get_key_by_id(key_id, user.id)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LiteLLM key not found"
            )
        
        return key
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting LiteLLM key {key_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve LiteLLM key"
        )


@router.post("/", response_model=LiteLLMKeyModel)
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
        LiteLLMKeyModel: The created key
        
    Raises:
        HTTPException: If user doesn't have access or validation fails
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Validate group access if group_ids are provided
        if key_data.group_ids:
            user_groups = get_user_groups(user)
            invalid_groups = [gid for gid in key_data.group_ids if gid not in user_groups]
            if invalid_groups:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User is not a member of groups: {', '.join(invalid_groups)}"
                )
        
        key = LiteLLMKeys.create_key(user.id, key_data)
        return key
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error creating LiteLLM key for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create LiteLLM key"
        )


@router.put("/{key_id}", response_model=LiteLLMKeyModel)
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
        LiteLLMKeyModel: The updated key
        
    Raises:
        HTTPException: If key not found or user doesn't have access
    """
    try:
        if not check_litellm_access(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to LiteLLM key management"
            )
        
        # Validate group access if group_ids are provided
        if update_data.group_ids:
            user_groups = get_user_groups(user)
            invalid_groups = [gid for gid in update_data.group_ids if gid not in user_groups]
            if invalid_groups:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User is not a member of groups: {', '.join(invalid_groups)}"
                )
        
        key = LiteLLMKeys.update_key(key_id, user.id, update_data)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LiteLLM key not found"
            )
        
        return key
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error updating LiteLLM key {key_id} for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update LiteLLM key"
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
        
        success = LiteLLMKeys.delete_key(key_id, user.id)
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
            detail="Failed to delete LiteLLM key"
        )


@router.get("/groups/accessible", response_model=List[LiteLLMKeyModel])
async def get_accessible_litellm_keys(
    request: Request,
    user: UserModel = Depends(get_verified_user)
):
    """
    Get LiteLLM keys accessible through user's groups.
    
    This endpoint returns keys that the user can access through group membership,
    in addition to their own keys.
    
    Args:
        request: FastAPI request object
        user: Authenticated user
        
    Returns:
        List[LiteLLMKeyModel]: List of accessible keys
        
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
        if not user_groups:
            return []
        
        keys = LiteLLMKeys.get_keys_by_group_ids(user_groups, user.id)
        return keys
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting accessible LiteLLM keys for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accessible LiteLLM keys"
        )


############################
# Admin Endpoints
############################

@router.get("/admin/all", response_model=LiteLLMKeyListResponse)
async def get_all_litellm_keys_admin(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    user: UserModel = Depends(get_admin_user)
):
    """
    Get all LiteLLM keys (admin only).
    
    Args:
        request: FastAPI request object
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        user: Admin user
        
    Returns:
        LiteLLMKeyListResponse: List of all keys and total count
        
    Raises:
        HTTPException: If user is not admin or other error occurs
    """
    try:
        # This would need to be implemented in LiteLLMKeys class
        # For now, return empty result
        return LiteLLMKeyListResponse(keys=[], total=0)
        
    except Exception as e:
        log.error(f"Error getting all LiteLLM keys (admin): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve all LiteLLM keys"
        )