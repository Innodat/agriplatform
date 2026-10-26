# Explicit confirmed-server own conflict resolution — 2026-10-26

The unmounted owner consumes approved Story2.3 for server-backed confirmed edit
conflicts. It reviews actual current detail or edit-context and records an explicit
use-current decision or a new complete replacement. Each invocation has a fresh Auth
lease, a30second total maximum/default and HTTP phases capped at10seconds/remaining.
No lease or transaction spans human review; external waits finish before local writes.

Use-current requires current own-read, including when own-edit is denied. It adopts
the actual reviewed current record without a PUT or fabricated server revision.
Replacement requires fresh exact own-edit context and the capture's original
definition, preserving the revision actually reviewed and using a new operation.
Actual server mutation still goes through existing conditional PUT, receipt/recovery
and readback. A lost response retains original identity; another server change
produces another ordinary conflict and preserves the new saved proposal.

Committed decisions recover under retained own-read before HTTP or new-edit checks.
Retry identity binds the original reviewed selection and normalized complete input,
so server progress or edit revocation cannot turn an exact retry into a new write.
Recovery validates actual retained effects and refuses missing/contradictory linkage.
An unavailable read probe after edit denial leaves independent own-read intact.

The local decision, new replacement/overlay and internally derived branch dispositions
commit atomically. Original source commands, proposals/bases, create bytes and
descendants remain retained. Descendants stay paused and never inherit a replacement
revision automatically. Unknown earlier prepared outcomes block a competing decision;
an unresolved lookup alone cannot exclude an in-flight commit. Head/current-state/
generation checks reject stale reviews. Late old outcomes cannot revive a resolved
branch or clear newer work. Storage failure does not imply rollback after commit.

Current detail and entry context do not renew seven-day offline observations. Existing
valid retained own-read is required; expired scope safely requires the existing
setup/history refresh. Original reviewed edit expiry is checked independently of
fresh current context. Read/create refresh and own-edit restoration remain separate.

The isolated format advances additively from schema3 to4, adding immutable resolutions
and capture indexes while preserving every existing store and opaque row. Old
connections close on versionchange; schema3 code refuses4. This prevents older code
from ignoring resolution fences. Activation remains gated on a coordinated compatible
browser update and recovery plan; this synthetic proof makes no ordinary-release
rollback or physical-device claim. No running app/storage is upgraded by default.
Conflict review and decision recovery refuse captures with more than100 retained
actions or unsupported/incomplete work. This declared qualification bound preserves
every row and makes no success claim for oversized branches.

Final qualification passes22 source-bound commands:282 focused
checks,77 actual synthetic HTTP checks and all20 affected regression/parity commands,
including five scaffold parities. Exact commands, source hashes, requirement mapping
and retained RED/GREEN frames are in [evidence](evidence/conflict-resolution-20261026.json).
Archived-source replays reproduce the recovery/decoder/graph/effect/normalization/cursor
failures. Two review rounds are complete:21 findings addressed, five rejected with
evidence, none deferred. Focused RED frames precede all four round2 decoder corrections.
Independent-connection races, deferred lookup/refresh cancellation/deadlines and actual
read403 branches pass. At100 actions/99 retained decisions, actual review took4.4seconds
within30seconds; fixture construction is recorded separately. No optimization was added.
The HTTP proof covers read-only adoption without server writes, exact retries after
server/baseline progress, replacement response-loss/receipt recovery under read-only,
repeated conflict and edit revocation between review and decision. Its four captures
have exactly11 committed outcomes/history entries (four creates/seven edits), with
balanced synthetic storage acquisition/release and verified child shutdown.
Same-phone unprepared and pending-create conflict decisions are the next separate
subset; no complete Story2.3/UI readiness claim is made.

Delivery impacts: KDG owns conflict and command semantics; builder Auth/IDB primitives
and their five parities are reused. Shared UI and agent context are unchanged. Current
contracts/handoff/README and evidence are updated; accepted ADRs remain immutable.
Retained Node26.11.1/TS7.0.2/modules/Chromium/Python only. No new endpoint/service,
runtime sender/startup, real accounts, native PostgreSQL/Docker, provisioning/migrations,
deployment/production/pilot or cleanup. Concurrent work, historical evidence/resources
and the dependency baseline remain preserved. Fingerprints/HMAC stay deferred.
