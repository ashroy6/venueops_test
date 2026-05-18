output "resource_group_name" {
  description = "Resource group name."
  value       = module.resource_group.name
}

output "vnet_id" {
  description = "Virtual network ID."
  value       = module.network.vnet_id
}

output "public_subnet_id" {
  description = "Public/DMZ subnet ID used by Azure Application Gateway WAF."
  value       = module.network.public_subnet_id
}

output "private_aks_subnet_id" {
  description = "Private AKS subnet ID."
  value       = module.network.private_aks_subnet_id
}

output "private_data_subnet_id" {
  description = "Private data subnet ID."
  value       = module.network.private_data_subnet_id
}

output "private_endpoint_subnet_id" {
  description = "Private endpoint subnet ID."
  value       = module.network.private_endpoint_subnet_id
}

output "aks_subnet_id" {
  description = "Backward-compatible AKS subnet ID output."
  value       = module.network.private_aks_subnet_id
}

output "aks_cluster_name" {
  description = "AKS cluster name."
  value       = module.aks.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server."
  value       = module.acr.login_server
}

output "key_vault_uri" {
  description = "Key Vault URI."
  value       = module.key_vault.vault_uri
}

output "storage_account_name" {
  description = "Storage account name."
  value       = module.storage.name
}

output "eventhub_namespace_name" {
  description = "Event Hub namespace name."
  value       = module.event_hubs.namespace_name
}

output "servicebus_namespace_name" {
  description = "Service Bus namespace name."
  value       = module.service_bus.namespace_name
}

output "postgresql_server_name" {
  description = "PostgreSQL Flexible Server name."
  value       = module.postgresql.server_name
}

output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID."
  value       = module.monitoring.log_analytics_workspace_id
}

output "application_insights_connection_string" {
  description = "Application Insights connection string."
  value       = module.monitoring.application_insights_connection_string
  sensitive   = true
}

output "application_gateway_name" {
  description = "Application Gateway name."
  value       = module.application_gateway.name
}

output "application_gateway_public_ip" {
  description = "Application Gateway public IP address."
  value       = module.application_gateway.public_ip_address
}

output "application_gateway_waf_policy_id" {
  description = "Application Gateway WAF policy ID."
  value       = module.application_gateway.waf_policy_id
}

output "redis_name" {
  description = "Azure Cache for Redis name."
  value       = module.redis.name
}

output "redis_hostname" {
  description = "Azure Cache for Redis hostname."
  value       = module.redis.hostname
}

output "redis_ssl_port" {
  description = "Azure Cache for Redis SSL port."
  value       = module.redis.ssl_port
}

output "redis_connection_string" {
  description = "Azure Cache for Redis TLS connection string."
  value       = module.redis.connection_string
  sensitive   = true
}
