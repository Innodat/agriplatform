# Rubric and input-reconciliation review

Reviewed 2026-10-21: `ARCHITECTURE-SPINE.md` against `SPEC.md`, `ux-behaviour.md`, `acceptance.md`, and `brownfield.md`, using the bmad-architecture good-spine checklist. This is an independent document review; no application behavior, migration, owner contract, or real-device evidence is claimed.

**Verdict: coherent architecture draft with two corrections; not an implementation-ready build substrate.** The open owner prerequisites are legitimate at this stage. No critical or high-severity contradiction was found, and the draft preserves the accepted product scope. The corrections below improve the reliability of its gates and diagram without requiring runtime implementation.

## Findings

### R-1 — Medium: D-4 postpones a shared interaction contract until final acceptance

**Evidence:** Spine D-4 (line 170) places exact inspected-note/current-note and two-pane replacement/history rules before “Final acceptance of consuming reader/editor stories.” The UX companion’s Comparison and mobile tools section explicitly requires settling replacement/focus/history behavior **before its implementation story**. Brownfield Q-4 and SPEC Q-4 also treat these as dependencies for the consuming stories.

**Divergence:** Independent reader, inspector, and editor units could implement different active-pane/history and current-note transitions, then each bring a plausible implementation to final acceptance. This conflicts with the spine’s stated purpose of preventing incompatible independently built units. Physical-device validation may naturally finish during acceptance, but the contract governing those units must precede their implementation.

**Disposition: autofix.** Split the revisit condition: settle the shared state/transition, replacement, focus/history, and fallback contract before consuming implementation; prove native-device and assistive behavior before final acceptance. Preserve the owner and all required device checks. This does not require performing those checks in the architecture task.

### R-2 — Medium: structural seed visually requires a live source note for every private response

**Evidence:** The ERD at line 138 is `NOTE ||--o{ PRIVATE_RESPONSE : source_when_available`. The `||` end means every response has exactly one source NOTE. AD-5 requires provenance to survive source absence without a live cascade dependency; the prose immediately below the diagram says the response is an independently owned NOTE. UX allows a response beside a shared note **or passage** and requires survival after source-note deletion.

**Divergence:** Although the prose clearly preserves independent ownership, a schema consumer following the ERD could require a non-null live source-note reference, or infer a separate response entity/body. Such a schema needs an unmentioned retained/tombstoned source or could reject passage responses and independent source deletion. D-2 correctly owns the final representation, so the seed should avoid pre-deciding a stronger relation.

**Disposition: autofix.** Remove the source edge from this intentionally minimal seed, or label an optional logical provenance relation to a response NOTE and make clear that source study/passage/note identity may outlive a live record. Keep the exact retained metadata/tombstone/deletion representation under D-2. Do not add retention of source text.

## Good-spine rubric

| Check | Assessment |
| --- | --- |
| Real divergence points | Covered: owner boundaries, public/private eligibility, restricted persistence, note aggregate/revisions, conflict branch, occurrence anchors, document representation, invitation/share lifetime, durable notification intent, frontend context, compatible operations. |
| Binds / Prevents / Rule | All 13 decisions provide each field. Rules are concrete enough to constrain downstream design, while D-1–D-3 own the eventual wire/physical details. R-1 and R-2 are the remaining ambiguity points. |
| Deferred cannot authorize incompatible consumers | D-1–D-3 explicitly centralize contracts and stop the consuming work; D-5 stops readiness/activation claims. D-4 needs R-1. Open contracts are not evidence the feature is build-ready. |
| Brownfield consistency | The draft retains the existing React/FastAPI silo, public corpus path, same-origin routing and optional public session. It does not treat the legacy JWT helper, organization Access check, public DB permissions, or planned Leave notification runtime as working protected-feature contracts. This review reconciles the supplied brownfield record; it is not an independent code audit. |
| Technology/version claims | No new framework, upgrade, editor, ORM, provider or pinned version is selected. Existing manifests/lockfiles remain version authorities. There is no newly bound current-version claim requiring external verification in this review. |
| Capability coverage | CAP-1–CAP-10 have owners and a decision map. More detailed picker, default-title, library ordering and interaction requirements remain binding in the referenced spec/UX/acceptance package rather than being unnecessarily duplicated. |
| Structural dimensions | Data/lifecycle, account/resource authorization, service APIs, persistence isolation, client state, source/import compatibility, notifications/workers, sensitive diagnostics, migration/release/environment and failure readiness all have named owners or gates. The private runtime/worker and common service roles remain distinct. |
| Scope and accepted decisions | Public reading and PtS launcher policy remain separate; no organization requirement, edit sharing, bearer link, extra panes, automatic quotation, synchronized copy, full offline promise, or Leave implementation is introduced. Accepted ADRs remain unchanged. |

## Load-bearing input reconciliation

- **SPEC:** All ten capabilities survive. Open personal-study eligibility is explicit and remains subject to current Access policy, suspension and resource checks. Ordinary sharing versus owner-only private responses remains distinct. Sharing/deletion remain explicit actions, with no submission product added.
- **UX:** Note-owned marks, separate passage list, one shared panel, retained current note, source-aware comparison, own-study private-response destination, independent copies, explicit acceptance and 30-day pending invitation expiry all land. Detailed interaction choices are retained through source references; R-1 prevents a late decision on the remaining shared transitions. R-2 removes a diagram ambiguity around passage responses and source absence.
- **Acceptance:** The decisions support ST-01–ST-29 without claiming they pass. Especially preserved are unknown-save outcomes, conflict-copy coherence, private search/count exclusion, cross-account checks, no resurrection, provider failure separation and controlled release recovery.
- **Brownfield:** Q-1 maps principally to D-1/D-3; Q-2/Q-3 to D-2 with AD-3–AD-9; Q-4 to D-4. Scaffold, shared UI, agent-context, documentation and ADR impact choices remain in the package and are not displaced by a second lifecycle or duplicate specification.

## Readiness boundary

Approve the corrected document as a **draft architecture consistency contract** only. D-1–D-5 still require owner design or evidence before their consuming work/readiness milestone. No additional user approval flow, implementation story dispatch, runtime build, or migration is requested by this review.

## Resolution check — 2026-10-21

Rechecked only the corrected Structural Seed and D-4 passages, as requested.

- **R-1 resolved:** D-4 now requires the shared interaction contract before reader/editor implementation and reserves device/accessibility evidence for final acceptance. Independent units can no longer defer their common transition contract until after construction.
- **R-2 resolved:** The seed now uses an optional NOTE provenance self-link. Its paragraph explicitly permits source-note or passage provenance without a live source note, separate response body, or source-delete cascade.

**Updated verdict: pass as a draft architecture consistency contract; no remaining issue from this rubric review.** The existing owner prerequisites remain open, so this is not an implementation-readiness endorsement. The original findings above are retained as review history.
