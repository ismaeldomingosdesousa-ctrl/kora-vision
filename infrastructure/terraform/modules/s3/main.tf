# Frontend S3 Bucket
resource "aws_s3_bucket" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = var.frontend_bucket_name

  tags = {
    Name = var.frontend_bucket_name
  }
}

# Block public access for frontend bucket
resource "aws_s3_bucket_public_access_block" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = aws_s3_bucket.frontend[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for frontend bucket
resource "aws_s3_bucket_versioning" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = aws_s3_bucket.frontend[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption for frontend bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = aws_s3_bucket.frontend[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Logging S3 Bucket
resource "aws_s3_bucket" "logging" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = var.logging_bucket_name

  tags = {
    Name = var.logging_bucket_name
  }
}

# Block public access for logging bucket
resource "aws_s3_bucket_public_access_block" "logging" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.logging[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning for logging bucket
resource "aws_s3_bucket_versioning" "logging" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.logging[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption for logging bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "logging" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.logging[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Lifecycle policy for logging bucket (delete old logs)
resource "aws_s3_bucket_lifecycle_configuration" "logging" {
  count  = var.enable_logging_bucket ? 1 : 0
  bucket = aws_s3_bucket.logging[0].id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Configure logging for frontend bucket
resource "aws_s3_bucket_logging" "frontend" {
  count         = var.enable_frontend_bucket && var.enable_logging_bucket ? 1 : 0
  bucket        = aws_s3_bucket.frontend[0].id
  target_bucket = aws_s3_bucket.logging[0].id
  target_prefix = "frontend-logs/"
}

# CORS configuration for frontend bucket
resource "aws_s3_bucket_cors_configuration" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = aws_s3_bucket.frontend[0].id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag", "x-amz-version-id"]
    max_age_seconds = 3000
  }
}

# Bucket policy for frontend (CloudFront access)
resource "aws_s3_bucket_policy" "frontend" {
  count  = var.enable_frontend_bucket ? 1 : 0
  bucket = aws_s3_bucket.frontend[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontAccess"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.frontend[0].arn}/*"
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = "arn:aws:cloudfront::${data.aws_caller_identity.current.account_id}:distribution/*"
          }
        }
      }
    ]
  })
}

data "aws_caller_identity" "current" {}
