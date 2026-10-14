---
title: 'ENV: qualify the pinned KDG toolchain in isolation'
type: feature
created: '2026-10-14'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 1e48e38ced19622973d7d56898f9641322f48cab
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
---

<frozen-after-approval reason="Continuation of the approved bounded ENV foundation and synthetic verification">

## Intent

**Problem:** Prepared targets do not have a reproducible, qualified toolchain. The workstation has Node24/npm11/uv0.12/Supabase2.108 and Python3.12; these cannot substitute for the selected baseline. Docker27 also fails the documented Docker28 minimum for reliable loopback publishing, blocking runtime qualification without an unapproved shared-daemon change.

**Approach:** Complete the next independent increment of existing ENV: checksum-pinned, run-bound installation and actual execution of Node26.11.1, npm12.2.0, TypeScript7.0.2, ordinary CPython3.15.0, uv0.13.1 and SupabaseCLI2.120.0. Provide `python3 platform/deployment/toolchain.py qualify --target <JSON> --run-id <UUID>` through the existing deployment owner. Keep runtime bootstrap and generator gates open.

## Boundaries & Constraints

**Always:** Require an already prepared unchanged target/run and existing dev.py safety checks. Install only Linux x86_64 GNU artifacts in this first qualified platform. Use publisher archives and immutable digest authority in `platform/deployment/toolchain-pins.json`; verify before extraction/execution. Put per-run tools/receipt under ignored `platform/deployment/.local/kdg-toolchains/<UUID>/` and shared verified archive cache under `.local/kdg-toolchain-downloads/`. These are tooling caches, not generated applications or competing frontend install roots. Preserve existing prepared inventory and root/package/owner locks. Hash source/pin/preparation inputs and installed payload in protected qualification evidence. Return `toolchain_ready=true` only after actual exact versions, CPython GIL/platform/stdlib checks and TypeScript valid/invalid type-check fixtures pass; always `runtime_ready=false`.

**Never:** Modify global tools/HOME, use floating latest, unpinned downloaded executables or existing repository node_modules as hidden dependencies. Run npm install/postinstall scripts, change the shared Docker daemon, start containers, provision infrastructure, migrate/grant/create real accounts, implement shared Identity/Access/WRITE, Leave or KDG domain/editor code. No new generator, generic service or lifecycle. No credentials, raw external errors or payload/child output dumps in diagnostics.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior |
| --- | --- | --- |
| Clean qualification | Supported platform, valid prepared run, pinned artifacts | Isolated tools execute at exact pins, compiler accepts valid and rejects invalid code, protected receipt binds payload/source identities |
| Repeat | Identical complete install | Verify integrity before executing; no reinstall or receipt replacement |
| Unsafe run | Missing/changed preparation, foreign owner/root/UUID, symlink/traversal/insecure output ancestor | Safe nonzero refusal before installation/execution; unrelated files untouched |
| Unsafe archive | Digest mismatch, escaping member/link, malformed/unknown pins | Safe nonzero refusal before extraction/execution; no outside write |
| Changed install | Modified binary/file/symlink or stale source/pin/receipt | Refuse, never silently repair/adopt/re-execute |
| Interrupted/concurrent install | Incomplete directory or active installer | Safe refusal or one complete installer; never report partial success or overwrite existing evidence |
| Actual host runtime | Docker27 and no runtime adapter | Record blocker in evidence; qualification never claims runnable Auth/database/generator |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py`: reuse Refusal, decode, read/directory, source evidence and prepare repeat validation. Existing 16 subprocess tests characterize preparation; keep it unchanged if possible. Calling its repeat validation before tool writes is acceptable, but missing run must refuse rather than implicitly prepare.
- `platform/deployment/toolchain-pins.json`: new fixed archive authority with publisher URLs/digests/versions/layout. Node26 archive bundles npm11.20; npm12 must be installed separately. Supabase archive contains supabase and supabase-go. uv wheel executable is under its data/scripts directory. TypeScript package requires its separately pinned native Linux x64 optional package in sibling node_modules.
- `platform/deployment/toolchain.py`: new narrow owning command; no shell execution, user startup/config loading or network mirror fallbacks. Use clean subprocess environments with explicit tool paths and private Supabase state; never repurpose HOME. Verify supported CPython build is GIL-enabled.
- `platform/deployment/tests/test_toolchain.py`: small local archive fixtures for focused guards; public CLI path/refusal tests plus separately executed real qualification command prove actual tools. Tests must not download per test or skip and claim real acceptance.
- `platform/deployment/DEVELOPMENT.md`, `ENV_TOOLCHAIN_EVIDENCE.md`: actual commands, requirement/test traceability, six-tool results, five impact decisions and Docker28/runtime/locks/native-owner/device gates. Root owns KDG next-session/test navigation and final verification.

## Tasks & Acceptance

- [x] Add tests and observe relevant public command acceptance failure before implementation, then focused safety/installer tests.
- [x] Add publisher-verified fixed artifact pins and bounded installer/integrity/receipt implementation under the existing ENV owner.
- [x] Execute real clean qualification and repeat with actual selected binaries, recording outputs without hidden tool dependencies.
- [x] Record five impacts, precise red/green evidence, platform support and remaining enclosing ENV prerequisites; preserve all unrelated changes.

**Acceptance Criteria:**
- Given an unchanged prepared synthetic target, when qualify completes and repeats, then every selected tool actually executes and the immutable receipt remains unchanged with toolchain_ready true and runtime_ready false.
- Given each adversarial matrix state, when qualification is attempted, then it refuses safely and performs no outside or global mutation.
- Given actual Docker27, when delivery evidence is read, then the documented Docker28 loopback gate prevents any claim of runtime qualification and no daemon upgrade or container start has occurred.

## Implementation Notes

This is the implementation handoff inside an already rendered bmad-build workflow; do not activate another workflow. Root performs review/full regression/real network qualification. User approval persists; do not ask again for implementation or owner acknowledgement. Root has verified/downloaded three publisher archives in /tmp/kdg-env-tool-qualification for investigation; do not treat those temporary files as required repository dependencies.

Root completed implementation after the implementation agent became unavailable on continuation. Public acceptance red was observed after setting aside the premature draft; actual qualification exposed npm12 duplicate config handling and TS7 exit1 behavior, both corrected with observed evidence. All6 tools/probes executed under ordinary filesystem sandbox, then real qualify and repeat succeeded for run67110d88-5625-49ef-9ba4-3fe4fa2b7fb5. Receipt1958bytes covers13655 payload entries and remained SHA256644d80f5e20d8bb40ca07be4b4cef144aa8c32a5710ac973efa3119ddf564590. Focused12 and owner147 tests passed before review. Concurrent Leave epics/plan/handoff changes are excluded from this delivery diff and preserved.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| Blind1: ambient TypeScript types | medium | ignoreConfig does not exclude ancestor @types; patch explicit empty typeRoots and execution tests. |
| Blind2: receipt changes during repeat | medium | Final comparison rereads the decoded object, not the protected file; patch end-of-execution bytes/identity validation. |
| Blind3: pin snapshot mismatch | medium | load_pins and binding hash read separately can describe different versions of the same file; patch one captured byte snapshot. |
| Blind4: shared-cache hard-link interval | medium | Publication briefly has nlink2 while another run verifies nlink1; patch bounded per-artifact serialization and concurrent-cache proof. |
| Blind5: archive limits after indexing | low | getmembers allocates before the existing limit checks; move the same checks into incremental enumeration. |
| Blind6: progressing download has no total deadline | medium | Socket timeout resets as progress arrives; patch monotonic total budget with bounded read1 operations. |
| Blind7: truncated HTTP/compression exception paths | medium | IncompleteRead/EOFError can bypass safe refusal; patch explicit relevant exception classes and negative tests. |
| Blind8: output ancestor replacement | medium | Ownership checks release FDs before path-based writes; patch pinned directory descriptors and replacement proof. |
| Edge1: planned symlink graph escape | medium | a -> dot and b -> a/a/../../outside defeats lexical normalization; patch graph resolution before extraction plus real resolved payload-link checks. |
| Edge2: receipt changed during execution | medium | Same observed stale decoded receipt as Blind2; grouped for end-of-execution protected-file check. |
| Verification1: wrong-version/compiler-result rejection coverage | medium | Successful fixtures stub execute and real positive probe cannot detect removed negative checks; patch controlled subprocess rejection tests. |
| Verification2: cached integrity not exercised end-to-end | medium | Direct verify_digest tests do not cover verified_archive or extraction ordering; patch corrupted-cache path and no-receipt/no-extraction proof. |

## Verification

- `python3 -m unittest discover -s platform/deployment/tests -p test_toolchain.py -v` — focused guards pass after red.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` — owner regression passes.
- Actual prepared-run `toolchain.py qualify` and repeat — six exact versions/compiler/GIL checks pass with protected unchanged receipt; runtime remains false.
- Scoped whitespace and documentation link checks pass.

## Final review resolution and delivery result

All twelve review findings were patched and verified; none were deferred. Initial
review regressions reproduced pin/receipt/link/transport defects before the fixes.
Output writes now retain validated directory descriptors, cache publication is serialized,
download/indexing limits apply during processing, and executable negative checks are
covered. The native compiler grandchild closure issue found by actual qualification
is fixed with owner-process descriptor paths and a regression test.

Final commands and results:

- `python3 -m unittest discover -s platform/deployment/tests -p test_toolchain.py -v`:
  23 tests, 4.471s, OK.
- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  158 tests, 36.861s, OK; isolated socket permission used.
- `python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id afd91508-2c2d-448e-a4f0-eed79e3c9a68`:
  exit0, prepared, runtime_ready=false.
- `python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id afd91508-2c2d-448e-a4f0-eed79e3c9a68`:
  clean qualification and repeat exit0, toolchain_ready=true, runtime_ready=false.
  Receipt remains mode0600, 1958bytes, 13655 payload entries, SHA256
  `7eb397f18739e2853199591fc54f19f43c121e6a85e781aa6de337fb97407091`.
- Scoped tracked/untracked whitespace and relative documentation-link checks: PASS.

Requirement-to-test mapping, exact qualified scope, five impact decisions and runtime
limits are in platform/deployment/ENV_TOOLCHAIN_EVIDENCE.md. KDG navigation and memlog
point there. Existing ENV still needs Docker>=28/runtime qualification before dependent
foundations; this completed toolchain increment does not close enclosing ENV/P1/SERVICE.
Concurrent Leave/PtS planning changes remain preserved and outside this commit.
