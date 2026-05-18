project     = "venueops"
environment = "prod"
location    = "uksouth"

vnet_address_space           = ["10.60.0.0/16"]
public_subnet_cidr           = "10.60.1.0/24"
private_aks_subnet_cidr      = "10.60.2.0/24"
private_data_subnet_cidr     = "10.60.3.0/24"
private_endpoint_subnet_cidr = "10.60.4.0/24"

cloudflare_enabled = false
cloudflare_zone_id = ""
app_hostname       = "venueops.example.com"

resource_tags = {
  cost_center = "interview"
}

app_gateway_backend_fqdn = "prod-aks-ingress.venueops.internal"
