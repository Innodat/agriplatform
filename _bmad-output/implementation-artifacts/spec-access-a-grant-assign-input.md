---
title: Strict organization grant assignment input
type: feature
created: '2026-10-21'
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: 379a865a472de952bf73c71c25979b9df27744c2
---

<frozen-after-approval reason="standing bounded shared prerequisite implementation approval">

## Intent

Prepare only `grant.assign` through the existing Access pure parser, following the
selected execution-substrate contract. Accept exact organization scope, account UUID,
positive membership decimal string, literal ASCII permission and exactly one of
expected_absent=true or expected_revision. Preserve existing closed envelope/decoder,
immutable representation-redacted records and all delivered command behavior. Parsing
checks no authority, existence, permission association or current membership. Valid
new bodies remain unsupported at Access execution/CLI/worker boundaries before all
I/O; outcome stays invalid and Identity stays closed. Do not add grant.revoke/account
grant inputs, persistence/execution, runtime/admission/consumer activation, migrations,
dependencies, native startup, resource operations or real-target changes. Preserve all
current concurrent work, historical source/evidence and approved baseline.

</frozen-after-approval>

## Implementation Notes

bmad-help selects the next ACCESS-A prerequisite after protected organization configure.
Existing substrate payload has account_id/membership_id/permission and expected state;
there is no payload app_id or grant_id on assignment. Reuse Identity _uuid/_decimal and
OrganizationScope, existing Access permission grammar and version1 decoder. Add distinct
create/update payload classes, one command and union branch in access_operator_input.py.
Existing adapter fallback and CLI/worker allowlists already refuse new types; keep them
closed. Current uppercase UUID spelling and exact permission bytes remain preserved.
No intent gap or irreversible action; small pure-input footprint uses oneshot. Standing
approval covers the dirty tree. /tmp/grant-assign-input-preservation.json records baseline,
concurrent files,50 protected sources and the mutable parser baseline. Focused acceptance RED precedes source
edits; regression covers Access/PtS release/migrate adapter plus both composers.
New tests/test_grant_assign_input.py proves variants, structural/decoder boundaries,
redaction and direct/CLI/worker pre-I/O refusals. Owner evidence, substrate contract and
KDG handoffs record requirement/test and scaffold/UI/context/docs/ADR impacts. No ADR,
shared UI, generator or agent-context edits expected; bootstrap portability remains an
existing follow-up. No native/runtime readiness claim follows from pure inputs.


Acceptance RED: valid create input rejected as access_operator_input_invalid before source
implementation. Characterization148 passed. First focused run48 passed/2 failed because
test incorrectly expected OperatorError from worker; inspection confirms unchanged
preconnection allowlist raises bare ValueError. Correct only that expectation; adapter
and CLI retain their command_unsupported contract.


## Review Triage Log

| Finding | Verdict / evidence / route |
| --- | --- |
| Reused operation ID in update prose | medium / same envelope could imply changed retry input; patch fresh-operation wording. |
| Lookup negatives omit app_id | medium / missing app independently refuses; patch otherwise-valid Access adapter/CLI arguments. |
| Identity worker route absent | low / five-element worker delegates to Access; patch explicit four-element execute/outcome negatives. |
| Whitespace permission preservation absent | medium / future strip regression would pass; patch leading/trailing/whitespace-only exact-value successes. |
| Results pending in draft evidence | low / root evidence was completed while reviewer ran; final verification remains required after test patches. |
| Abbreviated verification commands | low / add executable cd/P/F bindings and complete command paths. |

No deferrals. All six confirmed documentation/verification findings are patched.


Final verification:234 focused passed0.58s;1434 affected regression passed36.85s;
both composition modes exit0. All109 current source bindings,50 protected sources,
14 concurrent tracked/43 pre-existing untracked bytes and frozen intent match.
Both documented examples parse. No native startup or new deferral. Five impacts in
owner evidence; scoped local commit only, no push.
