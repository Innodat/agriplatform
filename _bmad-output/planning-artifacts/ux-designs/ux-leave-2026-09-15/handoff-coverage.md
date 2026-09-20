# Leave UX handoff coverage

Date: 20 September 2026. This is a bounded finalization check, not another review round or implementation-readiness approval. The existing review findings and their resolutions remain the review record.

## Contract coverage

| Check | Result |
|---|---|
| Sources and inheritance | Both spines link to repository-owned requirements/ADRs and shared platform spines. Leave has no local token overrides. Shared colors, typography, spacing, corners, borders, icons and drawer treatment supply the visual contract; light mode only is approved. |
| Document shape | DESIGN uses the canonical visual sections. EXPERIENCE contains Foundation, Information Architecture, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, Responsive & Platform, Inspiration & Anti-patterns and Key Flows. |
| Journeys and surfaces | IA destinations map to named, numbered journeys with outcomes and failure limits. Added explicit on-behalf and employee-settings journeys to expose already-approved behavior rather than bury it in correction/setup flows. Source feature names are retained; source requirements have no UJ identifiers. |
| Component alignment | Every named Leave Component Patterns section has a corresponding DESIGN component row. Employee Leave settings now has its own heading rather than sitting under Audit history. Shared primitives inherit platform rules rather than creating a competing component system. |
| State coverage | Shared load/empty/error, permission/session, concurrency, save/retry and uncertain-outcome rules apply to all relevant surfaces. Leave adds calculation, approval, acknowledgement, coverage, lifecycle and derived setup states. The state table distinguishes accepted behavior from delivery verification. |
| Visual references | All 28 promoted HTML keepers are linked inline from a spine; no orphan keeper was found. Seven earlier comparison studies remain explicitly historical. The inventory records limitations and the accepted written-pattern scope. |
| Latest approvals | Editable discretionary grant, one paid/unpaid request, minimal notification panel, stale-request feedback, upload readiness, return to My Leave after confirmed submission, partial loading, light-mode scope, on-behalf, role lifecycle, setup readiness and final shared visual defaults are reflected. |

## Accepted coverage without separate mockups

Routine profile creation/default/archive variations, temporary-approver changes and loading/error variants use the approved compositions and written patterns. Notification, upload, stale-record and partial-load feedback have approved text presentations. Shared sign-in/NGO/language surfaces inherit the platform contract. Consultant import and client approval stay in the runbook/email process rather than creating a Leave confirmation screen.

These choices do not waive implementation or testing. Historical mocks are composition examples; current contracts and authoritative business decisions govern conflicts, including final-approval acknowledgement gates and automatic return to My Leave after submission.

## Finalization blockers

No remaining user design choice was identified in this bounded check. The nine prior findings have been addressed in the source contracts or keeper corrections as recorded by the parent review-resolution work. The required structure/prose editorial passes are complete, with all six recommendations applied. Both Leave spines are final for UX handoff; that status does not mark the broader shared platform drafts or Phase 1 implementation readiness complete.

## Delivery follow-up

- Validate rendered responsive thresholds, focus restoration, keyboard/date navigation, error associations, meaningful announcements, zoom and assistive-technology behavior. Numerical contrast and static/script checks are not accessibility certification.
- Implement shared wrappers and shell patterns through the existing silo/service boundaries; validate authorization, identities, combined roles, NGO privacy and concurrency at runtime.
- Resolve architecture mechanics already identified upstream: exact policy-field validation, schedule/ledger impact calculation, month-end/leap-day expiry arithmetic, version/snapshot schema, imports and rollback contracts. These are not new visual-design approvals.
- Complete end-to-end state and action coverage for partial mock interactions, then run the repository's Phase 1 readiness process before Leave implementation is authorized.

## Scope of this pass

Edited only the Leave DESIGN/EXPERIENCE spines and this coverage note. No runtime, schema, shared-UI implementation, scaffold, agent-context or accepted ADR was changed. Existing documentation references and inherited design decisions were clarified; no new defaults or product behavior were introduced.

## Final verification

Final source checks passed: 215 relative file links, 15 inherited token references,
all 28 keeper references linked, unique keeper HTML IDs and syntax for 24 inline
scripts. The corrected interaction handlers also passed simulated-DOM checks.
Browser and assistive-technology verification remain delivery requirements.
