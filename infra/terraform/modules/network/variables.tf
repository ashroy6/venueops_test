variable "name_prefix" {
  description = "Name prefix."
  type        = string
}

variable "location" {
  description = "Azure region."
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name."
  type        = string
}

variable "vnet_address_space" {
  description = "VNet address space."
  type        = list(string)
}

variable "public_subnet_cidr" {
  description = "Public/DMZ subnet CIDR range for Azure Application Gateway WAF."
  type        = string
}

variable "private_aks_subnet_cidr" {
  description = "Private AKS subnet CIDR range for AKS node pools."
  type        = string
}

variable "private_data_subnet_cidr" {
  description = "Private data subnet CIDR range for database/cache/data services."
  type        = string
}

variable "private_endpoint_subnet_cidr" {
  description = "Private endpoint subnet CIDR range for Azure Private Link endpoints."
  type        = string
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
