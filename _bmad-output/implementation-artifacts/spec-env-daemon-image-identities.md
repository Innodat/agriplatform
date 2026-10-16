---
title: 'ENV: verify daemon-local qualified image identities'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: d489f264fea508a9b0175447b32930934232fae0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded foundation implementation and synthetic verification approval; user requested Next">

## Intent

**Problem:** Retained manifests select immutable references, but startup fixtures invent
image IDs. No adapter verifies that the daemon resolves those references to the
expected config identities before future execution.

**Approach:** Extend the existing image owner with verified config identities, inspect
all four selected local images through the existing Docker transport, and transfer
the observed metadata into the guarded startup fixture. Keep container execution off.

## Boundaries & Constraints

**Always:** ATDD red before implementation, focused TDD, unchanged approved dependency
pins and owner boundaries. Preserve concurrent Leave/PtS work and old receipts.
Derive child/config identities from owner-verified retained bytes, not caller assertions.
Inspect exact child-reference then exact config ID; require Id equal retained config
digest, Os=linux, Architecture=amd64, absent/empty Variant. RepoTags/RepoDigests are
not authority and may be absent/index-only. Return only selected safe identities;
never retain Config, env, paths, timestamps or response/error dumps.
Require current protected preparation/tool/image/source evidence before daemon access;
Linux Docker>=28 before image inspection. Recheck evidence and selected observations
before successful return. Reuse protected same-run lock. Bound the daemon phase to
five seconds total with existing framing/byte limits. Owner repeat qualification
runs outside that deadline with its existing bounded tool probes. Fixed local socket;
private test injection only, no public endpoint override. Missing images refuse without
pull, tag, import, repair, retry or deletion. Each verification observes afresh.

**Never:** Real Docker mutations, layers/config-blob downloads, containers, SQL,
migrations, grants/accounts, provisioning, deployment or pilot use. No activation of
up or dependent Identity/Access/WRITE/Leave/KDG. No alternate transport/generator or
offline service. No claim of independently hashing daemon bytes, daemon continuity
across separate connections, execution enforcement, helper completeness or runtime
readiness. Keep runtime_ready=false and first-create refusal. Separate startup proof
transfers descriptors; it does not extend the observation lock through execution.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Four exact child references/config IDs available | Two inspections per image, minimal verified metadata, guarded fixture handoff |
| Missing image or different config/platform | Safe refusal; no mutation/fallback |
| Plausible tags/index-only RepoDigests | Neither authorizes nor invalidates matching ID/platform |
| Missing/stale/tampered owner evidence | Refuse before daemon access; no collection/repair |
| Changed preparation/source/receipt/lock/observations | No successful result |
| Old daemon, malformed/oversized/slow/error response | Bounded safe refusal; no sensitive output |
| Foreign repository/tag/index/path/query or arbitrary plan | Refuse before unauthorized request |
| Repeat or concurrent run checks | Fresh observations, bounded same-run serialization, distinct-run isolation |

</frozen-after-approval>

## Code Map

- `platform/deployment/images.py:retained,document,qualify_evidence`: expose a closed
  four-image child/config plan while retained files are verified/held. Preserve existing
  selection_plan and receipts. Config digest is in child manifest; no blob is needed.
- `startup.py:existing_images`: retain its owner-repeat and snapshot guards; carry the
  additional plan through this internal boundary. Update internal tuple users together.
- New `platform/deployment/daemon_images.py`: reuse dev transport/preparation and
  networks.run_lock. Verify owner provenance, inspect only closed digest references
  and config IDs, snapshot/recheck evidence. No CLI dispatch or public real-daemon command.
- `dev.py:docker_exchange,SOURCES`: add only GET v1.48 image-inspect routes for the four
  public.ecr.aws/supabase repositories at sha256 and sha256 config IDs; no query/options,
  tag, list, pull or container route. Bind adapter/qualifier sources; update test_dev FILES.
- `startup.py:fixture_command,install_fixture,synthetic_probe` and
  `tests/qualify_startup.py`: public proof consumes acquired image observations rather
  than fabricated IDs. Internal unit fixtures may supply explicit synthetic profiles.
  Verify both forwarding hops with observation-specific evidence; missing/foreign
  descriptors refuse before image/create events. Preserve immutable first-create logic.
- New `tests/test_daemon_images.py`, `tests/qualify_daemon_images.py`: independent literal
  API oracle/private Unix daemon, complete ordered event assertions and safe controls.
  Reuse owner integration fixtures from test_images/test_startup_adapter. No production
  map used as the independent expected answer.
- Docker28 `api/types/image/image_inspect.go` defines Id as config digest, distinct from
  RepoDigests. `api/server/router/image/image_routes.go:getImagesByName` resolves name
  via ImageInspect; no v1.48 platform query is assumed. Keep the64KiB transport limit;
  oversized real metadata remains a documented qualification failure.

## Tasks & Acceptance

- [x] Observe acceptance failure, implement owner plan and bounded daemon checks.
- [x] Prove every matrix row and actual owner→public qualifier→CLI fixture transfer;
  removing either transfer must fail a test. Preserve container refusal.
- [x] Run focused/affected regression and public synthetic controls, including actual
  pinned CLI proof on fresh owner-qualified evidence; record exact results.
- [x] Record requirement/test and scaffold/UI/context/documentation/ADR impacts in
  `platform/deployment/ENV_DAEMON_IMAGE_EVIDENCE.md`, DEVELOPMENT.md, KDG navigation/memlog.
- [x] Independent review, fixes, final verification and scoped local commit.

**Acceptance:** Given current qualified evidence and matching private daemon images,
when verification and startup proof run, then exact owner config identities reach
the CLI fixture and first create is refused. Given unsafe/missing/changed inputs,
when verification runs, then no unverified handoff or daemon mutation occurs.

## Implementation Notes

No intent gap or irreversible action. Existing approval covers this bounded owner
increment. Implementer owns code/tests/runbook; root owns evidence/navigation/memlog
and final qualification. Source changes require fresh UUIDs, never receipt repair.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind 1: lower fixture accepts structurally valid unrelated IDs | false: `startup.qualify` checks the owner config plan before calling the fixture; direct fixture APIs intentionally accept explicit synthetic profiles for internal tests. No public bypass was demonstrated. | reject |
| Blind 2: wrong ID under valid child key untested | medium: existing tests reject foreign keys, but do not exercise the owner-config comparison. | patch |
| Blind 3: negative image controls only fail early | medium: later child/config responses are processed by the loop but rejection at those positions lacks regression evidence. | patch |
| Blind 4: same-byte replacement/restore untested | medium: metadata comparisons were added to detect these changes; existing mutation cases only leave changed bytes. | patch |
| Blind 5: missing evidence test does not remove files | medium: overwriting with `{}` does not cover public safe refusal for absent receipts. | patch |
| Blind 6: public sensitive-output cases untested in checked-in suite | low: public runner checks these outputs, but the repository regression tests only assert internal exception codes. Add direct public-main cases. | patch |
| Blind 7: late deadline coverage absent | medium: the existing timing test expires early; later config checks and final evidence accounting need targeted coverage. | patch |
| Blind 8: negative event validation races the handler | false: dispatch records every event before sending the response; slow control returns after its wait without appending an event/error. The specified controls do not mutate the event oracle after client refusal. | reject |
| Verification 1: startup owner-config comparison lacks negative case | medium: verified gap matches Blind 2; removing the comparison would leave existing tests green. | patch with Blind 2 |

Edge-case review returned no findings. Thread limits required sequential reviewer launches;
all three completed before triage. Seven finding instances group into six test patches;
no production-surface change or deferral is needed.

## Verification

Focused test_daemon_images.py, affected test_images.py/test_startup_adapter.py and
test_dev.py, then all deployment test_*.py. Fresh prepare/tool/image qualification,
public private-daemon controls and pinned CLI startup proof. Preserve evidence hashes,
identities/modes/mtimes; compile, scoped whitespace and documentation-link checks.
Whole public harness allows owner revalidation time separately from daemon deadlines.

Implementation matrix audit: focused daemon10/startup 38/image 34 checks pass; all eight matrix rows are covered, including distinct-run locks and omitted forwarding hops. Public pinned-tool controls and final sequential regression subsequently passed.

Review patches verified: daemon 16 and startup 38 pass. Added wrong-ID provenance, late failure prefixes, same-byte replacement/restored writes, public missing/sensitive-output checks and late/final deadlines. Bound production/qualifier sources unchanged; root read the patch and refreshed the scoped diff.


Final verification: 315 deployment tests pass in 57.409s; all 17 public controls pass
on fresh run 26946863-91af-4e92-b9bd-ceca8201bcf2. Protected record SHA-256
`4e39af62be7858040f68b061656fd24094a4b99235c79c253d23048725fe74ab`.
Thirteen evidence files/source bindings unchanged; actual `up` safely refuses
`docker_28_required`. Python compile, scoped whitespace and local links pass.
Requirement/test traceability, attempts, exact commands and five impacts are in
[owner evidence](../../platform/deployment/ENV_DAEMON_IMAGE_EVIDENCE.md).
Seven reviewer instances fixed, two disproved, none deferred. Scoped local commit only;
concurrent Leave/PtS changes preserved. Enclosing ENV runtime and P1/SERVICE remain open.
