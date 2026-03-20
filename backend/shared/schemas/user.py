"""Pydantic schemas for user-related requests/responses."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    """User roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)


class UserCreate(UserBase):
    """Schema for creating a user."""

    role: UserRole = UserRole.MEMBER


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    role: Optional[UserRole] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: UUID
    tenant_id: UUID
    role: UserRole
    is_active: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for listing users."""

    total: int
    items: list[UserResponse]


class CurrentUser(BaseModel):
    """Schema for current authenticated user."""

    id: UUID
    tenant_id: UUID
    email: str
    role: UserRole
    is_active: bool
