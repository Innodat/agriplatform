# KDG unfinished-input simplification — superseded proposal

**Resolution, 2026-10-13:** The user rejected even minimal unfinished-form recovery.
Current plan uses explicit Save only; before-Save typing may be lost on close/restart.
Historical alternatives below are not requirements. See [app rationale](architecture/decisions/0001-explicit-observation-save.md)
and [revised Story 1.5](story-candidates/1-5-save-observation-on-phone.md).

2026-10-13. Story 1.5 is not approved. The user questioned both Retry-only guidance
for persistent local-storage failure and the size of the unfinished-input workflow.
This proposal does not change the approved first four stories or shared ADRs.

## Recommended smaller scope

Retain automatic recovery of one unfinished new-observation form per phone/account/
Khula, with automatic resume and no draft list or unfinished-form merge screen.
Save observation remains explicit; multiple completed captures per child/date remain
allowed. Completing or explicitly discarding the current form permits a new one.
This is a proposed opt-in local workflow limit, not a universal draft constraint or
a server-side limit on captures. User preference is pending.

The alternative is explicit Save only. It still needs local-save failure handling,
and removes the earlier promise to recover interrupted unfinished entry. Closing or
restarting before Save can lose typing; choosing it requires updating the app's
requirements/saving rationale and affected acceptance examples. Neither option removes
record revisions, account/org isolation or synchronization conflict handling.

## Failure behavior common to both options

| Condition | Behavior |
| --- | --- |
| No internet | Normal local operation; no local save error or Retry merely for disconnection |
| Potentially recoverable local transaction interruption | Resolve uncertain write first; one bounded recovery attempt, then honest status if unconfirmed |
| Storage quota reached | Reclaim only verified re-downloadable, disposable cache if available; never pending captures, drafts, conflicts or their required versions; retry once after reclamation |
| Quota still reached / nothing safe to reclaim | Preserve values on screen, stop repeated automatic attempts, explain storage issue and give an action before manual Retry |
| Repeated unexpected storage failure | Keep input visible, do not claim successful saving or suggest clearing KDG/browser data; plain error and optional safe diagnostic reference |
| App restart | Not first-line recovery while current input is only in memory. Suggest only after acknowledged preservation, or after explicit acceptance of losing unacknowledged input; do not claim restarting fixes quota |

Proposed quota wording: **KDG Capture doesn’t have enough storage on this phone. Your
latest changes haven’t been saved. Keep this screen open, free some phone storage,
then try again.** Do not infer that the whole phone disk is full from browser quota
alone, or guarantee freeing space resolves every browser/storage failure.

Proposed repeated-failure wording: **This phone couldn’t save your latest changes.
Keep this screen open so you don’t lose them.** Do not expose IndexedDB codes or make
a nontechnical facilitator diagnose the database. A concrete safe recovery action
depends on the classified failure; never invent a Restart fix for an unknown error.

If unfinished-input autosave is retained, accepted platform ADR-0050 still supplies
inline Changes not saved / Retry and exit-only Stay / Close anyway. Retry is a means
to attempt saving after recovery, not the complete explanation or an assurance it
will fix storage. Normal acknowledged local saves close with no prompt. Technical
details remain in safe diagnostics, not the product flow.

## Why preserve the small safety net

Normal phone interruption/closure benefits from a locally acknowledged checkpoint;
this does not require user-facing draft administration. Deliberately crashing discards
the very in-memory values at risk and cannot produce missing storage capacity. Removing
automatic recovery does not remove the same storage problem from explicit Save.

Primary references: [IndexedDB transaction errors](https://www.w3.org/TR/IndexedDB/)
and [WebKit quota/eviction policy](https://webkit.org/blog/14403/updates-to-storage-policy/).
Inherited saving/failure rules: [ADR-0050](../../../platform/docs/architecture/decisions/0050-inline-draft-save-failure-and-exit-confirmation.md)
and [ADR-0051](../../../platform/docs/architecture/decisions/0051-saving-conventions-by-workflow.md).

No code, dependencies, migration, live data or physical tests are changed/executed.
