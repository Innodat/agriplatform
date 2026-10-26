# E7 source allocation and planned verification

**Prepared:** 2026-10-25. **Status:** Proposal for the single E7 review.
This maps source obligations to delivery/acceptance boundaries, not a new feature spec
or executed test suite. There are 48 obligation clusters and 31 candidates with 124
specific AC IDs. Compound clusters can require several real tests; this is not final
whole-product atomic coverage. Every actual test keeps its source clause, E7-xx-ACyy,
owner/fixture, observed acceptance failure, exact red/green commands/results and limits.

## Obligation-to-consumer map

| ID | Source | Obligation / oracle | E7 consumers | Planned evidence |
| --- | --- | --- | --- | --- |
| E7-R01 | Features §17; L-0065 | Current organization overview across departments, no cross-org/detail/action grant by role name | 7.1, 7.6 | API/Access consumer |
| E7-R02 | UX Organization overview; PRIV-15 | Current-month default, Previous/Today/Next and custom range; filters survive navigation | 7.1, 7.2, 7.3 | API/browser |
| E7-R03 | UX Organization overview; PRIV-15 | Approved plus distinctly awaiting approval; negative closed outcomes remain history | 7.1, 7.2, 7.3 | query/browser |
| E7-R04 | UX Organization overview; PRIV-15 | Default employees with leave, explicit Show all constrained by authorization/filters; search never enables it | 7.1, 7.3 | query/browser |
| E7-R05 | Features §18 | Department/team/location/status/date filters; type filtering only where allowed | 7.1, 7.3, 7.29 | API/filter-privacy |
| E7-R06 | UX Organization overview | Remember valid applied filters per account/org; no private cross-context selections | 7.4, 7.5 | native/API/browser |
| E7-R07 | P-0051; platform mobile filter pattern | Provisional edit/Reset until Apply; Close/Back discards; truthful preference failure | 7.3, 7.4, 7.5 | browser/native |
| E7-R08 | UX Organization overview; PRIV-16 | Timeline/List, current detail and full range, preserved dates/filter/scroll/focus; no drag/resize amendment | 7.2, 7.3, 7.29 | browser/API |
| E7-R09 | UX Organization overview; PRIV-17 | Continuous Friday–Monday calendar span differs from charged working duration | 7.1, 7.2, 7.29 | query/browser |
| E7-R10 | L-0074; UX overview | Individually selectable stacked partial requests; no invented exact absence times | 7.1, 7.2, 7.3, 7.29 | API/browser |
| E7-R11 | UX Organization overview; PRIV-17/18 | Employee-specific nonworking shading, fixed names/headings, readable date cells, continuation markers | 7.1, 7.2, 7.29 | browser/accessibility |
| E7-R12 | Features §18; UX overview | Location-aware holiday labels; multi-location holiday does not mean everyone is off | 7.1, 7.2, 7.29 | query/browser |
| E7-R13 | Features §18; L-0011/0074 | Colleague Unavailable/Part-day absence privacy across API/filter/group/style/export | 7.1, 7.19, 7.29 | API/browser/export |
| E7-R14 | L-0013; Features §18 | Current manager type/note/history boundary remains independent of medical document permission | 7.1, 7.25, 7.26, 7.27 | API/private-read |
| E7-R15 | L-0065/0066; UX manager home | Independent management tools and mobile full-row targets despite empty/failed attention | 7.6, 7.8, 7.27 | browser/accessibility |
| E7-R16 | Features §19 | Current employee/type balance report uses E3 remaining/reserved/available and proper work-local basis | 7.7, 7.8, 7.28 | actual calculation adapter |
| E7-R17 | Features §19; L-0107; proposed L-0169 | Dated balance uses corrected known effective history, original approval evidence distinct | 7.7, 7.8, 7.28 | query/native |
| E7-R18 | L-0125; proposed L-0169 | Current staffing groups versus effective-date report groups; no named teams or permission inheritance | 7.1, 7.7, 7.9, 7.11, 7.13, 7.15, 7.17 | People HTTP/query |
| E7-R19 | L-0125; proposed L-0169 | Split usage at a mid-request supervisor change, conserve minutes and separate non-additive request count | 7.11, 7.12, 7.28 | query/aggregate |
| E7-R20 | P-0042; Features §2/19 | Retained former/accountless employee history remains reportable within current scope, no synthetic account | 7.7, 7.9, 7.11, 7.17 | People/Leave query |
| E7-R21 | Features §6/19; L-0106 | Accrual/adjustment report explains derived versus actual events without posted daily grants or duplicate earning | 7.9, 7.10, 7.28 | E3 adapter/query |
| E7-R22 | Features §19; L-0074 | Used leave by employee/type/team/period counts actual duration once, not funding lines | 7.11, 7.12, 7.28 | query/aggregate |
| E7-R23 | Features §11/17; E6 contract | Cancelled original excluded from current absence; replacement uses actual state with unresolved follow-up explicit | 7.11, 7.12, 7.13, 7.14 | query/correction consumer |
| E7-R24 | Features §19; UX overview/report | Upcoming approved and distinctly pending intersection with full range and scoped current grouping | 7.13, 7.14 | query/browser |
| E7-R25 | Features §19; E5 clocks | Aging uses actual required current pending steps and preserved wait clocks; no duplicate requests or invented age for a blocker | 7.15, 7.16, 7.28 | E5 query adapter |
| E7-R26 | Features §19; E3/E5 source contracts | Override/adjustment report distinguishes recurring/reset, request exception and one-off action evidence | 7.17, 7.18 | query/source adapters |
| E7-R27 | Features §19 | Override action totals do not count ledger/allocation/step lines repeatedly; mixed kinds no fake common total | 7.17, 7.18, 7.28 | query/aggregate |
| E7-R28 | L-0135; E3 minute/conversion contracts | Not balance-limited is not zero/infinite; untracked usage real; incompatible day denominators not summed | 7.7, 7.9, 7.11, 7.17, 7.28 | typed contract/CSV |
| E7-R29 | Features §19; UX Reports | Six report definitions keep relevant filters/date basis/explanations and independent truthfully failed/empty states | 7.8, 7.10, 7.12, 7.14, 7.16, 7.18 | browser/query |
| E7-R30 | Features §19; UX flow 12 | CSV all matching authorized rows across pages with identical normalized query/fields, not browser-visible page | 7.19, 7.20, 7.28 | native/API/browser |
| E7-R31 | P-0025; Features §20 | Required durable export-generation authorization evidence before bytes; failure blocks release, download receipt not claimed | 7.19, 7.28 | native/HTTP failure |
| E7-R32 | Features §18/19; P-0023 | CSV field/privacy parity, Unicode/quotes/formula-like text safe, no business payload dumps | 7.19, 7.20, 7.28 | serializer/client |
| E7-R33 | Platform collection/export states | Export failure retains report and Retry export; old response cannot cross changed user/org/query | 7.20, 7.28 | browser/session |
| E7-R34 | Features §20; E1 audit ownership | Local audit uses actual producer evidence; no new full autosave history or fabricated committed failure | 7.25, 7.30 | native/query |
| E7-R35 | Features §20; P-0025/0056 | Audit durable actor/membership/UTC/action/resource/operation/correlation/reason/on-behalf attribution survives account changes | 7.21, 7.22, 7.23, 7.24, 7.25, 7.30 | owner API/native |
| E7-R36 | P-0003/0040; E1 audit ownership | Access/Identity evidence read remains source-owned and Leave/org/user scoped | 7.21, 7.26 | actual owner HTTP |
| E7-R37 | P-0041/0042/0062; E1 audit ownership | People evidence read/history remains source-owned and separate from Leave write authority | 7.22, 7.26 | actual People HTTP |
| E7-R38 | P-0054/0055; Features §20 | Content attachment/sensitive-read evidence projected without medical byte/metadata access bypass | 7.23, 7.26, 7.27 | actual Content HTTP |
| E7-R39 | Features §20; E3 notification contract | Delivery administration business audit is distinct from diagnostic attempt logs and message payloads | 7.24, 7.25, 7.26 | actual notification HTTP |
| E7-R40 | UX Audit history; PRIV-20 | Chronological when/who/what/why search with employee/action/date filters and permitted before/after links | 7.25, 7.26, 7.27, 7.30 | query/browser |
| E7-R41 | Features §18/20; PRIV-20 | Authorize before text matching/highlighting/counts; audit link rechecks field/resource and medical permissions | 7.25, 7.26, 7.27, 7.30 | API privacy |
| E7-R42 | P-0022; E5 read contract | Audit owner merge bounded/no cross-service DB transaction/frozen snapshot promise; current per-page scope | 7.21, 7.22, 7.23, 7.24, 7.26, 7.30 | HTTP/native |
| E7-R43 | E1 audit ownership; UX collection states | Missing source/retention/unsupported evidence cannot masquerade as empty-complete audit | 7.21, 7.22, 7.23, 7.24, 7.26, 7.27 | HTTP/browser failure |
| E7-R44 | Features NFRs; L-0108 | 100/1000 employee multi-year/5 readers/1 export workload, explicit row/window/time/memory limits and proposed targets | 7.1, 7.7, 7.19, 7.26, 7.31 | measured qualification |
| E7-R45 | P-0020; focused migration verification | Compatible schema/index/client adoption, real runtime RLS/DDL/owner denial and failure-blocked activation/recovery | 7.4, 7.19, 7.21, 7.22, 7.23, 7.24, 7.25, 7.31 | actual native/release |
| E7-R46 | Features UX/NFRs; browser policy | Actual keyboard/focus/mobile/status contrast and supported browser evidence, English/Portuguese readiness | 7.2, 7.3, 7.5, 7.6, 7.8, 7.10, 7.12, 7.14, 7.16, 7.18, 7.20, 7.27, 7.29, 7.31 | browser/accessibility |
| E7-R47 | AGENTS; P-0007/0059 | Five impacts per item, generator/template/managed copies maintained by owner with consuming proof | 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15, 7.16, 7.17, 7.18, 7.19, 7.20, 7.21, 7.22, 7.23, 7.24, 7.25, 7.26, 7.27, 7.28, 7.29, 7.30, 7.31 | owning delivery record |
| E7-R48 | Features §18; existing E5/E6 boundaries | Report/overview reads never create approvals, grants, reservation effects, correction or private file access | 7.1, 7.7, 7.9, 7.11, 7.13, 7.15, 7.17, 7.25, 7.26 | API/native read-only |

## Report family coverage and duplicate disposition

| Family | API / browser | Export proof |
| --- | --- | --- |
| Current and dated balances | 7.7 / 7.8 | 7.19/20/28, corrected-versus-original evidence and untracked rows |
| Accrual and adjustment history | 7.9 / 7.10 | 7.19/20/28, derived/actual source identities and period totals |
| Leave used by employee/type/team/period | 7.11 / 7.12 | 7.19/20/28, per-date effective grouping and conserved minutes |
| Upcoming absence | 7.13 / 7.14 | 7.19/20/28, approved/pending intersection and full original range |
| Pending approval aging | 7.15 / 7.16 | 7.19/20/28, real waiting-clock/nested steps and distinct request count |
| Overrides and administrative adjustments | 7.17 / 7.18 | 7.19/20/28, action identity, explicit kinds and no repeated allocation lines |

BIZ-32/33/34 and PRIV-15–20 are direct E7 work above. PRIV-01–08/10–14 are inherited
privacy/state/navigation/filter controls exercised by real E7 API/browser consumers.
CALC-01–22/27/31–35 remain E3/E5/E6 arithmetic/history/coordination owners; E7 reads
actual results with its corrected-history/grouping/aggregate adapters. FLOW waiting/
reminder/coverage rules remain E5, read only by aging/overview. E8 import, exact-batch
client email evidence, restoration/pilot and full release signoff remain E8. No current
query/test claim certifies an upstream planned service as implemented.

Every source §17/18/19/20 obligation is either directly mapped above or inherited:
management configuration/corrections/on-behalf remain E2/E3/E5/E6, own request and
assigned details remain E5, sensitive private reads remain E4, source audit capture
stays with each originating writer, technical delivery recovery stays with actual
E3/shared notification operators. The E7 screen adds read/search only. Capacity remains
informational; organization overview adds no booking limit or automatic action.

## Exact authority fingerprints

These hashes preserve the selected E7 authority sections/UX during preparation. They
are drift checks, not proof of semantic completeness. ADR-0169 remains proposed;
accepted predecessors and source behavior are not silently amended.

| ID | Source / section | SHA-256 |
| --- | --- | --- |
| E7-S01 | apps/leave/docs/features.md: 17. Leave Manager workspace | `1d770d53dbd1c11c7a5aac7aec8235db2b8c04e348b4ac35e58c894f7f3570fd` |
| E7-S02 | apps/leave/docs/features.md: 18. Calendars and privacy | `2ac4a874b4517ce5ceefdabfbc83ba96264d79adbf6a38a4e4e67c30cb48c6cf` |
| E7-S03 | apps/leave/docs/features.md: 19. Reports and exports | `5afc01f00ac9fb6e1e269fc986de04f3ffdffacfabd367bb33a07bacb7e6cf4f` |
| E7-S04 | apps/leave/docs/features.md: 20. Audit and operational administration | `d3281e2139c1c44f1f3b82ef6b1e5e32543c8d4e2416cdf4ee4bd08f355af896` |
| E7-S05 | _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md: Organization leave overview | `f976473a79471adc704b6e4957f86798d69289a321d4b25fd7f472bb53e26dc8` |
| E7-S06 | _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md: Reports | `518c31fd69d4088318f1f10047bc696966ce00ac4743966f474931f826593005` |
| E7-S07 | _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md: Leave Manager audit history | `030a9ed0ec167a260694511b536a876fd8513f6bcb976d037a90bc15bfedf3e4` |
| E7-S08 | apps/leave/docs/architecture/decisions/0125-supervisor-based-teams-for-mvp.md: ADR-0125: | `703b23e42cf8f5f2f769ba44717e2c71e59bc075103bc174a1981c0d7f36fb45` |
| E7-S09 | apps/leave/docs/architecture/decisions/0107-corrected-balances-preserve-decision-evidence.md: ADR-0107: | `f1ff531ed0a6e2843d11039ddd9c65aecd2b07bd133c5d08e91565ead0fa7bfd` |

## Verification limits

Document audits check candidate/AC uniqueness, exact dependency/size rows and earlier-only
acyclic order, six report pairs/four shared audit sources, 48 obligation IDs, these nine
source fingerprints, relative file/heading links and unchanged pre-E7 story bodies. The
prior E5 graph/230-criterion audit is rerun. Source/owner and first-use reconciliation is
recorded separately; counts and hashes cannot prove runtime correctness or full semantics.
No API/browser/native/DB/migration/release/performance tests ran. Exact executable artifacts,
fixtures, typed owner route/credential adapters, generated clients and acceptance evidence
remain actual consuming delivery work before readiness/activation. Proposed product choices
await the user's single review. No live or application implementation changes occurred.

### Accepted authority refresh — 2026-10-25

E7 and both ADR-0169 choices were accepted by the user. Report-related source fingerprints deliberately include the approved temporal
clarifications and their section boundaries. Earlier proposed-choice/check wording is historical; no other source
section or acceptance expectation was changed to dismiss a failure.

**Source consistency update — 2026-10-26:** Features §17 now names applicable correction authority and separately assigned approval authority, adopting already Accepted L-0168/L-0149. Its recorded source fingerprint was deliberately refreshed after those two wording changes. E7 report definitions, original stories/criteria and accepted ADR-0169 are unchanged.
