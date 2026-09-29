terraform {
  required_version = ">= 1.9, < 2.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.59"
    }
  }
}
# HCLOUD_TOKEN is read by the provider; never declare a token variable.
provider "hcloud" {}
variable "environment" {
  type = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Choose staging or production."
  }
}
variable "location" {
  type        = string
  description = "Explicit Hetzner location; initially evaluate nbg1 or fsn1 against Supabase Ireland latency."
  validation {
    condition     = length(var.location) > 0
    error_message = "A location is required."
  }
}
variable "server_type" {
  type        = string
  default     = "cpx12"
  description = "Initial 1 shared vCPU / 2 GB estimate; verify full-stack memory and load before activation."
}
variable "server_name" {
  type        = string
  default     = null
  description = "Optional host name override. Renames the existing resource without changing its Terraform address or bootstrap data."
  validation {
    condition     = var.server_name == null || can(regex("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", var.server_name))
    error_message = "Use a lowercase hostname of 1-63 characters."
  }
}
variable "private_ssh_verified" {
  type        = bool
  default     = false
  nullable    = false
  description = "Operator assertion backed by strict-host-key private SSH and deployment-path evidence; not automatic verification."
}
variable "acme_http_enabled" {
  type        = bool
  default     = false
  nullable    = false
  description = "Allow standalone ACME HTTP-01 on TCP80; public API remains HTTPS-only."
}
variable "wireguard_enabled" {
  type        = bool
  default     = false
  nullable    = false
  description = "Expose the existing host's WireGuard UDP51820 endpoint; never provisions a VPN secret or changes cloud-init."
}
variable "public_ssh_enabled" {
  type     = bool
  default  = true
  nullable = false
  validation {
    condition     = var.public_ssh_enabled || (var.private_ssh_verified && var.wireguard_enabled)
    error_message = "Enable WireGuard and verify private administrator and deployment access before removing public SSH."
  }
}
variable "ssh_public_key" {
  type    = string
  default = null
  validation {
    condition     = var.ssh_public_key == null || can(regex("^ssh-(ed25519|rsa) ", var.ssh_public_key))
    error_message = "Supply an SSH public key, never a private key."
  }
}
variable "existing_ssh_key_id" {
  type        = number
  default     = null
  description = "Registered Hetzner key to reference without taking ownership; alternatively supply ssh_public_key."
  validation {
    condition     = (var.existing_ssh_key_id != null) != (var.ssh_public_key != null)
    error_message = "Supply exactly one of existing_ssh_key_id or ssh_public_key."
  }
  validation {
    condition     = var.existing_ssh_key_id == null ? true : var.existing_ssh_key_id > 0 && floor(var.existing_ssh_key_id) == var.existing_ssh_key_id
    error_message = "The existing SSH key ID must be a positive integer."
  }
}
variable "admin_cidrs" {
  type = list(string)
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrhost(cidr, 0)) && try(tonumber(split("/", cidr)[1]) > 0, false)])
    error_message = "Supply restricted administrator CIDRs, not the entire internet."
  }
}
resource "hcloud_ssh_key" "admin" {
  count      = var.existing_ssh_key_id == null && var.ssh_public_key != null ? 1 : 0
  name       = "agriplatform-${var.environment}"
  public_key = var.ssh_public_key
}
moved {
  from = hcloud_ssh_key.admin
  to   = hcloud_ssh_key.admin[0]
}
data "hcloud_ssh_key" "existing" {
  count = var.existing_ssh_key_id != null ? 1 : 0
  id    = var.existing_ssh_key_id
}
resource "hcloud_firewall" "ingress" {
  name = "agriplatform-${var.environment}"
  dynamic "rule" {
    for_each = var.acme_http_enabled ? [1] : []
    content {
      direction  = "in"
      protocol   = "tcp"
      port       = "80"
      source_ips = ["0.0.0.0/0", "::/0"]
    }
  }
  dynamic "rule" {
    for_each = var.wireguard_enabled ? [1] : []
    content {
      direction  = "in"
      protocol   = "udp"
      port       = "51820"
      source_ips = ["0.0.0.0/0"]
    }
  }
  dynamic "rule" {
    for_each = var.public_ssh_enabled ? [1] : []
    content {
      direction  = "in"
      protocol   = "tcp"
      port       = "22"
      source_ips = var.admin_cidrs
    }
  }
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}
resource "hcloud_server" "backend" {
  name         = var.server_name != null ? var.server_name : "agriplatform-${var.environment}"
  server_type  = var.server_type
  location     = var.location
  image        = "ubuntu-24.04"
  ssh_keys     = var.existing_ssh_key_id != null ? [data.hcloud_ssh_key.existing[0].id] : [for key in hcloud_ssh_key.admin : key.id]
  firewall_ids = [hcloud_firewall.ingress.id]
  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
  user_data = file("${path.module}/cloud-init.yaml")
  labels    = { environment = var.environment, platform = "agriplatform" }
  lifecycle { prevent_destroy = true }
}
output "ipv4" { value = hcloud_server.backend.ipv4_address }
output "ipv6" { value = hcloud_server.backend.ipv6_address }
