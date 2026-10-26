# E6 source allocation and planned acceptance evidence

**Date:** 2026-10-25. **Status:** Planning allocation for the single E6 review.
Source requirements remain in Features/ADRs/UX; these rows are traceability and test
ownership, not a replacement requirements specification or executed tests.

The register has 50 reviewed obligation clusters, including shared controls. They map
to the 46 candidates and their 138 specific AC IDs in epics. A cluster may require
several concrete tests; these counts are not atomic whole-product coverage or readiness.
Each concrete delivery test must retain its source clause, family variant, actual fixture,
AC ID, exact command/red/green result and limits. Common foundations are referenced once;
every actual source variant still needs its own real producer/integration proof.

## Source obligation to owner and boundary

| ID | Authoritative source | Obligation / oracle | Candidate consumers | Primary allocation | Planned evidence boundary |
| --- | --- | --- | --- | --- | --- |
| E6-R01 | Features §11; L-0010 | Cancel approved leave without another approval round | 6.5, 6.6 | 6.5 | API/native |
| E6-R02 | Features Permissions; L-0152 | Own future cancellation; deny started/past without correction authority | 6.5, 6.6, 6.43 | 6.5 | API/browser boundary |
| E6-R03 | Features Permissions; L-0152; proposed L-0168 | Standard/custom/temporary cancellation rights and current target population | 6.5, 6.6, 6.11, 6.43 | 6.5 | Access consumer/API |
| E6-R04 | Features §11; L-0010 | New replacement ID, fresh cycle/validation/approval; no old decision transfer | 6.9, 6.10 | 6.9 | API/native |
| E6-R05 | UX Change approved leave | Invalid replacement leaves original intact and preserves entered input | 6.9, 6.10, 6.43 | 6.9 | native/browser |
| E6-R06 | Features §17; UX Administrative leave correction | Later administrative replacement rejection leaves original cancelled and visible follow-up | 6.7, 6.8, 6.44 | 6.7 | real reject producer |
| E6-R07 | Features §7; L-0052/0053 | Past/current/future correction requires current scoped manager and on-behalf authority | 6.11, 6.12 | 6.11 | API/Access consumer |
| E6-R08 | Features §7; L-0053 | Organization Administrator alone, ordinary approval and temporary-only denied | 6.11, 6.12 | 6.11 | API negative |
| E6-R09 | Features §7/11; L-0074 | Replacement preserves daily active-duration limit across types and concurrent attempts | 6.9, 6.11, 6.43 | 6.9 | native concurrency |
| E6-R10 | Features §6 cancellation example; L-0038 | Cap 20, take original 5, earn 2, other 4 leaves 13; cancel gives 16 | 6.4, 6.5, 6.43 | 6.4 | arithmetic/native |
| E6-R11 | Features §6; L-0038 | Retain other actual events and reverse only earning enabled by target booking | 6.4, 6.5 | 6.4 | arithmetic/property |
| E6-R12 | Features §6; L-0038/0129 | Original source periods/expiry and multi-source provenance survive restoration | 6.4, 6.5 | 6.4 | arithmetic/native |
| E6-R13 | Features §6; L-0135 | Untracked usage cancelled without invented entitlement; all-unpaid no paid grant | 6.4, 6.5, 6.9 | 6.4 | typed contract/native |
| E6-R14 | Features §6; L-0038/0039 | Spent extra earning creates visible deficit, no new cancellation approval or automatic unpaid rewrite | 6.2, 6.3, 6.4, 6.5 | 6.5 | API/native |
| E6-R15 | Features §6; L-0039 | Only scoped manager with balance-adjustment authority reviews deficits | 6.15, 6.16 | 6.15 | API negative |
| E6-R16 | UX Balance-deficit review | Keep open with reason and employee explanation | 6.15, 6.16 | 6.15 | API/browser |
| E6-R17 | UX Balance-deficit review | Correct source choice uses separate authority/real outcome; does not itself change facts | 6.15, 6.16 | 6.15 | HTTP/API/browser |
| E6-R18 | UX Balance-deficit review | Additional entitlement is separate explicit audited adjustment; review creates none | 6.15, 6.16, 6.19, 6.20 | 6.15 | native/API |
| E6-R19 | UX Balance-deficit review | Record handling without adjustment may finish review while retaining economic deficit | 6.15, 6.16 | 6.15 | API/browser |
| E6-R20 | Features §6/17 | New/material changed deficit cannot be dismissed by an old review revision | 6.2, 6.15 | 6.2 | native concurrency |
| E6-R21 | Features §6; L-0107 | Approval snapshot 10 retained, revised historical result 9 explained | 6.1, 6.17, 6.41 | 6.1 | contract/native |
| E6-R22 | Features §6; L-0107 | Current corrected balance includes subsequent events, not simply historical replacement amount | 6.1, 6.17, 6.41, 6.45 | 6.1 | arithmetic/native |
| E6-R23 | Features §6; L-0111 | Retained input values/immutable versions and separate calculation version, no read snapshots | 6.1, 6.4, 6.5 | 6.1 | API/native |
| E6-R24 | Features §6; L-0112 | Changed consequential inputs require renewed review; no arbitrary source backdate | 6.1, 6.5, 6.9, 6.19, 6.21, 6.23, 6.25, 6.27, 6.29, 6.31, 6.33, 6.35, 6.37, 6.39, 6.41 | 6.1 | native/source contract |
| E6-R25 | Features §6; L-0128 | Discretionary approved-impact change blocked until real authorized resolution | 6.19, 6.21, 6.23, 6.25, 6.27, 6.29, 6.31, 6.33, 6.35, 6.37, 6.39 | 6.1 | actual source API |
| E6-R26 | Features §6; L-0128 | Necessary factual correction retains reason, consequences and unresolved deficit attention | 6.29, 6.30, 6.41, 6.42 | 6.29 | actual People/Leave HTTP |
| E6-R27 | Features §7; L-0048 | April 480→240 at 15 April with proration, full 480 if no-proration | 6.29, 6.30, 6.45 | 6.29 | existing E3 calculation + producer |
| E6-R28 | Features §7; L-0049 | 30 June eligible, 1 July invalid; existing affected dates flagged, never trimmed | 6.29, 6.30, 6.45 | 6.29 | existing E5 gates + producer |
| E6-R29 | Features §7/13; L-0054/0151 | Administrative correction sends minimal email and in-app notice, authorized detail actor/reason | 6.5, 6.11, 6.15, 6.44 | 6.11 | outbox/recipient/channel consumer |
| E6-R30 | Features §7; L-0151 | Later pending unpaid increases/decreases notify without renewed employee gate | 6.1, 6.5, 6.19, 6.21, 6.23, 6.25, 6.27, 6.29, 6.31, 6.33, 6.35, 6.37, 6.39, 6.41 | 6.1 | existing source producer adapters |
| E6-R31 | Features §8; L-0088/0162 | New on-behalf replacement has own initial employee response; zero closure/current amount remain E5 | 6.9, 6.11, 6.13, 6.44 | 6.11 | API/native response race |
| E6-R32 | Features §11/17; L-0009/0159; UX correction | Authorized administrative rejected replacement uses same request ID/new cycle and preserved correction input | 6.13, 6.14, 6.44 | 6.13 | API/browser |
| E6-R33 | P-0050/0051; L-0159 | Autosave rejected correction only; inline Retry, exit-only Stay/Close anyway | 6.13, 6.14 | 6.14 | browser |
| E6-R34 | P-0033; L-0159 | Employee/manager revision races and late save cannot overwrite/resurrect closed cycle | 6.13, 6.14, 6.44 | 6.13 | native/browser |
| E6-R35 | UX Administrative leave correction | Corrected main entry separate from status; original cancelled in history, no duplicate current absence | 6.17, 6.18 | 6.18 | query/browser |
| E6-R36 | Features §14/18; PRIV-03 | Current history access, original decision attribution, no private documents by implication | 6.5, 6.11, 6.17, 6.18 | 6.17 | API/private-read |
| E6-R37 | Features §17; BIZ-32 | Independent tools remain available; empty/filtered/unavailable distinct | 6.2, 6.3, 6.8, 6.16 | 6.3 | browser |
| E6-R38 | UX flows 4/5; P-0032 | Preserved return/filter/year/focus context, same authorized user, no automatic confirmation | 6.6, 6.10, 6.12, 6.14, 6.16, 6.18 | 6.6 | browser/session |
| E6-R39 | P-0012/0013/0031 | Original operation identity, changed-input conflict, stale revision, safe typed errors | 6.5, 6.9, 6.13, 6.15 | 6.5 | native/API/client |
| E6-R40 | P-0022/0035; L-0112 | Complete protected source/ref/employee sets, new member races and no external waits under locks | 6.5, 6.9, 6.19, 6.21, 6.23, 6.25, 6.27, 6.29, 6.31, 6.33, 6.35, 6.37, 6.39, 6.41 | 6.5 | native/HTTP |
| E6-R41 | P-0025/0056 | Actual actor, initiator/executor, UTC attribution and immutable audit | 6.5, 6.9, 6.11, 6.13, 6.15, 6.41 | 6.5 | native/API |
| E6-R42 | P-0023; L-0014/0015 | Safe diagnostics; no sensitive reason/note/document in notices/receipt dumps | 6.5, 6.9, 6.11, 6.15, 6.46 | 6.5 | API/log/privacy assertions |
| E6-R43 | P-0054/0055; E4 | Separate authorized fixed-byte associations, original retained, no bearer private reads | 6.9, 6.11, 6.17 | 6.9 | actual Content consumer |
| E6-R44 | P-0040/0042/0062 | People owns corrected dates/history, enduring employment and accountless target; no grants inferred | 6.29, 6.30, 6.41, 6.42 | 6.41 | People native/HTTP |
| E6-R45 | P-0062; E5 source protocol | Prepared-source commit/cancel fencing and real source versus consequence recovery | 6.29, 6.41, 6.45 | 6.29 | two-owner HTTP/native |
| E6-R46 | L-0154; E5 5.25/5.28 | Cancellation absence-end affects current cover/gaps/reassessment; no invented decision or hidden read side effect | 6.5, 6.9 | 6.5 | real producer/worker |
| E6-R47 | P-0028; L-0114–0117 | Versioned actual notice intents, dated wording, delayed/reversed/retry compatibility and unsupported work retained | 6.5, 6.9, 6.11, 6.15, 6.46 | 6.46 | producer/receiver/release |
| E6-R48 | P-0020; focused migration verification | Controlled compatible migration, previous consumers, failure blocks activation and explicit recovery | 6.5, 6.9, 6.15, 6.41, 6.46 | 6.46 | actual native/release |
| E6-R49 | Features NFRs; L-0108/0113 | 100/1000 employee multi-year measured replay, bounded fail before mutation; no speculative cache/worker | 6.1, 6.4, 6.19, 6.29, 6.41, 6.46 | 6.46 | performance/native |
| E6-R50 | P-0007/0059; AGENTS | Same-item neutral scaffold/shared-UI/agent/docs/ADR decisions, generated sources maintained by owner | 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12, 6.13, 6.14, 6.15, 6.16, 6.17, 6.18, 6.19, 6.20, 6.21, 6.22, 6.23, 6.24, 6.25, 6.26, 6.27, 6.28, 6.29, 6.30, 6.31, 6.32, 6.33, 6.34, 6.35, 6.36, 6.37, 6.38, 6.39, 6.40, 6.41, 6.42, 6.43, 6.44, 6.45, 6.46 | all | owning consumer evidence |

## Eleven source families — complete variant disposition

The exact F01–F11 variant list is inherited from the E5 coverage audit, including its
actual source owners. Ordinary pending integration and approved-impact activation safety
stay in E5. These rows allocate the **additional** historical/approved correction delta.
An illegal retrospective mutation remains denied; E6 cannot bypass effective-date rules.

| Family | Actual source and inherited integration | E6 API / browser | Required extra scenario |
| --- | --- | --- | --- |
| F01 | Features §6; L-0107/0112/0128/0151; existing 3.29 and 5.15-A/B | 6.19 / 6.20 | Only the one-off balance adjustments API delta over actual 3.29 / 5.15-A/B; permission leave.balance.adjust; variants: Add and Deduct, including a correction of an earlier adjustment through another explained entry. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F02 | Features §6; L-0107/0112/0128/0151; existing 3.30 and 5.15-C/D | 6.21 / 6.22 | Only the recurring entitlement changes API delta over actual 3.30 / 5.15-C/D; permission leave.policy.manage; variants: explicit recurring allowance and return to policy at an actual leave-period boundary. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F03 | Features §6; L-0107/0112/0128/0151; existing 3.34-A/B and 5.15-E/F | 6.23 / 6.24 | Only the used-policy publication API delta over actual 3.34-A/B / 5.15-E/F; permission leave.policy.manage; variants: allowed used-policy transitions with actual holders, dated versions and approved request snapshots. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F04 | Features §6; L-0107/0112/0128/0151; existing 3.35-A/B and 5.15-G/H | 6.25 / 6.26 | Only the scheduled policy amendments and cancellations API delta over actual 3.35-A/B / 5.15-G/H; permission leave.policy.manage; variants: both amend and cancel before the first affected effect; already-effective changes use the existing prospective path. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F05 | Features §6; L-0107/0112/0128/0151; existing 3.28/3.36-A/B and 5.15-I/J | 6.27 / 6.28 | Only the employee policy assignments API delta over actual 3.28/3.36-A/B / 5.15-I/J; permission leave.policy.manage; variants: initial, replacement and end assignment, including gaps and original earned-period/expiry provenance. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F06 | Features §6; L-0107/0112/0128/0151; existing 2.11/12/13 and 5.15-K/L | 6.29 / 6.30 | Only the employment periods and departure API delta over actual 2.11/12/13 / 5.15-K/L; permission People owner authority plus separately authorized Leave consequences; variants: initial verified empty case, period-add/rehire and employment end, including spent upfront grants and after-end requests. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F07 | Features §6; L-0107/0112/0128/0151; existing 2.22 and 5.15-M/N | 6.31 / 6.32 | Only the employee work-setting overrides and resets API delta over actual 2.22 / 5.15-M/N; permission leave.schedule.manage; variants: each explicit field and real reset to inheritance, including timezone, calendar and standard-day changes. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F08 | Features §6; L-0107/0112/0128/0151; existing 2.20 and 5.15-O/P | 6.33 / 6.34 | Only the employee work-profile assignments API delta over actual 2.20 / 5.15-O/P; permission leave.schedule.manage; variants: initial/change/end explicit profile selection and actual fallback-to-default users. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F09 | Features §6; L-0107/0112/0128/0151; existing 2.21 and 5.15-Q/R | 6.35 / 6.36 | Only the organization-default work profiles API delta over actual 2.21 / 5.15-Q/R; permission leave.schedule.manage; variants: empty/default replacement, actual followers and partial overrides without touching unrelated explicit settings. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F10 | Features §6; L-0107/0112/0128/0151; existing 2.23 and 5.15-S/T | 6.37 / 6.38 | Only the shared work-profile publication API delta over actual 2.23 / 5.15-S/T; permission leave.schedule.manage; variants: explicit holders, default followers, partial overrides and concurrent new holders of actual published versions. Reuse the common projection, guards, replay, outcome and notice machinery. |
| F11 | Features §6; L-0107/0112/0128/0151; existing 2.18 and 5.15-U/V | 6.39 / 6.40 | Only the holiday-calendar changes API delta over actual 2.18 / 5.15-U/V; permission leave.calendar.manage; variants: add/edit/remove, absent slots, full/partial closure and downstream earning effects outside directly intersecting request dates. Reuse the common projection, guards, replay, outcome and notice machinery. |

F06 separately consumes 6.41/42 for factual recorded start/historical-period corrections.
No duplicate employment source or new person is created. Supervisor-only changes, optional
department/location, Access changes and appointment/transfer/return retain E2/E5 owners;
they do not acquire a new balance-correction path. Type/profile creation/archive/restore
retain existing structural dependency/no-impact checks, and used tracked/untracked mode
remains fixed. Any future legal source adapter must join the same actual writer protection.
E8 import must use the approved contracts, not alternate unguarded database writes.

## Existing cross-epic inventory disposition

- BIZ-04/07/08/11/12: E2/E3/E5 foundations reused; E6 actual correction consumers here.
- BIZ-13/25/26: E6 direct allocation, particularly R04–07, R10–29 and R44–45.
- BIZ-24: employee rejected lifecycle stays E5; narrow administrative extension R32–34.
- BIZ-31/32: E6 linked history/deficit/follow-up only; E7 broader organization/report scope.
- CALC-23/24/25/28: existing allocation/pending/exception/daily-limit rules consumed;
  CALC-26/31/32 have explicit historical/cancellation oracles above. CALC-35 measurement
  remains first-consumer/E8 qualification, with E6 delta 6.46.
- FLOW-13/23: existing coverage/reminder lifecycle stays E5; cancellation supplies its
  real absence-end/closed-work consequence. FLOW-27 is E6 direct.
- PRIV-03/13/21/22: actual authorized linked history, reviewed changes, saving and session
  recovery consumed here. PRIV-16 organization overview and PRIV-19/20 reports/search
  remain E7. No E6 CSV/export/search screen is introduced.

## Selected authoritative source fingerprint register

Exact paragraph hashes protect the principal correction clauses against silent drift.
They are a selected source snapshot, **not** a mechanical proof all requirements are covered.
Superseded acknowledgement wording is retained in its original source and interpreted under
L-0151; it is not copied as a renewed-gate criterion. IDs below reference exact current
Features paragraphs (whitespace preserved apart from leading/trailing paragraph whitespace).

| Source ID | Paragraph beginning | SHA-256 |
| --- | --- | --- |
| E6-S01 | Automatic entitlement is calculated authoritatively by the backend for the relevant | `2c7798a0b4413b6e0cb5b0debf68bc94284ac5a5ce0ab6b6f4a0aea77e590e19` |
| E6-S02 | Recalculation after a cancellation or historical correction means evaluating updated | `f49aad932e5f14331b7b7ca25b3b706c1db6f9999d53fb5e3546f11c2b928420` |
| E6-S03 | If employment ends after an upfront grant, recalculate the affected period's grant | `30f9e76c9f343e3dce90f7233158565a448f3e5c5b48fdc026cd1d05b488618f` |
| E6-S04 | Acceptance example: A start-of-month policy grants 480 minutes for April. An | `fc1f0b71d42a3725bbbf49d25a930293f7604d5951e2f292f504e707270fa160` |
| E6-S05 | Block new submission and final approval when any requested leave date falls after | `8777990df988c9aafaa23d800683505a4e35566cc8d8c247426157e2ab6b6c62` |
| E6-S06 | Authorized administrative correction must support past, current, and future leave | `c526418942597cc9510927c40c8a06b5d7b5e2be4a2ef183fe6255c9951acb35` |
| E6-S07 | Acceptance example: An in-scope Leave Manager with `leave.admin.on_behalf` can | `f84f179145d43a146aab657ea7d4ba03cf142e3331e5e223f5aef8760e42db7b` |
| E6-S08 | Notify the employee by email and in-app notification whenever an administrator | `b90aa6a97c2323772bf8b29023c8c8b4717efabf14f38d065429dd41115a68f0` |
| E6-S09 | When approved leave is cancelled, recalculate affected capped accrual as if that | `24d4ab6d3e85d7007970ff3ebe08087bc71b186c5f141703114e00c28ccd2809` |
| E6-S10 | Acceptance example (all day amounts use the employee's schedule): At a 20-day cap, | `f54c934a0636e38f495ab2d561c107ff213e609f4369a9e3d6748a494b9bdaf1` |
| E6-S11 | A Leave Manager with `leave.balance.adjust` within the authorized NGO/resource | `7cef1985159ce4e548074619440d4731b36ec97e9d83ed346f3912c6c72335ff` |
| E6-S12 | A rejected administrative correction appears as **Correction needs follow-up** in | `a8ac1eb54dcb691fb1bc6ac8e556a43dc59e5b8c601cfb3164d17cf7691c1728` |
| E6-S13 | Approved-cancellation defaults — accepted 2026-10-22 under | `b327dee46f8362a0bfcb54ef1095ba0258fb76441e1e7f18cdceab297b1b7b6b` |
| E6-S14 | Request-impact accountability — agreed 2026-10-13 under | `16c3dc4baf7d9e3ccdc6b02eae80befcb155cef25260e0312c982003ad401127` |
| E6-S15 | No balance tracking — accepted 2026-10-15 under | `1c67ab59867b830d3525551063df7e6d51f7fe0a1ebf995806b52455bda69c80` |
| E6-S16 | The Leave Manager home screen prioritizes escalated approvals and balance deficits | `8c98cd9d29d7cd8942455d2c2752c2a441f6e6ff6e8909939a65de523d713b43` |

## Planning validation versus delivery evidence

The document audit checks 46 unique story headings, 138 AC identifiers, exact graph and
size rows, predecessor existence/order, local file/heading links, these 16 selected source
hashes and unchanged 230 original E5 source-criterion hashes. Scoped whitespace is checked.
It does not execute Leave acceptance tests or prove semantic completeness from text matches.
Semantic reconciliation above separately considers first readers/producers, real source
variants, current permission/time scope and forbidden duplicate work.

Exact executable schema/OpenAPI/generated-client/native/browser fixtures and commands are
future named-owner deliverables before affected readiness. Source review is pending user
agreement; global atomic coverage, E7/E8 and sprint readiness remain open. No application,
database, Access grant, provider, live recipient or deployment was mutated by this planning.

### Accepted-choice source update — 2026-10-25

The user accepted both ADR-0168 choices. E6-S13 was deliberately refreshed after
the approved cancellation paragraph replaced its open-boundary wording. The new
accepted-detail paragraph is linked through ADR-0168 and the existing E6 boundary
scenarios. Historical check results above retain their original scope. E5 source
criteria remain unchanged; no runtime or acceptance test was executed.

## Living-spec supersession alignment — 2026-10-25

Source fingerprints E6-S01 and E6-S03 changed intentionally when whole-product
validation aligned stale renewed-acknowledgement wording to Accepted ADR-0151.
Later pending allocation changes require explanation/notification without a renewed
employee response; initial on-behalf response rules remain separate. Cancellation
wording elsewhere was aligned too. No E5 original criterion or accepted ADR changed.
Refreshed fingerprints establish current-source integrity, not an unexplained
change of expected business results.
