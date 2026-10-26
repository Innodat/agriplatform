# Local explicit edit Save — 2026-10-26

This candidate consumes verified own-edit context for server-backed original-owner
captures. It keeps the server baseline separate from an explicitly saved local overlay
and immutable action snapshots. Unfinished typing stays with the caller; no UI or
synchronization worker is activated.

Each Save pins the original questionnaire and actually reviewed base. A distinct
caller-supplied action ID identifies completed changes; identical retry can recover the
same local outcome, while contradictory reuse refuses. Later saves retain their
predecessor and do not guess the server revision it will produce. Stale forms and
unrelated remote changes preserve a separate attention-needed proposal without
replacing newer saved work. No result is a server receipt or a Synced claim.

The isolated IndexedDB upgrade preserves existing history and opaque pending/conflict
fields. Completed changes and intent share one transaction. Failure before commit
rolls back both; a session change at completion suppresses success publication even
when original-account work may already have committed. It makes no rollback promise
after transaction completion. Existing namespace, clock and session protections apply.

Read and edit authority remain independent. Current read evidence cannot renew edit
authority, restore known-denied edit evidence or silently upgrade an already reviewed
base. Known authority states must remain distinct from transient storage failures.
Retained actions/proposals are read through a scoped bounded local interface.

Scaffold impact: reuse the already generated and behaviorally tested IDB request/
transaction primitives and Auth execution fences. Original-definition validation,
edit authority, record bases, predecessors and proposal policy belong to KDG. No
neutral scaffold defect has been demonstrated by this delivery. Shared UI and agent
context impacts: none. Documentation appends current contracts and prepends the
handoff, retaining historical evidence. ADR impact: inherit existing accepted decisions;
no accepted ADR is edited.

Synthetic local/CI only. This proof does not establish physical-device persistence,
eviction resistance, at-rest security or actual PostgreSQL permissions/rollback. It
does not implement the remaining Story2.2 pending-create consumer, queue delivery,
reconciliation, conflict-resolution UI or accessible editor. No UI/editor/Leave,
service-worker/browser/default-startup activation, real accounts/Auth/Access,
PostgreSQL/native-driver/Docker qualification, provisioning/migrations,
deployment/production/pilot or cleanup is included. Dependencies remain unchanged,
including TypeScript7.0.2; fingerprints/HMAC remain deferred.

The first proof observed missing-context-import RED and characterized all61 history
checks before refactoring. Independent review exposed incomplete local retrieval,
capability-denial and typed-outcome planning. The non-frozen plan was corrected once;
the four owned implementation files were preserved as exact KEEP snapshots before
re-derivation. Frozen intent, prior evidence and unrelated changes were preserved.
Subsequent targeted RED checked the concrete review failures against those retained
sources. This is implementation correction within the same approved scope.

The schema upgrade proof qualifies existing v1 data preservation in isolated Chromium.
It does not qualify coexistence of released old/new application bundles or live upgrade
activation. That release work remains excluded. Intents have explicit type/version;
future senders must preserve supported pending/attention work and original identities.

The candidate store exposes:

| Operation | Contract |
|---|---|
| `importEditContext(value, pinned, execution)` | Clone and validate exact current observations and original record; explicit `restoreDenied: true` requires newly verified evidence after known denial. |
| `openEdit(capture_id, execution)` | Return a frozen handle-issued reviewed token. Newly opened unsaved records use latest baseline; existing saved overlays retain their reviewed base. |
| `saveEdit(reviewed, action_id, input, execution)` | Validate complete original-version date/answers and supported PUT size/characters; atomically retain immutable action plus eligible overlay. |
| `readEditActions({limit, after}, execution)` | Own-read-protected immutable actions/proposals, default30/max100, namespace key continuation. Valid own-read can retrieve proposals after edit denial. |
| `denyEdit(pinned, execution)` | Persist independent edit denial and invalidate old reviewed tokens while preserving current read access. |

`saveEdit` returns `saved_locally` or `needs_attention` only after local commit and
publication checks. `invalid` rejects unsupported input; `action_id_reused` rejects
changed content under an existing ID. `expired` and `denied` identify known authority
states; `unavailable` covers storage, clock, cancellation or invalidated execution.
After a completion-boundary failure, retain the original action ID and input. Work may
already be committed; inspect retained actions after valid own-read recovery or retry
the identical action under its original identity when the required authority is valid.
Never infer rollback, replace the action ID or claim Synced from a failed publication.
Reviewed tokens belong to their store handle; reopening obtains a fresh token for new
work. Identical existing-action replay is separately supported across handles.

Run the exact commands in [the machine record](evidence/local-edit-save-20261026.json)
from the repository root. The primary command is the approved Node26.11.1 executable
with `apps/kdg-capture/web/tests/local-edit-save-proof.mjs`; the history regression is
`apps/kdg-capture/web/tests/history-store-proof.mjs`. Both proofs assert TypeScript7.0.2
and use explicit selected-source capsules. They require the retained approved npm
capsule `platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules`,
Playwright from `platform/deployment/.local/scaffold-application/proof-dI2Gy9/root`,
and Chromium under `platform/deployment/.local/web-baseline-qualification/browsers/`.
These retained prerequisites are not supplied by a clean checkout alone. This delivery
installs no dependency and changes no baseline or package version; CI qualification
needs the same approved prerequisites supplied by its existing toolchain owner.

Final source-bound verification passes all29 affected jobs: 92 local Save checks,
61 history checks, 575 compiled client tests,127 direct tests,
four fixture guards and 16 loopback groups. Six strict adapter configurations,
twelve schema/client freshness checks and five scaffold parities pass. The prior313-test
backend proof is reused with all77 backend source hashes unchanged; no rerun is claimed.
Review resolved23 of25 findings across two review passes and one plan correction;
two findings were rejected with evidence and no new work was deferred. Existing native,
physical-device and remaining Story2.2 scope are still explicitly unqualified.

| Requirement | Executed proof |
|---|---|
| Exact context, immutable base and original questionnaire | Initial local cases: verified_context_commits, exact_independent_evidence, offline_immutable_reviewed_original |
| Whole-form explicit Save, false/1 and hidden details | Original rating/required/false and hidden-detail cases; invalid_wire_character and max_revision_wire_limit boundary refinements |
| Atomic overlay/action, failure and replay | Atomic baseline/attribution, quota/overlay rollback, same-ID exact/contradictory replay, completion session/expiry checks |
| Predecessors and stale proposals | Sequential predecessor/null revision, stale form, remote baseline and pending/conflict blockers; cross-realm stale save |
| Independent authority, denial and recovery | Independent original-token read/edit expiry after context refresh, late lookup expiry, read restoration, failed denial latch, cross-realm generation repair |
| Retained proposal access and isolation | Bounded actions reopen, three populated account/org partitions, read expiry/denial and edit-only-denial cases |
| Reopen/upgrade and caller snapshots | v1 pending preservation, immediate input/context mutation, actual page reload recovering overlay/proposals without old tokens |
| Existing shared behavior | All61 history checks, compiled clients, strict TS7.0.2, loopback, six contract owners and five scaffold parities |
