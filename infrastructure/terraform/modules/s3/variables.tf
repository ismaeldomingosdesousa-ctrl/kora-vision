variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "enable_frontend_bucket" {
  description = "Enable frontend S3 bucket"
  type        = bool
  default     = true
}

variable "frontend_bucket_name" {
  description = "Frontend S3 bucket name"
  type        = string
}

variable "enable_logging_bucket" {
  description = "Enable logging S3 bucket"
  type        = bool
  default     = true
}

variable "logging_bucket_name" {
  description = "Logging S3 bucket name"
  type        = string
}
