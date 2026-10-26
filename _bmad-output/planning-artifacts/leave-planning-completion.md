# Leave planning completion and implementation handoff

**Date:** 2026-10-26. **User approval:** explicit approval of the completed consolidated package.
**CE:** COMPLETE. **SP planning readiness:** PASS. **Implementation:** NOT STARTED in this session.
**User boundary:** stop now so implementation starts in a new Codex session.

## Approved baseline

All eight epic domains, 310 delivery leaves, 1,757 registered Given criteria and 1,564
acyclic dependency edges are retained. The earlier independent/source reconciliation
remains valid; the approval adds no criterion or scope. E5 remains closed. Accepted
platform ADR-0064 and Leave ADR-0171 record the final shared and Leave contract choices;
existing accepted ADRs remain byte-identical. Every changed contract has an adoption
annex resolving candidate status without rewriting the reviewed choices.

## Formal final validation

| BMAD check | Finding |
| --- | --- |
| Source coverage and traceability | Complete existing five-source/criterion reconciliation plus unchanged source/criterion hashes; no outstanding uncovered requirement identified. |
| Architecture and setup | Actual ENV/P1/SERVICE prerequisites precede use of the missing generator. No assumed installed starter, upfront all-domain tables or cross-owner imports. |
| Story completeness and size | Existing 310 actual owner boundaries and per-item residual sizing retained; final contracts bind the last invitation/continuity/calendar choices. Actual runtime witnesses belong to their delivery items. |
| Epic value, file churn and dependencies | Eight approved user outcomes; shared files evolve by first-consumer extensions with bounded regression, not copied platforms. Foundations can complete before later workflow integration. Graph has 66 acyclic layers. |
| Approval and consistency | Explicit final approval resolves the sole prior readiness concern. Contract adoption, new ADRs, tracker, epics and handoff agree. |

PASS means the approved plan is implementable without inventing the recorded decisions.
It does not claim native database/provider/browser/release tests already passed, that
all stories have individual implementation files, or that Phase1's scaffold is delivered.

## Tracking and parser adaptation

BMAD generated [Leave sprint status](../implementation-artifacts/leave-sprint-status.yaml):
eight epics and 310 stories all in backlog; eight retrospectives optional. No item is
marked implemented merely because related substrate exists. Current shared-owner evidence
is assessed against each actual story during delivery.

The strict parser accepts numeric story headings, while the approved plan uses E1 names
and hyphenated owner partitions. The [thin heading view](leave-sprint-input.md) contains
only actual leaf IDs/titles in dependency-respecting order within each epic. The
[source/key map](../implementation-artifacts/leave-sprint-source-map.json) preserves the
exact 310 identities and dependencies and the source graph hash. It is tracking navigation,
not a duplicate feature spec. Use this mapping when synchronizing bmad-build; never parse
historical parent headings as additional delivery stories or silently omit named owners.

## Next action

Open a new Codex session with [the implementation handoff](../../apps/leave/docs/implementation-handoff.md).
The first task is E1-ENV, using bmad-build and the approved owner contracts. No new guided
planning review is needed. Keep all unrelated working-tree edits. No runtime implementation,
customer email/import, grant/provider change, migration, deployment or commit was done here.

## Executed closing checks

- `python3 /tmp/check-leave-approved-planning.py` — PASS: 310/1,564/66 graph,
  1,757 exact criterion hashes, 1,219 source hashes, 115/837 unchanged individual
  judgments, current contract hashes and preserved original contract/story bodies.
- Approval-specific inspection — PASS: all 233 pre-existing numbered ADR files unchanged;
  310 unique mapped backlog stories, 326 total tracking entries, dependency-respecting
  tracking order and 36 local approval/handoff links. Only the two new accepted ADRs added.
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py generate
  --epic-file _bmad-output/planning-artifacts/leave-sprint-input.md
  --status-file _bmad-output/implementation-artifacts/leave-sprint-status.yaml
  --stories-dir _bmad-output/implementation-artifacts/leave-stories
  --project Leave --date '10-26-2026 11:14'` — PASS, eight epics/310 stories;
  no warnings, illegal statuses, dropped orphans or existing-story status upgrades.
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate
  --status-file _bmad-output/implementation-artifacts/leave-sprint-status.yaml`
  — PASS: valid=true, problems=[], legacy_mapped=[].
- Scoped `git diff --check` — PASS after removing trailing whitespace in the updated
  tracker status line. No source or acceptance expectation was changed to obtain a pass.
- CE completion hook resolves to an empty action. BMAD Help's next required delivery
  action is `[BD] bmad-build`, recommended in a fresh context; the user's session boundary
  is therefore the next step, not implementation in this session.

These are planning/tracking integrity checks, not application runtime acceptance.
