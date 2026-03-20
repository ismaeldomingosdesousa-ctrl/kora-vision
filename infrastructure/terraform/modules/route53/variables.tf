variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Domain name"
  type        = string
}

variable "alb_dns_name" {
  description = "ALB DNS name"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB zone ID"
  type        = string
}

variable "cloudfront_domain_name" {
  description = "CloudFront domain name"
  type        = string
}

variable "cloudfront_zone_id" {
  description = "CloudFront zone ID"
  type        = string
}
