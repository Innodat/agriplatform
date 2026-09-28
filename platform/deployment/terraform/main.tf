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
variable "ssh_public_key" {
  type = string
  validation {
    condition     = can(regex("^ssh-(ed25519|rsa) ", var.ssh_public_key))
    error_message = "Supply an SSH public key, never a private key."
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
  name       = "agriplatform-${var.environment}"
  public_key = var.ssh_public_key
}
resource "hcloud_firewall" "ingress" {
  name = "agriplatform-${var.environment}"
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = var.admin_cidrs
  }
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}
resource "hcloud_server" "backend" {
  name         = "agriplatform-${var.environment}"
  server_type  = var.server_type
  location     = var.location
  image        = "ubuntu-24.04"
  ssh_keys     = [hcloud_ssh_key.admin.id]
  firewall_ids = [hcloud_firewall.ingress.id]
  user_data    = file("${path.module}/cloud-init.yaml")
  labels       = { environment = var.environment, platform = "agriplatform" }
  lifecycle { prevent_destroy = true }
}
output "ipv4" { value = hcloud_server.backend.ipv4_address }
output "ipv6" { value = hcloud_server.backend.ipv6_address }
