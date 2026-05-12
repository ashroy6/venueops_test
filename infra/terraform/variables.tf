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

variable "aks_subnet_cidr" {
  description = "AKS subnet CIDR range."
  type        = string
  default     = "10.40.1.0/24"
}

variable "app_gateway_subnet_cidr" {
  description = "Application Gateway subnet CIDR range."
  type        = string
  default     = "10.40.2.0/24"
}

variable "private_endpoint_subnet_cidr" {
  description = "Private endpoint subnet CIDR range."
  type        = string
  default     = "10.40.3.0/24"
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
