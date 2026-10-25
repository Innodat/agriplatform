# Confirmed whole-study deletion — bounded contract

**Component implementation delivered; final native/owner/session qualification pending.**
[Delivery evidence](STUDY_DELETION_EVIDENCE.md) separates executed component checks from prepared integration. CAP-10/ST-24–25,
following [personal notes](PERSONAL_NOTES_V1.md), [note deletion](NOTE_DELETION_V1.md)
and [library search](LIBRARY_SEARCH_V1.md). Final native/owner/session integration
remains deferred by user direction266. No activation is authorized.

## Command, transaction and recovery

Add strict `DELETE /api/studies/{study_id}` accepting exactly `operation_id` and
`expected_revision` through the existing bounded JSON decoder. Reject query parameters,
unknown/duplicate fields and malformed input. Use `study.delete`, version1, and the
existing command/path/payload fingerprint. OperationAck is study-shaped (`note_id=null`),
with the final study metadata revision. No client account/actor or implicit enrollment.

Fresh Access precedes the local transaction. Lock operation then the owned parent
study FOR UPDATE, using the existing total transaction deadline (five seconds). Check
active ownership, expected metadata revision and revision overflow together. A stale
metadata revision returns existing `study_revision_conflict`; closed/foreign/unavailable
resources return safe404. Study revision remains metadata-only: it does not summarize
independent note or collection revisions. Confirmed deletion removes all currently
owned child content when this serialized transaction commits, including child edits
that committed before its parent lock. Do not invent an aggregate version.

Preflight revision overflow on the study and all active child notes. Atomically erase
and close every active owned note using the exact empty format1 aggregate from note
deletion, incrementing each affected note revision once with server actor/UTC attribution.
Already inactive notes remain unchanged, preserving their original deletion receipt.
Delete passage entries then their passage-list header. Set the parent title to the
fixed non-sensitive sentinel `Deleted study`, active=false, increment study revision
once with server attribution and insert one compact immutable study.delete receipt.
Keep study/note identities, scopes, final revisions and attribution required by receipts;
retain no prior titles, bodies, links or passage entries as recovery payloads. Other
studies and independent copies/recipient-owned responses are outside this deletion.
No backup erasure, undelete, asynchronous batch completion or unbounded-size success
promise. Failure rolls back the transaction; unknown outcome is not proof of rollback.

All existing API child writers already lock the parent first. Thus a concurrent write
commits before cleanup or sees the closed parent and refuses. Read/list/search exclude
closed studies and their contents. Historical study.create/rename/collection and
note.create/replace receipt recovery refuses after parent closure. Only the original
committed study.delete may replay/resolve against its same owned inactive parent under
current Access, without a write. Changed payload refuses operation_payload_mismatch;
a new operation against a closed parent refuses404. Original note.delete recovery
continues to work after parent closure, returning its original final note revision.

## Ordinary controlled migration0005

Preserve0001–0004. Widen only receipt command/resource-shape checks. Add an ordinary
CHECK requiring inactive study title=`Deleted study`; retain existing monotonic lifecycle.
Grant runtime only the additional DELETE on passage_lists needed for owned cleanup.
No new identity/access authority, broad grants, service imports or security-definer path.

Enforce closed-parent integrity for alternate restricted writes with small ordinary
invoker triggers (schema-qualified, safe search_path; revoke PUBLIC function access):
BEFORE INSERT on notes, passage_lists and passage_entries locks the scoped parent
FOR UPDATE and refuses absent/inactive parents. BEFORE UPDATE of studies resulting
in inactive state refuses remaining active notes or passage rows/headers. Erase children
before closing parent. Existing inactive-note CHECK/monotonic/scope guards prevent
payload refill, reopening or moving notes; do not add parent locks on child UPDATE
which would invert normal parent→child lock order. Do not claim protection against a
schema owner deliberately removing its safeguards.

Preexisting closed-parent violations must fail migration, never be erased/adopted.
The migrator owns tables but is NOBYPASSRLS and has no app.account_id; a plain SELECT
under FORCE RLS cannot establish absence. Inside the controlled migration transaction,
keep RLS enabled, temporarily remove FORCE on the relevant owned tables, validate all
closed-parent relationships using ordinary EXISTS, install guards and restore FORCE
before commit. DDL locks prevent a committed relaxation window; failure rolls back
these toggles and DDL. A fixed safe error blocks activation pending explicit controlled
recovery. No startup migration or automatic reversal. Previous API readers/writers
remain compatible; freeze the actual f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be consumer
for prepared verification and preserve earlier frozen consumers.

## Browser confirmation and all target lanes

Offer Delete study for the selected owned study, naming it and explaining permanent
removal of all its notes/highlights/collected passages with no undo, including discard
of this study's unsent writing/title input only on success. Cancel is initial focus.
Opening captures account/study/navigation identity, pauses every target note timer and
new title/collection/create action, and retains all input including final IME composition.
Do not autosave merely to erase. Other studies/public reading remain usable.

Coordinate existing note save/finalizer, title/title-read, collection, target creation
and child-deletion lanes. Settle executing operations within one preparation interval
of at most five seconds total. If any prior operation remains unknown, offer recovery
of that original operation first. Recovery never automatically confirms study deletion;
require a separate explicit fresh confirmation after known outcomes, using current
confirmed metadata revision. An explicit recovery action shares one five-second total
budget across original operations and its remaining preparation; timeout retains original
identities/input and ignores late state effects. A definitively failed prior save may be discarded only
by that fresh explicit whole-study confirmation, not by cancel/navigation.

Freeze one ready delete operation/payload. While executing/unknown, prevent new target
writes and retain input. The existing execute adapter may read-only lookup a lost reply.
Explicit Retry deletion uses the original identity/payload; show `Deletion not confirmed`
when uncertain. Same-account navigation retains discoverable, distinctly labelled
recovery. Sign-out/account replacement masks private state and rejects late effects;
reauthentication never auto-confirms or replays consequential deletion.

Definitive revision conflict requires serialized current-title/revision review and fresh
explicit confirmation; Cancel preserves independent write-lane bases and input. On
acknowledgement evict precisely this study, all its note/collection/title state, timers,
selections and resolved pending target recoveries. Retain server receipts. Acknowledge
no child rollback. Deleted-study identity and live lane/epoch checks must protect both
success and failure continuations of late list/search/page/open/read/create/save/title/
collection/delete responses. They may neither reinsert the target nor affect another
selection/account. Reuse focus provenance/current-tool guards from note deletion;
never steal focus from a deliberate surviving public-reader control. No private content
or command payload enters URLs/browser persistence.

## Evidence and impacts

Observe runnable missing-route API and missing-action browser ATDD failures first.
Observe focused DTO/storage-method TDD failures before implementing SQL behavior;
record chronology honestly. Cover atomic erasure/overflow/original receipts/current
Access, all target-lane preparation, unknown recovery, dirty/IME/cancel, conflicts,
account/navigation and stale success/error responses in component tests.

Prepare restricted native migration/rollback/raw-write/race/old-consumer cases and
actual-owner UI plus independent SQL assertions. Update historical fixture exclusions,
next failed-migration number, owner oracle and its synthetic unit inputs together.
Run collect/syntax only; native/real-owner/session execution waits until final phase.

Reuse app command/save/error/focus patterns; no unproven shared deletion engine or
scaffold/UI promotion. Agent context and accepted ADRs unchanged. Update generated
contracts through owning tools, app delivery evidence and parent-owned canonical status.
No Access competitor, sharing/notification owner implementation, Leave/factory,
provider/config/deploy/production mutation or use of KDG55481/55482.
