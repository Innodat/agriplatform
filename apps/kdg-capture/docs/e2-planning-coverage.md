# E2 planning closure — approved

2026-10-14. All four stories and E2 planning closure are user-approved with C. This checks planned coverage, not runtime
behavior or implementation readiness. No code or physical-device tests have run.

| Story | Approved scope |
| --- | --- |
| 2.1 | Own 30-day downloaded history, older online reads, partial-cache truth and safe refresh |
| 2.2 | Original-questionnaire own Save/Cancel edits, durable ordered queue, conditional server writes and internal provenance |
| 2.3 | Explicit review/use-current/replacement of own saved conflicts; repeat conflicts and paused dependent edits |
| 2.4 | Simple observation date/answers/status, minimal local storage and integrated automated/installed Android/iPhone proof |

## Requirement coverage

| Requirement | E2 allocation | Later completion |
| --- | --- | --- |
| FR-2 | 2.1/2.2 own-read/edit, ownership/current capability checks | E3 administrator all-record access/audit |
| FR-6 | 2.2 working Edit existing/Add another; editable observation date | Multiplicity remains E1; no global offline duplicate promise |
| FR-8 | 2.1 history; 2.2 edits; 2.4 simple details and proof | E3 authorized organization history |
| FR-9 | 2.2 revision detection; 2.3 explicit local/server resolution | E3 facilitator/admin concurrency and role boundaries |
| FR-11 | 2.1–2.4 exact original definitions for historical reads/edits | E4 actual editing/publication and old/new-version compatibility |
| FR-13/14 | 2.1 cached records; 2.2 ordered durable edit intents; 2.3 conflict state | E3 all-authorized cache; later patterns reuse these foundations |
| FR-15 | 2.1–2.4 truthful local/pending/synced/attention and partial history | Same states apply on administrator surfaces |
| FR-16/17 | Exact own read/edit observations, current server checks, account isolation, unassignment/inactive-child historical rights | E3 role loss; E5 normal assignment/onboarding management |
| FR-18 | Safe refresh, local schema/queue compatibility and pending/conflict retention | E5 declared pilot retention and full reliability closure |

NFR-1 authorization/privacy, NFR-2 durability/concurrency, NFR-3 accessibility,
NFR-4 bounded foreground operation and NFR-5 release/device evidence bind each affected
story. UX-DR4/5/7/8/9/11–14 are allocated to the history/edit/conflict/proof surfaces;
UX-DR10 administrator management remains E4/E5.

## Simplicity and platform boundaries

History means observations, not an audit/version catalogue. Routine capturer views show
observation date/answers and compact status; server attribution/evidence remain internal
for authorized administrator audit. Questionnaire definitions remain immutable and pinned
internally. No revision-download API, local archive, restore tool or unfinished-form store.
Retain only current observations, necessary definitions, pending commands/bases/conflicts.

The editor/device holding a conflicting proposal resolves it under existing own/all
rights. First access grants no priority; central intake of never-synchronized proposals
is outside MVP. Conditional writes protect simultaneous resolution attempts.

Existing platform owners provide proven domain-neutral persistence/migrations,
partitions, queue/retry/idempotency, conditional revision/conflict, status/PWA updates
and test utilities. KDG keeps questions, children, assignments, answers and authorized
API semantics. No generic offline runtime service, history engine or duplicate generator.
Shared changes require the pending Leave handoff.

## Gates and next step

Concrete wire/queue/local-schema/retention fixtures and shared owner/runtime prerequisites
remain Build gates; planned acceptance/device scenarios have not run. E2 depends only
on E1 and its shared prerequisites, not the administrator/editor/assignment portal.
Epic-completion confirmation is recorded; sequential E3 detailing now proceeds. Full BMAD final
validation/readiness and user implementation approval remain required afterward.
