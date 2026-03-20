output "repository_urls" {
  description = "ECR repository URLs"
  value = {
    for name, repo in aws_ecr_repository.main : name => repo.repository_url
  }
}

output "repository_uris" {
  description = "ECR repository URIs"
  value = {
    for name, repo in aws_ecr_repository.main : name => repo.repository_url
  }
}

output "registry_id" {
  description = "ECR registry ID"
  value       = data.aws_caller_identity.current.account_id
}

data "aws_caller_identity" "current" {}
