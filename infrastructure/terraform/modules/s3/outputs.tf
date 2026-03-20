output "frontend_bucket_id" {
  description = "Frontend S3 bucket ID"
  value       = try(aws_s3_bucket.frontend[0].id, "")
}

output "frontend_bucket_name" {
  description = "Frontend S3 bucket name"
  value       = try(aws_s3_bucket.frontend[0].bucket, "")
}

output "frontend_bucket_domain_name" {
  description = "Frontend S3 bucket domain name"
  value       = try(aws_s3_bucket.frontend[0].bucket_regional_domain_name, "")
}

output "frontend_bucket_arn" {
  description = "Frontend S3 bucket ARN"
  value       = try(aws_s3_bucket.frontend[0].arn, "")
}

output "logging_bucket_id" {
  description = "Logging S3 bucket ID"
  value       = try(aws_s3_bucket.logging[0].id, "")
}

output "logging_bucket_name" {
  description = "Logging S3 bucket name"
  value       = try(aws_s3_bucket.logging[0].bucket, "")
}

output "logging_bucket_arn" {
  description = "Logging S3 bucket ARN"
  value       = try(aws_s3_bucket.logging[0].arn, "")
}
