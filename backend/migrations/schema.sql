-- ============================================================================
-- UNIFIED PERSONAL OPERATIONS HUB - DATABASE SCHEMA
-- ============================================================================
-- Multi-tenant PostgreSQL schema with Row-Level Security (RLS)
-- All tables include tenant_id for isolation
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================================
-- ENUM TYPES
-- ============================================================================

CREATE TYPE user_role AS ENUM ('owner', 'admin', 'member', 'viewer');
CREATE TYPE integration_status AS ENUM ('connected', 'disconnected', 'error', 'pending');
CREATE TYPE event_type AS ENUM (
  'INTEGRATION_SYNC_STARTED',
  'INTEGRATION_SYNC_COMPLETED',
  'INTEGRATION_SYNC_FAILED',
  'WEBHOOK_RECEIVED',
  'DASHBOARD_UPDATED',
  'WIDGET_ADDED',
  'WIDGET_REMOVED',
  'USER_INVITED',
  'TENANT_SETTINGS_CHANGED',
  'ALERT_TRIGGERED'
);
CREATE TYPE widget_type AS ENUM (
  'calendar',
  'jira_board',
  'datadog_metrics',
  'dynatrace_metrics',
  'whatsapp_messages',
  'custom'
);

-- ============================================================================
-- TENANTS TABLE
-- ============================================================================

CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  logo_url VARCHAR(512),
  
  -- Subscription & Billing
  subscription_tier VARCHAR(50) DEFAULT 'free',
  subscription_status VARCHAR(50) DEFAULT 'active',
  max_users INT DEFAULT 5,
  max_integrations INT DEFAULT 3,
  max_dashboards INT DEFAULT 3,
  
  -- Settings
  settings JSONB DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT valid_slug CHECK (slug ~ '^[a-z0-9-]+$')
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_subscription_status ON tenants(subscription_status);
CREATE INDEX idx_tenants_created_at ON tenants(created_at DESC);

-- ============================================================================
-- USERS TABLE
-- ============================================================================

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Auth
  email VARCHAR(255) NOT NULL,
  cognito_sub VARCHAR(255),
  
  -- Profile
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  avatar_url VARCHAR(512),
  
  -- Role & Permissions
  role user_role DEFAULT 'member',
  is_active BOOLEAN DEFAULT true,
  
  -- Settings
  preferences JSONB DEFAULT '{}',
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_login_at TIMESTAMP WITH TIME ZONE,
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT unique_email_per_tenant UNIQUE (tenant_id, email)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_cognito_sub ON users(cognito_sub);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================================
-- INTEGRATIONS TABLE
-- ============================================================================

CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Integration Details
  name VARCHAR(255) NOT NULL,
  connector_type VARCHAR(100) NOT NULL,
  status integration_status DEFAULT 'pending',
  
  -- Credentials (encrypted in application layer)
  credentials JSONB NOT NULL,
  
  -- Sync Configuration
  sync_interval_minutes INT DEFAULT 30,
  last_sync_at TIMESTAMP WITH TIME ZONE,
  next_sync_at TIMESTAMP WITH TIME ZONE,
  sync_error_message TEXT,
  
  -- Webhook Configuration
  webhook_url VARCHAR(512),
  webhook_secret VARCHAR(255),
  
  -- Settings
  settings JSONB DEFAULT '{}',
  
  -- Metadata
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT unique_connector_per_tenant UNIQUE (tenant_id, connector_type)
);

CREATE INDEX idx_integrations_tenant_id ON integrations(tenant_id);
CREATE INDEX idx_integrations_connector_type ON integrations(connector_type);
CREATE INDEX idx_integrations_status ON integrations(status);
CREATE INDEX idx_integrations_next_sync_at ON integrations(next_sync_at) WHERE status = 'connected';

-- ============================================================================
-- DASHBOARDS TABLE
-- ============================================================================

CREATE TABLE dashboards (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Dashboard Details
  name VARCHAR(255) NOT NULL,
  description TEXT,
  slug VARCHAR(255) NOT NULL,
  
  -- Layout & Display
  layout JSONB DEFAULT '{"columns": 12}',
  is_public BOOLEAN DEFAULT false,
  
  -- Settings
  settings JSONB DEFAULT '{}',
  
  -- Metadata
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT unique_dashboard_slug_per_tenant UNIQUE (tenant_id, slug)
);

CREATE INDEX idx_dashboards_tenant_id ON dashboards(tenant_id);
CREATE INDEX idx_dashboards_slug ON dashboards(slug);
CREATE INDEX idx_dashboards_is_public ON dashboards(is_public);
CREATE INDEX idx_dashboards_created_at ON dashboards(created_at DESC);

-- ============================================================================
-- WIDGETS TABLE
-- ============================================================================

CREATE TABLE widgets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  dashboard_id UUID NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
  
  -- Widget Details
  name VARCHAR(255) NOT NULL,
  widget_type widget_type NOT NULL,
  
  -- Integration Link
  integration_id UUID REFERENCES integrations(id) ON DELETE SET NULL,
  
  -- Layout & Display
  position_x INT DEFAULT 0,
  position_y INT DEFAULT 0,
  width INT DEFAULT 4,
  height INT DEFAULT 4,
  
  -- Configuration
  config JSONB DEFAULT '{}',
  
  -- Refresh Settings
  refresh_interval_seconds INT DEFAULT 300,
  last_refresh_at TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_widgets_tenant_id ON widgets(tenant_id);
CREATE INDEX idx_widgets_dashboard_id ON widgets(dashboard_id);
CREATE INDEX idx_widgets_integration_id ON widgets(integration_id);
CREATE INDEX idx_widgets_widget_type ON widgets(widget_type);

-- ============================================================================
-- EVENTS TABLE (Immutable audit log)
-- ============================================================================

CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Event Details
  event_type event_type NOT NULL,
  source VARCHAR(100) NOT NULL,
  
  -- User & Context
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Event Data
  data JSONB NOT NULL,
  
  -- Tracing
  trace_id UUID,
  request_id UUID,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT immutable_event CHECK (false)
);

CREATE INDEX idx_events_tenant_id ON events(tenant_id);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_created_at ON events(created_at DESC);
CREATE INDEX idx_events_trace_id ON events(trace_id);
CREATE INDEX idx_events_source ON events(source);

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Action Details
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100) NOT NULL,
  resource_id UUID,
  
  -- User & Context
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Changes
  changes JSONB,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  ip_address INET,
  user_agent TEXT
);

CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- ============================================================================
-- SESSIONS TABLE (for Redis backup)
-- ============================================================================

CREATE TABLE sessions (
  id VARCHAR(255) PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Session Data
  data JSONB NOT NULL,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_sessions_tenant_id ON sessions(tenant_id);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE widgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Set current tenant context (application must set this)
CREATE OR REPLACE FUNCTION current_tenant_id() RETURNS UUID AS $$
  SELECT COALESCE(
    current_setting('app.current_tenant_id', true)::UUID,
    NULL::UUID
  );
$$ LANGUAGE SQL STABLE;

-- Users RLS Policy
CREATE POLICY users_tenant_isolation ON users
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Integrations RLS Policy
CREATE POLICY integrations_tenant_isolation ON integrations
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Dashboards RLS Policy
CREATE POLICY dashboards_tenant_isolation ON dashboards
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Widgets RLS Policy
CREATE POLICY widgets_tenant_isolation ON widgets
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Events RLS Policy
CREATE POLICY events_tenant_isolation ON events
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Audit Logs RLS Policy
CREATE POLICY audit_logs_tenant_isolation ON audit_logs
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- Sessions RLS Policy
CREATE POLICY sessions_tenant_isolation ON sessions
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tenants_updated_at BEFORE UPDATE ON tenants
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER integrations_updated_at BEFORE UPDATE ON integrations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER dashboards_updated_at BEFORE UPDATE ON dashboards
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER widgets_updated_at BEFORE UPDATE ON widgets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

-- Test RLS (set tenant context first)
-- SET app.current_tenant_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
-- SELECT * FROM users;

-- Get user's dashboards with widget count
-- SELECT d.id, d.name, COUNT(w.id) as widget_count
-- FROM dashboards d
-- LEFT JOIN widgets w ON d.id = w.dashboard_id
-- WHERE d.deleted_at IS NULL
-- GROUP BY d.id, d.name;

-- Get integration sync status
-- SELECT connector_type, status, last_sync_at, next_sync_at, sync_error_message
-- FROM integrations
-- WHERE deleted_at IS NULL
-- ORDER BY next_sync_at ASC;

-- Get recent events
-- SELECT event_type, source, data, created_at
-- FROM events
-- WHERE deleted_at IS NULL
-- ORDER BY created_at DESC
-- LIMIT 50;
