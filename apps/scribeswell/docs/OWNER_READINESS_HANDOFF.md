# Scribeswell owner readiness handoff

## Approved UI baseline for the release candidate — 2026-11-04

The user accepted the rendered UI changes and requested the next step. The local
UI baseline ends at `8747187cf45127ab3043abaeede54a00e542b861`, following
`b575bc8`, `37384d1`, `889f387` and `c699fc8`. It includes compact workspace
controls, discreet rename, Hebrew book/chapter labels, click-only book selection,
restored amber colours, softer borders, consistent Studies/Analysis controls and
bounded dialogs/mobile editing. Retain native system UI typography and bundled
Noto Serif Hebrew. The accepted appearance is the baseline for further work.

The completed [UI delivery record](../../../_bmad-output/implementation-artifacts/spec-scribeswell-study-ui-polish.md)
records 1,205 distinct browser passes, seven intentional skips, successful
TypeScript/Vite build and production-preview checks, and inspection of 57 rendered
captures. These results concern the local tested workspace, including preserved
concurrent changes; they do not qualify a clean archive of this commit or the
existing frozen release candidate. Temporary visual evidence is at
`/tmp/scribeswell-after/report.html`; preserve or regenerate it before relying on
it outside this workstation.

Subsequent investigation found a newer completed production handoff in the isolated
shared-adoption checkout: source `59e2c8884cad24bb2f6e99fc519b2e6dc5bc9d84` was deployed
on 2026-11-04. Earlier release-preparation entries below are historical. The UI
follow-up therefore uses a fresh frontend-only candidate based on that deployed
source; shared adoption and backend release work must not be repeated. See the
[UI candidate record](UI_RELEASE_CANDIDATE.md) for source selection, actual release
builds, candidate browser/visual evidence and the approved publication outcome.

This is a handoff within the existing release delivery, not a new release approval.
No push, publication, deployment, migration or production mutation occurred in this
UI follow-up. The mixed main workspace must not be treated as the selected release
source merely because the visual work is accepted.

## Active release preparation checkpoint — 2026-11-01

The shared release has resumed in the isolated
`apps/scribeswell/.local/shared-adoption-identity30` checkout, preserving MAIN's
Leave/KDG/E1 changes and the previous release branch. Fresh canonical Studies
qualification now passes Identity0030/Access0019 with readiness v3, all26 packaged
runtime modules,230 source bindings and eight actual native stages. Parent verified
all stage/source digests and normal shutdown of both new disposable runs. See the
[credential-free checkpoint](evidence/identity30-studies-readiness-20261101.json).
This replaces no historical proof and qualifies neither the managed target nor a
new packaged image. The exact canonical inputs were archived before further work.

The existing managed target cannot execute the canonical Auth-owner prerequisites.
The next bounded owner phase reuses the reviewed hosted baseline and adds an honest
`identity_0031_e1_hosted` successor, retaining `access_0020_hosted`, with explicit
qualification against E1's canonical0030/0019 contracts. These are proposed true
hosted ledger names, not deployed observations. No relabeling or stamping of0030,
old hosted0028 retirement integration or application capability reimplementation.
Managed Studies TEMP, explicit grants/corpus/Content binding, packaged consumers,
maintenance/failure/forward recovery and immutable publication inputs remain gated.

Fresh read-only production inventory at14:52UTC confirms backend2480de173149cc646e8c1c55d088a93c4b196f47,
five healthy APIs/zero restarts, gateway running, public200/39books and Studies404,
with no pending release/TLS. No production mutation, publication or activation has
occurred. Leave/KDG application activation and fullE1/Reference closure remain outside
this release. Their final deployed-version/recovery handoff is still pending.

## Leave E1 / Scribeswell-PtS release alignment — 2026-11-01

The user clarified that Scribeswell's impending PtS release should consume the shared
work completed through Leave E1. Continue the existing
[production adoption prerequisite delivery](../../../_bmad-output/implementation-artifacts/spec-scribeswell-production-adoption-prerequisites.md);
do not create a second Leave-owned shared migration or recovery delivery. That spec
already records the 2026-10-28 decision to include Identity/Access/PtS prerequisites.
Older scope-pending wording below and in the target report is historical.

| Responsibility | Owning work and handoff |
| --- | --- |
| Shared capability implementation and local proof | Reuse completed [E1-PTS-ADOPT](../../../_bmad-output/implementation-artifacts/spec-1-15-e1-pts-account-corpus-files.md), its [owner runbook](../../pts/docs/ACCOUNT_ADOPTION.md), and existing Identity/Access/Content contracts and evidence. Local completion is not production activation. |
| Actual legacy-target adoption, managed-role preparation, explicit grants/corpus/Content binding, coordinated consumer cutover and recovery | Existing Scribeswell/PtS release delivery owns the production plan and execution evidence. Reuse the owner migrations and tooling already delivered; qualify target-specific gaps in that delivery. |
| Leave entry pilot | Consume the shared release's observed outcome, then bind Leave-specific schema/runtime, Microsoft callback, site/TLS, admission and devices using the [prepared pilot runbook](../../../platform/deployment/LEAVE_PILOT.md). No repeated shared adoption. |
| KDG consumer | Consume existing Identity/Access/scaffold/WRITE work; retain KDG-owned capture, offline/sync and installed-device evidence. [KDG's current handoff](../../kdg-capture/docs/shared-platform-handoff.md) records completed local Story3.1 work and remaining HTTPS/device/assistive gates. KDG app activation is not added to this Scribeswell release. |
| Reference hosted verification | Separate E1-VERIFY consumer after its own readiness; it does not gate PtS activation. Full Leave E1 closure is not a prerequisite for the Scribeswell/PtS release. |

**Version reconciliation remains required.** The completed bounded Studies delivery
qualified frozen Identity0026 / Access0019. Completed PtS cleanup and the Leave pilot
require Identity0030 / Access0019. Neither an old0026 receipt nor later local0030
success qualifies Scribeswell against a new production candidate. The existing release
owner must select an exact source/image/owner-version set and qualify Scribeswell and
PtS together against it, or explicitly record a staged owner upgrade and the remaining
Leave prerequisite. KDG's retained-actor consumer requires the Identity0028 contract;
its local proof does not qualify a later shared candidate or an old0026 image. Include
that owner/API/restricted-runtime compatibility in the version handoff, with KDG's
own integration recheck before its later activation. Preserve the old frozen0026 qualification; do not relabel it,
silently retarget it or loosen the pilot's0030 admission gate.

Handoff acceptance requires exact immutable sources/images; observed before/after
owner revisions; supported managed-database authority and target-derived operational
inputs checked against independently qualified owner references; explicit account
grants and reviewed corpus/Content associations; required runtime key/role and PtS
file-origin bindings; retained migration/failure/recovery and current consumer results.
Use existing protected evidence custody. Preserve public reading, existing identities,
data and prior evidence; no production mutation follows from this alignment.

Order: finish the shared-code/evidence handoff now; resume the existing Scribeswell/PtS
release prerequisites and separately authorized cutover; recheck the actual deployed
shared versions; then activate the Leave pilot and perform Samsung/iPhone/iPad/Mac
qualification. Independent Leave work may continue locally meanwhile. Real-provider
return/cancellation, assistive/device results and the unexplained missing-session
nonpass remain open; none is a prerequisite for the unrelated PtS cutover. Leave's
later E1 context/choice/draft stories also remain tracked and are not added to that gate.

The user also prefers completing Leave work before resuming KDG completion. Retain
that work priority without inventing a whole-E1 technical dependency: KDG requires
only its specified shared contracts and its own acceptance/release gates, not Leave's
People/draft journey or hosted Reference. The offered Samsung/iPhone/iPad/Mac devices
can support later sessions, but Leave sign-in results do not prove KDG installed-PWA,
offline Save/reopen/sync, cache/update separation or retained pending/conflict behavior.
KDG uses emailed one-time codes, not the Leave Microsoft prerequisite. Keep synthetic
KDG target, fixed-organization admission, privacy and controlled migration/recovery
requirements; no KDG production or fixture lifecycle operation is authorized here.

This is an operational ownership/dependency clarification, not a new feature spec or
release approval. Documentation/tracking only; scaffold, shared UI, agent context,
runtime behavior and accepted ADRs are unchanged. Entries below retain their dated
qualification boundaries.

As of 2026-10-27, after local checkpoint `321f7eb`. This is an operational handoff,
not a new feature specification, accepted owner contract or release authorization.
The [canonical spec](../../../_bmad-output/specs/spec-scribeswell-studies/SPEC.md),
[Access contract](../../../services/access/STUDIES-ENROLLMENT.md) and
[final integration evidence](FINAL_INTEGRATION_EVIDENCE.md) remain authoritative.

Personal Studies and genuine standalone signup have passed the isolated real-owner
qualification. Default Access startup now also passes the app's actual browser/signup
consumer integration against the qualified exact owner pair; see
[default-startup evidence](DEFAULT_STARTUP_INTEGRATION_EVIDENCE.md).
The separate [frozen Access runtime qualification](FROZEN_ACCESS_RUNTIME_EVIDENCE.md)
now passes the unchanged hardened Python3.15 default image against the same reviewed
pair, with a freshly prepared version2 artifact and all inherited consumer oracles.
Coordinated environment release/recovery evidence remains outstanding. Sharing remains
separate; implementing a substitute Access or Notification path would cross ownership.

## Default Scribeswell API image follow-up — 2026-10-28

The [API image qualification](API_IMAGE_INTEGRATION_EVIDENCE.md) now includes the
required offline reference catalogue and passes the shipped default CMD on a fresh
real-owner fixture alongside frozen Access. Final review-fixed run
`56ec83ff-a9e3-4ad0-a0b2-9374c0d853a7` passed browser/privacy, disabled authority,
genuine signup/local mail/consumed/elapsed-expired links and24 SQL checkpoints,
without skips. Both actual restricted runtime URLs independently proved TLSv1.3;
UID10001, exact60 app files, installed dependency bytes and runtime hardening agree
with recorded image provenance. The app requirements remain unpinned.

All17 exact app/Access containers and21 process groups stopped normally; native
fixture stop exited0, no fixture containers/listeners remained and nine reuse binds
passed. All190 original owner inputs, qualification and live bundle remain unchanged.
The independent parent repeated146 affected tests and inspected the actual live/final
image. Blind and verification reviews had no findings; edge review found and fixed
one top-level COPY-directory-symlink boundary defect. Earlier failed/interrupted
attempts, including an unexplained privacy timeout, remain retained. The earlier
`eff62b26` success is superseded pre-review history with retained files/hashes. See [safe evidence](evidence/api-image-integration-20261028.json).
Production Studies refusal remains binding; environment release/recovery, external
SMTP, physical devices and recipient/Notification gates remain outstanding.

## Access/Identity owner: adopted exact-head readiness

The owning readiness delivery adopts artifact and qualification `schema_version: 2`
for exactly Identity0026 / Access0019 from reviewed baseline `deb424b`. See
[the adopted interface](../../../services/access/STUDIES-ENROLLMENT.md#exact-reviewed-current-owner-readiness--2026-10-27)
and [the qualified owner evidence](../../../services/access/docs/testing/studies-current-readiness-20261027.md). Historical Identity25 / Access18 app
integration remains retained; it is not default-startup proof for this pair.

Unrelated Identity0027 work appeared during implementation, so the current delivery
qualifies an isolated `deb424b` source archive with its own synthetic run IDs and
source hashes. This does not qualify the mixed live worktree or later heads. The
artifact binds all packaged default runtime modules and the preparation evidence
binds current migrations/catalogues/references plus actual stage proofs. Consumers
must use the published environment and artifact verbatim; no injected database or
fabricated readiness field establishes default-startup readiness.

## Application and platform release owners: truthful private-head reporting

**Follow-up2026-10-27:** the report correction below is now implemented and natively
qualified in this Scribeswell session. The [adopted private report contract](PRIVATE_MIGRATION_REPORT.md)
records actual before/committed after0009 and coordinated app/host validation.
The quoted request is retained as history, not outstanding implementation. Actual
environment release/recovery rehearsal remains. The default-startup consumer is now
qualified against the adopted archived owner pair as linked above.


`apps/scribeswell/deployment/studies_migrate.py:upgrade` upgrades Alembic `head` but
returns `after:scribeswell_studies_0001`. Both
`apps/scribeswell/deployment/migrate.py` and `platform/deployment/host-release.py`
require that exact four-field result. Actual private head is
`scribeswell_studies_0009`. Existing native ledger proof establishes the real schema;
the old release report cannot be treated as evidence that head0009 was recorded.

Request for the platform release owner, coordinated with this application session:

> Agree and publish a compatible private migration-report contract with Scribeswell.
> Require truthful observed before/after ledger revisions and the intended release
> target, while retaining controlled migration-before-activation, bounded supervision,
> previous-running-version compatibility and forward recovery. Update the helper,
> application supervisor, host validator and affected tests together; do not change
> only the application's hard-coded marker or accept arbitrary successful JSON.
> Qualify real current-head upgrade and repeat, wrong head, failed/unknown outcome,
> stale evidence and activation refusal, plus ordinary compatible release/recovery.
> Do not deploy or activate production as part of the contract change. Preserve all
> unrelated Leave/Access/platform working-tree changes.

The report shape/version remains an owner decision. This handoff adopts no new wire.

## Scribeswell consumer follow-through — 2026-10-27

The new app-owned qualifier consumes the adopted artifacts on a fresh isolated
fixture (Auth55491/DB55492), after the observed injected-launch acceptance failure.
The final review-fixed run passed all inherited browser/SQL/signup/privacy and disabled
authority oracles using real restricted owner credentials, live provider/local
mail and unmodified `main:app`. Owner preparation produced a fresh version2 artifact
bound to the new executor; no existing artifact or injected dependency was used.
Ten unsafe startup variants refused. Independent post-shutdown inspection confirmed
all 486 recorded hashes (171 app, 305 owner, nine qualification/proof and the binary),
200 recursive owner module paths/digests and 24 SQL checkpoints; 31 process stops and exact fixture stop
were normal. KDG55481/55482 and Leave environments were untouched.

The app/host report-refusal suite passed 47 tests without skips; independent
repetition passed in 3.15s. The parent separately qualified actual PostgreSQL17
private reports: 6 passed in 8.25s, runner 9.291s, no skips, with all 86 source
hashes unchanged. Its fresh exact container was stopped and retained, its volume
retained, and loopback port 32770 released. Independent helper/signup repetition
passed 92 tests in 1.01s after the late-module/package freeze repair (three initial
negative failures, then 12 focused passes in 0.77s). The parent also confirmed all 486 integration hashes,
13 retained private-proof digests, fresh actor binding, real expiry and normal
shutdown; composition check-only passed 15 migrations without writes.
Safe commands/results/hashes are linked in the default-startup evidence above;
the private PostgreSQL connection is excluded. Final proof is
`/tmp/scribeswell-default-integration-review-bbc64030`, run
`bbc64030-9df1-4dc2-a7e2-ab35f7874fd6`, with actual expiry 122.000218s.
The initial successful 377-hash run and artifact remain superseded history;
the original 190-input owner qualification/archive is unchanged.
Actual coordinated environment release/recovery remains outstanding.

Production signup/SMTP requires the deployment owner's real environment and delivery
verification. Local Mailpit proof is complete and must not be relabelled external mail
proof. Physical iOS/Android selection, OS Copy and keyboard acceptance needs actual
devices. Neither gate can be completed by another intercepted browser test.

## Sharing remains a separate owner dependency

The [recipient/invitation facade](../../../platform/docs/architecture/contracts/scribeswell-study-enrollment.md)
and [Notification/inbox contract](../../../platform/docs/architecture/contracts/notification-delivery-and-account-inbox.md)
are still explicitly proposed and undelivered. No matching recipient facade or common
notification runtime was found in the current service tree. Before a sharing consumer,
owners must publish implemented recipient resolve/verify/error/freshness contracts and
qualified account-scoped notification acceptance/inbox/dedup/retry/retention behavior.
Scribeswell then owns invitation/share transitions and its outbox under those contracts.
Existing own copies do not establish shared-source/private-response delivery.

## Current owner qualification and limits

The [owner evidence](../../../services/access/docs/testing/studies-current-readiness-20261027.md)
records successful isolated current-head readiness,190 source hashes/eight native
proof stages,13 preparation refusals and unmodified default startup200 followed by
current denial403. Its264-test archived compatibility run and native mutations use
the actual handoff Python3.12.3 interpreter; this does not qualify the production
Python3.15 bundle or unrelated Identity0027 working changes. Both new fixture runs
stopped normally. Prior historical handoff and unsuccessful-attempt evidence remains
retained; no production activation or coordinated release/recovery claim is made.

**Frozen runtime follow-up2026-10-27:** the separate exact-source Access bundle and
default image passed actual Python3.15.0/uv0.13.1 offline packaging, all three invalid
packaging builds, ten real startup refusals, browser/disabled-authority/signup/local-mail
and24 SQL checkpoints without skips. Runtime proved exactly14 owner modules and1,145
dependency files; independent live inspection matched the genuine artifact bytes.
Final review-fixed run`9d74848b-c1f5-4107-a07f-13bcfc1d9cb7` and its private proof/context remain
retained. Parent audit checked11,617 hashes/entries; all11 owned containers and21
process groups stopped normally, with API exit0/no OOM and no fixture-port listeners.
The earlier4fecf04d successful proof and safe JSON remain superseded pre-review
history; all failed-attempt history remains. The original190-input archive/qualification
and live bundle remain unchanged. This
qualifies the frozen Access image only; whole Scribeswell production-image and actual
environment release/recovery, external SMTP and physical-device gates remain.

Impacts: owner readiness/qualification, consumer artifact example and documentation;
no shared UI, generator, agent-context or ADR changes. Recipient/invitation and
Notification remain undelivered. Physical-device and external SMTP gates remain.

## Bounded sole-consumer production preparation — 2026-10-28

The [bounded rollout runbook](BOUNDED_STUDIES_ROLLOUT.md) now permits an app-local
production configuration for exactly one existing canonical account, still subject
to fresh current Access authority on every request. Enrollment is blocked before
upstream mutation; the bounded frontend checks current private read authority before
creation. The default remains public-only. This narrows the earlier unconditional
production refusal; it grants no deployment or production SQL authority.

The offline app-only preparer preserves retained unrelated Compose/gateway/env
configuration, binds exact source/image/proof references and same-project restricted
credentials, and leaves Access unusable until the supervised private head0009
report and actual archived owner preparation pass. It consumes only qualified
Identity0026/Access0019 readiness v2 and the exact frozen qualified Access image.
Global whole-registry guards and the mixed Identity0027 tree remain unchanged.

Focused local PostgreSQL17 proof preserves saved content, revision2, operation
receipt and actual public reads across private-route disable/restore, plus fresh
head/repeat and failure/forward retry. Parent browser and actual candidate-image
checks are retained with explicit limits in
[the bounded evidence](evidence/bounded-studies-rollout-20261028).
Actual production inventory/account/credentials, registry publication bindings,
coordinated target maintenance/readiness and live consumer verification remain
unresolved. No environment was activated; prior external SMTP, physical-device and
sharing/Notification gates remain separate.

Bounded-rollout parent completion: final affected suite127 passed3.25s after all six
BMAD review findings were fixed (two findings shared the inline-environment root
cause). Focused native3, bounded browser4 plus default enrollment2, API60-file and
migration40-file image proofs remain separately scoped. Actual image inspection
found and fixed0600 generated-helper readability in migration packaging. No generated
source was edited. No finding was deferred; production execution is still unapproved.
See [parent post-review output](evidence/bounded-studies-rollout-20261028/parent-postreview.log).

Post-BMAD read-only production preflight was attempted using the existing boabab
SSH configuration. The private-network connection timed out (exit255); no current
production metadata, database query or mutation occurred. [Safe diagnostic](evidence/bounded-studies-rollout-20261028/production-preflight.json).
Restore that existing connection before collecting the target-specific approval
bundle. Do not substitute historical inventory or approve activation from local proof.

## Live target follow-through — 2026-10-28

Private SSH to the renamed `machon` host now works. [Actual target readiness](STUDIES_TARGET_READINESS.md)
replaces the connection blocker with evidenced owner/consumer blockers: production
Identity is postgres-owned with no owned ledger; Access is0001 with three real PtS
grants; the actual PtS image uses `/v1/check`, while the qualified frozen Access
image deliberately refuses it. The managed deployment login is not superuser, so
the existing superuser-only Studies role helper also cannot be assumed executable.
Public reading passed200/39books; Studies remains404; no production state changed.
A coordinated Identity/Access/PtS adoption scope decision is pending. Do not activate
or ask approval for the previously generic sequence against this target.


### Hosted E1 native checkpoint — 2026-11-01 17:54 UTC

Shared production adoption remains owned by this release; production is unchanged.
Implementation and new private fixtures are isolated in
`apps/scribeswell/.local/shared-adoption-identity30`. Canonical0030/0019 Studies
qualification passed at its retained source boundary. The managed successor has
true `identity_0031_e1_hosted` / `access_0020_hosted` histories; no canonical revision
is stamped or claimed through that ancestry.

The independent source-only E1 reference reconstructed and rolled back the full
predecessor/successor. Native attempt01 exposed false-only catalogue rows for an
unrelated inaccessible schema. The source query was corrected with RED/GREEN,
retaining explicit owner/Auth denial and positive foreign authority checks.
Attempt02 then passed managed preparation/repeat, actual42501 foreign-read denial,
deliberate foreign-grant refusal and unknown-state checks. It stopped at a
restricted-migrator verifier name lookup requiring Auth schema access. A rollback-only
diagnostic confirms catalogue-OID privilege lookup works without that authority,
and the successor contract SQL itself executes under the real restricted migrator.
The verifier repair and stronger failure-injection attribution are in progress;
no complete hosted qualification, final image qualification or release approval is
claimed. Both failed attempts and exact315-input source archives are retained.
Attempt01 containers were stopped normally, with predecessor heads/data intact.

Next: finish focused managed-owner qualification, then app-owned Studies role/TEMP
preparation preserving every existing consumer's effective privileges; integrate
source-bound hosted readiness, existing shared adoption tools and the complete
service inventory before presenting a concrete maintenance/recovery approval.
No Leave/KDG activation is included. Do not restart/reset retained fixtures or
rebuild completed E1 PtS/Content work.


### Hosted E1 qualification completed locally — 2026-11-01

The repaired managed-owner candidate passed20 native stages in10.958s, including
attributable injected failure, preserved predecessor state and successful forward
retry/repeat. Parent109 focused checks passed. Genuine provider signin/logout,
explicit owner account-actor/person commands, restricted current-session/cleanup
clients and actual Access People API200/404/403/403 with no-store also passed.
Safe receipt: [hosted E1 owner qualification](evidence/hosted-e1-owner-qualification-20261101.json).
True heads are identity_0031_e1_hosted/access_0020_hosted, mapping the specified
canonical E1 contracts; canonical0030/0019 was not executed through that history.
Source-derived reference is5551c2128fb713a579a894d57e430fb42f3669c6345474398cdc45476d7cbe0f.
The prior failed attempts and exact inputs remain retained. Current ordered BMAD
implementation is phase C: managed Studies role preparation preserving all current
roles' effective CREATE/TEMP privileges, with the changed future PUBLIC defaults
explicit. Production, final images and activation remain unchanged/unqualified.


### Managed Studies preparation completed locally — 2026-11-01

Phase C native checks passed:63 existing roles' privileges preserved, new private
roles restricted, actual preparation rollback, private migration DDL failure and
forward retry/repeat to0009, saved-note/isolation/concurrency/deadline oracles,
public-reader preservation and unchanged hosted E1 owner catalogues.
Safe [managed Studies preparation evidence](evidence/managed-studies-preparation-20261101.json).
Parent160 focused checks passed. Current implementation is phase D1: a separately
qualified schema5 readiness path for the true hosted pair and bounded single-account
pregranted mode. No historical proof is relabelled. Native/runtime images and the
shared activation/recovery coordinator remain gates; production is unchanged.


### 2026-11-01 bounded hosted readiness checkpoint

The repaired schema5 source passed285 focused checks and a new genuine-provider
native qualification on retained cohort05. True owner heads are
identity_0031_e1_hosted/access_0020_hosted, using the unchanged reviewed reference;
canonical0030/0019 histories are not claimed. Actual private saves/reloads, all six
current denial cases,21 runtime authority denials and separate-account final
readiness preparation passed. Both preparation owner transactions were observed
read-only; denied access preserved saved rows. Two failed cohort04 attempts remain
historical evidence of the repaired local-profile no-row refusal mapping.
See evidence/hosted-bounded-studies-readiness-20261101.json for exact sources and
receipt/archive digests. This is a local source boundary, not packaged-image or
production-target qualification. Production remains unchanged. Existing public
reader/corpus contract retention and private-only migration/coordinator gating
are the next bounded work; Leave/KDG activation remains excluded.


### 2026-11-01 private migration and actual-target preparation checkpoint

Explicit private-only migration selection is implemented in the isolated release
checkout. Parent regression133passed/77opt-in native skips/99subtests and four
actual subprocess repeat/lock-refusal/timeout/forward-retry observations passed;
public postgres-owned no-ledger corpus/read and11studies/4notes/18receipts remained
unchanged. Fresh-schema/packaged integration remains a later gate. See
evidence/private-only-supervisor-20261101.json; prior schema5 proof is historical
after these source-bound changes.

The new forced-read-only actual check refused the original hosted predecessor
profile. Independent fresh source construction matches the original reference;
exact target differences are the standard Alembic PK name, stronger token-hook
PUBLIC denial, legitimate Access runtime schema USAGE and postgres's own migrator
membership edge. The same delivery is extending explicit, independently generated
operational predecessor support while preserving strict original profiles, old
references, real migration graphs and the stronger denial. See
evidence/actual-operational-predecessor-20261101.json. No production preparation
or migration has run.

Private proposed inputs now bind all three PtS grants explicitly to the same
verified existing account, preserving all six accounts. Studies authority remains
a separate explicit pregrant. Existing Content/corpus models validated ten exact
associations/objects; all191609122legacy bytes passed conditional reads/hash checks.
Content adoption will copy verified candidates while retaining originals; no
provider write occurred. Hosted Auth reportsGoTrue v2.197.0; signup stays disabled.
The complete inventory is Access/Content/PtS/Scribeswell/Directory/gateway. Proposed
files.scribeswell.com needs a Dynadot A record and its own TLS certificate; current
DNS is absent and current certificate covers api.scribeswell.com only. All are
proposals pending final preflight and execution approval; see
evidence/proposed-target-bindings-20261101.json. Leave/KDG remain downstream only.


### 2026-11-01 actual operational predecessor gate resolved locally

Explicit hosted-operational-postgres-v1 now exactly matches the actual production
predecessor in a fresh read-only check; managed capabilities are present. Independent
rollback-only operational and separately named E1 successor references were generated
and pinned; historical9b4/5551 bytes remain unchanged. A failed recorder completion
receipt and its unqualified reference/source are retained, repaired and independently
regenerated; it is not qualification.

Actual operational preparation/ordinary Alembic failure/rollback/forward retry passed
27stages, then20existing E1 stages in-place to true identity_0031_e1_hosted/
access_0020_hosted. The original predecessor path also passed separately. Exact
source bindings, archived grants/data/OIDs/sequences, provider ADMIN edges and stronger
token-hook PUBLIC denial passed. Parent331checks/0skips also passed. Runtime schema5
now binds the selected E1 successor file/hash explicitly. See
evidence/operational-owner-qualification-20261101.json. This source/native boundary
does not establish packaged HTTP/provider or production migration/activation.
Continue existing complete-inventory coordinator/runtime/frontend/gateway integration,
hosted PtS selection, exact images/target bindings and data-preserving recovery before
requesting production execution approval. No production mutation occurred.


### Parent maintenance carrier check — 2026-11-01

An exact145-file read-only source copy (143 selected hosted reference source pins
plus the pinning module and selected reference) passed the existing immutable
Content image's real source verifier with network disabled and no credentials.
The same image then executed ordinary hosted E1 Identity and Access Alembic head
repeats on nonce/image/loopback-verified retained cohort08, exit0 in2.931s and2.676s.
No owner source, migration or reference changed; this proves these packaged
dependencies/commands, not the future rebuilt PtS migration image or app consumers.
Safe proof: apps/scribeswell/docs/evidence/hosted-carrier-repeat-20261101.json.

Original-profile cohort09 completed23+20native stages and is stopped normally;
provider/database exit0/noOOM, volumes/network/data retained. Cohort08 remains
running and retained for subsequent focused checks. No production state changed.
D2b.1 source integration remains in progress; do not execute its pending candidate.


### D2b.1 bounded release integration — parent source checkpoint

Parent inspected the actual runtime/build/render/report diff and verified251tests/
139subtests in11.24s plus18Node coordinator/fingerprint tests in1.302s. Active
and public-only recovery builds retain current PtS and have distinct fingerprints;
only matched schema5/account/no-enrollment/private-role configuration emits the
narrow Studies routes. Full inventory and public route objects are preserved.
The archived exact18-file source boundary is recorded in
[evidence](evidence/bounded-runtime-source-20261101.json). This is source integration,
not new native/image/target qualification. Production remains unchanged. Next is
explicit hosted PtS migration repeat/packaging, then maintenance/forward recovery,
exact candidate qualification and concrete production execution approval.


### D2b.2 actual hosted PtS migration image — parent checkpoint

Explicit hosted migration selection and exact Access20/Content5/PtS3 report
gates passed parent21tests/60subtests. Fresh isolated frozen runtime packaging
passed; MAIN bundle was preserved. Initial actual Docker verifier refusal exposed
a context rule excluding five SQLAlchemy dependency fixtures; narrowed allowlist
repair preserves all5310 frozen entries/provenance and private fixture denials.
Fresh offline build/inspection passed as actual UID10001 with all143 selected
owner pins and190 exact installed source files, no mismatch/extra file. See
[evidence](evidence/hosted-pts-migration-image-20261101.json). This is a local
image packaging boundary, not native database/consumer/target qualification or
registry publication. Production remains unchanged; next is restricted actual-
target owner command transport, then existing maintenance/recovery coordination.


### D2b.3 restricted owner transport — source checkpoint

Parent inspected the new owner CLI and passed135focused tests in0.45s. It reuses
existing owner execute/outcome/parsers/receipt/session policies, with private
project/role/TLS inputs and fixed-operation reconciliation; disposable target
guards remain intact. See [source evidence](evidence/release-operator-source-20261101.json).
Actual restricted-session/TLS/carrier proof is pending. Fresh owned cohort11 now
has real database/provider TLS;08 is unchanged. Failed allocation10 (missing
OpenSSL executable in PG image) retained its labelled network/emptyTLS volume;
11 used host OpenSSL and passed real SSL-session checks. No production mutation.
Next source work closes file-certificate maintenance through the existing TLS
owner, then existing rollout/host maintenance/recovery integration.


### Continuation boundary: TLS owner commands and candidate Access image — 2026-11-01

Production remains unchanged and no execution approval has been requested. Continue
the same isolated shared-adoption-identity30 checkout/spec; preserve its inherited
source and MAIN unrelated changes. Current ordered source work is D2b.5 maintenance
entry/protected stop/backup gate, not Leave/KDG activation or a separate migration.

The retained TLS cohort11 passed operational predecessor27 and hosted E1-20 native
stages. Honest observed owner heads are identity_0031_e1_hosted/access_0020_hosted;
canonical0030/0019 were not stamped or executed. See
[evidence](evidence/operational-owner-tls-20261101.json). Actual restricted owner
commands ran with immutable Content carrier e915a8d5… at configured UID65532 and
explicit PostgreSQL TLS. Six command types, three account grants, replay/outcome,
wrong account/current disabled principal denials and exact preservation passed.
A deliberately discarded receipt body was recovered; actual COMMIT socket loss was
not simulated. See [source-bound proof](evidence/release-operator-native-20261101.json).
All private inputs/failed attempts remain retained; no production command ran.

New offline Access runtime image ID
sha256:a5f191ae82526f2b59341c2af20ecd4a5e6c85cf817a909eb6d15b91f2f75a9a
has observed Python3.15/UID65532 and exact26 installed source modules; provenance
7d3f4aec19f1e0263e6749d8ba6b693dbad73586325915944cab52730a2b3592.
See [image evidence](evidence/hosted-access-runtime-image-20261101.json). This local
image has no published RepoDigest or final coupled consumer/readiness claim.

Enforced actual-target read-only inspection confirms Content/PtS schemas and all
their tables already belong to content_migrator/pts_migrator; existing logins are
restricted. Preserve existing postgres admin/SET edges. Identity/public Scribeswell
remain postgres-owned; private Studies absent. No new Content/PtS ownership transfer
is needed. See [custody observation](evidence/actual-owner-custody-20261101.json).
New selected consumer roles must exist before exact managed Studies preparation.

Parent independently reran the five affected TLS/host/gateway suites:120 tests and
125 subtests passed in17.41s. Dedicated file certificate source/managed copies,
interrupted owner recovery and maintenance exclusion are implemented locally;
DNS/HTTP80/issuance and actual gateway/PtS TLS remain unexecuted prerequisites.
Historical Scribeswell migration Dockerfile names an absent floating local base;
its new packaging attempt stopped before build/fetch. Resolve dependency custody
explicitly, without relabelling an older image or performing an unrelated upgrade.
The final maintenance activation contract, explicit owner bootstrap/commands,
actual packaged migration/readiness, recovery artifacts, review and separate
production approval remain required. Retain full six-service inventory/public
reading and all accounts/grants/corpus/Content bytes/Studies rows and receipts.


### Maintenance coordinator and packaged PtS migration native proof — 2026-11-01

D2b.5 source is settled. Parent independently ran188 affected tests/125subtests,
all passing in24.88s. The actual maintenance coordinator then stopped exactly four
protected disposable processes, kept gateway/public Scribeswell process IDs
running, retained its marker on a real failed dump and verified a new private
custom backup/list on exact-bound retry. TLS rotation refused the marker.
[Native evidence](evidence/maintenance-coordinator-native-20261101.json) distinguishes
process preservation from app HTTP availability; no production backup or restore
was performed. Failed allocations and all fixture resources remain retained.

Actual PtS migration image5746eb2c… passed real restricted/TLS hosted Access20
repeat followed by Content5/PtS3. A missing corpus binding failed with applied
histories retained; exact reviewed recovery and repeat passed, changed binding
and wrong profile refused, all seeded corpus/accounts/actors/grants exact.
[Migration evidence](evidence/hosted-pts-migration-native-20261101.json) records the
193 source hashes/archive and limitations. It does not prove actual Content byte
adoption or final coupled readiness. Separate
[backup carrier evidence](evidence/backup-carrier-tls-20261101.json) records real
PG17 custom dump/archive-list transport, without a restoration claim.

Current ordered source dispatch D2b.6 resolves Scribeswell release-only API and
migration packaging with existing qualified dependency bytes. Ordinary offline
API build also hit uncached dependency installation; no packages were fetched or
upgraded. Older qualified API source differs in3current files and cannot be
relabelled as the current candidate. Remaining successor activation/owner calls,
exact final native/image/readiness/recovery/review and execution approval gates
stay in this same delivery. Production remains unchanged.


### Packaged Studies migration and both frontend variants — 2026-11-01

The current release API and private-only migration images passed actual offline
nonroot source/import verification. Dependency bytes match the explicitly selected
carriers; [image evidence](evidence/scribeswell-release-images-20261101.json) binds
the actual local IDs and source archives. They are not published registry digests.
The actual migration image then passed held-lock failure, forward repeat, second
repeat and authority refusals against retained TLS cohort11. All saved Studies
rows/revisions/14receipts, public rows and missing public ledger remained exact;
see [native evidence](evidence/private-studies-release-image-native-20261101.json).
Managed preparation separately preserved71 existing roles after Content/PtS roles
existed; [evidence](evidence/managed-studies-tls-20261101.json).

Both shared frontend variants actually built with Node26.11.1: primary5.332s,
public-only recovery5.627s. Their PtS artifact bytes are identical; Studies inputs
and fingerprints differ. All172 inventoried source files stayed unchanged during
the builds. [Frontend evidence](evidence/frontend-variants-20261101.json) retains
artifact inventories/source archive; release SHA is deliberately null until the
selected source commit exists. No browser/public HTTP recovery or deployment claim.
Earlier local tooling/parent assertion failures remain retained.

Current ordered source dispatch is D2c: explicit hosted successor preparation,
image inspection and the real read-only owner readiness gate in the existing
rollout tool. Final matched maintenance activation/recovery integration, fresh
source-bound coupled qualification, owner bootstrap/adoption run card, review and
execution approval remain. No production changes or image/frontend publication.

Actual current API image also passed default production-mode startup, health and
anonymous public books HTTP against the retained TLS fixture, with private Studies
routes absent. All saved/private/public/account/grant snapshots and missing public
ledger stayed exact. Its newly owned container stopped normally0/noOOM and remains
retained. [Recovery API proof](evidence/public-recovery-api-native-20261101.json)
is one synthetic book/API-only, not full gateway/browser/coupled recovery execution.


### Remaining cutover integration constraints

Ordinary host preflight still correctly requires previous-version compatibility
and refuses maintenance-pending. The next ordered source phase must add only the
explicit matched maintenance-forward path: bind the existing protected-stop/backup
marker, exact candidate images/inputs, successful migration reports and fresh real
owner readiness before activation. Do not set previous_version_compatible=true
for the incompatible old PtS caller. Keep the full six services. Preserve the old
pointer/Compose evidence while consuming matched maintenance state only after
verified activation; interrupted/unknown outcomes remain blocked and recoverable.
Public-only recovery uses the new shared owners/current PtS and the same candidate
API with Studies off, retaining all saved rows/revisions/receipts and applied heads.
A15minute maintenance budget must bound primary activation while leaving explicit
public recovery possible if that budget expires.

Initial dedicated file TLS needs separate DNS/HTTP80/issuance approval and proof.
Stage the new Certbot lineage into its distinct managed PtS certificate/key paths
without overwriting Certbot links or the existing API certificate. The active
renewal configuration and current gateway/pointer must stay coherent across first
activation; a prepared future file-origin configuration is not proof that the old
live gateway already contains that SSL owner. Existing renewal and ordinary host
operations continue refusing the maintenance marker.

The final bounded native qualification driver has been prepared locally but not
executed. It reuses genuine cohort11 provider accounts/operator authority, preserves
the existing A actor, explicitly creates only B attribution/Studies prerequisites,
and executes with the planned production release ID from the outset. Its final run
waits for source integration to freeze. Production executor/account bindings are
distinct from qualified fixture identities; never rewrite the qualification IDs
or immutable runtime principal attribution to make a target gate pass.

Recovery must also cover failure before the shared owner pair is complete. In
that state retain the verified public API/gateway, keep all four protected consumers
stopped, and continue forward repair under maintenance. Do not start new protected
consumers against partial heads or restart old PtSv1. Public-only recovery inputs
still declare the complete inventory; once shared prerequisites are verified they
may run current shared/PtS consumers with Studies off. No applied history, account,
legacy corpus/original byte, adopted byte or saved Studies row is reversed/deleted.
Frontend publication ordering must avoid exposing the incompatible old PtS browser
consumer after shared activation; both prepared variants contain the current PtS.

Actual deployment source transport is another explicit D2d prerequisite:
ci-deploy.sh uses git archive into /srv/agriplatform/incoming/<canonical-sha>,
without .git. Current maintenance_revision() calls git rev-parse HEAD, so local
checkout preparation alone does not prove archive-host execution. Add an explicit
verified archive/source identity binding through existing deployment/rollout owners
before approval: compare canonical archive identity, retained archive digest and
approved source-byte closure, and refuse missing/changed/arbitrary SHA claims.
Preserve ordinary Git checkout behavior and historical proof. This is source
transport verification, not permission to publish or deploy.


### Hosted successor gate source verified — 2026-11-01

D2c source is settled: explicit hosted preparation/image inspection/read-only owner
gate, complete current-consumer/public recovery inputs, privileged private custody
and exact process reconciliation. Parent independently passed104focused checks
in103.44s; source/tests remained unchanged. Agent passed406affected checks plus
171subtests;77existing native skips establish no native proof. Historical60setup
errors still identify the absent original /tmp archive and were not weakened.
The 624-file source archive and 337-file owner tool bundle are bound in
[source evidence](evidence/hosted-rollout-source-20261101.json). Actual carrier/
UID0/current-provider/gate qualification remains pending.

Next source phase D2d adds verified production archive identity and matched
maintenance-forward activation/data-preserving recovery through existing owners.
Ordinary release/TLS exclusions remain binding. Production remains unchanged.

Existing Content adoption CLI now imports/parses in immutable e915 carrier as
actual configured UID65532, with its exact nine runtime modules plus adoption
source; [carrier proof](evidence/content-adoption-carrier-20261101.json). No
database/provider operation occurred; this does not prove byte-copy permission.

Private production-owner-commands-03 now contains13 exact proposed owner commands
validated by unchanged Identity/Access parsers, plus separate bootstrap intent and
Studies pregrant operation. Separate accountless release/Studies executor and PtS
Content runtime actors are explicit. [Preparation evidence](evidence/proposed-owner-commands-20261101.json)
records no execution authority. Earlier proposal's release_adoption reason was
unsupported; new unexecuted operations use accepted identity_adoption. The partial
preparation attempts remain retained. Actual owner/bootstrap SQL, target credentials,
real command outcomes and byte adoption remain pending and require approval.

Private production-owner-commands-03/bootstrap-sql-01 now contains exact initial-only
Identity/Access bootstrap SQL, separate read-only observers and explicit Studies
pregrant SQL. Existing-principal drift refuses before writes; an unknown owner
commit is observed as absent/exact-prepared/drift before any forward execution.
Actual TLS original-owner READ ONLY checks passed both observers/refusals and
PostgreSQL PREPARE/EXPLAIN for all7 INSERT statements, with all retained rows exact;
[limited native proof](evidence/owner-bootstrap-sql-readonly-20261101.json). No INSERT
or pregrant executed. Positive bootstrap/target credentials/native gate and final
production execution approval remain pending. Original bytes/failed drafts retained.

Minimal consumer-role preparation is now explicit in private proposed-missing-
consumer-roles-01: only the two absent PtS successor roles, with account runtime
LOGIN and corpus importer NOLOGIN; own-schema USAGE executes separately as
pts_migrator. Existing Content/PtS roles, flags, passwords, ownership and provider
edges are preserved. An unused Content operator role is not required by current
selected statements and will not be created merely because a synthetic fixture
had one. Ten new login credential proposals are private/unapplied; no existing
password is rotated. [Input evidence](evidence/proposed-consumer-role-inputs-20261101.json)
is preparation only; fresh role observations, native execution/connection proof
and approval remain required. No importer/application or production activation.


### Positive owner bootstrap qualification — 2026-11-01

A separate retained TLS cohort12 now proves the initial controlled owner bootstrap,
not just parsing: both owners moved absent to exact-prepared, rejected repeat
initial insertion and identified rollback-only drift. All13 proposed command
shapes executed through the immutable Content carrier as UID65532 with restricted
original owner-operator logins; replay/outcome checks passed. Explicit restricted
Studies pregrant and repeat produced three PtS grants in access.account_grants
and one separate access.studies_account_grant, with correct executor/initiator,
no organization membership and unchanged legacy archive. Exact replay preserved
all observed retained rows. [Positive evidence](evidence/owner-bootstrap-positive-20261101.json)
binds original proposed SQL plus counterpart SQL with only three synthetic UUID
substitutions; no production account authority is inferred. Earlier incomplete
parent qualification attempts remain retained and disclosed. Production bootstrap,
commands, pregrant and activation remain unexecuted and need approval.


The exact proposed two-role managed SQL and separate pts_migrator schema-USAGE
SQL now passed real TLS cohort12 execution. Existing role OIDs/flags remained exact;
PtS corpus importer stayed NOLOGIN and no unused Content operator was created.
The immutable5746 migration image reached Access20/Content5/PtS3, preserved its
three-row corpus and owner identities, refused missing/changed bindings, and
recovered forward with exact binding/repeat. [Focused role/image proof](evidence/minimal-consumer-roles-native-20261101.json)
is synthetic counterpart evidence only; actual target role preparation, credentials,
provider copying and migration execution remain unapproved/unexecuted.


### Current Access/provider image proof — 2026-11-01

Actual selected a5f191ae Access image now passed default nonroot startup and real
GoTrue2.197 current-account capability/session/cleanup HTTP checks against TLS
owner connections in retained cohort12. Canonical account access, anonymous/wrong
key/scope denial, intentional legacy-v1 503 closure, dedicated session key, cleanup
prepare/repeat/check and local sign-out of only the fresh qualification session
passed. Current-session denial then coexisted with the retained historical cleanup
receipt reporting the provider session absent. Accounts/actors/grants/archive
remained exact; only newly owned API/transport containers stopped, exit0, retained.
[Image/provider evidence](evidence/access-current-provider-native-20261101.json)
records the supported localhost-HTTP provider/transport-adapter boundary honestly;
this does not establish production provider/gateway/Studies or whole-host activation.

Read-only machon observation also confirms Node/npm are absent. Host forward
execution must verify producer-owned source/artifact/fingerprint evidence through
its approved bindings; it must not assume host JS tooling or install an unqualified
toolchain during maintenance. Actual DNS/TLS/adoption/publication/cutover remain
unexecuted and require the final concrete approval.


Exact private first-assignment SQL is now prepared for the10 originally absent
login roles in four sequenced files; no existing Content/PtS/Access migration or
runtime password is rotated. [Proposed credential SQL](evidence/proposed-new-credential-sql-20261101.json)
requires fresh role absence, exact preparation receipts/new OIDs and original-role
TLS reconciliation of unknown outcomes. All four exact files passed actual managed
postgres TLS execution inside rollback-only cohort12 transactions: all global role
OIDs/flags/password hashes/settings/memberships/database ACLs remained identical.
[Rollback-only proof](evidence/new-credential-sql-rollback-native-20261101.json)
does not establish actual target provenance or install any production credential.

Distinct-target managed Studies preparation also passed13 steps after the minimal
current consumer roles existed, with original role/database privilege preservation,
private migrations/storage and public reader retained. [Separate-target proof](evidence/distinct-target-managed-studies-20261101.json)
remains separate from final source-frozen bounded readiness and host activation.


Private coordinated service-key bindings and minimal Content policy are prepared
for the selected actor split. Four distinct fresh private service keys pair
Access/PtS/Content, Access/Directory, Access/PtS current-session and Access/private
Scribeswell respectively. [Proposed bindings](evidence/proposed-runtime-service-bindings-20261101.json)
are uninstalled and require the coordinated stopped-consumer transition. No
provider, public Auth, API TLS or existing database credential changes are implied.
Actual immutable Content image e915 loaded the exact proposed policy as configured
UID65532 mode0600 with network disabled; PtS application read/metadata passed,
create/finalize/wrong-key/wrong-app denied. [Policy proof](evidence/proposed-content-policy-native-20261101.json)
does not establish actual target actor/current permissions, provider bytes or
whole-runtime readiness. Proposal bytes stayed exact, all new test custody restored.


### Settled-source Studies and post-save backup — 2026-11-01

Fresh source-bound schema5 qualification passed all7 native Studies stages on
retained TLS cohort11 using planned release scribeswell-pts-hosted-e1-20261101,
real provider sessions, restricted owner SQL and actual private save/reload/denials.
[Final bounded native proof](evidence/final-bounded-studies-native-20261101.json)
archives338 source files; historical earlier qualifications remain unchanged. A
Docker-only operator URL caused initial host-driver connection failure before
commands; exact partial preparation/credentials were observed and preserved while
correcting only host transport. Actual immutable distinct-target readiness/default
image coupling and whole-host preparation still have their separate gates.

Post-completion recovery's fresh backup now has actual saved-data evidence: original
managed postgres over TLS dumped all five schemas including scribeswell_studies
in1.462s,736282bytes. Network-none archive list/data extraction independently
matched9 Studies,2 notes and14 receipts; all saved rows stayed exact. No role/ACL
workaround, restore or PITR claim. [Post-save backup proof](evidence/post-save-five-schema-backup-native-20261101.json)
supports the runbook's fresh-maintenance/current-pointer/current-consumer recovery
path after primary completion. Actual target backup remains a mandatory live gate.

Parent reran existing TLS verification with loopback permission:42passed and38
subtests in13.36s. This resolves both sandbox EPERM failures; production TLS/DNS
initialization is still unexecuted. Parent archive transport13 tests passed67.42s.


### Separate-target immutable readiness CLI — 2026-11-01

The unchanged owner readiness CLI now passed as immutable e915 carrier UID65532
against separate cohort12 original Identity/Access TLS logins. It consumed final
source-frozen cohort11 qualification and produced schema5 with genuinely distinct
qualified/target accounts AND executor actors. All six observed public/private
owner row sets remained exact. [Carrier/target proof](evidence/distinct-target-readiness-carrier-native-20261101.json)
binds readiness5fd98aae8fd685d03dfd4f4c55c33c0878c394489f44d8249a4b6ede1d32dd00.
Initial local Docker staging timed out before CLI creation and remains retained;
its prematurely reported custody flag was independently corrected/restored. Named
observed helper custody succeeded on fresh staging. This establishes actual owner
CLI/carrier permission and distinct-target readiness, not whole privileged-host
coordinator execution, production target authority or activation.

Parent independently passed58 forward activation/recovery tests in252.06s,
including completed primary to fresh maintenance/current-public recovery, and13
real Git/archive source transport tests in67.42s. Formal review and concrete
canonical publication/actual-target maintenance inputs still remain.


### Packaged save/recovery and public entry correction — 2026-11-02

The exact selected default Scribeswell API618ba7e6 and Accessa5f191ae images
passed genuine-provider/restricted-TLS private save/reload, anonymous/foreign-account
and enrollment denial, current availability disable/re-enable, Access-outage public
reading, and current-public recovery. Recovery kept current PtS account access and
all11 Studies/4 notes/18 receipts exact; no restore or reverse migration was used.
[Packaged pair evidence](evidence/packaged-studies-pair-native-20261102.json)
preserves the exact image/readiness/source boundary. A prior harness enum assertion
and its explicit owner-command availability repair remain recorded separately.

Public observation identified a release-layout gap: production Scribeswell reads
at the existing site root, while the earlier shared frontend artifacts put PtS there.
Those artifacts are retained historical evidence and must not be published for this
site. The explicit bounded publication correction preserves Scribeswell `/` and puts
current PtS at `/pts/`; primary and recovery must share that layout. Its source/build/
readiness review is a separate successor boundary.
[Observed entry layout](evidence/public-entry-layout-20261102.json).

The immutable UID65532 carrier also executed both selected hosted preparers' help
and all four selected Alembic history commands offline, with all173 tool-source
files bound and all six retained containers exited0. This confirms the selected
source transport imports, not target permissions or migration execution.
[Offline owner tools](evidence/initial-owner-tool-carrier-offline-20261102.json).
Alembic1.20.0 remains an explicit qualified release override. Canonical release
source, actual corrected frontend builds, refreshed qualification, concrete target
inputs and formal review remain gates before production execution approval.


### Frozen public-root successor qualification — 2026-11-02

D2e's623-file source binding eaf12b55392616897f0bf8357229f0183de1a9cf2f7b91d81710737128b96f4f
passed392 source tests/145 subtests and22 selected Node26 tests. The old historical
suite still reports4pass/60setup errors for its missing retained /tmp source archive;
this has not been replaced with a different historical source or relabeled success.

A NEW seven-stage native qualification binds338 current source files and genuine
provider/owner SQL behavior at this boundary, qualification
ce364299bd42e16f16d99801f9bbc81d42adc651c5a038f4d66102ab5c4199bb.
It reused the existing target and created one genuine local counterpart, retaining
all previous data/credentials/revocations. [Native proof](evidence/public-root-bounded-studies-native-20261102.json).
The immutable UID65532 owner CLI independently prepared readiness against separate
cohort12 original-owner TLS logins, with distinct target/accountless executor IDs
and all six owner/public/private row sets exact. Readiness
274953fb52b8ac33657f6de8ea5442c831309e1870a22ee17b9e241fc698a503
is bound by [separate-target proof](evidence/public-root-distinct-readiness-carrier-native-20261102.json).

The SAME selected default API/Access images then passed the full local private
save/reload, denial, current availability and public/current-PtS recovery checks
using that NEW artifact. All12 Studies/5 notes/20 receipts remained exact; only the
newly owned five runtime processes were stopped normally and retained. No new
cohort12 Auth account or credential rotation was needed.
[Refreshed packaged pair](evidence/public-root-packaged-studies-pair-native-20261102.json).
These results supersede only their source/readiness qualification boundaries;
all historical receipts retain their exact original identities. Corrected real
frontend builds/canonical source transport/formal review/target runtime inputs and
separate production approval remain open. No production mutation/publication.


### Canonical frontend proof and actual gateway correction — 2026-11-02

Local candidate5e148e99db51de7459688854fbe1fafc9767bca2 captured404 selected release
changes while466 unrelated changes remained unstaged; MAIN stayed at
e16d441ff26cee838f81fe118f980c7971c1745f with its index unchanged. Its full5505-file
canonical archive/consumer verified all623 release pins. Both real Node26/npm12
Scribeswell-root variants built and passed the authoritative JS artifact verifier;
current PtS assets were exact across variants. Four actual Chromium desktop/mobile
checks passed for root reader/deep-query/reload and PtS `/pts/`, with explicit
API/Auth doubles and no production traffic. [Canonical build proof](evidence/canonical-public-root-builds-20261102.json),
[browser boundary](evidence/public-root-browser-20261102.json).

The actual archive-owned image inspector then exposed incorrect gateway assumptions:
Docker's official APISIX reports configured user `apisix` and untagged RepoDigests.
D2f preserves the exact official repository/digest, proves default effective UID636
without a forced user, and now passes the actual eight-image inspection. API65,
migration45, Access26, owner143 and q3 readiness338 byte closures remain unchanged.
Only rollout.py changed within623 sources; final source binding is
6e88cc886c3f9db91440d51bdf540a7423d8bc08ce07c043d3a1e19b74577fc7.
[Default UID](evidence/gateway-default-uid-native-20261102.json),
[actual corrected inspector](evidence/gateway-corrected-image-inspection-20261102.json).
The failed original attempt is retained, never converted to success. A canonical
successor and exact publication/build identity renewal remain before final approval.
D2f269 affected tests passed; reporting-only final10 tests passed afterward. The
boundary report now truthfully marks Directory/file-auth HTTP as not-probed.

The concrete private run card pins37 proposed inputs and orders owner preparation,
10 new credentials/4 keys/13 owner commands, explicit Studies pregrant, migrations,
corpus/191609122-byte Content-copy verification, current-consumer activation and
saved-data recovery. DNS/certificate/tool/image/frontend preparation precedes the
900-second maintenance window. Allow330seconds after verified protected-stop backup
for old signed-read URLs to expire; never promise recall of delivered bytes. The
producer's complete private-candidate checks run on machon with a proposed pinned
private offline Node/libatomic tool, without an OS package/global Node installation
or copying database/certificate/S3 inputs off host. Actual tool/version/JS checks,
provider copy permission, first file certificate, runtime staging and publication
remain conditional live gates. Supabase `/pts/` callback allowlist was asked read-only.

Automatic approval review rejected a proposed credential verification BEFORE execution:
existing Netlify/GitHub bearer tokens would be sent to their own APIs and a private
Netlify connection file retained. It requires explicit approval for that credential
use/custody. No command ran or workaround followed. Complete local review first;
include this specific use with the final production execution approval request.
No production account/grant/schema/object/configuration/publication change occurred.
