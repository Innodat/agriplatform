# E3 planning closure — approved

2026-10-14. Both stories and E3 planning closure are user-approved with C. This checks planned coverage, not implemented
behavior or runtime readiness; no code, browser or physical-device test has run.

| Story | Approved scope |
| --- | --- |
| 3.1 | Online administrator organization-wide observation reads and compact audit details; current read.all |
| 3.2 | Online Save/Cancel correction, current edit.all, preserved original owner/actual editor, conditional writes and in-memory conflict review |

## Requirement allocation

| Requirement | E3 coverage | Boundary / later work |
| --- | --- | --- |
| FR-2/8 | 3.1 all-authorized reads/audit, 3.2 edits with original owner preserved | No cross-org scope, People dependency or separate supervisor |
| FR-9 | 3.2 facilitator/admin edits in both orderings, repeat conflict, explicit replacement/current choice | Facilitator proposals stay durably on their phone; administrator uncommitted input stays in memory |
| FR-11 | 3.1/3.2 exact original questions/validation | E4 actual editor/publication/late-version compatibility |
| FR-13/14 | Own-only PWA behavior unchanged; 3.2 verifies pending facilitator edit survives online administrator change | No offline organization-wide cache/lease or admin queue |
| FR-15 | 3.1 online unavailable/partial vs empty; 3.2 true save/conflict/uncertain outcome | Receipt recovery is distinct from a saved draft |
| FR-16/17 | Current read.all/edit.all, role-loss/session/account/org isolation and late-response guards | Seven-day offline allowance applies only to own PWA actions |
| FR-18 | 3.2 verifies all-record response not persisted to phone; own pending state protected | E5 final pilot retention/reliability |

NFR-1 authorization/privacy and attribution, NFR-2 conditional writes/idempotency,
NFR-3 accessibility, NFR-4 bounded online checks and NFR-5 affected release/device
proof bind the introduced surfaces. UX-DR4/5/7–10/12/13 are covered in current portal
scope; questionnaire/assignment management remains E4/E5.

## Simplicity and test boundaries

Capturers and Louwnique use My observations offline in the PWA. The responsive online
administrator portal reviews/edits all authorized Khula observations and exposes compact
audit metadata/events; no revision browser/archive or dashboards/exports.

Administrator conflicts are handled immediately using in-memory attempted answers and
fresh current record. Closing/reloading may discard uncommitted input; no server-stored
conflict proposals or resolution drafts. Normal receipts recover unknown save outcomes.
Durable capturer offline saved proposals and paused descendants retain E2 safeguards.
First-reader priority and privileged force overwrite are never introduced.

ATDD links are in testing.md and each approved story. 3.2 requires both concurrency
orderings, repeated conflicts, role/session loss, cross-org denial, receipt replay and
actual facilitator installed-PWA conflict after an administrator change. Emulated,
automated and physical evidence stay distinct; no test results are claimed in planning.

## Dependencies and next step

Concrete all-read/all-edit schemas/actor-display/context/error/outcome fixtures and
shared owner prerequisites remain Build gates. E3 relies on E1/E2, not E4/E5, normal
onboarding or all Leave planning. Shared changes still require agreed Leave handoff;
reusable conditional-write/pagination/operation/status patterns use existing owners.
Epic-completion confirmation is recorded; sequential E4 detailing proceeds. Final BMAD
validation/readiness and user approval remain required before implementation.
