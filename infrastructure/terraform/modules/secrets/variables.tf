variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "secrets" {
  description = "Map of secrets to create"
  type        = map(string)
  sensitive   = true
  default     = {}
}
