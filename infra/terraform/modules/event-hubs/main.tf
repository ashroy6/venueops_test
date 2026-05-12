resource "azurerm_eventhub_namespace" "this" {
  name                = "ehns-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "Standard"
  capacity            = 2
  tags                = var.tags
}

resource "azurerm_eventhub" "device_logs" {
  name                = "device-logs"
  namespace_name      = azurerm_eventhub_namespace.this.name
  resource_group_name = var.resource_group_name
  partition_count     = 4
  message_retention   = 3
}

resource "azurerm_eventhub_consumer_group" "log_processors" {
  name                = "log-processors"
  namespace_name      = azurerm_eventhub_namespace.this.name
  eventhub_name       = azurerm_eventhub.device_logs.name
  resource_group_name = var.resource_group_name
}
