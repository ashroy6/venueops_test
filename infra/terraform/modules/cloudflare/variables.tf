variable "enabled" {
  description = "Whether Cloudflare resources should be managed."
  type        = bool
  default     = false
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID."
  type        = string
  default     = ""
}

variable "app_hostname" {
  description = "Application hostname."
  type        = string
}

variable "origin_hostname" {
  description = "Azure origin hostname."
  type        = string
}
