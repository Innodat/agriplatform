# Native recovery HTTP qualification — 2026-10-25

`migrations/tests/qualify_recovery_http.py --qualify-retained` consumes exact retained
fixture custody, applied0002 provenance and existing synthetic create identifiers. It
constructs the unchanged candidate HTTP factory and its actual SQLAlchemy QueuePool /
psycopg runtime connections. Access is MockTransport; request transport is in-process
ASGITransport with explicit normal lifespan exit. No real HTTP listener is started.

| Native group | Evidence |
| --- | --- |
| Original committed receipt and release | Exact stored operation/target/revision DTO; zero outstanding request leases |
| Unknown operation / required discriminator | Exact scoped unresolved DTOs |
| Foreign account / configured foreign organization | Isolation through real runtime RLS, no caller-selected tenant override |
| Cleared reused context | Every checkout probes org/account/actor/mode all unset/empty |
| Strict HTTP selectors | Duplicate/unknown query422 before Access or checkout |
| Current own-read denial |403 before request checkout |
| Pool saturation and reuse | Five actual held connections; safe bounded503; successful recovery after release |
| SQL error rollback and reuse | SELECT-only division-by-zero fault after checkout; safe503, no unresolved/receipt; zero leases and successful subsequent read |
| Exclusive overlap | Two simultaneous runtime connections with distinct PostgreSQL backends |
| Lifespan disposal | All six observed physical connections across both candidates closed after lifespan exit |

Every checkout verifies actual `kdg_capture_runtime` login and read-only transaction
state. Existing restricted-role checks separately verify nonprivileged identities.
Explicit read-only pool warm-up precedes deterministic receipt tests; it does not renew
or weaken per-request authorization freshness. SQL fault injection uses a test-only
SQLAlchemy event; the production candidate remains unchanged. Pool timeout is ordinary
QueuePool behavior, not a replacement lock or custom retry system.

Before and after, ordinary ledger revision0002, counts capture10/outcome10/history10 and
foreign sentinel remain unchanged. No migration, DML, seed, preparer, schema/role creation,
custom schema/cluster inventory or cleanup runs. Both append-only native reports remain:
initial11-group checkpoint `capture-commit-recovery-http-296f960eb02e4d94992de0f4421f4336.json`
and final12-group report `capture-commit-recovery-http-7f67806acf134f63b40ad4ad01ae69f2.json`.
The known Docker run was resumed and stopped normally; data/resources remain retained.
Historical metadata discrepancy is still unresolved and no inventory-pass claim follows.

Qualification snapshots owning/candidate/custody source digests before imports, then
rejects any change before or after execution. Failure receipts contain initial source
identity, safe stage and exception class only. Seven focused evidence tests ensure
mismatched responses, preservation/source drift and native failure cannot issue a success
receipt; CLI failure output excludes an injected credential canary. ATDD observed stub
failures before implementation. Final affected suite **148PASS**; three scaffold code/test
parity checks pass. Blind review raised five findings, all fixed with individual triage
in the [delivery record](../../../_bmad-output/implementation-artifacts/spec-kdg-native-recovery-http.md).

This proves candidate ASGI adaptation with native SQL/pool behavior and normal lifespan
disposal. It does not prove a TCP server's drain, native cancellation/commit uncertainty,
real bearer/Access, a native committed-edit receipt, browser integration, schema/client
adoption, active startup or release readiness. The candidate has no exported active app;
existing API dependency ownership and ADR-0020 compatibility/recovery/activation gates
remain. No runtime handler fix or approved dependency change was needed.

Scaffold/shared UI/agent-context/ADR impact: existing generated primitives reused and
parity-checked; no new reusable runtime behavior, UI or decision. Documentation and source
receipts updated here. Original candidate/recovery native source capsules and historical
evidence remain intact. TypeScript7.0.2 preserved; fingerprints/HMAC deferred. No
Leave/editor, production, real-account/access, provisioning, deployment, pilot or cleanup.

Exact commands, source hashes and retained report references are in the
[source-bound receipt](evidence/native-recovery-http-20261025.json).
