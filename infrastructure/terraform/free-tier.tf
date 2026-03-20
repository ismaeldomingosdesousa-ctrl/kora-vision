# ============================================================================
# Kora Vision - AWS Free-Tier Infrastructure
# Otimizado para MVP com custo zero por 12 meses
# ============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "kora-vision"
      Environment = "mvp"
      ManagedBy   = "terraform"
    }
  }
}

# ============================================================================
# VPC - Virtual Private Cloud
# ============================================================================

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "kora-vision-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "kora-vision-igw"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "kora-vision-public-subnet"
  }
}

# Private Subnet para RDS
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "kora-vision-private-subnet"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.main.id
  }

  tags = {
    Name = "kora-vision-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Data source para availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# ============================================================================
# Security Groups
# ============================================================================

resource "aws_security_group" "ec2" {
  name        = "kora-vision-ec2-sg"
  description = "Security group for EC2 instance"
  vpc_id      = aws_vpc.main.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Backend ports
  ingress {
    from_port   = 8000
    to_port     = 8003
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "kora-vision-ec2-sg"
  }
}

resource "aws_security_group" "rds" {
  name        = "kora-vision-rds-sg"
  description = "Security group for RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "kora-vision-rds-sg"
  }
}

# ============================================================================
# EC2 Instance (t2.micro - Free-Tier)
# ============================================================================

# Ubuntu 22.04 LTS AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "backend" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro" # Free-Tier eligible
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2.id]
  key_name               = aws_key_pair.deployer.key_name

  # User data script para instalar dependências
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    db_host     = aws_db_instance.postgres.endpoint
    db_name     = aws_db_instance.postgres.db_name
    db_user     = aws_db_instance.postgres.username
    db_password = random_password.db_password.result
  }))

  root_block_device {
    volume_type           = "gp2"
    volume_size           = 20
    delete_on_termination = true
  }

  tags = {
    Name = "kora-vision-backend"
  }

  depends_on = [aws_db_instance.postgres]
}

# Key Pair para SSH
resource "aws_key_pair" "deployer" {
  key_name   = "kora-vision-deployer"
  public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Name = "kora-vision-deployer"
  }
}

# ============================================================================
# RDS PostgreSQL (Free-Tier)
# ============================================================================

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_subnet_group" "main" {
  name       = "kora-vision-db-subnet-group"
  subnet_ids = [aws_subnet.public.id, aws_subnet.private.id]

  tags = {
    Name = "kora-vision-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier            = "kora-vision-db"
  engine                = "postgres"
  engine_version        = "15.3"
  instance_class        = "db.t3.micro" # Free-Tier eligible
  allocated_storage     = 20
  storage_type          = "gp2"
  db_name               = "koravision"
  username              = "admin"
  password              = random_password.db_password.result
  db_subnet_group_name  = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  skip_final_snapshot       = true
  publicly_accessible       = true
  backup_retention_period   = 7
  multi_az                  = false # Free-Tier: single-AZ only

  tags = {
    Name = "kora-vision-postgres"
  }
}

# ============================================================================
# S3 Bucket para Frontend
# ============================================================================

resource "aws_s3_bucket" "frontend" {
  bucket = "kora-vision-frontend-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "kora-vision-frontend"
  }
}

resource "aws_s3_bucket_versioning" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "PublicRead"
        Effect = "Allow"
        Principal = "*"
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# ============================================================================
# CloudFront Distribution
# ============================================================================

resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3Origin"
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3Origin"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "kora-vision-cdn"
  }
}

# ============================================================================
# Data Sources
# ============================================================================

data "aws_caller_identity" "current" {}

# ============================================================================
# Outputs
# ============================================================================

output "ec2_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.backend.public_ip
}

output "ec2_instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.backend.id
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_database_name" {
  description = "RDS Database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_username" {
  description = "RDS Master username"
  value       = aws_db_instance.postgres.username
}

output "rds_password" {
  description = "RDS Master password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.backend.public_ip}"
}
