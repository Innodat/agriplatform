# E5 planning closure — approved

2026-10-14. All four E5 stories and E5 planning closure are user-approved with C. This checks planned coverage only;
implementation, automated acceptance and actual phone/release evidence remain pending.

| Story | Approved scope |
| --- | --- |
| 5.1 | Minimal child create/name/status Save/Cancel; ordinary deactivation preserves pending observations under current access |
| 5.2 | Verified account/child assignments; no app grants; explicit renewal after membership retirement/rejoin |
| 5.3 | Bounded storage/update reliability; update first then sync; no mandatory adapter design |
| 5.4 | Integrated session/device/release evidence, simple guidance and Khula operating-policy closure before real-data pilot |

## Requirement allocation

| Requirement | E5 coverage | Boundary |
| --- | --- | --- |
| FR-12 | 5.1 children and 5.2 assignments | Identity onboarding/Access grants remain shared-owner workflows; no People/employment |
| FR-2/3/4 | Child/account eligibility, target verification, administrator create-all independence and automatic/small child choice | Fixed Khula; assignments grant no authority |
| FR-8/9 | Historical editing survives unassignment/deactivation with current rights; saved own conflicts protected in 5.3 | Online administrator conflicts stay in memory |
| FR-13/14/15 | 5.3 protected own local state/queue/update and truthful save/sync states | No other-author offline cache or universal offline framework |
| FR-16/17 | 5.2 membership generation/renewal; 5.4 expiry/logout/denial/same-user recovery evidence | No bypass upload or silent retention/deletion claim |
| FR-18 | 5.3 quota/schema/update/queue compatibility, 5.4 policy/device/release evidence | Browser eviction/uninstall/data clearing not guaranteed recoverable |
| FR-1–18 | 5.4 integrated evidence over earlier feature-specific allocations | Pilot evidence never substitutes for owning acceptance tests |

NFR-1–5 apply through authorization/attribution, transaction/idempotency/durability,
accessible administration/status, bounded execution and supported release/device proof.
UX-DR2/4/7–14 are allocated to current administration/reliability/proof; 5.4 checks
all approved UX scope without adding audit/version UI to capturer views.

## Scope and policy distinctions

Ordinary child inactivity removes refreshed choices but accepts prior-provisioned
pending observations if current access/assignment checks pass. Privacy processing
restriction/deletion is separate. Exact prior-eligibility evidence gates Build: a
client pending flag or phone date cannot prove eligibility or Save timing.

Membership retirement/rejoin needs explicit assignment renewal; same-membership grant
recovery alone does not. Trusted account/membership/capability evidence comes from
Identity/Access owners, never operator impersonation, email matching or direct tables.

Update first then sync is default. Safe unsaved-form/local-write/network handling
precedes reload, but pending edits/conflicts do not require successful sync first.
Compatibility is required; migrations/version handlers are added only for concrete
changed formats. No mandatory adapter framework or unfinished-form recovery.

Khula business/privacy owner, child-data processing basis, server/local pending/locked
retention/disposal and device suitability remain real-data pilot decisions. Seven-day
local access and 30-day own download windows are not retention periods. Synthetic
feature validation can proceed after implementation approval without a real-data pilot.

## Overall story inventory and next step

| Epic | Approved story count | Planning closure |
| --- | --- | --- |
| E1 first offline capture/sync/device proof | 7 | Approved |
| E2 own history/edit/conflicts | 4 | Approved |
| E3 online administrator review/edit/audit | 2 | Approved |
| E4 questionnaire working copy/publish | 2 | Approved |
| E5 assignments/reliability/pilot evidence | 4 | Approved |

Total: 19 approved stories, each scoped to preceding dependencies. Requirement/story/
acceptance traceability resides in testing.md and authoritative story text in epics.md.
No application has been built or tested, no shared contracts modified, and no production
change approved. Existing platform capabilities/design gaps and owner handoff remain
readiness inputs; completion does not require all Leave planning or a People service.

E5 completion and final step-3 confirmation are recorded. Run installed step-4 final
validation and BMAD implementation readiness on the final scope. Stop for user
review before any bmad-build, migrations, dependency installs or device execution.
