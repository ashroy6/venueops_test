locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = merge(
    {
      project     = var.project
      environment = var.environment
      managed_by  = "terraform"
      owner       = "devops-interview"
    },
    var.resource_tags
  )
}

data "azurerm_client_config" "current" {}

module "resource_group" {
  source = "./modules/resource-group"

  name     = "rg-${local.name_prefix}"
  location = var.location
  tags     = local.common_tags
}

module "network" {
  source = "./modules/network"

  name_prefix                  = local.name_prefix
  location                     = module.resource_group.location
  resource_group_name          = module.resource_group.name
  vnet_address_space           = var.vnet_address_space
  public_subnet_cidr           = var.public_subnet_cidr
  private_aks_subnet_cidr      = var.private_aks_subnet_cidr
  private_data_subnet_cidr     = var.private_data_subnet_cidr
  private_endpoint_subnet_cidr = var.private_endpoint_subnet_cidr
  tags                         = local.common_tags
}

module "acr" {
  source = "./modules/acr"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "key_vault" {
  source = "./modules/key-vault"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = local.common_tags
}

module "storage" {
  source = "./modules/storage"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "event_hubs" {
  source = "./modules/event-hubs"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "service_bus" {
  source = "./modules/service-bus"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "postgresql" {
  source = "./modules/postgresql"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "redis" {
  source = "./modules/redis"

  name_prefix                   = local.name_prefix
  location                      = module.resource_group.location
  resource_group_name           = module.resource_group.name
  subnet_id                     = module.network.private_data_subnet_id
  sku_name                      = var.redis_sku_name
  family                        = var.redis_family
  capacity                      = var.redis_capacity
  redis_version                 = var.redis_version
  public_network_access_enabled = var.redis_public_network_access_enabled
  maxmemory_policy              = var.redis_maxmemory_policy
  tags                          = local.common_tags
}


module "application_gateway" {
  source = "./modules/application-gateway"

  name_prefix           = local.name_prefix
  location              = module.resource_group.location
  resource_group_name   = module.resource_group.name
  app_gateway_subnet_id = module.network.public_subnet_id
  backend_fqdn          = var.app_gateway_backend_fqdn
  tags                  = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  name_prefix         = local.name_prefix
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  tags                = local.common_tags
}

module "aks" {
  source = "./modules/aks"

  name_prefix                = local.name_prefix
  location                   = module.resource_group.location
  resource_group_name        = module.resource_group.name
  aks_subnet_id              = module.network.private_aks_subnet_id
  acr_id                     = module.acr.id
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  tags                       = local.common_tags
}

module "cloudflare" {
  source = "./modules/cloudflare"

  enabled            = var.cloudflare_enabled
  cloudflare_zone_id = var.cloudflare_zone_id
  app_hostname       = var.app_hostname
  origin_hostname    = "appgw-${local.name_prefix}.cloudapp.azure.com"
}
