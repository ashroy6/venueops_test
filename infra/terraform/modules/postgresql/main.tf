resource "random_password" "admin" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "azurerm_postgresql_flexible_server" "this" {
  name                   = "psql-${var.name_prefix}"
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = "16"
  administrator_login    = var.administrator_login
  administrator_password = random_password.admin.result
  sku_name               = "GP_Standard_D2s_v3"
  storage_mb             = 32768
  backup_retention_days  = 7
  zone                   = "1"
  tags                   = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "venueops" {
  name      = "venueops"
  server_id = azurerm_postgresql_flexible_server.this.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}
