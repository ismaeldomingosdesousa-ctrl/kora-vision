"""Base models for SQLAlchemy ORM."""

from sqlalchemy import Column, DateTime, func, UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields."""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class TenantModel(BaseModel):
    """Base model for tenant-scoped tables."""

    __abstract__ = True

    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
