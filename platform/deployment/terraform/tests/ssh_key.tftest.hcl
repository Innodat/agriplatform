mock_provider "hcloud" {}

variables {
  environment = "production"
  location    = "nbg1"
  admin_cidrs = ["192.0.2.10/32"]
}

run "reuse_registered_key" {
  command = plan
  variables {
    existing_ssh_key_id = 130603320
  }
  assert {
    condition     = length(hcloud_ssh_key.admin) == 0
    error_message = "An existing key must not create or manage a key resource."
  }
  assert {
    condition     = length(hcloud_server.backend.ssh_keys) == 1 && contains(hcloud_server.backend.ssh_keys, tostring(var.existing_ssh_key_id))
    error_message = "The host must reference exactly the selected registered key."
  }
  assert {
    condition     = one(hcloud_server.backend.public_net).ipv4_enabled && one(hcloud_server.backend.public_net).ipv6_enabled
    error_message = "The initial plan must retain IPv4 and IPv6 connectivity."
  }
}

run "reject_missing_key" {
  command         = plan
  expect_failures = [var.existing_ssh_key_id]
}

run "reject_invalid_key_id" {
  command = plan
  variables {
    existing_ssh_key_id = -1
  }
  expect_failures = [var.existing_ssh_key_id]
}

run "reject_ambiguous_key" {
  command = plan
  variables {
    existing_ssh_key_id = 130603320
    ssh_public_key     = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA fixture"
  }
  expect_failures = [var.existing_ssh_key_id]
}

run "create_new_key" {
  command = plan
  variables {
    ssh_public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA fixture"
  }
  assert {
    condition     = length(hcloud_ssh_key.admin) == 1
    error_message = "A supplied new public key must retain key creation support."
  }
}
