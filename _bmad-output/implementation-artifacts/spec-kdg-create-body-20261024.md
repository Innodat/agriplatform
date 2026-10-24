---
title: 'KDG protected fresh capture transaction body'
type: 'feature'
created: '2026-10-24'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Replace fixture-only create SQL with a concrete KDG-owned fresh capture transaction body that consumes previously verified current create authority and the existing bounded installed context. Under operation then child coordination locks, privately recheck absence before domain validation, validate the original published definition and account/membership-bound historical eligibility, independently check current assignment when required, and insert capture/outcome/history together. An existing outcome stops this fresh-only path without disclosure; later HTTP/replay orchestration must authorize its actual stored target. Return only provisional private data inside the caller-owned transaction; no durable acknowledgement.

Qualify synthetically and against the retained rollback-only native fixture. No persistent migrations, resource preparation, API activation, real authority calls, production, Leave/editor, deployment or cleanup. Preserve concurrent work, old evidence, resources and dependency baseline including TypeScript7.0.2. Fingerprints/HMAC remain deferred.

</frozen-after-approval>

## Implementation Notes

- No intent gaps or irreversible work. Small owner-only change: new write-candidate/capture_create.py and behavioral write tests; existing native qualifier consumes it; documentation/evidence/handoff updated. Active migration unchanged.
- Reuse operation_outcomes.write as the single context/helper identity, api/capture_commands.py and questionnaire.py. No shared framework or new dependency. Runtime parents remain SELECT-only.
- Advisory lock scope is organization+child, ordered after operation lock. Future owner child/assignment mutations must take exactly this lock before reads/writes. Participating commands only, not arbitrary SQL; mutation workflows and two-session/durable qualification remain release prerequisites.
- Historical eligibility revisions/permission are evidence, never current authority; current membership must match. Prior active-child observation permits ordinary inactivity. Current create.assigned independently requires active same-membership assignment; create.all remains own-author. No invented expiry or requirement for unchanged historical revision.
- Scaffold/shared UI: domain-specific body and eligibility policy stay KDG-owned; managed helper/template unchanged with parity check. Agent context: no new generic rule. Documentation: new source-bound receipt and prepend handoff. ADR: existing accepted decisions suffice; no new architecture.

- ATDD observed missing module, then behavioral removed-assignment failure (no WriteError and three inserts). Focused assignment check fixes all missing/inactive/old-membership cases. Initial test inspected unsupported fake events; corrected to existing fake EXIT_WITH_ERROR/COMMIT call contract rather than claiming native rollback.
- Native consuming qualifier now uses the actual create body and separately exercises nine domain variations, existing-outcome stop and two-existing-connection advisory wait. First native run:38 PASS, all candidate objects/rows rolled back, head0001 retained. Write suite56 PASS. Managed code/test scaffold parity PASS.
- Original105 preexisting dirty/untracked files remain present and byte-identical; historical handoff is an exact suffix. No active migration/dependency/template changes.

- Review patch: distinct capture/operation UUID regression first failed (no refusal), then passed with the structural pre-lock guard. Expanded native fixture initially omitted required child active/revision (23502); rollback verified. Corrected seed fields only. Final native oracle observes actual capture+outcome rows before injected history23514, verifies rollback baseline, two published versions, both historical/current permission transitions, wrong-child reference and advisory release after holder rollback.
- Final write regression:57 PASS; native:43 PASS; no active migration or API route. All review findings patched; none deferred.

## Review Triage Log

1. medium / patch — Distinct capture/operation identity is required by contracts.md:336; reproduced failure and added pre-lock guard plus behavioral regression.
2. low / patch — Source-bound receipt absent during review; added final receipt with exact commands, native report and source bindings before finalization.
3. medium / patch — Original-version behavior lacked two-version proof; native seed now publishes different newer questions, creates on the older definition and verifies persisted original ID.
4. medium / patch — Historical/current capability transition claims needed fixtures; native current-assigned cases use historical-all records (with/without current assignment), and new historical-assigned record works under current-all with inactive assignment.
5. medium / patch — Earlier native refusals preceded writes; added injected native history23514 after observing capture+outcome rows, then verified full savepoint rollback to baseline.
6. medium / patch — Missing same-account/member wrong-child reference case; added native second-child eligibility and verified refusal without inserts.
7. low / patch — Contention did not prove release; same second connection rolls back, then the previously contested key is acquired successfully.
