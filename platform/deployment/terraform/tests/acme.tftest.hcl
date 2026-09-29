mock_provider "hcloud" {}
variables {
  environment = "production"
  location = "nbg1"
  admin_cidrs = ["192.0.2.10/32"]
  existing_ssh_key_id = 130603320
}
run "default_no_http" {
  command = plan
  assert {
    condition = length([for r in hcloud_firewall.ingress.rule : r if r.port == "80"]) == 0
    error_message = "HTTP must remain opt-in."
  }
}
run "acme_only_adds_http" {
  command = plan
  variables { acme_http_enabled = true }
  assert {
    condition = length(hcloud_firewall.ingress.rule) == 3 && length([for r in hcloud_firewall.ingress.rule : r if r.port == "80" && r.protocol == "tcp" && r.direction == "in" && toset(r.source_ips) == toset(["0.0.0.0/0", "::/0"])]) == 1
    error_message = "ACME adds only public TCP80."
  }
  assert {
    condition = hcloud_server.backend.user_data == file("cloud-init.yaml") && hcloud_server.backend.name == "agriplatform-production"
    error_message = "ACME must preserve host configuration."
  }
}
