"""Database models for Kora Vision."""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Integration(Base):
    """Integration configuration model."""
    __tablename__ = "integrations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "Jira - Production"
    type = Column(String, nullable=False)  # jira, google_chat, gmail, google_calendar, datadog, dynatrace
    credentials = Column(JSON, nullable=False)  # Encrypted credentials
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Type-specific fields
    jira_space_key = Column(String)  # For Jira integrations
    google_chat_space_id = Column(String)  # For Google Chat integrations
    datadog_site = Column(String)  # For Datadog (us3, eu, etc)
    dynatrace_environment = Column(String)  # For Dynatrace


class DashboardWidget(Base):
    """Dashboard widget configuration."""
    __tablename__ = "dashboard_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_id = Column(String, nullable=False)
    widget_type = Column(String, nullable=False)  # jira_issues, google_chat_activity, gmail_unread, etc
    position = Column(Integer)  # Order on dashboard
    is_visible = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=300)  # Seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CachedData(Base):
    """Cache for integration data."""
    __tablename__ = "cached_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_id = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # jira_issues, gmail_unread, etc
    data = Column(JSON)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
