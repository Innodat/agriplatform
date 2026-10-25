# Native stored-edit recovery qualification — 2026-10-25

`migrations/tests/qualify_edit_recovery_http.py --qualify-retained` qualifies stored-edit
recovery through the unchanged candidate HTTP factory. It reuses exact retained run
`99b7231c-0a5b-4bdb-98e8-3329564c526a`, custody and already-applied revision0002.
It supplies synthetic Access responses through MockTransport and candidate requests
through ASGITransport. No TCP listener or real Access is involved.

The append-only start receipt journals fresh organization/account/actor, questionnaire,
version, child, assignment, question, eligibility, capture, operation and fixture-outcome
identities before any writes. The existing seed helper now accepts an optional assignment
identity; its historical callers retain their existing behavior. The actual runtime
create handler commits revision1. Two explicitly test-only fixture transactions update
only that fresh capture under `kdg_capture_runtime`, using existing bounded transaction,
scoped outcome append, history SQL and native integrity. This does **not** implement or
qualify an edit API or its domain authorization.

An independent revision1 read now captures creation attribution before either edit.
Both transitions preserve that baseline and observe changed server update timestamps;
this is a bounded fixture observation, not a platform monotonic-clock rule. The oracle
checks journaled edit outcome IDs, original eligibility reference and membership too.
After every writer closes, new physical restricted read-only connections independently
verify the capture, each immutable snapshot, exact operation/outcome links, original
owner/version/child/device facts, editor attribution and original compact receipt.
Revision2 and revision3 HTTP passes each prove (the latter also recovers edit3 exactly):

- Original edit returns its own operation, capture and revision`"2"`.
- Original create still returns revision`"1"`.
- Wrong discriminator, foreign account and separately configured foreign organization
  return exact scoped unresolved DTOs.
- Current own-read denial returns safe403 before checkout; every response releases its
  lease, reused contexts are clear and lifespan disposal closes physical connections.

The revision3 oracle also compares exact hashes of all earlier history/outcome rows
and the original capture creation time. Preservation hashes cover complete prior rows
in the eight known business tables, avoiding a count-only preservation claim. The first dataset
changed capture10→11, outcome10→13, history10→13 and parent tables2→3. The reviewed
source run added a separate dataset, changing capture11→12, outcome13→16, history13→16
and parent tables3→4, exactly as planned per attempt. Both datasets remain retained. Original rows, foreign sentinel and ordinary ledger
revision0002 remained unchanged. No schema/ledger inventory, migration, privilege
expansion, preparer or cleanup ran. Historical metadata discrepancy remains unresolved.

The first native attempt passed; review then strengthened the proof without changing
the application reader. The reviewed-source native run also passed. Retained first receipts:

- Intent: `capture-commit-edit-recovery-start-2bb80f0685244de6be195b662f3a5453.json`
- Qualification: `capture-commit-edit-recovery-http-2ce811ff762c469aad5b9bb2443a1b55.json`
- SELECT-only HTTP pre-check: `capture-commit-recovery-http-ba2ab46381334086b789af6f6d4ea5d5.json`
- SELECT-only HTTP post-check: `capture-commit-recovery-http-5d0504144d6249b3b6a1a8c6be6425b0.json`

Source digests are captured before candidate/custody imports and checked before writes
and after all verification. Failed attempts retain intended identities, completed
evidence, a safe failure stage and exception class, never a qualified success or native
exception payload. Receipt-storage failure also exits safely; unavailable receipt
storage cannot guarantee a durable failure receipt. Synthetic focused tests cover
identity journaling/order, restricted target guards, exact deltas/prior-row preservation,
original-evidence stability, source drift and safe failure output. ATDD observed the
missing-module RED before implementation. Exact commands, results and source/receipt
hashes are recorded in the [source-bound record](evidence/native-edit-recovery-20261025.json).

Scaffold/shared UI/agent-context/ADR impact: none; existing shared primitives remain
unchanged and three scaffold parity checks pass. Documentation is updated here and in
contracts/next-session. TypeScript7.0.2 and concurrent work remain preserved.
Fingerprints/HMAC remain deferred. Real authorization, edit writer/domain validation,
TCP drain/native cancellation uncertainty, active startup/browser/queue/editor adoption,
ADR-0020 compatibility/recovery/activation, production and pilot gates remain open.

Final reviewed-source report: `capture-commit-edit-recovery-http-d58241785ea94f8b9f040771e1acd635.json`;
intent `capture-commit-edit-recovery-start-3a9ea0e99b1142c282e2d725369e0bd6.json`;
final SELECT-only report `capture-commit-recovery-http-03a0e31a22dc43cba25ba9bc8342f4aa.json`.
The exact run stopped normally; its database volume and network remain retained.
Final verification: **18 focused tests,176 affected tests, three scaffold parity checks**.
All ten review findings were individually triaged: nine patched, one rejected because
pending review/stop fields correctly described the intermediate record; nothing deferred.
Controlled rows reject fourteen storage corruptions, including mutually linked but
unjournaled outcome IDs. Source-read/import bootstrap failures return safe diagnostics
and a best-effort receipt when custody is available. First and reviewed source capsules,
review diff and full regression logs are retained under the receipt's source_capsules path.
