output "namespace_name" {
  description = "Event Hub namespace name."
  value       = azurerm_eventhub_namespace.this.name
}

output "device_logs_eventhub_name" {
  description = "Device logs Event Hub name."
  value       = azurerm_eventhub.device_logs.name
}

output "consumer_group_name" {
  description = "Log processor consumer group name."
  value       = azurerm_eventhub_consumer_group.log_processors.name
}
