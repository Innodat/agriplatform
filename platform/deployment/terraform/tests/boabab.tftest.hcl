mock_provider "hcloud" {}
variables {
  environment = "production"
  location = "nbg1"
  admin_cidrs = ["192.0.2.10/32"]
  existing_ssh_key_id = 130603320
}
run "preserve_defaults" {
  command = plan
  assert {
    condition = hcloud_server.backend.name == "agriplatform-production" && length([for r in hcloud_firewall.ingress.rule : r if r.port == "22"]) == 1
    error_message = "Existing installations must retain their name and restricted SSH."
  }
}
run "boabab_private_access" {
  command = plan
  variables {
    wireguard_enabled = true
    server_name = "boabab"
    public_ssh_enabled = false
    private_ssh_verified = true
  }
  assert {
    condition = hcloud_server.backend.name == "boabab" && length([for r in hcloud_firewall.ingress.rule : r if r.port == "22"]) == 0 && length([for r in hcloud_firewall.ingress.rule : r if r.port == "443"]) == 1
    error_message = "Private access must remove public SSH while retaining HTTPS and the requested name."
  }
  assert {
    condition = hcloud_server.backend.user_data == file("cloud-init.yaml")
    error_message = "Renaming must not mutate server bootstrap data."
  }
}
run "reject_unverified_private_access" {
  command = plan
  variables { public_ssh_enabled = false }
  expect_failures = [var.public_ssh_enabled]
}
run "reject_invalid_name" {
  command = plan
  variables { server_name = "bad name" }
  expect_failures = [var.server_name]
}
run "rename_only" {
  command = plan
  variables { server_name = "boabab" }
  assert {
    condition = hcloud_server.backend.name == "boabab" && hcloud_server.backend.user_data == file("cloud-init.yaml") && length(hcloud_firewall.ingress.rule) == 2
    error_message = "Rename-only must preserve bootstrap and the default two firewall rules."
  }
  assert {
    condition = alltrue([for r in hcloud_firewall.ingress.rule : r.direction == "in" && r.protocol == "tcp" && (r.port == "22" ? toset(r.source_ips) == toset(var.admin_cidrs) : r.port == "443" && toset(r.source_ips) == toset(["0.0.0.0/0", "::/0"]))])
    error_message = "Default firewall must expose only restricted SSH and public HTTPS."
  }
}
run "wireguard_with_restricted_ssh" {
  command = plan
  variables {
    server_name = "boabab"
    wireguard_enabled = true
  }
  assert {
    condition = length(hcloud_firewall.ingress.rule) == 3 && alltrue([for r in hcloud_firewall.ingress.rule : r.direction == "in" && (r.protocol == "udp" ? r.port == "51820" && toset(r.source_ips) == toset(["0.0.0.0/0"]) : r.protocol == "tcp" && (r.port == "22" ? toset(r.source_ips) == toset(var.admin_cidrs) : r.port == "443" && toset(r.source_ips) == toset(["0.0.0.0/0", "::/0"])))])
    error_message = "Only public HTTPS, public IPv4 WireGuard and restricted SSH are allowed."
  }
  assert {
    condition = hcloud_server.backend.user_data == file("cloud-init.yaml") && hcloud_server.backend.name == "boabab"
    error_message = "VPN enablement and rename must preserve cloud-init."
  }
}
run "wireguard_without_public_ssh" {
  command = plan
  variables {
    wireguard_enabled = true
    public_ssh_enabled = false
    private_ssh_verified = true
  }
  assert {
    condition = length(hcloud_firewall.ingress.rule) == 2 && alltrue([for r in hcloud_firewall.ingress.rule : r.direction == "in" && (r.protocol == "udp" ? r.port == "51820" && toset(r.source_ips) == toset(["0.0.0.0/0"]) : r.protocol == "tcp" && r.port == "443" && toset(r.source_ips) == toset(["0.0.0.0/0", "::/0"]))])
    error_message = "Verified private access removes only SSH, retaining exact HTTPS and WireGuard rules."
  }
}
run "wireguard_is_not_verification" {
  command = plan
  variables {
    wireguard_enabled = true
    public_ssh_enabled = false
  }
  expect_failures = [var.public_ssh_enabled]
}

run "reject_all_ssh_paths_disabled" {
  command = plan
  variables {
    public_ssh_enabled = false
    private_ssh_verified = true
    wireguard_enabled = false
  }
  expect_failures = [var.public_ssh_enabled]
}
