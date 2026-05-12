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

variable "app_gateway_subnet_id" {
  description = "Application Gateway subnet ID."
  type        = string
}

variable "backend_fqdn" {
  description = "Backend FQDN for AKS ingress or internal ingress endpoint."
  type        = string
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
