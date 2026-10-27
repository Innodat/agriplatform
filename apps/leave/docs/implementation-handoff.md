# Leave implementation — new Codex session

**Implementation continuation, 2026-10-26:** User authorized implementation and
epic-level reviews, then approved shared KDG development with isolated destructive
acceptance. E1-ENV is in progress. Reuse the existing KDG stack for ordinary development;
the Leave-local target is acceptance-only. Preserve KDG data and all unrelated edits.
See [current evidence](testing/e1-environment-evidence.md) and the
[approved topology refinement](testing/e1-environment-and-dependencies.md).
The original new-session instructions below retain the approved delivery sequence.

**2026-10-26:** Planning approved; CE complete; SP planning-readiness PASS.
Implementation has not started in the planning session. The user requested a new session.
Phase1's implementation milestones remain unchecked; a readiness PASS is not scaffold delivery.

Copy this into the new session:

```text
Start Leave implementation using bmad-build, beginning with E1-ENV only.
Read AGENTS.md and apps/leave/docs/implementation-handoff.md.

The user approved the completed consolidated planning package on 2026-10-26.
CE final validation is complete and SP planning readiness is PASS. Do not reopen E5,
repeat the story-by-story planning review or seek the same technical approvals again.
Acceptance is recorded in platform ADR-0064 and Leave ADR-0171. Existing ADRs remain binding.

Read _bmad-output/planning-artifacts/leave-planning-completion.md and
implementation-readiness.md. Product truth: apps/leave/docs/features.md;
delivery tracker: apps/leave/docs/implementation-plan.md; story authority:
_bmad-output/planning-artifacts/epics.md and its approved owner contracts.

Use _bmad-output/implementation-artifacts/leave-sprint-status.yaml and
leave-sprint-source-map.json. The map links tracking ordinals to the original 310
actual leaf IDs and dependencies. Do not count retained parent scopes twice.
Start E1-ENV: Reproduce an isolated development and acceptance environment.
Use its actual criteria and environment contract, not only its tracking title.

Inspect current shared work before changing it; some substrate has been delivered by
other applications. Credit only verified actual evidence. Preserve all unrelated changes.
Apply BMAD/ATDD with the relevant acceptance failure first; deliver the smallest bounded
story and record exact verification. Do not treat root npm dev/build as repository proof.
Do not generate Leave from a placeholder builder; actual environment/generator/reference
prerequisites must be proved in dependency order. E1's user outcome remains sign in →
select organization → create/resume → autosave → close → reopen, with no submission.

Proceed autonomously within the authorized story; report meaningful progress rather
than prompting for routine choices. Do not perform customer email/import, live grants,
provider changes, production migrations/deployment or commits without applicable authority.
```

Sources: [completion](../../../_bmad-output/planning-artifacts/leave-planning-completion.md),
[readiness](../../../_bmad-output/planning-artifacts/implementation-readiness.md),
[tracking](../../../_bmad-output/implementation-artifacts/leave-sprint-status.yaml),
[original ID mapping](../../../_bmad-output/implementation-artifacts/leave-sprint-source-map.json).


## Access commit baseline — authorized 2026-10-27

The user authorized scoped local commits of completed Identity, Access and Discovery
work plus required qualification dependencies so Scribeswell can extend a recorded
baseline before E1-PEOPLE. This supersedes the earlier no-commit restriction for this
scope; production activation, live adoption and push remain separately gated.

Identity26/Access19, person links/preferences, explicit account grants, current typed
capability/context checks and private organization/application discovery are complete.
All review findings are resolved; none deferred. Final Access/PtS regression:2,223passed.
Native constraints/roles, current HTTP, migration/recovery, previous clients, generated
contracts and hardened image proofs are recorded in the linked owner evidence.
See [Identity](testing/e1-identity-links-preferences-evidence.md),
[current access](testing/e1-current-access-evidence.md) and
[Discovery](testing/e1-discovery-evidence.md). This is a source checkpoint, not a
production-ready Scribeswell consumer/activation claim. E1-PEOPLE remains unimplemented;
its future narrow Access setup-reference addition is separate from the closed work.

Preserve unrelated Scribeswell/Content/platform changes and fixture state. Continue
Scribeswell from the recorded Access baseline; requalify affected contracts and its
source-bound consumer readiness after further Access changes.
