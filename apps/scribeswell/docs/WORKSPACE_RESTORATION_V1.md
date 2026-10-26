# Same-device workspace restoration v1

Status: adopted technical contract for CAP-11/ST-35; bounded component delivery
implemented, independently reviewed and verified:994 browser passes/2 expected
native integration skips,18.1m, and passing TypeScript/production build. Parent
patch audit closes the review corrections; one pre-existing shared Notes adapter
malformed-response defect is deferred. Consumes canonical reader-interaction,
WORKSPACE_TABS_V1, FOUR_PASSAGE_LAYOUT_V1 and existing personal Studies HTTP
contracts. Actual-owner/native-device/session, shared-resource and release gates
remain deferred to final integration.

## Device representation

Use native IndexedDB, one object store in a database scoped to the configured
Scribeswell base path on this origin. Store closed versioned DTOs: one public record
and at most three account-keyed private records. No persistence dependency or generic
platform persistence framework. Public data contains at most12 ordered tabs, each
with at most4 validated panes, active identities, canonical references, bounded
existing reading anchors and opaque tab incarnations. Private data contains only
the verified account ID and matching tab key/incarnation, acknowledged study/note
IDs and optional custom labels. Anonymous labels remain memory-only. Enforce the
existing key/reference/anchor/label bounds plus96KiB public and32KiB per private
record, measured as UTF-8 JSON bytes; test maximum accepted combinations.

Never serialize workspace views/maps generically, raw invalidSearch, note/study
titles or bodies, snippets, highlights, selections, credentials, command attempts,
receipts, native undo/caret or unsent input. Invalid-link provenance may be a closed
boolean; its arbitrary query bytes are not durable data. Public labels always
derive from public references. Storage is metadata, never permission or an offline
editor. Existing Auth SDK session storage remains separately owned.

Records expire after30 device-clock days; this is best effort, not a security TTL.
Reject non-finite/future-invalid timestamps and malformed/oversize current records.
Unknown future versions remain untouched and suspend writes, including cross-window
read-before-write version checks. Expiry/eviction never deletes server resources.
Retain the three most recently completed account records; pruning occurs atomically
with a successful eligible write and cannot expose another account's metadata.
Use a closed safe-integer completion ordinal in private storage records, assigned
inside that serialized transaction, to order retention even when device timestamps
tie or move backwards. It is storage metadata, never authority or business content.

Public/current-account projection commits are atomic. Never erase another account's
record merely because the window is anonymous. Last completed transaction wins for
future reload/return; no live window merging, leases or heartbeat. Serialize/coalesce
each window's writes: one executing batch, at most8 pending batches and64 waiters
per batch. Reject excess through the existing unavailable failure; never drop an
accepted distinct owner batch. Same-owner coalesced success acknowledges the latest
projection in that batch, not every intermediate projection. Debounce250ms with2s
maximum while changes continue, and skip equal projections. Lifecycle flush is best effort without unload guarantees. A
single open/read/write attempt has a3s total deadline; abort timed-out transactions
and ignore late open/read completions. No private network wait occurs in an IDB
transaction. Quota/denied/blocked/evicted failures leave reading usable, with concise
Reading setup not remembered feedback and explicit Retry; do not promise durability.

## Bootstrap, links and tab lifetime

Public reading starts immediately. Capture the original URL/native snapshot/entry
before the first user checkpoint; the current controller has no initial checkpoint
effect. Hold device writes while reading or resolving remembered setups. A late
automatic result cannot rewind intervening tab/pane/navigation/scroll/tool/edit or
account intent. Retry after changed intent requires an explicit current decision;
never silently apply the stale bootstrap projection.

An ordinary root return restores the saved active public setup. A compatible retained
native snapshot matching a stored tab may reuse its incarnation and ref-matching
anchors. A fresh explicit link controls its displayed target, has no private
association, and can restore other remembered setups alongside it. Never infer a
private association from equal passage references. Avoid duplicating a genuinely
retained native tab; equality of references alone is insufficient.

At12 stored tabs plus a fresh link, keep the fresh target displayed and stage the
remembered set outside the live collection. Offer explicit indexed choice of a
remembered tab to close, then install the remaining11 beside the fresh tab. Cancel
keeps the current target and old device record with Retry; no implicit eviction.
Current matching URL remains collectable. Intervening intent invalidates automatic
installation; Retry re-reads and offers an explicit replacement decision for the
current setup, preserving existing last-context guards. Never silently drop newly
created current tabs: if the union exceeds12, require explicit victims until it fits.
One controller owns commits, anchors, history and capacity; do not reuse its held
mismatched-history marker for this distinct matching-URL state. Existing mismatched
history also suspends durable writes. Restore itself never pushes history.

Give each live tab an opaque incarnation outside URL/history. Preserve it for
surviving-tab replay and retained-device refresh; create a new one for new tabs or
closed-tab replay, even when history reuses the same tab key. Private candidates
bind account + key + incarnation. Sign-out, anonymous closure and public replay
must never resurrect an old private association when its former owner signs in.

## Identity, authority and hydration

Verify identity before private writes as well as restoration. Add a narrow helper
inside existing Auth transport ownership: bounded GET of the configured provider's
/auth/v1/user using the captured token/public anon key, returning only a validated
canonical account ID or safe typed failure. Use existing15s authFetch bound plus
caller cancellation. Consume only the ID from the ordinary provider response; do
not log/cache the response or token. Missing configuration fails unavailable
without contacting the placeholder. This helper never mutates SDK sessions; do not
use SDK getUser(jwt), whose late session_not_found can remove a newer session.
Match verified ID to current captured session/account/token generation and ignore
stale completions. SDK signin/signup/signout/callback ownership remains unchanged.
No protected Studies call is triggered merely by untouched standalone signup.

Private restore separately obtains current Studies admission/resource authority
through existing Scribeswell api.study/api.note; label-only context can use current
api.studies after identity verification. No automatic enrollment or new Access path.
Validate owner_account_id and expected study/note/parent IDs in responses for the
delivered owner-only contract; future sharing needs its own compatible contract.
Progressively hydrate at most two requests concurrently, active tab first, with a
30s overall attempt; cancel/ignore unfinished work and expose Retry. Inactive
candidates stay hidden until verified; do not mount hidden analysis/network work.

StudiesContext owns hydration into its existing single account/resource lane. Do
not call ordinary openStudy/openNote (which navigate/guard/open tools). Capture
account/token epoch, tab incarnation, fields-map identity, navigation and input
generation. Late results cannot recreate closed views, change focus/tools/active
tab, replace newer selections or overwrite edited lanes. Refetch acknowledged
content; never restore an unsent body. Pending candidates are distinct from live
empty views, so Auth loading/outage cannot overwrite them with null. Opening
Studies for an authorized restored selection must load its current ordinary note
page/cursor and collected passages through the existing owner, preserving selected
note/dirty lanes. Do not require Leave/reselect to make the restored panel usable.
Keep current access/freshness and bounded read handling; this is ordinary context
consumption, not permission stored in metadata.

On401 or unavailable identity/access, hide private context and retain candidates
for Retry. Confirmed account admission denial clears owned private candidates and
labels; confirmed resource denial/deletion clears only affected associations and
sensitive labels. Public layouts survive. Explicit selection/replacement/closure,
deletion acknowledgements and confirmed denial update projections deliberately.
Sign-out clears live private state; retained metadata stays owner-bound and hidden
from anonymous/different accounts. No stored positive authority is durable proof.

## Verification and impacts

Observe a real IndexedDB reload acceptance red before storage/runtime changes;
characterize risky Auth/controller/lanes first. Use focused TDD for DTO privacy,
bounds, pending preservation, failure/version/expiry policy and races. Browser
fixtures use real IDB/reload/two windows with intercepted Auth/business HTTP only.
Cover fresh link precedence/12-cap/Cancel/intervening intent; same/switched account;
late old401 after new signin; changed-input/closed-incarnation stale hydration;
denial versus outage; quota/blocked/evicted/old/malformed/oversize records; completed
transaction ordering; actual stored absence of forbidden fields. Retain exact
commands/results and source hashes; broad browser/build follow affected checks.

Scaffold/shared UI: app-owned until proven neutral reuse. Agent context: no new
rule. Docs: this contract, evidence and canonical handoff. ADR: applies existing
decisions, no accepted decision edits or new platform choice. No API/migration,
provider/deployment activation, Leave/factory or Access/Notification implementation.
Native SQL, actual Auth/Identity/Access/session integration, KDG55481/55482, physical
devices and release qualification remain the final integration phase.
