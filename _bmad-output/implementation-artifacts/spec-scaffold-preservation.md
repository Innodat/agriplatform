---
title: 'Safe scaffold reruns preserve custom code'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: '23f6e209c17df024a6b4aaf905829725c812d192'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="user approved the five-step bounded preservation plan and said happy, cont">

## Intent

The existing shell proof writes only fresh output. Prove initial installation and safe
reruns through the existing builder so application-owned code survives and unexpected
generated edits are refused. Add an internal installer used by disposable proof, not a
public candidate bypass. The existing public-generation readiness gate stays closed.

## Boundaries & Constraints

Always preserve source, previous proofs and concurrent documents. Reuse explicit
seed/generated maps from existing renderers. Seeds are create-once application code;
custom files stay untouched. Generated files require a complete hash preflight. Record
small versioned generator/template/recipe/source identities and ownership/hashes in
.generated-files.json. Stage the complete plan, serialize one writer per output, journal
old/new files locally, and restore the previous complete generated set after failed or
interrupted installation before another generation/build. Never claim multi-file atomicity.
Validate paths, regular files, metadata and ownership before mutation; refuse symlinks,
escapes, collisions, missing/invalid manifests and silent ownership conversions. Use safe
error identifiers. Keep exact approved pins including TypeScript7.0.2.

No public generate command, candidate promotion, template upgrades/removal, extension
copy/import support, dependency changes, new generator/service, runtime authorization,
Leave/editor, provider/account changes, migration, Docker/infrastructure/deploy or real
data. Extensions remain refused. Controlled synthetic files are the only write targets.
Existing builder source is stable during a proof; this is not an adversarial filesystem
service. Fail closed on uncertain ownership/recovery rather than deleting user files.

## I/O & Edge-Case Matrix

| Scenario | State | Behavior | Failure |
| --- | --- | --- | --- |
| Initial output | Valid app/service file map, unrelated docs | Install planned files and manifest, preserve docs | Collision refuses before changes |
| Rerun | Valid manifest, generated files unchanged, edited seeds/custom file | Preserve edits; stable rerun remains coherent | No custom overwrite |
| Generated conflict | One generated file edited/missing, even after earlier valid entries | Refuse complete plan before writes | Existing tree unchanged |
| Unsafe state | Symlink, escape, invalid manifest/identity/classification or overlapping paths | Refuse before destination mutation | Safe identifier |
| Incomplete install | Error or process interruption after some replacements | Journal incomplete; restore previous set before reuse, preserve custom/seed edits | Uncertain state refuses |
| Competing writers | Output already held by live writer | Refuse second writer | No partial competing write |
| Unsupported recipe | Extension or invalid recipe | Existing renderer refusal | No output |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/src/application-renderer.ts`: validated app map; classifications
  already explicit. `service-renderer.ts` supplies shared HTTP files; preserve bytes.
- `src/recipe.ts`, `schema/patterns-v1.json`: references and candidates; do not promote.
- `scripts/test-generation-application.mjs`: fresh private proof, copied root workspace,
  selected offline tools/caches, actual TS/build/API/browser checks and hashes. Reuse
  this qualification rather than create another browser/install harness.
- `tests/application-renderer.test.mjs`: service-byte characterization and app ownership.
- `scripts/process-runner.mjs`: existing bounded subprocess support.
- `README.md`, `APPLICATION_BOOTSTRAP_EVIDENCE.md`: current commands/limits.
- `platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md`:
  thin configuration and consuming proof; accepted decision unchanged.

## Tasks & Acceptance

- [x] `platform/builder-cli/tests/scaffold-preservation.test.mjs`: first observe acceptance
  RED for missing installer, then test every matrix row with disposable trees. Include
  later-file conflicts, byte-identical seeds/custom/docs, generated update fixture,
  injected write failure and actual interrupted child recovery, live-writer exclusion.
- [x] `platform/builder-cli/src/scaffold-install.ts`: small internal validated installer,
  preflight/check/rerun, ownership manifest, staged writes and bounded journal/recovery.
  One active writer and explicit recoverable incomplete state; no blind stale-lock steal.
  Avoid general plugin/hook/recovery framework. Narrow test fault seam if necessary.
- [x] `scripts/test-generation-application.mjs`: install through this primitive in its
  fresh proof; make a benign visible custom shell change and unrelated custom file,
  rerun, assert byte preservation, then existing clean install/type/build/API/browser
  proof. Bind installer source and preservation evidence; final hashes reflect preserved
  owner code. Prior proof directories untouched. No extra command required if this fits.
- [x] `platform/builder-cli/README.md`: describe actual ownership, conflict and recovery
  commands/API, scope and supported limitations. No unsupported public commands.
- [x] Root-owned evidence, mutable scaffold contract and KDG handoff: requirement/test
  traceability, exact results, impacts, remaining public generation/extensions/Access gates.

Acceptance: Given an installed synthetic shell with custom code, when the same recipe
is rerun, then edits survive and fresh installed output passes real type/build/API/browser
checks. Given conflicting or incomplete state, when regeneration is attempted, then
existing custom content survives and unsafe success/build admission is prevented.

## Implementation Notes

No unresolved intent gaps or irreversible external actions. This is dispatch-sized
because filesystem ownership and crash recovery cross tests/installer/proof. Standing
user approval covers the plan and synthetic verification. Agent owns builder files only;
root owns spec/evidence/contract/KDG docs and final verification/commit. Record focused
RED/GREEN logs under deployment/.local/scaffold-preservation; root runs final actual
application proof after review. Do not rerender BMAD or commit. Preserve all other work.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: __proto__ map entry omitted | low / patch | Ordinary next.files object loses own special key; use null-prototype dictionary and regression test. |
| Blind2: recovery lacks exclusive owner | medium / patch | Dead-writer observation alone permits concurrent restore/cleanup and delayed overwrite. Claim exclusive recovery ownership before mutation and test exclusion. |
| Blind3: partial replacement scratch blocks rollback | medium / patch | Scratch bytes are never a restore source; matching every scratch byte to complete payload needlessly blocks valid journal recovery after staging failure. Remove that unnecessary comparison; preserve target/journal validation. |
| Blind4: interrupted cleanup leaves dead lock/no journal | low / reject | Such state fails closed without changing custom/generated bytes. Automatically resolving this small cleanup window needs a new completion protocol; unlikely in everyday disposable proof use. Document the limited journal-backed recovery guarantee and retain uncertain state. |
| Blind5: caught owner metadata write failure strands lock | low / patch | Owner write sits outside try; protect initialization and release the known just-created lock on caught pre-mutation failure. |
| Blind6: caught journal write failure leaves state | medium / patch | Caught pre-mutation staging failure removes lock but leaves partial owned state, blocking reuse. Clean only this writer's known pre-mutation artifacts. |
| Blind7: only first replacement failure covered | medium / patch | Tests exercise one position; add initial/rerun failures through seed/manifest and compare whole previous files and owner content. |
| Blind8: build admission drift negatives absent | medium / patch | checkScaffold negative tests cover interruption only, not generated edits/missing/invalid manifest. Add direct cases with edited seeds accepted. |
| Edge1: concurrent recovery can overwrite newer install | medium / patch | Same demonstrated missing recovery claim as Blind2; private exclusive claim with live PID before restore. |
| Edge2: special map key silently loses ownership | low / patch | Same ordinary dictionary assignment as Blind1; null-prototype map fixes ownership storage. |
| Verification1: generated drift build admission untested | medium / patch | Filed mutation removes checkInternal hash comparison without current test failure; add direct missing/edited negatives. |
| Verification2: initial interrupted rollback untested | medium / patch | Successful recovery only updates existing files; add SIGKILL after seed creation, verify new files/manifest removed and custom/docs preserved, then reinstall. |

## Verification

Selected Node26.11.1/npm12.2.0: builder test, type-check, schema:check. Existing
application proof runs with the exact explicit npm/uv/Python/Chromium/cache selection
from README. Service regression rerun only if its source bindings change. Matrix
coverage audit required. Scaffold gains preservation; shared UI/context need no new
behavior, docs update, accepted ADRs unchanged unless new decision proven necessary.


Implementation verification: acceptance RED retained in red.log, focused10/10 GREEN;
root normal builder38/38, type/schema, service proof-5XZDuI and application proof-874WQD
all pass. Visible custom shell text inspected in mobile screenshot. Matrix audited to
executed tests and actual proof;44 verification bindings unchanged. Review follows.

Review patch outcome: all eleven patch findings addressed in the existing installer,
focused18/18 passing (review-fixes.log). Recovery now claims exclusive ownership;
partial scratch is not authority; caught pre-mutation I/O errors clean only known
owned artifacts. Coverage adds initial SIGKILL rollback/reinstall, multiple write
positions, direct build admission negatives, special path ownership and actual live
competing child refusal. One low cleanup-window finding rejected as documented
fail-closed uncertainty; no completion protocol added. Final reviewed-source checks
follow. Nothing deferred.

Final reviewed-source closeout:46/46 builder tests, type-check and schema:check pass;
application proof-r5WUAZ passes all13 stages including four API tests and actual
Chromium desktop/mobile with preserved customization. Service proof-5XZDuI retains13
matching source bindings. Root verification records44 unchanged source hashes;2521
protected pre-existing files unchanged. All12 findings individually triaged,11 patches
verified, one low rejected, no deferrals. Scaffold/UI/context/docs/ADR impacts and all
seven matrix rows traced in PRESERVATION_EVIDENCE.md. Public generation, extension
import and current Auth/Access remain separate; no candidate promoted.
