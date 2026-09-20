# Requirements revalidation — resolution log

20 September 2026. The validation report remains the original revalidation snapshot.

| Finding | Disposition |
|---|---|
| R3 — carry-over month arithmetic | Resolved by approved ADR-0089: preceding matching date, or destination month end when the matching day is absent; leap-year examples, inclusive eligibility and earlier-expiry preservation recorded. |
| R6 — operational targets | Resolved by user approval: architect/security own signed-operation lifetime; technical lead/operations own recovery and alerts, agreed by architecture completion; product owner/technical lead own browsers and workload/performance targets by relevant story planning. Verify all before pilot. Numerical targets remain downstream deliverables. |
| R9 — unpaid on-behalf acknowledgement | Resolved by user decision and ADR-0088: submit then employee response; final approval waits, even with a sole submitting approver; exact amount and employee draft protected. Acceptance examples added. |
| R10 — stale request controls | Corrected to date/duration controls and truthful autosave with Close/Submit. Source updated date refreshed. |

No product code or tests implemented. Existing accepted ADRs remain unchanged.
Requirements/UX/tracker updates preserve separate funding, approval and employee
acknowledgement authority. No new scaffold/shared-UI implementation or agent-context
change. Implementation readiness remains pending.
