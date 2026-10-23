# Scaffold Auth lifecycle and KDG parity — 2026-10-23

The bounded reconciliation is complete after all nine Blind Hunter findings were
patched. Final23 generated tests,28 unchanged KDG consuming tests and15 SDK/React proof
checks pass. See [the durable receipt](evidence/auth-pattern-parity-20261023.json).
Historical proof counts below are source-bound to those attempts.
User requested same-item scaffold/code/test maintenance rather than after KDG completion.
bmad-help selected [BD] bmad-build. Active renderApplication previously emitted only
health presentation; legacy templates/web/AuthContext was separate unused unsafe source.

## Adoption and maintenance contract

One canonical template group is now emitted by renderApplication and consumed as KDG
managed owner-local files: src/auth/lifecycle.ts, src/auth/use-lifecycle.ts and
scripts/test-auth-lifecycle.mjs. The build-time source map lives in src/auth-pattern.ts;
no runtime app imports builder code or another application. Structural AuthPort requires
no SDK dependency in generated applications; actual SDK compatibility remains KDG-owned.

The existing installer adopts only these three newly absent KDG paths, records them
in web/.generated-files.json, updates unedited managed bytes and refuses manual edits.
Existing KDG owner code is not bulk-adopted or overwritten. sync-kdg-auth --check first
checks the stored manifest and then exact current-template bytes. This detects freshness
that manifest-only checks cannot. Builder npm test includes parity assertions, so
changing a template or its tests requires updating the managed KDG copies together.
No arbitrary target, force flag, new preservation protocol or public generator.

Run selected Node26.11.1 from repository root (N below):

- `N platform/builder-cli/scripts/sync-kdg-auth.mjs --check`: readonly current code/hook/test parity.
- `N platform/builder-cli/scripts/sync-kdg-auth.mjs --write`: existing preservation installer
  updates unedited managed copies; conflicts fail without replacing owner edits.
- `N --test platform/builder-cli/tests/*.test.mjs`: affected builder suite, including
  deterministic generated map, current-template drift, installed-manifest false freshness,
  tamper refusal for code and tests, and owner preservation.
- `N platform/builder-cli/scripts/prove-auth-lifecycle.mjs`: actual render/install,
  generated23 behavioral tests and preservation/regeneration in a new retained proof root.
- `N apps/kdg-capture/web/tests/auth-proof.mjs`: generated23 plus unchanged28 KDG tests,
  strict TS7/negative own-source control and actual SDK2.117.3/React/Chromium consuming proof.
- Existing test:generation:application now runs generated test:auth before type/build/browser.
  Tool/cache environment remains in README.md; copied root lock only, fully offline.

N: platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
D: platform/deployment/.local/scaffold-auth-lifecycle-20261023. Every new attempt/proof
is retained. No root dependency/lock edit, Docker work, real account/access, provisioning,
Leave/editor, deployment/pilot, cleanup or fingerprint/HMAC work.

## Current KDG source inventory

| KDG source | Ownership and scaffold decision | Consuming verification |
| --- | --- | --- |
| auth lifecycle/React setup-disposal | neutral, now managed from common templates | generated23 + owner28 SDK tests; React strict replay/replacement proof |
| auth-entry.ts/AuthEntry.tsx | thin owner boundary/UI adapters | same28 owner tests and SDK/browser journey |
| entry.ts and generated Context types | owner API DTO/permission/fixed-org/resource validation; keep local | existing29 context-client tests/strict readonly types; API schema generation remains its existing owner |
| EntryScreen.tsx/CSS | KDG state copy/branding/setup presentation; keep local | existing15 presentation tests/13 browser proof checks; neutral shell skip/focus conventions already scaffolded |
| API/runtime/Access integration | owner service policy, credentials and current authorization; keep local | historical source-bound API/Access evidence retained; not rerun or promoted as Auth UI |
| provider launch/callback/PKCE/return/domain persistence | not implemented/qualified; do not invent scaffold behavior | still future consuming acceptance, no readiness claim |

Scoped builder/KDG AGENTS and generated guidance require scaffold/test impact at each
consuming delivery. This is a BMAD delivery rule plus executable parity for adopted
patterns, not automatic inference that every app-specific change should be shared.
New neutral patterns require explicit adoption and actual consuming tests.

## Behavioral evidence and limits

Before extraction, a conservative generated lifecycle stayed signed_out. The actual
rendered/installed acceptance failed expected authorized / actual signed_out in
D/proof-sUs6nl/tests.log. This is behavioral RED, not only file/import absence.
Focused generated23 scenarios then failed against that seed in proof-AVCzEK; several
failures are missing callback setup and only outer acceptance is claimed as behavioral.

Extracting the proven implementation and React lifecycle from KDG initially produced20 passing
generated tests in proof-SKKFRx and48 generated+KDG tests in the consuming proof
platform/deployment/.local/kdg-auth-entry-20261023/auth-c5b3401a-6a7a-44d9-ad4c-beec1bf4846d.
The KDG28 SDK tests were preserved byte-for-byte; the actual SDK/React15 proof checks pass.
The generic module preserves logout precedence, bounded work, disposed callback cleanup,
previous-account guards and guarded interactive recovery; owner admission is always injected.

Focused7 renderer/parity/legacy tests pass. Builder regression66 pass and strict TS7
exits0. First full application proof proof-bZqvPr passes offline generation/lock/install,
Auth20 tests, generated client/error tests, Python runtime, strict types, Vite8 build,
source/lock custody, seed/extension preservation and actual health success/outage browser.
Its independent API loops use only synthetic health probes, no business DB or Auth accounts.
Final source-bound proof after guidance/review updates follows below.

Legacy AuthProvider/useAuth now throw legacy_auth_template_retired. An executable
refusal test protects that retirement; copying the old template cannot silently retain
unbounded lookup/default-global sign-out. Existing apps copied earlier are not changed.
No claim that all legacy templates/dependencies or all consumers were migrated.

## Five impacts

Scaffold: canonical neutral code/hook/tests plus generator/parity/preservation checks.
Shared UI: React lifecycle hook only; KDG screen/brand remains app-owned. Agent context:
scoped builder/KDG and generated guidance; concurrent root AGENTS remains untouched.
Documentation: current adoption inventory/commands, new owner evidence and additive KDG
handoff; historical evidence immutable. ADR: existing0059/0031/0032/0023, no accepted edits.
All patterns remain internal candidates, no public generation or complete provider readiness.

## Compatibility and owner-boundary contract

Older application outputs carry the old inventory. In-place regeneration with the new
map intentionally refuses scaffold_ownership_invalid; no automatic inventory migration
or manifest deletion is supported. Keep the original output retained, render/install a
fresh internal candidate at an absent path, port reviewed owner seed/custom files through
the existing preservation/extension mechanisms and rerun acceptance. This is not public
generation or permission to replace an existing live application. KDG adoption starts
with new three-file web-root ownership; it never overwrites an old full-app manifest.
Future inventory growth needs an explicitly proven ownership migration in that delivery.

The reusable hook requires stable Auth client, memoized createBoundary and memoized
beginSignIn; generated README contains a useCallback example. Owner boundaries return
validated check outcomes. Their callback publications are ignored; coordinator epoch
checks govern the returned result and prevent both stale callbacks and callback-free
outcomes from breaking admission. Cleanup is attempted, but its exceptions cannot
prevent local closure or SDK subscription detachment. Late SDK side effects remain
outside cancellation guarantees, as before.

## Final review and evidence

Only the configured Blind Hunter layer ran. All nine findings were patched; none
remain deferred. Managed ownership now checks generator/template/recipe/source identity,
exact three-file inventory and generated classifications, in addition to stored hashes
and current-template byte parity. review-manifest-red.log records the observed missing
exception before correction. Code, React hook and generated tests all have tamper and
stale-generated coverage, with owner seed/custom files preserved.

The original neutral fixture hid stale callbacks behind its own generation guard.
Removing that guard reproduced stale authority in proof-7GHFqU. The generic lifecycle
now ignores all callback publications and checks epochs before publishing returned
outcomes; it also handles return-only boundaries. Throwing owner clear/dispose cannot
prevent local signed-out state or SDK detachment. Added generated cases cover these
contracts plus TOKEN_REFRESHED superseding the refresh return before interactive recovery.

Generated README documents stable memoized React inputs and old-inventory migration
limits. Narrow proof preflight rejects unqualified Node before creating output; a
negative control verifies this. No prior candidate inventory is silently expanded or
existing copied app claimed upgraded. No new runtime/provider capability is inferred.

Final generated-only source: D/proof-UK6FY0/result.json,23 passing tests plus actual
renderer/installer and seed/custom preservation checks. Final KDG consuming source:
platform/deployment/.local/kdg-auth-entry-20261023/auth-cc45edc1-343c-4f51-aeec-8e2ceaa1152e/result.json,
51 tests (23 generated+28 owner) and15 SDK/React/TS7 proof checks, normal HTTP shutdown.
Existing28 owner-test source bytes are unchanged from baseline. App-owned context/UI
and API/Access implementation/evidence are preserved.

Final full application: platform/deployment/.local/scaffold-application/proof-5grA1c/proof.json,
status passed. Its recorded source hashes match the final sources. It verifies offline
copied-lock resolution/clean install, generated Auth23 tests, generated client/error and
API runtime tests, TS7/Vite8 build, real own-health success/outage browser checks,
seed/extension preservation, managed source/lock custody and normal owned process closure.
Previous full passes proof-bZqvPr and proof-IOFsvS remain retained; no proof directory is
reused/deleted. This new proof is still bootstrap_only:true/generation_ready:false.

Builder regression68 passed after runtime/lifecycle review corrections; final focused6
parity tests also cover the subsequent source-digest identity assertion. Strict builder
TS7 checks exit0. All exact command logs/tool versions/source hashes are bound in the
receipt. No root build/test shortcut or unqualified runtime was used.

Preservation checks verify632 unchanged protected KDG/Access/builder/deployment/dependency
files, including all previous evidence, the approved dependency contract and root lock.
Only the listed source/guidance/test changes are authorized exclusions. Complete prior
KDG handoff remains an exact suffix. Concurrent Leave/Scribeswell/root AGENTS changes
and Docker resources remain untouched. Synthetic local/CI scope remains binding.
