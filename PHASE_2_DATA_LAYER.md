# PHASE 2 — Data Layer

## Overview

This phase provisions and configures the **data layer** for the Unified Personal Operations Hub, including:

1. **Aurora PostgreSQL Serverless v2** database provisioning
2. **Database schema** with multi-tenant Row-Level Security (RLS)
3. **Migration strategy** using Alembic
4. **Tenant isolation model** implementation
5. **Backup and disaster recovery** configuration

---

## Architecture Decisions

### 1. Database Choice: Aurora PostgreSQL Serverless v2
**Choice:** Managed PostgreSQL with serverless auto-scaling
**Rationale:**
- Automatic scaling based on workload
- Multi-AZ for high availability
- Automated backups and point-in-time recovery
- Native JSON support (JSONB)
- Row-Level Security (RLS) for multi-tenant isolation
- Encryption at rest with KMS

**Alternatives Rejected:**
- DynamoDB: Not suitable for relational multi-tenant data
- RDS Aurora Provisioned: Requires manual capacity management

### 2. Multi-Tenant Isolation: Row-Level Security (RLS)
**Choice:** PostgreSQL RLS policies at database layer
**Rationale:**
- Strong isolation guarantee
- No application-level filtering needed
- Efficient resource sharing (single database)
- Simplified backup/restore per tenant
- Cost-effective for thousands of tenants

**How It Works:**
- Every table has `tenant_id` column
- PostgreSQL RLS policies enforce `tenant_id` filtering
- Application sets `app.current_tenant_id` context variable
- All queries automatically filtered by tenant

**Example:**
```sql
-- Set tenant context (application does this)
SET app.current_tenant_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';

-- Query automatically filtered
SELECT * FROM users;  -- Only returns users for this tenant
```

### 3. Migration Strategy: Alembic
**Choice:** Alembic for database migrations
**Rationale:**
- Version control for schema changes
- Reversible migrations (up/down)
- Multi-environment support (dev, staging, prod)
- Automatic migration detection
- Integration with SQLAlchemy

**Migration Workflow:**
```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### 4. Backup Strategy
**Choice:** Automated backups with point-in-time recovery
**Rationale:**
- 30-day retention for dev/staging
- 35-day retention for production
- Daily snapshots
- Cross-region replication (prod)
- Encryption with KMS

---

## Database Schema Overview

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| **tenants** | Tenant accounts | id, name, slug, subscription_tier |
| **users** | User accounts | id, tenant_id, email, role, is_active |
| **integrations** | External service connections | id, tenant_id, connector_type, status |
| **dashboards** | User dashboards | id, tenant_id, name, slug, is_public |
| **widgets** | Dashboard widgets | id, tenant_id, dashboard_id, widget_type |
| **events** | Event audit trail | id, tenant_id, event_type, source, data |
| **audit_logs** | User action logs | id, tenant_id, action, resource_type |
| **sessions** | User sessions | id, tenant_id, user_id, expires_at |

### Schema Characteristics

✅ **Multi-tenant:** All tables include `tenant_id`  
✅ **Soft deletes:** `deleted_at` column for data retention  
✅ **Timestamps:** `created_at`, `updated_at` with triggers  
✅ **JSONB support:** Flexible configuration storage  
✅ **Indexing:** Strategic indexes for query performance  
✅ **RLS policies:** Automatic tenant isolation  

---

## File Structure

```
backend/
├── migrations/
│   ├── alembic.ini                      # Alembic configuration
│   ├── env.py                           # Alembic environment setup
│   ├── script.py.mako                   # Migration template
│   ├── schema.sql                       # Full schema (reference)
│   └── versions/
│       └── 001_initial_schema.py        # Initial migration
├── models/
│   ├── __init__.py
│   ├── base.py                          # SQLAlchemy Base
│   ├── tenant.py                        # Tenant model
│   ├── user.py                          # User model
│   ├── integration.py                   # Integration model
│   ├── dashboard.py                     # Dashboard model
│   ├── widget.py                        # Widget model
│   ├── event.py                         # Event model
│   └── audit_log.py                     # Audit log model
└── requirements.txt
```

---

## Setup Instructions

### Step 1: Prerequisites

Ensure Phase 1 (Infrastructure) is complete:
- ✅ RDS Aurora cluster provisioned
- ✅ Secrets Manager configured with DB password
- ✅ Security groups allow database access

### Step 2: Connect to Database

```bash
# Get RDS endpoint from Terraform output
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Get database password from Secrets Manager
DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id unified-ops-hub/db-password-dev \
  --query SecretString --output text)

# Connect to database
psql -h $RDS_ENDPOINT -U admin -d unifiedopshub
```

### Step 3: Initialize Alembic

```bash
cd backend/migrations

# Initialize Alembic (already done, but for reference)
# alembic init .

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://admin:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/unifiedopshub"

# Verify connection
alembic current
```

### Step 4: Run Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Verify migration status
alembic current

# View migration history
alembic history
```

### Step 5: Verify Schema

```bash
# Connect to database
psql -h $RDS_ENDPOINT -U admin -d unifiedopshub

# List tables
\dt

# List RLS policies
SELECT schemaname, tablename, policyname FROM pg_policies;

# Test RLS (set tenant context)
SET app.current_tenant_id = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';
SELECT * FROM users;
```

---

## Multi-Tenant Isolation Testing

### Test 1: Verify RLS Policies

```sql
-- Create test tenants
INSERT INTO tenants (name, slug) VALUES ('Tenant A', 'tenant-a');
INSERT INTO tenants (name, slug) VALUES ('Tenant B', 'tenant-b');

-- Create test users
INSERT INTO users (tenant_id, email, role) 
VALUES 
  ((SELECT id FROM tenants WHERE slug = 'tenant-a'), 'user-a@example.com', 'owner'),
  ((SELECT id FROM tenants WHERE slug = 'tenant-b'), 'user-b@example.com', 'owner');

-- Set context to Tenant A
SET app.current_tenant_id = (SELECT id FROM tenants WHERE slug = 'tenant-a');

-- Query should only return Tenant A's users
SELECT email FROM users;  -- Returns: user-a@example.com

-- Switch context to Tenant B
SET app.current_tenant_id = (SELECT id FROM tenants WHERE slug = 'tenant-b');

-- Query should only return Tenant B's users
SELECT email FROM users;  -- Returns: user-b@example.com
```

### Test 2: Verify Isolation Enforcement

```sql
-- Try to insert user for different tenant (should fail)
SET app.current_tenant_id = (SELECT id FROM tenants WHERE slug = 'tenant-a');

INSERT INTO users (tenant_id, email, role) 
VALUES 
  ((SELECT id FROM tenants WHERE slug = 'tenant-b'), 'hacker@example.com', 'owner');
-- Error: new row violates row-level security policy
```

---

## Backup & Recovery

### Automated Backups (Terraform-configured)

- **Retention:** 30 days (dev/staging), 35 days (prod)
- **Backup window:** 03:00-04:00 UTC
- **Maintenance window:** Mon 04:00-05:00 UTC
- **Encryption:** KMS-encrypted

### Manual Backup

```bash
# Create manual snapshot
aws rds create-db-cluster-snapshot \
  --db-cluster-identifier unified-ops-hub-cluster-dev \
  --db-cluster-snapshot-identifier unified-ops-hub-backup-$(date +%Y%m%d-%H%M%S)

# List snapshots
aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier unified-ops-hub-cluster-dev
```

### Point-in-Time Recovery

```bash
# Restore to specific point in time
aws rds restore-db-cluster-to-point-in-time \
  --db-cluster-identifier unified-ops-hub-cluster-dev-restore \
  --source-db-cluster-identifier unified-ops-hub-cluster-dev \
  --restore-type copy-on-write \
  --restore-to-time 2026-03-20T10:30:00Z
```

---

## Performance Optimization

### Indexes

Strategic indexes created for common queries:

```sql
-- Tenant-based queries
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_dashboards_tenant_id ON dashboards(tenant_id);

-- Filtering and sorting
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_dashboards_created_at ON dashboards(created_at DESC);

-- Integration sync scheduling
CREATE INDEX idx_integrations_next_sync_at ON integrations(next_sync_at) 
  WHERE status = 'connected';

-- Event queries
CREATE INDEX idx_events_created_at ON events(created_at DESC);
```

### Query Examples

```sql
-- Get user's dashboards with widget count
SELECT d.id, d.name, COUNT(w.id) as widget_count
FROM dashboards d
LEFT JOIN widgets w ON d.id = w.dashboard_id
WHERE d.deleted_at IS NULL
GROUP BY d.id, d.name;

-- Get integration sync status
SELECT connector_type, status, last_sync_at, next_sync_at
FROM integrations
WHERE deleted_at IS NULL AND status = 'connected'
ORDER BY next_sync_at ASC;

-- Get recent events
SELECT event_type, source, data, created_at
FROM events
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 50;
```

---

## Monitoring & Alerts

### CloudWatch Metrics

Configured in Phase 1:

- **CPU Utilization:** Alert if > 80%
- **Database Connections:** Alert if > 100
- **Storage:** Alert if > 90% full
- **Query Performance:** Monitor slow queries

### Enable Query Logging

```sql
-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Reload configuration
SELECT pg_reload_conf();

-- View slow queries
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

---

## Disaster Recovery Plan

### Recovery Time Objective (RTO): 1 hour
### Recovery Point Objective (RPO): 5 minutes

**Procedure:**

1. **Detect failure** → CloudWatch alarm triggers
2. **Assess damage** → Check RDS cluster status
3. **Initiate recovery** → Restore from snapshot or point-in-time
4. **Verify data** → Run integrity checks
5. **Update DNS** → Point to new endpoint
6. **Notify users** → Status page update

---

## Validation Checklist

After Phase 2 deployment:

- [ ] **Database Created**
  ```bash
  aws rds describe-db-clusters --db-cluster-identifier unified-ops-hub-cluster-dev
  ```

- [ ] **Schema Initialized**
  ```bash
  alembic current
  ```

- [ ] **RLS Policies Active**
  ```sql
  SELECT schemaname, tablename, policyname FROM pg_policies;
  ```

- [ ] **Backups Configured**
  ```bash
  aws rds describe-db-clusters --query 'DBClusters[0].BackupRetentionPeriod'
  ```

- [ ] **CloudWatch Alarms Active**
  ```bash
  aws cloudwatch describe-alarms --alarm-name-prefix unified-ops-hub-rds
  ```

- [ ] **Test RLS Isolation** (see testing section above)

- [ ] **Verify Encryption**
  ```bash
  aws rds describe-db-clusters --query 'DBClusters[0].StorageEncrypted'
  ```

---

## Troubleshooting

### Issue: Migration Fails

```bash
# Check migration status
alembic current

# View migration history
alembic history

# Rollback last migration
alembic downgrade -1

# Re-run migration with verbose output
alembic upgrade head -v
```

### Issue: RLS Policy Not Working

```sql
-- Verify RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'users';

-- Check if policy exists
SELECT * FROM pg_policies WHERE tablename = 'users';

-- Re-create policy
DROP POLICY IF EXISTS users_tenant_isolation ON users;
CREATE POLICY users_tenant_isolation ON users
  USING (tenant_id = current_tenant_id())
  WITH CHECK (tenant_id = current_tenant_id());
```

### Issue: Slow Queries

```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC;

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

---

## Next Steps

**Phase 2 Complete.** Awaiting approval to proceed to **Phase 3 — Backend Core**.

Please confirm:
1. ✅ Database schema created successfully?
2. ✅ RLS policies verified and working?
3. ✅ Migrations applied without errors?
4. ✅ Backups configured and tested?
5. ✅ Ready to proceed with FastAPI backend services?

**Reply "APPROVED" or provide feedback for adjustments.**
