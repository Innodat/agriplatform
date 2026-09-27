# Platform deployment: staged Netlify + Hetzner releases

This package is preparation, not evidence that an uninspected target is ready.
Nothing here provisions accounts, DNS, Supabase branches, schemas or production data
automatically. Obtain final approval for the concrete target plan before enabling
these workflows or applying infrastructure. Main deploys **staging only**; production
requires manual promotion of an exact SHA with successful staging evidence.

## Architecture and inputs

The registry lists app/service-owned manifests and Dockerfiles. Initial services:
PtS, Scribeswell, directory, access and content. Frontends share one origin: PtS `/`,
Scribeswell `/scribeswell/`, unchanged `pts-auth` storage. Only APISIX publishes 443.
Access and content are reachable only on the Compose network. All browser business
requests go through explicit API origins. Supabase provides Auth, PostgreSQL and
private Storage; no local database, etcd, workers, Temporal or Leave is deployed.

Production inputs already selected: `https://scribeswell.com`,
`https://api.scribeswell.com`, Supabase Pro project
`https://gjbsnxmbhxsvcblzgfts.supabase.co` in Ireland, Dynadot DNS.
Create a distinct persistent Supabase staging branch/project only after approval.
Persistent branching is available on Pro but billed separately; no production data
or credentials are copied by this package. Confirm current pricing before approval.
Prefer Germany (evaluate `nbg1`/`fsn1`) initially; measure database roundtrip and signed
upload latency from the actual host before activation. The Terraform `cx33` estimate
is configurable; confirm availability/capacity, backup and recovery expectations.

Still required per environment: Hetzner account/token, explicit region/server size,
SSH public key and restricted admin/runner CIDRs, trusted SSH host key, host account,
Supabase URL/public key, runtime roles, service credentials, TLS certificate/key,
Netlify site/account/token, GHCR read credential for host, organization/account IDs,
and verified schema/Auth/Storage/import/recovery evidence. No invented UUIDs.

## Local verification (no provider credentials)

From repository root:

```sh
python3 platform/deployment/release.py check
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'
node --test platform/deployment/tests/release.test.mjs
python3 tools/py/run_compose_supabase.py --check-only
python3 platform/deployment/install-frontends.py
# Supply explicit PUBLIC_SITE_ORIGIN, PUBLIC_API_ORIGIN, DEPLOY_ENV,
# VITE_SUPABASE_URL and public VITE_SUPABASE_ANON_KEY (never server credentials).
node platform/deployment/build-release.mjs
npm run test:browser --workspace=apps/scribeswell/web
npm run test:browser --prefix apps/pts/web
npx --prefix apps/scribeswell/web playwright test --config apps/scribeswell/web/playwright.release.config.cjs
python3 platform/deployment/tests/gateway_smoke.py
terraform -chdir=platform/deployment/terraform fmt -check
terraform -chdir=platform/deployment/terraform init -backend=false
terraform -chdir=platform/deployment/terraform validate
```

The gateway smoke creates only disposable local fixture containers and self-signed
certificates. It verifies TLS host/path allowlists, public GET/OPTIONS, forwarded
Auth/org headers, CORS, denied private/Admin/control paths and safe access logs.
`ci-build.py --sha <40-hex> --repository innodat/agriplatform --output /tmp/images.json`
builds local API and migration images; `--push` is reserved for approved CI.
Run `python3 platform/deployment/tests/container_smoke.py` against built images; it
loads each registered API's fixture environment, required artifacts and declared health path; liveness
is not database/Auth/Storage readiness. Do not substitute fixture evidence for live
permission, isolation, backup/restore or latency checks.

The static builder loads only explicit process public inputs with an empty Vite
envDir; ignored developer env files cannot bleed into releases. Only frontend dist
files are copied into `platform/deployment/public-release`, including shipped font
licenses. Never publish repository root or private source/PDF archives. Netlify
SPA fallback rules are generated from manifests in `_redirects`; root `netlify.toml`
sets the publish directory and headers. Existing assets take precedence.

## Terraform and host preparation

Use a separate directory/state backend per environment; never share state between
staging and production. Copy Terraform files into each operational state workspace,
set encrypted/access-controlled remote state, locking and retention before apply.
The checked-in example tfvars is illustrative and has no valid credentials. The
provider reads `HCLOUD_TOKEN` from the operator environment only. Terraform contains
only host/firewall/public-key resources; it does not receive runtime secrets, create
DNS, generate credentials, run migrations or activate applications. Inspect and
approve the saved plan before applying. No apply has been performed here.

SSH is limited to supplied administrator networks. Hosted GitHub runners do not
have a single fixed egress IP: use a runner with controlled egress or a deliberately
managed runner network range. Never solve this by opening SSH to the internet.
Port 443 is public; HTTP80 is closed. Cloud-init installs host tooling only. Confirm
Docker Engine and **Compose>=2.30.0** (required for raw env files). Cloud-init installs
Compose 2.39.4 from checksum-pinned upstream binaries for x86_64/aarch64;
confirm cloud-init completed successfully, security updates, time synchronization, disk space and
firewall behavior on the resulting Ubuntu host.

Register the host key from an independent trusted console, store it as
`SSH_KNOWN_HOSTS`; CI never calls `ssh-keyscan` or disables strict verification.
The current host runner uses root for file ownership and Docker access; configure a
dedicated, reviewed root SSH key or a narrowly scoped forced-command wrapper before
enabling CI. Docker group membership is root-equivalent. Register a read-only GHCR
credential on the host via `docker login --password-stdin`; no registry token goes
in Terraform or release source. CI authentication uses GitHub's packages token.

## External configuration and scoped authority

Store target configuration as `/etc/agriplatform/staging.json` or `production.json`,
not in git. Its fields are:

```json
{
  "environment": "staging",
  "site": "https://staging--YOUR_SITE.netlify.app",
  "api": "https://YOUR_STAGING_API_HOST",
  "supabase_url": "https://YOUR_STAGING_PROJECT.supabase.co",
  "env_dir": "/etc/agriplatform/staging",
  "state_dir": "/srv/agriplatform/state/staging",
  "bootstrap_evidence": "/etc/agriplatform/staging-bootstrap.json",
  "cert": "/etc/agriplatform/tls/staging/fullchain.pem",
  "key": "/etc/agriplatform/tls/staging/privkey.pem"
}
```

Copy each owner's `deployment/runtime.env.example` to the external env directory
as `<manifest-id>.env`, mode0600. Compose uses `format: raw`: dollar signs and
quotes are literal, with no Compose substitution. Do not add shell-style quotes
around values. The local gateway smoke checks a literal dollar credential fixture. Replace every placeholder and set exact CORS origin.
Host preflight binds every database URL to `db.<approved-ref>.supabase.co` with
the declared `<owner>_runtime`/`<owner>_migrator` role, or a Supabase pooler host
with `<role>.<approved-ref>` username. Require explicit TLS and reject undeclared
database authority and mixed-project Storage endpoints. No application receives
another owner's database login. PtS gets its own service
key; Content additionally gets its own access-check key and Storage credentials;
Access recognizes only the required service keys. Directory has only public Auth
key/JWT verification inputs, no database/service-role key. Scribeswell currently
requires its existing server-side Supabase key; review and restrict its actual
provider permissions before activation. Runtime image contexts deny everything
except required source/artifacts and exclude env/caches/tests.

`pts-migrations.env` contains the approved `SUPABASE_URL` and three migrator URLs from the PtS migration
example, with SSL. They are passed only to the separate migration image, never API
images. Import authority is a separate explicit operator process; see PtS import
example. The Content import key/org may be configured temporarily for an approved
import operation, then removed before normal release preflight. No import/reset/
seed/deploy.sh command is run by CI or container startup.

## Initial schema, data and activation gates

Review the actual project's histories and consumers first. The runtime migration
adapter coordinates **access → content → PtS** using the existing PostgreSQL advisory
lock and owner Alembic histories. It does not apply platform identity or Bible SQL.
Review/apply those histories in a separate approved initial bootstrap procedure,
with owner-specific deployment authority and compatibility/recovery tests. The root
composition currently includes Expense SQL; check-only is not approval to push that
entire composition. Inspect and approve the target-specific owner set. Expose
`identity` and `scribeswell` via hosted PostgREST only with the approved grants.
Enable and verify the existing custom Auth hook, organization membership and access
bridge. Employment/account linking alone never grants application access.

Record external bootstrap JSON with `environment`, `supabase_url`,
`schema_fingerprint` and `migration_compatibility_fingerprint` from
`python3 platform/deployment/host-release.py --fingerprint`,
and explicit true fields `initial_schema_verified`, `previous_version_compatible`,
`recovery_verified`, `auth_storage_verified`, plus a nonempty `approval_reference` linking real
inspection/test evidence. This is an operator assertion backed by evidence, not an
automatic audit. A changed platform/Bible SQL fingerprint blocks automatic release
until the changed owner steps have been explicitly reviewed, applied and verified.
An owner Alembic change also invalidates the migration compatibility fingerprint;
review prior-version compatibility and recovery evidence before approving that
new fingerprint. The ordered adapter then applies those approved owner changes.
Never copy a staging fingerprint approval to production without target verification.

Before first activation, test supported prior schema/data on a disposable database,
upgrade correctness, previous-image behavior against the new schema, partial failure
reporting and restore/corrective recovery. Record code/image identities, exact owner
before/after revisions and outcomes. Test Auth Site URL, recovery/invite callbacks,
mail delivery, disabled public signup, account provisioning, shared login/logout,
anonymous denial, revocation and organization isolation. Private Storage bucket and
global limits must permit128MiB; verify uploaded bytes, signed URL expiry/replay,
permission revocation and source rights/notices using the real owner APIs.

Follow the [PtS release inventory](../../apps/pts/deployment/RELEASE_PREPARATION.md)
for organization **PtS / Psalms that Sings** and import counts:312 poems,190 with text,
33 assistant-checked complete transcriptions,275 witnesses,19 source/rights pairs. Assistant checks
do not establish human verification, copyright clearance or training readiness. Follow its
Bible import/verify-only procedure for39 books,929 chapters,23,213 verses,306,785 words
and471,674 morphemes. Existing target data must be audited before writes. Conflicts
stop for review; never change expected counts to conceal unexplained discrepancies.

## TLS and renewal

Use ACME DNS-01 with Dynadot DNS under explicit operational authorization. A manual
Certbot DNS challenge is supported without putting Dynadot credentials on the API
host: `certbot certonly --manual --preferred-challenges dns -d <API_HOST>`; approve
and publish only the requested TXT record, verify propagation, finish issuance,
then remove the challenge record. No real certificate has been requested here.
Manual DNS challenges do **not** renew unattended. Assign an operator and expiry
alerts, rehearse renewal well before expiry, or separately review an automated
DNS hook with scoped credentials. Never claim auto-renewal from this package.

Copy fullchain/key to the external configured paths. Rendering checks hostname,
remaining validity (>24h) and key match. Generated `apisix.yaml` includes the TLS
private key: external directory mode0750/group636, file0640/group636 for official
APISIX uid636. Never upload that file as CI evidence or commit it. Mount secret files
read-only. To rotate: obtain and validate the new cert/key, rerender a *new external*
gateway directory using the current digest manifest and config, preserve old files,
set group636 permissions, run `docker compose -f <new>/compose.json up -d --wait`,
verify external TLS/SNI and routes and certificate expiry, then update operational
current-pointer evidence. On failure restore previous gateway config/certificate
while still valid; no database rollback. The local smoke validates self-signed
issuance/rendering/handshake; actual ACME/Dynadot renewal remains an operator rehearsal.

## GitHub and Netlify setup

Before enabling the workflows create separate `staging` and `production` GitHub
environments. Private-repository environment secrets require an eligible GitHub
plan; verify required-reviewer availability for the account/plan. Restrict production
environment to protected main and require reviewers where available; manual dispatch
and verified staging SHA are required regardless. Protect main/workflow changes and
review deployment code. Environment secrets: `DEPLOY_HOST`, `DEPLOY_USER`,
`SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS`, `PUBLIC_SUPABASE_KEY`, `NETLIFY_AUTH_TOKEN`,
`NETLIFY_SITE_ID`. Variables: `PUBLIC_SITE_ORIGIN`, `PUBLIC_API_ORIGIN`,
`PUBLIC_SUPABASE_URL`. Use independent runtime/SSH credentials for each environment.

Use one Netlify site, production domain scribeswell.com, and the stable draft alias
`https://staging--SITE.netlify.app`. Configure staging Auth/CORS against that exact
origin. Disable Netlify native Git main auto-publishing; CI deploys built files with
`--no-build`. Staging uses `--alias=staging` with **no --prod**. Disable Supabase GitHub
automatic migrations so it cannot compete with this release authority. Configure
Dynadot A/AAAA/CNAME and Netlify domain/TLS only after target plan approval; verify
both IPv4/IPv6 or omit AAAA until validated.

Main serializes checks, separate image builds, immutable registry digest recording,
ordered host migrations and health-gated activation, then Netlify staging. A staging
marker is uploaded only after all succeed. CLI23.6.0 returns the provider
`deploy_ssl_url` as `deploy_url`, not a promise that it is the stable alias. The
recorder verifies the site ID/name, ready alias branch and nonpublished deploy
against Netlify's API, then checks the stable alias serves this exact SHA, workflow
attempt and public configuration from `release-identity.json`. It does not confuse
a per-deploy URL with the staging alias. Verified source: npm
[netlify-cli23.6.0 package](https://registry.npmjs.org/netlify-cli/-/netlify-cli-23.6.0.tgz),
`dist/commands/deploy/deploy.js` (alias branch405-406, URL475, JSON563-568);
package SHA1 `7269c1df1a5c9b17f58a7d9f16d42c5c9a568e42`. Production workflow requires a40-character
SHA and finds a successful main staging workflow and nonexpired matching artifact;
it reuses those exact backend/migration digests. Frontend is rebuilt from that SHA
with production public inputs. Expired staging evidence requires restaging; no tag
or freeform-ref fallback. Concurrency never cancels running migrations; GitHub may
coalesce pending main pushes. A later successful main contains skipped commits.

## Failure, rollback and operations

Host flock and the database migration lock prevent competing runs. All candidate
images, including pinned APISIX, are pulled before migrations. Every migrator URL
is validated before the first owner. Database connections are bounded to5s, lock
waits10s, statements120s, and each Alembic process180s. The container supervisor
has a1500s outer bound and records timeout/stop uncertainty for reconciliation. Each release has
safe evidence with previous image/config pointer, current identities, owner outcomes
and activation result. Failure halts later owners and activation. Partial migration
outcomes require reconciliation against actual database histories; no automatic
SQL downgrade. Do not assume a failed migration was atomic. Migration stdout/stderr
is suppressed because third-party errors may contain sensitive parameters; use
controlled owner diagnostics with approved redaction when investigating.

Container activation is rolling/nonatomic on one host. The supervisor captures
Docker stop/kill/die/OOM events and exit codes, recording forced-termination or
unobserved-shutdown warnings even if Compose activation fails. A health failure can leave
some new services running; the failed report is not a rollback claim. Restore the
previous digest Compose configuration only after verifying compatibility with the
actual database state. Otherwise use a reviewed corrective migration or a planned
maintenance/restore procedure. If APIs succeed but Netlify fails, there is no staged
success marker; reconcile/retry the same exact images or restore the prior frontend
via Netlify only after compatibility checks. Preserve successful prior deploy IDs
and immutable artifacts. Never automatically reverse applied migrations.

APISIX selected JSON logs include status, duration and request ID only, excluding
URI/query/body/headers/signed URLs. Raw gateway error logging is disabled because
nginx diagnostics can expose query strings. API uvicorn access logs are disabled and its raw exception logger is restricted to
critical messages; Scribeswell emits a selected structured error without exception
text. This reduces diagnostics deliberately; review monitoring before activation. Docker rotates10MiB×3 per
container; restrict Docker/log access to operators and set operational retention
policy before release. Health probes are liveness only; external authenticated and
anonymous functional verification remains required. Graceful API timeout20s and
container stop grace30s are bounded; record forced termination and don't claim
resumed work without evidence. No worker recovery is claimed because no worker runs.

## Onboarding another silo

Add an owner manifest and explicit Dockerfile/deny-default context, then register
its manifest path. Declare unique id, dependency IDs, env_file, required_env, narrow database_roles,
health_path, smoke_env/artifacts, frontend path/base/install mode and API-variable
mappings, plus public path and HTTP-method allowlists
if applicable. A frontend's `api_variables` maps public VITE names to gateway suffixes.
Add owner migration group/adapter with progress evidence when needed; uncoordinated
schema files must enter bootstrap_paths and require explicit owner evidence. Never
import another app's server implementation. Future workers need explicit worker
identity/scope, bounded shutdown, queue compatibility and owner migration contracts
before registration; this package does not pretend nonexistent workers are ready.

Scaffold impact: the builder CLI is not implemented; document this contract for its
future templates without claiming generated support. Shared UI/agent context: none.
ADR impact: new platform deployment decision; accepted predecessors unchanged.

Official references: [APISIX deployment modes](https://apisix.apache.org/docs/apisix/deployment-modes/),
[Netlify CLI deploy](https://cli.netlify.com/commands/deploy/),
[Supabase deployment](https://supabase.com/docs/guides/deployment),
[Hetzner provider](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs).
