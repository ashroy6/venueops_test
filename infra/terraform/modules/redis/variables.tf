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

variable "subnet_id" {
  description = "Private data subnet ID for Premium Azure Cache for Redis VNet placement."
  type        = string
}

variable "sku_name" {
  description = "Azure Cache for Redis SKU. Premium is required for subnet_id-based VNet placement."
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Premium"], var.sku_name)
    error_message = "This module uses subnet_id, so sku_name must be Premium."
  }
}

variable "family" {
  description = "Redis SKU family. P is required for Premium."
  type        = string
  default     = "P"

  validation {
    condition     = var.family == "P"
    error_message = "This module uses Premium Redis, so family must be P."
  }
}

variable "capacity" {
  description = "Redis Premium capacity. P1 = 1."
  type        = number
  default     = 1

  validation {
    condition     = var.capacity >= 1 && var.capacity <= 5
    error_message = "Premium Redis capacity must be between 1 and 5."
  }
}

variable "redis_version" {
  description = "Redis major version."
  type        = string
  default     = "6"
}

variable "public_network_access_enabled" {
  description = "Whether public network access is enabled for Redis."
  type        = bool
  default     = false
}

variable "maxmemory_policy" {
  description = "Redis maxmemory eviction policy."
  type        = string
  default     = "volatile-lru"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
