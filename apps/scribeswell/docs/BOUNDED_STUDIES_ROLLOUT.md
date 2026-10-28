# Bounded private Studies rollout preparation

This prepares a separately approved maintenance operation for the existing sole
consumer. It performs no deployment, production SQL, account provisioning, mail,
push, signup/provider change or sharing activation. Public reading is the default.
The [canonical spec](../../../_bmad-output/specs/spec-scribeswell-studies/SPEC.md),
[owner handoff](OWNER_READINESS_HANDOFF.md), [private report](PRIVATE_MIGRATION_REPORT.md)
and platform ADR-0020 remain authoritative.

## Current outcome and missing live inputs

The app supports exactly one canonical nonnil account UUID in production. Its
configured account must still receive a successful current Access check on every
private request; revocation, verification loss, app disable and outages still deny.
The enrollment proxy refuses before any upstream request, including for that
account. The bounded frontend uses an ordinary current private read before opening
creation, rather than enrollment. Default development enrollment is unchanged.

Production inventory is absent. No account UUID, project credential, target host,
current Compose/APISIX/environment bytes, current source/image registry digests,
retained frontend build inputs, migration profile/custody, target maintenance lock
or proven old-consumer baseline has been invented. Historical local host evidence
is not current inventory. The prior Access image is frozen Identity0026/Access0019;
the mixed live Identity0027 worktree is excluded. No executable activation is
approved by this document or the tool, even after a successful gate.

Run the offline refusal now:

```sh
P=apps/scribeswell/.local/owner-integration-20261027/python/bin/python
$P -B apps/scribeswell/deployment/studies_rollout.py prepare --output /private/NEW_CANDIDATE
```

It exits2 with `status:blocked`, lists missing inputs and creates no files. A real
external `--inputs` document is required to prepare a candidate. All output is
create-only; a failed/partial attempt remains retained and requires a new directory.

## Admission and exact external input contract

Collect the following through a separately authorized read-only target inventory.
Use the actual deployment's paths/project name; keep raw environment, TLS keys and
container inspect output in a private directory. Do not paste them into logs/chat.
Commands below describe the exact local inspection, not authority to contact a host.

```sh
umask 077
mkdir "$INVENTORY"
date -u +%Y-%m-%dT%H:%M:%SZ > "$INVENTORY/observed-at"
cp -- "$CURRENT_COMPOSE" "$INVENTORY/compose.json"
cp -- "$CURRENT_APISIX" "$INVENTORY/apisix.yaml"
cp -- "$CURRENT_SCRIBESWELL_ENV" "$INVENTORY/scribeswell.env"
cp -- "$CURRENT_ACCESS_ENV" "$INVENTORY/access.env"
cp -- "$CURRENT_FRONTEND_ENV" "$INVENTORY/frontend.env"
docker compose -f "$CURRENT_COMPOSE" ps --format json > "$INVENTORY/containers.json"
docker image inspect "$API_IMAGE" "$MIGRATION_IMAGE" "$ACCESS_IMAGE" > "$INVENTORY/images.json"
```

The deployment owner must establish the actual state directory and exclusive
`release.lock`, public reader/frontend API origin/base, TLS certificate validity,
current public corpus head and compatible validation profile/custody, exact existing
account's current verified grant and durable actor, restricted role/executor setup,
network and startup health. Do not enroll or prepare a grant as a side effect.
Capture authorized Directory/PtS Access consumer success/denial baselines so those
interfaces can be checked after the frozen Access replacement. If later shared
owner heads or running consumers require the mixed runtime, stop: this candidate
must not replace their owner/runtime with an incompatible historical pair.

The JSON inputs have exactly these fields (replace all placeholders privately):

```json
{
  "schema_version": 1,
  "release_id": "unique-maintenance-release",
  "source_revision": "EXACT_40_LOWERCASE_HEX_SOURCE_COMMIT",
  "account_id": "EXISTING_CANONICAL_ACCOUNT_UUID",
  "observed_at": "FRESH_UTC_INVENTORY_TIMESTAMP",
  "site_origin": "https://ACTUAL_SITE",
  "api_origin": "https://ACTUAL_API",
  "retained_compose": "/private/inventory/compose.json",
  "retained_gateway": "/private/inventory/apisix.yaml",
  "retained_api_env": "/private/inventory/scribeswell.env",
  "retained_access_env": "/private/inventory/access.env",
  "retained_frontend_env": "/private/inventory/frontend.env",
  "private_env": "/private/studies-private.env",
  "api_image": "ACTUAL_REGISTRY_REFERENCE@sha256:ACTUAL_MANIFEST_DIGEST",
  "migration_image": "ACTUAL_REGISTRY_REFERENCE@sha256:ACTUAL_MANIFEST_DIGEST",
  "access_image": "QUALIFIED_FROZEN_REFERENCE@sha256:ACTUAL_MANIFEST_DIGEST",
  "image_proof": "/private/inspections/image-proof.json",
  "migration_network": "ACTUAL_RETAINED_PRIVATE_COMPOSE_NETWORK",
  "migration_profile": {"profile": "ACTUAL_APPROVED_PUBLIC_PROFILE", "custody": null}
}
```

`custody` must be the real approved object where its existing release profile
requires it. Production database URLs bind both restricted role and the same exact
Supabase project/database as the retained API, Access and frontend. Direct and
supported pooler URLs retain explicit TLS. The seven supplemental secrets use
[the example](../deployment/studies-runtime.env.example). No migration/admin URL
belongs in API or Access runtime configuration. Existing complete environment
files are retained before adding the selected private variables.

Access stays internal at exactly `http://access:8000` on the retained Compose
network; its service is not exposed through a public gateway route. This narrowly
bounded internal HTTP hop matches the existing owner deployment. Production DB
connections and browser-facing API retain TLS. The runtime also supports a separately
qualified HTTPS Access endpoint, but this Compose candidate only selects its own
`access` service. No arbitrary remote plaintext Access endpoint is accepted.

The inventory expires after24hours. Preparation checks the existing public route
is GET/OPTIONS `/scribeswell/api/bible/*` on the selected HTTPS host and retains its
bytes and TLS entries. It only adds the private Studies/operation route and changes
selected API/Access image/environment references plus the gateway document mount.
Every unselected service, network, gateway image, TLS key/certificate and public
route stays in the copied candidate. Do not run the whole-registry host release or
generator against the mixed worktree; its global private-production guards remain.

## Exact candidate image/source preparation

Build/package the candidate API and migration images from a reviewed app-only
context, plus the unchanged qualified frozen Access bundle. Preserve exact source
and installed dependency/image observations. App requirements are unpinned: a local
image identity never qualifies a different rebuild. Publication is separately
approved; this task has not pushed images. A local config image ID without a
registry RepoDigest cannot satisfy the production input contract.

Once immutable images exist locally, this read-only local inspector starts
network-isolated, read-only byte probes and retains their exact image IDs,
RepoDigests and packaged source hashes. It never pulls, pushes or contacts a target:

```sh
$P -B apps/scribeswell/deployment/studies_rollout.py inspect-images \
  --inputs "$INPUTS" --output "$INSPECTIONS"
$P -B apps/scribeswell/deployment/studies_rollout.py prepare \
  --inputs "$INPUTS" --output "$ROLLOUT"
```

Set `image_proof` to the inspector's output before preparation. The inspector
compares each selected image's actual packaged bytes to its owning Docker COPY
inputs; frozen Access compares all14 runtime modules to the immutable archive.
The Access image config ID must also match the qualified frozen
`sha256:792933a8b3678b78657588e230e4f14dbbfe0e44909e616b56e1f9cf25448eba`;
matching module bytes alone cannot qualify rebuilt dependencies. The source/image
proof is evidence to review, not a signature or production
qualification. It must be accompanied by the focused authorization/native evidence
and operator review. The gate always reports `activation_authorized:false`.

Preparation writes complete candidate `compose.json`, `apisix.yaml`, API env,
Access pending env, frontend env and retained public recovery envs under0700/0600.
It records source, tool, owner qualification, image/proof and retained-input hashes.
No usable Access private environment exists until migration and live preparation
pass. Frontend config preserves the actual deployed `VITE_APP_BASE`, public Bible
URL, provider/session configuration and other retained inputs; it explicitly sets:

```text
VITE_STUDIES_ENABLED=true
VITE_STUDIES_PREGRANTED=true
VITE_STUDIES_API_URL=https://ACTUAL_API/scribeswell
```

`VITE_API_BASE_URL` remains the existing development proxy target. It is not the
browser private API base. Build using an isolated env directory to exclude ignored
workstation dotenv files:

```sh
mkdir "$FRONTEND_BUILD_ENV"
cp -- "$ROLLOUT/frontend.env" "$FRONTEND_BUILD_ENV/.env.production"
RELEASE_ENV_DIR="$FRONTEND_BUILD_ENV" npm --prefix apps/scribeswell/web run build
```

Retain the actual output bytes and publication recipe. Do not publish from a build
whose base/public API/auth inputs differ from the retained target.

## Separately approved maintenance execution

Maximum maintenance budget is15minutes. Keep public reading available where the
retained topology permits it; stop private write admission and drain ongoing
requests for up to30seconds before owner or private migration. Hold the actual
existing target release lock for the entire operation, including activation and
verification. Do not invent a second independent lock. Confirm recoverable backup
and the data-preserving procedure before starting; backup availability is not
permission to overwrite later writes.

1. Before the window, compare all retained/candidate hashes, image identities,
   frontend output, exact current heads and old-consumer baselines. Prove the
   frozen owner pair is compatible with the actual existing owner state/consumers.
   Stop on later/unknown heads, unqualified source, missing grant/actor, unsafe
   roles, unavailable profile hook/provider, invalid TLS or absent inventory.
2. Where needed, owners perform their existing controlled Identity0026 then
   Access0019 compatible migrations/preparation with their published tooling and
   separately scoped credentials. If already at the qualified pair, verify it.
   No Identity0027 or broader service migration belongs to this operation. Any
   failure/unknown result stops activation; reconcile actual committed state.
3. Execute only the selected Scribeswell image under its bounded supervisor.
   `MIGRATION_ENV` is an external complete file with `SUPABASE_URL`, existing
   corpus migrator/profile/custody, `SCRIBESWELL_STUDIES_MIGRATION_ENABLED=true`
   and private migrator URL. The wrapper freezes validated private inputs,
   changes only the newly created evidence directory to UID10001, runs the
   immutable image on the explicitly retained network, and retains the exact
   stopped migration container for investigation. Host administrator privileges
   match the existing release adapter's evidence-directory ownership requirement.

   ```sh
   sudo "$ABSOLUTE_P" -B "$APP_ROOT/deployment/studies_rollout.py" migrate \
     --candidate "$ROLLOUT" --migration-env "$MIGRATION_ENV"
   ```

   The app supervisor has a180second total budget; the wrapper allows190seconds.
   Timeout attempts a bounded stop of only its exact named container and retains
   unknown outcome. Do not infer rollback. A failed, unknown, malformed or wrong
   private head report blocks the next step. Public report/profile and actual
   committed private head0009 must both pass.
4. Immediately run the gate with Identity/Access migrator credentials loaded
   privately into the process environment for this same Supabase project. The
   gate revalidates all frozen inputs and calls the unchanged archive's actual
   read-only `prepare`, including owner baselines/principals/profile-hook/role
   checks. It never accepts supplied readiness JSON or an operator boolean.

   ```sh
   sudo --preserve-env=IDENTITY_MIGRATION_DATABASE_URL,ACCESS_MIGRATION_DATABASE_URL \
     "$ABSOLUTE_P" -B "$APP_ROOT/deployment/studies_rollout.py" gate --candidate "$ROLLOUT"
   ```

   Its migration evidence must be less than15minutes old. Live preparation
   creates a new release-bound readiness v2 artifact and complete `access.env`.
   Review the actual prepared artifact/report and apply the separately approved
   activation within5minutes; after that rerun preparation in a new retained
   attempt, reconciling actual head rather than downgrading/stamping. The artifact
   itself does not claim perpetual readiness; every request rechecks Access.
5. Only with separate production execution approval, make the gateway secret
   readable by its actual retained UID/GID636 (`chown :636`, `chmod0640` on the
   exact candidate `apisix.yaml`; no recursive chmod/chown). Verify its actual
   certificate/key and retained gateway bind settings. Then execute only:

   ```sh
   docker compose -f "$ROLLOUT/compose.json" up -d --no-deps access scribeswell
   docker compose -f "$ROLLOUT/compose.json" up -d --no-deps --force-recreate gateway
   ```

   Publish only the reviewed Scribeswell frontend output using its retained host
   recipe. Do not run a broad `compose up`, owner migrators on startup or an
   automatic database rollback. The tool does not execute these commands.
6. Verify within5minutes: unauthenticated public books/chapter GET and OPTIONS,
   anonymous private401, other verified account403, enrollment403 with no owner
   mutation, configured account current-authority read/create/edit/save/reload,
   revision and operation receipt agreement, revoke/disable denial and restored
   still-valid authority, cache no-store, no private gateway log content, TLS for
   both app DB logins. Check the retained Directory/PtS current-authority success
   and denial baselines against the replaced Access runtime. Any failed check,
   unhealthy service or exceeded15minute window enters public-reader recovery.

The live verification actions need the real approved account and exact expected
saved rows; do not issue sample production writes without explicit agreement.
Physical devices and external SMTP remain separate gates. No signup/provider
setting change is required to use an existing verified granted account.

## Public-reader recovery and forward repair

Stop private admission first. Deploy the candidate API with the complete retained
`public-scribeswell.env` (Studies disabled and all private variables absent),
restore the retained public-only gateway route document and retained public
frontend/build configuration. Use app-specific reviewed Compose edits and
`up -d --no-deps` for only the affected API/gateway/frontend; preserve the complete
retained unrelated configuration. Recheck public GET/OPTIONS and private404.
The same candidate API supports this recovery at the actual committed schema.

Preserve private schema head0009, saved rows, revisions, receipts and owner
actors/grants. Never restore an old backup over acknowledged writes, downgrade,
stamp, automatically reverse migrations or claim rollback from a timeout. Retain
migration execution, committed ledger observations, source/image/runtime evidence
and exact stop state; inspect the named migration container before removing it.
Reconcile failed/unknown actual owner and app ledger/data with restricted owner
views, then forward repair/retry under a new operation/attempt. Previous owner
runtime recovery is allowed only after compatibility with the actual committed
owner state is verified; otherwise keep private disabled and repair forward.

Restoring private mode on unchanged compatible head requires a newly successful
migration/report attempt and fresh owner preparation; use the same canonical
account and still-current grant, then check the saved revision/receipt. Changing
account restrictions never transfers saved content or grants authority. Do not
reuse an old successful artifact to bypass a revoked grant or failed release.

## Local evidence, traceability and impacts

- Default/private opt-in, canonical single-account restriction, DB TLS, arbitrary
  plaintext Access refusal, fresh request checks, cross-account/current denial,
  enrollment with zero upstream calls and public OPTIONS: `test_bounded_studies.py`.
- Retained configuration isolation, strict/bounded/duplicate input refusal,
  project/profile/image/source/proof binding, actual live preparation invocation,
  stale/missing/failed/unknown migration refusal and safe errors:
  `test_studies_rollout.py`. These are wrapper/control-flow doubles, not live
  production permission/readiness proof.
- Actual fresh PostgreSQL17 head/repeat, current saved revision2 and receipt across
  real private-route disable/restore with public reads, failed DDL and forward
  retry: selected `test_studies_migration_report_native.py` cases. HTTP authority
  in the new preservation case uses an explicit owner double; existing frozen
  real-owner qualification remains separately retained.
- Parent browser evidence proves desktop/mobile pregranted first-create, save and
  reload, no enrollment, explicit production private URL and current denial;
  default enrollment smoke remains green. Interception is consumer evidence.
- The newly built production-capable API image is independently identified in
  parent image evidence. Network-isolated actual default-command checks prove
  enabled/disabled startup/denial and packaged bytes; they do not prove live
  owner requests, TLS/database writes or production readiness. Its local image
  config ID has no published RepoDigest and cannot satisfy activation inputs.

Final focused app runtime/tool/image/report verification: **100 passed in3.18s**
(one existing TestClient deprecation warning). Native selected checks: **3 passed
in5.52s**, with all64 observed source inputs unchanged during execution and normal
exact-container/volume cleanup. Parent browser/build/composition and candidate
API/migration image probes are separately recorded, including their limits.

Exact commands/results/source hashes and limitations are retained in
[the local evidence directory](evidence/bounded-studies-rollout-20261028).
No broad upgrade matrix or full repository suite is claimed. Scaffold: no generic
generator/lifecycle change; app-owned release adapter and cache-exclusion pattern
and restricted-image readability for the generated migration helper; generated
sources themselves remain unchanged. Shared UI: none. Agent context: existing policies suffice. Documentation:
this runbook, env example and handoff/evidence. ADR: implements accepted ownership,
restricted authority, release safety and saving decisions; none changed.
