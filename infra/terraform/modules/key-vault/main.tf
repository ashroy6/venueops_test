locals {
  key_vault_name = substr(replace("kv-${var.name_prefix}", "-", ""), 0, 24)
}

resource "azurerm_key_vault" "this" {
  name                       = local.key_vault_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  purge_protection_enabled   = true
  soft_delete_retention_days = 30
  rbac_authorization_enabled = true
  tags                       = var.tags
}
