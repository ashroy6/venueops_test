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

variable "sku" {
  description = "ACR SKU."
  type        = string
  default     = "Premium"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
