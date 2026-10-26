# Workspace-tabs architecture rubric review

Reviewed 2026-10-22. Scope: the draft architecture spine and its reconciliation with SPEC, UX, reader-interaction, acceptance, brownfield and data-and-saving companions. This is planning review, not implementation or device evidence.

**Verdict: coherent gated draft; fix one proposed navigation-contract gap and one acceptance rendering defect before recording this reconciliation as complete. D-1–D-5 remain open. No critical or high findings.**

## Findings

### R1 — Medium: the proposed public URL drops reference range identity

`reader-interaction.md`, “One browser history path,” proposes `{v:1, panes:[{book,chapter,verse?}], active:0}`. The spec permits chapter, verse and verse-range entry; ST-05 requires both range endpoints to survive. D-2 separately defines canonical range identities. The new wire proposal has no end bound, and does not explicitly explain whether a range is just an initial seek or part of a reading target that must survive share/reload/browser restore. Two consumers could obey the prose while one retains a range and the other silently reduces it to its first verse.

**Disposition: autofix the draft contract.** Reuse the canonical reference/target representation, or explicitly encode validated optional end bounds and explain which range/seek metadata is retained in URL and snapshots. Keep physical schema, bounds and executable qualification in D-4. Add range round-trip/restore to the relevant future acceptance case. No new user-level choice is necessary to preserve the already accepted range semantics.

### R2 — Low: new acceptance rows are outside the Markdown table

`acceptance.md` has a blank line between ST-27 and ST-32. The new ST-32–34 pipe rows therefore do not continue the existing GFM table. Their text exists, but the rendered requirement-to-test map is broken precisely for the added workspace cases.

**Disposition: autofix.** Remove the blank line, preserving stable ST IDs and wording.

## Rubric assessment

| Dimension | Assessment |
| --- | --- |
| Real divergence boundaries | AD-12 now fixes stable tab/pane ownership, independent positions, one shared tool surface, per-tab associations and one resource save lane. D-4 owns the proposed public navigation/closure details rather than leaving each component to choose. R1 is the remaining identified draft shape mismatch. |
| Enforceability | Rules name authority, ownership and prohibited outcomes. Inactive views cannot write obsolete snapshots; close does not delete records; explicit pane targeting at capacity prevents arbitrary replacement; private associations never enter public history. These are testable controller/API boundaries, with executable proof explicitly pending. |
| Deferred decisions | D-1–D-5 remain actual prerequisites. Numeric tab/snapshot bounds, last-pane defaults, responsiveness and native selection are proposed qualification choices, not falsely delivered guarantees. Shared D-4 closure before consuming code prevents independently invented snapshot contracts. |
| Capability coverage | CAP-1–11 are mapped; CAP-6 grows comparison to four panes, CAP-11 owns multiple setups. ST-16/31–34 cover repeated passages, history, public tabs, shared editing and closure. Existing privacy/copy/source-loss/save cases remain present. R2 affects presentation, not missing requirements. |
| Brownfield reality | ReaderPage still has a fixed two-pane model; PassagePane arrows really are Previous/Next chapter controls. The documents clearly call tabs new work, retain chapter arrows, and explicitly supersede proposed separate pane histories. WordStudy remount risk is correctly addressed by moving sole edit ownership above that lifecycle. No claim that runtime tabs already exist. |
| Inherited invariants | Account-scoped admission, public-read independence, owner-local writes, private-response visibility, source-aware anchors, revision/retry protection and safe session recovery remain binding. Public tabs require no new organization or login. Accepted ADRs are unchanged. |
| Operational/environmental envelope | Existing web/API/PostgreSQL deployment is retained; AD-13/D-5 address roles, private/public readiness, controlled migrations and explicit recovery. Inactive tab resource bounds are named under D-4; no browser durable-storage or cross-device promise is smuggled in. No infrastructure/stack change is introduced. |
| Technology claims | Existing stack/manifests are authority and no new library is selected. This rubric review inspected the relevant current reader references; dedicated configured technology reviewer provides the independent technology lens. |

## Qualification remains required

The proposed URL/snapshot formats, closed-tab replay at capacity, generation-gated seek restoration, global note-lane remount behavior and last-context close guards still need executable sequence tests before their consuming implementation is ready. Three/four-pane geometry and keyboard accessibility need browser proof; real iOS/Android selection/Copy/IME evidence remains necessary. These are explicitly assigned existing gates, not newly discovered reasons to halt the planning update.

No additional ADR, shared runtime, framework, Leave implementation or user confirmation is required by this review.
