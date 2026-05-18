variable "project" {
  description = "Project name used for resource naming."
  type        = string
  default     = "venueops"
}

variable "environment" {
  description = "Environment name."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "uksouth"
}

variable "resource_tags" {
  description = "Common resource tags."
  type        = map(string)
  default     = {}
}

variable "vnet_address_space" {
  description = "VNet CIDR range."
  type        = list(string)
  default     = ["10.40.0.0/16"]
}

variable "public_subnet_cidr" {
  description = "Public/DMZ subnet CIDR range for Azure Application Gateway WAF."
  type        = string
  default     = "10.40.1.0/24"
}

variable "private_aks_subnet_cidr" {
  description = "Private AKS subnet CIDR range for AKS node pools."
  type        = string
  default     = "10.40.2.0/24"
}

variable "private_data_subnet_cidr" {
  description = "Private data subnet CIDR range for database/cache/data services."
  type        = string
  default     = "10.40.3.0/24"
}

variable "private_endpoint_subnet_cidr" {
  description = "Private endpoint subnet CIDR range for Azure Private Link endpoints."
  type        = string
  default     = "10.40.4.0/24"
}

variable "cloudflare_enabled" {
  description = "Whether to create Cloudflare resources."
  type        = bool
  default     = false
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID. Required when cloudflare_enabled is true."
  type        = string
  default     = ""
}

variable "app_hostname" {
  description = "Application hostname."
  type        = string
  default     = "venueops.example.com"
}

variable "app_gateway_backend_fqdn" {
  description = "Backend FQDN used by Application Gateway to reach AKS ingress. Replace with real AKS ingress FQDN/IP during live deployment."
  type        = string
  default     = "venueops-web.venueops.svc.cluster.local"
}

variable "redis_sku_name" {
  description = "Azure Cache for Redis SKU. Premium is used so Redis can be placed in the private data subnet."
  type        = string
  default     = "Premium"

  validation {
    condition     = var.redis_sku_name == "Premium"
    error_message = "redis_sku_name must be Premium because the Redis module uses subnet_id."
  }
}

variable "redis_family" {
  description = "Azure Cache for Redis SKU family. P is Premium."
  type        = string
  default     = "P"

  validation {
    condition     = var.redis_family == "P"
    error_message = "redis_family must be P for Premium Redis."
  }
}

variable "redis_capacity" {
  description = "Azure Cache for Redis Premium capacity. P1 = 1."
  type        = number
  default     = 1

  validation {
    condition     = var.redis_capacity >= 1 && var.redis_capacity <= 5
    error_message = "redis_capacity must be between 1 and 5 for Premium Redis."
  }
}

variable "redis_version" {
  description = "Redis major version."
  type        = string
  default     = "6"
}

variable "redis_public_network_access_enabled" {
  description = "Whether public network access is enabled for Redis."
  type        = bool
  default     = false
}

variable "redis_maxmemory_policy" {
  description = "Redis maxmemory eviction policy."
  type        = string
  default     = "volatile-lru"
}
