# KDG Capture planning

Planning only, 2026-10-12. No application implementation, dependency installation,
migration, access change or deployment is authorized by these files.

This is the first organization-scoped Survey application, owned by the KDG silo.
Survey is a domain, not a new shared runtime service. MVP organization is fixed to
Khula Development Group; there is no organization switcher.

| Authority | Document |
| --- | --- |
| Requirements / focused BMAD PRD | [prd.md](prd.md) |
| Runtime evidence and shared dependency handoff | [discovery.md](discovery.md) |
| Application decisions | [ADR index](architecture/decisions/README.md) |
| Visual contract | [DESIGN.md](DESIGN.md) |
| Interaction contract | [EXPERIENCE.md](EXPERIENCE.md) |
| BMAD architecture spine | [ARCHITECTURE-SPINE.md](ARCHITECTURE-SPINE.md) |
| Proposed application API/persistence/sync contract | [contracts.md](contracts.md) |
| Requirement → story → test evidence | [testing.md](testing.md) |
| Shared/scaffold/UI/context/documentation/ADR impacts | [delivery-impact.md](delivery-impact.md) |
| BMAD extraction and delivery sequence | [epics.md](epics.md) |
| Readiness and outstanding decisions | [implementation-readiness.md](implementation-readiness.md) |
| Independent reviews | [review-resolution.md](review-resolution.md), [validation-report.md](validation-report.md) |
| Decision audit | [.memlog.md](.memlog.md), written through BMAD memlog.py |

Documents are draft proposals unless they explicitly identify an agreed user choice
or inherited accepted ADR. Drafting completion is not implementation approval or a
claim that runtime tests passed. No parallel requirements copies are maintained in
the global BMAD folders: those already contain Leave work.

The KDG session is the user-appointed shared-platform coordinator. Existing
Identity/Access, scaffold/environment and release owners retain their components.
Leave handoff agreement remains required before modifying shared contracts or code.

BMAD route: focused existing-project discovery → PRD → UX → architecture →
epics/stories → bmad-sprint-planning readiness → user review → bmad-build/ATDD.
Brainstorming, market research and a separate product brief are unnecessary for the
agreed internal scope. Required epic confirmation menus remain part of the installed
workflow. Use fresh BMAD contexts when resuming, with this index as the input.

Current amendment, 2026-10-13: explicit observation Save only; unfinished typing is
not automatically persisted/recovered. Saved captures remain local and queue for sync.
[Story 1.5](epics.md#story-15-explicitly-save-an-observation-on-this-phone) is planning-approved;
earlier recovery proposals are withdrawn. Questionnaire draft/published versions remain.

Current BMAD checkpoint: E1 planning is user-approved (seven stories); E2 planning is closed (four stories); current review is
[questionnaire draft editor candidate 4.1](story-candidates/4-1-questionnaire-editor.md). Implementation readiness
and runtime/physical proof remain pending.
