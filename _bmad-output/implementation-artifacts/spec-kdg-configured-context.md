---
title: KDG configured current-context API boundary
type: feature
created: 2026-10-22
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Make the existing read-only KDG context consumer constructible from explicit
server-owned startup configuration, then qualify its actual current Access owner
integration against retained synthetic state. Require exact organization, HTTPS Access
origin and restricted service key; missing/invalid policy fails safely without
configuration or credential dumps. No default organization, selector, embedded shared
server, cached authority, migration or grant is introduced. The unconfigured default
app keeps its existing refusal semantics.

Given explicit valid server policy and current exact authority, when the configured
context API is called, then return validated current own-account context; missing or
invalid policy refuses. Given retained positive/denied/unmapped synthetic accounts,
when KDG calls the actual current Access HTTP owner backed by restricted PostgreSQL,
then expose the corresponding200/403/409 safe outcomes with no-store. Verify original
retained business/catalog state before and after. Start/resume only the existing
synthetic local stack and bounded test servers; retain all historical resources/data.

Use behavioral ATDD and focused TDD. No browser sign-in, whole-story completion,
business persistence, Leave/editor, production, real accounts/access, provisioning,
deployment/pilot, reset/prune/cleanup or fingerprints/HMAC. Preserve concurrent edits
and published dependency/lock baseline including TypeScript7.0.2. Synthetic provider
identity is a test seam, not Entra qualification.
</frozen-after-approval>

## Implementation Notes

- bmad-help selects [BD] Build for the next Story1.1 API prerequisite. Small bounded
  startup adapter plus consuming tests/evidence; no unresolved user-facing choice or
  irreversible action. Existing concurrent dirty work remains authorized and excluded.
- Reuse api/main.py create_app and closed DTO/errors; leave those tested sources
  unchanged unless a demonstrated defect requires correction. New api/runtime.py
  adapts explicit KDG_ORG_ID/KDG_ACCESS_URL/KDG_SERVICE_KEY into that factory.
- Native fixture authority is services/access/ORGANIZATION_CHECK_EVIDENCE.md final
  closure: organization-check-reviewed3-20261022, retained receipt2c341e184cc151eaa017a9c46e96028959165c867e02eed5528cfb43f1f2f48b.
  Earlier final/attempt frames remain historical. Existing owner --verify-retained
  checks both owners/state in read-only transactions. No --all or preparer will run.
- Existing Access owner fixture loader/auxiliary runtime role and current HTTP factory
  stay Access-owned. App tests communicate by HTTP and do not import Access server.
  New owner-local test server support is synthetic-only; no production server change.
- Backend setup policy is internal configuration, never caller supplied. TLS fixture
  trust is confined to the qualification transport; no verify=False/default bypass.
- Actual commands and source/results custody will be recorded in owner evidence;
  root/owner baseline locks and all historical evidence remain unchanged.
- Behavioral ATDD observed503 instead of200 before the adapter; eight policy tests
  then failed before implementation. Adapter GREEN8; ambient snapshot test plus70
  existing API and60 Access tests passed139 in3.04s.
- Existing guarded up first refused a relative CLI path; the corrected absolute pinned
  path resumed the same retained run. Read-only owner inspection passed before use.
- Two native attempts reached all six live HTTP cases but Access's TLS connection
  drain exceeded12s, requiring recorded-9 forced termination. Safe diagnostic shows
  Uvicorn waiting for connections, not busy SQL; underlying behavior is not fixed.
  Both exact executed-source capsules match original hashes and remain retained.
- A test-only3s graceful-shutdown bound records the idle-TLS timeout warning and permits
  bounded process exit0. Candidate seven-case native proof/state inspections pass;
  do not describe that as fully graceful deployed draining or release readiness.
- Configured oneshot review runs only Blind Hunter; other lenses are not configured.
  All seven findings are triaged below. Supervisor probe exits143 with fixed failure
  identifier, both child exits0 and independent retained-after inspection passed.

## Review Triage Log

| Finding | Verdict, evidence and disposition |
| --- | --- |
| safe_errors omitted from executed-source capsule | medium verification gap; source list omitted imported application adapter; added exact capsule/hash/current comparison; patched |
| Failed attempts skip independent after-inspection | medium verification gap; after call was success-only; moved to finally after bounded child teardown and persists outcome even on failure/interruption; patched |
| Failed receipt lacks check/stage identifier | medium diagnostic gap; results only had passed:false; fixed local-check identifiers and stage now retained, arbitrary exception content reduced to type; patched |
| SIGTERM runner can orphan child test servers | medium harness defect; no handler was installed; SIGTERM/SIGINT raise controlled interruption through finally, preserve signal/teardown/state evidence; actual interruption probe verified; patched |
| Leakage checks cover only one bearer | medium verification gap; only positive token checked; all supplied synthetic tokens checked across every response and server logs; patched |
| Missing actual interpreter/package/TLS provenance | medium evidence gap given observed TLS drain; exact executable/version/hash, relevant installed versions, OpenSSL and owner/app lock digests retained; patched |
| Advertised ASGI factory lacks direct command/smoke proof | medium consumption gap; prior tests imported factory programmatically; added explicit local Uvicorn --app-dir/--factory command and fresh-process401/automatic-exit smoke; patched |

No new product/runtime feature deferred by review. Browser/provider/device and deployed
Access drain/pool/release behavior remain explicit unqualified gates; the observed TLS
warning and earlier forced attempts remain evidence, never claimed repaired.

- Final reviewed native3502e9ca55d24b1997df5414cb2b13a7 passes eight HTTP/CLI checks,
  four restricted reads and both independent retained inspections; all three server
  processes exit0. TLS drain warning remains explicit. Interruption c52dac4237b5406ba8623f0cd49268bd
  correctly exits143 with failed/interrupted receipt, both child exits0 and after
  inspection passed. Final79 KDG/139 affected, OpenAPI and TS7 checks pass. Native
  stack stopped normally after verification; all resources/data and prior evidence stay.
