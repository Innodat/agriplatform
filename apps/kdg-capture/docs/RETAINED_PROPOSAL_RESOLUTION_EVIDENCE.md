# Retained own-proposal resolution — 2026-10-26

Implementation, independent review and final26-command qualification pass.
This technical subset of approved
Story2.3 completes persistence paths for confirmed pending-create edit409, unsent active
work stale after server progress, and explicitly reconsidered paused proposals. It adds
no HTTP endpoint, server command version, service, schema upgrade or mounted behavior.

Existing server review/choice/lookup APIs accept validated new source classifications.
Current server records still come from authorized read/edit-context; replacements are
fresh ordinary v1 intents at the revision actually reviewed. Actual create/ancestor
receipts establish v2 provenance. No missing server creation/audit fields are fabricated.
Unknown prepared outcomes block competing decisions; original bytes remain retained.

Local paused review uses the actual chosen phone state and may retain a pending chosen
ancestor. New edits wait for matching actual predecessor receipts. New server/local
reconsideration decisions use versions3/4 in the existing isolated schema4 store;
legacy server/local versions1/2 remain recognized. Earlier paused dispositions and
immutable decision identities stay intact. A new decision links the exact prior pause,
with bounded generation relationships and complete retained-effect validation.
Original current-review own-read is privately pinned for new choices; refreshing a
partition cannot renew it. Current own-read recovers committed choices after original
expiry, edit denial, reopen and legitimate progress.

The first focused acceptance failed active-unsent stale review before implementation.
The initial integrated candidate passes70 actual synthetic HTTP/Chromium IDB checks.
Three actual creates and six edits produce exactly nine committed outcomes/history
entries, with balanced storage and verified normal owned-fixture shutdown. Scenarios
cover actual v2 conflict, fresh server replacement, offline local reconsideration of its
paused child, actual ordered receipts, committed response loss and actual edit403
followed by read-only receipt recovery without repeat PUT. Additional v1/v2 unsent
branches become stale after actual remote progress, adopt actual current state, then
explicitly reconsider paused children. Earlier/later decisions recover after progress;
actual read403 blocks protected recovery. The unprepared stale branch cases issue no
original PUT.

Acceptance audit reproduced a legacy descendant-disposition decoder regression and a
mixed legacy-local/new-server linkage recursion. Registered RED frames and corrected
regressions are retained privately. Source-bound687 focused checks and70 integrated HTTP checks pass. All26 affected
commands pass, including all24 prior suites and five scaffold parities. All262 current
source hashes,179 protected historical/dependency files and85 unchanged backend sources
are verified;342 backend tests are reused only with those unchanged effective sources.
All14 review findings were individually triaged:13 addressed, one low-impact type
refinement rejected with evidence, none deferred. Mixed retired/paused branches now
use compatible retained encodings; strict historical versions remain unchanged.
Regressions cover complete historical head consistency, longer actual v2 receipt
lineage, local reconsideration atomicity/CAS and independently corrupted/missing links.

The first broad run passed eight commands, then a preexisting create-proof20ms timer
expired before its intended receipt-storage phase. A controlled30ms pre-phase delay
reproduced receiptPhaseReached=false. The test now selects that phase before expiring
a controlled ten-second deadline, awaits the actual delayed consume, and retains the
same timeout/no-receipt assertions plus an explicit phase-reached assertion. Corrected
create proof passes220 checks. Its original failure, exact before-source and controlled
probe remain retained. Production code did not change for this correction. The first candidate reused eight unchanged-effective-source proofs, then passed the
corrected command and remaining17 commands. Following review patches, all26 commands
were executed fresh on the final262-source map; none of those26 results is reused.
The HTTP proof's injected stall ends after10.5seconds with confirmed normal fixture
shutdown. A private missing-compiler-project injection exits1, publishes its failed
result/types/failure logs with unchanged sources, and starts no fixture or browser.
The combined100-action/100-decision fixture measures local/server review, exact
recovery and refused insertion under explicit30-second fences; every measurement passes.
No extra runtime optimization was introduced. Exact commands, source/result references and traceability are in the
[machine record](evidence/retained-proposal-resolution-20261026.json).

Impacts: KDG-specific origin, questionnaire, proposal and permission logic stays local.
Existing builder Auth/IDB primitives remain adopted; verify all five scaffold parities.
No demonstrated neutral defect requires a template change. Shared UI and agent context
are unchanged; contracts, handoff, README and evidence are updated together. Accepted
ADRs remain immutable. No complete Story2.3/UI, native, browser update/device or release
readiness claim. Auth/Access and backend storage remain synthetic fixtures; no actual
PostgreSQL permissions/rollback or physical-device durability is established.

Synthetic local/CI only. Preserve concurrent work, historical evidence/resources and
TS7.0.2. No UI/editor/Leave, active sender/claims/queue/scheduling/browser/service-worker/
startup activation, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/
migrations, deployment/production/pilot or cleanup. Fingerprints/HMAC remain deferred.
Never read/run/copy/hash the preexisting untracked migration fixture.

The first post-review broad attempt reached its240-second outer process allowance
without result publication. The interrupted capsule/log remains; shutdown is not
claimed confirmed. Final qualification uses a660-second process allowance around
the existing600-second proof watchdog. Behavioral30-second fences are unchanged.
