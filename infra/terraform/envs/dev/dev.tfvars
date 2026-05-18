project     = "venueops"
environment = "dev"
location    = "uksouth"

vnet_address_space           = ["10.40.0.0/16"]
public_subnet_cidr           = "10.40.1.0/24"
private_aks_subnet_cidr      = "10.40.2.0/24"
private_data_subnet_cidr     = "10.40.3.0/24"
private_endpoint_subnet_cidr = "10.40.4.0/24"

cloudflare_enabled = false
cloudflare_zone_id = ""
app_hostname       = "dev.venueops.example.com"

resource_tags = {
  cost_center = "interview"
}

app_gateway_backend_fqdn = "dev-aks-ingress.venueops.internal"

redis_sku_name                      = "Premium"
redis_family                        = "P"
redis_capacity                      = 1
redis_version                       = "6"
redis_public_network_access_enabled = false
redis_maxmemory_policy              = "volatile-lru"
