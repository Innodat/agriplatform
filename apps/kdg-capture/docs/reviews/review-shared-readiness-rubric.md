# Shared readiness architecture rubric review

2026-10-14. Independent bmad-architecture reviewer-gate rubric walker.

**Verdict: PASS for the selected architecture/contract baseline. This is not an
implementation-readiness PASS or approval to implement.** No critical/high semantic
defect was found in the reviewed boundary decisions. Remaining named planning inputs
must be dispositioned by the readiness workflow; executable acceptance remains later
delivery work.

## Scope and authority

Reviewed the current working-tree KDG architecture spine, platform KDG shared-readiness
addendum, KDG fingerprint disposition and app shared-prerequisites packet. Compared
the selected decisions against the approved PRD, current application command/receipt/
eligibility contract, canonical Access v2 wire and resume handoff. The user's explicit
sole-owner acknowledgement satisfies the requested owner acknowledgement; it is not
an open issue. No product discovery or delivery was performed.

This is the semantic rubric lens. Deterministic spine lint and independent adversarial/
technology lenses belong to the parent gate, not an inferred result of this report.

## Rubric assessment

| Criterion | Assessment |
| --- | --- |
| Real divergence points fixed | PASS. Capability authorization scope is distinct from resource ownership; author/account and membership renewal are distinct; Access and KDG retain separate authorization/domain responsibilities; setup cannot impersonate a target; old queued commands preserve identity and receipt semantics. |
| Enforceable AD rules | PASS at planning altitude. AD-2 names exact current authority and restricted DB enforcement; AD-4 defines the atomic local acknowledgement boundary; AD-5/6 define replay and conflict ordering; AD-7/8 define local authority/partition limits; AD-9/10 preserve migration and release safety. Shared acceptance names real-role/concurrency/negative proof. |
| Non-obvious trade-offs | PASS. Fixed-org account-own authority without People, no unfinished observation persistence, seven-day local authority, online-only cross-account administration, update-before-sync, retained old-membership pending work and keyed initial fingerprints are explicit divergence-preventing decisions. |
| Approved scope covered | PASS. The FR/NFR mapping spans sign-in/setup, versioned questionnaire, explicit Save, own history/edit/conflicts, administration, offline isolation/sync/session/update and operating envelope. Selected shared refinements do not introduce a selector, observation autosave, employment dependency, conflict draft, worker or additional generator. |
| Parent/brownfield constraints | PASS. Existing Identity/Access/ENV/P1/SERVICE/WRITE/release owners retain authority. Accepted ADRs remain unchanged. New KDG closed variants extend the declared Access union while retaining PtS account/Leave person variants. |
| Deferred decisions safe for the next step | PASS for continued planning. Exact pins, executable commands, DDL/adoption/privileges, operator targets and key paths remain visible gates rather than implementation discretion disguised as closure. They do prevent claiming unrestricted Build readiness until resolved or allocated to a precise first consuming delivery item. |
| Whole operating envelope | PASS. Environment isolation, bounded requests/locks, diagnostic secrecy, runtime/migrator/operator separation, controlled migration/activation, key/data restore, installed-device qualification and pilot policy all have named owners and acceptance timing. |
| Technology evidence | No unverified KDG pin is asserted. Existing resolved-version evidence is explicitly reuse evidence, not selected dependency compatibility. Current technology fit and exact compatible selection require the separate technology/environment check. |
| Planning versus delivery | PASS. The addendum and work packet expressly distinguish selected contracts from installed APIs, generator/privileges/secrets and runtime/device proof. Shared substrate precedes consuming app behavior; missing runtime code alone is not a demand to implement during planning. |

## Material observations for readiness triage

### R1 — Exact environment and generator selections remain named planning gates

**Severity:** Medium; readiness follow-up, not a defect in the selected authority model.

The shared addendum selects recipe ownership, minimum keys, extension restrictions and
planned command names, but explicitly leaves exact compatible tool/package/container
pins, generation options, bootstrap invocation and real callback/device target open.
The spine/work packet preserve that qualification. A readiness report should state
which inputs must be selected before the first test is authored and which are actual
delivery proof before their consumer, rather than closing the entire ENV/P1 boundary
from the existence of these documents.

**Disposition:** Keep the named gate; resolve concrete planning selections through
the existing ENV/P1 owner item and preserve later executable acceptance. No new generic
workflow or extra product approval is needed.

### R2 — Physical privileges/adoption and secret wiring are deliberately unverified

**Severity:** Medium; affected-delivery gate, not missing logical ownership.

The addendum chooses authenticated PostgreSQL session_user mapping, separate owner
operator credentials, narrow setup HTTP authority and fail-closed HMAC key retention.
It correctly does not claim these choices establish a trustworthy installed operator
or recoverable environment. The exact DDL/adoption/privilege/invocation matrix and
secret-file principals/library conformance remain necessary before affected writes
or real data. A broad readiness PASS must not erase this distinction.

**Disposition:** Retain ID-A/ID-B/WRITE/ENV acceptance and earliest-consumer ordering.
Name concrete planning inventories where readiness requires them; verify actual roles,
rotation/rollback and matching data+key restore in authorized delivery.

### R3 — Membership renewal and account ownership are coherent but need paired fixtures

**Severity:** Low; acceptance emphasis.

The selected rules deliberately allow a same account, with newly approved current
read/edit rights, to access its historical observations after rejoin while refusing
an old-membership pending create under old eligibility. Both behaviors follow the
approved lifecycle policy. Testing only retirement denial would miss the historical
continuity half; testing only continuity would risk resurrecting old create authority.

**Disposition:** Preserve a paired acceptance fixture: retire/rejoin/explicit rights
renewal permits old own-record read/edit; the same transition rejects old create
eligibility until valid renewal. Do not add transfer, export or deletion policy.

## Conclusion

The selected architecture gives independent shared-owner and KDG builders a coherent
contract without expanding approved product scope. The remaining gates are identified
engineering selection/evidence work, not missing owner consent or an instruction to
restart requirements. Proceed with their bounded planning disposition and the required
readiness rerun; implementation remains separately unauthorized.
