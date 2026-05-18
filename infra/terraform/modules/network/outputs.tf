output "vnet_id" {
  description = "Virtual network ID."
  value       = azurerm_virtual_network.this.id
}

output "vnet_name" {
  description = "Virtual network name."
  value       = azurerm_virtual_network.this.name
}

output "public_subnet_id" {
  description = "Public/DMZ subnet ID used by Azure Application Gateway WAF."
  value       = azurerm_subnet.public_dmz.id
}

output "private_aks_subnet_id" {
  description = "Private AKS subnet ID."
  value       = azurerm_subnet.private_aks.id
}

output "private_data_subnet_id" {
  description = "Private data subnet ID."
  value       = azurerm_subnet.private_data.id
}

output "private_endpoint_subnet_id" {
  description = "Private endpoint subnet ID."
  value       = azurerm_subnet.private_endpoints.id
}

# Backward-compatible aliases for existing root modules/outputs.
output "app_gateway_subnet_id" {
  description = "Application Gateway subnet ID. Alias for public_subnet_id."
  value       = azurerm_subnet.public_dmz.id
}

output "aks_subnet_id" {
  description = "AKS subnet ID. Alias for private_aks_subnet_id."
  value       = azurerm_subnet.private_aks.id
}
