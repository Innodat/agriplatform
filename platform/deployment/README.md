# Platform deployment: production on Netlify + Hetzner

This package is preparation, not evidence that an uninspected target is ready.
Nothing here provisions accounts, DNS, Supabase branches, schemas or production data
automatically. Obtain final approval for the concrete target plan before enabling
the workflow or applying infrastructure. Main deploys **production directly** after
all release checks pass. There is no active staging workflow or staging prerequisite.
Manual dispatch also uses the exact main event SHA; other branches cannot release.

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
The owner chose one production environment for the initial release. Netlify and
Hetzner accounts are ready; use the existing Supabase production project. Do not
create a persistent Supabase staging branch or a second host for this setup.
Prefer Germany (evaluate `nbg1`/`fsn1`) initially; measure database roundtrip and signed
upload latency from the actual host before activation. Terraform defaults to `cpx12`
(1 shared vCPU, 2 GB RAM, 40 GB disk). This is a starting estimate, not a measured
capacity guarantee. Measure total host/container memory and CPU during realistic
reading, searches, exports, imports and release activation; check for OOM events and
leave OS/deployment headroom. Increase the size if measurements warrant it. Images
build in CI, not on this host; keep disk space for current and recovery images.

Still required per environment: Hetzner account/token, explicit region/server size,
SSH public key and restricted admin CIDRs, dedicated CI WireGuard peer, trusted SSH host key, host account,
Supabase URL/public key, runtime roles, service credentials, TLS certificate/key,
Netlify site/account/token, GHCR read credential for host, organization/account IDs,
and verified schema/Auth/Storage/import/recovery evidence. No invented UUIDs.

## Local verification (no provider credentials)

From repository root:

```sh
python3 platform/deployment/release.py check
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'
node --test platform/deployment/tests/*.test.mjs
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

Use one production state workspace now. If staging is added later, give it its own
host, credentials and state. Copy Terraform files into the operational workspace,
set encrypted/access-controlled remote state, locking and retention before apply.
The checked-in example tfvars is illustrative and has no valid credentials. The
provider reads `HCLOUD_TOKEN` from the operator environment only. Terraform contains
only host/firewall/public-key resources; it does not receive runtime secrets, create
DNS, generate credentials, run migrations or activate applications. Inspect and
approve the saved plan before applying. The first approved host/firewall apply is
recorded in [production status](PRODUCTION_STATUS.md); application activation remains pending.

Supply exactly one SSH key input: `existing_ssh_key_id` references a registered
Hetzner key without managing or renaming it; `ssh_public_key` creates a new key.
The current owner has registered `hetzner-ck-wsl`; use its ID after verifying the
public key against the local key. The ignored root `.env` uses
`DEPLOY_SERVER_API_KEY`; the plan runner reads that value without printing it and
passes it to Terraform only as `HCLOUD_TOKEN`, never as a Terraform variable.
The host explicitly enables IPv4 and IPv6. Initial administrator SSH access uses
the approved current public IPv4 /32; changing ISP addresses requires a reviewed
firewall update. Publish an IPv6 AAAA record only after IPv6 routing is verified.
The existing Netlify site is `boabab.netlify.app`, serving `scribeswell.com`;
reuse it and verify its Git integration settings before enabling release CI.

Public SSH is limited to supplied administrator networks. Hosted GitHub runners
use the dedicated WireGuard peer below because their egress addresses change.
Never solve changing runner IPs by opening SSH to the internet.
Port 443 is public; HTTP80 is closed. Cloud-init installs host tooling only. Confirm
Docker Engine and **Compose>=2.30.0** (required for raw env files). Cloud-init installs
Compose 2.39.4 from checksum-pinned upstream binaries for x86_64/aarch64;
confirm cloud-init completed successfully, security updates, time synchronization, disk space and
firewall behavior on the resulting Ubuntu host.

Register the host key from an independent trusted console, store it as
`SSH_KNOWN_HOSTS`; CI never calls `ssh-keyscan` or disables strict verification.
The current host runner uses root for file ownership and Docker access; configure a
dedicated, reviewed root SSH key or a narrowly scoped forced-command wrapper before
enabling CI. Docker group membership is root-equivalent. CI sends its temporary
`GITHUB_TOKEN` to `registry-deploy.py` through strict SSH stdin. The wrapper logs
into GHCR in a root-only temporary `/run` Docker config, bounds login to 45 seconds,
passes that config to all release image pulls, and removes it on success or failure.
The isolated config intentionally hides user-installed Docker CLI plugins. Install
Compose >=2.30.0 system-wide (for example in `/usr/local/lib/docker/cli-plugins`);
production boabab has system-wide 2.39.4. The wrapper checks Compose using its empty
private config before login or deployment and fails closed if unavailable. Never
copy a user's plugin directory or credentials into the temporary config.
Existing host credentials are untouched; no permanent PAT is required. TERM/HUP/INT
cancellation drains the detached release coordinator under its per-stage deadlines;
it retains its lock and credentials until its final possible pull, then the wrapper
returns failure and removes its temporary config. Do not force-kill the coordinator
during a Docker migration. A hard host/process kill requires operational reconciliation;
`/run` is volatile and temporary credentials remain root-only until cleanup/reboot. Registry
package access must permit the workflow token; actual pulls require hosted evidence.

## External configuration and scoped authority

Store target configuration as `/etc/agriplatform/production.json`,
not in git. Its fields are:

```json
{
  "environment": "production",
  "site": "https://scribeswell.com",
  "api": "https://api.scribeswell.com",
  "supabase_url": "https://gjbsnxmbhxsvcblzgfts.supabase.co",
  "env_dir": "/etc/agriplatform/production",
  "state_dir": "/srv/agriplatform/state/production",
  "bootstrap_evidence": "/etc/agriplatform/production-bootstrap.json",
  "cert": "/etc/agriplatform/tls/production/fullchain.pem",
  "key": "/etc/agriplatform/tls/production/privkey.pem"
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
key/JWT verification inputs, no database/service-role key. Directory verifies ES256/RS256
tokens with the configured Supabase Auth endpoint. Omit `SUPABASE_JWT_SECRET`
for asymmetric signing; supply the actual project secret only for legacy HS256.
Do not use a placeholder signing secret. Scribeswell's current Bible routes are
public and do not require that optional legacy setting. Scribeswell requires
`SCRIBESWELL_DATABASE_URL` as `scribeswell_runtime`, with explicit TLS. Host
preflight rejects obsolete Supabase service-key authority. Import uses the separate
`SCRIBESWELL_IMPORT_DATABASE_URL` as `scribeswell_import`; never place it in runtime env.
Follow the [Scribeswell transition](../../apps/scribeswell/deployment/README.md) before activation. Runtime image contexts deny everything
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
entire composition. Inspect and approve the target-specific owner set. The app
directory uses a static catalogue and verified Auth claims, with no PostgREST
dependency on `identity`. Scribeswell uses restricted direct PostgreSQL. Neither
requires Data API schema exposure. Retain any existing exposure until all affected
consumers pass the separately approved transition; do not remove unrelated access.
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
Bootstrap approval must describe this production target and actual verification.

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

Use Certbot standalone HTTP-01 on TCP80; API traffic remains HTTPS443. Terraform
`acme_http_enabled` defaults to false. Before live installation, review a saved plan
that adds only TCP80 and preserves the host, cloud-init and existing firewall rules.
Check A/AAAA records reach the host, port80 is free, and host firewall permits TCP80.
Do not publish application containers as part of this preparation.

Under separately approved operational installation:

1. Install `tls/renew.py` at `/opt/agriplatform-operations/tls/renew.py` owned by root,
   and `tls/agriplatform-tls.{service,timer}` under `/etc/systemd/system/`. Keep the
   external target JSON and TLS files private. Install `tls/deploy-hook.sh` executable
   as `/etc/letsencrypt/renewal-hooks/deploy/agriplatform-tls`.
2. With Certbot >=2.3, run `certbot reconfigure --cert-name api.scribeswell.com
   --authenticator standalone --preferred-challenges http` (staging validation).
   Then run `certbot renew --cert-name api.scribeswell.com --dry-run`.
   A dry-run does not establish live gateway adoption; never install staging certs.
3. Run `systemctl daemon-reload`, enable/start `certbot.timer` and
   `agriplatform-tls.timer`, then start `agriplatform-tls.service`. The Certbot deploy
   hook starts adoption immediately. The independent 15-minute timer retries even
   after Certbot has successfully renewed the lineage, and starts after reboot.
4. Inspect `systemctl status certbot.timer agriplatform-tls.timer
   agriplatform-tls.service` and protected `state_dir/tls-*.json` evidence. Failed
   validation, expiry <=24h, route/handshake failure, or a busy release lock returns
   nonzero. Monitoring must observe failed units/evidence; no outbound alert delivery
   is claimed without an explicitly configured destination. No paid service is added.

The hook acquires the existing deployment lock, snapshots and validates hostname,
>24h validity, private-key match and system-trusted chain. Before first activation it
only installs verified copies and reports `pending_gateway_activation`. After
activation it copies the current gateway config, replacing only TLS material and
its bind-mount paths, then recreates **gateway only** with `--no-deps --pull never`.
It verifies the served fingerprint and `/directory/api/apps` through trusted TLS
before updating the current pointer. The leaf fingerprint is extracted from the
first certificate with OpenSSL; full certificate/key comparison also adopts a changed
chain with the same leaf. No API restarts, migrations, imports, image
changes or route changes occur. Generated APISIX content contains the private key:
keep it outside git/artifacts with mode0640/group636 and directory0750/group636.

Before mutation the hook fsyncs protected recovery intent and backups of the
installed cert/key pair. Those two paths are not claimed to update atomically: any
second-write failure restores both prior copies. TERM/HUP/INT is cooperative: the
current bounded command drains, then recovery runs. The primary operation has a
180-second budget and reserves a separate 120 seconds for recovery; systemd allows
600 seconds overall and a 240-second graceful stop margin.

On failure the hook attempts the previous gateway configuration and certificate,
verifies recovery and records stable nonsecret failure codes and interruption status.
If process loss leaves `state_dir/tls-pending.json`, the next hook reconciles the prior
gateway/copies/pointer before a later timer retries adoption. The release coordinator
refuses all image pulls/migrations/activation while that intent remains, preventing
a later recovery from overwriting a newer release. Never delete pending intent just
to bypass that guard. Conversely, host-release writes `release-pending.json` before
application activation and durably clears it only after route verification and the
current-pointer update. TLS refuses to run while application activation is uncertain.
Failed application activation can leave newer APIs running while `current.json` still
names the previous release; never infer runtime identity from that pointer alone.

Unchanged certificates still receive expiry/trust/served-route checks, but do not
rewrite matching copies or create private-key backups. Completed transactions remove
unneeded pair backups after durable intent removal. Keep the newest 96 routine
polling records; failures, recovery records and evidence referenced by current/pending
state are retained for operator review rather than automatic deletion.

An expired/untrusted previous certificate makes automatic recovery fail closed.
Not all failures automatically heal. A timed-out or externally interrupted Docker
client does not prove the daemon stopped mutating containers. Timeout uncertainty
retains pending intent even after a recovery probe; inspect daemon events/container
state and require settled, verified state before operator reconciliation. Do not
repeatedly force-kill clients or clear markers to bypass persistent uncertainty.

For coordinated operator recovery:

1. Pause deployment dispatch and stop `agriplatform-tls.timer`; let the service's
   bounded stop/recovery finish. Inspect safe failure/recovery codes and retained
   configuration. Confirm Docker has finished prior mutations. Keep both pending
   files until their corresponding operations are reconciled.
2. If `release-pending.json` exists, reconcile the application release first under
   `release.lock`: its `candidate` and `previous` records identify the exact Compose
   files/images/evidence. Reconcile migrations against actual database state; do not
   reverse them. Select a compatible release, restore/complete its services using
   its exact Compose file and `up -d --wait --wait-timeout 120 --pull never`, then
   verify every service's health and immutable image identity. Also verify trusted
   gateway TLS and the real API route. Durably save the verified selected record to
   `current.json` using `tls.save`, then `tls.durable_unlink(release-pending)`.
   If certificate expiry prevents that verification, keep the marker and perform
   the TLS helper sequence below as part of the same locked reconciliation, taking
   `known` from the selected application-release record instead of stale current
   state; clear the release marker only after all application and TLS checks pass.
   Do not use the TLS-only example unchanged while application identity is uncertain.
3. For TLS-only recovery, the following example uses existing Python helpers and
   holds the same lock across gateway, copies, current pointer and intent. Run as
   root only after step 1, with no application pending marker. Leave `use_renewed`
   false to restore a still-valid previous certificate. If previous TLS is expired,
   set it true to validate the current renewed lineage and combine it with the
   previous known routes, images and service configuration. This recreates gateway
   only. A failure preserves pending intent and backups; inspect/reconcile before
   retrying. Before first activation, the same sequence installs verified lineage
   copies without starting containers.

```python
import fcntl, json, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, '/opt/agriplatform-operations/tls')
import renew as tls

config = json.loads(Path('/etc/agriplatform/production.json').read_text())
state = Path(config['state_dir'])
use_renewed = False  # Set true only for the validated renewed-lineage recovery path.
with (state/'release.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (state/'release-pending.json').exists():
        raise SystemExit('Reconcile application identity first; keep pending markers')
    pending = json.loads((state/'tls-pending.json').read_text())
    known = pending['previous']
    evidence = state/('tls-operator-'+str(time.time_ns())+'.json')
    report = {'operation': 'operator_tls_recovery', 'outcome': 'failed'}
    tls.save(evidence, report)
    try:
        with tempfile.TemporaryDirectory(dir=state) as directory:
            cert, key = Path(directory)/'cert.pem', Path(directory)/'key.pem'
            if use_renewed or known is None:
                lineage = Path('/etc/letsencrypt/live/api.scribeswell.com')
                tls.atomic(cert, (lineage/'fullchain.pem').read_bytes())
                tls.atomic(key, (lineage/'privkey.pem').read_bytes())
            else:
                old = json.loads((Path(known['compose']).parent/'apisix.yaml')
                                 .read_text().removesuffix('\n#END\n'))['ssls'][0]
                tls.atomic(cert, old['cert'].encode())
                tls.atomic(key, old['key'].encode())
            budget = tls.Budget(seconds=300)
            fingerprint = tls.validate(cert, key, tls.urlsplit(config['api']).hostname, budget)
            if known is not None:
                compose = tls.prepare_gateway(known, cert, key, state) or Path(known['compose'])
                pending['operator_compose'] = str(compose)
                pending['operator_evidence'] = str(evidence)
                tls.save(state/'tls-pending.json', pending)
                tls.activate(compose, budget)
                tls.verify_retry(config['api'], fingerprint, budget)
            tls.install_pair(config, cert, key, budget)
            if known is not None:
                tls.save(state/'current.json', {**known, 'compose': str(compose),
                                               'tls_evidence': str(evidence)})
            report.update(outcome='verified', fingerprint=fingerprint)
            tls.save(evidence, report)
            tls.durable_unlink(state/'tls-pending.json')
            tls.discard_backup(state, pending)
    except Exception as error:
        report.update(outcome='failed', code=tls.safe_code(error))
        tls.diagnostic(evidence, report)
        raise SystemExit('Operator recovery failed; retain intent and reconcile') from None
```

4. Inspect the verified current pointer, protected evidence, installed cert/key and
   served certificate/route; resume the TLS timer and deployment dispatch only after
   reconciliation. Retain previous gateway directories until operational recovery
   retention is reviewed. This procedure does not roll back database state.

## GitHub and Netlify setup

Before enabling the workflow, create a `production` GitHub environment. Private-repository
environment secrets require an eligible GitHub plan; verify required-reviewer
availability for the account/plan. Restrict the environment to protected main and
use protected-main review before merging. Do not require per-release environment
reviewers when automatic main deployment is desired; first enablement still requires
the concrete target approval. Protect workflow changes and review deployment code. Both main pushes and manual dispatch run the same checks against `github.sha`;
manual dispatch from another branch is skipped. Environment secrets: `DEPLOY_HOST`,
`DEPLOY_USER`, `SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS`, `PUBLIC_SUPABASE_KEY`,
`NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`, `WG_CLIENT_PRIVATE_KEY`,
`WG_SERVER_PUBLIC_KEY`, `WG_ENDPOINT`, `WG_SERVER_ADDRESS`, `WG_CLIENT_ADDRESS`. Variables: `PUBLIC_SITE_ORIGIN`,
`PUBLIC_API_ORIGIN`, `PUBLIC_SUPABASE_URL`.

Use one Netlify site with production domain scribeswell.com. Configure production
Auth/CORS against that exact origin. Disable Netlify native Git main auto-publishing;
CI deploys built files with `--prod --no-build`. Disable Supabase GitHub automatic
migrations so it cannot compete with this release authority. Configure Dynadot
A/AAAA/CNAME and Netlify domain/TLS only after target plan approval; verify both
IPv4/IPv6 or omit AAAA until validated.

Before any host or publishing effects, the workflow binds NETLIFY_SITE_ID to the
intended production hostname using the provider site/domain metadata.
Main serializes contract tests, frontend builds, browser/session/artifact tests,
gateway acceptance, separate image builds, immutable registry digest recording and
isolated API health tests before any host migrations. Ordered migrations and
health-gated activation precede Netlify publishing. A production success artifact
for a newly published frontend is written only after Netlify confirms the site has
published this ready production deploy and the actual production origin serves the
exact SHA, workflow attempt and public configuration in `release-identity.json`.
Retained-frontend releases instead verify the selected existing frontend identity
and record frontend and backend SHAs separately, as described below. A public HTTPS request from CI to
`/directory/api/apps` must also pass DNS/TLS, status and exact-origin CORS checks.
Failure messages identify safe verification codes without credentials or response bodies.
No staging evidence or Supabase
branch is required. Concurrency never cancels running migrations; GitHub may coalesce
pending main pushes. A later successful main contains skipped commits.

### Frontend input selection

Production checks out full Git history and writes `frontend-plan.json` before
frontend installation. `record-production.py --select` binds the configured Netlify
site and hostname, its currently published ready production deploy, and identical
release identities at the immutable deploy URL and public origin. It compares that
published frontend SHA with the candidate SHA using `frontend-inputs.mjs`. It does
not use `push.before`, the latest attempted build, or a failed publication as the
production baseline. An unpublished frontend change therefore remains part of the
next release even when its newest commit only changes a backend.

Frontend inputs include registered frontend paths, any app `web`/`frontend` folder,
shared platform JavaScript package roots, registry/manifests, root dependency and
toolchain/configuration files, and frontend build/publish/detector tooling. Deleted
paths and both sides of renames count. Backend code, migrations, server Terraform/
WireGuard tooling and general documentation do not by themselves rebuild frontends.
The manifest/registry policy is intentionally conservative: their changes rebuild
even when a particular edit affects only backend metadata.

The builder records a deterministic SHA-256 `public_build_fingerprint` over the
explicit public environment, site/API/Supabase origins and public Supabase key.
Selection requires that fingerprint to match the intended configuration; key
rotations rebuild without source changes. Evidence contains the fingerprint,
never the key or provider credentials. Missing/invalid/old identities, unavailable
provider data, incomplete history, an unknown/nonancestor baseline, or identical
baseline/candidate revisions rebuild conservatively. The first release builds.
Choose **force_frontend_build** when manually dispatching main to deliberately
rebuild unchanged inputs.

For a verified backend-only release, installation, static build, browser tests and
Netlify publication are skipped. Contract tests, gateway smoke, API image/container
checks, strict private SSH, coordinated migrations and activation still run.
`record-production.py --retained` rechecks the exact selected provider deploy,
immutable/public identity and public configuration before and after the public
API/CORS probe. A mismatch fails the release. `production.json` records backend
`sha`/`backend_sha` separately from `frontend_sha`, `frontend_release_attempt` and
`netlify_deploy_id`; retained assets are never labelled with the new backend SHA.
The always-run upload preserves the non-secret decision plan even if a later stage
fails. A failure before selection may have no plan to upload.

The root Netlify ignore command uses the same dependency-free, Node 18 compatible
path/history detector with provider `CACHED_COMMIT_REF` and `COMMIT_REF`: exit 0
skips; exit 1 builds. Missing/unusable/equal refs build. Set
`FORCE_FRONTEND_BUILD=true` to override this native ignore decision. Native ignore
is a source-input optimization; production publication additionally verifies
provider identity and public configuration. **Explicit Netlify build hooks bypass
ignore by provider design.** The intended CI publication policy requires native Git
publishing to be disabled. The live Netlify integration is still enabled pending
separate approval; this change does not alter any live provider settings.

If retained verification fails, reconcile the actual Netlify published deploy,
public identity and API status before retrying. Do not publish the backend SHA over
old assets or manufacture a success marker. A new run selects against the actual
published baseline again; use force to request a fresh frontend candidate. Existing
partial-release recovery and approval boundaries below continue to apply. No
migration is reversed automatically.

`record-staging.py` and `verify-promotion.py` remain optional, tested helpers for a
future staging setup, but no active workflow invokes them. Reintroducing staging
requires an explicit workflow/configuration decision, not merely creating a branch.

## Dual-stack container networking

The Linux deployment host requires [Docker Engine >=27](https://docs.docker.com/engine/release-notes/27/#ipv6-network-configuration-improvements)
for automatic IPv6 subnet allocation, alongside Docker Compose >=2.30.0. It must
have working outbound IPv4 and IPv6, including
IPv6 access to the configured direct Supabase database endpoint. Host connectivity
alone does not prove container connectivity: verify a read-only database connection
from a disposable dual-stack bridge using the existing restricted role before
release. Auth HTTPS succeeding is not proof that the database is reachable.

Generated Compose declares `enable_ipv6: true` on its project-scoped default bridge;
IPv4 remains enabled. Only gateway TCP443 is published. Docker allocates an IPv6
ULA pool automatically when no pool is configured; no fixed global subnet, host
networking, daemon restart or global daemon/firewall changes are part of this fix.
See [Docker IPv6 networking](https://docs.docker.com/engine/daemon/ipv6/).

Each migration job creates its own uniquely named, labelled dual-stack bridge before
running, then removes it before activation. Creation and removal have 30-second
bounds. A migration timeout retains the existing bounded stop attempt before network
cleanup. Any creation, migration or cleanup failure blocks activation; inspect the
migration's network name, creation/cleanup outcomes and stop warning in release
`evidence.json`. An uncertain create may have left a network behind; inspect its
ownership label and attached containers before an explicit recovery action. Cleanup
never targets a network whose creation was not confirmed. Failed stop/removal may
leave a container/network requiring reconciliation; do not infer rollback or safe
retry from an error. Third-party command output remains suppressed.

An existing IPv4-only Compose network needs a planned replacement. Do not silently
recreate a network carrying a running release: arrange a maintenance/recovery window,
record the current release and compatibility evidence, stop affected containers,
replace only that project's unused network, and verify the candidate's dual-stack
connectivity and gateway checks before resuming service. There is no live stack on
boabab at the time of this preparation. No production activation is part of this fix.

Impact: this is generic deployment tooling and documentation. No application
scaffold, shared UI, agent-context or API changes; accepted ADRs remain unchanged.

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
maintenance/restore procedure. If APIs succeed but Netlify fails, there is no production
success marker. The always-run artifact step retains any available digest manifest,
Netlify result, verified-success marker and built frontend even when publication or
verification fails. A marker exists only after verification passes. Preserve successful
prior deploy IDs and immutable artifacts. Never automatically reverse applied migrations.


### Retry saved artifacts after a partial release

A GitHub workflow rerun is a **new build candidate**: base images/dependencies may
produce different digests for the same source SHA. Do not use it as an exact-artifact
recovery. First inspect host `evidence.json`, actual migration revisions and Netlify
published state. Obtain approval for the specific corrective action.

Before any manual recovery, suspend new production workflow runs and wait for any
active release to finish; drain or cancel queued runs before they start. Do not
cancel an in-flight migration. For example, disable `production.yml` using GitHub's
workflow controls, then verify there are no running, queued or waiting production
runs. Keep this deployment hold through frontend/API verification. Direct operator
commands do not share GitHub concurrency; the host lock alone does not serialize
Netlify publication. Restore automatic delivery only after recording the recovered
state and reconciling any main commits that arrived during the hold.

Download the failed run's `production-<SHA>-<ATTEMPT>` artifact to an external operator
directory using `gh run download <RUN_ID> --repo Innodat/agriplatform --name <ARTIFACT_NAME> --dir <RECOVERY_DIR>`.
It contains `images.json`, the original `netlify.toml`, `frontend-plan.json` when
selection ran, any `netlify-deploy.json`, and
`platform/deployment/public-release/` only when a frontend artifact was built. If
backend activation already succeeded, leave it running. Inspect the original
`frontend-plan.json` to determine whether this release retained the frontend.
Configure the original production public inputs (including the public Supabase
key), original `RELEASE_SHA`, `GITHUB_RUN_ID`, `GITHUB_RUN_ATTEMPT` and secure Netlify
credentials in the recovery directory.

For a retained release (`build: false`), keep the original `frontend-plan.json`
in that directory and use the recorder from a checkout of the exact original
backend release SHA:

```sh
python3 <CHECKOUT>/platform/deployment/record-production.py --retained
```

This reloads the original selected frontend deploy/identity and verifies it with
the public configuration and API. If it no longer matches, reconcile the actual
provider state, identity and API before choosing an approved recovery action. Do
not publish nonexistent artifacts or stale frontend assets from another release.
Do not rewrite the retained plan to manufacture verification. A deliberate new
frontend build requires a new verified release candidate.

For a release that built a frontend (`build: true`), require its saved immutable
`platform/deployment/public-release/` artifact before republishing. Using the
recorder from a checkout of the exact original release SHA:

```sh
python3 <CHECKOUT>/platform/deployment/record-production.py --preflight
python3 <CHECKOUT>/platform/deployment/publish-frontend.py --output netlify-retry.json
# Existing output files are never overwritten.
```

The publisher copies the artifact and configuration to a temporary directory outside
the monorepo, preventing Netlify from selecting a single workspace application.
Preserve the original result; use the new result as `netlify-deploy.json` in a separate
verification working directory and run `record-production.py` there with the original
release identity inputs. If publication succeeded and only verification failed, fix
DNS/CORS/configuration as appropriate and rerun verification before republishing.

If the backend itself needs retry after schema reconciliation, reuse the saved
incoming source and **original images.json** on the host. For an approved exact SHA
and a unique recovery directory, run the existing coordinator explicitly (no build):

```sh
python3 /srv/agriplatform/incoming/<SHA>/platform/deployment/host-release.py \
  --environment production --sha <SHA> \
  --images /srv/agriplatform/incoming/<SHA>/images.json \
  --public-config /srv/agriplatform/incoming/<SHA>/public-config.json \
  --config /etc/agriplatform/production.json \
  --release-dir /srv/agriplatform/releases/<SHA>-recovery-<UNIQUE_ID>
```

Confirm the incoming manifest matches the failed-run artifact before this command;
a later rerun of the same SHA may have replaced incoming files. Restore verified
original inputs from the retained artifact if needed. The coordinator preserves
all target, fingerprint, migration, health and lock gates and pulls exact digests.
If required artifacts or registry digests are unavailable, stop exact recovery and
plan a new verified release or a compatible rollback.

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
ADR impact: proposed ADR0043 updated for the user’s production-only decision; accepted predecessors unchanged.

Official references: [APISIX deployment modes](https://apisix.apache.org/docs/apisix/deployment-modes/),
[Netlify CLI deploy](https://cli.netlify.com/commands/deploy/),
[Supabase deployment](https://supabase.com/docs/guides/deployment),
[Hetzner provider](https://registry.terraform.io/providers/hetznercloud/hcloud/latest/docs).


## Boabab private administrator access

Use [the WireGuard operator guide](wireguard/README.md) for the in-place `boabab`
rename, administrator onboarding/removal, dedicated CI credentials and console
recovery. Terraform's `wireguard_enabled` defaults to false; enabling it adds only
public IPv4 UDP51820. `server_name` changes only the existing resource name; retain
its state, disks, IPs and unchanged cloud-init. Keep restricted public TCP22 until
both private administrator and CI SSH are verified, then explicitly assert
`private_ssh_verified=true` before setting `public_ssh_enabled=false`.

Production CI requires `WG_CLIENT_PRIVATE_KEY`, `WG_SERVER_PUBLIC_KEY`, `WG_ENDPOINT`,
`WG_SERVER_ADDRESS` and `WG_CLIENT_ADDRESS` in addition to its existing secrets.
`DEPLOY_HOST` is the server's private IPv4 address and `SSH_KNOWN_HOSTS` binds that
address to the independently verified existing host key. A temporary runner tunnel
and strict SSH preflight precede the unchanged migration/activation coordinator;
always-run teardown removes its owned interface and secret files. CI retains
root-capable deployment authority. This is preparation, not evidence of a live
private path or provider activation. The Mac Mini and its Tailscale network remain
separate and unchanged.
