# WSA Finance

WSA Finance is the working name for Wycliffe South Africa’s finance app. Its first module, **Field Journal**, lets field teams keep their monthly journals offline and gives Finance an Excel workbook it can process through the existing RDE import. The first pilot covers a project bank journal, with the April 2026 Mongu ZMW workbook as a layout reference.

## Team administration

An authorized administrator can create a team, assign an existing user as its preparer, and change or end the assignment. A monthly journal belongs to its team, journal reference and period. A handover preserves the journal, receipt references and the identity of the person who made each entry. A preparer can capture for their assigned team. Accountants can see the teams they are authorized to review.

## Capture during the month

Preparers can record one transaction when it happens or enter a stack of receipts in one sitting. Prioritize fast batch entry. Keep the current team, journal and period in view. **Save and next** saves the row on the device, updates the running balance and moves directly to the next row. Support keyboard navigation on devices with a keyboard. A saved row can be reopened after a restart, corrected before submission, and linked to its receipt. A statement belongs to the journal for the month.

Capture works offline in the preparer’s chosen language, including account labels, validation messages, dates and amount formatting. Preserve the accounting codes, currency and original transaction descriptions across language changes and Excel export. Confirm the pilot language and terminology with its field team.

## Two calendar months of offline access

A successful online check of the preparer’s current team assignment starts or renews a two-calendar-month offline access window for that team. For example, a check on 10 April gives an expiry date of 10 June. Show the expiry date and make the periods, account choices and translations needed during that window available on the prepared device. The submission schedule remains monthly.

Reopening the app offline does not renew access. At expiry, stop further offline entry and preserve saved rows and pending support. On reconnection, check the current assignment before accepting uploads or a submission. If the preparer was reassigned while offline, keep unsynced work on the device. Finance and the field team handle any missing entries manually outside the app.

## Early visibility and monthly submission

Sync saved entries when the app is open and connected. Resume interrupted transfers without duplicating entries. Distinguish work saved on the device, entries confirmed by the server and support still awaiting upload.

Authorized accountants can see synced entries and provisional totals during the month. Show **In progress** and the last successful sync so Finance can judge how current the view is. The preparer reviews the period and explicitly submits one identifiable journal version. Finance sees **Submitted** only after the server confirms receipt of that version. Keep subsequent corrections traceable to the version they amend.

Finance can download the submitted workbook with the filename and Register layout expected by the existing period RDE, together with the associated support. Finance retains receipt review, reconciliation and the import decision.

## Pilot acceptance

- On a field device, enter a representative batch in the preparer’s language, close the app, and reopen it offline. Verify saved rows, receipt references and the running balance. Time the batch with the preparer.
- Cross a monthly boundary offline, check the displayed expiry, and verify that offline use cannot extend it. Confirm expiry preserves saved rows and receipts.
- Interrupt a sync after the server has accepted an entry. On retry, verify Finance sees the entry once, in a journal that remains in progress until explicitly submitted.
- Verify that ending a preparer’s assignment prevents further uploads and submission while preserving entries already saved on the device.
- Replay a reviewed bank journal with its matching period RDE. Import the original workbook and the app export into separate clean copies. Compare dates, receipt references, account codes, debit and credit amounts, and opening and closing balances. The Mongu layout sample has no entered amounts, so obtain a completed pair for this check.

## Existing references

- The WSA Finance SystemMap documents the monthly process in `24-Field-Journal-Setup-and-Workflow.md` and the Excel import contract in `25-Field-Journal-Data-and-Business-Rules.md`.
- KDG provides tested examples of saving offline, reopening after a restart, recovering interrupted sync and protecting another user’s pending work. Use that evidence when evaluating reuse for the journal’s two-month window. [KDG offline verification](../../kdg-capture/docs/STORY31_OWN_WORKSPACE_EVIDENCE.md)
