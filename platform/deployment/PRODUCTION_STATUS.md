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

The owner independently confirmed the server's ED25519 fingerprint through the
Hetzner web console: `SHA256:Pc22yqh+TKgCxmiz7CjpFN72GbaaByyxjzni9WLP9Wk`.
The matching key was explicitly accepted into the protected local `known_hosts`;
subsequent SSH uses strict checking and the configured Hetzner private key.

Verified host results:
- Cloud-init: done; errors and recoverable_errors empty.
- Docker29.1.3 active; Compose2.39.4 installed.
- Empty-host memory: 1914MiB total, 1589MiB available; no swap.
- Root disk: 38GiB total, approximately34GiB available.
- /srv/agriplatform mode0750; /etc/agriplatform mode0700.
- Supabase Auth and GHCR HTTPS connections succeeded; unauthenticated endpoints
  returned expected401. Direct Supabase PostgreSQL TCP5432 connects over IPv6;
  no database login/query was performed.
- SSH permits public-key authentication and prohibits root password authentication.
- No application containers are running. Empty-host measurements do not establish
  capacity for the full stack or indicate application readiness.

The existing website remains on Netlify (`boabab.netlify.app` / scribeswell.com).
`api.scribeswell.com` has no DNS record yet. Netlify inspection confirmed site ID `e739718f-de86-4ad4-ab84-cf6249134558`, HTTPS
forced, linked to `Innodat/agriplatform` main. Native automatic builds are currently
**enabled**, publishing only `apps/scribeswell/web/dist` using
`npm --workspace scribeswell-web run build`. Before pushing the combined release,
stop native builds so the coordinated workflow is the sole deployment authority.
No setting was changed and no Git push has been performed.
The root SUPABASE_URL points to local development (localhost54321); the target guard
stopped inspection before any production request. The separately supplied production publishable key works: Auth settings are readable,
with public signup enabled and email autoconfirm disabled. Anonymous HEAD requests
to the five expected Bible tables using the scribeswell schema return406, so record
counts remain unverified; this does not prove the tables are absent. A privileged
read-only inventory requires the missing production secret key/database connection.
The owner created .env.prod with the production URL and publishable key; it is now
explicitly ignored along with credential-file editor swaps. Existing local development
credentials remain unchanged. NETLIFY_AUTH_TOKEN was used only for read-only inspection.

Terraform state is currently local in the git-ignored, mode0700 directory
`platform/deployment/.local/production-infrastructure`; state/log/plan files are
mode0600 and a local state backup exists. This first, single-operator bootstrap used
the explicitly approved saved local plan. It does **not** provide remote-state
locking, off-machine backup or encryption at rest. Establish protected durable state
storage before another operator or automation changes infrastructure; preserve the
current state and migrate it deliberately rather than initializing an empty state.
The API key is loaded from ignored .env and passed only through HCLOUD_TOKEN.

Next gates: production provider inspection, durable Terraform state,
CI SSH connectivity, TLS/domain configuration, scoped runtime/migration credentials,
then separately approved production schema/import and public activation plans.
