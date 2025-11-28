"""
User Models for Trivya Backend

This module defines the Pydantic models for User management and Authentication.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base User model with shared attributes."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    
    class Config:
        orm_mode = True


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        """Basic password length validation."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    """Model for updating user data."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    
    class Config:
        orm_mode = True


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Role-based access control
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


class User(UserBase):
    """User model returned to API clients (no password)."""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    roles: List[str] = []


class Token(BaseModel):
    """Token model for authentication response."""
    access_token: str
    token_type: str
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """JWT Token payload."""
    user_id: str
    roles: List[str] = []
    exp: Optional[int] = None
