# E4 owner boundary assessment

**Adopted 2026-10-26:** Explicit user approval resolves the final candidate-review gate.
The approved choices are recorded in platform ADR-0064 and Leave ADR-0171. Earlier
pending-approval wording is historical; source/criterion bodies and dependencies unchanged.
Implementation is held for a new Codex session at the user's request.

**Date:** 2026-10-25. **Status:** Technical correction candidates for the consolidated
planning review, not implementation readiness or runtime evidence.

Fourteen original approved scopes yield seventeen delivery leaves. Parents 4.4, 4.11
and 4.12 retain all original acceptance as source evidence and each has an actual S/L
child pair in [epics](epics.md#e4-executable-owner-boundaries--technical-correction-2026-10-25).
The [owning protocol](../../platform/docs/architecture/contracts/content-association-and-reclamation.md)
allocates every original parent Given block, including cross-owner halves, to actual
child acceptance and a race/recovery oracle. Counting parent and child would duplicate work.

## Actual reuse and scope

`services/content-service/provider.py` already supplies S3 presigning with 900-second
PUT expiry, a sealed namespace and bounded streamed digest verification. `main.py`
has a conservative finalization path. Ownership/adoption/authenticated read extensions
remain with E1-CONTENT-READ. These are source reuse, not proof that new owner variants,
Azure parity, bounded crash recovery or Leave association already work. In particular,
the current no-takeover finalizer is not evidence for the new recovery protocol.
Expense coordinates shared Content delivery and may deliver these shared leaves first;
the Leave plan consumes their actual output once. The scope contains no Expense scanner,
production Expense compatibility migration or Scribeswell Content adoption.

| Leaf | Remaining owner delta and required scoped proof | Size judgment after real predecessors |
| --- | --- | --- |
| 4.1 | One scoped upload-session create/outcome/renew contract, using existing S3 presigning and E1 owner/service checks. Real expiry, changed-payload/retry and wrong-scope checks. | Bounded backend capability; provider parity is 4.3, verification 4.2 and association separate. |
| 4.2 | One finalization state machine using unique sealed attempt candidates and atomic locator publication; actual-byte/type/digest checks, concurrency/crash/replay and bounded verification. | Bounded owner operation after 4.1; retains current hashing/sealing reuse while correcting unsafe takeover assumptions. Does not implement association or Azure configuration. |
| 4.3 | Trusted provider resolution and Azure adapter against the completed upload/finalization/read contract; shared parity fixtures prove both providers and unchanged existing-file locators after default changes. | Bounded adapter/parity increment. New provider configuration is release input; no existing-file migration, app UI or second storage service. |
| 4.4-S | Content pending/confirmed/released references, fenced preparation and bounded reconciliation against an exact registered fixture owner. | One reference state machine over completed ready bytes/worker conventions; no Leave tables or deletion engine. Provider waits remain outside locks. |
| 4.4-L | One local pending-association/commit/outcome/read/release adapter under the existing draft guard; actual file/count/size constraints, duplicate/reconcile/discard races and reopened saved input. | One domain command/read integration after 4.4-S and E1 draft persistence. Basic Remove is first-use release; replacement UI is later. |
| 4.5 | Browser upload/camera review/retake and truthful upload/verify/attach states using completed APIs, with retry/remove, preserved draft and actual Android/iOS/desktop proof. | One input/upload surface. No cropping/OCR/scanner/native packaging; file conversion choices are explicit qualification inputs rather than a second document editor. |
| 4.6 | Safe document metadata projection and its existing draft display. Direct API/privacy/own-versus-sensitive permission fixtures. | One projection/display extension; no byte transport or actual future approval screen. E5 adds its real screen integration. |
| 4.7 | Actual Leave authorization/context and Open/Download consumption of the completed shared file transport; native PDF/range/session/privacy proof. | One app adapter/browser integration. Shared streaming and first auth implementation are credited to E1, not rebuilt. |
| 4.8 | Atomic local replacement/association swap, preserved original through failure, release intent and actual existing controls. | One draft transition using prepared references/recovery from 4.4 and upload UI from 4.5; no submitted-request replacement. |
| 4.9 | Persisted action-required transition producer and safe destination using E3 outbox/receiver/templates and E4 outcomes; current recipient, replay, stale-link and no-validation-spam proof. | One producer family. No new delivery worker, email provider, scanner or general notification UI. |
| 4.10 | One versioned organization/jurisdiction retention setting and explicit Save/Cancel form, with applicability/impact and capability tests. | One settings capability using existing configuration/revision/history patterns; candidate exact applicability is in the owning retention contract. No deletion on Save or legal-rule engine. |
| 4.11-S | Content unreferenced disposal fence/provider outcome and restricted-worker extension; crash/retry/read-tombstone/restore protection. | One physical-disposal state machine, reusing references and provider adapters. Not a backup redesign or Leave eligibility engine. |
| 4.11-L | Version-bound request-closure/retention eligibility and atomic domain release intent, plus accurate existing unavailable/disposed status. | One domain release adapter over completed settings and Content disposal. Existing E5/E6 lifecycle adapters integrate before their activation. |
| 4.12-S | Upload abandonment/staging discovery and late-byte eligibility over completed reconciliation/disposal, with both-provider race fixtures. | One discovery/eligibility extension; reuses the disposal worker and terminal identities rather than another cleanup engine. |
| 4.12-L | Exact Leave association outcome/recovery endpoint and actual saved-draft/late-confirm protection with operational uncertainty evidence. | One narrow recovery integration over 4.4-L state; no broad callback authorization service, provider delete or new UI queue. |
| 4.13 | Hosted composition of already-completed capture/association/auth/privacy/recovery mechanisms and ordinary-draft independence, on the approved browser/device matrix. | Bounded qualification item, not implementation of missing earlier mechanisms. Earlier owners retain their own ATDD/native/provider evidence. |
| 4.14 | Inventory actual retired callers/configuration/credentials and coordinate supported PtS/Expense replacement/recovery with controlled release evidence. | Bounded retirement/adoption item after actual replacement owner work. No blanket receipt migration, new service or dependency on future Leave 4.13. |

These qualitative fit judgments count owner-local incremental work with completed
predecessors, targeted contracts/native tests and applicable browser/provider/generated
evidence. They are not measured time estimates or evidence that prerequisites are
delivered. No additional split is justified by the selected boundaries alone; actual
delivery must revisit concrete excess rather than omit an acceptance obligation.

## G04 disposition and remaining gates

G04's missing executable owner/criterion bindings are resolved as a planning proposal:
six actual child stories, all parent Given blocks allocated, seventeen source-backed
leaves, explicit predecessors and the per-leaf size/reuse assessment above. The global
graph remains 310 nodes; derived partition aliases now point to actual child stories.
Candidate contracts select the reference protocol and provider model. G03 now has selected early-owner and Content technical candidates; consolidated
acceptance and full G01 semantic validation remain. No automatic whole-product readiness
PASS follows from closing this allocation.

All leaves retain scaffold/shared-UI/agent-context/documentation/ADR impact decisions in
their source stories. Original accepted ADRs and E5 criteria remain unchanged. Runtime
tests, migrations, cleanup, provider changes, grants, activation and commits are not part
of this planning correction.
