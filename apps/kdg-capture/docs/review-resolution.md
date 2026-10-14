# Planning review reconciliation

2026-10-12. All reviews inspect documents/source, not running KDG software.

| Review | Finding and disposition |
| --- | --- |
| [PRD rubric](reviews/review-prd.md) | Expiry ambiguity corrected: token expiry alone permits local use within valid seven-day window; window expiry/logout/learned denial lock. Approved JSON split recorded in architecture/contracts. |
| [Architecture rubric](reviews/review-architecture-rubric.md) and [adversary](reviews/review-architecture-adversary.md) | Exact scoped renewal, paused/reviewed descendant edits, retained baseline/overlay/conflict state and durable cross-tab claim/conditional acknowledgement added. |
| [Architecture recheck](reviews/recheck-architecture.md) | Four material findings resolved; FR/NFR acceptance coverage complete. Low child-management capability clarified in contracts. |
| [UX coverage/accessibility](reviews/review-ux.md) | Identified theme source/extraction gate and contrast targets, matching component contracts, per-surface loading/empty/denial/error states, language metadata, assignment journey and interrupted-upgrade UX. Saving classification subsequently approved by user. |
| [UX recheck](reviews/recheck-ux.md) | Material findings resolved or explicitly gated; remaining base label/numbered-step refinements completed in component tables/UJ1–4. |
| [Technology](reviews/review-technology.md) | Retained stack fits; actual lockfile versions/Node floor recorded, Expense manifest incompatibility flagged, strict durability is a browser hint, physical devices remain distinct from emulation. No replacement stack needed. |
| [Editorial](reviews/review-editorial.md) | Clarified local/server acknowledgements and absence of mocks. Preserve intentional cross-document safety reinforcement; canonical UX section order retained over proposed Key Flows move. |

Initial review files retain their original findings as evidence; this file records
subsequent corrections rather than rewriting reviewers' historical conclusions.
There are no unresolved material app-boundary divergence findings from these reviews.
Shared handoff, contract validation, policy assumptions and the BMAD epic/stories menu
remain explicit readiness gates. Independent review is not user approval.

User decisions captured in BMAD memlog: JSONB/relational split, fixed Khula, Nee default,
seven-day local access, KDG session coordination, fast drafting, UX validation lenses,
and unfinished-input autosave/explicit completion/whole-form capture editing.
These are preserved in the PRD/UX/spine/contracts; no user input has been set aside.

Requirement extraction: 18 FR, 5 NFR, 14 UX items; acceptance groups KDG-A01–A22.
Requirements were subsequently confirmed with C; the five-epic structure and Stories 1.1–1.4 were then approved. Candidate 1.5 is the
current sequential review. Story links remain incomplete until the installed epic workflow
confirmations.
All physical/runtime evidence is planned, not executed. Architecture linter passed
with zero findings; final app-owned link/whitespace checks follow below.

Scope update, 2026-10-13: earlier autosave approval is superseded by the user rejecting
unfinished-entry recovery. Current PRD/UX/spine/contracts and revised candidate 1.5
use explicit Save. Earlier review conclusions do not cover this new saving scope;
questionnaire administrative drafts and completed-capture synchronization remain.

Current checkpoint: the user accepted explicit Save and requested next; revised 1.5
is now formalized. Candidate 1.6 adds server create/receipt/read and foreground sync;
its wire/fingerprint/readiness gates and ordinary story approval remain pending.

E1 checkpoint: final 1.7 and all seven E1 scopes/closure approved with C; no runtime
completion implied. E2 candidate 2.1 introduces own-history/cache pagination and is
awaiting its review. Original-version/own-after-unassignment/pending-overlay safeguards
remain; all-record administration is E3.
