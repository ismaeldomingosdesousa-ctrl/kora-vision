# Log Groups
resource "aws_cloudwatch_log_group" "core_api" {
  name              = "/aws/ecs/${var.project_name}-core-api-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-core-api-logs-${var.environment}"
  }
}

resource "aws_cloudwatch_log_group" "integration_worker" {
  name              = "/aws/ecs/${var.project_name}-integration-worker-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-integration-worker-logs-${var.environment}"
  }
}

resource "aws_cloudwatch_log_group" "webhook_ingestor" {
  name              = "/aws/ecs/${var.project_name}-webhook-ingestor-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-webhook-ingestor-logs-${var.environment}"
  }
}

resource "aws_cloudwatch_log_group" "realtime_service" {
  name              = "/aws/ecs/${var.project_name}-realtime-service-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-realtime-service-logs-${var.environment}"
  }
}

# Metric Alarms for Application Health
resource "aws_cloudwatch_metric_alarm" "application_errors" {
  alarm_name          = "${var.project_name}-application-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alert when application errors exceed threshold"
  treat_missing_data  = "notBreaching"
}

# Dashboard for monitoring
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", { stat = "Average" }],
            [".", "MemoryUtilization", { stat = "Average" }],
            ["AWS/RDS", "CPUUtilization", { stat = "Average" }],
            [".", "DatabaseConnections", { stat = "Average" }],
            ["AWS/ElastiCache", "EngineCPUUtilization", { stat = "Average" }],
            [".", "DatabaseMemoryUsagePercentage", { stat = "Average" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Infrastructure Metrics"
        }
      },
      {
        type = "log"
        properties = {
          query   = "fields @timestamp, @message | stats count() as error_count by @logStream"
          region  = data.aws_region.current.name
          title   = "Error Count by Service"
        }
      }
    ]
  })
}

data "aws_region" "current" {}
