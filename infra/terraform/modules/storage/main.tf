locals {
  storage_name = substr(replace("st${var.name_prefix}", "-", ""), 0, 24)
}

resource "azurerm_storage_account" "this" {
  name                            = local.storage_name
  resource_group_name             = var.resource_group_name
  location                        = var.location
  account_tier                    = "Standard"
  account_replication_type        = "ZRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true
  tags                            = var.tags
}

resource "azurerm_storage_container" "raw_logs" {
  name                  = "raw-logs"
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "video_landing" {
  name                  = "video-landing"
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "video_processed" {
  name                  = "video-processed"
  storage_account_name  = azurerm_storage_account.this.name
  container_access_type = "private"
}
