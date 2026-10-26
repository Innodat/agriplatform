---
title: 'Resolve retained same-phone capture proposals'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: '6926cb527e319e1842c105c06fcd5d5fabac4a45'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/PENDING_CREATE_EDIT_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/docs/CONFLICT_RESOLUTION_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Explicit stale same-phone Saves retain competing proposals, including pending-create edits, but cannot choose the existing saved phone state or a reviewed replacement.

**Approach:** Add isolated local review/decision methods using actual saved state, valid local authority and atomic CAS. Preserve the chosen current action/create; save replacements as ordinary ordered edits. Reuse current decisions and delivery, without server calls during local review/decision.

## Boundaries & Constraints

**Always:** Retain original creates, proposals, bases, commands, receipts and predecessors. Use-current needs own-read only and preserves current local representation/status; it never sets Synced or invents server evidence. Replacement needs valid exact own-edit observations, original definition, new identity and the actual current typed predecessor. Commit decision/new intent/overlay/dispositions together. Retire only the competing unprepared source and pause its descendants; never replay/include them automatically. Recover exact decisions under own-read after reopen, permission loss or legitimate later progress; validate actual effects, reject changed retry inputs. Respect scope, generations, original reviewed expiry, deadline/cancellation and storage completion ambiguity.

**Never:** UI/editor/Leave, new HTTP endpoint/service, active sender/claims/scheduling/queue/browser/service-worker/startup activation, autosaved typing, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/migrations, deployment/production/pilot/cleanup, installs/dependency changes, fingerprints/HMAC or push. Preserve TS7.0.2, concurrent work and historical evidence. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`. This subset covers unprepared off-head Needs attention proposals; confirmed v2 server409, an active unprepared head made stale by server progress, and re-review of already paused descendants follow separately without routine stops.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected result | Failure behavior |
|---|---|---|---|
| Local adoption | Off-head unprepared v1/v2 Needs attention proposal; actual saved head/create | Atomic explicit decision; selected current content/status unchanged | No HTTP, fake revision or lost proposal |
| Local replacement | Ready current local state; valid own-edit; complete original-version input | Fresh ordinary v1/v2 intent linked to actual current predecessor | Actual receipt required before command revision; no blind rebase |
| Read-only | Edit denial/expiry, valid own-read | Adoption/recovery allowed; new replacement refused | Independent read/create refresh cannot restore edit |
| Pending creation | Original create unresolved, possibly response unknown | Original immutable create remains ancestor; new edit waits on its actual receipt | No competing root create or inferred acknowledgement |
| Concurrent/late | Head/content/baseline/generation changes; old receipt or review arrives | Stale decision refused; later legitimate progress preserves selected work | No resurrection or false success |
| Storage/retry | Abort/quota/commit ambiguity, exact/changed identities, reopen | Atomic effects or honest unavailable; exact recovery verifies retained effects | No inferred rollback; corrupted/unknown state retained and refused |
| Compatibility | Schema4 with server decisions and real v1/v2 chains | Additive typed local decision interpretation; existing behavior preserved | Bound100 capture actions; oversized/incomplete graph refuses without deletion |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: reuse `captureGraph`, complete v1/v2 interpretation, `originalLocalBase`, observation/epoch/generation fences, `normalizeChanges`, `editOperation` and original intent shapes. Add `ReviewedLocalConflict` and explicit `openLocalConflict`, `useLocalCurrent`, `saveLocalConflictReplacement`, `lookupLocalResolution` (equivalent concise names acceptable). No new coordinator/Auth entry is needed for these pure store transactions; callers supply existing `Execution`, as for Save.
- A local source is an undisposed off-head `status:'Needs attention'` edit with no delivery envelope. Current selected head is outside its descendant branch. Do not reuse server `conflictBranch`'s source-to-head requirement or `decideConflict`'s clear-overlay/import-baseline/Synced behavior. Refuse opaque blockers or unsupported state. Replacement requires the same ready/editable state as ordinary Save; use-current may preserve remaining attention truthfully.
- Review pins complete actual current local snapshot, head/create identities, nullable baseline revision, current typed predecessor, resolution generation and applicable authority generations. Frozen branded review plus complete-time CAS prevents stale decisions. Current representation is the actual saved overlay, otherwise original local capture or actual baseline under its correct shape; no fabricated server fields. Pending ancestry is preserved: prepared uncertain actions outside the chosen predecessor chain block competing decisions. Unresolved chosen ancestors may remain because the new action waits on their matching actual receipts, as ordinary ordered Save already does.
- Persist a versioned local decision in existing schema4 `resolutions`; preserve version1 server decisions. Decoder/linked-effect validation must accept legitimate local progress without requiring the original overlay still active. Existing server branch validation must understand recognized local decisions without weakening old dispositions; unknown versions safely refuse. Existing legacy code must still block disposed work. New replacement has ordinary input/content/result shape and next generation, preserving original action bytes. No global cross-kind UUID namespace or generic merge engine.
- `web/tests/local-conflict-resolution-proof.mjs`, `.types.ts`, `web/tsconfig.local-conflict-resolution.json`: selected-source strict real-IDB proof; characterize existing Saves before shared refactoring. Parent owns integration/docs/broad qualification; implementation child owns store/focused proof/types/config only.

## Tasks & Acceptance

- [x] Focused proof/types/config — observe missing local behavior RED, then matrix, scope/expiry/denial, normalized1/false, corrupt effects/graph, real reopen, independent connections, live abort and completion ambiguity.
- [x] Store — atomic local adoption/replacement/recovery and compatible decision interpretation.
- [x] `web/tests/local-conflict-resolution-http-proof.mjs` — parent: actual synthetic setup/create/edit/recovery with real IDB, local choices issue no HTTP, original create and actual receipt chain retained, read-only denial/recovery.
- [x] `docs/LOCAL_CONFLICT_RESOLUTION_EVIDENCE.md`, machine record, contracts/handoff and web README — parent: exact source-bound commands/results and five impact decisions.

**Acceptance:** Given the matrix and existing consumers, when focused/integrated/regression checks run, then local choices preserve every saved proposal and actual receipt lineage while existing server resolution, normal Save/delivery and scaffold parities remain valid. Given later unrelated server progress, when normal delivery occurs, then existing409 retains the new proposal rather than rebasing it.

## Implementation Notes

Acceptance audit first24-job candidate passes152 focused/58 HTTP and all22 prior
commands. Additional source-bound probes reproduce four implementation corrections:
remove unrelated create-status prerequisite; allow reference-only label refresh during
recovery; pin lookup identity before awaiting; prefer actual synchronized baseline over
retained original create evidence once the local chain completes. No public API or
frozen-intent change is needed. Register focused/HTTP regressions before correction.

Technical subset of approved Story2.3, not full-story/UI completion; story_key unset. No unresolved product questions or irreversible effects. Standing authorization covers dirty-tree preservation, cohesive spec size and routine checkpoints. Investigation confirms existing stale Saves produce these off-head proposals. Reuse proven Auth/IDB primitives unchanged; no neutral runtime defect demonstrated. Shared UI and agent context unchanged; update docs; accepted ADRs unchanged. Native/browser-update/release gates remain.

## Spec Change Log

## Review Triage Log

Every layer reported before classification. All findings are direct internal corrections or focused regression additions; no exported API or frozen intent changes.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| B1 | medium | patch | captureGraph permits100 retained actions; decideLocal adds another without checking resulting count; next lookup captureGraph refuses101. Add resulting-size fence and valid boundary regressions. |
| B2 | medium | patch | Current reviews only brand with WeakSet; readAccess observes refreshed meta, so original own-read expiry is lost. Private branded-observation retention corrects this without exported surface changes. |
| B3 | medium | patch | localDecisionEffects skips selected-action progress when any saved_edit exists, including the retained prior valid head. Validate actual active ancestry or matching receipt/disposition evidence. |
| B4 | medium | patch | localBranch checks only active head disposition; retained valid chain with disposed ancestor bypasses this check. A direct ancestor check plus corruption regression protects the same supported graph invariant. |
| B5 | medium | patch | Current focused seed contains no competing descendants, so claimed multi-level pausing/immutability lacks a behavioral assertion. Add complete valid branch coverage. |
| B6 | medium | patch | Overflow fixture has unknown version99; failure cannot independently establish the action bound. Valid99/100/101 fixtures must isolate it. |
| B7 | medium | patch | Replacement collision loop has no action_id_reused regression for edit/create identities. Add no-effect collision assertions. |
| B8 | medium | patch | Current-mode expiry case does not refresh authority; it cannot expose B2. Add refreshed-read original-expiry regression. |
| B9 | medium | patch | Live abort currently uses adoption and checks only resolutions; replacement atomicity after intent queueing is not established. Snapshot all affected stores/record fields. |
| B10 | medium | patch | New HTTP proof fetch/evaluate can remain pending beyond external parent timeout, bypassing owned child cleanup. Add bounded request and overall watchdog, forced-stop evidence and injected stall qualification. |
| E1 | medium | patch | Independently confirms B1 resulting-size omission; preserve its own row and use the same bound correction. |
| E2 | medium | patch | Independently confirms B3: restoring previous valid overlay leaves selected replacement unacknowledged but exact lookup reports success. Add ancestry validation and regression. |
| V1 | medium | patch | Preverified regression gap: new v2 reviewed.capture equality has no create-parent or edit-parent contradictory-evidence test; add both with unchanged retained evidence. |

## Verification

Retained Node26.11.1/TS7.0.2/modules/Chromium/Python only; no installs. New focused RED→GREEN, actual synthetic HTTP, then previous22 jobs from `platform/deployment/.local/kdg-own-conflict-resolution-20261026/root-verify/final-qualified.json`. That prior focused job constructs99 real decisions and needs660sec process bound; its actual operation remains30sec. Run broader checks once after stable code and again only for justified changes. Reconfirm342 backend tests'85 effective hashes and176 protected historical/dependency files; append contracts/prepend handoff. Never scan the forbidden fixture. Private custody: `platform/deployment/.local/kdg-local-conflict-resolution-20261026/`.

Pre-review qualification:24 source-bound commands pass with258 stable sources,172 focused
and71 actual HTTP checks, all22 prior jobs and five scaffold parities. Four acceptance
audit failures have targeted REDs and registered regressions. All176 protected files
and85 backend sources reconfirmed; reuse342 backend tests only with unchanged hashes.

Review corrections: all13 findings addressed without public API changes. Targeted
RED frames retained;883 focused checks and71 actual HTTP checks pass corrected code.
Injected HTTP stall confirms bounded normal owned-child shutdown. Final24-command
post-review verification passes on258 stable sources; prior qualification remains
historical evidence. All176 protected files and85 backend hashes reconfirmed.
