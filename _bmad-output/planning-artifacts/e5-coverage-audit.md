# E5 source-criterion ownership audit

**Status:** E5 story planning closed by user agreement on 2026-10-25 — all 230 original source criteria allocated; residual
writers, refinements, first-use ownership, graph and qualitative sizing reconciled.
Whole-product final coverage and implementation readiness remain open.  
**Date:** 2026-10-25  
**Source:** [current epics](epics.md), original approved Story 5.1–5.32 criteria, interpreted
with the later accepted refinements and owning contracts. No implementation/test run.

## What this inventory establishes

32 original scopes contain **230 source Given/When/Then criteria**. All 230 are indexed
below with proposed existing owner links. Many criteria contain several Then/And obligations;
230 is not a count of independent atomic requirements or successful tests. Cue text is
navigation only, never a rewritten specification. The authoritative complete criterion is
at its original story heading/ordinal. Hashes detect edits to the normalized source text.

Historical pass-1 count: **80 approved suffixed delivery boundaries**. The accepted
5.28-C extraction increases this to **81**, plus seven retained foundation items = **88**
candidate executable items; see the final reconciliation below. Seven previously approved
foundation scopes have no suffixed child: 5.1 route, 5.2 temporary eligibility, 5.3 applicant
coverage, 5.4 absence fallback, 5.6 duration/capacity, 5.7 employment/policy/date eligibility,
and 5.9 document policy/readiness. They remain real work and must appear in the final
executable order/sizing. This is not seven new features or approval of seven sized stories.
Final executable count is pending their allocation; the historical 80 cannot be presented
as a complete estimate for all E5 work.

Original 5.8 funding is different: E3 owns deterministic read allocation, 5.8-A actual
protected commitments, and submission/exception consumers actual reviewed result/progression.
Audit remaining clauses before claiming that the parent needs no additional boundary.
Original 5.14 is deliberately absorbed into actual 5.12 response/5.13 and 5.15 changes/
5.19 withdrawal, not another response system. Other unsuffixed parents describe approved
scope and references rather than extra duplicate implementation items.

Current original criterion digest (normalized criteria in scope/ordinal order):
`d5c14c8d45afe8f4c2a1570868386abfe3595a0eb8df76a319581096e9f47cd9`.

## Source scope and existing owner inventory

| Original scope | Source criteria | Approved suffixed boundaries | C6 allocation status |
| --- | --- | --- | --- |
| 5.1 | 8 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.2 | 7 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.3 | 9 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.4 | 7 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.5 | 7 | 5.5-A, 5.5-B | Existing suffixed owners; clause/producer audit pending |
| 5.6 | 8 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.7 | 7 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.8 | 8 | 5.8-A | Detailed funding allocation below; no residual standalone funding engine needed, final dependency/size check open |
| 5.9 | 7 | — | Existing foundation scope; executable allocation/sizing pending |
| 5.10 | 8 | 5.10-A, 5.10-B, 5.10-C | Existing suffixed owners; clause/producer audit pending |
| 5.11 | 8 | 5.11-A, 5.11-B | Existing suffixed owners; clause/producer audit pending |
| 5.12 | 9 | 5.12-A, 5.12-B | Existing suffixed owners; clause/producer audit pending |
| 5.13 | 7 | 5.13-A, 5.13-B | Existing suffixed owners; clause/producer audit pending |
| 5.14 | 8 | — | Allocated into 5.12/13/15/19; not another employee-response implementation |
| 5.15 | 8 | 5.15-A, 5.15-B, 5.15-C, 5.15-D, 5.15-E, 5.15-F, 5.15-G, 5.15-H, 5.15-I, 5.15-J, 5.15-K, 5.15-L, 5.15-M, 5.15-N, 5.15-O, 5.15-P, 5.15-Q, 5.15-R, 5.15-S, 5.15-T, 5.15-U, 5.15-V | Eleven real source-family/leaf allocations below; actual full predecessor/order/size check open |
| 5.16 | 8 | 5.16-A, 5.16-B | Existing suffixed owners; clause/producer audit pending |
| 5.17 | 8 | 5.17-A, 5.17-B | Existing suffixed owners; clause/producer audit pending |
| 5.18 | 8 | 5.18-A, 5.18-B | Existing suffixed owners; clause/producer audit pending |
| 5.19 | 8 | 5.19-A, 5.19-B | Existing suffixed owners; clause/producer audit pending |
| 5.20 | 8 | 5.20-A, 5.20-B | Existing suffixed owners; clause/producer audit pending |
| 5.21 | 9 | 5.21-A, 5.21-B | Existing suffixed owners; clause/producer audit pending |
| 5.22 | 8 | 5.22-A, 5.22-B, 5.22-C, 5.22-D | Existing suffixed owners; clause/producer audit pending |
| 5.23 | 8 | 5.23-A | Existing suffixed owners; clause/producer audit pending |
| 5.24 | 8 | 5.24-A, 5.24-B, 5.24-C, 5.24-D, 5.24-E, 5.24-F | Existing suffixed owners; clause/producer audit pending |
| 5.25 | 8 | 5.25-A | Existing suffixed owners; clause/producer audit pending |
| 5.26 | 5 | 5.26-A | Existing suffixed owners; clause/producer audit pending |
| 5.27 | 4 | 5.27-A, 5.27-B | Existing suffixed owners; clause/producer audit pending |
| 5.28 | 5 | 5.28-A, 5.28-B | Existing suffixed owners; clause/producer audit pending |
| 5.29 | 6 | 5.29-A, 5.29-B | Existing suffixed owners; clause/producer audit pending |
| 5.30 | 5 | 5.30-A, 5.30-B | Existing suffixed owners; clause/producer audit pending |
| 5.31 | 4 | 5.31-A | Existing suffixed owners; clause/producer audit pending |
| 5.32 | 4 | 5.32-A, 5.32-B, 5.32-C, 5.32-D, 5.32-E, 5.32-F, 5.32-G, 5.32-H, 5.32-I, 5.32-J, 5.32-K, 5.32-L | Existing suffixed owners; clause/producer audit pending |

## Candidate criterion-to-owner ledger

`A/B` means the existing API/browser partners, not a new combined executable story.
Ranges such as 5.15-A–V mean every actual applicable source family must be resolved in
the next pass, not that one convenient source test covers all 22 boundaries. External E3
references must be checked against actual completed predecessor work, with only real new
integration counted. Candidate composite ownership is explicitly not yet a one-primary-
owner-per-atomic-clause allocation.

| Stable source ID | Source story/ordinal and navigation cue | Candidate existing owners | Source hash |
| --- | --- | --- | --- |
| E5-01-AC01 | 5.1 AC1 — an applicable one-step policy, | 5.1 | a760df828e43 |
| E5-01-AC02 | 5.1 AC2 — an applicable two-step policy, | 5.1 | d17292101572 |
| E5-01-AC03 | 5.1 AC3 — a definitively missing or invalid configured route, | 5.1 | b209dfb9bd70 |
| E5-01-AC04 | 5.1 AC4 — a required owner cannot supply a trustworthy observation, | 5.1 | bb4cafdb4bc3 |
| E5-01-AC05 | 5.1 AC5 — the requester occupies a configured approval position or the same person | 5.1 | 4bb474d7bbae |
| E5-01-AC06 | 5.1 AC6 — known approver absence or an applicant approval-responsibility coverage gap, | 5.1 | 5f000c66575a |
| E5-01-AC07 | 5.1 AC7 — requester-facing approval information, | 5.1 | f974450b89cd |
| E5-01-AC08 | 5.1 AC8 — a successful provisional route check, | 5.1 | 71c9796e010d |
| E5-02-AC01 | 5.2 AC1 — an authorized manager selecting a temporary approver, | 5.2 | 91ce2ab1bb73 |
| E5-02-AC02 | 5.2 AC2 — selected responsibilities and dates, | 5.2 | 3998a7727a68 |
| E5-02-AC03 | 5.2 AC3 — known absence, inactive membership or a self-approval conflict, | 5.2 | be1ddab8949a |
| E5-02-AC04 | 5.2 AC4 — another temporary assignment for the same responsibilities, | 5.2 | 08df35dd655d |
| E5-02-AC05 | 5.2 AC5 — a valid recorded appointment, | 5.2 | 4c1a0f2ccbab |
| E5-02-AC06 | 5.2 AC6 — temporary approval authority, | 5.2 | a5baa40506ac |
| E5-02-AC07 | 5.2 AC7 — a required eligibility check fails temporarily, | 5.2 | 08b5a43df46b |
| E5-03-AC01 | 5.3 AC1 — an applicant with no approval responsibilities, | 5.3 | 9f1c80f93a54 |
| E5-03-AC02 | 5.3 AC2 — an applicant with approval responsibilities, | 5.3 | 2f941b4c2fb0 |
| E5-03-AC03 | 5.3 AC3 — eligible temporary appointments, | 5.3 | 54773924a3ce |
| E5-03-AC04 | 5.3 AC4 — an explicitly enabled absence policy, | 5.3 | a20d8b62b100 |
| E5-03-AC05 | 5.3 AC5 — incomplete coverage, | 5.3 | f13a5b302ea8 |
| E5-03-AC06 | 5.3 AC6 — a valid reasoned coverage exception, | 5.3 | 2fb32d71003e |
| E5-03-AC07 | 5.3 AC7 — required coverage information cannot be verified, | 5.3 | 69959ea4b2cc |
| E5-03-AC08 | 5.3 AC8 — cover becomes unavailable after leave is approved, | 5.3 | d89dc64ca9aa |
| E5-03-AC09 | 5.3 AC9 — human-selected cover arrangements, | 5.3 | 22c2327a4ac6 |
| E5-04-AC01 | 5.4 AC1 — the optional absence policy is disabled, | 5.4 | a8a31fb58b83 |
| E5-04-AC02 | 5.4 AC2 — the policy is enabled and the supervisor has recorded applicable absence, | 5.4 | 80d014f44fc9 |
| E5-04-AC03 | 5.4 AC3 — the final approver is absent, | 5.4 | 27c53bb5b2b0 |
| E5-04-AC04 | 5.4 AC4 — both usual approvers are absent and the applicable absence policy is | 5.4 | 95ab63a77c24 |
| E5-04-AC05 | 5.4 AC5 — absence is evaluated, | 5.4 | d67445de85f3 |
| E5-04-AC06 | 5.4 AC6 — a request waits for the supervisor's return, | 5.4 | c11536e80c1f |
| E5-04-AC07 | 5.4 AC7 — fallback permits fewer required steps, | 5.4 | 0be00ef2e958 |
| E5-05-AC01 | 5.5 AC1 — an identified approval-coverage gap, | 5.5-A | 738fcb0be558 |
| E5-05-AC02 | 5.5 AC2 — an authorized exception, | 5.5-A | 34d499db2d7a |
| E5-05-AC03 | 5.5 AC3 — a valid exception, | 5.5-A | 28d62684178c |
| E5-05-AC04 | 5.5 AC4 — a recorded exception, | 5.5-A | ce2add584e99 |
| E5-05-AC05 | 5.5 AC5 — actual absence dates, | 5.5-A | dced8dc4b564 |
| E5-05-AC06 | 5.5 AC6 — changed absence dates or responsibilities, | 5.5-B | daf6350c2e9f |
| E5-05-AC07 | 5.5 AC7 — an authorized manager grants the coverage exception, | 5.5-A | bd86047041bf |
| E5-06-AC01 | 5.6 AC1 — a selected leave type, | 5.6 | 5165d03124c3 |
| E5-06-AC02 | 5.6 AC2 — a valid range containing working and non-working dates, | 5.6 | c67f2b69fd15 |
| E5-06-AC03 | 5.6 AC3 — half-day leave, | 5.6 | 3d902cb3972a |
| E5-06-AC04 | 5.6 AC4 — hourly leave, | 5.6 | 0d813aca58ad |
| E5-06-AC05 | 5.6 AC5 — another active request for the same employee, organization and absence date, | 5.6 | 88433e1405bb |
| E5-06-AC06 | 5.6 AC6 — combined active durations within that date's scheduled working time, | 5.6 | 4854c4749734 |
| E5-06-AC07 | 5.6 AC7 — simultaneous requests covering the same absence date, | 5.6 | 377f89f10a0a |
| E5-06-AC08 | 5.6 AC8 — failed validation or unavailable required schedule information, | 5.6 | 20d96405968f |
| E5-07-AC01 | 5.7 AC1 — the employee, leave type and requested dates, | 5.7 | e7bc4ce29efb |
| E5-07-AC02 | 5.7 AC2 — a known employment end date, | 5.7 | 8c6528c34f1c |
| E5-07-AC03 | 5.7 AC3 — the policy's advance-booking window, | 5.7 | 10114c683e1e |
| E5-07-AC04 | 5.7 AC4 — less than configured minimum notice, | 5.7 | b065881690bc |
| E5-07-AC05 | 5.7 AC5 — backdated leave, | 5.7 | c7423af82f46 |
| E5-07-AC06 | 5.7 AC6 — changed employment or applicable configuration since preview, | 5.7 | 70f063ae165d |
| E5-07-AC07 | 5.7 AC7 — missing configuration or failed dependency verification, | 5.7 | deca501f5ebd |
| E5-08-AC01 | 5.8 AC1 — a balance-tracked policy, | 3.18 | 809999908575 |
| E5-08-AC02 | 5.8 AC2 — earning becomes available between requested dates, | 3.18 | 9e711928297e |
| E5-08-AC03 | 5.8 AC3 — existing reservations, | 3.18; 5.8-A | 0af5f6f5a01c |
| E5-08-AC04 | 5.8 AC4 — several eligible entitlement portions, | 3.18 | 8abb3388ee6b |
| E5-08-AC05 | 5.8 AC5 — insufficient funding, | 5.11-A/B; 5.13-A/B | 52d27bd87b88 |
| E5-08-AC06 | 5.8 AC6 — a policy with No balance tracking, | 5.8-A; 5.11-A/B | 7976f2cfd730 |
| E5-08-AC07 | 5.8 AC7 — changed funding inputs or simultaneous competing requests, | 5.8-A; 5.11-A | 15b7ff7a7b1d |
| E5-08-AC08 | 5.8 AC8 — funding cannot be verified, | 5.11-B; 3.18 | 1bc5ef790053 |
| E5-09-AC01 | 5.9 AC1 — the applicable policy and calculated duration, | 5.9 | 688c209d44c9 |
| E5-09-AC02 | 5.9 AC2 — a required document, | 5.9 | 260a4670b4bc |
| E5-09-AC03 | 5.9 AC3 — a missing, pending, rejected or failed required attachment, | 5.9 | b6280fbf4d4c |
| E5-09-AC04 | 5.9 AC4 — document status cannot be checked, | 5.9 | d82ceca21ad5 |
| E5-09-AC05 | 5.9 AC5 — final approval is attempted, | 5.9 | be4a7304e047 |
| E5-09-AC06 | 5.9 AC6 — an assigned approver or Leave Manager without sensitive-document permission, | 5.9 | b1a8ae1b2357 |
| E5-09-AC07 | 5.9 AC7 — valid evidence already attached, | 5.9 | d60b5d31593f |
| E5-10-AC01 | 5.10 AC1 — a request approaching completion, | 5.10-B | 60e04dc58d9c |
| E5-10-AC02 | 5.10 AC2 — required decisions are satisfied, | 5.10-B | e971ef31dd48 |
| E5-10-AC03 | 5.10 AC3 — one condition remains unmet, | 5.10-B | 8b71a522c1b5 |
| E5-10-AC04 | 5.10 AC4 — an authorized submitting approver already satisfied their own step, | 5.10-B | 0b9b4ac4af0c |
| E5-10-AC05 | 5.10 AC5 — an employee response to an unpaid amount, | 5.10-B | ec7cee759b6c |
| E5-10-AC06 | 5.10 AC6 — all conditions pass, | 5.10-B | 5f3cb659add3 |
| E5-10-AC07 | 5.10 AC7 — competing approvals, employee responses, withdrawal or relevant configuration changes, | 5.10-B | adf406f74e13 |
| E5-10-AC08 | 5.10 AC8 — a required check cannot finish, | 5.10-B | 0830eb2dadff |
| E5-11-AC01 | 5.11 AC1 — my application is ready for review, | 5.11-B | 717ea068286f |
| E5-11-AC02 | 5.11 AC2 — requested unpaid leave, | 5.11-A/B | a42ba56e70e9 |
| E5-11-AC03 | 5.11 AC3 — I submit, | 5.11-A | 3f465bf5dcac |
| E5-11-AC04 | 5.11 AC4 — valid submission, | 5.11-A | 4946b92c842b |
| E5-11-AC05 | 5.11 AC5 — I am an authorized assigned approver and self-approval is explicitly enabled, | 5.11-A | 5895278c3cc3 |
| E5-11-AC06 | 5.11 AC6 — confirmed success, | 5.11-B | 180298d0c533 |
| E5-11-AC07 | 5.11 AC7 — confirmed failure or uncertain outcome, | 5.11-A/B | fd78e459c0b7 |
| E5-11-AC08 | 5.11 AC8 — duplicate clicks, response loss or late autosaves from another tab, | 5.11-A/B | 6e4558c6ff4e |
| E5-12-AC01 | 5.12 AC1 — current scoped on-behalf submission permission, | 5.12-A/B | 9a4c28f45162 |
| E5-12-AC02 | 5.12 AC2 — a selected employee, | 5.12-A | 0aa057fefa94 |
| E5-12-AC03 | 5.12 AC3 — completed input, | 5.12-B | 0186425bce1e |
| E5-12-AC04 | 5.12 AC4 — submission, | 5.12-A | e96e6856a06d |
| E5-12-AC05 | 5.12 AC5 — the submitter also owns an authorized approval step, | 5.12-A | d13f50d34b66 |
| E5-12-AC06 | 5.12 AC6 — requested unpaid leave, | 5.12-A/B | a667ebae61b9 |
| E5-12-AC07 | 5.12 AC7 — all decisions are satisfied but employee response or another finalization condition | 5.12-A | 9c0b90ad0d0f |
| E5-12-AC08 | 5.12 AC8 — the employee already has a saved draft, | 5.12-A/B | 2a3d9baf2503 |
| E5-12-AC09 | 5.12 AC9 — failure, unknown outcome or repeated submission, | 5.12-A/B | 0ec8e02375c6 |
| E5-13-AC01 | 5.13 AC1 — a request needing a balance override, | 5.13-A/B | bed7cade284e |
| E5-13-AC02 | 5.13 AC2 — an actor reviewing alternatives, | 5.13-A | e2396ca94912 |
| E5-13-AC03 | 5.13 AC3 — permitted alternatives, | 5.13-A/B | de80b107e3bc |
| E5-13-AC04 | 5.13 AC4 — proposed allocation, | 5.13-A | a4965ce155a7 |
| E5-13-AC05 | 5.13 AC5 — funding-only confirmation or an actor authorized for both funding and their | 5.13-A/B | 9da5fa6ab551 |
| E5-13-AC06 | 5.13 AC6 — an increased requested-unpaid amount, | 5.13-A/B | 7ec2d2de7d39 |
| E5-13-AC07 | 5.13 AC7 — changed inputs, conflicting actions or unknown results, | 5.13-A/B | e085a52f6b70 |
| E5-14-AC01 | 5.14 AC1 — an on-behalf request containing unpaid leave, | 5.12-A/B | 282cdb512ad4 |
| E5-14-AC02 | 5.14 AC2 — a later authorized change increases or decreases pending unpaid allocation, | 5.13-A/B; 5.15-A–V | 0a0b4a574a7d |
| E5-14-AC03 | 5.14 AC3 — a required response, | 5.12-A | aea6e7525e00 |
| E5-14-AC04 | 5.14 AC4 — allocation changes while the response is open, | 5.12-A | 0d4a3f400218 |
| E5-14-AC05 | 5.14 AC5 — successful acknowledgement, | 5.12-A; 5.10-B | fc4d47d4f634 |
| E5-14-AC06 | 5.14 AC6 — a notification is opened/marked read, | 5.12-A; 3.26 | a7db28ab7b98 |
| E5-14-AC07 | 5.14 AC7 — a request eligible for withdrawal, | 5.19-A/B | 2df9e5753c6d |
| E5-14-AC08 | 5.14 AC8 — failed/unknown/duplicate response or a request closed elsewhere, | 5.12-A/B | 5f2233e2db82 |
| E5-15-AC01 | 5.15 AC1 — a proposed change affects pending requests, | 5.15-A–V | 53fb0ad147d8 |
| E5-15-AC02 | 5.15 AC2 — consequential request changes, | 5.15-A–V | 6aac7459a1ee |
| E5-15-AC03 | 5.15 AC3 — a later authorized pending paid/unpaid allocation change, | 5.15-A–V | 594245967547 |
| E5-15-AC04 | 5.15 AC4 — an affected pending request, | 5.15-A–V | 3387c8a1a730 |
| E5-15-AC05 | 5.15 AC5 — another eligibility condition becomes invalid, such as dates beyond corrected employment | 5.15-A–V | af3369ea020b |
| E5-15-AC06 | 5.15 AC6 — resolution needs exceptional funding, adjustment or correction, | 5.15-A–V | 69323779be77 |
| E5-15-AC07 | 5.15 AC7 — concurrent changes/decisions/retries, | 5.15-A–V | bbea6dba7768 |
| E5-15-AC08 | 5.15 AC8 — ordinary expected accrual, expiry or rollover, | 5.15-A–V | c977f949326e |
| E5-16-AC01 | 5.16 AC1 — current approval responsibilities, | 5.16-A | efd37e923626 |
| E5-16-AC02 | 5.16 AC2 — ordinary or temporary assignments, | 5.16-A/B | 7191f89b1434 |
| E5-16-AC03 | 5.16 AC3 — effective supervisor change or expired/lost authority, | 5.16-A | 55c93cb78fbe |
| E5-16-AC04 | 5.16 AC4 — a queue row, | 5.16-A/B | 1885d8d0f272 |
| E5-16-AC05 | 5.16 AC5 — multiple tasks, | 5.16-A/B | 98083a4281d8 |
| E5-16-AC06 | 5.16 AC6 — a selected request, | 5.16-A/B | a03dfd01b1ec |
| E5-16-AC07 | 5.16 AC7 — loading/no tasks/no matches/failed refresh, | 5.16-A/B | e5d241eb8947 |
| E5-16-AC08 | 5.16 AC8 — desktop/mobile inspection, | 5.16-B | 3b09ba517d12 |
| E5-17-AC01 | 5.17 AC1 — an authorized request review, | 5.17-A | 2877d5d89fb3 |
| E5-17-AC02 | 5.17 AC2 — relevant colleague absences, | 5.17-A | 9d52580f955a |
| E5-17-AC03 | 5.17 AC3 — desktop/mobile review, | 5.17-B | 7c9f4979feba |
| E5-17-AC04 | 5.17 AC4 — partial-day leave, | 5.17-A/B | 7abef3128601 |
| E5-17-AC05 | 5.17 AC5 — no authority for a colleague's detailed request, | 5.17-A | 4f04b1af2c85 |
| E5-17-AC06 | 5.17 AC6 — temporary approval responsibilities, | 5.17-A | f07a462d90e9 |
| E5-17-AC07 | 5.17 AC7 — failed availability load, | 5.17-B | e7c68a6aa264 |
| E5-17-AC08 | 5.17 AC8 — capacity concerns, | 5.17-A | bc761794bb86 |
| E5-18-AC01 | 5.18 AC1 — an actionable assigned step, | 5.18-A | 0c8a29c4d1ec |
| E5-18-AC02 | 5.18 AC2 — approval, | 5.18-A/B | afee545fc1c0 |
| E5-18-AC03 | 5.18 AC3 — another required decision/finalization condition remains, | 5.18-A | 7f4867a8691d |
| E5-18-AC04 | 5.18 AC4 — the last outstanding decision and every independent condition pass, | 5.18-A; 5.10-B | 29de219c309e |
| E5-18-AC05 | 5.18 AC5 — rejection, | 5.18-A/B | 0cc72c7ccddd |
| E5-18-AC06 | 5.18 AC6 — successful decision, | 5.18-A | 9f0158b5131a |
| E5-18-AC07 | 5.18 AC7 — change/closure/reassignment during review, | 5.18-A/B | f94f9483d0e4 |
| E5-18-AC08 | 5.18 AC8 — failed/unknown outcome, | 5.18-A/B | 8d40d67dd1f9 |
| E5-19-AC01 | 5.19 AC1 — my eligible submitted/in-approval request, | 5.19-A/B | 26bc3d9cc588 |
| E5-19-AC02 | 5.19 AC2 — withdrawal is selected, | 5.19-A/B | c348389e21f2 |
| E5-19-AC03 | 5.19 AC3 — confirmation, | 5.19-A/B | 8e3da3186016 |
| E5-19-AC04 | 5.19 AC4 — valid withdrawal, | 5.19-A/B | bb06504bf6cc |
| E5-19-AC05 | 5.19 AC5 — earlier decisions or attachments, | 5.19-A/B | 2b194250c6f1 |
| E5-19-AC06 | 5.19 AC6 — an approver already reviewing the request, | 5.19-A/B | ca4de27edd62 |
| E5-19-AC07 | 5.19 AC7 — competing final approval/withdrawal/retries, | 5.19-A/B | 5ac7a50444f8 |
| E5-19-AC08 | 5.19 AC8 — failed/unknown result, | 5.19-A/B | 22f9acc61d97 |
| E5-20-AC01 | 5.20 AC1 — my rejected request, | 5.20-A/B | 62d89f0156c5 |
| E5-20-AC02 | 5.20 AC2 — I choose edit, | 5.20-A/B | b57dc755ceb7 |
| E5-20-AC03 | 5.20 AC3 — editing, | 5.20-A/B | 511ac50e59b0 |
| E5-20-AC04 | 5.20 AC4 — resubmission, | 5.20-A/B | 7c367a395abe |
| E5-20-AC05 | 5.20 AC5 — valid resubmission, | 5.20-A/B | eae23f4e562d |
| E5-20-AC06 | 5.20 AC6 — a submitting employee eligible for automatic approval, | 5.20-A/B | 948636fac969 |
| E5-20-AC07 | 5.20 AC7 — successful resubmission, | 5.20-A/B | 91a3076a07c2 |
| E5-20-AC08 | 5.20 AC8 — failed validation, competing edits or unknown result, | 5.20-A/B | efb6d568e2ed |
| E5-21-AC01 | 5.21 AC1 — appointment authority, | 5.21-A/B | 21a55216359a |
| E5-21-AC02 | 5.21 AC2 — a proposed appointment, | 5.21-A/B | c985e5a57214 |
| E5-21-AC03 | 5.21 AC3 — outstanding approvals, | 5.21-A/B | c1ca05bf97a2 |
| E5-21-AC04 | 5.21 AC4 — temporary final responsibilities, | 5.21-A/B | 608c1566a64f |
| E5-21-AC05 | 5.21 AC5 — appointment review, | 5.21-A/B | 03b1f53dc5ad |
| E5-21-AC06 | 5.21 AC6 — valid confirmation, | 5.21-A/B | a92790fc797c |
| E5-21-AC07 | 5.21 AC7 — the appointment becomes effective, | 5.21-A/B | ee3647fe8d57 |
| E5-21-AC08 | 5.21 AC8 — appointed authority, | 5.21-A/B | 4fe0641373b5 |
| E5-21-AC09 | 5.21 AC9 — changed inputs, unavailable checks or unknown confirmation, | 5.21-A/B | 7459757c4305 |
| E5-22-AC01 | 5.22 AC1 — an existing assignment, | 5.22-A/B | 69abb7124f25 |
| E5-22-AC02 | 5.22 AC2 — a pre-expiry extension, | 5.22-A/B | b0d5afca1ea5 |
| E5-22-AC03 | 5.22 AC3 — valid extension, | 5.22-A | a5696e08804b |
| E5-22-AC04 | 5.22 AC4 — early termination, | 5.22-C/D | 9d30a37658f8 |
| E5-22-AC05 | 5.22 AC5 — confirmed early termination, | 5.22-C | dfc4110c52ea |
| E5-22-AC06 | 5.22 AC6 — original approver still absent without valid cover, | 5.22-C; 5.28-A | 4cc5de6a099b |
| E5-22-AC07 | 5.22 AC7 — successful change, | 5.22-A/C | ecc5943c1ae2 |
| E5-22-AC08 | 5.22 AC8 — racing decisions/expiry/repeated confirmation, | 5.22-A/C | 247607c1b945 |
| E5-23-AC01 | 5.23 AC1 — an assignment reaches its end, | 5.23-A | f86b9b446a95 |
| E5-23-AC02 | 5.23 AC2 — return was authorized at setup, | 5.23-A | 212e3b47b1fe |
| E5-23-AC03 | 5.23 AC3 — a valid return destination, | 5.23-A | d3901813163f |
| E5-23-AC04 | 5.23 AC4 — no eligible return destination, | 5.23-A | 1bacba001bd2 |
| E5-23-AC05 | 5.23 AC5 — an extension, early end or newer reassignment, | 5.23-A | 4f0333d878f1 |
| E5-23-AC06 | 5.23 AC6 — interrupted or missed processing, | 5.23-A | def03d269564 |
| E5-23-AC07 | 5.23 AC7 — temporarily unavailable verification, | 5.23-A | 51a7af96f5a4 |
| E5-23-AC08 | 5.23 AC8 — actual responsibility or coverage changes, | 5.23-A | 595fc775d3a9 |
| E5-24-AC01 | 5.24 AC1 — outstanding approval work, | 5.24-A/B | b0b12332ee94 |
| E5-24-AC02 | 5.24 AC2 — a chosen recipient, | 5.24-A | 790744778138 |
| E5-24-AC03 | 5.24 AC3 — valid confirmation, | 5.24-A | 72d1c576319e |
| E5-24-AC04 | 5.24 AC4 — an effective permanent supervisor change, | 5.24-C/D/E/F | 6accac35a54e |
| E5-24-AC05 | 5.24 AC5 — an ineligible recipient or unavailable verification, | 5.24-A/C/E | 8f23e1f7a933 |
| E5-24-AC06 | 5.24 AC6 — successful transfer, | 5.24-A/C/E | 3d0d1a6cf20f |
| E5-24-AC07 | 5.24 AC7 — an unavailable primary Leave Manager, | 5.24-A | abe493f77897 |
| E5-24-AC08 | 5.24 AC8 — concurrent decisions, assignment changes or retries, | 5.24-A/C/E | 541194713468 |
| E5-25-AC01 | 5.25 AC1 — a request awaiting a decision under absence fallback, | 5.25-A | 2e909659f09d |
| E5-25-AC02 | 5.25 AC2 — the request is waiting, | 5.26-A; 5.27-A | afdf6c55068c |
| E5-25-AC03 | 5.25 AC3 — no final decision has been made, | 5.25-A | 06ae6edd41cf |
| E5-25-AC04 | 5.25 AC4 — the supervisor step is restored, | 5.25-A; 5.18-A | d7f849330188 |
| E5-25-AC05 | 5.25 AC5 — a valid final decision already completed under fallback, | 5.25-A | bbe24a9d5ab2 |
| E5-25-AC06 | 5.25 AC6 — an ineligible supervisor or unavailable return verification, | 5.25-A | 68452a7527a9 |
| E5-25-AC07 | 5.25 AC7 — successful return transition, | 5.25-A | 186f27f3639d |
| E5-25-AC08 | 5.25 AC8 — return processing races with a decision or is retried, | 5.25-A | 1e3e2e065376 |
| E5-26-AC01 | 5.26 AC1 — an unanswered currently required approval, | 5.26-A | 531d46340d4f |
| E5-26-AC02 | 5.26 AC2 — other workflow participants, | 5.26-A | 49995e5d3188 |
| E5-26-AC03 | 5.26 AC3 — transferred responsibility, | 5.26-A | 720921ed05ae |
| E5-26-AC04 | 5.26 AC4 — completed action or a request no longer awaiting approval, | 5.26-A | a3664dc68134 |
| E5-26-AC05 | 5.26 AC5 — a delivered reminder, | 5.26-A | 5eb1b8e0e275 |
| E5-27-AC01 | 5.27 AC1 — a currently required approval remains unanswered, | 5.27-A | 341bdec9976c |
| E5-27-AC02 | 5.27 AC2 — an escalated approval remains unresolved, | 5.27-A/B | 4d644f902261 |
| E5-27-AC03 | 5.27 AC3 — an escalated item, | 5.27-A/B | 50d6c504358e |
| E5-27-AC04 | 5.27 AC4 — resolution of the outstanding approval, | 5.27-A | 2cd8c9d62a6d |
| E5-28-AC01 | 5.28 AC1 — a known approval coverage gap, | 5.28-A/B | 8d5d0effda03 |
| E5-28-AC02 | 5.28 AC2 — coverage becomes unavailable after leave was approved, | 5.28-A/B | 54c636e0bb30 |
| E5-28-AC03 | 5.28 AC3 — a coverage issue, | 5.28-A/B | cf7a85e9eb47 |
| E5-28-AC04 | 5.28 AC4 — an authorized coverage exception, | 5.28-A/B | ae4b5f586af9 |
| E5-28-AC05 | 5.28 AC5 — changing circumstances, | 5.28-A/B | 5d07e5556296 |
| E5-29-AC01 | 5.29 AC1 — my leave history, | 5.29-A/B | a26c0710f22e |
| E5-29-AC02 | 5.29 AC2 — a selected year, | 5.29-A/B | f68d96c8b98d |
| E5-29-AC03 | 5.29 AC3 — a calendar or list entry identifying one request, | 5.29-B | f0032cbcd4ce |
| E5-29-AC04 | 5.29 AC4 — historical employment or rehire periods, | 5.29-A | ecb60f7b3dd2 |
| E5-29-AC05 | 5.29 AC5 — phone use, | 5.29-B | 9a126a69c376 |
| E5-29-AC06 | 5.29 AC6 — no records in the selected year, | 5.29-A/B | 7a566afbc329 |
| E5-30-AC01 | 5.30 AC1 — my request, | 5.30-A/B | 60e116f5ee8c |
| E5-30-AC02 | 5.30 AC2 — recorded approval decisions, | 5.30-A/B | 401efae181d2 |
| E5-30-AC03 | 5.30 AC3 — a request awaiting action, | 5.30-A/B | bda563a11003 |
| E5-30-AC04 | 5.30 AC4 — a rejected and resubmitted request, | 5.30-A/B | 3670b6cefa33 |
| E5-30-AC05 | 5.30 AC5 — an available employee action, | 5.30-A/B | 5f4e408561f3 |
| E5-31-AC01 | 5.31 AC1 — outstanding requests, | 5.31-A | 9065030c6167 |
| E5-31-AC02 | 5.31 AC2 — a request in either section, | 5.31-A | bf4ddfd32f50 |
| E5-31-AC03 | 5.31 AC3 — a completed request action, | 5.31-A | 9c69c33ce47e |
| E5-31-AC04 | 5.31 AC4 — one section fails to load, | 5.31-A | eb7f1f4d0a6b |
| E5-32-AC01 | 5.32 AC1 — completed components, | 5.32-A/B/C/D | c1c6dd4ba4df |
| E5-32-AC02 | 5.32 AC2 — employment, policy, balance or supporting-document changes, | 5.32-E/F/G/H | 76b761297adf |
| E5-32-AC03 | 5.32 AC3 — responsibility changes or scheduled work, | 5.32-I/J/K; 5.24 producer proof | 5db05bddde9e |
| E5-32-AC04 | 5.32 AC4 — competing actions or interrupted operations, | 5.32-L; actual producer race/rollback proof | f7fb1d6b2b67 |

## Required next C6 work

1. Split composite Then/And obligations into exact leaf evidence obligations where needed;
   identify one primary implementation/test owner per leaf, plus reference versus real
   producer/browser integration. Preserve approved behavior; do not duplicate common guards,
   calculators, E4 pipeline, receipt recovery or reminder processing across stories.
2. Expand 5.15's generic criteria through all eleven API/browser source families and their
   initial assignment/rehire/reference writer variants. A repeated general sentence is not
   evidence every actual writer is protected. Carry the C3 source register forward.
3. Verify foundational scopes and residual 5.8 against exact contracts; include real base
   work in the graph. Reconcile generated 5.10-A/C and 5.8-A support without pretending a
   synthetic fixture completes actual submission/source integration.
4. Check late accepted refinements explicitly: current People transfer/temporary precedence,
   same-person decision, employee-only withdrawal, notification-only later unpaid changes/
   zero-unpaid initial-response closure, separate medical permission and current-team/
   approved-versus-pending projection. Historical phrasing must not revive superseded rules.
5. Reconcile original 5.32 four broad criteria with actual 12 journey owners and each source/
   transfer producer proof. Representative journey coverage is not all-writer or concurrency
   coverage. Cross-org/access-loss/unknown outcome and real transaction rollback remain
   primary owner evidence even when a journey references them.
6. Extend the 80-node mechanical candidate graph with the real foundation and external
   predecessor work. Inspect actual KDG/Access/client/Auth delivery and credit existing
   slices. Recheck cycles and activation dependencies; an acyclic partial graph is not
   semantic delivery readiness.
7. Size final actual items for one dev agent only after ownership/order is concrete. Any
   material split/merge/scope choice returns to the user; routine traceability corrections
   do not require re-reading already approved story text. Do not start E6 until the E5
   completion summary and explicit user agreement.

The artifact/command map owns existing versus planned executable checks. No runtime tests
were run or test files invented in this inventory. Requirement inventory extraction beyond
these original E5 criteria, cross-cutting FR/NFR/UX coverage, final evidence allocation and
readiness remain open. This audit is a BMAD planning evidence supplement, not a competing
feature specification or delivery workflow.

## C6 pass 2 — funding and actual source-change ownership

This allocation supersedes the broad candidate links for original 5.8 and 5.15 only.
It establishes planning ownership/evidence obligations, not executed tests or final overall
coverage. Other original criteria, refinements and cross-cutting requirements remain for
subsequent passes. No new business requirement, boundary or generic engine is introduced.

### Original 5.8 detailed obligation allocation

| Leaf ID / source | One primary owner of implementation/evidence | Actual additional consumer evidence, not another implementation |
| --- | --- | --- |
| FND-01 / AC1 valid date-effective entitlement | E3 3.18 date-by-date allocator | 5.11-A own, 5.12-A on-behalf and 5.20-A resubmit pass actual employee/current cycle inputs |
| FND-02 / AC2 later earning cannot repair earlier shortfall | E3 3.18 forward candidate allocation | Actual submit producer retains ordered evidence; do not recreate earning logic in the handler |
| FND-03 / AC2 no double use across candidate dates | E3 3.18 portion conservation | 5.8-A accepts only protected actual allocation and links its commitment |
| FND-04 / AC3 remaining availability protects prior reservations | E3 3.18 selection with other commitments | 5.8-A proves actual serialized reserve versus competing requests, not a second allocator |
| FND-05 / AC4 expiry/original-period/stable identity order | E3 3.18 under L-0129 and E3 evidence contract | 5.8-A persists actual selected portion refs; source-impact owners verify their actual changed inputs |
| FND-06 / AC4 no automatic cross-type borrowing | E3 3.18 ordinary allocation restriction | 5.13-A alone applies explicitly authorized permitted exceptional alternatives |
| FND-07 / AC5 exact funded/shortfall classification inputs | E3 3.18 normalized result and policy evidence | 5.11-A first ordinary input/result classification adapter; 5.12/20 consume same rules with real contexts |
| FND-08 / AC5 displayed paid/requested-unpaid and progression | 5.11-B first own review presentation | 5.12-B employee-target review and 5.13-B exception review prove their actual values/action gates; no duplicated form/calculator |
| FND-09 / AC5 shortfall is not exception or approved unpaid | 5.11-A protected ordinary submission classification/gates | 5.12-A initial employee obligation and 5.13-A explicit exception authority; B finalizer remains independent |
| FND-10 / AC6 untracked result has actual classification, no invented shortfall | E3 3.18 untracked branch | 5.11/12-B show Not balance-limited under actual normalized result |
| FND-11 / AC6 untracked creates no entitlement commitment | 5.8-A protected tracked/untracked distinction | Actual 5.11/12/20 and 5.10-B prove no fabricated reserve/consume lines while other gates still apply |
| FND-12 / AC7 current protected funding through commit | 5.8-A actual employee/dependency/commitment foundation | 5.11-A/12-A/20-A each prove their own actual input/revision/race envelope; 5.13-A reviewed replacement remains distinct |
| FND-13 / AC7 renewed materially changed review/exact initial acknowledgement | 5.11-A own submission comparison | 5.12-A/B actual on-behalf handoff, 5.20-A/B fresh cycle and employee response handle their existing rules; later same-cycle change is L-0151 notice only |
| FND-14 / AC8 verification failure is not zero/eligible/untracked | E3 3.18 typed read/calculation failure | 5.11-B, 5.12-B and 5.20-B preserve actual input and show Retry; 5.8-A/5.10-B cannot consume a failed observation |

**Residual conclusion:** The original 5.8 product scope is covered by these existing
algorithm/foundation/producer/presentation responsibilities. It is not an extra standalone
funding engine or another executable unsuffixed parent. Retain original source criteria for
traceability. Actual first-use classification/adapters remain part of normal submit scope,
not hidden inside 5.8-A's reserve/consume/release foundation. Final size/order still must
verify that those producer boundaries are bounded with these known obligations.

### Original 5.15 detailed obligations applied through each source family

`API(F)` and `Browser(F)` below resolve to one concrete pair in the next table, not a new
common service. Shared primitives/fixtures can be reused or parameterized, but every real
source adapter must prove its promised effects. A generic calculator unit test is never
all-writer integration proof.

| Leaf ID / source | Primary owner for each concrete family | Required evidence boundary / existing reuse |
| --- | --- | --- |
| IMP-01 / AC1 discover exact affected set | API(F) actual source adapter | Both request-date and funding-history paths; actual old/new reference membership protected |
| IMP-02 / AC1 truthful before/after review | Browser(F) with API(F)'s typed projection | Actual authorized selected requests and consequences, no silent page truncation or empty-on-failure |
| IMP-03 / AC2 current source/consequence authority | API(F) | Existing Access/People checks reused; no grant from manager label or service key |
| IMP-04 / AC2 employee-visible explanation | Browser(F) | Existing reason control required; actual API validates and records it, not just client checks |
| IMP-05 / AC2 actual actor/reason/effect evidence | API(F) | Actual owning audit/evidence + source/request writes in declared owner transaction |
| IMP-06 / AC3 previous/revised values and authorized detail link | Browser(F) | Current real result/detail, actor/reason; no sensitive-document content |
| IMP-07 / AC3 required employee notification intent | API(F) | E3 outbox/current-recipient primitive reused with actual source producer proof |
| IMP-08 / AC3 no renewed same-cycle response gate | API(F) | L-0151 actual increase AND decrease; read notice never creates consent |
| IMP-09 / AC3 existing initial response retained or closes at zero | API(F) | Actual 5.12 obligation; L-0162 zero closure/no later reopen, valid prior human decisions retained |
| IMP-10 / AC3 no new discussion/consent checkbox | Browser(F) | Existing explanation/notice UX; no extra proxy-ack/referral UI |
| IMP-11 / AC4 retained valid decisions/history | API(F) | Actual current request/cycle refs; original immutable evidence not overwritten |
| IMP-12 / AC4 no automatic reject/cancel/trim/grant | API(F) | Each unresolved condition preserved; actual separately authorized remedy can resolve it |
| IMP-13 / AC4 unresolved detail/manager attention projection | API(F), common minimum read first 5.15-A | Source producer updates retained current issue evidence; minimum pending-request issue attention is not deferred to E6 or later dashboard |
| IMP-14 / AC5 independent invalid eligibility still blocks finalization | API(F) source consequence | 5.7 actual validity and 5.10-B independent gate reused; allocated notice/response is not a waiver |
| IMP-15 / AC6 actual remedy permission | Actual remedy handler (5.13-A, source owner or later authorized E6 correction) | API(F) supplies no implicit authority; Browser(F) links only existing permitted actions |
| IMP-16 / AC6 existing human coordination, no permission transfer/referral flow | Browser(F) | Preserve current source/detail entry and useful return context |
| IMP-17 / AC7 protected current source/request/allocation/revision effects | API(F) | Actual source mutation versus approve/respond/withdraw and reference-holder races |
| IMP-18 / AC7 original recovery/no repeated effects | API(F) | Reuse 5.10-C or actual People source outcome; Browser(F) distinguishes confirmed success from failed refresh |
| IMP-19 / AC7 failed impact verification not no affected requests | API(F) | Failure leaves actual source/request promised state unchanged, or truthful cross-owner pending recovery under P-0062 |
| IMP-20 / AC8 expected time passage/projection unchanged | E3 3.17-A/3.18 rules, API(F) actual source integration | No daily earning posting or surprise unpaid increase from time alone; deliberate source corrections use their real reviewed consequence path |

### Eleven actual source families and concrete producer variants

| Family | API(F) / Browser(F) | Actual source variants that require integration evidence |
| --- | --- | --- |
| F01 one-off balance | 5.15-A / 5.15-B | Existing 3.29 Add AND Deduct, actual date/reason/event order, zero/changed pending impacts, later funding reachability |
| F02 recurring entitlement | 5.15-C / 5.15-D | Existing 3.30 change explicit recurring value AND return to policy; retain source period/override provenance |
| F03 used policy publication | 5.15-E / 5.15-F | Actual 3.34 used-policy publish, all applicable source transitions/effective intervals under retained request policy rules |
| F04 scheduled policy | 5.15-G / 5.15-H | Actual 3.35 amend AND cancel scheduled change, not a second publish path; superseded schedule/current boundaries |
| F05 employee policy assignment | 5.15-I / 5.15-J | Actual 3.28 initial assignment and 3.36 change/end, including relevant existing pending work and verified truly empty initial case |
| F06 employment periods | 5.15-K / 5.15-L | Actual 2.12 end, 2.13 period-add/rehire and 2.11 genuine initial employee precondition; People attempt prepare/commit/cancel/reconcile, no cross-owner rollback |
| F07 employee work overrides | 5.15-M / 5.15-N | Actual 2.22 override/reset, explicit value equal to inherited versus genuine inheritance, timezones/calendars/standard-day and partial fields |
| F08 employee work profile | 5.15-O / 5.15-P | Actual 2.20 initial/change/end selection, explicit profile versus default users and old/new dated reference membership |
| F09 organization default | 5.15-Q / 5.15-R | Actual 2.21 empty-to-default/change, actual fallback users and partial overrides, concurrent explicit selection/reset |
| F10 shared work profile | 5.15-S / 5.15-T | Actual 2.23 publication, explicit holders/default followers/partial overrides and new holder races; unused 2.19/24 create/archive retain narrow no-holder proofs |
| F11 holiday calendar | 5.15-U / 5.15-V | Actual 2.18 add/edit/remove, previously absent entry, full/partial closure, direct/profile/default users and later earning/funding consequences |

Common oracle identifiers are family-qualified (for example F05/IMP-17), not a claim of
220 separate test files or executed test results. Factor shared fixtures/assertions, while
retaining each actual source variant's protected consumer test. Evidence outside family
scope is a reference to its owner; do not rerun all generic mechanisms under every family.

Type create/deactivate/restore/metadata, Access/member changes, request lifecycle, appointment/
transfer/return, supported imports and no-write time boundaries retain their C3 register
rows and separate actual owner proofs; they are not falsely covered by the eleven-row
5.15 matrix. Their detailed residual reconciliation remains part of later C6 passes.

### Contract gap resolved: pending-request source issues in manager attention

IMP-13 exposed an allocation gap: original 5.15 AC4 requires current unresolved detail and
manager attention, but the bound E5 attention read union named only escalation and coverage.
Assign the minimum `pending_request_issue` read branch/current issue evidence to **5.15-A**,
the first actual local source-impact integration, and its usable minimum existing-attention
presentation/detail entry to **5.15-B**. All later API(F)/Browser(F) producers reuse that
read/presentation and prove their own actual issue update/clear. This makes an existing
approved obligation concrete; no extra permission, dashboard, issue engine or story.

The contract extension below is a delivery allocation correction, subject to final sizing.
If the minimum read/presentation makes that first source family exceed one-agent scope,
raise a concrete split before readiness rather than hiding this work in a later story.
5.27/28 extend their actual escalation/coverage branches and preserve this earlier branch.
E6 retains approved/ongoing/past correction or deficit workflows; it does not own the first
pending issue display required for safe source integration.

### Current pass limits and next work

Original 5.8/5.15 obligations now have detailed implementation versus presentation/producer
allocation, including all 11 concrete source families. This is not final coverage for all
230 source criteria. Next inspect seven foundational rule scopes and late-refinement
ownership, then actual remaining mutation/display/proof obligations and external graph.
No runtime tests or source implementation performed; original 230-criterion hashes remain
unchanged by this planning-only allocation.

## C6 pass 3 — seven foundation scopes and later accepted refinements

All **53 source criteria** from 5.1/2/3/4/6/7/9 are reconciled below. Rule implementation,
actual domain transition and presentation/integration are explicitly distinguished. This
is detailed planning allocation, not 53 executed tests or final single-agent sizing.

The seven scope labels are not yet seven approved executable units. Final boundary/size
assessment must count their actual owner-client/rule/minimum-feedback work. Where a source
criterion combines a rule with another owner's mutation, the rule does not duplicate that
transition; the actual mutating owner retains it. Existing foundation previews must include
their required minimal feedback on the already existing draft/review surface, using E1
preservation patterns, rather than leave an invisible result until a future display story.
No independent setup wizard, new team system or parallel request form is introduced.

| Source criterion | Obligations reconciled | Primary core/effect owner | Actual other-owner/producer/presentation evidence |
| --- | --- | --- | --- |
| E5-01-AC01 | One-step configured principal; relationship alone is not authority | 5.1 route resolution; Access owns effective grant | 5.11-A resolves current submission route; 5.18-A proves actual current assigned authority |
| E5-01-AC02 | Two-step supervisor plus configured final; no dropped step/assumed CEO | 5.1 ordered configured-position projection | 5.11/12-A record real steps; 5.18-A and 5.10-B enforce them |
| E5-01-AC03 | Definite setup issue, authorized setup assessment and useful draft feedback | 5.1 minimum route/setup projection and existing draft feedback | E1 remains owner of preserved input/Draft saved; 5.11-A refuses invalid route |
| E5-01-AC04 | Unavailable owner is verification failure, not missing/valid configuration | 5.1 owner-observation classification and retry feedback | Actual People/Access adapters; E1 preservation unaffected; submit handler proves no unverified route |
| E5-01-AC05 | Self and consecutive same-person configured responsibility rules | 5.1 configured route validation/projection | 5.11/12-A permitted own decision; 5.18-A actual L-0158 decision set; 5.10-B all required gates |
| E5-01-AC06 | Route setup versus absence/coverage are different results | 5.1 route result classification | 5.2 selected cover, 5.4 fallback and 5.3 applicant coverage own their actual conditions |
| E5-01-AC07 | Concise requester summary, no approver absence/cover leakage | 5.1 minimum requester projection and existing draft feedback | 5.11-B review uses same projection; 5.30 formal permitted history stays separate |
| E5-01-AC08 | Provisional check has no grant/reserve/submitted assignment effects | 5.1 side-effect-free route observation | 5.11-A actual cycle/steps; 5.24-C/E actual later supervisor transfer; original final/decisions retained |
| E5-02-AC01 | Chosen same-org active member; no permanent Approver or Org Admin-derived appointment right | 5.2 selected-member eligibility rule | 5.21-A create and 5.22-A extend check current management/action scope; Access context supplies no permanent grant |
| E5-02-AC02 | Exact principal/responsibility/interval, including authorized final duty | 5.2 typed scoped eligibility input/result | 5.21-A actual stable configured responsibility plus principal binding, not arbitrary role/step selection |
| E5-02-AC03 | Known absence/inactive member/self-conflict is invalid for exact affected scope | 5.2 conflict classification | 5.21/22-A actual source/interval checks; 5.18-A per-request self/distinct-person gate |
| E5-02-AC04 | Overlapping same-duty appointment is conflict; sequential cover valid | 5.2 interval overlap rule | 5.21-A protected actual create race and 5.22-A extension race; no automatic substitute |
| E5-02-AC05 | Only effective exact appointment scope, no rights after expiry | 5.2 scope/time predicate | 5.2 owns first actual appointment storage/current interval reads; 5.23-A owns expiry/current deny; 5.18-A actual decision consumer |
| E5-02-AC06 | No unrelated role/on-behalf/medical rights from appointment | 5.2 bounded authority projection | Actual Access/Leave action consumers deny those independent actions; E4 document permission remains owner |
| E5-02-AC07 | Failed membership/absence verification versus verified no absence | 5.2 verification result and selected-member retry feedback | 5.21/22 browser preserves input; API refuses confirmation without required verified eligibility |
| E5-03-AC01 | Verified no responsibilities means coverage not applicable | 5.3 complete responsibility enumeration/result | 5.10-B consumes not_applicable only from actual verified evidence |
| E5-03-AC02 | All duties across applicant absence, including incoming work | 5.3 configured-responsibility scope enumeration | People/configuration source writers protect scope; 5.10-B actual applicant-coverage gate |
| E5-03-AC03 | Union of eligible sequential cover intervals and exact remaining gaps | 5.3 interval composition | 5.21/22/23 actual producer/source change; 5.28-A actual gap projection |
| E5-03-AC04 | Configured directional fallback counts, including eligible temporary final | 5.4 primary fallback predicate; 5.3 composition uses it | 5.18-A actual final actor; 5.10-B finalization; L-0146 requires no extra appointment flag |
| E5-03-AC05 | Known gap allows otherwise valid submission but blocks final completion absent exception | 5.3 action-stage coverage result | 5.11/12/20-A actual accepted pending gap; 5.10-B every completion path; 5.5-A bounded exception |
| E5-03-AC06 | Exception recorded is distinct from covered and grants no other authority | 5.3 result classification | 5.5-A actual reasoned exception; 5.28-A gap remains visible |
| E5-03-AC07 | Unknown coverage is neither complete nor proven gap; Retry | 5.3 typed verification failure | 5.10-B cannot finalize from failed check; actual supporting presentation cannot show false cover |
| E5-03-AC08 | Lost cover after approval preserves approval and exposes replacement need | 5.3 reassessment result | Actual appointment/source writers preserve approved state; first actual gap producer retains evidence; 5.28-A/B residual attention |
| E5-03-AC09 | Human-selected arrangements, no automatic ranking or applicant appointment requirement | 5.3 gap explanation/projection | 5.21-B person-first appointment UI; 5.11-B does not send applicant chasing approving staff |
| E5-04-AC01 | Disabled absence policy retains every required step | 5.4 required-step predicate | 5.18-A actual action and 5.10-B current completion check |
| E5-04-AC02 | Enabled supervisor-absence fallback omits step as not required, not approved | 5.4 required-step/omission result | 5.18-A actual decision/step attribution; current/historical detail keeps omission distinct |
| E5-04-AC03 | Supervisor cannot substitute for absent final approver | 5.4 directional restriction | 5.18-A denies wrong actor/path; 5.21-A supplies only explicitly appointed valid final duty |
| E5-04-AC04 | Both absent: eligible temp final uses original policy with no added checkbox | 5.4 actual configured fallback rule | 5.2/5.21 scope eligibility and 5.18-A actor decision; independent gates 5.10-B |
| E5-04-AC05 | Approver absence at action time, not applicant future dates/slow response | 5.4 temporal predicate | 5.18-A/5.10-B fresh current action; actor/subject guards and source protocol protect actual observation |
| E5-04-AC06 | Unfinished return restores required step; keep decisions/timers; separate temp expiry | 5.25-A actual supervisor-return transition | 5.4 defines no ended-absence waiver; 5.23-A temporary expiry; 5.26/27 clocks; no repeated return implementation here |
| E5-04-AC07 | At least one valid approval and all independent gates | 5.10-B all-gate finalization | 5.4 supplies only current required-step set; 5.18-A actual actor authority; other rules not waived |
| E5-06-AC01 | Only type-permitted full/half/hour mode | 5.6 request-duration validation | E3 type/date metadata owner; 5.11/12/20-A actual selected-mode input checks |
| E5-06-AC02 | Mixed range valid; working-only duration; zero eligible/invalid range blocked | E3 3.7 authoritative duration, 5.6 adapter/result | 5.6 minimum existing draft feedback; 5.11/12/20 actual range producer; never force weekend splitting |
| E5-06-AC03 | Half scheduled day, including 450 -> 225 minutes without 30-minute rounding | E3 3.7 half-day calculation | 5.6 selected-mode validation; actual submit/resubmit retains exact integer result |
| E5-06-AC04 | Hourly one date/positive 30-minute increments/no exact times | 5.6 request-input validation | Existing E3 schedule/duration; actual input screens and handlers share accepted fields |
| E5-06-AC05 | Warn and total active same-date leave across types; correct included states | 5.6 active-duration/capacity query | 5.11/12/20 actual producers; current state changes actual owners update included work |
| E5-06-AC06 | Within schedule permits, over schedule blocks; no fixed eight hours/count limit | 5.6 capacity rule | Actual source schedule/projection and 5.11/12/20-A protected current consumer |
| E5-06-AC07 | Concurrent submissions cannot jointly overfill the absence date | 5.8-A shared employee/dependency protection, actual producer 5.11-A | 5.6 supplies rule; 5.12/20-A prove their actual command integration, no extra duplicate guard |
| E5-06-AC08 | Validation/unverified schedule preserves input, no false no-conflicts result | 5.6 typed result and minimum existing draft feedback | E1 draft preservation; actual submit/resubmit browser/API handles same result, not zero fallback |
| E5-07-AC01 | Explicit applicable policy/employment, no department/location inference | 5.7 date-eligibility predicate | Actual E3 assignment and People facts; 5.11/12/20-A current input consumer |
| E5-07-AC02 | Inclusive employment end, no later dates or silent trimming | 5.7 date rule | 5.11/12/20-A submit and 5.10-B finalize; 5.15-K source change preserves truthful blocker |
| E5-07-AC03 | Every date within inclusive advance window, default twelve months | 5.7 whole-request date rule | Actual submission/review consumers; existing effective policy/work-timezone inputs |
| E5-07-AC04 | Short notice needs explanation/flag, not blanket ban; zero default same-day allowed | 5.7 notice result | Existing draft reason/flag feedback; actual 5.11/12/20 input/handler; 5.16 queue flag |
| E5-07-AC05 | Backdated needs reason/lateness/historical inputs, no fixed cutoff/new admin route | 5.7 historical-date result | E2/E3 historic work/policy owner; actual 5.11/12/20 source and review |
| E5-07-AC06 | Current consequential input recheck/review without replacing retained policy | 5.7 current eligibility observation | Each actual owning handler protects/compares before commit; 5.15 source variants and 5.10-B recheck |
| E5-07-AC07 | Definite missing setup versus unavailability; keep authorized draft saving | 5.7 typed result and minimum existing draft feedback | E1 retains independent lightweight save; submit may fail but cannot erase input |
| E5-09-AC01 | Exact document policy threshold: above two != exactly two | 5.9 document-rule predicate | Actual E3 policy/duration; current submit/finalizer consume same threshold rule |
| E5-09-AC02 | Required attachment must be confirmed association and verified ready content | 5.9 policy/readiness adapter | E4 4.4 owns real association/cleanup; actual 5.11/12/20-A bind target refs |
| E5-09-AC03 | Missing/pending/rejected/failed required evidence blocks submission, preserves input | 5.9 classified gate and minimum existing feedback | Actual 5.11/12/20 producer/browser; E4 source semantics reused, no upload pipeline here |
| E5-09-AC04 | Unverified status means Retry, not missing/ready; draft saving independent | 5.9 verification result | E4 current owner observation; E1 preservation remains independent |
| E5-09-AC05 | Finalization rechecks required readiness independently of preview/decision | 5.10-B current document gate | 5.9 adapter and actual E4 lifecycle protection; 5.18-A actual command producer |
| E5-09-AC06 | Ordinary approver/manager sees safe status, medical metadata/bytes need explicit right | E4 4.7 current document read authorization | 5.9 safe status projection; 5.16/18/30 actual audience/API/UI no sensitive leak; no default role grant |
| E5-09-AC07 | Retain content identity/protection; no human-inspection gate; later authorized history only | E4 4.4/4.7/4.13 actual association/read/retention | 5.9 no new medical-validation state; 5.11/12/20 actual cycle link continuity and 5.32-H integration, E6 separately authorized corrections |

### No-forward-dependency interpretation for final execution

- 5.1 supplies current configured route/responsibility projection and minimum existing
  draft feedback independently of a public Submit command. Actual 5.11/12/18 consumers
  later prove their mutations once. Provisional observations reserve/grant nothing.
- 5.2 supplies selected-member/interval eligibility. Typed appointment projections can
  exercise its rule independently; actual appointment storage/current expiry enforcement
  is first introduced by 5.23-A and its real producer/decision consumers. A synthetic
  interval test alone is never claimed as actual expired-authority integration proof.
- 5.4 directional fallback predicate precedes 5.3 composition. Its wording about restore,
  timers and all-gate completion references the actual 5.25/26/27/10-B owners; it does not
  require those future mutations merely to decide the configured required-step set.
- 5.3 enumerates configured duties/principal scope and composes actual typed cover/fallback
  observations. It grants no appointment and performs no request finalization. First
  actual gap producer must retain minimum truthful issue evidence; 5.28 enriches the
  existing manager attention surface and cannot be the first safety condition after activation.
- 5.6/5.7 use actual E2/E3/People inputs and minimum existing form feedback. E3 owns duration
  arithmetic; actual submissions own current protected commits. Distinguish pure read
  previews from capacity concurrency under real guard/employee transactions.
- 5.9 consumes actual E4 verified association/readiness policy. It implements no bytes,
  upload, cleanup or document reading permission and no human medical-inspection gate.

These directions preserve the original approved responsibilities but still need final
executable allocation and sizing. Do not mark a foundation complete with synthetic inputs
when its promised owner HTTP/projection/minimum-feedback is missing, or make its public
consumer silently depend on a later actual source writer. Full graph reconciliation is
still required; this table alone is not a proof of acyclic deployable order.

### Later accepted decision-to-owner/evidence reconciliation

| Accepted decision | Actual implementation owner(s), with one mechanism per responsibility | Specific composition/refinement evidence |
| --- | --- | --- |
| L-0146 temporary final follows existing absence policy | 5.4 predicate; 5.2 scoped eligibility; 5.21 actual appointment; 5.18 actual decision | Both usual approvers absent, policy on/off, no extra fallback checkbox or permanent role |
| L-0147 current supervisor transfer / actual attribution | People P-0062 source; 5.24-C/E transfer; actual decision history 5.18/30 | Disclosed source effect, only unfinished supervisor work; completed/final decisions retained, no duplicate reassignment history engine |
| L-0148 simple Retry / original outcome first | E1 receipt then 5.10-C request extension | Actual 5.11/12 and other mutations recover same operation/input; no Check status technical UI or new operation on unknown |
| L-0149 standard Approver explicit on-behalf default | Access catalog/role consumer and 5.12-A | Custom approval-only and temporary-only do not inherit; no role-name authorization |
| L-0150 one exceptional funding capability / combined confirmation | 5.13-A one protected allocation/optional decision envelope | No per-line grant; current actual approval needed for combined path; funding-only is not human approval |
| L-0151 later paid/unpaid notice only | 5.13-A and each actual 5.15 API(F) | Increase/decrease preserve prior/revised values/reason/notice; no renewed same-cycle acknowledgement |
| L-0152 approved cancellation defaults | E6 owns actual cancellation/correction; E5 stores only needed stable history/lifecycle | Recorded agreement is not E5 on-behalf/temporary permission to cancel; started/future E6 details remain open |
| L-0153 standard manager reassignment | Access catalog/default consumer and 5.24-A | Explicit granted action, restricted custom role can omit, separate current eligible target/reason |
| L-0154 last gate resolution triggers finalizer | 5.10-B kernel; real resolving command/source/timed owner invokes it | Retained valid decisions, no Complete button/read-side finalization or generic approval polling |
| L-0155 recurring reminders / one escalation | 5.26-A recurrence and 5.27-A escalation | Same unanswered action, 3/7 calendar-day defaults, continued reminders after single manager escalation |
| L-0156 same-step waiting survives transfer | Actual 5.24 and 5.21–25 transition owners; timed clock interface | Immediate recipient assignment notice, retained waiting clock/escalation; different first-actionable step has own clock |
| L-0157 one missed-run catch-up / retained outbox | 5.26-A occurrence with actual E3 handover | Latest missed due slot only, original pending/uncertain identities retained, no shared delivery domain calculation |
| L-0158 one decision for permitted consecutive same-person positions | 5.1 configured route, 5.18-A actual decision-set link | Exact covered steps, one actual decision, distinct-person/self rules, no second Approve or silent subset |
| L-0159 rejected correction preservation | 5.20-A correction/current cycle/state and 5.20-B form | Separate ordinary draft untouched; closed correction cannot resurrect; explicit resubmit creates fresh cycle |
| L-0160 permanent supervisor supersedes matching temporary scope | 5.24-C/E People transfer and 5.23/25 current return precedence | Replacement gets unfinished supervisor work; unrelated cover/final work retained; stale expiry cannot return to former supervisor |
| L-0161 employee-only pending withdrawal | 5.19-A handler and 5.19-B UI | On-behalf origin does not allow proxy withdrawal; approver rejects with visible reason under its actual authority |
| L-0162 initial unpaid reaches zero | 5.10-B minimum response model/predicate; 5.12-A production response; actual 5.13/15 allocation writer | Close as not needed with actual source actor, no fake employee consent or later same-cycle reopening; fresh cycle uses initial rules |
| L-0163 protected authority instant at supervisor boundary | Real protected 5.18/24/10-B action and P-0062 source integration | Check before boundary may finish bounded local transaction; at/after uses replacement. No grace for temp expiry or Access denial; restart fresh check |
| L-0164 on-behalf target population | Access resource branch and 5.12-A lookup/submit | Normal configured population versus explicit org administrative scope; no widening from temporary/fallback/history |
| L-0165 manual selected reassignment outcomes | 5.24-A per-request atomic command, 5.24-B selected-item orchestration | Valid successes retained, unknown original IDs recover; do not copy semantics to source or appointment batches |
| L-0166 current team for advisory availability | 5.17-A actual People current-group query | Requested-date absence intersection, future supervisor schedule not projected; no expanded temporary/read authority |
| L-0167 approved versus pending availability | 5.17-A inclusion/count and 5.17-B labels | Current cycle/state, excluded negative/draft/self, unique people with distinct approved/pending categories |
| P-0060 application-owned pending supervisor transfer | People owns facts; 5.24-C/E owns Leave unfinished-step consequences | No cross-service SQL, preserved actual decisions/final choice and current user authority |
| P-0062 prepared People source change coordination | Actual People/Leave owner adapters under source protocol | Prepare/commit versus cancelled fence, no TTL gate release/distributed rollback; org disable retains restricted recovery |
| P-0063 internal People Access registration | Existing Access registry/admission commands reused; People current check consumer added | No extra app tile/customer setup or role-name grant; Leave disable independent, KDG-specific check is not People implementation |

Earlier medical visibility decisions and saving conventions remain required through 5.9/
E4 and E1/correction owners above. The late-decision table is not a replacement FR/NFR/UX
inventory or acceptance signature. Future cancellation scope stays E6; existing evidence
is referenced without creating a duplicate E5 feature.

### Progress and remaining allocation

53 foundation source criteria and the 22 accepted Leave L-0146–0167 refinements now have
explicit core/effect/consumer allocation, with three related platform decisions linked.
The seven foundation scopes still need final executable boundaries and actual sizing;
no automatic change to the 80 suffixed count. Next reconcile actual remaining command/
display/journey ownership and non-5.15 C3 writer variants, then whole-graph/external
predecessor and cross-cutting requirement coverage before final sizes and epic completion.
No source code, tests, grants, migrations or runtime implementation performed.

## C6 pass 4 — remaining command, display and journey ownership

The **remaining 161 original source criteria** are allocated below, bringing detailed
source-criterion ownership to **230/230**. This is owner allocation, not final atomic
requirement coverage, completed tests, approved executable count or readiness. Each
compound criterion's domain/current-read/effect and presentation/integration obligations
are explicitly separated. When a row references multiple real producers, each retains
its actual promised command test; no composite A/B row is a new executable story.

| Source criterion | Primary domain/read/effect owner | Primary presentation or additional actual composition proof |
| --- | --- | --- |
| E5-05-AC01 | 5.5-A | 5.5-B |
| E5-05-AC02 | 5.5-A | 5.5-B |
| E5-05-AC03 | 5.10-B | 5.5-B |
| E5-05-AC04 | 5.5-A; 5.28-A | 5.5-B; 5.28-B |
| E5-05-AC05 | 5.5-A | 5.5-B |
| E5-05-AC06 | 5.5-A; 5.3 | 5.5-B |
| E5-05-AC07 | 5.18-A | 5.5-B |
| E5-10-AC01 | 5.10-B | Actual result consumer |
| E5-10-AC02 | 5.10-B | Actual result consumer |
| E5-10-AC03 | 5.10-B | First minimum own/assigned result |
| E5-10-AC04 | 5.10-B | 5.12-B |
| E5-10-AC05 | 5.12-A; 5.10-B | 5.12-B |
| E5-10-AC06 | 5.10-B | Actual confirmed-result consumer |
| E5-10-AC07 | 5.10-B | Actual mutation browser |
| E5-10-AC08 | 5.10-B | Actual Retry consumer |
| E5-11-AC01 | 5.11-A review | 5.11-B |
| E5-11-AC02 | 5.11-A exact input | 5.11-B |
| E5-11-AC03 | 5.11-A | 5.11-B changed review |
| E5-11-AC04 | 5.11-A | 5.11-B confirmed result |
| E5-11-AC05 | 5.11-A; 5.10-B | 5.11-B |
| E5-11-AC06 | 5.11-A minimum read | 5.11-B |
| E5-11-AC07 | 5.10-C; 5.11-A | 5.11-B |
| E5-11-AC08 | 5.11-A | 5.11-B |
| E5-12-AC01 | 5.12-A target/scope | 5.12-B |
| E5-12-AC02 | 5.12-A employee context | 5.12-B |
| E5-12-AC03 | 5.12-A review | 5.12-B |
| E5-12-AC04 | 5.12-A | 5.12-B |
| E5-12-AC05 | 5.12-A | 5.12-B |
| E5-12-AC06 | 5.12-A response creation | 5.12-B employee response |
| E5-12-AC07 | 5.12-A; 5.10-B | 5.12-B |
| E5-12-AC08 | 5.12-A | 5.12-B first minimum My Leave |
| E5-12-AC09 | 5.10-C; 5.12-A | 5.12-B |
| E5-13-AC01 | 5.13-A preview | 5.13-B |
| E5-13-AC02 | 5.13-A authority | 5.13-B |
| E5-13-AC03 | 5.13-A source effects | 5.13-B |
| E5-13-AC04 | 5.13-A conservation | 5.13-B |
| E5-13-AC05 | 5.13-A combined envelope | 5.13-B |
| E5-13-AC06 | 5.13-A L-0151/0162 | 5.13-B |
| E5-13-AC07 | 5.10-C; 5.13-A | 5.13-B |
| E5-14-AC01 | 5.12-A notice/obligation | 5.12-B first response entry |
| E5-14-AC02 | Actual 5.13/15 allocation writer | 5.13/15-B-family revised detail |
| E5-14-AC03 | 5.12-A employee action | 5.12-B |
| E5-14-AC04 | 5.12-A current amount | 5.12-B changed response |
| E5-14-AC05 | 5.12-A invokes 5.10-B | 5.12-B confirmed result |
| E5-14-AC06 | E3 3.26 read state; 5.12-A business response | 5.12-B |
| E5-14-AC07 | 5.19-A | 5.19-B from response view |
| E5-14-AC08 | 5.12-A; 5.10-C | 5.12-B |
| E5-16-AC01 | 5.16-A | 5.16-B |
| E5-16-AC02 | 5.16-A | 5.16-B |
| E5-16-AC03 | 5.16-A current scope | 5.16-B safe refresh |
| E5-16-AC04 | 5.16-A privacy projection | 5.16-B |
| E5-16-AC05 | 5.16-A query/order | 5.16-B controls |
| E5-16-AC06 | 5.18-A minimum + 5.16-A residual read | 5.16-B inspection |
| E5-16-AC07 | 5.16-A typed collection result | 5.16-B states/Retry |
| E5-16-AC08 | Existing detail identity/read | 5.16-B navigation |
| E5-17-AC01 | 5.17-A current group | 5.17-B |
| E5-17-AC02 | 5.17-A inclusion/count | 5.17-B |
| E5-17-AC03 | 5.17-A dates only | 5.17-B timeline/list |
| E5-17-AC04 | 5.17-A per-date extent | 5.17-B labels |
| E5-17-AC05 | 5.17-A field privacy | 5.17-B no side channels |
| E5-17-AC06 | 5.17-A actual scope | 5.17-B |
| E5-17-AC07 | 5.17-A typed failure | 5.17-B independent panel |
| E5-17-AC08 | 5.17-A advisory projection | 5.17-B; 5.3 mandatory gate stays independent |
| E5-18-AC01 | 5.18-A current authority | 5.18-B |
| E5-18-AC02 | 5.18-A decision record | 5.18-B |
| E5-18-AC03 | 5.18-A invokes 5.10-B | 5.18-B pending versus overall approved |
| E5-18-AC04 | 5.10-B from actual 5.18-A | 5.18-B confirmed status |
| E5-18-AC05 | 5.18-A reject/release | 5.18-B visible reason |
| E5-18-AC06 | 5.18-A atomic envelope | 5.18-B confirmed versus refresh failure |
| E5-18-AC07 | 5.18-A stale action | 5.18-B comment/review preservation |
| E5-18-AC08 | 5.18-A; 5.10-C | 5.18-B original Retry/queue return |
| E5-19-AC01 | 5.19-A eligible actions | 5.19-B |
| E5-19-AC02 | 5.19-A command semantics | 5.19-B confirmation |
| E5-19-AC03 | 5.19-A current lifecycle | 5.19-B changed state |
| E5-19-AC04 | 5.19-A terminal envelope | 5.19-B confirmed result |
| E5-19-AC05 | 5.19-A retained links/history | 5.19-B details |
| E5-19-AC06 | 5.18-A terminal deny | 5.18-B current withdrawal presentation |
| E5-19-AC07 | 5.19-A versus actual 5.18-A | 5.19-B no false success |
| E5-19-AC08 | 5.19-A; 5.10-C | 5.19-B/My Leave refresh |
| E5-20-AC01 | 5.20-A context | 5.20-B |
| E5-20-AC02 | 5.20-A correction storage | 5.20-B prefill/save |
| E5-20-AC03 | E3 calculation; 5.20-A input adapter | 5.20-B preview |
| E5-20-AC04 | 5.20-A explicit resubmit | 5.20-B review/initial acknowledgement |
| E5-20-AC05 | 5.20-A new cycle | 5.20-B current/prior cycle |
| E5-20-AC06 | 5.20-A; 5.10-B | 5.20-B |
| E5-20-AC07 | 5.20-A atomic envelope | 5.20-B confirmed return |
| E5-20-AC08 | 5.20-A; 5.10-C | 5.20-B original recovery |
| E5-21-AC01 | 5.21-A target/responsibility context | 5.21-B chosen-person UI |
| E5-21-AC02 | 5.2; 5.21-A actual checks | 5.21-B verification |
| E5-21-AC03 | 5.21-A exact selected work | 5.21-B selection |
| E5-21-AC04 | 5.4; 5.21-A context | 5.21-B no extra flag |
| E5-21-AC05 | 5.21-A review | 5.21-B return explanation/reason |
| E5-21-AC06 | 5.21-A create/start/progress | 5.21-B truthful progress |
| E5-21-AC07 | 5.21-A actual effective authority | Existing 5.16 queue, 5.21-B confirmation |
| E5-21-AC08 | 5.2; actual action consumers | 5.21-B bounded authority labels |
| E5-21-AC09 | 5.21-A; 5.10-C | 5.21-B Retry/changed review |
| E5-22-AC01 | 5.22-A/C context | 5.22-B/D |
| E5-22-AC02 | 5.22-A actual extension check | 5.22-B |
| E5-22-AC03 | 5.22-A revision/schedule update | 5.22-B |
| E5-22-AC04 | 5.22-C actual end review | 5.22-D |
| E5-22-AC05 | 5.22-C termination/current transfer | 5.22-D truthful pending |
| E5-22-AC06 | 5.22-C source/gap effect | Existing gap attention, 5.22-D |
| E5-22-AC07 | 5.22-A/C actual audit/intent | 5.22-B/D result |
| E5-22-AC08 | 5.22-A/C versus 5.23-A | 5.22-B/D recovery |
| E5-23-AC01 | 5.23-A current expiry enforcement | Actual decision UI consumes denied/current outcome |
| E5-23-AC02 | 5.23-A actual return condition | Existing current assignment/detail |
| E5-23-AC03 | 5.23-A transfer transaction | Existing queue/read consumer |
| E5-23-AC04 | 5.23-A unresolved attention | Existing minimum manager attention |
| E5-23-AC05 | 5.23-A revision/precedence fence | Existing actual state consumers |
| E5-23-AC06 | 5.23-A claim/recovery | No new recovery screen |
| E5-23-AC07 | 5.23-A failed observation | Existing retry/attention; no authority extension |
| E5-23-AC08 | 5.23-A actual state; 5.28-A residual read | 5.28-B residual attention |
| E5-24-AC01 | 5.24-A manual context | 5.24-B |
| E5-24-AC02 | 5.24-A current target | 5.24-B explicit appointment entry |
| E5-24-AC03 | 5.24-A selected steps | 5.24-B result |
| E5-24-AC04 | 5.24-C single / E selected-planned source | 5.24-D single / F selected-planned review |
| E5-24-AC05 | 5.24-A/C/E current failure | Their existing review/attention consumers |
| E5-24-AC06 | 5.24-A/C/E actual effects | Existing unified queue/details |
| E5-24-AC07 | 5.24-A any currently authorized manager | 5.24-B ordinary action |
| E5-24-AC08 | 5.24-A/C/E races/recovery | 5.24-B/D/F truthful results |
| E5-25-AC01 | 5.4/5.18-A leave pending | Existing review; no new Wait command |
| E5-25-AC02 | 5.26-A/5.27-A timers | Existing pending/clock display |
| E5-25-AC03 | 5.25-A return transition | Existing assigned detail/queue |
| E5-25-AC04 | 5.25-A plus 5.18-A current gate | Existing review/current outcome |
| E5-25-AC05 | 5.25-A decision preservation | Existing formal history |
| E5-25-AC06 | 5.25-A unresolved result | Existing minimum manager attention |
| E5-25-AC07 | 5.25-A atomic transition/intent | Existing queue/current status |
| E5-25-AC08 | 5.25-A versus actual 5.18-A | Existing original recovery |
| E5-26-AC01 | 5.26-A occurrence | E3 notification/inbox |
| E5-26-AC02 | 5.26-A current required recipient | No UI grant from notification |
| E5-26-AC03 | 5.26-A source relevance | Existing new-assignment notice separate |
| E5-26-AC04 | 5.26-A suppress stale unhanded work | No false recall of unknown/accepted delivery |
| E5-26-AC05 | Actual request access/read owner | E3 notification deep link, current request details |
| E5-27-AC01 | 5.27-A one escalation | E3 notification/inbox |
| E5-27-AC02 | 5.27-A current read | 5.27-B attention |
| E5-27-AC03 | 5.27-A current history/action mapping | 5.27-B existing reassignment entry |
| E5-27-AC04 | 5.27-A current resolution projection | 5.27-B active versus retained history |
| E5-28-AC01 | 5.28-A current gap projection | 5.28-B attention |
| E5-28-AC02 | Actual source gap + 5.28-A residual read | 5.28-B replacement-needed |
| E5-28-AC03 | 5.28-A permitted actions/current refs | 5.28-B existing appointment/reassign entry |
| E5-28-AC04 | 5.28-A recorded exception | 5.28-B no false covered label |
| E5-28-AC05 | Actual source/appointment owner + 5.28-A projection | 5.28-B actual refreshed gap |
| E5-29-AC01 | 5.29-A preference/year | 5.29-B |
| E5-29-AC02 | 5.29-A year/status/clock | 5.29-B labels/list |
| E5-29-AC03 | 5.30-A existing detail identity | 5.29-B direct panel/page/ambiguous chooser |
| E5-29-AC04 | 5.29-A bounds/history | 5.29-B navigation |
| E5-29-AC05 | 5.29-A same inclusion | 5.29-B mobile month/context |
| E5-29-AC06 | 5.29-A true empty | 5.29-B empty versus failed and navigation |
| E5-30-AC01 | 5.30-A residual own details | 5.30-B |
| E5-30-AC02 | 5.30-A formal decision/cycle read | 5.30-B history/direct rejection |
| E5-30-AC03 | 5.12-A obligation + 5.30-A projection | 5.30-B existing response entry |
| E5-30-AC04 | 5.20-A prior cycle + 5.30-A history | 5.30-B current versus original |
| E5-30-AC05 | Actual 5.19/20 action + 5.30-A eligibility | 5.30-B existing entry/return context |
| E5-31-AC01 | Existing own-requests sections/response source | 5.31-A residual composition |
| E5-31-AC02 | Existing 5.30 detail/5.12 response | 5.31-A direct entry |
| E5-31-AC03 | Actual completed command/read owners | 5.31-A affected section invalidation/focus |
| E5-31-AC04 | Existing independent section APIs | 5.31-A independent Retry/true empty |
| E5-32-AC01 | Actual owners 5.11/12/18/19/20 | 5.32-A/B/C/D composition only |
| E5-32-AC02 | Actual source/E4 owners | 5.32-E/F/G/H representative composition |
| E5-32-AC03 | Actual 5.21–28 owners | 5.32-I/J/K plus actual 5.24 API/browser producer composition |
| E5-32-AC04 | Actual domain/receipt/transaction owners | 5.32-L response loss plus producer race/rollback cases |

### Original 5.32 broad criteria versus the twelve bounded journeys

| Journey owner | Specific additional integration evidence | Existing implementation/safeguard evidence to reference |
| --- | --- | --- |
| 5.32-A | Actual funded own request -> review -> final status/balance/history/notice | 5.11/18/B/8-A and E3 allocator/effects; not first protection against double consumption |
| 5.32-B | Actual on-behalf request -> employee-only initial response -> final result | 5.12 response/state/current authority and B; no separate response workflow |
| 5.32-C | Rejected original -> persisted corrections -> same request/fresh cycle | 5.20 state/history/save/late-write/initial rules and actual reserve/finalizer |
| 5.32-D | Pending employee withdrawal -> queue/response/balance closed consistently | 5.19 actual terminal action and 5.18 stale decision denial, E4 retention |
| 5.32-E | Real one-off balance source affects actual pending request and visible notice | 5.15-A/B and E3 source; not coverage for other ten actual source families |
| 5.32-F | Real People employment-end attempt -> protected Leave consequences/display | P-0062/5.15-K/L actual source/gate/outcomes; not first proof of commit/cancel fence |
| 5.32-G | Actual used-policy publication -> retained/current evidence and pending effects | 5.15-E/F; scheduled/assignment/recurring actual producers keep their own tests |
| 5.32-H | Existing E4 content/association survives actual submit/finalize/history read | 4.4/4.7/4.13 and 5.9; no copied upload/download/cleanup test engine |
| 5.32-I | Actual chosen temporary appointment -> effective start -> expiry/conditional return | 5.21/23/24 current authority/transfer/clock; extension/end producers retain their actual tests |
| 5.32-J | Actual ended recorded absence -> restored current supervisor step/queue | 5.25/5.4 and decision gate; no duplicate return implementation |
| 5.32-K | Actual overdue action -> recurrence -> one escalation and current attention | 5.26/27 and E3 delivery; same occurrence/outbox rules, no reminder code inside proof |
| 5.32-L | Actual own submit loses commit response -> original receipt -> one truthful UI result | 5.10-C/5.11 and E1 recovery; no new generic retry mechanism |

Manual single/selected reassignment and current/planned People supervisor change remain
actual **5.24-A/B/C/D/E/F** API/browser integration proof. There is no dedicated 5.32
manual transfer journey, and none is needed solely to repeat the already required complete
actual producer evidence. Original 5.32 AC3 is satisfied by those actual interface tests
plus the bounded appointment/return/reminder journeys, not by claiming 5.32-I covers every
transfer. The same rule applies to all real source variants and original 5.32 AC4 races:
core owner tests + actual producer integration are mandatory before proof-story execution.

No 5.32 journey supplies the first missing authorization, schema/RLS, ledger/receipt/intent
atomicity, cleanup protection, current authority or source-writer safety. If a journey
finds a missing owner obligation, fix/allocate it in that owner and count its size rather
than introduce safeguards hidden in an integration story.

### First-use presentation and duplicate-work reconciliation

- 5.11-B owns first usable own submitted result/minimum My Leave row/detail/status;
  5.12-B owns first usable employee-response entry/view. 5.30/31 add only residual detail/
  history/composition. The employee must not submit into a handoff with a future response
  or details screen as a dependency.
- 5.18-A/B own minimum actual assigned inspection/decision and current outcome. 5.16 adds
  residual collection/inspection query/layout; it does not implement approve/reject again.
- 5.15-A/B own minimum pending-source-issue read/presentation; later source families reuse
  them and prove their actual issues. 5.27/28 add escalation/coverage branches rather than
  own the first unresolved source consequence display.
- 5.10-A supplies state/current-read integrity, C original receipt/outcome extension,
  5.8-A actual commitment/coordination and B all-gate consume completion. Actual handlers
  call those mechanisms inside their own promised transaction and prove their own state/
  evidence/intent envelope once. Repeated contract words are references, not reimplementation.
- 5.14 has no residual separate response story: 5.12 owns initial obligation/action/view,
  5.13/15 subsequent allocation effects and 5.19 actual employee withdrawal. Notification
  read state remains the E3 inbox owner's separate concern and never employee consent.
- 5.25's waiting/reminder sentences reference existing pending decision/5.26/27 timing;
  its actual new transition is recorded-absence return. It does not add a Wait action,
  reminder service or automatic approval. Temporary appointment expiry remains 5.23.
- 5.29 Calendar/List directly uses existing 5.30 details; chooser is only for ambiguous
  grouped markers. 5.31 composes completed sections independently and retries failed reads,
  never replays a confirmed mutation to refresh a balance.

### Stale source wording aligned with agreed appointment contract

Original **5.21 AC6** said appointment and selected transfers were recorded together,
which could incorrectly imply all selected requests had transferred at creation. Align
that editable source criterion with the already bound appointment lifecycle: create
atomically retains exact reviewed selected-work/return intent and actual outcome/notice;
protected effective start processing retains truthful per-request progress. Creation
alone does not claim all selected transfers complete. This clarifies the existing agreed
contract, not a new policy, manual-batch rule or changed product scope. Original AC count
stays 230; updated source digest and AC6 hash record the deliberate alignment. Accepted
ADRs remain unchanged. Appointment start/expiry/current authority proof remains with its
actual owners and is included in final size.

### Remaining C6 gates after 230/230 source-owner allocation

All original criteria now have detailed owner links. Still open: non-5.15 C3 writer/import/
access/type/source variants; granular cross-cutting FR/NFR/UX/release/security obligations;
semantic/external/foundation graph; final executable foundation allocation; actual bounded
single-agent sizes and any material split/merge approval. Source criterion ownership
alone cannot establish these. No runtime tests, migrations, grants or code performed.

## C6 pass 5 — residual writers and cross-cutting source disposition

All 230 original E5 source criteria retain the preceding detailed allocation. This pass
checks requirements outside that story checklist. It reuses the existing BIZ/CALC/FLOW/PRIV
planning index, which references authoritative Features/ADRs/UX; these IDs are not claimed
to be source-native FR numbers or independently atomic requirements. All 122 existing
index entries receive an E5/inherited/later-owner disposition below. Full source meaning,
examples and accepted supersession remain authoritative, not the short navigation rows.

### Residual actual writer/alternate-path obligations

Each row is a real source/consumer test obligation, not a new story. All eleven 5.15 source
families/variants remain in pass 2 and are not repeated here.

| Writer ID / real owner | Required concrete proof / no-impact boundary | Actual consuming owner / completion limit |
| --- | --- | --- |
| W01 type create / first unused policy, E3 3.1/3.3-A | No implicit assignment/earning/employee holder; stable source guards precede later references | 5.11/12/20 later select actual date-effective policy, not the draft-choice pointer |
| W02 metadata/permitted mode, E3 3.39 | Actual new input mode admission/choice compatibility; pure labels/icons do not reallocate existing requests | 5.6/11/12/20; source preserves prior policy/calculation and ordinary draft compatibility rather than clearing on outage |
| W03 type deactivate, E3 3.37 | Current/planned assignment dependency refusal and assignment/deactivate race; retain balances/history | Actual source proves current admission versus recorded request use; inactive label is no invented finalization blocker |
| W04 type restore, E3 3.38 | Same stable identity, no recreated grants/assignments/earning or closed-work resurrection | Actual submit selection/current inputs; no universal finalizer callback merely for metadata restoration |
| W05 unused work-profile create, E2 2.19 | No automatic holders/default/assignment; profile/source guard exists before reference | Actual later 5.15-O/Q reference writer, not an empty-profile impact worker |
| W06 unused profile archive, E2 2.24 | Refuse actual current/planned/default dependencies and concurrent new holder; retain historical source refs | Historical 5.6/7/8 inputs remain explainable; archive does not move employees |
| W07 Access app/org admission/grant/role/member writes, actual Access + E2 2.1–10 | Current revoke/disable and custom default scope; no employment/role-name grant; exact owner check evidence | Every E5 protected read/command and current appointment consumer; use existing KDG foundation, add actual Leave/People variants only |
| W08 account/person/employment link and staged access, Identity/Access/People owner | Explicit verified link/adoption/current membership; accountless employee remains valid and service actor needs no fake employment | 5.12 employee-only response and 5.21 nonemployee appointee exact actor/member context; no guessed email linking |
| W09 department/location, People E2 2.14/15 | Descriptive organizational facts do not grant approval or change Leave work/policy settings | Actual authorized grouping reads; no invented funding-impact writer for a descriptive field |
| W10 actual request lifecycle/exception, 5.11/12/13/18/19/20 | Same employee/date capacity, reserve/consume/release/evidence/receipt/notice atomicity; actor absence can affect other duties | Actual cross-subject dependency/coverage consumers; not just applicant employee lock or a copied ledger |
| W11 appointment start/extend/end/expiry, 5.21/22/23 | Old/new actor duty scope, overlap, current interval/revision fence, no stale expiry return or extended authority | Actual 5.18 current decision and 5.3/28 gap; worker lag never authority |
| W12 manual/current/planned supervisor transfer/return, 5.24/25 + People | Correct exact pending selection/source attempt, unfinished steps only, retained final/completed decisions, no source bypass | Current authority check and actual queues/notices; manual per-request batch semantics not silently used for source attempts |
| W13 coverage exception, 5.5 | Exact current gap/reason/authority without grant or false cover; changed source rechecks applicability | 5.10-B gate and actual gap attention, no independent appointment engine |
| W14 E4 association/readiness/disposal | Actual source target/version and fixed bytes/cleanup protection, current metadata/byte permissions and retained lifecycle | 5.9/11/12/20/B actual policy/association composition; no human inspection gate or second upload pipeline |
| W15 supported import/provisioning/maintenance, owning E8/source/release item | No hidden API/worker/raw SQL path bypass; supported actual business writers use protected source/effect/review contract | Imports are E8, not E7; stay inactive until actual protected writer/adoption is delivered. No new E5 import UI/tool |
| W16 no-write time boundaries, E3/People/appointment owners | Date-effective earning/expiry/period/configuration/current authority computed correctly without daily posting; obsolete scheduled intent fenced | Actual 5.7/8/B and 5.23/25 due transition; no universal periodic approval worker |
| W17 migrations/repair/release/restore, actual owning release/operator | Restricted runtime cannot migrate; actual compatible owner upgrades/failed-write rollback, deliberate repair attribution and outbound-side-effect reconciliation | First affected E5 source/effect/worker and E8 restore rehearsal; no generic schema whitelist or migration on API startup |

**Source-index correction:** The older C3 register said “E7 import”. The approved epic
scope places consultant import/cutover in E8; corrected that reference in the owning
contract. This is a navigation/ownership correction, not additional import scope.

### Existing cross-epic source index: E5 / reuse / later-owner disposition

| Existing index ID | E5 disposition | Primary E5 or actual inherited/later owner |
| --- | --- | --- |
| BIZ-01 | Inherited + E5 consumer | Identity/Access/E2 administration; every E5 API/link current check |
| BIZ-02 | Inherited setup | E2/E3 actual assessment; 5.1/7 expose required setup versus unavailable, no new checklist |
| BIZ-03 | E5 integration | People + 5.15-K/5.24-C/E; no employee copy or employment-derived grant |
| BIZ-04 | E5 integration | 5.15-M/O/Q/S/U, E2 work owners and 5.6/7 date inputs |
| BIZ-05 | E5 source participation | Actual E2/E3 create/archive/metadata/deactivate/restore C3 residual variants below |
| BIZ-06 | E5 integration | 5.15-E/G/I and 5.1/7 retained governing version, E3 editor remains owner |
| BIZ-07 | E5 integration | 5.15-C/D recurring/reset, no request-exception grant inference |
| BIZ-08 | E5 integration | 5.15-A/B actual Add/Deduct and minimum pending issues |
| BIZ-09 | Inherited + actual use | E3 allocator/events; 5.8-A/B actual commitments/consumption, no earning worker |
| BIZ-10 | E5 integration | 5.8-A with E3 3.18 date/source/reservation priority |
| BIZ-11 | E5 integration | E3 event/evidence + 5.8-A/5.10-B actual transaction and protected inputs |
| BIZ-12 | E5 direct | 5.13/15 actual later-change notice/response distinction, L-0162 zero closure |
| BIZ-13 | Pending E5; approved E6 | 5.15-K/source effects pending; E6 owns spent/approved deficit correction |
| BIZ-14 | Inherited + closure | E1 preservation; 5.11 closes ordinary draft, 5.20 separate correction |
| BIZ-15 | E5 direct | 5.6 selected mode/capacity using E3 duration, no exact partial times |
| BIZ-16 | E5 direct | 5.11-A/B and rule/B/8-A/E4 composition |
| BIZ-17 | E5 direct | 5.12-A/B explicit target/actor/reason/initial response |
| BIZ-18 | E5 direct | 5.13-A/B exception lines/current scope and optional atomic combined decision |
| BIZ-19 | E5 direct | 5.1 route, 5.11/12 conditional own decision and 5.18/B actual approval |
| BIZ-20 | E5 direct | 5.4 directional current-absence predicate, B independent gates |
| BIZ-21 | E5 direct | 5.2/21/22/23/24 exact appointment/transfer/return and current actor |
| BIZ-22 | E5 direct | 5.16/17/18 and separate mandatory 5.3 coverage |
| BIZ-23 | E5 direct | 5.8-A lifecycle + real 5.11/12/18/19/20/B producers |
| BIZ-24 | E5 direct | 5.20 correction/current cycle and fresh validation/commitment |
| BIZ-25 | Later E6 | Approved cancellation/replacement, L-0152 accepted defaults only; no E5 action |
| BIZ-26 | Pending E5; corrective E6 | 5.15 truthful unresolved pending issue; approved/deficit correction follow-up E6 |
| BIZ-27 | Inherited E4 + consumer | 4.4/4.13 upload/association/type/size; 5.9/11/12/20 actual readiness/continuity |
| BIZ-28 | Inherited E4 + consumer | 4.7/10/11 current medical permission/retention; E5 safe projections only |
| BIZ-29 | E5 event producer | E3 delivery/inbox; each E5 producer minimal allowed envelope/current recipient |
| BIZ-30 | Inherited + E5 timed | E3 outbox/acceptance/worker; 5.23/25/26/27 due/current relevance |
| BIZ-31 | E5 direct + E3 reuse | 5.29/30/31 own history/sections/preference; E3 balances remain owner |
| BIZ-32 | E5 narrow; wider E7 | 5.15/27/28 attention and 5.17 advisory team; org overview/tools/reporting later owner |
| BIZ-33 | Later E7 | Report/export catalog outside E5, current scoped views are not organization reports |
| BIZ-34 | E5 provenance; search E7 | Every consequential E5 writer immutable attribution; searchable audit UI remains E7 |
| BIZ-35 | Later E8 + all-writer safety | Consultant exact-batch import/approval/cutover E8; no active E5 bypass |
| BIZ-36 | E5 evidence; pilot E8 | Actual bounded E5 acceptance/owner proofs, representative production UAT/activation E8 |
| CALC-01 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-02 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-03 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-04 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-05 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-06 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-07 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-08 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-09 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-10 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-11 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-12 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-13 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-14 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-15 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-16 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-17 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-18 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-19 | Inherited E3 calculation | E3 earning/period/cap/rollover/expiry source tests; actual 5.8/15 integration references those inputs |
| CALC-20 | E5 current input | E3 date/boundary rules + actual 5.7/8-A/B and source writes |
| CALC-21 | E5 protected use | E3 3.18 ordered allocation + 5.8-A actual commitment |
| CALC-22 | E5 direct | 5.7 full requested-date horizon and 5.11/12/20 actual checks |
| CALC-23 | E5 direct | 5.8-A prior reservation/validity actual consume/release |
| CALC-24 | E5 direct | Each 5.13/15 source writer L-0151 notice, not renewed acknowledgement |
| CALC-25 | E5 direct | 5.13-A/B explicit authorized whole-duration source plan |
| CALC-26 | Pending E5; source E2/E6 | 5.7/5.15-K actual end/add periods; approved historical correction E6 |
| CALC-27 | E5 validation; E3 arithmetic | 5.6 selected input mode, E3 exact half-day/minute result |
| CALC-28 | E5 direct | 5.6 active per-date capacity, real producers under employee coordination |
| CALC-29 | E5 direct | 5.7 short notice/backdating with reasons, no arbitrary cutoff |
| CALC-30 | E5 direct | 5.8-A effects and 5.11/12/18/19/20/B actual envelopes |
| CALC-31 | Later E6 | Approved cancellation/counterfactual earning correction, no E5 consumed->released shortcut |
| CALC-32 | E5 preservation; correction E6 | Immutable decision/evidence retained by all E5 sources; actual historical approved corrections E6 |
| CALC-33 | Inherited + actual use | E3 stable employee event sequence; actual 5.8/13/15 effects |
| CALC-34 | E5 all writers | Core guard + real source/ref/employee participation, protected current action |
| CALC-35 | Inherited E3 + E5 bound | On-demand indexed calculation, workload evidence; no speculative accrual worker/cache |
| CALC-36 | E5 own/review display | 5.11/12/13/16/30/31 permitted explanations; E3 balance evidence source |
| FLOW-01 | E5 direct | 5.1 configured route and 5.10-B at least one valid decision |
| FLOW-02 | E5 direct | 5.1 definite missing setup/current owner failure, 5.11/12 blocking route |
| FLOW-03 | Inherited defaults + execution | E2/E3 source setup; actual 5.4 fallback off and 5.26/27 3/7-day defaults |
| FLOW-04 | E5 direct | 5.24-C/E source transfer, retained policy/final choice and actual history |
| FLOW-05 | E5 direct | Access explicit defaults; 5.11/12 current conditional own-step decision |
| FLOW-06 | E5 direct | 5.12-A permitted later-step automatic decision retained while earlier outstanding |
| FLOW-07 | E5 direct | 5.18-A exact current consecutive step set; 5.1 config; distinct-person rules |
| FLOW-08 | E5 direct | 5.11/20 exact own initial unpaid acknowledgement |
| FLOW-09 | E5 direct | 5.12 initial response and separate employee draft |
| FLOW-10 | E5 direct | Actual 5.13/15 later notification, independently outstanding initial response |
| FLOW-11 | E5 direct | 5.3 stage result; 5.11/12 pending known gap and B final gate |
| FLOW-12 | E5 direct | 5.5 bounded permission/reason exception; gap remains visible |
| FLOW-13 | E5 direct | Actual loss-of-cover source preserves approval and required manager gap evidence |
| FLOW-14 | E5 direct | 5.2/21 effective responsibility appointment/current member |
| FLOW-15 | E5 direct | 5.2 overlap and actual 5.21/22 protected interval writes |
| FLOW-16 | E5 direct | 5.21 exact selection/conditional return intent and effective processing |
| FLOW-17 | E5 direct | 5.23 actual latest/current return checks and transfer |
| FLOW-18 | E5 direct | 5.22-C/D current early end even no eligible destination |
| FLOW-19 | E5 direct | 5.21/22 actual notice; no appointee acceptance gate |
| FLOW-20 | E5 direct | 5.4 current required-step predicate and 5.18 actual decision |
| FLOW-21 | E5 direct | L-0146 configured temp-final fallback, no extra flag |
| FLOW-22 | E5 direct | 5.25 actual return; 5.26/27 independent timers, no Wait command |
| FLOW-23 | E5 direct | 5.26/27 current required recipient/occurrence/state, no reminder to completed/later steps |
| FLOW-24 | E5 direct | 5.16/18 queue/review/current outcome and visible rejection reason |
| FLOW-25 | E5 direct | 5.8-A and actual lifecycle producers, no second ledger |
| FLOW-26 | E5 direct | 5.20 same ID/fresh cycle/history and current rules |
| FLOW-27 | Later E6 | Approved replacement distinct from E5 rejected correction |
| FLOW-28 | E5 direct | 5.11-B minimum My Leave result/return/context; no automatic details open |
| PRIV-01 | E5 projection | 5.17 generic absence + current actual scope; no type-derived side channels |
| PRIV-02 | E5 projection | 5.16/18 assigned and actual manager source/detail fields, no unrelated request read |
| PRIV-03 | E5 projection | 5.30 formal named decision history and direct rejection; first minimum reads earlier |
| PRIV-04 | Inherited E4 + E5 deny | 4.7 separate permission; all E5 projections exclude medical metadata absent authority |
| PRIV-05 | E5 producer | Every actual notice payload name/dates/status/link only, E3 templates enforce |
| PRIV-06 | Inherited + E5 consumer | Current Access/domain check on every notification link/detail/action |
| PRIV-07 | Inherited E3 + consumer | E3 active-org inbox/exact permitted count variant; no global org business read |
| PRIV-08 | E5 distinction | 5.12 business response independent of E3 per-user read state |
| PRIV-09 | Inherited E3 UI | Existing notification panel and exact typed current reads; no new E5 inbox |
| PRIV-10 | E5 direct | 5.31 independent sections/read Retry; balance outage alone does not disable Apply |
| PRIV-11 | E5 direct | 5.16/29/attention true empty versus filtered versus failed/loading, stale/current scope |
| PRIV-12 | E5 direct | 5.17 safe advisory unavailable; no false nobody away or new capacity blocker |
| PRIV-13 | E5 direct | 5.18/13/20/24 current revision/review; preserve unsent input within actual support |
| PRIV-14 | E5 inherited control | 5.16/29 mobile filter controls use existing provisional Apply semantics |
| PRIV-15 | Wider E7 | Organization overview defaults remain E7; E5 own/queue/current-team rules separately bound |
| PRIV-16 | Wider E7; own E5 | Organization overview entry remains E7; 5.29/30 direct permitted own detail |
| PRIV-17 | E5 scoped view | 5.17 per-date/partial markers versus duration; no invented exact times |
| PRIV-18 | Source E2/E3; broader E7 | 5.6 actual calendar/work values; no new org holiday overview in E5 |
| PRIV-19 | Later E7 | Matching authorized reports/CSV transformations, no E5 export feature |
| PRIV-20 | Later E7; writers E5 | Protected searchable audit UI later; E5 actual immutable provenance/private detail protection now |
| PRIV-21 | E5 saving integration | 5.20 correction autosave, 5.15/21/22 explicit confirmation; no mixed hidden field writes |
| PRIV-22 | E5 recovery integration | E1 adopted draft failures/session protection + actual 5.11/20 lifecycle closure/late-write behavior |

### Cross-cutting acceptance evidence, beginning with first affected owner

These are concrete boundary obligations, not late generic “test everything” work. They
apply to actual relevant consumers and reuse owner fixtures/assertions while preserving
one actual producer/UI integration where needed. No passing test is claimed here.

| Obligation ID / authoritative source | Primary implementation/evidence owner | Required actual boundary / later evidence limit |
| --- | --- | --- |
| X01 tenant/account/resource isolation, Features NFR/Permissions + P-0019/0035/0046/0053 | 5.10-A native storage/read and actual shared owner current scope | API + real restricted PostgreSQL allow/deny; cross-org/account/cycle/decision/evidence refs and pooled worker context; no fixture token or frontend filter as proof |
| X02 current capability and role-default/temporary separation, P-0046/0053/0063 | Access current consumer + each E5 action | Revoked/disabled/current membership, custom omissions, independent People admission, bounded appointment versus permanent capabilities; no grant from employment/team/role label |
| X03 provenance/immutability, Features §20 + P-0025/0056/L-0111 | Actual source/decision/event/evidence writer; 5.10-A immutable links | Real initiator/executor/service actor, UTC creation/update as appropriate; actual decisions/source/evidence preserved; E7 later searches, does not first create history |
| X04 transactions/concurrency/dedup, P-0022/0033–35/L-0112/0113 | 5.10-C + 5.8-A primitives and actual command/source owner | Before/after/induced failure and competing real DB writes; no external wait under locks, orphan effects, request resurrection or duplicate outcome/intent |
| X05 native schema/release compatibility, P-0020 and focused migration guidance | Actual API/source/worker migration/release owner | Current/previous supported runtime/schema, actual business RLS/constraints/forbidden DDL, migration failure blocks activation; no automatic downgrade or empty-ledger-only PASS |
| X06 safe errors/generated contract, P-0001/0031 | Actual owner DTO/export/adapter and shared generator reused | Closed discriminator/current revision/UUID/string minute semantics, malformed/unknown error safe; stale schema/client check must fail before regeneration, no English branching |
| X07 draft/correction/session recovery, P-0032/0033/0049–51/L-0159 | E1 + 5.11 ordinary close / 5.20 correction / actual browser | Same authorized user/validated org return, late-save protection, supported useful input only; inline Retry and exit-only Stay/Close anyway; never automatically reconfirm a consequential action |
| X08 private attachments, P-0030/0036/0038/0054/0055 + E4 | Actual Content/E4 source and 5.9/submit/finalizer consumer | Owner/target/readiness/retained-byte and cleanup race, no medical metadata absent permission, authenticated streamed read; signed uploads remain separate, no public read-URL fallback |
| X09 notification isolation/lifecycle, P-0028/0029 + L-0114–17/0157 | E3 notification/outbox + each actual E5 event producer | Actual immutable payload/version/recipient acceptance/dedup/expiry, uncertain handover retained, readable inbox current scope; read state not business response, comments/docs excluded |
| X10 worker safety/compatibility, P-0026–28 | Actual due/handover first owner and release | Restricted discovery/per-item scope/claims/stale fencing/bounded shutdown/forced-termination evidence and unsupported queued versions; API independent of delivery outage |
| X11 operational diagnostics/sensitive data, P-0023/L-0118/0120 | Existing API/service instrumentation plus first source/worker consumer | Actual exception/background/streaming paths log only safe structured fields; correlation/recovery refs, no payloads/notes/secrets/private URLs. Existing diagnostic patterns referenced, not copied log frameworks |
| X12 metrics/performance, Features NFR + accepted endpoint-measurement baseline | Actual API/calculation/source owner | Latency/error/in-flight/phase metrics low cardinality; local source changes synchronous first, representative 100/1,000 workload evidence before limits/readiness claims; no borrowed E1 p95 or unmeasured 5–20ms estimate as E5 SLA |
| X13 operational alerting, L-0120 | First API/worker/delivery owner, operations release configuration | API/heartbeat 5min, overdue notice warning 15min/escalation 1h, stale recovery point/integrity immediate per accepted source; retry does not reset age, exclude future scheduled work, grouped incident/verified recovery |
| X14 encryption/dependency/secret environment, Features NFR/P-0017 and owner manifests | Actual shared/app runtime/release owner | Verified HTTPS/nonlocal transport and storage encryption, owner-separated credentials/current service policy, safe configs/pins; no operational production/security compliance inferred from docs or mocks |
| X15 accessibility, Features WCAG 2.2 AA + shared/Leave DESIGN/EXPERIENCE | Each actual first browser consumer; shared patterns promoted with consuming proof | Keyboard/focus/labels/error associations/live messages/zoom/contrast/status not colour alone, drawer/page/date/list/calendar usability; static mock checks do not prove browser/assistive tech |
| X16 responsive/navigation/filter states, approved UX | 5.11/12/16/17/18/19/20/21/22/24/29/30/31 browser owners | Desktop right panel/mobile page, direct detail/ambiguous chooser only, return focus/context, provisional mobile filters, independent failed panel Retry and true empty; real browser proof, not another global UI rewrite |
| X17 localization/date/number presentation, Features localization + shared UX/L-0059 | E1 localization foundation and actual new labels/amount/state consumers | Approved language/fallback, no raw English error branching, actual work timezone/civil dates/canonical minutes and localized display; no translation changing authority or arithmetic |
| X18 saving/confirmation conventions, P-0050/0051 | Actual request/correction/source/appointment/preference owner | Ordinary/correction autosave versus whole-form source Save/Review/Confirm versus immediate preference; explicit balance/destructive effects, no hidden per-field commits or extra default submit confirmation |
| X19 retention/deletion, Features §12/NFR and actual retry/evidence contracts | E4 retention/cleanup, request/evidence/outcome/outbox owners | Actual retained links/unknown work/required audit prevent premature cleanup; no new arbitrary active-draft or outcome purge. Sensitive deletion respects real policy, not just a UI hide |
| X20 recovery/restore consistency, L-0119/P-0020 | Actual owner release/recovery support, E8 integrated rehearsal | 1h RPO/4h essential RTO/30day backups accepted targets; verify DB/files/identity/config and outbound hold. E5 must preserve recoverable durable state; full rehearsal/pilot evidence remains E8 |
| X21 ATDD/TDD/impacts/traceability, AGENTS/BMAD/P-0059 | Every actual delivery item and shared first consumer | Record observed relevant failing acceptance then focused tests/results; characterize risky legacy refactor; same-item scaffold/shared UI/context/docs/ADR decisions and consuming pattern tests, not duplicate feature specs |

The X rows are owner/evidence obligations rather than a claim every NFR has been fully
implemented. Actual detailed test-node/fixture/command results are recorded during authorized
delivery under the artifact map, with exact scope and limits; no placeholder PASS.

### Cross-check findings carried to the delivery graph

- Credit implemented KDG Access registry/admission/commands and shared client/Auth patterns.
  Exact People/Leave check consumers remain new work. No plan to rebuild the registry or
  infer live grants/People runtime from existing source.
- Preserve the pass-2 minimum pending-source-issue attention allocation to 5.15-A/B. Wider
  E6 deficits/organization reports remain later scope.
- A separate **first-use approval-coverage gap attention dependency** still needs explicit
  executable graph allocation. 5.3 emits the rule/gap, actual request/appointment/source
  producers retain real gap evidence, and later 5.28-A currently consumes completed manager
  attention/appointment flows. Do not claim all first-use manager gap read/presentation is
  supplied by that later residual story. Resolve the earliest minimum read/presentation
  owner and its size before final order; no new feature approval is needed for the already
  required gap visibility, but a material executable split must be reviewed with the user.
- Generic phased source/effect tests cannot stand in for all actual W01–W17 alternate
  writers. Keep their exact owners in external/dependency reconciliation. Unsupported import/
  maintenance paths remain unavailable until actually delivered with those protections.

Source-writer and cross-cutting planning obligations now have explicit dispositions. This
is not final atomic FR/NFR/UX completeness: graph finding above, actual external delivery
status, foundation/executable allocation, semantic order and final single-agent sizing
remain open. No runtime tests, migrations, grants or Leave implementation performed.

## C6 graph correction proposal: minimum coverage attention

Proposed 5.28-C extracts the already required minimum manager gap read/presentation from
later residual 5.28-A/B. Candidate graph explicitly includes seven foundation scope inputs
and places C before actual first producers, without depending on later appointment or
escalation/browser flows. Source producers still own real protected gap effects. Internal
acyclic check recorded in e5-delivery-graph-reconciliation; full external/order/size remains.
User agreement pending; 80 approved suffixed boundaries unchanged. If accepted, count 81
and reassign the minimum once; no new feature/permission/dashboard or duplicate engine.

## Minimum gap attention accepted; residual and external allocation — 2026-10-25

User accepted 5.28-C; approved suffixed boundaries now 81. Earlier proposed/count-80 notes
for this extraction are historical. C owns minimum manager gap representation/read/update
and existing display; later 5.28-A/B source/detail/action composition reuses it. Real
source producers retain their actual protected effects and tests. Original 230 source
criteria unchanged. C6 graph register now explicitly maps twelve external prerequisite
clusters to real owning E1/E2/E3/E4 delivery items/implemented evidence and remaining deltas.
Seven foundation scopes have bounded candidate assessments; prospective executable total
88 if retained. Full all-item sizing/order/coverage closure and E5 completion agreement
still open; no runtime implementation/tests or generic foundation rebuild.

## Final E5 allocation reconciliation — 2026-10-25

The graph register's final first-read allocation supersedes earlier first-storage wording:
appointment storage/read is 5.2, initial response storage/predicate is B, and C's one gap
representation contains its minimum nullable exception evidence. Production writes and
integration remain with actual 5.21/22/23, 5.12/13/15 and 5.5 producers respectively.
All original source criteria remain unchanged. Source ownership, residual writers,
accepted refinements and cross-cutting dispositions map to the same 88 candidate items
and existing external owners. No new product policy, duplicated engine or boundary.

E5 completion summary may now be presented for user agreement. The ledger establishes
planning ownership, not successful tests or whole-product final atomic coverage. Remaining
epics, requirements-inventory final validation and broader Phase 1 readiness remain open.

## E5 planning closure accepted — 2026-10-25

User explicitly approved E5 story-planning closure. Earlier requests for E5 completion
agreement are now historical. The assessed 88-item baseline and its evidence limits stand.
Next: E6 preparation followed by guided review. Whole-product final coverage, executable
contract/test/release evidence and Phase 1 implementation readiness remain open.
