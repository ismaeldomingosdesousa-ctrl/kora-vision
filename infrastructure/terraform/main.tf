terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state management
  # backend "s3" {
  #   bucket         = "unified-ops-hub-terraform-state"
  #   key            = "prod/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  project_name           = var.project_name
  environment            = var.environment
  vpc_cidr               = var.vpc_cidr
  availability_zones     = var.availability_zones
  public_subnet_cidrs    = var.public_subnet_cidrs
  private_subnet_cidrs   = var.private_subnet_cidrs
  enable_nat_gateway     = true
  enable_vpn_gateway     = false
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security_groups"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
}

# ALB Module
module "alb" {
  source = "./modules/alb"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  public_subnet_ids         = module.vpc.public_subnet_ids
  alb_security_group_id     = module.security_groups.alb_security_group_id
  enable_https              = var.enable_https
  certificate_arn           = var.acm_certificate_arn
}

# ECR Module
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
  
  repositories = [
    "core-api",
    "integration-worker",
    "webhook-ingestor",
    "realtime-service"
  ]
}

# ECS Cluster Module
module "ecs_cluster" {
  source = "./modules/ecs"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_subnet_ids        = module.vpc.private_subnet_ids
  ecs_security_group_id     = module.security_groups.ecs_security_group_id
  alb_target_group_arn      = module.alb.target_group_arn
  
  # Capacity configuration
  desired_capacity          = var.ecs_desired_capacity
  min_capacity              = var.ecs_min_capacity
  max_capacity              = var.ecs_max_capacity
  instance_type             = var.ecs_instance_type
}

# RDS Aurora PostgreSQL Module
module "rds" {
  source = "./modules/rds"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_subnet_ids        = module.vpc.private_subnet_ids
  rds_security_group_id     = module.security_groups.rds_security_group_id
  
  # Database configuration
  db_name                   = var.db_name
  db_username               = var.db_username
  db_password               = var.db_password
  engine_version            = var.db_engine_version
  instance_class            = var.db_instance_class
  backup_retention_period   = var.db_backup_retention_period
  multi_az                  = var.db_multi_az
  
  depends_on = [module.vpc]
}

# ElastiCache Redis Module
module "elasticache" {
  source = "./modules/elasticache"

  project_name              = var.project_name
  environment               = var.environment
  vpc_id                    = module.vpc.vpc_id
  private_subnet_ids        = module.vpc.private_subnet_ids
  elasticache_security_group_id = module.security_groups.elasticache_security_group_id
  
  # Redis configuration
  engine_version            = var.redis_engine_version
  node_type                 = var.redis_node_type
  num_cache_nodes           = var.redis_num_nodes
  automatic_failover        = var.redis_automatic_failover
  
  depends_on = [module.vpc]
}

# S3 Module
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
  
  # Frontend bucket
  enable_frontend_bucket = true
  frontend_bucket_name   = "${var.project_name}-frontend-${var.environment}"
  
  # Logging bucket
  enable_logging_bucket  = true
  logging_bucket_name    = "${var.project_name}-logs-${var.environment}"
}

# CloudFront Module
module "cloudfront" {
  source = "./modules/cloudfront"

  project_name           = var.project_name
  environment            = var.environment
  s3_bucket_domain_name  = module.s3.frontend_bucket_domain_name
  s3_bucket_id           = module.s3.frontend_bucket_id
  certificate_arn        = var.acm_certificate_arn
  domain_name            = var.domain_name
  
  depends_on = [module.s3]
}

# Route53 Module
module "route53" {
  source = "./modules/route53"

  project_name           = var.project_name
  environment            = var.environment
  domain_name            = var.domain_name
  
  # ALB DNS
  alb_dns_name           = module.alb.alb_dns_name
  alb_zone_id            = module.alb.alb_zone_id
  
  # CloudFront DNS
  cloudfront_domain_name = module.cloudfront.cloudfront_domain_name
  cloudfront_zone_id     = module.cloudfront.cloudfront_zone_id
  
  depends_on = [module.alb, module.cloudfront]
}

# Secrets Manager Module
module "secrets" {
  source = "./modules/secrets"

  project_name = var.project_name
  environment  = var.environment
  
  secrets = {
    "db-password"        = var.db_password
    "jwt-secret"         = var.jwt_secret
    "cognito-client-id"  = var.cognito_client_id
    "cognito-client-secret" = var.cognito_client_secret
  }
}

# CloudWatch Module
module "cloudwatch" {
  source = "./modules/cloudwatch"

  project_name = var.project_name
  environment  = var.environment
  
  # Log groups
  log_retention_days = var.log_retention_days
}
