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

variable "aks_subnet_cidr" {
  description = "AKS subnet CIDR."
  type        = string
}

variable "app_gateway_subnet_cidr" {
  description = "Application Gateway subnet CIDR."
  type        = string
}

variable "private_endpoint_subnet_cidr" {
  description = "Private endpoint subnet CIDR."
  type        = string
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
