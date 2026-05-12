resource "azurerm_servicebus_namespace" "this" {
  name                = "sbns-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Premium"
  capacity            = 1
  tags                = var.tags
}

resource "azurerm_servicebus_queue" "notification_jobs" {
  name         = "notification-jobs"
  namespace_id = azurerm_servicebus_namespace.this.id

  lock_duration                        = "PT1M"
  max_delivery_count                   = 10
  dead_lettering_on_message_expiration = true
}

resource "azurerm_servicebus_queue" "video_jobs" {
  name         = "video-jobs"
  namespace_id = azurerm_servicebus_namespace.this.id

  lock_duration                        = "PT5M"
  max_delivery_count                   = 5
  dead_lettering_on_message_expiration = true
}

resource "azurerm_servicebus_queue" "device_commands" {
  name         = "device-commands"
  namespace_id = azurerm_servicebus_namespace.this.id

  lock_duration                        = "PT1M"
  max_delivery_count                   = 10
  dead_lettering_on_message_expiration = true
}
