# Ordered local edit reconciliation — 2026-10-26

This isolated consumer connects completed saved edits to the existing command,
receipt and current-detail contracts. It prepares a frozen command under its original
action identity, acknowledges only that action and preserves newer saved changes.
It activates no sender, automatic retry, worker or UI.

A first action uses its reviewed revision. A successor waits for its exact
predecessor's committed receipt, including a receipt with an unchanged revision.
Preparation stores the exact wire snapshot before returning it; repeating preparation
must not pick up a newer downloaded revision or generate a replacement operation ID.
Unknown outcomes retain the original identity and payload for later bounded recovery.

Receipt and conflict consumption validates the supported closed contract and the
prepared account/organization/action/target. A receipt alone is not a current-state
snapshot and supplies no creation/update attribution. Current authorized readback
alone never acknowledges an uncertain operation. Confirmation requires both matched
receipt and original-owner detail; a late acknowledgement cannot overwrite newer local
work. Own predecessor progress can support its existing ordered chain, while an
unrelated remote revision still requires attention.

Conflicts preserve the attempted command, reviewed base, completed proposal and safe
current revision. Descendants remain unsent and retained; this consumer provides no
implicit rebase or conflict-resolution decision. Existing own-read/edit, denial,
clock, account and transaction/publication protections remain binding. A completion
failure may retain committed original-account work; recovery keeps its original ID.

Scaffold impact: use the existing builder-owned IDB completion primitives; edit ordering,
original questionnaire and receipt policy are KDG domain logic. Promote a neutral fix
only if a concrete failure demonstrates one. Shared UI and agent-context impacts:
none. Documentation appends contracts/prepends the handoff while preserving prior
bytes and evidence. ADR impact: inherit accepted decisions; no accepted ADR edits.

The proof is synthetic Chromium IndexedDB plus previously qualified exact adapter
contracts. It establishes neither physical-device durability nor actual PostgreSQL
permissions/transaction effects. Pending-create persistence/setup, sender claims and
scheduling, active queue/browser/service-worker/default-startup wiring, UI/editor/Leave,
real accounts/Auth/Access, native-driver/Docker qualification, provisioning/migrations,
deployment/production/pilot and cleanup remain outside this delivery. Dependencies
including TypeScript7.0.2 are preserved; fingerprints/HMAC remain deferred.

The local store adds explicit operations:

| Operation | Contract |
|---|---|
| `prepareEdit(action_id, execution)` | Under valid own-read/edit, persist and return immutable `{pending, serialized}` for a supported eligible action. The pending value is structurally compatible with the existing PUT adapter. |
| `consumeEditReceipt(pending, outcome, execution)` | Under valid own-read, consume the existing adapter's closed committed result for that exact frozen command. Identical consumption is idempotent; contradictory/foreign/unsupported results refuse. |
| `consumeEditConflict(pending, outcome, execution)` | Consume the exact typed revision-conflict result and retain its attempted command/proposal/base plus current revision. No English error matching or automatic resolution. |

Preparation returns `prepared`, `blocked` or `invalid`, alongside the existing safe
`expired`, `denied` and `unavailable` authority/execution results. Consumers return
`reconciled` or `invalid`, or the relevant authority failure. `prepared` confirms
stored bytes only; it does not claim that a network attempt occurred. The same frozen
payload remains available for original-identity recovery even after a newer read.
A not-yet-prepared action facing known unrelated server progress is blocked for
attention; that local observation is not manufactured as a server conflict response.

Receipt revision must equal the frozen expected revision or its single successor.
Current detail at that same revision must match the acknowledged date/answers before
retiring the latest overlay. A newer authoritative detail may instead confirm that
the already-acknowledged action completed while displaying a later server state.
Newer local overlays, unresolved bases and attention proposals stay intact. Subsequent
normal edits use their newly reviewed base; existing descendants continue only their
own acknowledged chain. Readback never renews edit permission or resolves a conflict.

Outcome consumption uses own-read independently, so a committed fact can be retained
after edit-only denial/expiry while new preparation remains blocked. Callers must use
the existing validated transport/recovery owner and preserve its account/session
execution fence when passing results to storage. This isolated storage proof does not
claim that an activated Auth-to-sender coordinator exists.

Run the exact commands in [the machine record](evidence/edit-reconciliation-20261026.json)
from repository root. Primary proof: approved Node26.11.1 with
`apps/kdg-capture/web/tests/edit-reconciliation-proof.mjs`. It asserts TypeScript7.0.2
and uses explicit selected-source capsules. Required retained prerequisites are
`platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`,
Playwright under `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root`,
and the approved Chromium installation under
`platform/deployment/.local/web-baseline-qualification/browsers/`. A clean checkout
alone lacks these ignored prerequisites. No installation, package or baseline change
is part of this delivery; existing CI toolchain owners must supply approved artifacts.

Final source-bound verification passes all30 affected jobs: 103 reconciliation checks,
92 local Save checks, 61 history checks,575 compiled client tests,
127 direct tests, four fixture guards and16 loopback groups. Six strict adapter
configurations, twelve schema/client freshness checks and five scaffold parities pass.
The prior313 backend proof is reused only after matching all77 backend source hashes;
no new backend execution is claimed. Independent review addressed nine of ten findings;
one complexity proposal was rejected and no new work was deferred.

| Requirement | Executed evidence |
|---|---|
| Exact preparation and predecessor ordering | First reviewed command, successor wait, parent receipt, unchanged receipt and three-action continuation cases |
| Stable bytes across tabs/reopen/unknown outcome | Initial and competing preparation, cross-realm/reload, unresolved result and frozen newer-read cases |
| Exact receipt/retained delivery safety | Foreign/extra/version/revision refusal, duplicate/contradictory outcomes and unsupported persisted delivery cases |
| Receipt-bound readback and provenance | Readback without receipt, same-revision answer/date mismatches, newer authoritative detail, late overlays and original actor/detail cases |
| Conflict and unrelated revision protection | Known unrelated baseline, conflict retention, descendants blocked, no automatic resolution or rebase |
| Authority and atomic storage | Independent read/edit denial/expiry, ancestry expiry, quota/rollback, abort/session and completion-boundary identity cases |
| Proof custody and shared compatibility | Three isolated source-change CLI canaries;92 Save/61 history regressions and all contract/scaffold checks |

Initial sandbox loopback failures are retained as infrastructure failures, distinct
from the later actual missing-behavior RED. Review RED retained the pre-fix source
capsule; custody canaries mutate only isolated selected-source copies. No shared
worktree source or historical evidence was modified by a canary.
