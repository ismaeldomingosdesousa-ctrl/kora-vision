output "cloudfront_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.main.id
}

output "cloudfront_arn" {
  description = "CloudFront distribution ARN"
  value       = aws_cloudfront_distribution.main.arn
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.main.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (alias)"
  value       = aws_cloudfront_distribution.main.id
}

output "origin_access_identity_path" {
  description = "Origin Access Identity path"
  value       = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
}
