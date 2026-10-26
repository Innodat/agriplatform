# Content association and reclamation

**Status:** Technical planning candidate, 2026-10-25; implementation not authorized.
**Owners:** Content references/physical bytes; each application its domain associations.
**Authority:** Platform ADR-0020/0022/0025–0030/0033/0035/0038/0054; the
[Content ownership/read contract](content-ownership-and-authenticated-read.md).
This supplies E4's agreed bounded protection, not a new authorization callback service.

## State and command ownership

Content owns upload, verified immutable bytes, reference protection, disposal fence and
provider outcome. Leave owns draft revision/lifecycle, attachment allowance/limits,
association and original operation outcome. Neither reads the other's database.
All commands authenticate a restricted service and compare exact application, typed
resource scope, content ID, association ID and operation ID. Those identifiers are
references, never authority. Calling service policy permits only registered operations.

Use one durable application association operation with a terminal outcome. A prepared
operation is internal coordination, not a visible attachment or a new application status.
Its stable input binds draft, expected revision, content identity and association identity;
reusing its ID with changed input fails. Content references have pending, confirmed and
released states, bound to that operation. Released identities are terminal. Physical
content disposal is separate and cannot succeed while any legitimate reference protects it.

The first consumer persists only this information plus attribution, timestamps, the
fixed preparation deadline, compact outcome and required outbound intents. This is not a
general transaction coordinator, application ACL store or shared domain object model.

## Association sequence and linearization

1. Leave authenticates the user and validates current draft ownership, editability,
   revision, policy allowance and declared content reference. Under its local guard it
   records the pending operation before making the Content call. It releases the lock.
2. Leave requests Content reference preparation. Content checks service/owner/scope,
   readiness/fixed identity and reclamation state, then durably creates or recovers the
   pending reference. It returns the reference and fixed deadline. A disposal fence wins
   against a new prepare; successful prepare protects bytes against later disposal.
3. Leave reacquires its local draft/operation guard, rechecks current local conditions and
   verified type/size/aggregate limits, and resolves the operation. Success commits the
   association, draft revision, compact outcome and confirmation intent atomically.
   Failure commits terminal non-commit and release intent. External waits are outside locks.
4. After commit, deliver confirm/release to Content idempotently. A locally saved
   association is confirmed business input even if the Content acknowledgement is lost;
   its pending Content reference still protects bytes. The normal read can resolve that
   protected ready object under current application authorization. It must not hide a
   committed attachment or falsely say an uncommitted association was saved.

The application commit in step 3 decides whether the attachment exists. A Content
prepare or upload success alone cannot decide it. Confirm is accepted only for that
matching protected operation and committed owner outcome, never for released/reclaimed
identity. An expired preparation enters reconciliation; it is not immediately deleted.

For initial implementation use a ten-minute preparation budget from its first durable
creation. Retries do not reset it. After expiry, normal execution must resolve through
the reconciliation path instead of renewing protection. Recovery examines due work at
least every five minutes, warns when fifteen minutes overdue and escalates at one hour.
These are bounded operational defaults, not retention or draft-expiry rules. A retry
does not extend an outstanding signed upload capability's separate expiry.

## Expiry, recovery and explicit release

On expiry Content marks the reference as awaiting reconciliation while keeping its byte
fence. The registered application-specific recovery operation resolves the exact durable
association operation under the same guard as step 3. It returns either committed with
the matching association/content, or terminal non-commit with a durable decision that
future step 3 attempts must obey. This outcome probe is a narrow recovery contract; it
does not answer ordinary file authorization or expose draft/request contents.

If the local operation is pending, recovery atomically chooses its valid committed
association or terminal non-commit. A competing commit can win first; release cannot
then claim abandonment. If recovery wins terminal non-commit, a delayed commit fails.
Content confirms the former or releases the latter. A missing operation can authorize
release only through an owner outcome that also fences creation of that same operation
ID; an unprotected not-found response is insufficient. Do not reconstruct it later as new.

When the owner is unavailable or outcome binding is inconsistent, retain the fence,
record selected safe diagnostics and alert restricted operations. Retry is bounded per
attempt; unrelated items continue. An operator may resolve with authenticated owner
evidence, not by merely deleting a lease or guessing from age. The fixed execution
deadline and escalation prevent silent indefinite renewal; uncertainty cannot justify
destroying possibly saved input. No distributed clock agreement substitutes for the
owner's terminal compare-and-set outcome.

Remove/discard/replacement commits local association release and outbound intent under
the existing domain guard before asking Content to release protection. Saved associations
do not expire merely because a browser closes. E5/E6 consequential request transitions
extend this same owner lifecycle before their activation; E4 does not pretend to prove
those future transitions with a mock. Replacement uses a new content identity and retains
old protected evidence where required.

Do not prune terminal operation/reference evidence while supported delayed operations
can be replayed. Initial delivery retains compact tombstones without automatic pruning;
the operator capacity budget blocks new preparations before exhaustion rather than
silently dropping fencing evidence. A later retention design must prove old attempts
cannot recreate reclaimed identities and must preserve consequential audit separately.

## Disposal and staging

Leave supplies version-bound domain eligibility and commits release intent. Content
independently requires no reference/protection and atomically claims a disposal fence.
An association/renewal either won before that fence or is rejected after it. Provider
deletion follows outside database locks using a durable disposal ID. Success is recorded
only with the supported provider's definitive evidence. Timeout/crash remains recoverable;
never rewrite it as completed or allocate replacement bytes to the old identity.

Abandoned-upload discovery reuses these fences and the disposal worker. No age-only
query bypasses pending reconciliation. Staging cleanup distinguishes redundant uploaded
staging from the verified sealed locator. A still-capable or in-flight upload can leave
late provider bytes: discover and reclaim those against the terminal upload identity
without promoting it back to ready. Old capabilities never target the sealed namespace.
Provider expiry/in-flight completion/version deletion semantics and finite reclamation
budgets are proved by 4.1–4.3/4.12-S on the selected provider; this protocol does not
claim those experiments have run or assume a generic URL's expiry cancels a transfer.

Minimal tombstones retain identity/scope/operation/disposition/time/actor and safe outcome
references, not filenames or document contents. Active-object deletion and backup expiry
are distinct. Restore/replay applies disposal/reference outcomes before restoring ordinary
readability and outbox execution. Do not report erasure from every backup when only the
active object is gone. Existing backup retention and release recovery remain binding.

## Parent-clause allocation and acceptance oracles

AC numbers refer to Given blocks in the unchanged parent stories in `epics.md`.
One primary owner implements each side; integration witnesses do not duplicate engines.

| Parent source | Implementation owner | Required observable oracle |
| --- | --- | --- |
| 4.4 AC01 | 4.4-L AC01/02 | Current user, draft, policy and verified content checks govern the actual local commit. |
| 4.4 AC02 | 4.4-L AC02 | Concurrent attempts cannot exceed three files/20 MB total or per-file/type restrictions. |
| 4.4 AC03/04 | 4.4-L AC03, 4.4-S AC01/03 | Lost upload/prepare/commit/confirm replies recover one content/reference/association; only local commit means saved. |
| 4.4 AC05 | 4.4-S AC02, 4.4-L AC04 | Cleanup-versus-association has one fenced outcome and preserves committed input. |
| 4.4 AC06/07 | 4.4-S AC04/05, 4.4-L AC04 | Deadline causes terminal owner reconciliation and monitored uncertainty, never blind deletion or endless retry renewal. |
| 4.4 AC08 | 4.4-L AC04, 4.4-S AC05 | Closed/revised/released/reclaimed attempts cannot resurrect or overwrite. |
| 4.4 AC09 | 4.4-L AC05 | Reopened saved attachment remains available; permanently missing content is reported honestly. |
| 4.11 AC01 | 4.11-L AC01/02, 4.11-S AC01 | Version-bound domain release and an independent Content protection check both succeed. |
| 4.11 AC02/03 | 4.11-S AC01/02, 4.11-L AC01/02 | Saved/pending references block deletion; release and renewed protection cannot both win. |
| 4.11 AC04 | 4.11-S AC03/05 | Successful disposal preserves minimal evidence and permanently retires the byte identity. |
| 4.11 AC05/06 | 4.11-S AC04, 4.11-L AC03 | Crash/provider uncertainty retains original outcome/recovery responsibility; unrelated work proceeds. |
| 4.11 AC07 | 4.11-L AC04, 4.11-S AC05 | Authorized later reads say disposed accurately without metadata leaks or resurrection. |
| 4.12 AC01/05/06 | 4.12-S AC01/04/05 | Lifecycle-derived eligibility, safe staging removal and truthful original deletion recovery. |
| 4.12 AC02/03 | 4.12-S AC01/02, 4.12-L AC01/02 | Exact owner outcome and actual saved association protect bytes. |
| 4.12 AC04 | 4.12-S AC03, 4.12-L AC03 | Late provider bytes/confirmation/retry cannot reactivate a reclaimed identity. |
| 4.12 AC07 | 4.12-S AC05, 4.12-L AC04 | Overdue protection/storage has attributable alerts and restricted recovery. |

Shared children use a registered restricted fixture caller and real Content/database
state; Leave children use actual draft state. Evidence must cover both orderings of
commit/reconcile/dispose, process death between each durable boundary, duplicate/change-
payload attempts, owner outage, current scope denial and previous-release recovery.
No production cleanup or runtime acceptance has been executed by writing this document.

## Remaining design and impact boundaries

The owner split and race protocol are now concrete planning candidates. Provider models are selected below; the owning read contract selects the ingress/session
adapter and Leave document-retention contract selects applicability as a candidate.
These are G03 planning models, not real-provider/browser proof or silent user acceptance. Source/contract changes update generated DTOs and
restricted-role/native/browser fixtures with their first implementation consumer.
No shared runtime framework, employee-facing cleanup UI or new generic BMAD lifecycle.

## Provider execution model — technical planning candidate 2026-10-25

Use the current Supabase S3-compatible adapter's SigV4 PUT with 900-second expiry,
rather than the standard Storage upload-token route with its different lifetime.
Azure uses an exact staging-blob SAS permitting the required create/write operation,
HTTPS only, with expiry no more than 900 seconds after issuance and a server-side
credential held only by Content. Prefer the already-configured managed identity/user
delegation credential where available; no production identity is provisioned by planning.
Neither capability grants list, read, delete, another object or the sealed namespace.
Renewal rechecks service/domain/lifecycle authority and keeps the same content identity
only while its upload remains recoverable. It cannot revive terminal abandoned content.

The current repository already uses `ExpiresIn=900` in
[provider.py](../../../../services/content-service/provider.py); that is source evidence,
not real-provider expiry proof. [Supabase S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication)
documents server-only keys and S3 compatibility. [Azure's SAS guide](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-user-delegation-sas-create-python)
documents resource/permission/expiry constraints. [Amazon's presigned URL guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
explains replay and replacement of the same key. These sources were checked 2026-10-25;
S3-compatible Supabase enforcement must still be tested, rather than inferred from AWS.

Finalization copies uploaded staging into an attempt-unique, server-only sealed candidate,
then verifies the candidate's actual length, digest and allowed file signature/media type.
Do not verify staging and later publish a mutable staging locator. An Azure asynchronous
copy must reach definitive success before verification; a pending copy is not ready.
See [Copy Blob](https://learn.microsoft.com/en-us/rest/api/storageservices/copy-blob).
The owner atomically publishes only one verified candidate locator against its finalizing
operation/fence. Published locators are never overwritten or used for a subsequent copy;
retries resolve the already-published locator. Unpublished candidates are reclaimable
only after their operation resolves. Version IDs, where supported, are retained as part
of the exact locator. Do not require a new general WORM retention policy merely to seal.

This attempt-unique model prevents a delayed old sealing attempt from overwriting the
locator selected by a newer attempt. Replaying a staging capability can at most change
staging: it cannot change a published candidate or make failed verification successful.
Copy/verify and provider waits hold no business write lock. Start with a 180-second
verification attempt deadline, 1 MiB buffers, 5-second connect/30-second upstream-idle
bounds and one owner-controlled retry after reconciliation; the complete original
operation retains its fixed recovery identity. PtS's larger source support is distinct
from Leave's per-file/aggregate restrictions.

After a capability expires, do not infer that an already-started request stopped. An
abandoned upload remains terminal in Content while its exact staging key and any
unpublished candidates remain in cleanup discovery. Start a cleanup pass at least every
five minutes, reconcile pending owner outcomes first, and repeat deletion if late bytes
appear. Failed/overdue reclamation uses the existing 15-minute warning/one-hour escalation.
No automatic capability renewal follows abandonment. Configured staging capacity stops
new uploads before exhaustion and alerts operations; normal saved references remain
readable. Real provider request/late-completion/resource evidence belongs to 4.1–4.3
and 4.12-S, not a fabricated claim of finite erasure from an unknown provider timeout.

The delivery oracle must run both providers: replay before/after 900 seconds, a transfer
started before expiry completing after expiry, concurrent finalizers with different
attempt candidates, crash after copy/before publication, invalid length/signature/digest,
post-ready upload replay and disposal during late completion. A failing provider path
blocks activation and requires a compatible fix or linked superseding decision, never a
frontend expiry timer or publication of mutable bytes. These selected models close the
unselected-mechanism planning question; actual provider qualification remains delivery.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0064-approved-onboarding-continuity-and-content-contracts.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.
