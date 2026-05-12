output "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID."
  value       = azurerm_log_analytics_workspace.this.id
}

output "application_insights_id" {
  description = "Application Insights ID."
  value       = azurerm_application_insights.this.id
}

output "application_insights_connection_string" {
  description = "Application Insights connection string."
  value       = azurerm_application_insights.this.connection_string
  sensitive   = true
}

output "azure_monitor_workspace_id" {
  description = "Azure Monitor Workspace ID for managed Prometheus."
  value       = azurerm_monitor_workspace.this.id
}
