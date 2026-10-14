# Architecture correction recheck

Date: 2026-10-12. Sources: corrected ARCHITECTURE-SPINE.md, contracts.md and testing.md. Planning-only review; no tests executed.

## Verdict

All four previously reported divergence findings are resolved at planning-rule level. No remaining critical/high architecture finding was identified. Concrete shared schemas, privileges, operator binding, approved open policy choices and eventual executable evidence remain readiness gates; this result does not authorize implementation.

| Finding | Resolution and acceptance coverage |
| --- | --- |
| Unrelated authorization renews stronger cached rights | AD-7 and contract Offline window explicitly renew only corresponding capability/assignment observations; KDG-A16 checks unrelated success cannot renew stronger rights; KDG-A15 covers token/local-window distinction |
| Conflict descendants undo reviewed resolution | AD-6 and contract Conflict pause dependent unsent edits for explicit re-review, retain proposals and prohibit automatic replay/rebase; KDG-A11 covers this chain |
| Downloads overwrite pending local state | AD-6 retains pending overlays/conflict evidence; contract Queue preserves newer local snapshot after older acknowledgement; KDG-A10/A18 cover acknowledgements, downloads and pruning |
| Cross-tab drainers race and stale acknowledgements corrupt state | AD-5 compares durable claim/local sequence; contract Queue uses transactional IndexedDB claims with interrupted-attempt recovery; KDG-A09/A10 cover duplicate sends, two tabs and interrupted drainer |

## Remaining small contract clarification

- **low — Child-management permission mapping:** proposed capability table gives assignment management a name and domain guard, while the API table also contains child save. Explicitly map child creation/edit/deactivation to that capability or a separately registered exact capability before the administration story/shared schema gate. Do not infer it merely from an administrator role label. This is a refinement of an already gated capability catalogue, not a new role or service.

## Requirement-to-acceptance coverage

Every FR-1–FR-18 and NFR-1–NFR-5 appears in the acceptance map. Required source boundaries have concrete planned scenarios: fixed Khula/current server authority; own/all-scoped editing; offline installed launch and close/reopen; conditional details and multiple daily captures; interrupted sync/idempotency; concurrent edits; old-version sync/historical editing; user/org isolation; session expiry/pending work; schema/shell updates. Shared owner tests are explicitly separated from KDG semantics. Physical Android/iPhone installation, offline and assistive-technology evidence is distinguished from browser automation, and early synthetic-device proof precedes the full portal.

These are scenario plans, not runnable or passing tests. Story links are correctly pending the mandatory epic-planning confirmation step. Final requirement→story→test traceability and implementation-readiness checks must follow that step; the current acceptance map alone cannot be called completed delivery traceability.
