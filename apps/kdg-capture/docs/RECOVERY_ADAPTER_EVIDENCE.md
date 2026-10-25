# Candidate recovery request adapter — 2026-10-25

`web/src/recovery.ts:recoverOperation` consumes the generated recovery request/receipt/
error types. It remains unimported by active startup. It performs one fixed relative
GET with one command discriminator and current bearer, same-origin credentials/mode,
no-store cache policy and redirect refusal. No account/org selectors or body are sent.
Input account must match the pinned session; organization and original operation UUID
are canonical nonnil IDs. Edit acknowledgement also binds the queued capture target.
Create recovery preserves the first committed target, which may differ from a later
changed request under ADR-0061. Revision strings remain exact through signed-bigint max.

The required caller-owned `{signal,isCurrent}` lease represents the existing owner's
session/organization generation and pinned account/org. It is not a second Auth lifecycle,
offline grant or server authorization observation. Future integration must abort on
logout, account/org/session replacement and disposal, and make the predicate false for
superseded execution, including A→B→A. Predicate exceptions fail closed. The adapter
checks the lease before transport and before returning; actual Auth integration and
publication fencing remain later consuming work. Server authorization is fresh per call.

The total deadline is at most10 seconds across response headers and body, with16KiB
maximum decoded bytes and fatal UTF-8. Native JSON.parse owns grammar; a bounded lexical
object-key scan refuses duplicate keys, including escaped-equivalent names. Exact DTO
shapes refuse unknown fields, malformed IDs/versions/revisions, nonfinite numbers,
NUL/unpaired Unicode and wrong operation/command/edited target. Responses must be JSON
and private/no-store. Ordinary request/body cancellation is best effort; a transport
ignoring abort cannot keep the returned promise pending indefinitely, and late bodies
are discarded without consuming or publishing them.

The result contains a frozen compact committed receipt, frozen verified unresolved,
a safe declared status/error identifier, or a local fixed failure kind. No upstream
message/exception text is returned or logged. Denial, network failure, malformed data
and deadline never become unresolved. No retry, token refresh, write, new operation ID,
queue/store change or Synced mutation follows from this adapter. Unresolved is not proof
of rollback and cannot authorize descendants or a fresh operation.

Scaffold impact: existing generated contracts and entry transport conventions reused;
no new shared transport/lifecycle or generic SDK. KDG receipt/target binding stays in
its silo. Existing entry/Auth source and generated artifacts remain unchanged. Shared
UI, agent context and ADR impact: none. Contracts, handoff and evidence updated here.
No native fixture/HTTP server, actual Auth/Access, browser/editor wiring or release
activation is qualified. Dependencies and TypeScript7.0.2 preserved; fingerprints/HMAC
deferred. No Leave/editor, real-account/access, production, provisioning, deployment,
pilot or cleanup work; Docker stays stopped with retained resources/data intact.


| Requirement | Synthetic acceptance evidence in recovery.test.mjs |
| --- | --- |
| Original identity/target and immutable receipt | Single fixed request, create/edit binding and mutation-after-start cases |
| Verified absence distinct from failure | Valid unresolved and create/edit malformed unresolved cases |
| Exact DTO/error contract | Unknown/version/revision/target tests; all declared error pairs cross-checked with exported schema |
| Current execution fence | Header/body cancellation, stale/throwing predicate, replacement generation and disposal cases |
| Bounded body/deadline | Noncooperating headers/body, controlled empty microtask chunks, exact16384/16385 byte and split UTF-8 cases |
| Safe parsing and cleanup | Duplicate/escaped keys, Unicode/nonfinite refusal, rejected/late/overflow body cancellation and safe network errors |

ATDD observed29 failures against the explicit adapter stub. Focused TDD caught network
classification and cleanup errors before their fixes. Final **39 recovery tests** and
**29 existing entry tests** pass together (**68 cases**). TypeScript7.0.2 passes the new
adapter fixture, existing entry fixture and generated recovery contract fixture, with
5 new negative typing cases plus12 existing contract negative cases. Three scaffold
code/test parity checks pass. Blind review raised5 findings, all fixed; the deadline
finding was reproduced before the monotonic read-loop correction. See individual triage
in the [delivery record](../../../_bmad-output/implementation-artifacts/spec-kdg-recovery-adapter.md).

The previous contract source capsule still matches current files; existing backend,
Auth, entry and generated sources were not changed. Backend/native suites were therefore
not rerun and no new native claim follows. The synthetic freshness predicate proves the
adapter's fence behavior, not actual Auth event integration. Next consuming work must
bind it to KDG's existing Auth/entry observations and abort lifecycle, without inventing
a second lifecycle or activating editor/API behavior.

Exact commands and source hashes are in the
[source-bound receipt](evidence/recovery-adapter-20261025.json).
