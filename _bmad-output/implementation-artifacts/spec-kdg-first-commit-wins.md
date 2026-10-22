---
title: Defer KDG fingerprints and use first committed outcomes
type: chore
created: '2026-10-22'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 0720203627714a93f9b0c8f65538d93d31fea393
context:
  - AGENTS.md
  - platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md
---

<frozen-after-approval reason="user explicitly says leave fingerprints and HMAC until needed after agreeing simpler first-commit-wins retries">

## Intent

Defer KDG command fingerprints, HMAC, fingerprint secret files and associated key
backup/restore work until a concrete need justifies them. Select first committed
request wins for the current KDG MVP. Reconcile authoritative decisions/contracts and
handoff so later work cannot accidentally restore the deferred prerequisite.

## Boundaries & Constraints

The server defines command type (capture.create/edit), never trusts an arbitrary action
field as authority. Uniqueness remains(org_id,executor_account_id,command_type,operation_id).
Business changes, required immutable evidence and compact outcome commit atomically;
concurrent duplicates cannot execute twice. Successful committed duplicates return
the original authorized receipt, including its original target/revision, even if
incoming content differs. No payload comparison, SHA/JCS digest, HMAC or fingerprint
metadata is required for current KDG commands. Strict input validation, current
permissions on actual stored resources, supported receipt versions, structural scope,
revision/lifecycle and bounded uncertainty protections remain. Replays must resolve
stored target privately and recheck current authority; supplied target/action never
grants authority. New business actions/changed submitted input use a new operation ID.
The client freezes queued command input; only that submitted snapshot is confirmed by
its receipt. Pending predecessors continue blocking later sends; unknown outcomes
never create a new operation automatically. Failed/uncommitted actions have no success
receipt. No automatic outcome expiry/deletion is introduced.

Record a linked partially superseding platform ADR for KDG's changed-content rule;
leave accepted ADR0012 bytes unchanged. Preserve Leave/PtS/Identity/Access choices and
existing runtime/migration/SQL/tests, completed candidate code, evidence and synthetic
resources as historical reusable work. This is a documentation/decision change only:
no runtime conversion, migration, implementation, provisioning, deployment or cleanup.
Ordinary business-data backups/recovery and child privacy gates remain binding.

## I/O & Edge-Case Matrix

| Scenario | Current KDG contract |
| --- | --- |
| Repeated scoped command/operation ID, identical or changed body | Original committed receipt after current stored-resource authorization; no second effect |
| Changed/new intended action | New operation ID, ordinary validation and expected revision |
| In-flight/unknown or denied/foreign recovery | Existing bounded busy/unresolved/denial semantics, no existence leak or automatic fresh action |
| Historical fingerprint/HMAC candidates | Retained untouched; no active KDG prerequisite or automatic algorithm fallback |

</frozen-after-approval>

## Code Map

- New `platform/docs/architecture/decisions/0061-kdg-first-committed-operation-wins.md`: accepted user choice, partially supersedes0012 for KDG only. Root handles platform ADR index because it contains concurrent edits. Agent must not edit that index.
- `apps/kdg-capture/docs/contracts.md`: owning outcome/receipt/retry/canonical-envelope sections.
- `platform/docs/architecture/contracts/owned-write-and-secret-execution.md`, `operation-fingerprint-security-evolution.md`, `kdg-shared-readiness.md`, `api-errors-and-operation-recovery.md`: precise KDG amendment/selected model and deferred-secret status, operator/Leave behavior preserved.
- KDG `ARCHITECTURE-SPINE.md`, `shared-prerequisites.md`, `implementation-readiness.md`, `testing.md`, `epics.md`, `shared-platform-handoff.md`, `architecture/decisions/README.md`: align current KDG requirements and acceptance mappings; retain historical checkpoint accounts with explicit supersession.
- `apps/kdg-capture/docs/next-session.md`: prepend decision/current-next-work, preserve complete original tail.
- `platform/builder-cli/examples/owned-service/README.md`: prepend current deferral/status; do not change candidate/evidence/test bytes.

## Tasks & Acceptance

- [x] Write accepted0061 with authority/context/consequences; update clean KDG decision index. Root adds only its own row to concurrently modified platform index.
- [x] Reconcile current owner/app contracts and readiness/test plans, linking authoritative decisions instead of duplicating feature specifications. Label historic HMAC selections superseded; remove current key-recovery gate from KDG.
- [x] Update handoff/current example status; leave historical evidence/candidate code untouched. Report exact documentation checks, source preservation and five impacts.

Given an authoritative current KDG document, when determining retry prerequisites,
then it selects first-commit-wins with no fingerprint requirement and retains all
other current access/atomicity/queue/recovery safeguards. Given other owners/accepted
ADRs or historical code/evidence, when inspected, then bytes/behavior remain unchanged.

## Implementation Notes

User approval covers the contract decision and concurrent-tree preservation. Agent
owns ADR/contracts/KDG docs/example status only, no staging/commit/platform-index edit.
Root owns final review/audit/index surgical delta/local commit. Keep lean; append
explicit current amendments to historical documents where rewriting would erase
history, but fix live normative clauses that would otherwise contradict the decision.
Do not claim tests of new runtime behavior: none is implemented. No new automated test
suite needed for prose; validate changed links, old/new requirement consistency and
prior byte hashes. Proof snapshots: platform/builder-cli/.local/kdg-first-commit-wins-20261022.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence and resolution |
| --- | --- | --- |
| Blind 1: receipt cannot prove content equality | false / reject | Frozen unique client operation binding is an explicit client invariant; server equality attestation was deliberately removed. Clarify this limitation with the client-target patch; no payload comparison is restored. |
| Blind 2: changed target can misassociate local queue | medium / patch | Receipt and queued target reconciliation was implicit; explicitly preserve input and block descendants on mismatch. |
| Blind 3: supplied-target preauthorization can reject stored replay | medium / patch | Execution step 1 permitted either source. Prefer private stored target discovery for committed KDG outcomes; preserve race restart. |
| Blind 4: structural versus domain validation order | medium / patch | Strict validation was ambiguous before lookup. Clarify supported structural parsing first and fresh-only domain validation. |
| Blind 5: command version omitted from operation key | medium / patch | Supported incoming versions versus original receipt version needed an explicit rule; return original supported receipt. |
| Blind 6: different-body concurrency evidence | medium / patch | A09 concurrency lacked explicit competing body assertions; add planned acceptance scenario. |
| Blind 7: replay after later revision/lifecycle change | medium / patch | Fresh-only checks were specified but corresponding replay-after-change scenario absent; add A09 evidence. |
| Blind 8: lock encoding removed with canonical envelope | false / reject | Execution step 2 still independently specifies UTF-8 JCS object fields, normalized typed UUIDs, SHA256 first8 signed big-endian64 and stable lock_version1. Command fingerprint deferral does not remove advisory-lock encoding or existing scaffold dependencies. |
| Blind 9: remaining current references | medium / patch | Substrate HMAC sentence and story1.6 prerequisite still directed future delivery to deferred work; reconcile these two live references only. |

Edge-case reviewer returned no findings. Verification-gap reviewer returned no gaps.

## Verification

Read changed docs against the matrix; check new/changed links and scoped whitespace.
Verify ADR0012 and all runtime/candidate/test/evidence bytes preserved. Record scaffold
impact (future opt-in; existing candidates historical), shared UI (snapshot receipt
interpretation documented, no code), agent context (unchanged), docs (reconciled), ADR
(accepted0061 partially supersedes0012 for KDG). No production/migration/CI readiness claim.


Completed documentation verification: `python3 platform/builder-cli/.local/kdg-first-commit-wins-20261022/check_docs.py` passed (19 docs and changed relative links; accepted ADR0012, historical candidate execution sources/proofs and retained fixture hashes unchanged). `python3 .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace apps/kdg-capture/docs` passed with zero findings. Scoped `git diff --check` passed. All three reviews completed; seven direct documentation corrections applied, two findings rejected with evidence above. No runtime behavior was implemented or tested. Scaffold, shared UI, agent-context, documentation and ADR impacts are recorded in ADR0061. Concurrent changes excluded from the commit, including the existing platform ADR index delta.
