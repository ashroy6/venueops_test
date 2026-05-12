resource "azurerm_public_ip" "app_gateway" {
  name                = "pip-appgw-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]
  tags                = var.tags
}

resource "azurerm_web_application_firewall_policy" "this" {
  name                = "wafpol-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  policy_settings {
    enabled                     = true
    mode                        = "Prevention"
    request_body_check          = true
    file_upload_limit_in_mb     = 100
    max_request_body_size_in_kb = 128
  }

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }

  custom_rules {
    name      = "BlockHighRiskMethods"
    priority  = 10
    rule_type = "MatchRule"

    match_conditions {
      match_variables {
        variable_name = "RequestMethod"
      }

      operator           = "Equal"
      negation_condition = false
      match_values       = ["TRACE"]
    }

    action = "Block"
  }
}

resource "azurerm_application_gateway" "this" {
  name                = "appgw-${var.name_prefix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  firewall_policy_id  = azurerm_web_application_firewall_policy.this.id
  tags                = var.tags

  sku {
    name = "WAF_v2"
    tier = "WAF_v2"
  }

  autoscale_configuration {
    min_capacity = 2
    max_capacity = 10
  }

  gateway_ip_configuration {
    name      = "appgw-ip-configuration"
    subnet_id = var.app_gateway_subnet_id
  }

  frontend_ip_configuration {
    name                 = "public-frontend"
    public_ip_address_id = azurerm_public_ip.app_gateway.id
  }

  frontend_port {
    name = "http-80"
    port = 80
  }

  backend_address_pool {
    name  = "aks-ingress-backend"
    fqdns = [var.backend_fqdn]
  }

  backend_http_settings {
    name                                = "http-settings"
    cookie_based_affinity               = "Disabled"
    port                                = 80
    protocol                            = "Http"
    request_timeout                     = 30
    pick_host_name_from_backend_address = true
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "public-frontend"
    frontend_port_name             = "http-80"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "default-route"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "aks-ingress-backend"
    backend_http_settings_name = "http-settings"
    priority                   = 100
  }

  probe {
    name                                      = "health-probe"
    protocol                                  = "Http"
    path                                      = "/health"
    interval                                  = 30
    timeout                                   = 10
    unhealthy_threshold                       = 3
    pick_host_name_from_backend_http_settings = true
  }
}
