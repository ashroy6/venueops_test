locals {
  cloudflare_note = var.enabled ? "Cloudflare enabled for ${var.app_hostname}" : "Cloudflare disabled for this environment"

  recommended_controls = {
    dns_record      = "Create proxied DNS record pointing app hostname to Azure Application Gateway public endpoint."
    waf_rules       = "Enable managed WAF rules and custom rules for API abuse protection."
    rate_limiting   = "Rate limit login, ingestion, and high-cost API paths."
    bot_protection  = "Enable bot protection for public web and API routes."
    ddos_protection = "Use Cloudflare edge DDoS protection before Azure origin."
    tls_mode        = "Use Full Strict TLS between Cloudflare and Azure origin."
    origin_lockdown = "Restrict Azure origin access to Cloudflare IP ranges where feasible."
    logpush         = "Send Cloudflare security/access logs to storage or SIEM."
    cache_policy    = "Cache static web assets and processed media where safe."
  }
}

# Safe design marker:
# The real Cloudflare DNS/WAF/rate-limit resources should be enabled only after
# the real Cloudflare account, zone, hostname, and origin strategy are known.
#
# This avoids committing fragile or fake Cloudflare config that validates locally
# but is wrong for the actual account.
resource "terraform_data" "cloudflare_design_marker" {
  input = {
    enabled              = var.enabled
    cloudflare_zone_id   = var.cloudflare_zone_id
    app_hostname         = var.app_hostname
    origin_hostname      = var.origin_hostname
    note                 = local.cloudflare_note
    recommended_controls = local.recommended_controls
  }
}
