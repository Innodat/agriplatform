# Production setup status — 28 September 2026

The owner approved the saved EUR11.99/month Hetzner plan with “yes, I approve, next.”
The exact saved plan was applied after rechecking the account prices and confirming
that no server existed. Terraform reported 2 additions, 0 changes and 0 deletions.
No DNS, database, collection import or public application deployment was performed.

## Provisioned host

- Server: `agriplatform-production`, Hetzner ID `167776264`.
- CPX12, Nuremberg (`nbg1`), Ubuntu24.04, 1 shared vCPU, 2 GB RAM, 40 GB disk.
- IPv4: `138.199.217.158`; IPv6: `2a01:4f8:1c1b:cb26::1`.
- Firewall ID `11693527`: HTTPS443 public over IPv4/IPv6; SSH22 restricted to the
  administrator's approved current public IPv4 /32 in the protected plan inputs.
- Existing SSH key `hetzner-ck-wsl` referenced without mutation.
- Paid host backups, volumes and load balancers are not enabled.
- Account API quote at apply: EUR11.49/month server + EUR0.50/month IPv4;
  account VAT0, IPv6 free. Usage extras and existing Supabase/Netlify/domain costs
  are separate. Hetzner reports server running and firewall applied.

## Verification and remaining work

Strict SSH handshake reached the host and rejected its unknown host key as intended.
Host fingerprint confirmation through Hetzner's trusted console is pending. Cloud-init
completion, Docker/Compose versions, disk/memory and remote administration therefore
remain unverified. The infrastructure being running is not application readiness.

The existing website remains on Netlify (`boabab.netlify.app` / scribeswell.com).
`api.scribeswell.com` has no DNS record yet. Netlify Git auto-build settings and
provider site metadata still require inspection. No Git push has been performed.

Terraform state is currently local in the git-ignored, mode0700 directory
`platform/deployment/.local/production-infrastructure`; state/log/plan files are
mode0600 and a local state backup exists. This first, single-operator bootstrap used
the explicitly approved saved local plan. It does **not** provide remote-state
locking, off-machine backup or encryption at rest. Establish protected durable state
storage before another operator or automation changes infrastructure; preserve the
current state and migrate it deliberately rather than initializing an empty state.
The API key is loaded from ignored .env and passed only through HCLOUD_TOKEN.

Next gates: trusted SSH identity, host bootstrap checks, durable Terraform state,
CI SSH connectivity, TLS/domain configuration, scoped runtime/migration credentials,
then separately approved production schema/import and public activation plans.
