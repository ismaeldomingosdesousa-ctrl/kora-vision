# PHASE 1 — Infrastructure Foundation (Terraform)

## Overview

This phase provisions the complete AWS infrastructure for the **Unified Personal Operations Hub** using Terraform. All resources are organized into reusable modules for maintainability and scalability.

---

## Architecture Decisions

### 1. Infrastructure as Code (IaC)
**Choice:** Terraform with modular structure
**Rationale:** Version control, reproducibility, team collaboration, multi-environment support
**Modules:** VPC, Security Groups, ALB, ECS, RDS, ElastiCache, S3, CloudFront, Route53, Secrets, CloudWatch

### 2. Networking
**Choice:** Multi-AZ VPC with public/private subnets
**Rationale:** High availability, security isolation, NAT Gateway for private subnet egress
**Configuration:**
- VPC CIDR: `10.0.0.0/16`
- 3 Availability Zones
- Public subnets: `10.0.1.0/24`, `10.0.2.0/24`, `10.0.3.0/24`
- Private subnets: `10.0.11.0/24`, `10.0.12.0/24`, `10.0.13.0/24`
- NAT Gateway per AZ for redundancy

### 3. Load Balancing
**Choice:** Application Load Balancer (ALB)
**Rationale:** Layer 7 routing, path-based routing, HTTPS termination
**Configuration:**
- HTTP → HTTPS redirect
- Target group on port 8000
- Health checks every 30s
- CloudWatch alarms for unhealthy hosts

### 4. Container Orchestration
**Choice:** ECS Fargate (serverless containers)
**Rationale:** No infrastructure management, auto-scaling, cost-effective
**Configuration:**
- Capacity providers: FARGATE + FARGATE_SPOT
- Auto-scaling: CPU 70%, Memory 80%
- CloudWatch Container Insights enabled

### 5. Database
**Choice:** Aurora PostgreSQL Serverless v2
**Rationale:** Managed, auto-scaling, multi-AZ, encryption at rest
**Configuration:**
- Engine: PostgreSQL 15.3
- Serverless v2 (auto-scaling compute)
- Multi-AZ deployment (prod)
- Automated backups (30-day retention)
- Encryption with KMS

### 6. Cache Layer
**Choice:** ElastiCache Redis with Multi-AZ
**Rationale:** Session store, cache, real-time subscriptions, high performance
**Configuration:**
- Redis 7.0
- 3 nodes (Multi-AZ + automatic failover)
- Encryption in transit + at rest
- Auth token via Secrets Manager

### 7. Frontend Hosting
**Choice:** S3 + CloudFront CDN
**Rationale:** Global distribution, low latency, cost-effective
**Configuration:**
- S3 bucket with versioning + encryption
- CloudFront with OAI (Origin Access Identity)
- Custom error responses (404/403 → index.html for SPA)
- Logging bucket for access logs

### 8. Secrets Management
**Choice:** AWS Secrets Manager
**Rationale:** Secure credential storage, rotation support, audit logging
**Secrets:**
- Database password
- JWT secret
- Cognito credentials
- API keys

---

## Terraform Structure

```
infrastructure/terraform/
├── main.tf                          # Root module (orchestrates all modules)
├── variables.tf                     # Input variables
├── outputs.tf                       # Output values
├── terraform.tfvars.example         # Example values
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── security_groups/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── alb/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── elasticache/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── s3/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloudfront/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── route53/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── secrets/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── cloudwatch/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── dev.tfvars
    ├── staging.tfvars
    └── prod.tfvars
```

---

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.5 installed
3. **AWS CLI** configured with credentials
4. **Domain name** registered (for Route53)
5. **ACM Certificate** for HTTPS (optional, can use CloudFront default)

---

## Setup Instructions

### Step 1: Initialize Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform (download providers, set up backend)
terraform init
```

### Step 2: Configure Variables

Copy the example file and customize:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
# AWS Configuration
aws_region = "us-east-1"
environment = "dev"

# Domain Configuration
domain_name = "yourdomain.com"
acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/xxx"

# Database Configuration
db_password = "YourSecurePassword123!"

# Secrets
jwt_secret = "your-jwt-secret"
cognito_client_id = "your-cognito-id"
cognito_client_secret = "your-cognito-secret"
```

### Step 3: Validate Configuration

```bash
# Validate Terraform syntax
terraform validate

# Format Terraform files
terraform fmt -recursive
```

### Step 4: Plan Deployment

```bash
# Generate execution plan
terraform plan -out=tfplan

# Review the plan carefully before applying
```

### Step 5: Apply Infrastructure

```bash
# Apply the plan
terraform apply tfplan

# Terraform will provision all resources
# This typically takes 15-20 minutes
```

### Step 6: Retrieve Outputs

```bash
# Display all outputs
terraform output

# Get specific output
terraform output alb_dns_name
terraform output rds_endpoint
terraform output elasticache_endpoint
```

---

## Validation Checklist

After deployment, verify:

- [ ] **VPC Created**
  ```bash
  aws ec2 describe-vpcs --filters Name=tag:Name,Values=unified-ops-hub-vpc-dev
  ```

- [ ] **Subnets Created** (3 public + 3 private)
  ```bash
  aws ec2 describe-subnets --filters Name=vpc-id,Values=<vpc-id>
  ```

- [ ] **NAT Gateways Active**
  ```bash
  aws ec2 describe-nat-gateways --filters Name=state,Values=available
  ```

- [ ] **Security Groups Created**
  ```bash
  aws ec2 describe-security-groups --filters Name=group-name,Values=unified-ops-hub-*
  ```

- [ ] **ALB Active**
  ```bash
  aws elbv2 describe-load-balancers --names unified-ops-hub-alb-dev
  ```

- [ ] **ECS Cluster Created**
  ```bash
  aws ecs describe-clusters --clusters unified-ops-hub-cluster-dev
  ```

- [ ] **RDS Cluster Available**
  ```bash
  aws rds describe-db-clusters --db-cluster-identifier unified-ops-hub-cluster-dev
  ```

- [ ] **ElastiCache Cluster Available**
  ```bash
  aws elasticache describe-replication-groups --replication-group-id unified-ops-hub-redis-dev
  ```

- [ ] **S3 Buckets Created**
  ```bash
  aws s3 ls | grep unified-ops-hub
  ```

- [ ] **CloudFront Distribution Active**
  ```bash
  aws cloudfront list-distributions
  ```

- [ ] **Route53 Records Created**
  ```bash
  aws route53 list-resource-record-sets --hosted-zone-id <zone-id>
  ```

- [ ] **Secrets Created**
  ```bash
  aws secretsmanager list-secrets --filters Key=name,Values=unified-ops-hub
  ```

---

## Key Outputs

After successful deployment, note these values for Phase 2+:

| Output | Purpose | Command |
|--------|---------|---------|
| ALB DNS Name | API endpoint | `terraform output alb_dns_name` |
| RDS Endpoint | Database connection | `terraform output rds_endpoint` |
| RDS Reader Endpoint | Read replicas | `terraform output rds_reader_endpoint` |
| ElastiCache Endpoint | Redis connection | `terraform output elasticache_endpoint` |
| ECR Repository URIs | Container registry | `terraform output ecr_repositories` |
| CloudFront Domain | Frontend CDN | `terraform output cloudfront_domain_name` |
| Route53 Zone ID | DNS management | `terraform output route53_zone_id` |

---

## Cost Estimation

**Monthly Costs (Approximate, dev environment):**

| Service | Estimate |
|---------|----------|
| VPC (NAT Gateway) | $32 |
| ALB | $16 + data transfer |
| ECS Fargate | $30-50 |
| RDS Aurora Serverless | $20-40 |
| ElastiCache Redis | $15-25 |
| S3 + CloudFront | $5-10 |
| Secrets Manager | $0.40 |
| CloudWatch | $5-10 |
| **Total** | **~$120-180/month** |

*Production costs will be higher due to Multi-AZ and larger instances.*

---

## Troubleshooting

### Issue: Terraform State Lock

```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

### Issue: RDS Creation Timeout

```bash
# Increase timeout in main.tf
timeouts {
  create = "60m"
  delete = "60m"
}
```

### Issue: ALB Target Group Unhealthy

- Verify security group allows traffic from ALB
- Check ECS task health checks
- Review ALB target group health check settings

### Issue: CloudFront 403 Forbidden

- Verify S3 bucket policy allows CloudFront OAI
- Check S3 bucket public access settings
- Verify CloudFront distribution is enabled

---

## Destroying Infrastructure

**Warning:** This will delete all resources.

```bash
# Plan destruction
terraform plan -destroy

# Destroy resources
terraform destroy

# Confirm by typing 'yes'
```

---

## Next Steps

**Phase 1 Complete.** Awaiting approval to proceed to **Phase 2 — Data Layer**.

Please confirm:
1. ✅ All infrastructure provisioned successfully?
2. ✅ Outputs captured and documented?
3. ✅ Security groups properly configured?
4. ✅ Ready to proceed with database schema and migrations?

**Reply "APPROVED" or provide feedback for adjustments.**
