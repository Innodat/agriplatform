# Confirmed own-note deletion — bounded contract

**Component implementation delivered; native migration/owner/session qualification prepared only.**
[Delivery evidence](NOTE_DELETION_EVIDENCE.md) records executed checks and remaining integration boundaries.
This is the own-note subset of CAP-10/ST-24–25. It inherits
[personal notes](PERSONAL_NOTES_V1.md), [note references](NOTE_REFERENCES_V1.md)
and [library search](LIBRARY_SEARCH_V1.md). Whole-study deletion follows separately.

## Authorized command and recovery

Add `DELETE /api/studies/{study_id}/notes/{note_id}` with the existing strict bounded
JSON decoder, exactly `operation_id` and `expected_revision`. Both retain their
existing UUID/revision rules. Reject query parameters, unknown/duplicate fields and
malformed input through the fixed400/no-store envelope. There is no generic upsert,
client-supplied account/actor, new grant or implicit enrollment.

Fresh Access checking precedes the local transaction. Require the active own study
and active own note. Use command `note.delete`, version1 and the existing fingerprint
binding of command/path/payload. Under the existing operation-lock → parent-study-lock
→ note-lock order, compare the expected note revision and lifecycle together. A stale
revision gives the existing `note_revision_conflict`; unavailable/foreign/closed targets
give the existing safe404. Refuse revision overflow without erasure or a receipt.

One transaction replaces the note value with the exact empty format1 aggregate
`{"document":{"version":1,"blocks":[]},"connections":[],"highlights":[]}`,
sets `active=false`, increments its revision once, records server actor/UTC update
attribution and inserts the compact immutable operation receipt. Return the existing
OperationAck shape with `command=note.delete`, original study/note IDs and the committed
final note revision. This explicit erasure is separate from the active-note format2
downgrade prohibition. Other notes, study metadata and the collected-passage list do
not change. References and future marks held inside this note aggregate disappear
with its value; no independent copy/other-owner data is traversed.

Retain only the existing note identity/scope/lifecycle/revision/attribution and compact
operation evidence in application tables. Receipts hold IDs/revisions and server-only
fingerprints, never prior bodies/labels/reference payloads. No undelete, historical-body
retention or backup-erasure promise is introduced. Ordinary read/list/search exclude
the tombstone. The empty aggregate preserves the existing non-null storage shape;
nullable note values or another lifecycle store are unnecessary.

Only an original committed `note.delete` may replay or resolve through operation lookup
against the same owned inactive note. Verify its retained scope without requiring an
active parent; recovery still works after a later owned-study closure. Current Access
always applies. Return the original compact acknowledgement without any new write.
Changed original payload fails `operation_payload_mismatch`. A new delete operation
against a closed note refuses404. Historical create/replace receipts continue to refuse
after deletion: they neither return content nor recreate the note. Unknown outcomes
retain the original delete operation/payload; unresolved is never proof of rollback.

## Structural and release contract

Prepare controlled migration0004 after0003; never edit prior migrations. Widen only
the receipt command/resource-shape checks for `note.delete`, and add an ordinary
constraint requiring every inactive note value to equal the exact empty aggregate.
The existing trigger continues to prohibit inactive→active. Together these prevent
alternate writes from retaining/repopulating a closed note's payload or reopening it.
Existing restricted update grants suffice; add no table/delete/admin privileges.

Constraint installation must fail transactionally if pre-existing inactive rows hold
payloads. Do not silently erase/adopt those rows during migration; preserve them for
an explicit controlled recovery decision. Migration failure blocks activation and
does not reverse already-applied histories. Ordinary previous-version API readers and
writers exclude closed notes and remain compatible; prove this using the actual
previous checkpoint implementation. Historical fixture constructors must exclude0004
when constructing earlier histories. No runtime-startup migration is permitted.

## Confirmation and the existing save lane

Offer Delete note through the selected owned note's actions. Confirmation names the
action: “Delete this note?” and explains that its writing and highlights will be
removed while other notes remain. Cancel is the safe initial focus and changes no
data. Explicit confirmation includes discarding this note's unsent local writing if
deletion succeeds; do not autosave merely to erase that same unsent input.

Opening confirmation captures account/study/note/lane identity and pauses its pending
save timer while retaining input. Cancel before a delete attempt resumes the existing
save policy. Do not issue deletion alongside an executing/unknown prior save: allow
the already executing save to settle within one bounded preparation interval (at most
five seconds). If a prior attempt remains unresolved, preserve the input and show a
simple save-recovery action; retry only that original save first. A separately confirmed
delete may proceed once its outcome is known. Never reinterpret an unknown save as
rolled back, invent a new expected revision or silently replay deletion after sign-in.

Once ready, freeze the actual current confirmed note revision and one delete operation.
Suppress editing/new saves for this target during executing or unresolved deletion.
The existing execute adapter may perform bounded read-only outcome lookup after a
lost reply. An explicit Retry deletion reuses the same operation/payload. Show truthful
“Deletion not confirmed” feedback when uncertain; no success, rollback or undo claim.
Other notes and public reading remain usable. Preserve target input until a committed
acknowledgement; then evict precisely that lane/list item/selection and stop all of its
timers/finalizers. A stale save/read response cannot reinsert the deleted note locally.

A definitive revision conflict preserves local input and requires current-note review
and a fresh explicit confirmation; never automatically advance the delete revision.
Current denial/account replacement clears or masks private state using the existing
session policy. Account replacement/sign-out dismisses private confirmation/attempts
and rejects late success/denial. Reauthentication never confirms/replays a delete.
Capture the target so navigation cannot make confirmation delete a different note.
An original unresolved deletion remains recoverable within the same account's in-memory
state; ordinary navigation cannot discard its operation identity or permit new writes
to that target. No private body, operation payload or label enters URLs/browser storage.

## Evidence and impacts

ATDD must first observe runnable missing-delete API and browser-confirmation failures;
focused TDD covers strict DTO/ack/error/lookup and serialized storage-method behavior.
Desktop/mobile component tests cover cancel, dirty input, executing/unknown save,
lost delete reply/same-operation retry, conflict, navigation/account races and late-save
non-resurrection while preserving other notes, passages and reader position.

Prepare restricted native tests for atomic erasure/attribution/receipt, rollback,
save/delete races, alternate-write constraints, overflow, foreign owner, original-delete
recovery and historical create/save refusal. Prepare actual-owner UI plus independent
SQL proof of the exact target tombstone and unchanged non-target rows. Syntax/collection
are preparation only. **Native/owner/session execution remains at final integration.**

Scaffold/shared UI: reuse existing app command/save/error patterns; do not promote
an unproven deletion abstraction. Agent context and accepted ADRs: unchanged. Update
owned generated clients, delivery evidence, app contract and canonical status in this
slice. No Access/Identity competitor, sharing/notification owner, Leave/factory work,
provider/config/deployment/activation or production-data deletion is authorized here.
