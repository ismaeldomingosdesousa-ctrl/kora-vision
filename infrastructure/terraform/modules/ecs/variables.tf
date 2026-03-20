variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID"
  type        = string
}

variable "alb_target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}

variable "desired_capacity" {
  description = "Desired number of ECS instances"
  type        = number
  default     = 3
}

variable "min_capacity" {
  description = "Minimum number of ECS instances"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum number of ECS instances"
  type        = number
  default     = 10
}

variable "instance_type" {
  description = "EC2 instance type for ECS"
  type        = string
  default     = "t3.medium"
}
