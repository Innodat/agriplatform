---
title: 'Specify preparation worker results and durable attempt evidence'
type: 'chore'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
baseline_commit: '8c54fc17d36ba89e182a35c852d4e17ffaaf3806'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The request parser exists, but the future worker cannot yet produce a closed request-bound result or retain precisely typed recovery evidence at the correct crash boundaries. Local journal capture must not be mistaken for a committed database audit.

**Approach:** Specify app-owned version1 result/record shapes, canonical digests, named row/session snapshots, finite phase transitions, local durable capture/retention rules and honest crash/reconciliation semantics. The next consuming slice is a pure codec; no storage writer, executor, supervisor, SQL/schema/migration, Identity/Access or live preparation implementation here. Preserve existing request/custody contracts, owner boundaries, UX and standalone signup.

</frozen-after-approval>

## Implementation Notes

- BMAD investigation: no intent gaps/irreversibles for documentation only; three delivery files: new `apps/scribeswell/docs/CORPUS_PREPARATION_EVIDENCE.md`, link/alignment in tool doc, this record. Canonical derivation adopts the app contract without duplicating its schema. Preserve all concurrent dirty work.
- Code map: parser9fields/immutable custody/error in `backend/caller_preparation_input.py`; actual11principal/9authority columns and server timestamp triggers in immutable0003; test-only mapping/reconciliation helper; existing supervisor private bounded transport precedent. Do not edit any implementations, applied revisions, existing validators or owner APIs.
- Required two checkpoints: locked before-state plus semantic intended values before first mapping write, then exact server-produced rows after postchecks before COMMIT. Operational journal and DB commit are not atomic business audit; ADR0022/0025 audit qualification remains an explicit execution gate, not a claimed capability or authority to alter schema.
- Close result variant types, stream caps, request/target/record digest binding, phase/row types and missing/corrupt/commit-loss/no-op handling. Hashes detect identity/integrity under retained trusted custody; they never establish owner admission alone.
- Verification is source alignment, closed-field/row count inspection, scoped links/anchors/whitespace, canonical IDs/companions and protected-source preservation. Acceptance matrix lists future codec/storage/executor tests; no new runtime tests or actual storage/crash proof claimed.
- Impacts: app docs only; no scaffold/shared UI/agent context or accepted ADR change. No production pattern proven for promotion. Separate Access/KDG/Leave/factory ownership and existing readiness gates remain.

## Review Triage Log

- R1 medium/patch: six-field session omitted retained ledger/isolation/writability/authority inventory required by authoritative tool policy. Add literal head/isolation/false-readonly plus bounded authority-observation reference bound to exact session/run; inventory captured outside locks, actual checks current before effects. No owner API fabricated.
- R2 medium/patch: admitted-only/failed-intent prefixes lack session/before-state. Explicitly recover independently retained actual observations via trusted session-authorization custody; trusted never-connected proof can establish no effect. Otherwise unknown, no row comparison/new preparation or inference from empty state; not every early crash resolves from journal alone.
- R3 medium/patch: terminal outcome/code lost rollback-proof distinction. Add exact tagged proof kind/reference (commit_ack, rollback_ack, ended_no_effects, pre_write, unconfirmed/null), with outcome compatibility and trusted retained observation requirement. Reply remains unchanged eight-field reference to terminal record.
- R4 medium/patch: canonical size wording did not explicitly cap raw record bytes. Require exactly bytes, predecode32768raw-byte cap and byte-for-byte canonical re-encoding; no whitespace/key-order/alternate-escape normalization during record decode. Complete record hashing includes previous/binding digests, own digest external.
- R5 medium/patch: create timestamp phrase ambiguous within/across rows. Require one identical transaction_timestamp() across all eight principal/authority attribution timestamps; future negative case includes individually equal rows with cross-row differences.
- All five individually source-verified and patched, none deferred. Review scope24744bytes SHA256a600847a2daed21aab38a6692ead26f700ed0431d69a4ebcf4033c7c745c59df. Source/document checks only; no runtime/physical storage/crash tests run.
- Final checks: actual immutable0003 principal11/authority9 field names match document exactly; eight reply fields; scoped/canonical links/anchors/whitespace; canonical11CAP/38ST/22distinct existing companions; captured Scribeswell/Identity/AGENTS bytes unchanged except intended tool-doc alignment. All five review findings resolved/no deferrals. No pytest, database/native/container/image/provider/storage/crash or live permission operation run; prior207/394 parser evidence remains historical, not proof of proposed codecs/storage.
