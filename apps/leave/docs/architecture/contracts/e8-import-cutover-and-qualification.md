# E8 import, cutover and qualification — owning contract proposal

**Status:** E8 planning accepted on 2026-10-25; not implemented or readiness-approved
**Date:** 2026-10-25
**Owners:** Leave import/accounting/request leads; Identity/Access, People, Content,
notification and deployment/operations owners retain their boundaries

Product authority remains [Features](../../features.md), the
[migration runbook](../../operations/migration-runbook.md), accepted ADRs and approved UX.
[E8 review/size/dependencies](../../../../../_bmad-output/planning-artifacts/e8-planning-review.md)
and [source allocation](../../../../../_bmad-output/planning-artifacts/e8-coverage-audit.md)
map the proposed work. [ADR-0170](../decisions/0170-imported-pending-work-and-resumable-employee-units.md)
is Accepted by explicit user approval of E8 and both choices on 2026-10-25. This is technical allocation, not a second import product spec
or an executable consultant manual.

## Existing owners and execution limits

Use E1's actual environment/identity/current-access/owned-write/operation machinery,
E2 People/source/setup contracts, [E3 accounting](e3-request-accounting-interface.md),
[E5 protected commands](e5-request-command-and-finalization.md),
[E5 worker contracts](e5-timed-work-and-errors.md), [E6 corrections](e6-corrections-and-consequences.md),
[E7 reports/audit](e7-overview-reports-and-audit.md), E4 actual Content association/private
read/retention, and each owner's real migration/qualification tools. No source database
imports, duplicate directory/ledger, universal credential, workflow engine, backup engine
or monitoring bake-off. Business security and recovery begin at each first consuming
story; E8 qualifies their real composition, not delayed first implementation.

No Leave API/web, People runtime or shared notification runtime is established by the
current docs. Access and Content exist; their exact Leave consumers remain actual
prerequisites. Platform deployment tooling exists for registered apps/services, but its
README explicitly does not deploy Leave or prove an uninspected target ready. Current
cloud resources/accounts/plans, credentials/cost/capacity and actual recovery evidence
must be inspected during separately authorized operational delivery. Never infer them
from examples or run provider/deployment commands to complete this planning.

## Import package and source conventions

8.1 owns versioned documented source templates and CLI `validate`/report contracts.
Proposed artifact names describe intended outputs, not existing executables:

| Artifact | Minimum bounded evidence |
| --- | --- |
| `manifest.v1.json` | Batch UUID, explicit target organization, source-system namespace, schema version, immutable source file digests, source export UTC time, balance effective date/timezone, units/standard-day basis, selected source identities and package digest |
| normalized preview plan | Exact mapped employee/type/policy/work/calendar/request/document source IDs and revisions, economic convention/portion provenance, resulting records/effects, current route/response/notice consequences, per-row errors/unsupported history and deterministic plan digest |
| reconciliation report | Human-reviewable source/results/differences and exact selected scope, its own digest and normalized plan/package/batch identities |
| client approval evidence | Restricted email reference/hash, contact and authority basis, operator/time, exact approved report/plan/package digests and selected target/cutover scope; evidence does not itself grant application authority |
| apply/status report | Original operator/batch/unit operation links, actual committed/uncommitted/unresolved owner outcomes, record/evidence IDs and safe codes, never copied source payload dumps |
| post-apply/cutover dossier | Actual-versus-approved results, reviewed deltas, renewed approval where required, final scope and release/activation references |

Canonical normalization uses existing UUID/ISO date/UTC instant/integer-minute/string-
bigint conventions and versioned RFC-8785 SHA-256 digests. Bind source namespaces and
keys, original file identities, selection, target org, normalized source convention and
material planned results. File paths/names and unverified labels confer no identity.
Do not put private files, email contents, request notes or hashes-as-bearer-capabilities
in public builds, Git history, process arguments or operational logs. Store artifacts
in an operator-restricted nonpublished location with actual approved retention controls.
No automatic email sending/reading or in-app client signoff flow is added.

8.2 resolves verified durable person/employment/actor references through actual owners.
No email-only matching, implicit account creation, duplicate employment after rehire,
permissions from employment, synthetic historical approver or editable employee copy.
Unknown external actor remains explicitly external provenance with safe source label,
not a fabricated registry actor who appears to have approved. People/configuration setup
is completed through its existing E1/E2 authorized operations before dependent import;
source operations retain separate real outcomes, not a cross-owner rollback promise.

8.3 normalizes source opening balances and transferred historical/pending/future approved
request effects together. Declare whether the source amount is before or already includes
future consumption/reservations. The accepted example is 8 days plus 2 future approved:
6 available when 8 is gross before booking, 8 when 8 is already net. No blanket subtraction.
Preserve source portions' original periods, validity/expiry, conversion basis and already-
reflected history. E3 derives actual events/earning once; importing a history row must not
mint a second grant, deduction or annual entitlement. Tracked/untracked types retain actual
mode and paid/unpaid usage rather than fictional pots. Cross-type earning/basis migration
restrictions remain binding.

One opening total cannot establish arbitrary prior cap/expiry/reservation/cancellation
history. Record a supported history/replay boundary and actual provenance sufficient for
required reports and E6 consequences. A retained old request may be displayable while a
balance date before the proven baseline is explicitly unavailable. Do not invent older
calculation snapshots or claim E6 counterfactual replay works without required sources.
Missing facts needed for required pilot actions block the affected migration scope until
resolved through reviewed source data/owner design; do not waive them with a disclaimer.

## Narrow actual import capabilities and adapters

Propose exact organization-scoped `leave.import.preview`, `leave.import.apply` and
`leave.import.read` capabilities, registered only for explicit restricted operator adoption.
They are not in standard employee/Approver/Leave Manager roles by inference. Apply also
requires the actual approved manifest, current target scope and permitted migration
control-plane admission. Source management remains separately authorized by People/
Identity/Access; Content service policy and current on-behalf/domain predicates remain.
A consultant's title, client email or service key alone is insufficient.

Select explicit app API design routes under `/api/v1/organizations/{org_id}/imports`:

- `POST /previews`: authenticated read-only current preflight/normalization; offline CLI
  validation alone cannot certify remote state. It creates no business event or request.
- `POST /manifests`: register immutable reviewed package/plan/report/approval references;
  retain server actor/UTC attribution and scoped version/source selection constraints.
- `POST /{batch_id}/employees/{employment_id}/apply`: one explicit current authorized
  employee-unit command with original operation UUID, expected manifest/source revisions
  and exact approved plan digest. Body cannot supply trusted actor/grant/event lines.
- `GET /{batch_id}` and unit/outcome reads: current permitted migration context, actual
  original operation status, safe progress and retained source/result references.
- `POST /{batch_id}/activation`: exact manifest/release/selection/generation confirmation,
  only after actual release go/no-go and final reconciliation; no ordinary user entry.

These are planned route/command names, not current endpoints. Reuse owner-local receipts
with constrained import-manifest/unit targets, command versions, canonical submitted-input
fingerprints and actual scoped FKs. Same operation with changed input conflicts; receipts
report the original outcome, not current request state. Unique organization/source namespace/
source-record identity prevents a fresh operation or another batch from duplicating the
same adopted source record. Unit outcomes are actual command outcomes, not a background
batch job. Operator changes use explicitly permitted status/recovery context; they cannot
impersonate the original actor or reuse a different actor's receipt as authority.

8.5/6/7 are **internal** owner adapters to that unit command, not three external requests
that separately commit parts of a supposedly atomic import. 8.5 owns E3 normalized opening/
reconciliation effects and staged-source economic-read eligibility. 8.6 owns settled
external-record adoption/provenance, current-read eligibility and actual source/economic
links. 8.7 owns pending task/finalization eligibility, route/reservation/response/activation
integration. All use actual E3/E5 models and structural/org constraints. Ordinary E5 routes
cannot accept arbitrary client-supplied approved status or backfill signed human decisions.
8.8 separately prepares exact verified Content identity/pending association under E4;
final local association confirmation participates in the employee unit's local envelope.
No copied blob, mutable byte substitution or unsafely abandoned pending import reference.

## Atomic employee unit, retries and source eligibility

Under accepted ADR-0170, one employee's selected records across leave types use one bounded
Leave transaction: exact manifest/selection and source/revision/current-access checks,
complete source/reference/employee coordination set, all opening/request/cycle/allocation/
association-confirmation links, immutable evidence/audit, operation outcome and required
held intent. Any local failure rolls it all back. External waits and byte transfers occur
outside business locks using existing owner preparation/current evidence. Dynamic required
sets follow E5 discover/protect/reload/restart, not locks added out of order.

Successful employees remain committed when another fails. Batch status distinguishes
committed selection count, known-uncommitted errors and unresolved outcomes without
changing application lifecycle vocabulary or reporting total success. Explicit status/
resume resolves original unit operations first. Fresh operation IDs do not bypass source
uniqueness; stale retries cannot overwrite a later legitimate correction/closed cycle.
No automatic deletion/ledger edit undoes previously committed units. A changed manifest/
selection/material source plan requires a revised report and renewed client email approval.

Initial bounds reuse 30-second total execution, three-second owner reads, one-second lock
acquisition within five-second local transaction and 35-second client wait. Preflight
limits a unit to 100 selected requests and 1000 normalized accounting lines, and a source
package to 1000 employees/10,000 requests; larger inputs require explicitly partitioned
approved batches/owner design, never silent truncation. These are technical initial
qualification bounds, not employee/product limits or demonstrated throughput. If a
single employee cannot fit, fail before effects and resolve the concrete unit design;
never split its economic envelope silently. CLI serializes applies initially; no need
for a new worker or speculative performance engine.

All imported-source rows have explicit manifest/unit/provenance and activation eligibility.
Unreleased rows remain excluded from ordinary user request/detail/task/report/action scope;
only current import operators can inspect staged facts through the import projection.
E5 mutations/finalization and E7 query adapters must enforce this source predicate. This
is a narrow import boundary, not a new public request status or broad draft workflow.
Deliver eligible-reader/finalizer compatibility in an expansion release before creating
held rows; prove the supported previous version cannot ignore the predicate. If impossible,
use P-0020's planned maintenance/recovery rather than weakening protection.

Accepted pending adoption creates a new Leave cycle with current E5 validation/route,
initial unpaid response and real authorizer/employee distinction. External source partial
decisions remain readable history only. The approved plan discloses new route/wait/response
consequences; materially changed authority/route at activation requires re-review/client
approval, not silent rerouting. Preserve source wait/submit times separately. The new
current actionable clock starts at actual activation, never during an unavailable held
period, with E5 current responsibility/same-person/finalization rules unchanged.

## Notification release and cutover

Only import-adoption events are recorded for imported concluded source history; no bulk
replay of old business notices. Actual current pending response/approval notices use the
existing versioned Leave intent/outbox/receiver and channel template system. Tag them
with actual source activation generation and hold only that imported scope until approved
release. Preserve real required intent/dedup identity, current eligibility/recipient checks
and unsupported-work retention. Provider outage does not undo an employee import.
Do not pause unrelated legitimate Leave notifications merely because one batch is staged.

No activation until all selected units/required documents reconcile and the exact target/
release/client-approved cutover delta is ready. Existing Access enablement/grant/Directory
owners still determine admission; import never creates membership/access. Activation
records actual manifest/generation/actor/instant locally and real owner outcomes separately;
no distributed atomic release. Recover partial activation under existing identities and
suspension/release procedures, preserving data, drafts and audit. Initial source activation
is a release gate, not an automatic approval of a subsequent real request.

The consultant records source export time, effective balance date, old-system write cutoff,
Leave authority/handover time and accountable contact/operator. Reconcile every intervening
request/decision/cancellation/employment/adjustment. Changed package/plan/report needs
renewed email approval against exact revised digests. Post-apply comparison reads actual
state using import operator scoped projections plus actual E3/E5/E6/E7 adapters, not
ordinary unactivated-user views. Mismatch blocks handover; changing an expected number or
editing old ledger entries to get a PASS is prohibited. Supported corrections use existing
owner actions or a deliberately reviewed replacement migration plan.

## Qualification ownership and actual evidence

8.14 proves import composition under actual restricted roles/HTTP/Content and failure
injection; 8.15–17 compose threat/privacy/accessibility/browser evidence from completed
features, not substitute UI hiding or mocks for native authorization. Document retention
retains the accepted configurable initial medical default of two years after closure and
existing explicit-Save form; actual per-client privacy/legal review is a delivery input,
not a new statutory/legal conclusion. Protect drafts/in-flight import associations and
required retained history before actual owner disposal. Malware scanning/OCR remains
outside MVP under the accepted roadmap, while exact-byte safety extension is retained.

8.18 uses actual worker grace/claim/fencing/dedup contracts: stop claims, bounded drain,
supervisor-recorded forced termination, truthful replacement/idle/progress evidence. 8.19
proves one working monitoring setup using safe operation/trace/release fields and bounded
OpenTelemetry instrumentation. No vendor bake-off, dual log stores, AI repair pipeline or
new business operations screen. 8.20 demonstrates L-0120's actual 5-minute API/heartbeat,
15-minute/1-hour overdue delivery and immediate stale-usable-backup/integrity alerts,
with incident grouping and verified recovery. Alert delivery is independent of the
notification channel being monitored; no implicit 24-hour support SLA.

8.21/22 prove L-0119's actual DB/file/identity/access/config recovery: at most one-hour
loss, essential service within four hours of incident declaration, thirty-day backup
retention, rehearsal before pilot then quarterly/after major backup changes. A scheduled
job or provider plan alone is not evidence. Private object bytes/version and their DB
associations must be usable at the chosen point. Current provider capability/cost/restore
commands are actual owner/target inspection work before operational execution.
8.23 holds outbound work during restoration, reconciles actual producer/receiver/provider
acceptance and dedup evidence, and leaves uncertainty held. A DB restore cannot unsend
email. Resume only verified eligible work with current authority and causal identity.

8.24 composes P-0020 controlled owner migrations, coordination, previous-version and durable
payload compatibility, failure-blocked activation and explicit corrective/compatible-version
recovery. Ordinary Alembic/native checks remain owners; no extra internal-ledger interpreter,
startup migrations or automatic downgrade. 8.25 measures actual 100/1000 employee, five-year
source/request-density and accepted E7 target workloads, including full actual route costs,
resource headroom and imports. Record limits and optimize only with concrete measurements.

8.26 is representative **human UAT**, not acceptance of planning documents. 8.27 assigns
actual support/recovery/alert/contact ownership and only verified runbook commands.
8.28 assembles exact release/configuration/batch/target evidence and actual product/security/
pilot signoffs. 8.29/30 execute the approved scoped pilot only during authorized delivery,
then verify actual access/records/private bytes/worker/delivery/reconciliation and handover.
Each has explicit no-go and real recovery status; no planning check can mark them complete.

## Artifacts, tests and the five impacts

Actual delivery records source requirement → E8-xx-ACyy → owner/fixture/test node → observed
acceptance failure → focused TDD/affected suites → command/result/evidence/limits. Follow
[E5 artifact strategy](e5-verification-and-artifact-map.md) and actual owning package:
planned Leave pytest/OpenAPI/generated-client/Playwright commands are not runnable proof
until packages/fixtures exist. Native migration/RLS/rollback, provider restore and actual
target/browser checks must use their declared isolated target and explicit current
credentials/roles, not root npm wrappers or unrelated app successes.

Scaffold: reuse actual bounded HTTP/owned-write/receipt/worker/release/native fixtures and
promote only demonstrated neutral gaps in the same item, maintaining templates/installers/
managed copies/preservation tests. Import semantics/source data stay Leave-owned. Shared
UI: use existing app controls in UAT; consultant CLI adds no self-service import/approval
screen. Agent context: current instructions suffice; actual generated commands/runbook
guidance updates with owner delivery. Docs: migration/qualification/source-contract/test/
release/support evidence in existing project artifacts, not another generic lifecycle.
ADR: accepted 0170 binds the approved import choices; accepted predecessors unchanged.
No emails, scheduling, imports, migrations, grants, provider/backup changes, production
qualification, deployment or commit were performed or authorized by this planning package.
