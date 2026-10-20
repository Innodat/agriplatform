---
title: 'Explicit scaffold extension import and preservation'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: 'f85d8e510b3fc66827155403eae46d17ea26fcc9'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing shared-foundation implementation approval and next after safe reruns">

## Intent

The builder preserves seeds but cannot import a declared custom module. Extend its
existing internal installation path to copy explicit extension source into disposable
output once, then preserve application ownership on reruns. Prove an imported module
actually contributes to the built shell after owner edits and source changes.

## Boundaries & Constraints

Use existing version1 recipe declarations, renderers, installer/journal and application
proof. Candidates stay generation_ready:false; no public generation/bypass command or
another generator. Imports are create-once custom content: edits, additions and deletions
are owner maintenance and never trigger recopy. Record source/destination and initial
file hashes separately from generated authority. Existing extension-free v1 manifests
remain supported; extension metadata must have an explicit validated version. Installed
import declarations/recipe identity and file ownership cannot silently change.

Initial imports validate all source entries and all destinations before any target
writes. Refuse symlinks (including descendants/dangling), special files, escapes,
source/output overlap, installer/.git metadata and destination overlap with generated,
seed or other extension roots. Existing destination content is a collision, not merge
permission. Import only bounded valid UTF-8 source files for this increment; reject
binary input, huge/deep trees and unsafe names. Do not infer dependencies or execute
extension code during copying. Reruns use the installed inventory without enumerating,
reading or requiring the old source directory; output must be self-contained.

Preserve generated conflict checks, seed rules, live writer/recovery exclusion and
journal-backed rollback. Interrupted initial imports may be rolled back only with
known unchanged bytes; unknown owner edits refuse safely. Preserve all previous proof,
source/state/resources and concurrent documents; exact baseline including TS7.0.2.
No Auth/Access implementation/promotion, dependency changes, Leave/editor, owner
migrations, account/provider changes, Docker/provision/deploy or real data.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Initial module | Explicit safe text source and disjoint destination | Exact copy, custom ownership and provenance | No hidden source dependency |
| Owner maintenance | Edited/deleted/import-added files; source changed or absent | Rerun preserves owner state without source reads | No recopy |
| Unsafe import | Symlink/special/binary/escape/limit or source/output overlap | Refuse complete plan before target writes | Safe identifier |
| Destination collision | Base seed/generated/custom file or overlapping declarations | Refuse all writes | Existing bytes unchanged |
| Existing output | Legacy no-import manifest or changed import identity | Legacy continues; undeclared adoption/conversion refuses | No silent import upgrade |
| Interrupted import | Failure/SIGKILL after imported writes/manifest | Restore complete prior set; refuse unknown edits | Existing journal limits remain |
| Real consumption | Imported typed module edited, rerun, original source unavailable | Type/build/API/browser and rendered owner behavior pass | No unregistered or skipped suite |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/src/recipe.ts`: version1 declarations/preflight; public initial
  validation stays intact. `application-renderer.ts`/`service-renderer.ts`: existing
  candidate base maps; preserve no-extension bytes and rejection boundaries if possible.
- `src/scaffold-install.ts`: existing ownership manifest, complete preflight, writer/
  recovery claims and old/new journal. Import inside this lock before staging; reuse
  recovery, no separate copier/journal lifecycle. Optional internal import input can
  carry repository root/declarations. Private harness may render an extensions-empty
  base recipe and pass actual declared imports to installer; no new public bypass.
- `tests/scaffold-preservation.test.mjs`: characterization of prior behavior, real
  SIGKILL/ENOSPC/live ownership tests. Keep them passing.
- `scripts/test-generation-application.mjs`: unique ENV proof; explicit tools, copied
  workspace/root lock, real strict/build/API/browser qualification. Reuse this harness.
- `templates/application/web/scripts/browser-smoke.mjs`: add bounded proof assertion of
  imported rendered text, e.g. optional explicit expected text. Ordinary shell stays valid.

## Tasks & Acceptance

- [x] `tests/scaffold-extensions.test.mjs`: observe acceptance RED, then cover every
  matrix row, real import rollback and missing-source replay; preserve old tests.
- [x] `src/scaffold-install.ts` and small internal helper if justified: initial bounded
  import planning, explicit provenance/custom ownership, compatible manifest parsing,
  safe regeneration/admission/recovery with no source reads after installation.
- [x] `scripts/test-generation-application.mjs`: create synthetic source in its fresh
  ignored proof, declare/import a typed module, wire owner App seed to it, edit imported
  behavior and change/remove synthetic source. Rerun and assert exact owner state;
  run existing clean type/build/API/browser checks and assert rendered custom behavior.
  Bind new sources/output/provenance; keep all earlier outputs unchanged.
- [x] `README.md` and owning browser template if changed: document actual import limits,
  commands and ownership; no unsupported public generate claims.
- [x] Root evidence/contract/KDG navigation: exact requirement/test traceability and
  scaffold/UI/context/docs/ADR impacts, compatibility and remaining gates.

Given a declared module, when initial output is installed and owner edits are rerun,
then the self-contained module remains owner-owned and works in the real built shell.
Given unsafe/conflicting/interrupted input, when import or rerun is attempted, then
existing custom/generated bytes are preserved and unsafe success is refused.

## Implementation Notes

No unresolved intent gaps or irreversible external actions. Bounded text import is
needed now; binary assets, later import additions/upgrades and dependency discovery
remain separate consuming needs. Agent owns builder files; root owns spec/evidence/
contract/KDG docs and final proof/commit. No BMAD rerender or commit by agent. Focused
RED/GREEN logs under deployment/.local/scaffold-extensions; root runs final full checks.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: declaration key order changes identity | low / patch | JSON.stringify compares raw declaration key order to reconstructed fields; normalize source/destination fields before comparison. |
| Blind2: empty directories not reproduced | low / reject | Current scope imports UTF-8 source files, not directory-only state. Empty directories carry no module behavior; document omission rather than add directory ownership/recovery. |
| Blind3: source swaps to symlink between stat/read | low / reject | Requires external mutation of the private initial-source snapshot; current isolated proof has one owner and stable inputs. Descriptor-relative hostile-filesystem handling would add unsupported machinery; explicitly document quiescent source/output scope. |
| Blind4: concurrent growth can allocate beyond byte limit | low / reject | Static files are checked before reading and changed length refuses. Growth during import requires unsupported external source mutation; bounding a hostile concurrent writer is outside this controlled snapshot proof. |
| Blind5: directory names materialized before entry cap | low / patch | A static wide source directory is reachable even without concurrency; use bounded directory iteration before sorting known entries. |
| Blind6: case-folded names and .GIT accepted | false / reject | Qualified output is Linux case-sensitive: Module.ts/module.ts and .GIT/.git are distinct paths; portable segment syntax does not claim case-insensitive filesystem support. Actual .git metadata is refused. |
| Blind7: unknown post-crash custom files leave retry collision | medium / patch | Initial destination was absent, so unexpected children make rollback ownership uncertain. Preflight full known import directory inventory and refuse before changing known files. |
| Blind8: import cleanup target checked after mutation | medium / patch | Empty import metadata can reach cleanup with a replaced directory; validate all import directory types/children before restore, then remove only known empty directories. |
| Edge1: source symlink swap after validation | low / reject | Same unsupported externally mutated initial snapshot as Blind3; stable controlled source required, no hostile descriptor framework. |
| Edge2: source growth before read | low / reject | Same concurrent mutation assumption as Blind4; no accepted-static-input byte-limit bypass. |
| Edge3: late owner creation can be overwritten | medium / patch | Initial rename can replace a newly appeared target. Publish new files exclusively using the existing same-filesystem stage; retain unknown bytes and recovery evidence on collision. |
| Verification1: multiple successful imports untested | medium / patch | Filed slice(0,1) mutation could drop later declarations unnoticed. Add two disjoint successful imports/provenance, missing-source replay and declaration key-order replay. |

## Verification

Selected Node26.11.1/npm12.2.0: builder test, type-check, schema:check; real existing
application proof with qualified uv/Python/Chromium/cache. Service proof rerun only
when bound files change. Scaffold gains explicit import; no shared UI promotion or
root context change. Existing0059/ownership ADRs suffice; accepted decisions unchanged.


Implementation verification: host-node24 initial acceptance failure and selected26
untouched-baseline RED replay timing retained explicitly. Focused28/28; root56/56,
type/schema, service proof-ZxlpHi and application proof-UkL6wo pass on45 unchanged
verification source bindings. All seven matrix rows map to executed tests/actual proof.
Wrong-text browser negative fails correctly, confirms teardown and preserves the
passing output. Root owns application harness/browser work; agent implements installer,
new tests and README. Review follows.


Review fixes: six patch findings addressed in existing installer/tests,32/32 focused
extension/preservation tests pass (revision-green.log; revision-red.log retains the
new regression failures). Import key-order equivalence, two-module replay, bounded
directory traversal, all-directory recovery preflight and exclusive first publication
are verified. Five low concurrency/empty-directory findings rejected with documented
controlled-snapshot limits; case-insensitive-platform finding false for qualified
Linux. No deferrals. Final reviewed-source suite/application proof follows.


Final closeout:60/60 builder tests, type/schema checks and application proof-GyYZQO
pass on45 unchanged verification source bindings. Real imported behavior checked in
Chromium before/after reload; four API tests pass. Service proof-ZxlpHi retains13
matching sources; prior wrong-text negative stays tied to unchanged browser template.
All seven matrix rows covered; review six patches verified, five low rejections and
one false finding recorded individually, nothing deferred.2523 protected prior files
unchanged. Five impact decisions and exact evidence in EXTENSION_EVIDENCE.md. Public
generation and current Auth/Access remain pending; no readiness promotion.
