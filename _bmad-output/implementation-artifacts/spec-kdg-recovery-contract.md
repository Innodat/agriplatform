---
title: Candidate recovery OpenAPI and generated client contract
type: feature
created: 2026-10-25
status: done
route: oneshot
baseline_commit: c4fd2ef578c986c138d8613f27c1379ab54077c1
---

<frozen-after-approval>
## Intent
Expose the existing candidate recovery endpoint's precise OpenAPI contract and generate its separate TypeScript client types using approved local tooling. Document required closed command query, canonical operation UUID, Bearer authorization, committed/unresolved output and safe status-specific errors. Qualify DTO/schema/wire parity, deterministic no-network/no-database export and generated positive/negative TypeScript7.0.2 cases. Preserve runtime validation order, current access/transaction semantics and active context API. No browser/editor integration, active startup/API activation, dependency changes, migration/data/native fixture work, real accounts/Access, deployment, provisioning, pilot, cleanup or fingerprints/HMAC.
</frozen-after-approval>

## Implementation Notes
- bmad-help [BD] Build selected from native qualification handoff. Small metadata/export/type boundary, no intent gaps or irreversible work; oneshot route. Authorized dirty-tree snapshot /tmp/kdg-recovery-contract-before.json.
- Existing generator intentionally emits types only, not SDK/network runtime. Separate contracts/recovery-generated output preserves active contracts/generated.
- Candidate custom OpenAPI metadata derives from existing DTOs and validators, including required serialized unresolved status and signed-bigint revision bounds. Manual route input validation stays unchanged; no automatic FastAPI query/path behavior is introduced.
- Existing deterministic exporter pattern reused with explicit candidate-only synthetic configuration and no checkout/network calls. Active context export untouched.
- Scaffold: existing platform types generator/ownership installer reused; no new generic mechanism. Shared UI/agent context/ADR: none. Docs/evidence/handoff updated in same delivery. Historical native receipts remain source-bound to their original candidate version; metadata-only source update gets separate evidence, no historical proof rewrite.

- Existing24 HTTP characterization tests passed before route-registration factoring. ATDD then observed5 new contract failures (2 assertions/3 errors) before metadata/export implementation.
- Schema-only registration uses no authority or engine; runtime factory keeps the same manual validation, current Access and transaction callback. Metadata adds required serialized status, safe per-status error enums, canonical UUIDs and signed-bigint decimal bounds without changing runtime DTO validation.
- Direct generator refused api_client_tool_invalid because its dependencies are absent. Existing retained G sources and installer byte-match current files; G generated and check-verified candidate types without install/download or retained-source mutation. Root TypeScript remains7.0.2; generator compiler6.0.3 remains tool-only.
- Review schema validation uses existing /usr/bin/python3 plus jsonschema4.10.3; no application dependency/package installation. Candidate and active TS fixtures pass,12 @ts-expect-error cases checked. Candidate export/types freshness and active context export checks pass; scaffold3 parity checks pass.
- Final158 affected tests include10 new contract cases. A multi-request contract test initially tripped the reused fixture's zero-prior-checkout assertion; gave each outcome a fresh synthetic pool and kept expected200/schema checks unchanged. No production bug or assertion weakening.
- Future native qualifier source list now includes the imported metadata owner. No native rerun or receipt rewrite; previous native capsules bind their original source versions. Docker remained stopped and dependencies/data unchanged.

## Review Triage Log
- medium / patch: copied UUID pattern lacked beginning anchor and strict end. Added anchored exact36-character schema with portable strict-end assertion; JSON Schema validator rejects prefix/suffix/uppercase/nil/newline cases.
- medium / patch: dollar end could match before trailing newline in revision schema; fullmatch tests masked search semantics. Added strict end and actual JSON Schema tests including1\n and max+1.
- medium / patch: success metadata lacked wire/schema relationship. Validate actual create/edit receipts at signed-bigint max and unresolved against exported union using Draft202012Validator.
- medium / patch: only403 error schema tested. Every declared HandlerError pair now goes through ASGI and validates its actual status/body/headers against the corresponding exported schema.
- medium / patch: no-I/O guards began after import. Added fresh isolated child process installing engine/http/socket sentinels before exporter/candidate import and render.
- medium / patch: temporary stale check never checked committed artifact. Added actual --check assertion against repository recovery-openapi.json, plus existing deterministic generation checks.
All6 findings fixed; none deferred. Blind hunter ran; broader layers omitted under oneshot.
