# Production setup status — 28 September 2026

## Current state

The existing Hetzner host is now **boabab** (same server ID, disk and IPs).
Operator `ssh boabab` works over WireGuard at 10.77.80.1; only that /32 uses the
tunnel. Default SSH cryptography and the independently verified host key are
retained. MTU1200 resolved the observed packet-size stall; 4 MiB transfers in each
direction matched SHA256, and SSH reconnected after restarting the server tunnel.
The user persisted the client MTU fix. UDP51820 is public; TCP22 remains restricted
as a fallback; removing it remains a separate guarded infrastructure change. CI has separate VPN
and SSH keys; its SSH public key is restricted to 10.77.80.3 with forwarding disabled.
Nine CI inputs are uploaded to GitHub’s existing `Production` environment and their names verified; the environment now permits only branch `main`. The hosted connectivity check passed, including cleanup (run 36480376365). No Mac Mini or Tailscale changes.

The previously approved additive Supabase bootstrap **completed successfully**:
seven restricted roles, access/content/pts owner migrations, Scribeswell schema
and migration history entry, and private `pts-private` bucket (128 MiB limit).
Heads: access_0001, content_0004, pts_0001. All seven role logins passed; none is
superuser or bypasses RLS. Business table RLS checks passed (forced for owned
access/content/pts tables). Existing legacy row counts/digests matched the rehearsal
and were unchanged after migration. No poems, Bible corpus, accounts, invitations,
PtS organization or memberships have been imported/created. No DNS or public
application activation occurred. Netlify native builds are now paused and only
the isolated connectivity workflow/helpers have been published to main.

Evidence: ignored `production-bootstrap-apply.json`, `production-owner-migrations.json`,
`wireguard-private-check.json` and protected bootstrap/recovery artifacts. Credentials
remain in ignored protected files; do not attach them to issues or workflow artifacts.

Remaining CI variables/secrets are configured and verified (see preparation record
below). Seven root-only configuration files are installed on boabab without starting
services. Next: API DNS and TLS, registry pull authorization, then Auth/Storage/data
and account verification before approving first activation. Imports, account
provisioning, DNS, public SSH removal and public release still require their approved
execution steps. Netlify native builds are paused; its served deployment is unchanged.
The frontend build filter is tested locally but not yet published.

## Provisioning and earlier preparation history

The following records describe the state at each earlier step; the current state
above supersedes earlier absence/pending statements.

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
  later authenticated inspection used an SSH tunnel and enforced read-only transactions.
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
to the five expected Bible tables using the scribeswell schema returned406;
subsequent privileged inspection confirmed that the scribeswell schema is absent.
The owner created ignored `.env.prod` with production `SUPABASE_URL`, public key,
`SUPABASE_SECRET_KEY` and **`DATABASE_URL`** (not `PRODUCTION_DATABASE_URL`). Local
development credentials remain unchanged. Netlify credentials were used read-only.

### Authenticated database and storage inventory

Verified against project `gjbsnxmbhxsvcblzgfts` on 28 September 2026, using a
strictly verified SSH tunnel through the provisioned host because the direct local
connection was unavailable. PostgreSQL confirmed `transaction_read_only=on`;
queries had bounded statement/lock/connect timeouts. No mutations were executed.
Selected metadata is saved in ignored `supabase-private-inventory.json` beside the
protected infrastructure state; no credentials or business record bodies are recorded.

- Existing application schemas: `identity`, `cs`, `finance`; preserve them and their data.
- Identity counts: 2 organizations, 3 users, 1 membership, 1 member role,
  46 role permissions and 49 audit entries. No organization named PtS exists.
- Eleven Supabase migration versions are recorded, from `20250815110000` through
  `20250815220000`. This inventory is not a full schema-drift comparison.
- `access`, `content`, `pts` and `scribeswell` are absent; no matching service roles
  or owner Alembic histories exist. Both application collections need initial import.
- The identity bridge's required organization/member ID and deletion columns exist.
  The custom Auth hook function exists; its activation remains unverified.
- Identity business tables have RLS enabled. The legacy audit table does not;
  `authenticated` has INSERT/UPDATE grants on it. Review effective exposure and
  compatible hardening before first release; do not silently change historical grants.
- Existing bucket `content_kok-home_dev` is private, limited to 52,428,800 bytes
  (50 MiB), with no objects recorded. Preserve it. Create a separate `pts-private`
  bucket with a 134,217,728-byte (128 MiB) limit after approval; the global limit
  still needs verification. Content S3 credentials passed an authenticated ListBuckets
  request against this project in eu-west-1; `pts-private` is absent. No S3 writes
  were performed. Evidence: ignored `supabase-s3-inventory.json`.

### Target-specific initial release sequence — pending approval and evidence

1. Establish a recent production recovery point and verify restoration before writes.
   Complete compatibility review against existing identity, cs and finance consumers.
2. Add separate owner/runtime/import roles and restricted login credentials, adapting
   `apps/pts/tools/bootstrap_roles.sql` to this existing hosted project: grant the
   migrator roles to the provisioning administrator before assigning schema ownership.
   Keep administrator and migrator connections out of runtime services.
3. Apply the identity-owner access bridge and only the missing Scribeswell SQL
   migration `20260614000000`. Do not replay the existing platform migrations or
   run the composed Expense SQL/legacy deploy-and-seed scripts. Coordinate owner
   migrations in the established access → content → PtS order with release evidence.
4. Create PtS / Psalms that Sings from the committed organization manifest; resolve
   the intended production account and add explicit membership and the three PtS
   Reader permissions. Never copy local account IDs or passwords.
5. Configure the new private bucket, Content-only S3 credentials, Auth callbacks for
   scribeswell.com and the reviewed Auth hook/schema exposure. Public signup is
   currently enabled; changing it requires accounting for existing consumers.
6. Import the existing canonical poetry material and checked-in Hebrew corpus through
   their owner tooling. Verify baseline counts, repeatability, protected source access,
   signed transfers and prior identity behavior before accepting bootstrap evidence.
7. Configure CI credentials, trusted SSH access and DNS/TLS for api.scribeswell.com.
   Disable Netlify native builds before pushing; the coordinated production workflow
   must be the sole activation path. Approve concrete provider changes and release
   identity before any database writes, DNS changes or public activation.

Production S3 access key/secret were supplied in ignored `.env.prod` as
`CONTENT_S3_ACCESS_KEY` / `CONTENT_S3_SECRET_KEY` and verified read-only. Pending
operator inputs were subsequently supplied; see the dated updates below.
A backup's existence alone is not evidence of tested restoration. No approval for
these production mutations is inferred from supplying credentials.

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

### Local preparation recheck

- `apps/pts/.local/venv/bin/python -m apps.pts.tools.verify_archive`: passed;
  all 264 files (222,505,940 bytes) match the committed archive manifest. Counts:
  312 poems, 190 with text, 33 assistant-checked, 275 witnesses, 19 sources and
  19 rights records. No import performed.
- `python3 tools/py/run_compose_supabase.py --check-only`: passed; no files changed.
  Composition still includes Expense migrations and seeds; this does not authorize
  applying that composition to production.

### Owner-confirmed backup and upload ceiling

The owner reports a successful Supabase backup at `2026-09-28T02:37:50.531Z`.
Restoration has not been tested. The dashboard's global file-size limit is currently
50 MB, restricted by the enabled spend cap; no billing or storage setting was changed.
Measured source folder: 247 files / 212,816,529 bytes; its 9 PDFs total
191,263,367 bytes, with the largest PDF 89,237,181 bytes (85.1 MiB).
The owner requested cost clarification before changing the spend cap.

### Connectivity and operator updates

The owner confirmed updating the spend-cap/global-upload settings as recommended
and authorized `kristov.kok@gmail.com` as the initial production PtS Reader account.
Provider-side global-limit verification is still pending; the project API/S3 keys
cannot read organization billing settings.

The workstation public IPv4 changed. Under the existing authorization to allow this
machine's current address, a saved Terraform plan replaced the SSH source /32 only.
The plan had one in-place firewall update, no server changes/additions/deletions;
HTTPS ingress remained unchanged. Apply succeeded and strict-host-key SSH passed.
Protected plan, apply log and pre-change state are retained alongside the existing
state. No infrastructure price change. Production database writes remain unapproved.

### Restore and migration rehearsal completed

A protected read-only snapshot of production `auth`, `identity`, `cs`, `finance`
and `supabase_migrations` was captured (226,245 bytes, SHA256
`e5a35e735d5321929e97a644f65ae34c60f6ae770f90d20b792fb715c7157bb6`).
It was restored with original grants and constraints, but without restoring original
object ownership, into `release_rehearsal_20260928` inside the existing local Supabase
instance. Database CONNECT is revoked from PUBLIC. The normal local development
`postgres` database and production data were not changed. Snapshot and rehearsal
contain sensitive Auth/business data and remain in the protected ignored workspace.

This is a selected-schema logical recovery rehearsal, not a full hosted-project,
provider backup, Storage-object or original-owner restoration test. The provider's
successful backup timestamp is separately recorded above. Original-owner restoration
and full hosted recovery remain limitations; ordinary initial deployment recovery is
stop activation, preserve applied additive schemas and correct forward. Never use
this partial snapshot to overwrite a live hosted project or automatically downgrade.

The existing owner coordinator succeeded twice against the restored copy, in
access → content → PtS order: access_0001, content_0004, pts_0001. Scribeswell SQL and
the identity bridge also applied successfully. Counts and row-content digests across
all 42 restored tables matched before/after both migration runs. Anonymous,
authenticated and Content runtime database roles were denied direct poem SELECT;
PtS runtime/import roles had their intended access. Runtime/import roles are neither
superusers nor RLS-bypass roles, and owned business tables force RLS. These empty-table
role checks do not replace post-import organization-isolation/provider tests.

The approved email `kristov.kok@gmail.com` has no production Auth account. Account
creation/invitation and organization membership are still pending; no email sent.

### Approved and completed: additive database bootstrap and private bucket only

Target: production Supabase project `gjbsnxmbhxsvcblzgfts`.
Code: `48e4b3c442f94fa53825fdb9387127d726ea21ba`; exact SQL/coordinator/migration
hashes and private bucket request are recorded in the protected
`recovery/bootstrap-approval-manifest.json` (approval recorded; execution succeeded).

Approved mutations (now completed):
1. Create seven restricted roles: pts_migrator, pts_runtime, pts_import,
   access_migrator, access_runtime, content_migrator, content_runtime. Generate
   separate credentials locally and store them only in protected deployment secrets.
   Grant the three migration roles to the provisioning administrator so it can
   assign their schema ownership; never grant migrator roles to runtime logins.
2. Create the access/content/pts owned schemas, revoke PUBLIC schema access, apply
   the narrow identity read bridge, and run the reviewed owner migrations through
   the existing ordered coordinator. The hosted bootstrap SQL adds the administrator
   role-membership grant before schema ownership assignment. The local rehearsal
   reused existing local roles and did not mutate global local role definitions.
3. Apply only Scribeswell's `20260614000000` schema migration and record its version
   in the existing Supabase migration history. Preserve all existing migration rows.
4. Create private bucket `pts-private`, limit 134,217,728 bytes. Preserve the existing
   bucket and its limits. If the provider rejects the configured global limit, stop;
   do not change billing/global settings or silently reduce the document requirement.

Before writes, recheck the target, hashed input files, absence of conflicting
roles/schemas/bucket, recovery artifacts and legacy baseline. Stop on any unexpected
state. Record each owner result and actual migration heads. Afterward compare
legacy data, inspect new grants/RLS and verify private bucket metadata. On failure,
block activation and reconcile committed steps; never delete existing data or apply
an automatic downgrade. No content imports, Auth changes/invitations, account grants,
DNS changes, Netlify changes, Git push or public activation are included in this approval.

Evidence files: recovery/snapshot-report.json, restore-report.json,
owner-migrations-1.json, owner-migrations-2.json, migration-rehearsal-report.json,
permission-check.json and baseline-digests.json (all ignored and protected).


### GitHub configuration and completed connectivity publication

The supplied fine-grained PAT configured the existing Production environment
(ID9903880451), restricted to branch `main`. Nine WireGuard/SSH inputs were encrypted
with its public key, uploaded and verified by metadata. The PAT was not uploaded.

User approval “Ok, next” authorized pausing native Netlify builds and publishing
only the manual connectivity workflow plus common.py/runner.py. The initial commit
`cf5b95e1a218ce1ca367bd7c2031a4f5fb26f3b3` passed hosted SSH but failed cleanup
(run 36477990203): Ubuntu accepted link-add's alias argument without installing
an ownership label. Reproduced in an isolated Ubuntu network namespace. Corrected
setup explicitly sets the alias before installing tunnel keys/bringing up the link.
The fixture now models that actual behavior; its regression failed before the fix.

The one-file fix `4cffad16ddf4dcb1bd658a0093c67431072dad7e` was published separately.
[Hosted run 36480376365](https://github.com/Innodat/agriplatform/actions/runs/36480376365)
passed connection, strict SSH and always-run cleanup. All 78 Python deployment tests
passed; actual Ubuntu namespace teardown also verified interface removal, secret
removal and repeat cleanup. Published history is merged into local main; no force push.

Netlify native builds are stopped (`build_settings.stop_builds=true`), with build
command/directory/repository settings preserved. Published deployment
`6aba06e3dac3132bd6edcc1a` remains unchanged. Full application release changes and
frontend build filtering are still local. No imports, accounts, DNS or application
activation occurred during this connectivity publication. Restricted public SSH
remains available pending its separately guarded removal.

Protected evidence: connectivity-publication-plan-initial.json,
connectivity-publication-plan.json, connectivity-netlify-pause.json,
connectivity-dispatch.json and connectivity-runs.json. Do not publish secret files.


### Application configuration preparation (2026-09-28)

User “next” authorized continuation with release settings. Added and verified GitHub
Production secrets `PUBLIC_SUPABASE_KEY`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`;
variables `PUBLIC_SITE_ORIGIN=https://scribeswell.com`,
`PUBLIC_API_ORIGIN=https://api.scribeswell.com`,
`PUBLIC_SUPABASE_URL=https://gjbsnxmbhxsvcblzgfts.supabase.co`. No workflow dispatched.

Prepared six owner-specific environment files with existing restricted role URLs
and separately generated service keys. Validated role/project binding, migration
separation and exact-origin CORS using real host preflight. Installed them under
`/etc/agriplatform/production` (0700, files0600) and installed root-only
`/etc/agriplatform/production.json`, without overwriting different existing files.
Secret values travel only in authenticated SSH stdin and remain ignored locally.
No containers started, database changed, import performed or release published.
No bootstrap approval assertion was created: actual Auth/Storage verification remains.

Production public JWKS advertises ES256. Fixed manifests that incorrectly required
legacy JWT signing secret; runtime verifier unchanged. 79 deployment tests, 14 Auth
tests and five local real container health checks passed. See
[optional JWT delivery record](OPTIONAL_JWT_CONFIGURATION.md).

Read-only host check found no existing TLS certificate or registry credentials.
API hostname was not resolvable. Next DNS record for operator setup:
`api.scribeswell.com A 138.199.217.158` (TTL300 or provider default); keep apex/www
Netlify records unchanged and omit AAAA until IPv6 service verification. Then prepare
ACME DNS-01 challenge and certificate/renewal process under explicit authorization.
GHCR pull authorization must also be configured before image activation; a working
SSH tunnel alone does not grant registry access.

Protected evidence/tools: release-github-settings.json, release-settings-report.json,
release-settings-installed.json, prepare-release-settings.py, check-release-settings.py,
install-release-settings.py and release-settings/ (contains credentials; never publish).
