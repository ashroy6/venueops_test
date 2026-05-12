output "namespace_name" {
  description = "Service Bus namespace name."
  value       = azurerm_servicebus_namespace.this.name
}

output "notification_queue_name" {
  description = "Notification jobs queue name."
  value       = azurerm_servicebus_queue.notification_jobs.name
}

output "video_queue_name" {
  description = "Video jobs queue name."
  value       = azurerm_servicebus_queue.video_jobs.name
}

output "device_commands_queue_name" {
  description = "Device commands queue name."
  value       = azurerm_servicebus_queue.device_commands.name
}
