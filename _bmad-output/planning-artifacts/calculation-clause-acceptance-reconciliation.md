# Calculation clause-to-acceptance reconciliation

**Date:** 2026-10-25. **Status:** Scoped semantic reconciliation; whole-product G01 remains open.

This checks the existing CALC-01–36 source-rule/example ledger in
[epics](epics.md#entitlement-rule-and-acceptance-example-ledger--2026-10-05)
against actual current delivery-leaf acceptance. It adds no competing calculation spec.
References identify Given blocks in the story, counted from one; source/ADR clauses and
original examples remain authoritative. E5's 230-clause allocation and E6 correction
register cover their actual downstream command halves, rather than broad references here
claiming to implement all request/correction behavior in E3.

These are manual semantic judgments and boundary assertions. They are distinct from the
1,219-unit lexical navigation index and do not turn that index into atomic coverage proof.

| Existing source rule | Actual acceptance witnesses | Clause assertion / precedence |
| --- | --- | --- |
| CALC-01 | 3.8/AC01, 3.8/AC06, 3.9/AC06, 3.17-A/AC04 | Repeated automatic reads have no posted grant/snapshot; manual-only without grants is a genuine zero, distinct from untracked. |
| CALC-02 | 3.7/AC02, 3.7/AC03, 3.14/AC02 | Effective standard-day conversion and actual six-hour Friday duration are independent; retained rollover conversion cannot drift. |
| CALC-03 | 3.8/AC07 | Original leap-day anchor clamps then returns; explicit 2027–2028 inclusive period example now has a dedicated witness. |
| CALC-04 | 3.8/AC02, 3.8/AC03, 3.8/AC04 | Calendar denominator, leap-year and inclusive date tests include 8640×100/365→2367, full-year total and no double proration. |
| CALC-05 | 3.10/AC01, 3.10/AC02, 3.10/AC03, 3.10/AC04 | Chronological precise cap admits .2 of .5 at 119.8/120 and never catches up Monday exclusion after later deduction. |
| CALC-06 | 3.8/AC05 | Prospective old/new annual-rate portions retain full-year denominator and are combined before final floor. |
| CALC-07 | 3.16/AC01, 3.16/AC02, 3.16/AC03, 3.16/AC04 | Method transition waits for each employee period boundary; prior history, carry-over/expiry and no-duplicate grant remain. |
| CALC-08 | 3.11/AC01, 3.11/AC02, 3.11/AC05 | Calendar/anniversary period-start and prorated joining availability; ordinary annual change does not replace current upfront grant. |
| CALC-09 | 3.11/AC03, 3.11/AC10, 3.13/AC01 | Independent upfront floor is distinct from cumulative monthly precision; 481×15/30→240 usable has an explicit witness. |
| CALC-10 | 3.12/AC01, 3.12/AC02 | Twelve contiguous original-anchor periods; 31 January clamps February and returns to March without iterative drift. |
| CALC-11 | 3.12/AC03, 3.13/AC02, 3.13/AC04 | Joining availability versus configured month-end; an end-date portion cannot fund the previous date, including changed-rate timing. |
| CALC-12 | 3.12/AC04, 3.12/AC05 | 8550 annual minutes partitions 712/713 and totals 8550; consumption/cap exclusion cannot enlarge next nominal instalment. |
| CALC-13 | 3.13/AC05, 3.13/AC06 | Related monthly fractions retain cumulative precision under L-0105; 712.5+952.5→1665 and 240.5+481→721, without restoring excluded earning. |
| CALC-14 | 3.13/AC03, 3.13/AC04, 3.34-A/AC09 | Next-instalment rate differs from first usable date; overriding employees get truthful actual-effect notices, not a false allowance change. |
| CALC-15 | 3.30/AC01, 3.30/AC02, 3.30/AC03, 3.30/AC04, 3.30/AC05 | Persistent recurring override/return at the actual leave-period boundary, no automatic end/reset; immediate change remains adjustment. |
| CALC-16 | 3.10/AC05, 3.11/AC06, 3.10/AC07 | Earned reservation still counts toward cap, future reservation does not; consumption differs from withdrawal/headroom and no catch-up. |
| CALC-17 | 3.14/AC01, 3.14/AC02 | No/all/limited rollover, exact 600/480 outcome and effective 8/6-hour conversion retained. |
| CALC-18 | 3.15/AC01, 3.15/AC02, 3.15/AC03 | Actual new-period-relative month arithmetic and inclusive last usable date, including month-end/leap examples. |
| CALC-19 | 3.14/AC03, 3.14/AC04, 3.15/AC04 | Once-only/repeated carry provenance, no earlier-expiry extension, explain nontransferred expiry; no automatic payout/transfer. |
| CALC-20 | 3.15/AC03, 3.15/AC05, 3.16/AC03, 3.18/AC01 | Employee work date, expiry/rollover before earning/cap and no funding before availability; 20 minus 2 before April earning. |
| CALC-21 | 3.18/AC02, 3.18/AC03, 3.18/AC04 | Ascending dates and earliest expiry, then L-0129 oldest original period/stable key tie; future earning cannot repair earlier shortfall. |
| CALC-22 | 3.20/AC02, 3.18/AC01 | Every requested date fits the inclusive twelve-month default horizon and each actual funding validity window. |
| CALC-23 | 3.18/AC05, 3.14/AC05, 5.8-A/AC01 | New earlier requests cannot displace valid prior commitments; expiry does not extend through reservation, and known rollover is projected initially. |
| CALC-24 | 3.29/AC05, 3.36-A/AC05, 5.15-A/AC01 | L-0151 governs later pending increases: prior/revised actor/reason and notice, no renewed response gate; independently outstanding initial response remains. E5 source-family audit owns actual command integration. |
| CALC-25 | 3.21/AC01, 3.21/AC02, 3.21/AC03, 3.21/AC04, 3.21/AC06 | Explicit authorized source lines conserve duration and do not grant/borrow/decide from a preview; ordinary approval is not override authority. |
| CALC-26 | 3.11/AC04, 3.20/AC05, 6.29/AC01 | Inclusive final employment date and proration/full departure effects; protected source correction preserves decisions and flags actual impacts. |
| CALC-27 | 3.7/AC03, 3.7/AC04, 3.8/AC04 | Half-hour request increment is separate from exact 225-minute half-day and whole-minute entitlement precision. |
| CALC-28 | 3.20/AC06, 5.6/AC01 | Cross-type active same-date capacity includes only actual active request states; previews warn and actual protected submit enforces concurrency. |
| CALC-29 | 3.20/AC03, 3.20/AC04 | Zero notice default, short-notice reason, backdating reason and historical work dates; no arbitrary old-request cutoff. |
| CALC-30 | 5.8-A/AC01, 5.10-B/AC01 | One actual commitment/event history with intermediate reservation, single final consumption and rejection/withdrawal release; actual producers remain in accepted E5 audit. |
| CALC-31 | 6.4/AC01, 6.5/AC01 | Cancellation replay/counterfactual capped earning, original source validity and one protected reversal; deficit resolution stays explicit E6, not a consumed→released shortcut. |
| CALC-32 | 3.17-A/AC06, 3.17-B/AC05, 6.17/AC01 | Corrected known history differs from retained Balance at approval; original decisions/calculation version remain immutable. |
| CALC-33 | 3.9/AC02, 3.9/AC03, 3.9/AC04 | Effective date, recorded time and serialized sequence remain distinct; retry keeps original order after automatic date effects. |
| CALC-34 | 3.29/AC04, 3.29/AC08, 3.34-A/AC05, 3.28/AC08 | Protected current inputs, reviewed consequential change and first real source-writer participation; distinguish known busy/no-effect from unknown commit. |
| CALC-35 | 3.17-B/AC07, 3.17-A/AC07 | Measure direct indexed multi-year replay first; no speculative cache/checkpoints, posting worker or routine snapshots. |
| CALC-36 | 3.17-A/AC03, 3.31/AC01, 3.31/AC03, 3.31/AC04, 3.31/AC05 | Explain available/reserved/used/current versus history, preserve source/actor/reason links and standard-day context; no double deduction or year-filter mutation. |

## Later accepted coverage and complete initial fields

The original 36-rule ledger predates L-0133–0145. The following exact new witnesses bind
those accepted additions rather than treating the older ledger as exhaustive:

| Source obligation | Actual acceptance | Assertion |
| --- | --- | --- |
| Features §4 complete fields | 3.3-A/AC07; 3.3-B/AC08 | Typed metadata/classification/units/category/allowance/proration/cap/carry/expiry/duration/notice/dates/funding/documents/privacy/approval settings and real four-section editor are present. |
| L-0127/defaults | 3.3-A/AC08 | New automatic policy proposes upfront/adjustment while preserving explicit existing choices; no assignment/grant from publication. |
| Conditional field combinations | 3.3-A/AC09; 3.3-B/AC08 | Carry/cap/final-position/document dependencies validate; hidden incompatible values cannot silently publish. |
| Strict threshold/horizon | 3.3-A/AC10; 3.20/AC02/07 | Exactly two versus three days, duration bounds and every-date horizon use authoritative results. |
| L-0133/0134/0135/0140 | 3.34-A/AC10; 3.28/AC09 | First confirmed future assignment locks used basis/category; unused publication/draft choice does not. No cancellation approval/cutoff option is inferred from old generalized fields. |
| L-0143 initial coverage | 3.11/AC08 | Later employment/assignment start; 1 July 2026 18×184/365 adjusted versus full, before conversion/floor. |
| L-0136/0137/0141 upfront gaps | 3.11/AC09; 3.36-A/AC04 | Retain earned/expiry, no uncovered earning or duplicate upfront grant on resumption/replacement; employment departure stays separate. |
| L-0142 monthly covered intervals | 3.13/AC08/11 | 15/30 employed-and-assigned gives .75 adjusted or 1.5 full once; no covered days none; repeated assignment cannot multiply periods. |
| L-0144 later availability | 3.13/AC09 | Covered .75 portion survives coverage ending and becomes usable 30 April, not before; retained funding alone grants no outside-coverage request authority. |
| L-0145 start-available reconciliation | 3.13/AC10 | Ending 15 April recalculates 1.5→.75 adjusted or 1.5 full; no duplicate posted deduction/approved rewrite. |
| First actual source writers | 3.28/AC08 | Real E2 source edits consume actual entitlement review/history/notice protection before assignment activation, not later E5 or mock-only evidence. |
| Override-aware change notices | 3.34-A/AC09 | Effective/first-usable dates and actual employee amounts remain accurate when explicit overrides continue. |

Seventeen explicit Given/When/Then witnesses were appended to seven existing E3 leaves.
No original criterion was removed or rewritten. The early-size assessment was refreshed
against the expanded actual acceptance, with the same 48 E3 leaves and no duplicate 3.40.

Accepted precedence applies to old discussion paragraphs: L-0103/0105 fix rounding,
L-0106 removes posted daily accrual, L-0129 fixes equal-expiry priority, L-0135 distinguishes
untracked from manual zero, L-0151 removes renewed response for later pending changes,
and L-0162 closes an initial response when its current unpaid amount reaches zero.
Old 2.23/3.14/3.16/3.21/3.30 acknowledgement phrases cannot restore the superseded gate.
Original E5 criteria and accepted ADRs remain untouched.

## Remaining coverage boundary

This closes the specifically identified policy-field/coverage-gap/arithmetic witness
omissions and binds all 36 existing CALC source rows. It is not an exhaustive semantic
pass for all Features, Permissions, shared/Leave UX states, exclusions and NFR clauses.
Those remain G01's final bidirectional reconciliation. The source-unit index is still
navigation; executable tests and exact commands bind during authorized delivery.
