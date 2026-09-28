# Copy outside version control; these are examples, not usable targets.
environment    = "production"
location       = "nbg1"
server_type    = "cpx12"
ssh_public_key = "ssh-ed25519 REPLACE_WITH_PUBLIC_KEY"
# To reuse a registered key, remove ssh_public_key and set existing_ssh_key_id.
# existing_ssh_key_id = 123456
admin_cidrs = ["192.0.2.10/32"]
