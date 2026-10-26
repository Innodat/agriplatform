---
title: 'Audit the exact closed corpus attempt'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Implement the bounded protected auditor needed before durable manifest staging. Given a caller-owned restricted connection, the original corpus.seal operation, approved full source bytes and a stable owner-chosen revision UUID, requalify the source, reconcile its closed receipt under existing current authority, then observe the enforced closed epoch/attempt, principal/authority and complete actual corpus in one read-only repeatable snapshot. Return a bound immutable manifest candidate only after complete comparison and successful snapshot exit. Recovered/stale/wrong identity, disabled fencing/authority, malformed or incomplete corpus and errors must fail safely without returning partial proof.

No business coordination locks span the full scan; reuse the existing full audit, manifest assembler and controller lookup. No connection creation, credentials, new operator framework, migration/grant changes or source writes. Existing historical audit remains historical. The result is unpublished and is not a durable sealed attestation or activation permission. Actual native role/fence/DDL/transport qualification remains final-phase; no KDG ports or owner-service implementation. Preserve unrelated changes and all earlier unresolved test evidence.

</frozen-after-approval>

## Implementation Notes

- Small app-owned adapter plus focused tests and existing contract addendum; no product intent gap or irreversible action. Same source labels come from strict seal command. Existing corpus_publication._idle/lookup_outcome enforce caller shape and lookup authority. corpus_database_audit._verify_visibility/_compare reuse exact inventory, token/digest and ordered ID checks; corpus_manifest owns immutable result assembly.
- The source owner trusts the controlled auditor runtime to establish actual correspondence; SQL shape/candidate acceptance alone will never be called a sealed audit. Subsequent staging requires its own protected immutable completion boundary and final current-authority/closed-attempt CAS. This slice implements audit observation only, leaving durable staging/activation proposed.
- The adapter has a60s executing deadline with existing finite per-statement/lock/idle bounds; caller execution containment must bound network/transport stalls. It does not introduce a hard wall-clock supervisor. Closed epoch excludes supported writers while enforcement is enabled; recovery may race the snapshot, so later activation must recheck the exact tuple. Controlled schema/role DDL stability is required.
- Runtime uses explicitly prepared SELECT visibility of owned control/epoch/attempt/principal/authority and corpus plus existing lookup EXECUTE; shipped operator still has none of these new read grants. Missing preparation fails closed. No automatic provisioning or activation.
- Scaffold/shared UI/agent context/ADR: app-specific adapter, no promotion or decision change. Update adopted highlight evidence contract and canonical derived status through bmad-spec. No migration or generated reference edits.

- ATDD chronology retained: first test double lacked module hook imports (27setup failures1pass), corrected unavailable stub produced14genuine failures14pass2.72s. Implementation28pass1.92s; expanded deadline/read denial32pass16.92s. Independent review6individual findings addressed; actual controller lookup exposed2genuine dict/custom-factory failures1.92s. Corrected35pass1.87s, then lookup-failure restoration36pass2.38s.
- Final exact command is retained in apps/scribeswell/docs/evidence/closed-corpus-audit/verification.json: temporary Python3.12 pytest over closed auditor, fenced importer, legacy importer, manifest, highlight, command-input and source-evidence suites.335pass18.56s exit0; runner20.29s,21relevant source/test/fixture before-after hashes unchanged and current hashes match. Initial runner wrong oshb_morph dependency path stopped before tests; empty output directory removed, path corrected, no test failure hidden. No frontend build needed for Python-only changes.
- No native SQL/role/owner-service/device/transport/release check ran. Previous API-reader missing-dependency/stall and anonymous mobile-scroll failure remain unresolved; these pure/application-side passes do not qualify them. Existing controller/audit/migration behavior unchanged. No new cleanup, role provisioning, source publication or KDGport use.

## Review Triage Log

- Medium / patch: tuple-indexing receipt decoder broke caller dict/custom factories before audit; actual lookup adapter tests reproduced two reds, normalize tuple for reconciliation/dict for snapshot and restore caller factory across both failure paths.
- Medium / patch: proposed stage/batch/completion writes lacked durable retry semantics; explicit command/version/semantic operation UUIDs, revision/batch keys, same-input replay, conflict and original lookup now defined. Implementation remains proposed.
- Medium / patch: proposed revision identity could rebind distinct evidence; globally unique immutable revision-to-source/attempt/manifest rule now explicit. No new runtime DDL claimed.
- Medium / patch: proposed digest omitted auditor contract version; canonical encoding now includes it and completion/activation verify its immutable binding. Encoding still unimplemented.
- Low / patch: negative corpus tests accepted any failure code; exact corpus_mismatch versus unavailable assertions now establish error classification.
- Low / patch: lookup deadline phase lacked proof; delayed valid receipt beyond budget rejects before opening snapshot and restores original caller factory.

Configured oneshot blind layer only; fresh context-free same-capability reviewer returned all six findings before triage. No other review layer configured. All review findings addressed within existing intent; no new defer.
