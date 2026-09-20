# Leave UX review resolution — 20 September 2026

This update follows the user’s instruction to apply the straightforward corrections
from the final review. The [validation report](./validation-report.md) remains the
original findings snapshot. This log records subsequent disposition; it is not a
new independent review or browser accessibility certification.

| Finding | Disposition | Evidence / remaining work |
|---|---|---|
| UX-R08 — visual defaults | Resolved by user decision | Shared 6px controls, 8px cards/dialogs, modest marker corners, 1px borders, Lucide icons and the approved subtle drawer separation are recorded as inherited tokens. |
| UX-R09 — on-behalf component index | Addressed in source | Added the matching DESIGN component-table row and approved reference. |
| UX-R10 — setup status criteria | Resolved by user decision | Derived Not started / Needs review / Ready / Couldn’t check predicates recorded in EXPERIENCE and product requirements; no manual completion or consultant-email state. |
| UX-R11 — reference promotion | Addressed | 28 approved composition references promoted to mockups; seven comparison studies remain historical. Inventory identifies current, historical and accepted written-pattern coverage. |
| UX-R12 — stale status prose | Addressed in reviewed locations | Removed obsolete dark-mode/standard-width open statements, corrected setup reference and routine-state coverage, condensed duplicated policy-review wording. Remaining architecture/rendering questions are preserved. |
| UX-R13 — final approval gate | Addressed in source | Allocation flow and acknowledgement copy now explicitly gate final approval. Otherwise-authorized intermediate steps may proceed; accepted ADR-0032 remains unchanged. |
| UX-A01 — field-error associations | Corrected in prototype source | Dedicated reason/name error IDs, aria-describedby and invalid-state lifecycle; role-level workflow errors remain separate. Browser/AT verification outstanding. |
| UX-A02 — allocation announcements | Corrected in prototype source | Dedicated polite status announces settled radio/amount changes; initial render and keystrokes do not trigger repeated announcements. Browser/AT timing verification outstanding. |
| UX-A03 — history semantics | Corrected in prototype source | Period status for user navigation, selected-date pressed state on ordinary buttons and explicit return to selected date. No new grid keyboard contract introduced. Browser/AT verification outstanding. |

## Verification

Before editing, static inspection reproduced the three missing error relationships,
the missing allocation status region and the absent month announcement.

- `node /tmp/check_leave_review.cjs` — passed simulated-handler checks for invalid-state lifecycle, role-name versus workflow errors, and increased/unchanged/decreased unpaid allocation announcements on committed changes rather than each keystroke.
- `node --check` for each modified inline script — passed.
- Python HTML inspection — unique IDs and accessible-description targets resolve in modified references; history source includes period status and selected-date semantics.
- Relative-file checks cover current shared/Leave spines, the promoted inventory and links between handoff HTMLs.

These checks do not run a browser, screen reader, touch target assessment, zoom,
reflow or a real API. The sample calculations remain illustrative. Do not infer
production readiness or change document status to final from these results.

## Impact

- Product rules: no new funding, approval or permission rule; clarify the existing ADR-0032 finalization gate.
- Scaffold and shared UI: no implementation changes. Shared documentation reflects already selected dimensions and light-only scope.
- Agent context: no change.
- Documentation: update Leave/shared spines, keeper links, inventory and this resolution log; preserve the reviewer snapshots.
- ADR: accepted decisions remain unchanged; no superseding ADR needed for corrections that align with existing decisions.

Both remaining user choices are approved. Final handoff distillation and the required editorial passes are complete; both Leave spines are final. Final checks covered 215 relative file links, 15 inherited tokens, all 28 keeper references and 24 inline scripts. Runtime accessibility and implementation readiness remain separate.
