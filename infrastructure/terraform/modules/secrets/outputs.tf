output "secret_arns" {
  description = "ARNs of created secrets"
  value = {
    for key, secret in aws_secretsmanager_secret.main : key => secret.arn
  }
  sensitive = true
}

output "secret_ids" {
  description = "IDs of created secrets"
  value = {
    for key, secret in aws_secretsmanager_secret.main : key => secret.id
  }
}

output "secrets_access_policy_arn" {
  description = "ARN of secrets access policy"
  value       = aws_iam_policy.secrets_access.arn
}
