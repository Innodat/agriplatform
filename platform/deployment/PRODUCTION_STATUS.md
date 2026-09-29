# Production setup status — 29 September 2026

## Current state

As of 29 September 2026, boabab is provisioned on Hetzner and reachable through
WireGuard. API DNS/TLS and automatic certificate renewal are verified. Native
Netlify builds are paused; the existing served website is unchanged and the full
platform release has not been pushed or activated. CI connectivity passed, but the
first coordinated application release remains pending.

The Supabase owner migrations and private storage bucket are prepared. The PtS
organization, confirmed reader account and three reader grants exist. The canonical
poetry import and its replay passed (312 poems, 190 with text, 33 assistant-checked,
19 sources, 275 witnesses); ten existing source documents were uploaded and reused
on replay. Copyright and verification distinctions remain preserved.

The approved Scribeswell direct PostgreSQL transition is complete: restricted
runtime/import roles, targeted legacy function permission correction and protected
server configuration are verified. The canonical Hebrew import, separate full audit
and repeat import passed with zero errors and unchanged row/ID digests: 39 books,
929 chapters, 23,213 verses, 306,785 words and 471,674 morphemes. Read-only FastAPI
checks against production data passed. Temporary import containers and credential
files are gone; the runtime configuration is mode0600 and contains no broad service
key. Recovery configuration and ACL evidence remain protected.

Remaining gates are actual issued-session/Auth and signed-document acceptance,
container runtime networking and coordinated release verification, then separately
approved public API/frontend activation and removal of unnecessary Data API schema
exposure. No schema exposure was changed during the database transition. Protected
operation reports live in the ignored production-infrastructure directory; never
attach secrets or raw configuration to workflow artifacts or issues.

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


### DNS and HTTPS certificate prepared (2026-09-28)

Both Dynadot authoritative nameservers now return `138.199.217.158` for
`api.scribeswell.com`; the earlier missing-digit record was corrected by the owner.
Both nameservers verified the owner's manual DNS-01 TXT challenge before submission.
Let’s Encrypt issued the certificate after the approved account registration using
`kristov.kok@gmail.com` as contact. Certificate expiry: **2026-12-27 20:00:35 UTC**.

Verified hostname, trusted certificate chain, matching private key and more than
30 days remaining. Root-only certificate/key copies installed at
`/etc/agriplatform/tls/production/{fullchain.pem,privkey.pem}` (files0600,
directory0700), matching the prepared target configuration. Original Certbot
certificate lineage remains in `/etc/letsencrypt/live/api.scribeswell.com`.
Certificate SHA256: `219b70015458f4b2228cea62e885548b131ab6030404e23393d8921699046840`.
No certificate/private-key contents exported; no APIs or gateway started.

**Historical status, superseded by automatic renewal verification below.** The initial manual setup required renewal before expiry, with a
recommended operational target of **2026-11-27**, using the documented Certbot
DNS-01 command and a fresh temporary TXT challenge. After renewal, validate and
replace the external certificate/key copies, rerender/reload the gateway and
verify the publicly served certificate as documented in README. Certbot renewal
alone does not refresh these copies or the generated APISIX configuration.
No reminder or unattended DNS/renewal hook is configured. The completed challenge
TXT can now be removed by the owner. Protected evidence: tls-challenge.json.

Next: establish GHCR pull authorization, then complete the remaining approved
Auth/data/content checks and first-release activation plan. Public HTTPS service
availability is not claimed merely because certificate issuance succeeded.


### Automatic renewal and first-content preflight (2026-09-29)

Automatic HTTP-01 renewal is now configured. Both Certbot and certificate adoption
timers are enabled/active; staging reconfigure and renewal with deploy-hook dry-run
passed. Existing certificate is unchanged and valid through 2026-12-27. The hook
reported expected pending gateway activation; no application containers started.
See [verified operational evidence](AUTOMATED_OPERATIONS.md). Temporary GHCR
workflow-token transport is implemented/tested; actual hosted pull awaits release.

Read-only production preflight found no PtS organization, intended reader account,
poems, sources, witnesses, grants or private source objects. The pts-private bucket
is private with limit 134217728 bytes. Email login is enabled; public signup is still
enabled and needs disabling for the agreed administrator-provisioned setup. Asked
the owner to create kristov.kok@gmail.com in production with a new private password
and confirmed email; local credentials are not reused. Organization membership and
PtS read/export/document grants remain a separate controlled provisioning step.
Auth Site URL, redirect allowlist, custom token hook and mail delivery still need
verification; no bootstrap authorization assertion has been created.

Archive verification: `apps/pts/.local/venv/bin/python -m apps.pts.tools.verify_archive`
passed: 264 files / 222505940 bytes; canonical 312 poems / 190 texts / 33 checked /
275 witnesses / 19 sources / 19 rights. Hebrew validation: `apps/scribeswell/.local/venv/bin/python
apps/scribeswell/scripts/seed.py --dry-run` passed with 39 books, 929 chapters, 23213 verses,
306785 words, 471674 morphemes, zero errors. These commands made no production writes.
No collection imports, account writes by the agent, or public app publication occurred.
Protected read-only inventory: release-readiness.json; source validation output:
/tmp/boabab-bible-dry-run.log.

The read-only inventory also confirmed all five Scribeswell corpus tables are empty.


### Production reader provisioned (2026-09-29)

Owner created the production account; read-only check verified public signup is
disabled and found email initially unconfirmed. The explicitly approved provisioning
operation created organization PtS (slug pts, description Psalms that Sings), linked
the existing active identity profile as a non-owner member and granted exactly
pts.poetry.read, pts.poetry.export and pts.poetry.documents. No platform/legacy
administrator role was granted. Supabase admin API confirmed the existing account
and selected PtS via current_org_id while preserving other metadata and password.
No confirmation email was sent. Production identifiers and operation evidence remain
in ignored protected pts-reader-plan.json, pts-reader-apply.json and
pts-reader-verify.json; credentials and session tokens are not included in reports.

Independent read-only verification confirmed the membership, exact grants, email
confirmation, and identity.custom_access_token_hook output for this user/organization
(including member_id and absence of owner/admin claims). Calling the database
function does not establish that hosted Auth has enabled it. Asked owner to verify
Auth Site URL https://scribeswell.com, exact root redirect https://scribeswell.com/
and enabled Custom Access Token hook identity.custom_access_token_hook; preserve
redirects needed by other existing apps. Management API credentials are unavailable.

No imports or application publication were performed in this step. Provisioning is
additive and conflict-checked, with a short database transaction followed by an
idempotent Auth update outside that transaction. On a partial failure, reconcile
the protected report and rerun; do not reverse unrelated identity data.


### Canonical poetry imported (2026-09-29)

After owner confirmation of hosted Auth settings, an explicitly approved restricted
pts_import operation imported the verified canonical library into the production
PtS organization. All 663 catalogue/metadata rows were inserted without conflicts:
312 poems, 190 with text, 33 assistant-checked complete transcriptions, 275 witnesses,
19 sources and 19 rights records. Every stored payload equals the canonical source.
A second import replay inserted zero rows and reported zero conflicts. No alternative
SQLite/JSONL export was imported, and no collected text was changed. Protected
evidence: collection-import-plan.json and poetry-import-result.json.

The existing Bible importer cannot yet access hosted PostgREST: read-only preflight
returned HTTP406/PGRST106, with exposed schemas limited to public and graphql_public.
Asked owner to add identity and scribeswell while retaining existing exposed schemas;
pts, access and content must remain unexposed. All five Bible tables remain empty.
No public application release has been activated. Ten existing documents are being
transferred through the private Content owner in a separately approved operation;
do not claim upload completion until document-import-result.json is verified.


### Private documents uploaded and verified (2026-09-29)

Explicitly approved upload completed for all ten files already collected in the
archive sources folder: 191609122 bytes total, largest 89237181 bytes. The existing
Content service ran temporarily on loopback only, using content_runtime and an
organization-bound ephemeral import key. Each storage copy was hash/size verified
by the provider before readiness and catalogue association. All ten PtS attachments
were verified; a repeat pass reused every content identity. Missing credentials and
wrong-organization requests returned 403. The temporary service and tunnel stopped
and the import key was not installed on the production server. Staging objects are
retained according to the existing upload lifecycle; no cleanup was improvised.
Evidence: document-import-plan.json and document-import-result.json (protected).

Owner reports exposing identity and scribeswell in Data API. Explained existing
backend database access: browser -> FastAPI -> Supabase Data API for Scribeswell
and platform identity directory; browser business-data calls remain FastAPI only.
PtS/access/content use direct PostgreSQL. Production API reachability verification
is still in progress; no Hebrew import or public activation claimed.

Unauthenticated public Storage requests for both a staging and sealed copy returned
HTTP400, with no document download; private-document-access-check.json records
statuses only. Signed-download expiry and live user revocation checks remain part
of release acceptance. Recheck still returned PGRST106 for both schemas; asked
owner to verify Exposed schemas (not Extra search path), correct project and Save.

### Scribeswell direct PostgreSQL transition — 29 September 2026

The owner explicitly approved the transition after local implementation/review
(`163467a`). The targeted `public.get_user_roles()` correction is applied: PUBLIC
execute revoked, authenticated/service_role execute preserved. Two new restricted
roles are installed and actual login/RLS/owner-isolation checks passed. Runtime
cannot write, importer cannot delete, neither can access identity/PtS/content or
execute the legacy role-lookup function. Protected Scribeswell server configuration
now uses its runtime PostgreSQL URL; the broad Supabase service key was removed.
Prior configuration and function ACL evidence are retained in protected storage.

The first bootstrap guard rejected unreachable PUBLIC SELECT grants on Supabase
extension statistics. Role creation rolled back. A focused failing acceptance test
reproduced this; the corrected guard requires schema USAGE for effective PUBLIC
table access and continues to reject all explicit cross-owner role table grants.
All 48 Scribeswell tests passed before retry; the approved role transition then
succeeded. No extension grants were revoked to bypass the check.

The canonical corpus import, separate read-only audit and full repeat import all
completed with zero errors. Counts are 39 books, 929 chapters, 23,213 verses,
306,785 words and 471,674 morphemes. All five table digests (including IDs and full
row contents) were identical after verification and replay. A slow local import
was stopped, with unfinished chapter rollback, and
resumed through a one-off non-root, read-only container on boabab using only import
credentials, no listener and no published ports. Transferred image rootfs layers,
runtime configuration and architecture match the locally smoke-tested image;
Docker omitted empty legacy fields on import, yielding a different image ID.
No public application deployment, Git push or Data API schema unexposure occurred.


Read-only FastAPI acceptance against production using the runtime role passed:
anonymous book listing, Genesis chapter list, Psalm 119 (176 verses/1,067 words),
morphology, lexicon, occurrence pagination/filtering and missing-book 404. This used
an in-process test client, not a publicly activated API. PtS still has 312 poems,
19 sources, 275 witnesses and 3 reader grants; the private 128 MiB bucket and confirmed
reader account remain unchanged, and public signup remains disabled. Existing 20
storage objects represent the previously uploaded 10 documents' staging/sealed copies.

Evidence is protected under the production-infrastructure directory:
`scribeswell-transition-applied.json`, `scribeswell-image-transfer.json`,
`scribeswell-import-result.json`, `scribeswell-verify-result.json`,
`scribeswell-replay-result.json`, and `scribeswell-http-check.log`.
Source SHA256 remains `c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498`.

Remaining release gates: final actual Auth/Storage acceptance, host runtime-network
and coordinated release checks, then separately approved public API/frontend
activation and removal of unnecessary Data API schema exposure. Native Netlify
builds remain paused. No public release or complete production-readiness claim is
made by the successful database transition.

Final host check passed: temporary job and import credential file absent; runtime
configuration mode0600, correct restricted role, no broad service keys, protected
prior configuration retained (`scribeswell-host-check.json`).

### Container connectivity and issued Auth claims (2026-09-29)

Read-only tests using the release-check Scribeswell image on boabab found direct
PostgreSQL unreachable from the default IPv4-only Docker bridge, while Auth HTTPS
was reachable. The identical probe on an owned disposable dual-stack bridge connected
to PostgreSQL in0.31s and reached Auth; its container and network were removed.
Generated runtime and migration network changes are under local review; no public
application activation or push occurred.

Owner corrected hosted Auth Site URL to https://scribeswell.com. A temporary
no-email magic-link session verified that redirect and the existing confirmed user's
identity, but issued tokens lacked org_id and member_id. The collection/PDF acceptance
probe stopped before any private API access. Its own session was signed out and its
refresh token rejected afterwards. The owner was asked to enable the existing
identity.custom_access_token_hook in Authentication → Hooks. No passwords changed;
no token or signed URL was retained in evidence. Mail delivery and full Auth/Storage
release acceptance remain unverified.

Dual-stack preparation completed local review: 110 deployment tests and actual
local gateway smoke passed. Migration cleanup now proceeds despite evidence-save
failures. Existing uncertain migration outcomes still require operator reconciliation;
a durable retry gate is tracked as follow-up. Public release remains blocked.

### Issued Auth and private document acceptance passed (2026-09-29)

After the owner enabled identity.custom_access_token_hook, a newly issued temporary
production session contained the expected organization and member claims without
owner/admin privileges. The configured redirect remained https://scribeswell.com.
The real Auth identity and shared app-directory session passed verification.
Private loopback FastAPI processes used the production restricted database roles
through the trusted boabab tunnel; no public application was activated.

The acceptance probe verified 312 catalogue records,190 with text and33 checked
transcriptions; title search and all available filter categories; poem citations;
filtered JSON/text exports;19 sources and19 rights records. Anonymous and wrong-org
requests were denied for poems, sources, exports and documents. The smallest existing
source PDF downloaded twice within its 300-second signed URL lifetime and matched
the canonical file SHA256. After the real lifetime plus a10-second margin, Storage
rejected the same URL with HTTP400. No URLs, tokens or protected content were logged.

The temporary session was signed out locally and its refresh token was rejected;
all private services and the SSH tunnel stopped. No password changes or emails.
Safe evidence: ignored production-auth-document-acceptance.json; every recorded
verification boolean is true. The probe's initial handling of nullable local_path
was corrected before this successful run; no source material changed.

This verifies issued claims, shared API session, protected collection access and
read-link expiry/replay, not the entire first-release checklist. Live permission
revocation, signed upload expiry/replay, password/recovery mail delivery and final
browser/public-origin activation checks remain outstanding. The bootstrap assertion
remains absent and the public release remains blocked until required evidence and
concrete activation approval are complete.

### Approved final acceptance checks (2026-09-29)

The owner approved the temporary document-permission test, isolated storage
canaries and one recovery email. The existing pts.poetry.documents grant was
backed up with its identity and attribution, removed briefly, and restored exactly.
New PDF issuance returned 403 while revoked; catalogue access remained 200. An
already-issued PDF URL remained valid inside its 300-second lifetime and was denied
after actual expiry. Restored PDF issuance succeeded. The temporary Auth session
was signed out, its refresh token rejected, and private test services stopped.
Safe evidence: document-permission-revocation.json and
production-auth-document-acceptance.json under the ignored operational directory.

Supabase accepted exactly one recovery request and the owner confirmed email
delivery. The link was not consumed and the password was not changed. Actual
live-origin password sign-in and user-driven password change are not claimed here.
Recovery UI/browser behavior was separately verified with fixtures: 24 desktop/mobile
login/recovery tests and 11 cross-application session tests passed. The assembled
production-configured frontend browser test passed, including nested assets, direct
reader navigation and the external API endpoint. All 13 deployment JavaScript tests,
manifest contracts and dry-run Supabase composition passed. JavaScript tests needed
an unrestricted subprocess environment; the initial sandbox invocation failed.

Read-only production reinspection confirmed 312 poems, 19 sources, 275 witnesses,
three access grants, 39 books, 929 chapters, 23,213 verses, 306,785 words and 471,674
morphemes; the reader is confirmed, public signup disabled, and storage private
with a 128 MiB limit. Its 22 objects during the test include exactly two isolated
canaries beyond the previous 20; final canary cleanup is recorded separately below.

See FIRST_PRODUCTION_ACTIVATION.md for the concrete pending publication plan and
first-release recovery limits. No public activation or push occurred in this step.

The isolated Storage-provider test completed successfully: repeated signed uploads
worked within the 900-second lifetime; changing the disposable staging object could
not replace the sealed PDF; after the actual expiry plus a 10-second margin, upload
was rejected with HTTP400 and staged bytes remained unchanged. Both canary objects
were deleted and HEAD confirmed their absence. Safe evidence:
storage-transfer-acceptance.json. Canonical source files/objects were not modified.
All three explicitly approved acceptance operations are complete. Public activation
and the production bootstrap assertion remain pending separate owner approval.

### 2026-09-29 approved activation and frontend publication follow-up

The owner approved public activation. Run 36555147676 activated revision
ffb8b84a05bd57a1bec2d84db1b89e5bb556ae72 successfully: gateway and five APIs running,
all APIs healthy with zero restarts, no direct API host ports, dual-stack network,
no pending activation markers or supervisor warnings. Migration checks succeeded
at existing access_0001/content_0004/pts_0001 heads with no schema version changes.

Public API acceptance passed: Hebrew Bible and CORS; fresh authenticated organization
claims and directory membership; PtS 312/190/33 counts, search/filter/citation/export,
source/rights relationships and canonical PDF bytes. Anonymous and wrong-organization
requests were denied. Temporary session signed out and refresh token rejected.
Evidence: ignored public-production-acceptance.json and live-host-acceptance.json.

Netlify publication failed before uploading because its CLI detected multiple
workspace projects. Backend remains healthy. FRONTEND_PUBLICATION.md records the
isolated-artifact publishing fix and verification. Public frontend replacement and
real-browser verification remain pending the corrected CI run; no live user password
sign-in or password change is claimed.
