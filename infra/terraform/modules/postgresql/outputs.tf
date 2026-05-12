output "server_name" {
  description = "PostgreSQL Flexible Server name."
  value       = azurerm_postgresql_flexible_server.this.name
}

output "database_name" {
  description = "PostgreSQL database name."
  value       = azurerm_postgresql_flexible_server_database.venueops.name
}

output "administrator_login" {
  description = "PostgreSQL administrator username."
  value       = azurerm_postgresql_flexible_server.this.administrator_login
}
