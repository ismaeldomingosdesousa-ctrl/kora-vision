"""Pydantic schemas for tenant-related requests/responses."""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class TenantBase(BaseModel):
    """Base tenant schema."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255, regex=r"^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = Field(None, max_length=512)


class TenantCreate(TenantBase):
    """Schema for creating a tenant."""

    pass


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    logo_url: Optional[str] = Field(None, max_length=512)
    settings: Optional[Dict[str, Any]] = None


class TenantResponse(TenantBase):
    """Schema for tenant response."""

    id: UUID
    subscription_tier: str
    subscription_status: str
    max_users: int
    max_integrations: int
    max_dashboards: int
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """Schema for listing tenants."""

    total: int
    items: list[TenantResponse]
