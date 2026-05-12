provider "azurerm" {
  features {}
}

provider "cloudflare" {
  # Authentication is expected through CLOUDFLARE_API_TOKEN.
  # Cloudflare resources are enabled only when cloudflare_enabled = true.
}
