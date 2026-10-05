# E1 work-profile and timezone configuration

**Status:** Configuration design; draft-save gating superseded by ADR-0122  
**Date:** 2026-10-04  
**Owner:** Leave; E1-CONTEXT and first draft writers

Authority: [features §3](../../features.md#3-jurisdictions-and-workplace-calendars),
[Leave ADR-0023](../decisions/0023-employee-work-timezone.md),
[ADR-0086](../decisions/0086-archive-markers-and-effective-dated-versions.md),
[shared employment contract](../../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
and [draft persistence contract](./e1-draft-persistence-and-recovery.md).
This does not change shared location/department ownership or add an HR suite.

## Resolve one authorized source

1. Resolve the caller's current shared employment identity through authorized HTTP.
2. Load Leave-owned settings for exactly `(org_id, employment_id)`.
3. Use an explicit assigned profile if present, otherwise the organization's configured
   default. The default is a fallback, not an assignment silently copied into every employee.
4. Resolve the applicable employee timezone override, if explicitly configured; otherwise
   use the applicable version of that selected profile's timezone.
5. Validate the configured timezone and derive the employment business date from the
   server clock. Ask People for its effective interpretation of that date; verify returned
   identity/date/revision before using it for draft preparation.

Use a named IANA timezone (for example `Africa/Johannesburg`), not a browser locale,
current UTC offset or department/location guess. Null timezone override means inherit;
there is no separate boolean that can contradict it. Explicit assignment/override must
never be silently replaced when organization defaults change. A stale, missing,
cross-organization or archived explicit profile is a setup error, not permission to
fall back to a different profile. A invalid explicit timezone override is likewise not
silently replaced with the profile value. Correct setup through its authorized owner.

For E1, retain the existing safe setup identifiers `work_timezone_missing` and
`work_timezone_invalid`: absent required profile/default/version or timezone produces
missing setup; malformed/inconsistent/cross-scope references or invalid configured
zone produces invalid setup with safe diagnostics. Dependency failure stays unavailable.
Only timezone prerequisites are evaluated here: no claim of complete work-schedule,
holiday, policy or submission readiness. Missing/invalid timezone does not block authorized draft creation/edit/save/reopen under
ADR-0122. It blocks dependent calculations/submission; preserve saved values.

## Minimum owned structure

The following are the minimum logical records, implemented through Leave's own schema
and migration history. Exact effective-version/assignment table layout must be reconciled
before D1/D2 readiness; no temporary parallel timezone master is acceptable.

| Record | Minimum data and ownership rule |
| --- | --- |
| Organization Leave settings | `org_id`, nullable default profile ID, revision and server attribution. Missing row/default is meaningful setup state, not an automatic default. |
| Stable work profile | Organization-scoped UUID, display name, archive timestamp and attribution. Unique `(org_id,id)` supports local composite references. Creating it assigns nobody automatically. |
| Work-profile version | Stable version UUID, organization/profile reference, effective applicability and work timezone, with creation attribution. Retain earlier versions; no overlapping applicable versions. E1 needs no invented schedule hours or holiday calendar fields. |
| Employment Leave settings/assignment history | Organization and external employment ID, nullable explicit profile reference and nullable timezone override, applicability/revision and attribution. One applicable configuration per employment/date or instant as defined by the final effective-boundary contract. No copied person name, employment periods, supervisor, department or location. |

All profile/default references use organization-preserving local constraints. External
employment references are validated through the shared owner, without a cross-owner FK.
Ordinary mutable settings use server-managed created/updated actor/time and revisions;
immutable versions use creation attribution. No generic duplicate history table per
record is prescribed. E2 may add schedule/calendar/version fields only with their
consuming contract; it must reuse these profile identities and settings ownership.

## E1 baseline and effective-boundary gate

E1 controlled provisioning supplies one unambiguous initial applicable configuration
for its synthetic organization/employee profiles. It does not expose scheduled timezone
changes, profile reassignment, override editing or archiving as public E1 actions.
The absence of a settings row can use an explicitly configured organization fallback;
absence of both never implies UTC or the server timezone. An explicit override does
not make a broken selected-profile reference silently valid.

Version selection must not first ask for “today in the employee's timezone” when the
selected version is itself what supplies that timezone. Before implementation, specify
how the initial version/assignment applicability is anchored and read without that
circular dependency. Before E2 future-dated timezone changes, define the timezone used
to interpret the requested effective boundary and preserve the resulting unambiguous
instant/version evidence. Do not silently choose browser time, UTC midnight, or whichever
candidate timezone happens to make its own version applicable. This is a technical
contract gap, not an already-approved new effective-date policy.

Read the configuration chain coherently and retain its source IDs/revisions (organization
settings, assignment/override, selected profile version), resolved timezone and derived
business date as internal preparation evidence. After external People checks and before
a draft write, the existing local guard revalidates that configuration/date. A change
or local midnight requires fresh preparation outside business write locks. The final
schema/locking plan must protect that guard through commit, cover previously absent
settings rows becoming present, and compose with scope → outcome → draft lock order.
A reread alone is not proof of protection against a later concurrent config commit.

E1 tests may inject controlled setup changes to verify these races without exposing
an incomplete administration API. Do not make the shared People response carry Leave's
configuration version or turn its observation into a reusable authorization token.

## Evidence attached to the existing stories

E1-CONTEXT proves explicit profile versus organization fallback, inherited timezone
versus explicit override, missing/invalid setup, wrong-organization references and a
viewer travelling in a different timezone. E1-D1/D2 prove the same resolution through
real create/save guards, changed settings and local-midnight recovery. Fixture setup
has no production fallback and does not manufacture membership/grants/employment.

E2 verifies profile/default/override edits, effective dates, preserve-overrides behavior,
archive blocking for current/scheduled assignments or a default, and historical change
impacts. Shared location changes never silently replace Leave profiles. E3 owns schedule
consumption and balances; E5 snapshots calculation-relevant versions on submission.
None is demonstrated by E1's work-timezone read.

Scaffold: reuse scoped configuration reads, typed safe errors and revision test helpers
only where proven generic; resolution precedence stays in Leave. Shared UI: use the
existing setup/read-only/unavailable states, no E1 configuration screen. Agent context:
existing owner/transaction instructions suffice. Documentation/ADR: link the existing
authorities above, with no accepted ADR amendment. Physical version applicability,
local guard/absence locking, exact provisioning and runnable fixtures remain readiness
inputs. No application code, schema or settings changed.


## Applicability amendment — 2026-10-04

[ADR-0122](../decisions/0122-lightweight-draft-compatibility-and-setup.md) removes complete
work-timezone configuration/version guarding as a prerequisite merely to preserve a
draft. The preceding detailed version/guard plan remains a requirement for consumers
that rely on timezone-dependent results, not an additional E1 save condition. Prefer
source-field validation and simple nonblocking draft setup feedback. E1 retains current
access/ownership and confirmed restrictions; no implicit UTC eligibility is introduced.
