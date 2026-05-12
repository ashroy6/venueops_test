output "app_hostname" {
  description = "Application hostname."
  value       = var.app_hostname
}

output "origin_hostname" {
  description = "Origin hostname."
  value       = var.origin_hostname
}

output "recommended_controls" {
  description = "Recommended Cloudflare edge security controls."
  value       = terraform_data.cloudflare_design_marker.output.recommended_controls
}
