# Controlled account capability grants

`account_grant.assign` and `account_grant.revoke` configure an explicitly registered
account capability through the existing isolated operator transport. Organization grants
remain independent. Restricted runtime reads use forced RLS on the asserted current
account; writes and operator evidence remain unavailable to runtime credentials. Configuring a disabled application does not confer effective
admission; runtime enforcement and consumer cutover remain ACCESS-B work.

The closed version1 envelope uses platform scope. Assignment creation supplies
`account_id`, `permission`, and `expected_absent: true`. Updating an existing retained
grant supplies the exact UUID `grant_id` and positive decimal string
`expected_revision` instead of `expected_absent`. Revocation requires those same four
exact target/revision fields. Actor, organization, membership, person and employment
fields are forbidden. Server attribution comes from the original database login's
current exact command, application and selected-account authority.

Assign verifies the selected live Auth/profile and permanent account-kind actor through
Identity's private `account_grant_target(uuid)` before local locks. The bounded observation
expires after five seconds and is checked at deferred commit. The setup context contains
no user account or organization. Revocation deliberately requires no live account
observation: retained grant identity and revision protect removal after deactivation.
Regrant retains the UUID and advances revision; a delayed older revoke cannot affect it.

Each changed operation records one compact receipt and business event atomically with
the grant. Unchanged operations have no event. Retry the exact command and operation ID
following uncertain completion, including after target deactivation, or query the matching command/account/permission receipt
under current original-login authority. Revocation receipt selection also requires the
exact grant UUID. Changed input conflicts. Never create another operation merely to
conceal an unresolved result.

## Controlled release and recovery

Coordinate Identity24 before Access17 under the existing controlled migration runner.
Both append to delivered owner histories; neither runs at API or worker startup. Migration
failure blocks activation. Inspect actual ledgers and retained data before explicitly
retrying forward; do not automatically downgrade. Previous organization commands and
Studies enrollment retain their prior independent behavior. Private native fixtures,
failed-attempt journals, source/lock hashes, rollback-only reference rehearsal, previous
client compatibility and the hardened image proof belong in the consuming Leave evidence.
The catalog helpers fail closed until independently rehearsed references are published.

The prepared offline owner interpreter is
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, `-I -B -m pytest`, and
`-p no:cacheprovider`. `tests/test_account_grants.py` maps the closed command, exact
receipt, selector, context and observation contracts. `tests/qualify_account_grants.py`
consumes an explicit private root-prepared Leave fixture, checks the actual retained
run/container/network binding, uses real original logins and the isolated CLI, and
records exclusive append-only attempt evidence. It never bootstraps or discovers
accounts, roles, authority or catalog references. Unit tests do not establish database
permissions or migration rollback.

## Offline package and image build

Run from the repository root with the prepared Python3.15.0 interpreter, uv0.13.1,
and the already populated offline cache. The owner lock and production source inputs
must remain unchanged throughout packaging. No root dependencies are installed.

```bash
P="$PWD/platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python"
task_toolchain="$PWD/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload"
task_cache="$PWD/platform/deployment/.local/python-baseline-qualification/cache"
"$P" -I -B services/access/deployment/package_runtime.py \
  --python "$task_toolchain/python/bin/python3.15" --uv "$task_toolchain/uv/uv" --cache "$task_cache" \
  --output "$PWD/services/access/runtime-bundle"
"$P" -I -B services/access/deployment/verify_runtime.py \
  --root "$PWD/services/access" --bundle "$PWD/services/access/runtime-bundle"
docker build --network none --pull=false \
  -f services/access/deployment/Dockerfile -t agri-access-a-api:reviewed "$PWD"
```

The selected carrier image must already be present locally. Packaging is frozen,
production-only and offline; the Dockerfile verifies the source-bound bundle before
copying it into the image. A successful build alone does not prove restricted startup,
health or absence of setup credentials; retain the actual hardened image proof with
its image identity and bundle provenance before activation.

Packaging refuses an occupied output. After a source, lock or packaging change, preserve
the old bundle and its provenance before rebuilding. Never clear it in place or reuse
old image evidence for changed bytes. This reserves a private archive directory and
moves the entire retained bundle into it:

```bash
mkdir -p .local
if [ -e services/access/runtime-bundle ] || [ -L services/access/runtime-bundle ]; then
  archive_dir=$(mktemp -d "$PWD/.local/access-runtime-archive.XXXXXXXX")
  mv -- services/access/runtime-bundle "$archive_dir/runtime-bundle"
fi
```

Then repeat package, verify and Docker build above, recording fresh logs and provenance.
Retain failed staging directories and failed verification/build logs for reconciliation;
never activate a failed or stale package. Independent database catalog references are
published through the root-owned rollback rehearsal, separately from image packaging.

## Explicit legacy cohort preparation

Keep synthetic legacy11 PtS rows read-only, including composite grant IDs and historical
creator strings. Select a reviewed cohort manually. Validate each known permission maps
to a registered account-scoped capability and each selected account has the verified
permanent account actor mapping. Unknown capabilities or missing/ambiguous mappings block
preparation. Generate ordinary explicit account assignment commands with actual executor
attribution; do not reuse a legacy creator as the new executor. Preserve the old source
at11 when incompatible. Do not union old organization grants, invent employment or
membership, convert automatically, or take over raw legacy tables. PtS consumer cutover
and corpus storage migration remain gated on ACCESS-B and PTS-ADOPT.

## Impact decisions

- Scaffold: reuse the proven controlled owner migration, isolated operator, and offline
  production packaging patterns. Access owns its SQL, account contracts and local
  packaging adaptation; no unproven generic import/authorization framework is added.
- Shared UI: no UI surface or reusable UI change is required.
- Agent context: existing account/organization ownership and attribution rules suffice.
- Documentation: this owner runbook and Leave release/acceptance evidence track the change.
- ADR: accepted account-scope, attribution and release decisions are implemented; no new
  decision or amendment is required.
