# E1 planning closure — approved

2026-10-13. All seven story scopes and E1 planning closure are user-approved. No story has
been implemented, tested on phones or declared Build-ready. E1 is the first usable
create/read vertical slice, not the complete KDG MVP.

| Story | Planning scope |
| --- | --- |
| 1.1 | Sign-in/current fixed Khula entry |
| 1.2 | Initial immutable questionnaire setup/read |
| 1.3 | Initial child/assignment setup/current eligible-child reads |
| 1.4 | Installed shell/current authorized offline setup |
| 1.5 | Explicit local capture/queue/read/reopen; no unfinished-entry recovery |
| 1.6 | Current-authorized idempotent server create/receipt/read/foreground sync |
| 1.7 | Full installed Android/iPhone first-slice proof and evidence |

## Requirement allocation

| Requirement | E1 coverage | Explicit later completion |
| --- | --- | --- |
| FR-1 | 1.1/1.4/1.6 current entry/authorization and fixed organization | Current checks continue on every new surface |
| FR-2 | 1.1/1.3/1.5/1.6 role/create scope, own author/read and backend negatives | E2 own edits; E3 all-record administrator read/edit |
| FR-3 | 1.2/1.3 initial controlled setup with existing shared owners | Normal management/onboarding E5 |
| FR-4 | 1.4/1.5/1.7 phone identity/install/form/child choice | Later responsive admin surfaces |
| FR-5 | 1.2/1.5 exact initial labels/defaults/answers/details and validation | New editable types/definitions E4 |
| FR-6 | 1.5 editable phone-default date, repeat same-day captures, locally known read/add | E2 Edit existing with actual existing-record editing |
| FR-7 | Revised 1.5 explicit local Save/atomic acknowledgement/failure guidance | No unfinished-input recovery requirement; editing uses E2 Save/Cancel |
| FR-8 | 1.5 local saved details/reopen; 1.6 server-backed own read | E2 downloaded observation history/edit; internal revision evidence; E3 organization history |
| FR-11 | 1.2 immutable seed; 1.4/1.5 pinned definition; 1.6 old published acceptance | E4 live publication/new-version/historical-edit compatibility |
| FR-13 | 1.4 setup and 1.5 saved local capture persistence/isolation | E2 30-day history, E3 all-permitted history |
| FR-14 | 1.5 durable create intent; 1.6 create sync/retries | E2 ordered edit delivery and full edit conflicts |
| FR-15 | 1.5/1.6 local/pending/synced/attention truth | Same pattern on later edits/admin actions |
| FR-16/17 | 1.4 local window/session/partition plus 1.6 current server scope | Changed assignments/normal onboarding E5; no fake immediate offline revocation |
| FR-18 | 1.4/1.5/1.7 quota/schema/update baseline and pending-create retention | E5 full pilot reliability/retention/recovery evidence |

NFR-1 isolation, NFR-2 durability, NFR-3 accessibility and NFR-4 bounded action behavior
bind their introduced story surfaces. NFR-5 physical first-slice proof is approved Story 1.7;
release compatibility remains required for each schema/queue change. UX-DR1–7 and
12–14 are addressed in E1 to its explicit-Save/create scope; UX-DR8 has basic read
here and full E2/E3 history; UX-DR9 is E2/E3 conflicts; UX-DR10 is E4/E5 admin;
UX-DR11 has baseline storage/update handling here and full E5 reliability.

## Outstanding gates

Existing shared owner handoff, current Identity/Access KDG schemas/target verification,
trusted setup/scaffold/toolchain, concrete wire/fingerprint/privacy/retention and
environment/device targets still need their named readiness closure. Do not require
finished application code to plan a story, or claim a planned dependency is operational.

Final 1.7 and E1 planning closure are approved; sequential E2 detailing now proceeds. Full BMAD
final validation and implementation-readiness are still required after story planning;
implementation/physical execution remain outside this planning session's authorization.
