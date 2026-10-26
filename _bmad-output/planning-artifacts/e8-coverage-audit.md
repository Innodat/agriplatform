# E8 source allocation and planned verification

**Prepared:** 2026-10-25. **Status:** Proposal for one E8 review.
There are 48 obligation clusters, 30 candidates and 120 specific AC IDs. These clusters
are not a second feature specification or final whole-product atomic requirements count.
Every actual test keeps source clause → E8-xx-ACyy → owner/fixture/node → observed red →
focused/affected commands/results and limits. No runtime/acceptance/native/provider or
pilot tests were executed in this planning pass.

## Source-to-consumer allocation

| ID | Source | Obligation / oracle | E8 consumers | Planned evidence |
| --- | --- | --- | --- | --- |
| E8-R01 | Features MVP exclusions; migration runbook | Consultant templates and versioned exact source/batch identity; no self-service upload screen | 8.1, 8.4 | CLI/schema/document |
| E8-R02 | Migration runbook source conventions | Source org/system/export timestamp, balance date/timezone, units and original period/expiry captured | 8.1, 8.2, 8.3 | pure normalization |
| E8-R03 | P-0040/0042/0056/0058 | Verified person/accountless/employment/actor mappings; no email-only link, duplicate person/rehire, synthetic grants | 8.2, 8.6 | actual owner HTTP |
| E8-R04 | Migration runbook examples | 8 gross minus future 2 yields 6; already-net 8 stays 8, with no double effects | 8.3, 8.5, 8.11, 8.14 | arithmetic/native/API |
| E8-R05 | Features §6; E3 provenance | Imported history/opening/automatic earning preserve portions/expiry and do not invent entitlement | 8.3, 8.5, 8.6, 8.14 | E3 adapter/native |
| E8-R06 | Features §6; L-0107 | Insufficient prior history/reversal basis is explicit and required pilot scope blocked rather than fabricated snapshots | 8.3, 8.6, 8.11 | preview/native |
| E8-R07 | Migration runbook Validate/review/apply | Row/employee/mapping errors and report differences visible before mutation | 8.1, 8.2, 8.3, 8.4 | CLI/API |
| E8-R08 | Migration runbook step 4; UX flow 15 | Authorized client email proof binds exact report/plan/package/selection; changed data needs renewed approval | 8.4, 8.9, 8.12 | artifact/API |
| E8-R09 | UX setup/migration | No client confirmation page/Awaiting client confirmation or opening balance assumption; manual setup remains | 8.4, 8.12 | docs/actual app |
| E8-R10 | P-0012/0013/0035; proposed L-0170 | Internal adapters commit one employee opening/request/association/evidence/outcome/intent envelope | 8.5, 8.6, 8.7, 8.9, 8.14 | actual native rollback |
| E8-R11 | Proposed L-0170; P-0022 | Successful units survive other failures; no distributed/all-batch atomicity or automatic destructive rollback | 8.9, 8.10, 8.14 | native/CLI |
| E8-R12 | P-0012; migration runbook | Original operation recovery, source uniqueness, changed-payload denial and safe partial status | 8.9, 8.10, 8.14 | native/API/CLI |
| E8-R13 | E5 guard/source/review contracts | Fresh complete source/ref/employee/current capability and revision protection, no remote waits under locks | 8.5, 8.6, 8.7, 8.9 | actual native/HTTP |
| E8-R14 | Features §11/20; P-0025/0056 | Recorded imported approvals carry external provenance, real migration actor distinct, no counterfeit local decision | 8.6, 8.14 | native/history API |
| E8-R15 | Proposed L-0170; E5 initial response | Pending imports new disclosed current cycle/route; old steps historical, no proxy acknowledgement | 8.7, 8.13, 8.14 | API/native |
| E8-R16 | Proposed L-0170; P-0020 | Staged imported economic/read/action scope ineligible before approved activation, prior-consumer compatibility required | 8.5, 8.6, 8.7, 8.9, 8.13, 8.24 | native/read/client/release |
| E8-R17 | Proposed L-0170; E5 waiting clocks | Actual activation anchors new actionable wait, original source submit/wait evidence preserved separately | 8.7, 8.13, 8.14 | clock/API |
| E8-R18 | P-0030/0038/0054/0055; E4 | Document import exact verified bytes/ownership/association/private read, protected staged references | 8.8, 8.9, 8.14 | actual Content HTTP/native |
| E8-R19 | Migration runbook step 6 | Actual applied results reconcile with approved report, never modify expectation to hide mismatch | 8.11, 8.14 | actual query/report |
| E8-R20 | Migration runbook Cutover | Explicit old-system cutoff, balance/source-export times and all intervening request/decision/employment/adjustment deltas | 8.12 | consultant evidence |
| E8-R21 | Proposed L-0170; E3 notifications | No replay of concluded historical notices; held current actions release only with real activation/dedup/relevance | 8.7, 8.13, 8.14 | producer/receiver/API |
| E8-R22 | Features NFRs/MVP 1–6 | Cross-org/API/DB/job/cache/file/export/audit/current field/temporary/custom role threat cases | 8.15 | actual native/HTTP/browser |
| E8-R23 | P-0023; Features NFRs | No credentials/notes/private URLs/payload dumps in logs/traces/errors/public builds/import diagnostics | 8.1, 8.4, 8.15, 8.19 | canary/diagnostic/artifact |
| E8-R24 | Features §12/NFRs | Configurable retention reviewed per client; initial two years after closure is not legal compliance or immediate deletion | 8.16 | settings/Content qualification |
| E8-R25 | E4 cleanup; P-0030 | Draft/pending import/in-flight associations and retained decision/audit protected during auditable disposal | 8.8, 8.16 | actual Content/native |
| E8-R26 | Features UX/NFRs; L-0072/0073 | WCAG 2.2 AA, actual keyboard/screen-reader/mobile/focus/color-independent status | 8.17, 8.26 | actual browser/human |
| E8-R27 | Accepted browser policy | Current/previous Chrome/Edge/Firefox/Safari plus Android Chrome/iPhone/iPad Safari, exact versions/OS and gaps | 8.17 | browser matrix |
| E8-R28 | L-0059/0060; MVP exclusions | English and Portuguese readiness retained; translation/scanner/integrations not silently new MVP gates | 8.16, 8.17 | source/UI scope |
| E8-R29 | P-0026/0027; E3/E5 worker contracts | Restricted discovery/per-item scope, bounded drain/forced stop, supervisor evidence, stable claims and recovery | 8.18 | actual worker/supervisor |
| E8-R30 | P-0027 | Verified resumed/healthy idle/unconfirmed progress remain distinct; forced-stop warning retained | 8.18, 8.30 | worker/operational report |
| E8-R31 | Platform observability direction | One working safe log/operation/trace/health setup; no vendor bake-off/AI workflow or new business screen | 8.19 | actual controlled failure |
| E8-R32 | Platform observability; L-0120 | API readiness/worker heartbeat-progress/delivery backlog independent; monitoring outage does not undo unrelated actions | 8.19, 8.20 | actual probe/failure |
| E8-R33 | L-0120 | 5-minute API/heartbeat including empty queue; delivery due-age 15-minute warning/one-hour escalation not reset by retries | 8.20 | real alert integration |
| E8-R34 | L-0120/0119 | Immediate stale verified recovery-point/integrity alerts, grouped incident/verified recovery and independent routing | 8.20, 8.21 | actual monitoring |
| E8-R35 | L-0119 | Verified usable RPO <=1 hour, 30-day backup retention across actual DB/private bytes/dependencies | 8.21, 8.22 | actual backup/restore |
| E8-R36 | L-0119 | Essential service within four hours from incident declaration, consistent sign-in/access/requests/balances/private files | 8.22 | timed isolated restore |
| E8-R37 | L-0119 | Rehearsal before pilot then quarterly/major backup changes; real owners/results/remediation retained | 8.22, 8.27 | operational evidence |
| E8-R38 | L-0119; P-0012/0028/0029 | Restore holds outbound work; reconcile producer/receiver/provider acceptance, uncertainty held, no blind resend | 8.23 | actual multi-owner recovery |
| E8-R39 | P-0020; focused migration verification | Controlled owner migrations, actual previous versions/native roles, blocked activation, accurate partial outcomes and explicit recovery | 8.24 | actual native/release |
| E8-R40 | P-0028 | Queued/in-flight/failed payload compatibility and unsupported retention; no retirement by empty ready queue | 8.18, 8.23, 8.24 | actual worker/release |
| E8-R41 | E5 scale; accepted E7 targets; L-0108 | 100/1000 employees, five-year actual density/concurrency/hardware and endpoint/tx/memory measurements | 8.25 | actual performance |
| E8-R42 | Features MVP acceptance; BIZ-36 | Representative human employee/approver/custom/temporary/manager/org-admin UAT with exact scope and explicit failures | 8.26 | actual human UAT |
| E8-R43 | Tracker Phase 10 | Verified support/runbook commands, owner coverage/escalation/recovery and safe correlation references | 8.27 | rehearsed operations |
| E8-R44 | Tracker exit; Features MVP acceptance 1–10 | Exact-release/config/batch/target go/no-go signed by product/security/pilot with native/provider/UAT blockers retained | 8.28 | actual release dossier |
| E8-R45 | P-0046/0057/0058; E1/E2 admission | Existing Access/Directory pilot enable/grants and current admission, employment/import/email not an access grant | 8.29 | actual owner rollout |
| E8-R46 | P-0020/0027; Tracker Phase 10 | Partial activation recovered truthfully; scoped suspension preserves data/drafts/history and compatible work | 8.29, 8.30 | actual rollout/recovery |
| E8-R47 | Tracker exit; L-0119/0120 | Actual-target smoke/progress/reconciliation before operational handover; healthy idle not fake work progress | 8.30 | target verification |
| E8-R48 | AGENTS; P-0007/0059; Features acceptance 9/10 | Five impacts per item, true ATDD/TDD evidence, owned generator/managed-copy preservation and exact test/command/results | 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11, 8.12, 8.13, 8.14, 8.15, 8.16, 8.17, 8.18, 8.19, 8.20, 8.21, 8.22, 8.23, 8.24, 8.25, 8.26, 8.27, 8.28, 8.29, 8.30 | actual first-consumer evidence |

## Cross-epic and duplicate disposition

BIZ-35/36 are direct E8 import/pilot composition. NFR/security/browser/recovery obligations
remain first-consuming-owner requirements throughout E1–E7; E8 independently composes and
qualifies their actual results. E8 does not count unimplemented People/Leave/notification
services or unavailable native/provider evidence as delivered infrastructure. Existing
CALC/BIZ/FLOW/PRIV arithmetic/workflow/privacy matrices retain their owners, with actual
import adoption/eligibility and operational replay consumer proof above. Malware scanner
hardening, external sync, translations and AI monitoring tooling remain deferred.

Migration runbook source convention, exact client email, row/mapping preview, apply,
post-apply compare and cutover clauses all have explicit owners above. Every Phase 10
tracker obligation maps to threat/retention/browser/worker/monitor/alert/restore/release/
performance/UAT/support/pilot evidence items. Actual signoff remains a future release
action, not something this documentation can supply.

## Exact authority section fingerprints

These selected source sections protect the principal import/operations requirements
against silent drift; hashes cannot prove semantic completeness. Proposed ADR-0170 is
not an accepted amendment. Accepted E7 source adoption is complete before this snapshot.

| ID | Source / section | SHA-256 |
| --- | --- | --- |
| E8-S01 | apps/leave/docs/operations/migration-runbook.md: Establish what the source balances mean | `5e1109849a562f68aa402c525d8199d89e1842d33c3bc0201764c79a945fa260` |
| E8-S02 | apps/leave/docs/operations/migration-runbook.md: Validate, review, and apply | `c351c57c3d3875966bec4628978f6d30bc2634aaeb0cd602cabd2a302b2c37b6` |
| E8-S03 | apps/leave/docs/operations/migration-runbook.md: Cutover checklist | `cce73142692531c5a4e6e291fe181a7edcf24e184568452044eb88f1ea0b84aa` |
| E8-S04 | apps/leave/docs/features.md: Non-functional requirements | `3c7db2ba1af491895f7ce1c0ad627b822be5765da30d52480dd80c95a39446c9` |
| E8-S05 | apps/leave/docs/features.md: MVP exclusions | `9091015ac5f7c5e59848de939c9b24a0a79a8c16da576b820d49d42ab227b15d` |
| E8-S06 | apps/leave/docs/features.md: MVP acceptance summary | `01a2a1c47c7c4e23b5dc426eca2e015a715d5555b03d97e48bbacf7e577070b4` |
| E8-S07 | apps/leave/docs/architecture/decisions/0119-initial-production-backup-and-recovery-targets.md: ADR-0119: | `05474ad473bcdbb4f079b9a10dce66cfafd9583b2c81e26de0dc5f153ef2b7fb` |
| E8-S08 | apps/leave/docs/architecture/decisions/0120-initial-operational-alert-thresholds.md: ADR-0120: | `eff1b7f127a344b17506178cac15dacd911baf7aa838dd3db2da2279180d1c5e` |
| E8-S09 | platform/docs/operations/observability-and-ai-investigation-direction.md: MVP delivery boundary | `f0fcba51a3f9e950f56c72b878e1f8aa1b4e736e5dc0b0d4a6e4788b3d50283b` |
| E8-S10 | _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md: 15 — Setup and migration: | `2bbc1839042082ecdda075a24e54e20f9a4b410cb0db8678117081b059ce5ceb` |

## Planning checks and limits

The document audit checks 30 candidate headings/120 AC IDs, exact size/dependency rows,
earlier-only acyclic order, 48 obligation IDs, these ten authority hashes, relative
links/heading targets and unchanged pre-E8 story bodies. Prior E5 criterion/graph checks
are rerun. E7 acceptance/source adoption is verified separately; no accepted ADR is
altered by E8 planning. Actual source contract/native test/restore/monitoring/target
qualification commands and evidence remain named-owner delivery obligations. E8 and
ADR-0170 await one review; global atomic coverage/readiness and implementation remain open.

### Accepted source refresh — 2026-10-25

E8 and both ADR-0170 choices are accepted. The runbook's retained cutover-to-end
fingerprint deliberately includes the adopted recovery/pending-work section. Historical
proposed/check language above retains its original context. Actual application/runtime
verification remains future delivery work; no unexplained failing expectation changed.
