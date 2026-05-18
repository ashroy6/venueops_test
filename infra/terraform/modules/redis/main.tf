resource "azurerm_redis_cache" "this" {
  name                = "redis-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name

  capacity = var.capacity
  family   = var.family
  sku_name = var.sku_name

  minimum_tls_version           = "1.2"
  non_ssl_port_enabled          = false
  public_network_access_enabled = var.public_network_access_enabled
  redis_version                 = var.redis_version

  subnet_id = var.subnet_id

  redis_configuration {
    maxmemory_policy = var.maxmemory_policy
  }

  tags = var.tags
}
