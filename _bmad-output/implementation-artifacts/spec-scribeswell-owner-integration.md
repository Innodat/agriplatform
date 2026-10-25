---
title: 'Qualify personal Studies through actual owner services'
type: 'chore'
created: '2026-10-25'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'aa2ce1ec8d1c12e922715c9c3631f2dbbfa4eb6d'
context:
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/services/access/STUDIES-ENROLLMENT.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Approved runtime b7b292fc5c0e28eea3b526e13e359bb2bad5f392 proves saving with synthetic Access responses; the browser-to-app-to-owner chain needs integrated evidence.

**Approach:** Qualify explicit enrollment, create, autosave and reload through actual Scribeswell, Access, Identity and local Supabase Auth using fresh synthetic accounts in one new disposable run.

## Boundaries & Constraints

**Always:** Preserve dirty/concurrent work and existing owner implementations. Use the native Supabase CLI wrapper and ordinary owner migrations, restricted runtime credentials, actual provider-issued sessions, and HTTP between applications/services. Keep setup/oracle SQL confined to the new synthetic fixture. Use ATDD/TDD; record observed failures, commands, sources and outcomes. Stop only owned processes and the exact new wrapper run, retaining private evidence.

**Never:** Mutate/resume retained runs, enable production, deploy/push, change provider configuration, send external mail, fabricate tokens, mirror Auth accounts into stubs, mock protected HTTP, add competing Access/Auth/environment lifecycle or implement Leave/factory. Standalone signup remains required but unqualified: the wrapper disables it. No default Access startup/readiness or physical-device claim.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Fresh provider-verified synthetic reader opens public reader/Studies before enrollment | Actual Identity profile exists; zero organization memberships, Studies grant or study. Protected access refuses safely; public reading works. |
| Reader explicitly enrolls, creates and writes Hebrew/combining marks | Actual Access checks and restricted app SQL acknowledge current content; reload/reopen returns identical text and durable attribution. |
| Second enrolled account requests the first account's resources/outcomes | No private data or unauthorized effect; browser never receives service credentials. |
| Original enrollment/create reply is lost, then original operation retried | Discard only a real completed reply; current eligibility is rechecked with no duplicate effect or replaced operation. |
| Application authority is disabled through the existing protected operator | Subsequent read/write/lookup denies; public reading remains available. |
| Preparation/migration fails, ports are occupied, or execution is interrupted | No app startup on failed preparation, no adoption/reset/cleanup of another run; report failure honestly and stop owned work. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `S=services/access`, `P=platform/deployment`.
`P/DEVELOPMENT.md` first125lines / `P/native_cli.py` define the current wrapper,
superseding historical interception gates. Reuse `P/dev.py prepare/up/verify/stop`,
`P/environments/kdg-local.json`, new UUID and CLI2.120.0. Fixed ports/origins are
contractual; refuse collisions. This starts no KDG app. Config disables signup/mail:
use local synthetic admin-created accounts and real magic-link verification.

`S/main.py:create_app` accepts real `studies_identity.AsyncDatabase` connections;
leave provider verification unchanged. This test seam bypasses release-artifact
startup validation; it proves HTTP/domain integration only. Separate owner/app
processes avoid module-name collisions. Existing owner Alembic/configs and
`S/tools/prepare_*` own roles, Auth hook/evidence and ordered upgrades. Register app
and permission through protected operator commands; seed no user grants.
`S/tests/qualify_studies_enrollment.py` is reference only: its retained RUN/PRIOR,
Auth-stub clones and source-reference writers must never execute here.
`A/tests/test_personal_notes_storage.py` supplies restricted app SQL and bounded
browser orchestration patterns. Use actual `A/backend/main.py:app`, a minimal public
corpus sample and private history. Vite proxies private HTTP; callback origin is
localhost5188. Existing browser setup fakes sessions/private responses: use a separate
integration config/spec instead.

## Tasks & Acceptance

- [x] `A/tests/test_studies_owner_integration.py`: add missing-capability acceptance plus focused orchestration/failure checks; no skipped case counts as proof.
- [x] `A/tests/studies_owner_fixture.py`: new fixture-only setup/oracle using existing wrapper, private status capture, owner role preparation/migrations, actual Auth profiles/principals and restricted app SQL. No general provisioner or runtime owner code.
- [x] `A/tools/py/qualify_studies_owner_integration.py`: explicit one-run entry, bounded subprocesses, protected secrets/results, setup-before-start, independent SQL observations and exact-run normal stop. Refuse existing/unowned inputs; retain partial failure evidence.
- [x] `A/web/playwright.owner-integration.config.cjs`, `A/web/tests/studies-owner.integration.cjs`: real provider callback/session, enrollment/create/write/reload, isolation and denial/retry observations. No private API/Auth interception or session-storage injection; disable private traces/payload logging.
- [x] `A/docs/PERSONAL_NOTES_V1.md`, `A/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md`: exact executed evidence and remaining signup/startup/release/device gates; reconcile canonical memory through bmad-spec.

Given the fresh native run, when the integrated browser scenario finishes, then
independent SQL confirms acknowledged text, account/actor binding and no duplicate effects.
Given failed owner preparation, when qualification is attempted, then app processes
never start and unrelated resources remain unchanged.

## Implementation Notes

All five tasks and six frozen matrix rows audited against the actual fixture/browser diff and executed run41b8351e-bcc4-4128-ac22-d7ef3dc561b3. Parent inspected both passing browser logs, SQL zero-effect/value/attribution/count observations, exact-run stop0 and all173 source hashes; parent focused command passed11 tests9.44s. Fixture-control doubles are distinguished from native proof. Canonical event247 and derived status preserve11CAP/38ST/24companions and remaining gates; independent review follows. Exact commands and every earlier failure are in the [integration evidence](../../apps/scribeswell/docs/STUDIES_OWNER_INTEGRATION_EVIDENCE.md).

## Spec Change Log

2026-10-25: no frozen-intent change or loopback. Direct review corrections strengthen only the existing fixture/test proof; actual UI create and separate lost-reply create intentionally produce two studies.

## Review Triage Log

| Finding | Verdict | Individual evidence | Route |
| --- | --- | --- | --- |
| B1 | medium | Snapshot omits executed app role SQL/corpus migration/Alembic configs and only rehashes the old file set; source changes may escape the success guard. Direct fixture inventory correction. Resolved by source_inventory rediscovery; final222 source hashes match. | patch G1 |
| B2 | medium | After-denial oracle compares text/counts but omits revision, attribution timestamps and complete receipt/outcome sets; an unauthorized side effect could pass. Compare protected state before/after denial. Resolved by identical complete before/after disabled-state digests in final native proof. | patch G2 |
| B3 | medium | Initial checkpoint omits outcome/event/receipt tables; premature effects in those tables are not observed. Assert complete empty protected state. Resolved by empty account outcome/event/receipt assertions at initial and post-check SQL observations. | patch G3 |
| B4 | medium | Actual isolation requests omit foreign note-list/create paths; those operations could disclose/create without this integrated scenario failing. Add requests and unchanged-state observation. Resolved by actual foreign collection GET and note POST404 plus identical complete denial-state digests. | patch G4 |
| B5 | medium | Oracle checks note attribution only and does not require both account bindings or study actors; documented durable attribution is incompletely pinned. Add direct SQL assertions. Resolved by both account binding and all study/note/receipt actor assertions; seven focused oracle variants pass. | patch G5 |
| B6 | low | Disable phase reads public text only in an authenticated context; anonymous availability is not explicitly exercised. Direct anonymous browser assertion is small and relevant. Resolved by successful fresh anonymous-context public reading after disable. | patch G6 |
| B7 | medium | Credential scan observes headers and selected same-origin responses but misses URL/body/other response channels. Direct sentinel assertions need no payload logging. Resolved by credentialInspection over URL/header/body/all-origin responses/WebSockets, focused sentinel cases and complete native observations. | patch G7 |
| B8 | medium | After SIGKILL stop_process waits for the leader only; real-process test waits for descendant kernel delivery outside cleanup. Observe stopped descendants within cleanup before declaring stopped. Resolved by bounded executing-group observation; final native termination_confirmed is true for every stopped group, and forced/unconfirmed cases pass focused checks. | patch G8 |
| B9 | medium | Native enrollment/create uses manual fetch rather than the delivered UI handlers; actual-provider UI integration could fail while this proof passes. Exercise those existing controls alongside explicit completed-response replay. Resolved by actual Start a study / Create study controls in the final native scenario; separate completed-response retry remains explicit. | patch G9 |
| E1 | medium | Constructor path-existence check is not an atomic reservation; concurrent fixture invocations using the same explicit UUID can both pass it and wrapper prepare accepts an existing matching run. Create-only fixture reservation before any wrapper operation, retained through completion. Resolved by create-only retained per-UUID reservation; concurrent same-UUID test permits exactly one owner. | patch G10 |
| E2 | medium | Fixture psycopg connects bound connection establishment only; SQL lock waits have no timeout and can prevent cleanup. Set bounded fixture statement/lock timeouts. Resolved by fixture connection statement20s/lock3s/idle-transaction20s settings; option test and actual native SQL pass. | patch G11 |
| E3 | medium | Executed app role SQL and corpus migration are missing from the recorded source set; same source-inventory defect as independently filed B1. Resolved by source_inventory rediscovery, including app SQL/config and wrapper schema; final222 hashes match. | patch G1 |
| V1 | medium | Pre-verified gap: autouse replaces check_ports and collision test replaces it with an unconditional throw, so no automated real detector assertion fails if detector becomes a no-op. Add occupied real-socket test. Resolved by actual occupied ephemeral socket detection before wrapper preparation; focused socket-enabled suite passes. | patch G12 |

All13 findings individually classified before grouping;12 distinct root-cause groups, no intent change, loopback or deferral. Each fix stays in fixture/tests and adds no public API. Only B1/E3 share a root cause and are grouped; other findings remain distinct even when their corrections edit the same fixture or browser file. The complete external verification finding is retained at `/tmp/scribeswell-owner-verification-findings.md`.

## Design Notes

No human intent gap; this is integration qualification, not release activation.
Only new synthetic fixture state is mutated. Broad cross-service test footprint requires
dispatch. Scaffold/shared UI/agent context/ADRs: no change; reuse existing patterns and
record any demonstrated runtime defect before its smallest consuming correction.

## Verification

Final parent evidence: run21c6a0b8-957b-4623-9462-fabd63264275 exit0; both native browser cases12.331s/3.497s,222 unchanged rediscovered sources, complete protected-state equality around foreign and disabled requests, anonymous reading and confirmed owned-group termination/exact stop0. Parent affected170 tests11.26s, owner56 tests3.38s, retained session12 tests20.7s, build8.99s and generated/helper/composition pass; child37 focused9.93s. All13 review rows addressed in12 distinct correction groups, no deferrals. Historical broad203/3 remains disclosed despite unchanged isolated retries passing; no repository-wide pass or new activation claim.

Run the smallest failing orchestration/browser acceptance first, then the focused
fixture tests and full native qualifier with explicit CLI/run inputs. Record its exact
final invocation and every executed matrix case. Run retained app contract/API/release,
owner Studies characterization, affected browser/session suites, app build, generated
checks and composition dry-run when affected. Report exclusions and earlier failures;
never substitute a mocked pass for the integrated proof or claim a repository-wide pass.
