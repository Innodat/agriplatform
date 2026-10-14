# E4 planning closure — approved

2026-10-14. Both stories and E4 planning closure are user-approved with C. This checks planned coverage only; no application,
publication, synchronization or physical-device test has been executed.

| Story | Approved scope |
| --- | --- |
| 4.1 | Small online editor; one saved working copy; explicit Save/Cancel; stable question IDs; add/reorder/retire and supported types |
| 4.2 | Explicit immutable publication; atomic live pointer/draft closure; safe replay; offline old-version acceptance, pinned forms and historical editing |

## Requirement allocation

| Requirement | E4 coverage | Boundary |
| --- | --- | --- |
| FR-10 | 4.1 rating/Ja-Nee/text editor and optional Ja details; 4.2 explicit Publish | No branching/scoring/general builder |
| FR-11 | 4.1 stable IDs/immutable live definition; 4.2 old/new-version lifecycle and references | Retired questions survive in old versions; no silent migration |
| FR-5 | Editor supported definition validation; 4.2 new published controls | Initial Afrikaans Ja/Nee/default Nee and numeric rating semantics remain |
| FR-2/12/16/17 | Current questionnaire.manage on each editor/publish request, scope/session/role negatives | Membership/platform admin alone grants no access; all administration online |
| FR-8/9 | 4.2 original-questionnaire owner/admin edits with normal record conflicts | Publication cannot bypass capture authority or revision checks |
| FR-13/14 | Old offline capture accepted; latest download changes only next entry | Pending operations pin original version; no version picker |
| FR-18 | Atomic definition selection, referenced-version retention and upgrade compatibility | E5 remaining pilot retention/reliability evidence |

NFR-1 scoped current authorization/attribution, NFR-2 immutable/atomic/replay safety,
NFR-3 accessible editor/controls, NFR-4 bounded online operations and NFR-5 affected
release/device proof bind both stories. UX-DR5/7/10–14 are assigned in these surfaces;
E5 completes child/facilitator management and pilot reliability.

## Saving, lifecycle and evidence

Questionnaire draft means one explicit saved working copy, not autosave/recovery.
Save prepares; Cancel drops unsaved typing; Publish commits the exact saved copy.
A published working copy closes; late Save/retry cannot reopen it. Starting another
working copy is explicit. Concurrent editor changes are reviewed in memory, with no
server-stored conflict draft. Actual observations retain their original questionnaire.

4.2 requires the actual editor/publish producer while Android/iPhone PWAs are offline,
not merely seeded version fixtures. Verify old-version synchronization, an already-open
entry staying pinned, a later new entry using the downloaded update and original-version
historical editing. Automated and installed physical evidence remain distinct and pending.

## Gates and next step

Concrete working-draft start/lifecycle, validation limits, publication/outcome/error DTOs,
constraints and queue/version fixtures remain affected Build gates. Current shared
Identity/Access/scaffold/release prerequisites and Leave ownership handoff remain.
No People or E5 management UI dependency; no wait for all Leave planning.
Epic-completion confirmation is recorded; sequential E5 detailing proceeds. Complete BMAD
final validation/readiness and stop for implementation approval afterward.
