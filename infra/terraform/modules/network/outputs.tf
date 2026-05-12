output "vnet_id" {
  description = "Virtual network ID."
  value       = azurerm_virtual_network.this.id
}

output "vnet_name" {
  description = "Virtual network name."
  value       = azurerm_virtual_network.this.name
}

output "aks_subnet_id" {
  description = "AKS subnet ID."
  value       = azurerm_subnet.aks.id
}

output "app_gateway_subnet_id" {
  description = "Application Gateway subnet ID."
  value       = azurerm_subnet.app_gateway.id
}

output "private_endpoint_subnet_id" {
  description = "Private endpoint subnet ID."
  value       = azurerm_subnet.private_endpoints.id
}
