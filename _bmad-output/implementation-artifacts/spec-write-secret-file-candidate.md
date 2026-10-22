---
title: Copyable KDG fingerprint secret-file loading prerequisite
type: feature
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 8f14364a6549f36e775873131d34dee3c3f3adc0
context:
  - AGENTS.md
  - platform/docs/architecture/contracts/owned-write-and-secret-execution.md
  - platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md
---

<frozen-after-approval reason="user says next under standing bounded WRITE synthetic local/CI implementation approval">

## Intent

After completed fingerprint and atomic-write candidates, supply the next missing
prerequisite: a small owner-copied KDG fingerprint secret-file loader, with real local
filesystem permissions and separate-process retry proof. Reuse the existing fingerprint
helper and scaffold importer. Keep release backup/recovery and business APIs gated.

## Boundaries & Constraints

Accept public-safe KDG_FINGERPRINT_ACTIVE_KEY_ID, KDG_FINGERPRINT_SECRET_DIR,
DEPLOY_ENV and KDG_OWNER_ID=kdg_capture configuration as explicit validated inputs;
no key bytes in configuration strings, argv, logs, database or frontend. Require
actual runtime effective UID/GID10001, directory UID/GID10001 mode0700 and regular
file UID/GID10001 mode0400. Reject symlinks, nonregular files, bad permissions or
namespace without repairing them. Key IDs use existing1–64 ASCII letters/digits/_/-
grammar before joining paths. Read only requested <key_id>.json with bounded reads,
descriptor-based path/type/ownership checks and safe errors. Reject duplicate/unknown
fields and invalid UTF8/JSON. File fields are exactly schema_version integer1,
owner_id kdg_capture, environment_id matching explicit execution environment, key_id
matching filename, key_b64 canonical Base64 of exactly32 decoded bytes. Keep material
out of object representations and exception chains. No implicit key generation, fallback,
environment adoption or digest rewrite. Missing/bad active key refuses write readiness;
missing/bad old key uses operation_verification_unavailable and preserves outcomes.

Use approved Python3.15/rfc8785 and standard library, no new pins/locks. Synthetic
random files only in fresh ignored ENV proof runs. Linux user namespaces provide actual
UID/GID10001 kernel checks without account changes: record uid/gid maps explicitly.
This proves local mapped identity, not deployed host ownership or read-only mounts.
Preserve concurrent work, historical proof and Docker resources. No provisioning,
production/real-account/access, deployment/pilot, resource cleanup, Leave/editor, KDG
business API, backup service or public scaffold promotion. Independently encrypted
secret archive and matching data restore remain later explicit release inputs.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Valid protected matching active file | Load selected material; existing fingerprint helper executes |
| Restart/rotation/old-release active key | Separate processes verify retained outcomes by recorded key; new creation selects explicit active key |
| Missing active/old key, malformed schema/Base64 or wrong namespace | Safe refusal; no fallback, mutation or key generation |
| Traversing key ID, symlink, FIFO/device/directory, oversized input | Bounded refusal before unsafe content use; no blocking FIFO |
| Incorrect directory/file owner, mode or effective identity | Refuse without permission weakening or repair |
| Error/repr/traceback and actual installer replay | No material/content leakage; copied siblings execute and owner edits/provenance survive |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/examples/owned-service/command_fingerprint.py`: reuse existing key-ID grammar, create/verify functions and error vocabulary; preserve bytes.
- `platform/builder-cli/src/scaffold-install.ts`, `tests/test_command_fingerprint.py`: actual extension copying/provenance/preservation, no generator changes.
- `platform/deployment/dev.py`: secure directory-descriptor precedent; reference only, never import deployment runtime into copied owner.
- Prepared Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`. Prepared Node: `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.

## Tasks & Acceptance

- [x] Add `platform/builder-cli/examples/owned-service/fingerprint_secret_files.py`: read-only closed KDG configuration/loading candidate with safe material representation; no generic keyring engine.
- [x] Add `platform/builder-cli/tests/test_fingerprint_secret_files.py` and a small subprocess fixture if needed: ATDD missing-module RED before production, focused TDD, actual mapped UID/GID/filesystem and subprocess restart/rotation/retained retry; real installer copying/preservation. No silent skips; retain synthetic files.
- [x] Update `examples/owned-service/README.md`, add `WRITE_SECRET_FILES_EVIDENCE.md` and prepend current `apps/kdg-capture/docs/next-session.md`: exact commands/results, traces, limits and five impact decisions. Root owns evidence/handoff.

Given a retained original fingerprint and protected files, when a restarted process
runs after rotation, then it verifies only through the original recorded key. Given
wrong/missing material or namespace, when loading, then it refuses safely and leaves
original files/metadata untouched. Given approved local proof, when inspected, then
actual kernel ownership/modes and explicit namespace maps substantiate its scope.

## Implementation Notes

No unresolved intent gaps or real-world irreversible actions; existing approval covers
dirty-tree preservation. Root owns initial RED, final verification/review/audit and
scope-only local commit. Agent owns helper/tests/README, no staging/commit. Proof D:
`platform/builder-cli/.local/write-secret-files-20261022`. Synthetic file roots belong
under ignored `platform/deployment/.local/write-secret-files-20261022`, unique per run.
Run focused tests via `unshare --user --map-user=10001 --map-group=10001 <prepared Python>
-I -B -m pytest ... -q -p no:cacheprovider`, with explicit FINGERPRINT_TEST_NODE and
SECRET_TEST_RUN_ROOT absolute paths. Confirmed actual maps are10001→host1002; no sudo,
Docker or account change needed. No production mount/archive claims. Use finite small
file/document bounds and exact environment string equality; consumers own transport
readiness and matching data/secret recovery. Keep APIs small and owner-specific.

Review patches change focused tests/README only. Actual ownership is exercised via
mapped IDs and unmapped foreign descriptors; isolated UID/GID negative tests use
metadata fault injection with otherwise valid kind/modes. Subprocess overlap executes
the same implementation under old/new active configuration; it makes no distinct
release-version compatibility claim. Root final audit separately preserves earlier
atomic proof source/artifact hashes. No new dependency or production surface.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1: pytest failure diagnostics can dump secret/receipt/child bytes | medium | Rewritten assertions compare raw file/receipt bytes and captured child output; failing tests could retain material. Patch fixed safe preservation/output checks and an intentionally failing subprocess canary proof. Current successful logs show no actual leak. |
| Blind2: wrong-owner cases also have wrong modes | medium | /etc0755 and passwd0644 refuse even without UID/GID checks. Patch otherwise-valid directory/file metadata fault cases independently for UID/GID, retaining actual foreign-descriptor evidence. |
| Blind3: unavailable active key with valid recorded key untested | medium | Success cases all retain the active file; patch missing/malformed active file with successful old-key verification and independent active refusal, preserving originals. |
| Blind4: old-release wording overstates code-version overlap | low | All subprocesses execute identical code with different active IDs; direct documentation/test-name correction to old-active configuration overlap. Actual release-version compatibility stays unclaimed. |
| Blind5: in-place inode mutation not exercised | medium | Current replacement case changes pathname/inode only; patch actual in-place mutation during chunked read and safe refusal. Both FD and pathname signature checks remain. |
| Blind6: exact4096/read-growth boundary not exercised | medium | Oversize test refuses by initial stat; patch4096-byte valid acceptance and growth after fstat with4097 total-read ceiling. |
| Verification1: ownership checks masked by invalid permissions | medium | Pre-verified same root as Blind2; patch isolated directory/file UID/GID metadata cases with correct kind/mode and retain real kernel-positive/foreign descriptors. |

| Root: in-place rewrite could refuse through invalid JSON instead of metadata | medium | Byte20 mutation can corrupt schema; replace with a different canonical same-length key_b64 while retaining valid exact schema/namespace. Then the chunked read must refuse although a fresh read of the completed file succeeds. Direct test correction. |

Edge-case review returned no findings. All surviving entries route to direct test/doc
patches; no production helper defect or new public API is required. No deferrals.

## Verification

Focused namespace pytest plus unchanged fingerprint63 and existing Node builder62
checks; actual scaffold copy included. Atomic candidate sources stay untouched; no
native DB startup needed. Audit scoped diff and pre-existing hashes. Scaffold: candidate
copy/import only. Shared UI unchanged. Agent context unchanged. Docs guide/evidence/
handoff. ADR unchanged. Explicitly report production ownership/mount/archive/recovery
and first-consumer gates; no new lifecycle or duplicated feature specifications.


## Completion

Root missing-module acceptance RED preceded production source; focused behavioral RED
for strict path configuration preceded its correction. Final reviewed namespace128
checks PASS (65 secret-file/63 fingerprint), existing builder62 PASS, no skips.
Three review lenses complete; direct test/doc corrections verified, no new deferrals.
Independent read-only retained inspection PASS. Audit binds6 execution sources,
21 proof inputs/logs and818 retained fixture files;17 logs exclude191 synthetic keys
and27 outcome digests.37 dependency inputs unchanged; prior atomic8 sources/28 proof
inputs match. Concurrent Leave/Scribeswell work preserved/excluded. No Docker, real
accounts/access, host chown, provisioning/deployment/pilot/cleanup or push. Scope-only
local Build commit. Production ownership/mounts, encrypted archive/matching data
restore, release and first-consuming business APIs remain gated; see owner evidence.
