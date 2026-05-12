output "id" {
  description = "Application Gateway ID."
  value       = azurerm_application_gateway.this.id
}

output "name" {
  description = "Application Gateway name."
  value       = azurerm_application_gateway.this.name
}

output "public_ip_address" {
  description = "Application Gateway public IP address."
  value       = azurerm_public_ip.app_gateway.ip_address
}

output "public_ip_fqdn" {
  description = "Application Gateway public IP FQDN."
  value       = azurerm_public_ip.app_gateway.fqdn
}

output "waf_policy_id" {
  description = "WAF policy ID."
  value       = azurerm_web_application_firewall_policy.this.id
}
