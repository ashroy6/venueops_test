locals {
  acr_name = replace("acr${var.name_prefix}", "-", "")
}

resource "azurerm_container_registry" "this" {
  name                          = substr(local.acr_name, 0, 50)
  resource_group_name           = var.resource_group_name
  location                      = var.location
  sku                           = var.sku
  admin_enabled                 = false
  public_network_access_enabled = true
  zone_redundancy_enabled       = var.sku == "Premium" ? true : false
  tags                          = var.tags
}
