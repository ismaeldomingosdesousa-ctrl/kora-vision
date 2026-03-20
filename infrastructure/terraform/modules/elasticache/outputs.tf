output "replication_group_id" {
  description = "Redis replication group ID"
  value       = aws_elasticache_replication_group.main.id
}

output "primary_endpoint_address" {
  description = "Redis primary endpoint address"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "reader_endpoint_address" {
  description = "Redis reader endpoint address"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_replication_group.main.port
}

output "auth_token_secret_arn" {
  description = "Secrets Manager ARN for Redis auth token"
  value       = aws_secretsmanager_secret.redis_auth_token.arn
  sensitive   = true
}

output "configuration_endpoint_address" {
  description = "Redis configuration endpoint address"
  value       = aws_elasticache_replication_group.main.configuration_endpoint_address
}
