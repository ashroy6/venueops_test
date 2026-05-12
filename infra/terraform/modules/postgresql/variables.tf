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

variable "administrator_login" {
  description = "PostgreSQL administrator username."
  type        = string
  default     = "venueopsadmin"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
