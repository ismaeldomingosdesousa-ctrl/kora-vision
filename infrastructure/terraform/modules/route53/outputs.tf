output "zone_id" {
  description = "Route53 zone ID"
  value       = data.aws_route53_zone.main.zone_id
}

output "nameservers" {
  description = "Route53 nameservers"
  value       = data.aws_route53_zone.main.name_servers
}

output "api_record_fqdn" {
  description = "API record FQDN"
  value       = aws_route53_record.api.fqdn
}

output "frontend_record_fqdn" {
  description = "Frontend record FQDN"
  value       = aws_route53_record.frontend.fqdn
}

output "www_record_fqdn" {
  description = "WWW record FQDN"
  value       = aws_route53_record.www.fqdn
}

output "alb_health_check_id" {
  description = "ALB health check ID"
  value       = aws_route53_health_check.alb.id
}
