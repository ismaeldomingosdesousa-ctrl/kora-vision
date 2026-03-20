"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2026-03-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "btree_gin"')
    
    # Create ENUM types
    user_role_enum = postgresql.ENUM('owner', 'admin', 'member', 'viewer', name='user_role')
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    integration_status_enum = postgresql.ENUM(
        'connected', 'disconnected', 'error', 'pending',
        name='integration_status'
    )
    integration_status_enum.create(op.get_bind(), checkfirst=True)
    
    event_type_enum = postgresql.ENUM(
        'INTEGRATION_SYNC_STARTED',
        'INTEGRATION_SYNC_COMPLETED',
        'INTEGRATION_SYNC_FAILED',
        'WEBHOOK_RECEIVED',
        'DASHBOARD_UPDATED',
        'WIDGET_ADDED',
        'WIDGET_REMOVED',
        'USER_INVITED',
        'TENANT_SETTINGS_CHANGED',
        'ALERT_TRIGGERED',
        name='event_type'
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)
    
    widget_type_enum = postgresql.ENUM(
        'calendar',
        'jira_board',
        'datadog_metrics',
        'dynatrace_metrics',
        'whatsapp_messages',
        'custom',
        name='widget_type'
    )
    widget_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(512), nullable=True),
        sa.Column('subscription_tier', sa.String(50), nullable=False, server_default='free'),
        sa.Column('subscription_status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('max_users', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('max_integrations', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('max_dashboards', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("slug ~ '^[a-z0-9-]+$'", name='valid_slug')
    )
    op.create_index('idx_tenants_slug', 'tenants', ['slug'])
    op.create_index('idx_tenants_subscription_status', 'tenants', ['subscription_status'])
    op.create_index('idx_tenants_created_at', 'tenants', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('cognito_sub', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=True),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('role', user_role_enum, nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'email', name='unique_email_per_tenant')
    )
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_cognito_sub', 'users', ['cognito_sub'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    
    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('connector_type', sa.String(100), nullable=False),
        sa.Column('status', integration_status_enum, nullable=False, server_default='pending'),
        sa.Column('credentials', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('sync_interval_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_error_message', sa.Text(), nullable=True),
        sa.Column('webhook_url', sa.String(512), nullable=True),
        sa.Column('webhook_secret', sa.String(255), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'connector_type', name='unique_connector_per_tenant')
    )
    op.create_index('idx_integrations_tenant_id', 'integrations', ['tenant_id'])
    op.create_index('idx_integrations_connector_type', 'integrations', ['connector_type'])
    op.create_index('idx_integrations_status', 'integrations', ['status'])
    op.create_index('idx_integrations_next_sync_at', 'integrations', ['next_sync_at'], 
                   postgresql_where=sa.text("status = 'connected'"))
    
    # Create dashboards table
    op.create_table(
        'dashboards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('layout', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{"columns": 12}'),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'slug', name='unique_dashboard_slug_per_tenant')
    )
    op.create_index('idx_dashboards_tenant_id', 'dashboards', ['tenant_id'])
    op.create_index('idx_dashboards_slug', 'dashboards', ['slug'])
    op.create_index('idx_dashboards_is_public', 'dashboards', ['is_public'])
    op.create_index('idx_dashboards_created_at', 'dashboards', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Create widgets table
    op.create_table(
        'widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dashboard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('widget_type', widget_type_enum, nullable=False),
        sa.Column('integration_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('position_y', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('height', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('refresh_interval_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('last_refresh_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_widgets_tenant_id', 'widgets', ['tenant_id'])
    op.create_index('idx_widgets_dashboard_id', 'widgets', ['dashboard_id'])
    op.create_index('idx_widgets_integration_id', 'widgets', ['integration_id'])
    op.create_index('idx_widgets_widget_type', 'widgets', ['widget_type'])
    
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', event_type_enum, nullable=False),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('trace_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_events_tenant_id', 'events', ['tenant_id'])
    op.create_index('idx_events_event_type', 'events', ['event_type'])
    op.create_index('idx_events_user_id', 'events', ['user_id'])
    op.create_index('idx_events_created_at', 'events', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_events_trace_id', 'events', ['trace_id'])
    op.create_index('idx_events_source', 'events', ['source'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('ip_address', sa.types.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_tenant_id', 'sessions', ['tenant_id'])
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])
    
    # Enable RLS on all tables
    op.execute('ALTER TABLE users ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE integrations ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE dashboards ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE widgets ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE events ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE sessions ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies
    op.execute("""
        CREATE OR REPLACE FUNCTION current_tenant_id() RETURNS UUID AS $$
          SELECT COALESCE(
            current_setting('app.current_tenant_id', true)::UUID,
            NULL::UUID
          );
        $$ LANGUAGE SQL STABLE;
    """)
    
    op.execute("""
        CREATE POLICY users_tenant_isolation ON users
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY integrations_tenant_isolation ON integrations
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY dashboards_tenant_isolation ON dashboards
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY widgets_tenant_isolation ON widgets
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY events_tenant_isolation ON events
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY audit_logs_tenant_isolation ON audit_logs
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    op.execute("""
        CREATE POLICY sessions_tenant_isolation ON sessions
          USING (tenant_id = current_tenant_id())
          WITH CHECK (tenant_id = current_tenant_id());
    """)
    
    # Create triggers for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = CURRENT_TIMESTAMP;
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute('CREATE TRIGGER tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()')
    op.execute('CREATE TRIGGER users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()')
    op.execute('CREATE TRIGGER integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()')
    op.execute('CREATE TRIGGER dashboards_updated_at BEFORE UPDATE ON dashboards FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()')
    op.execute('CREATE TRIGGER widgets_updated_at BEFORE UPDATE ON widgets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()')


def downgrade() -> None:
    """Drop all tables and types."""
    
    # Drop tables (in reverse order of creation)
    op.drop_table('sessions')
    op.drop_table('audit_logs')
    op.drop_table('events')
    op.drop_table('widgets')
    op.drop_table('dashboards')
    op.drop_table('integrations')
    op.drop_table('users')
    op.drop_table('tenants')
    
    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS widget_type')
    op.execute('DROP TYPE IF EXISTS event_type')
    op.execute('DROP TYPE IF EXISTS integration_status')
    op.execute('DROP TYPE IF EXISTS user_role')
