# E1 draft choice resolution

**Status:** Endpoint and resolution design; owner schema and executable validation pending  
**Date:** 2026-10-05  
**Owners:** Leave E1-CHOICES and E1-D2

Authority: [features §4/7](../../features.md), [ADR-0122](../decisions/0122-lightweight-draft-compatibility-and-setup.md),
[platform ADR-0049](../../../../../platform/docs/architecture/decisions/0049-lightweight-draft-preservation-and-compatibility.md)
and [draft input contract](./e1-draft-persistence-and-recovery.md).
This is minimum form metadata, not an eligibility/calculation or policy administration API.

## One read for choices and the existing selection

Propose `GET /api/v1/organizations/{org_id}/draft-choices`, requiring current own-read
authority and verified organization context. Optional `selected_type_id` is a UUID or
omitted; optional opaque `cursor` represents list position. Reject unknown parameters
and malformed values. There is no account/person override, client-selected authorization
or browser table access. Response is private/no-store:

- `choices`: at most 100 items, ordered by stable type UUID. Each has `type_id` and `version_id` UUIDs,
  `name` display text, positive decimal-string `revision`, and `permitted_modes`, a
  nonempty unique subset of `full_days`, `half_day`, `hours`.
- `next_cursor`: opaque next-page position or null; no truncated-success claim.
- `selected`: `{status: not_requested}` when omitted; `{status: available, choice}`
  for a currently offered scoped type; `{status: obsolete}` when authoritative scoped
  resolution confirms that ID is no longer a usable choice. The available choice has
  the same schema as list items even if it is outside this page.

The selected lookup runs independently of list pagination in the same local read
snapshot. `obsolete` provides no foreign-organization name, reason distinguishing a
foreign ID from a missing one, or historical details. Authorization failure is an error
before lookup. A response/read/schema failure yields unavailable handling, not an
obsolete result. An empty list is not enough to clear a selection without its explicit
selected result. If configured metadata is inconsistent (for example, no recognized
permitted mode), fail safely as unavailable rather than clearing input or inventing
Full days. Display names are plain text, never markup.

For E1, “available” means offered for unfinished draft entry: an owned nonarchived type
with structurally valid configured modes. It does not establish request-date eligibility,
entitlement or submission readiness. Future-dated leave is possible, so do not clear a
type simply because today's date is outside its eventual policy applicability. E3 adds
request-date policy guidance/validation through its own versioned contract. E1's exact
minimal type/version schema must identify which published choice revision supplies name
and modes; do not guess an effective policy or expose draft administration edits.

## Simple client behavior

On reopening or refreshing an existing form, resolve its selected ID explicitly. If
available, preserve it and validate only whether its selected duration mode remains an
offered mode. If definitively obsolete, clear the type selection and its selected mode,
retain independent dates, notes and inactive-mode input, and show “Please choose a leave
type again.” If only the mode is no longer permitted, clear that selection and show
“Please choose a duration again.” Do not choose a replacement, convert hours to days
or reapply the initial new-request Full days default during repair. The next explicit
choice uses ordinary permitted-mode selection; a repair is not a new request.

Clearing is an ordinary local input change and uses D2's serialized, revision-guarded
autosave when editable. GET never updates stored input. In read-only mode, explain that
the selected option is unavailable without starting a save or altering the stored draft.
Mark Saved only for input acknowledged by persistence. Preserve useful independent
input on retry/conflict and apply simple platform failure navigation. A failed lookup
keeps the original values and offers retry; there is no special technical recovery dialog.

Do not apply a delayed selected-result to a newer local choice: bind each response to
its requested organization, account, selected ID and current form request generation.
Ignore stale results after user input, account/org switch or newer refresh. Choice
configuration may change after this read; a draft save still preserves structurally
safe input under current authority. Do not add a choice-service lookup/lock to every
keystroke save. Refresh may clear a newly obsolete choice later; submission revalidates.
Cross-organization IDs never grant access or disclose labels; they are not dereferenced
as authority during preservation.

## Fixtures and delivery impacts

Verify selected type outside the first page, available and retired/missing/foreign IDs,
empty configuration, changed permitted modes, malformed metadata, outage, delayed reply
after a different choice, and read-only reopening. Test revision-safe clearing through
actual save/reopen, unchanged independent dates/notes, preserved input during lookup
failure and no automatic default refill. New configured types initially permit all
three modes; managers may restrict them. Arbitrary day fractions remain excluded.

Link E1-AC-03/04/05/07/13/15/16/17 and existing choice/default requirement coverage.
Generate/validate OpenAPI and TypeScript types from the owning API when implemented.
Scaffold/shared UI: promote proven safe selector/reset/error handling only; Leave owns
obsolescence and units. Agent guidance and accepted ADRs unchanged. Remaining readiness:
actual schema/role/command validation and API/browser fixtures. The following section
now specifies the minimum type/version structure, metadata bounds and cursor contents. No new shared service, code, data
clearing or migration was performed by this contract.

## Minimum owned type/version schema — 2026-10-05

Use the existing Leave owner/migration history and two records. This is a concrete E1
baseline under ADR-0002/0086, not a second type catalogue or complete policy schema.

| Record | Minimum columns | Constraints and interpretation |
| --- | --- | --- |
| `leave.leave_type` | `id uuid`, `org_id uuid`, stable `code text`, nullable `archived_at timestamptz`, nullable `choice_version_id uuid`, positive `revision bigint`, server-managed created/updated actor UUIDs and UTC timestamps | PK id; unique `(org_id,id)` and `(org_id,code)`. Code uniqueness is retained after archive; never repurpose an old ID/code to mean another type. Explicit pointer identifies the published metadata used for draft choices. |
| `leave.leave_type_version` | `id uuid`, `org_id uuid`, `leave_type_id uuid`, positive `version_number bigint`, `name text`, `permitted_modes text[]`, `effective_from date`, nullable inclusive `effective_to date`, nullable `published_at timestamptz`, creation actor/time | PK id; scoped FK to type; unique `(org_id,leave_type_id,id)` and `(org_id,leave_type_id,version_number)`. End null or >= start; bounded name; nonempty duplicate-free subset of full_days/half_day/hours. Published domain fields are immutable; changing them creates a version. |

The type pointer has a composite FK `(org_id,id,choice_version_id)` referencing the
version's `(org_id,leave_type_id,id)`, preventing wrong-type or cross-organization
selection. Null pointer means no published choice is configured, not an automatic
version selection. The owner provisioning command creates the type, creates/publishes
its version and assigns the pointer in one local transaction with required attribution/
operation evidence. An owner-enforced integrity check requires a selected choice version
to be published; API reads fail safely if inconsistent storage is encountered. Runtime
read credentials cannot publish, change the pointer or grant themselves write access.

For E1, provisioning creates one published initial version per example type. Draft-choice
reads join only the explicit pointer; they never use MAX(version_number), server/browser
“today”, or expose unpublished edits. This pointer identifies offered form metadata,
not the policy that governs requested leave dates. The endpoint's `revision` is the
stable type's revision, advanced atomically when pointer/availability changes. Return
`choice_version_id` as `version_id` in each choice to make the source explicit; a draft
still saves stable `type_id`, not a binding to a submission policy snapshot.

E1 does not implement future scheduled policy publication or overlapping competing
published effective versions. Before E3 adds those, its date-aware policy contract
must define how offered units relate to all applicable request dates and how choice
metadata is refreshed. A current-date selection must not invalidate a valid future-date
choice. Calculation/submission use explicit effective policy versions and snapshots,
never the draft-choice pointer alone. These are existing E3 gates, not work required
merely to render and preserve the E1 form.

### Metadata bounds and availability

Define codes as 1–64 lowercase ASCII letters/digits/underscores, starting with a letter;
normalize only during explicit provisioning before uniqueness checks. Names are 1–120
Unicode code points after outer whitespace trimming at configuration entry, with no
U+0000, invalid Unicode or control characters. Store/display plain text. API identifiers
are UUID strings; revisions are positive bigint decimal strings. Provision examples
with scoped codes `annual`, `sick`, `family_responsibility`, and all three modes initially
allowed. No entitlement amounts, legal compliance claim, approval route or paid/unpaid
assumption is seeded merely to make this form work.

Archive marks the stable type and preserves all versions; it makes the type obsolete
for this draft selector under ADR-0122. Missing/foreign IDs yield the same safe obsolete
result. A nonarchived type whose pointer is null is unconfigured and not offered; a
previously selected such type may be reset only after this definitive authorized lookup.
An invalid non-null pointer, unpublished pointed version or malformed mode/name metadata
is configuration inconsistency: return unavailable, not a destructive obsolete inference.
Used types/versions cannot be hard-deleted through generated CRUD. No automatic whole-
draft cleanup, restoration UI or copying of policy content into draft rows is introduced.

### Pagination and provisioning evidence

Encode the opaque HTTP cursor as a versioned position containing exactly the requested
organization and last returned type UUID. Validate encoding, version and organization
match; reject malformed/unknown fields. Cursor contains no authority or credentials;
current access and filtering are reevaluated each request. It need not be signed because
altering position cannot expand authorized results. Fix E1 page size at 100 and query
101 eligible rows to determine next_cursor; selected lookup remains independent. No
hidden arbitrary account parameter, offsets over foreign data or server-side cursor store.

E1 controlled setup uses the owner writer, separated from read runtime and migrations.
Record creation/publication/archival evidence when such fixture commands are exercised;
no public administrative mutation route is added. Fixtures prove stable code/ID and
scope constraints, pointer publication integrity, immutable published values, no leaked
unpublished rows, archival without deletion, selected lookup beyond page one, and the
three default modes versus explicitly restricted subsets. Existing D2 fixtures prove
only normal guarded persistence of any resulting selection reset.

Scaffold impact stays generic (scoped reference, published-version fixture, typed client);
Leave owns codes, modes and choice semantics. No new UI, agent policy or ADR required.
Exact migration/role/trigger implementation, failure mapping, command/evidence shape and
executable contract tests remain readiness work. No tables or fixture data were created.
