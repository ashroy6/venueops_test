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

variable "aks_subnet_id" {
  description = "AKS subnet ID."
  type        = string
}

variable "acr_id" {
  description = "Azure Container Registry ID."
  type        = string
}

variable "log_analytics_workspace_id" {
  description = "Log Analytics Workspace ID."
  type        = string
}

variable "tenant_id" {
  description = "Microsoft Entra tenant ID for AKS Azure RBAC."
  type        = string
}

variable "node_min_count" {
  description = "Minimum AKS node count."
  type        = number
  default     = 2
}

variable "node_max_count" {
  description = "Maximum AKS node count."
  type        = number
  default     = 6
}

variable "node_vm_size" {
  description = "AKS node VM size."
  type        = string
  default     = "Standard_D4s_v5"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}
