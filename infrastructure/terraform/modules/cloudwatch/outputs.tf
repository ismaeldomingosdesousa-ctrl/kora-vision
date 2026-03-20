output "log_group_names" {
  description = "CloudWatch log group names"
  value = {
    core_api            = aws_cloudwatch_log_group.core_api.name
    integration_worker  = aws_cloudwatch_log_group.integration_worker.name
    webhook_ingestor    = aws_cloudwatch_log_group.webhook_ingestor.name
    realtime_service    = aws_cloudwatch_log_group.realtime_service.name
  }
}

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${data.aws_region.current.name}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

data "aws_region" "current" {}
