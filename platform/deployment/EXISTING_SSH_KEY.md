---
title: Reuse the registered Hetzner SSH key for the first host plan
created: 2026-09-28
type: chore
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

The owner configured DEPLOY_SERVER_API_KEY in the ignored root .env and registered
an SSH public key in Hetzner. Prepare a read-only, single-production-host plan using
that existing key and the existing Netlify site. Terraform must reference an existing
key without recreating, renaming or owning it, while retaining new-key support for
other initial setups. Accept exactly one key input. No cloud apply, DNS change,
production database write or public deployment is authorized by this preparation.
</frozen-after-approval>

## Implementation Notes

Read-only inventory confirms no project servers and one registered key. CPX12 is
available in nbg1. Public HTTPS confirms Netlify serves scribeswell.com; API hostname
has no DNS record. Token is read with dotenv_values, passed only to provider requests
or HCLOUD_TOKEN environment, never interpolated into shell text, tfvars or output.
Use conditional data/resource references and a moved block for managed-key address
compatibility. Scope is Terraform inputs/tests and setup documentation. Scaffold:
existing-key input becomes reusable; no shared UI/agent-context/ADR decision change.
Prepare plan in an ignored local operational workspace; persistent remote-state
arrangements remain required before apply. Missing admin CIDR and Netlify linkage
are being clarified while reversible template work proceeds.


Completion 2026-09-28: existing key is a data source, with zero managed SSH-key
resources in the selected plan. New-key mode retains resource creation and a moved
block preserves its previous address. Exactly-one and positive-ID validations are
covered by mock provider tests. Explicit IPv4 and IPv6 are enabled per the owner's
request to assess cost/compatibility. No architecture decision changed.

Observed failing existing-key Terraform acceptance before implementation (missing
required ssh_public_key and undeclared existing_ssh_key_id). Afterward all five
`terraform -chdir=platform/deployment/terraform test -no-color` tests passed, covering
reuse, missing/invalid/ambiguous inputs, creation and dual-stack networking. Existing
34 deployment unit tests passed; fmt/check and diff checks passed. Independent
blind reviewer found no actionable issues and independently reran all five tests.

Read-only live Terraform plan succeeded in ignored .local/production-infrastructure:
2 create actions (hcloud_server.backend and hcloud_firewall.ingress), 0 modifications,
0 deletions, and no key import/mutation. Server: CPX12, nbg1, Ubuntu24.04, dual-stack,
backups false, registered key verified against local hetzner_ed25519.pub. Administrator
SSH /32 is the owner's approved current public IPv4; HTTPS443 is public. Actual
inputs and saved binary plan remain ignored with restricted filesystem permissions.
The token is absent from tfvars and provider token is supplied only in process env.

Hetzner API quote: EUR11.49 monthly server + EUR0.50 IPv4 = EUR11.99 monthly,
account VAT rate0, IPv6 free. No paid backups, volumes or load balancer selected.
Netlify boabab.netlify.app is user-confirmed; public scribeswell.com returns Netlify
HTTPS200. Git integration settings and authenticated Netlify site metadata remain
unverified. No DNS/host/database/site changes were performed. Secure persistent
Terraform state, CI SSH access arrangement, host/TLS/runtime secrets and first
bootstrap/activation approvals remain operational setup steps; plan is not apply.
