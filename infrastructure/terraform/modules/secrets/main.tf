resource "aws_secretsmanager_secret" "main" {
  for_each = var.secrets

  name                    = "${var.project_name}/${each.key}-${var.environment}"
  recovery_window_in_days = var.environment == "prod" ? 30 : 7
  description             = "Secret for ${each.key}"

  tags = {
    Name = "${var.project_name}-${each.key}-${var.environment}"
  }
}

resource "aws_secretsmanager_secret_version" "main" {
  for_each = var.secrets

  secret_id     = aws_secretsmanager_secret.main[each.key].id
  secret_string = each.value
}

# IAM Policy for ECS tasks to access secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.project_name}-secrets-access-${var.environment}"
  description = "Policy for ECS tasks to access secrets"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          for secret in aws_secretsmanager_secret.main : secret.arn
        ]
      }
    ]
  })
}
