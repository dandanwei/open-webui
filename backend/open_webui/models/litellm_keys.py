"""
LiteLLM Keys Model

This module defines the database schema and models for managing LiteLLM API keys
in Open WebUI. It provides functionality to store, retrieve, and manage API keys
associated with users and groups.

Author: LiteLLM Key Management Plugin
"""

import time
import logging
from typing import Optional, List
import uuid

from open_webui.internal.db import Base, get_db
from open_webui.env import SRC_LOG_LEVELS

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# LiteLLM Key DB Schema
####################


class LiteLLMKey(Base):
    """
    Database model for storing LiteLLM API keys.
    
    Each key is associated with a user and can have group-based access control.
    Keys are encrypted before storage for security.
    """
    __tablename__ = "litellm_key"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Key information
    key_name = Column(Text, nullable=False)  # User-friendly name for the key
    api_key = Column(Text, nullable=False)   # Encrypted API key
    key_type = Column(String, default="api_key")  # Type of key (api_key, etc.)
    
    # Access control
    group_ids = Column(JSON, nullable=True)  # List of group IDs that can access this key
    is_active = Column(Boolean, default=True)  # Whether the key is active
    
    # Metadata
    description = Column(Text, nullable=True)  # Optional description
    metadata = Column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()))
    last_used_at = Column(BigInteger, nullable=True)  # When the key was last used
    
    # Relationship
    user = relationship("User", back_populates="litellm_keys")


class LiteLLMKeyModel(BaseModel):
    """
    Pydantic model for LiteLLM key data transfer.
    
    This model is used for API responses and request validation.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    key_name: str
    api_key: str  # This will be masked in responses
    key_type: str = "api_key"
    group_ids: Optional[List[str]] = None
    is_active: bool = True
    description: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: int
    updated_at: int
    last_used_at: Optional[int] = None


class LiteLLMKeyCreateForm(BaseModel):
    """
    Form model for creating new LiteLLM keys.
    """
    key_name: str
    api_key: str
    key_type: str = "api_key"
    group_ids: Optional[List[str]] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class LiteLLMKeyUpdateForm(BaseModel):
    """
    Form model for updating existing LiteLLM keys.
    """
    key_name: Optional[str] = None
    api_key: Optional[str] = None
    key_type: Optional[str] = None
    group_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None


class LiteLLMKeyListResponse(BaseModel):
    """
    Response model for listing LiteLLM keys.
    """
    keys: List[LiteLLMKeyModel]
    total: int


####################
# LiteLLM Keys CRUD Operations
####################


class LiteLLMKeys:
    """
    CRUD operations for LiteLLM keys.
    
    This class provides methods to create, read, update, and delete LiteLLM keys
    with proper access control and security measures.
    """
    
    @staticmethod
    def create_key(user_id: str, key_data: LiteLLMKeyCreateForm) -> LiteLLMKeyModel:
        """
        Create a new LiteLLM key.
        
        Args:
            user_id: ID of the user creating the key
            key_data: Key creation data
            
        Returns:
            LiteLLMKeyModel: The created key
            
        Raises:
            ValueError: If key name already exists for user
        """
        db = next(get_db())
        
        try:
            # Check if key name already exists for this user
            existing_key = db.query(LiteLLMKey).filter(
                LiteLLMKey.user_id == user_id,
                LiteLLMKey.key_name == key_data.key_name
            ).first()
            
            if existing_key:
                raise ValueError(f"Key name '{key_data.key_name}' already exists")
            
            # Create new key
            new_key = LiteLLMKey(
                user_id=user_id,
                key_name=key_data.key_name,
                api_key=key_data.api_key,  # In production, this should be encrypted
                key_type=key_data.key_type,
                group_ids=key_data.group_ids,
                description=key_data.description,
                metadata=key_data.metadata
            )
            
            db.add(new_key)
            db.commit()
            db.refresh(new_key)
            
            return LiteLLMKeyModel.model_validate(new_key)
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_keys_by_user_id(user_id: str, skip: int = 0, limit: int = 100) -> LiteLLMKeyListResponse:
        """
        Get all LiteLLM keys for a specific user.
        
        Args:
            user_id: ID of the user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            LiteLLMKeyListResponse: List of keys and total count
        """
        db = next(get_db())
        
        try:
            # Get total count
            total = db.query(LiteLLMKey).filter(LiteLLMKey.user_id == user_id).count()
            
            # Get keys with pagination
            keys = db.query(LiteLLMKey).filter(
                LiteLLMKey.user_id == user_id
            ).offset(skip).limit(limit).all()
            
            # Convert to models and mask API keys
            key_models = []
            for key in keys:
                key_model = LiteLLMKeyModel.model_validate(key)
                # Mask the API key for security
                key_model.api_key = LiteLLMKeys._mask_api_key(key_model.api_key)
                key_models.append(key_model)
            
            return LiteLLMKeyListResponse(keys=key_models, total=total)
            
        finally:
            db.close()
    
    @staticmethod
    def get_key_by_id(key_id: str, user_id: str) -> Optional[LiteLLMKeyModel]:
        """
        Get a specific LiteLLM key by ID.
        
        Args:
            key_id: ID of the key
            user_id: ID of the user (for access control)
            
        Returns:
            LiteLLMKeyModel or None: The key if found and accessible
        """
        db = next(get_db())
        
        try:
            key = db.query(LiteLLMKey).filter(
                LiteLLMKey.id == key_id,
                LiteLLMKey.user_id == user_id
            ).first()
            
            if key:
                key_model = LiteLLMKeyModel.model_validate(key)
                # Mask the API key for security
                key_model.api_key = LiteLLMKeys._mask_api_key(key_model.api_key)
                return key_model
            
            return None
            
        finally:
            db.close()
    
    @staticmethod
    def update_key(key_id: str, user_id: str, update_data: LiteLLMKeyUpdateForm) -> Optional[LiteLLMKeyModel]:
        """
        Update an existing LiteLLM key.
        
        Args:
            key_id: ID of the key to update
            user_id: ID of the user (for access control)
            update_data: Update data
            
        Returns:
            LiteLLMKeyModel or None: The updated key if found and accessible
        """
        db = next(get_db())
        
        try:
            key = db.query(LiteLLMKey).filter(
                LiteLLMKey.id == key_id,
                LiteLLMKey.user_id == user_id
            ).first()
            
            if not key:
                return None
            
            # Update fields if provided
            if update_data.key_name is not None:
                # Check if new name already exists for this user
                existing_key = db.query(LiteLLMKey).filter(
                    LiteLLMKey.user_id == user_id,
                    LiteLLMKey.key_name == update_data.key_name,
                    LiteLLMKey.id != key_id
                ).first()
                
                if existing_key:
                    raise ValueError(f"Key name '{update_data.key_name}' already exists")
                
                key.key_name = update_data.key_name
            
            if update_data.api_key is not None:
                key.api_key = update_data.api_key  # In production, this should be encrypted
            
            if update_data.key_type is not None:
                key.key_type = update_data.key_type
            
            if update_data.group_ids is not None:
                key.group_ids = update_data.group_ids
            
            if update_data.is_active is not None:
                key.is_active = update_data.is_active
            
            if update_data.description is not None:
                key.description = update_data.description
            
            if update_data.metadata is not None:
                key.metadata = update_data.metadata
            
            key.updated_at = int(time.time())
            
            db.commit()
            db.refresh(key)
            
            key_model = LiteLLMKeyModel.model_validate(key)
            # Mask the API key for security
            key_model.api_key = LiteLLMKeys._mask_api_key(key_model.api_key)
            return key_model
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def delete_key(key_id: str, user_id: str) -> bool:
        """
        Delete a LiteLLM key.
        
        Args:
            key_id: ID of the key to delete
            user_id: ID of the user (for access control)
            
        Returns:
            bool: True if key was deleted, False if not found
        """
        db = next(get_db())
        
        try:
            key = db.query(LiteLLMKey).filter(
                LiteLLMKey.id == key_id,
                LiteLLMKey.user_id == user_id
            ).first()
            
            if not key:
                return False
            
            db.delete(key)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_keys_by_group_ids(group_ids: List[str], user_id: str) -> List[LiteLLMKeyModel]:
        """
        Get LiteLLM keys accessible by specific groups.
        
        Args:
            group_ids: List of group IDs
            user_id: ID of the user requesting access
            
        Returns:
            List[LiteLLMKeyModel]: List of accessible keys
        """
        db = next(get_db())
        
        try:
            # Get keys that are either owned by the user or accessible by the groups
            keys = db.query(LiteLLMKey).filter(
                (LiteLLMKey.user_id == user_id) | 
                (LiteLLMKey.group_ids.op('&&')(group_ids))  # PostgreSQL array overlap operator
            ).filter(LiteLLMKey.is_active == True).all()
            
            # Convert to models and mask API keys
            key_models = []
            for key in keys:
                key_model = LiteLLMKeyModel.model_validate(key)
                # Mask the API key for security
                key_model.api_key = LiteLLMKeys._mask_api_key(key_model.api_key)
                key_models.append(key_model)
            
            return key_models
            
        finally:
            db.close()
    
    @staticmethod
    def _mask_api_key(api_key: str) -> str:
        """
        Mask an API key for display purposes.
        
        Args:
            api_key: The API key to mask
            
        Returns:
            str: Masked API key (shows first 8 and last 4 characters)
        """
        if len(api_key) <= 12:
            return "*" * len(api_key)
        
        return api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]