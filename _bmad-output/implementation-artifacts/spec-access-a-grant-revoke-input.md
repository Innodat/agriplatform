---
title: Strict organization grant revocation input
type: feature
created: '2026-10-22'
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: be6b9bf0fd6e1744ad7c20e48ea870dd8d3a3a47
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval and next instruction">

## Intent

Prepare `grant.revoke` through the existing Access pure parser, using the approved
execution-substrate contract: exact organization scope and payload grant_id text,
account UUID, positive membership decimal string, literal ASCII permission and positive
expected_revision. Preserve existing opaque grant IDs exactly, including empty/Unicode
values, without trimming, UUID casting or arbitrary field limits beyond the shared body
bound and forbidden-text decoder. Retain strict closed envelope, frozen redacted records,
shared decoder and all six delivered commands. Parsing confers no authority and performs
no existence/current-membership checks. Existing Access adapter/CLI/worker must refuse
valid revocation before I/O; outcome stays invalid and Identity stays closed.
No migration, grant mutation/execution, runtime/admission/consumer activation, dependency,
native startup, resource operation or real-target change. Preserve concurrent work,
existing source/receipts and the approved baseline including TypeScript7.0.2.

</frozen-after-approval>

## Implementation Notes

bmad-help selects the next ACCESS-A dependency after delivered grant.assign. The missing
pure-input contract precedes protected revoke execution; deliver only this bounded
foundation now. No intent gap, irreversible operation or missing external prerequisite.
Small owner-parser footprint uses oneshot under existing approval, including dirty tree.
Reuse OrganizationScope, Identity _uuid/_decimal and Access permission grammar/decoder.
Add GrantRevocationPayload/RevokeGrantCommand and union/parse branch in
services/access/access_operator_input.py. Existing adapter final isinstance guard and
CLI/worker allowlists must stay closed; tests demonstrate safe refusal before any I/O.
Tests in services/access/tests/test_grant_revoke_input.py cover preserved values,
closed/duplicate fields, expected-state/type/decoder boundaries, redaction/immutability,
Access and Identity execute/outcome/CLI/worker refusal. Observe acceptance RED first.
/tmp/grant-revoke-input-preservation.json binds starting source/concurrent bytes.
Owner evidence plus mutable substrate/KDG handoffs record requirement-to-test mapping
and five impacts: existing owner input scaffold extended; no shared UI, agent-context or
ADR change; documentation updated. No generator or runtime framework. Deployment impact
is none; no lifecycle startup or native qualification is needed for a pure parser.
Use prepared Python for focused tests, then Access/PtS release/migrate adapter regression
and both composition modes. Review current owned changes only, preserve all other work,
record exact results/custody and create a scoped conventional local commit without push.


Acceptance RED observed valid revocation rejection before production edits (1 expected
failure0.06s). Only access_operator_input.py production changed; existing adapter/CLI
guards required no edits. Focused126 PASS0.37s, affected1645 PASS44.46s, both composition
checks exit0; documented example parses. Review and final custody/commit follow.


## Review Triage Log

| Finding | Verdict / evidence / route |
| --- | --- |
| Raw UTF-8/multibyte body boundary missing | medium / Unicode success currently uses ASCII escapes and padded ASCII body boundary; add raw UTF-8 grant ID and exact65536/65537-byte payload tests. Patch. |
| Sensitive opaque grant ID absence not asserted | medium / generic refusal helper omits the specific opaque value; add distinct sentinel grant ID and explicit exception/traceback/CLI checks. Patch. |
| Unusual opaque IDs absent from execution refusals | low / guard is type-based before inspecting fields, but boundary proof uses one ID only; direct test parameterization over empty/Unicode/long/sentinel values is small and supports the stated contract. Patch. |
| Extract imported tests into new helper module | false / no silent failure demonstrated: incompatible signatures fail loudly; pytest monkeypatch restores the shared document factory after each test. Existing adjacent input suites use the same assertions and full regression passes. No concrete caller divergence or invariant failure supports introducing new shared test infrastructure. Reject. |
| Temporary custody evidence lacks durable digests | medium / /tmp receipts do not accompany the commit. Add completed results, baseline-reconstructible protected inventory digest, parser/frozen-intent and command-log digests to repository owner evidence. Patch. |

Findings individually classified before grouping: sensitive-ID and unusual-ID boundary
checks share one parameterized fixture correction; UTF-8 and durable custody are separate.
No deferral. Production parser and execution boundaries need no change after review.


Final verification:130 focused PASS0.41s;1649 affected regression PASS39.12s; both
composition modes exit0 and documented example parses. One configured oneshot review
completed:5 individually triaged findings,4 direct test/evidence corrections,1 false
refuted, no deferral. All202 protected Access files and frozen intent remain intact;
only parser production source changes. Durable custody/log digests and five impacts
are in owner evidence. No native startup or resource/real-target operation. Scoped local
commit completes this pure-input foundation; protected writer remains next.
