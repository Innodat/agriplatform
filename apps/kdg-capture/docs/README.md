# KDG Capture planning

Current authorization, 2026-10-14: the user approved beginning bounded shared-platform
implementation with synthetic local/CI verification. This supersedes the historical
planning-only authorization statements below. bmad-help selected ENV before
P1/SERVICE and Identity/Access/WRITE. The first Build increment is
[guarded disposable target preparation](../../../_bmad-output/implementation-artifacts/spec-env-kdg-target-preparation.md),
under the existing deployment owner. Preparation alone does not deliver the enclosing
ENV runtime/bootstrap acceptance, generator or KDG Story 1.1 prerequisites. Production
migrations, access/account changes, infrastructure, deployment and real-data pilot use
remain outside approval. Leave implementation and the questionnaire editor remain out
of scope.

Planning only, 2026-10-12. No application implementation, dependency installation,
migration, access change or deployment is authorized by these files.

This is the first organization-scoped Survey application, owned by the KDG silo.
Survey is a domain, not a new shared runtime service. MVP organization is fixed to
Khula Development Group; there is no organization switcher.

| Authority | Document |
| --- | --- |
| Requirements / focused BMAD PRD | [prd.md](prd.md) |
| Runtime evidence and dependency order | [discovery.md](discovery.md) |
| User-approved shared ownership packet | [shared-platform-handoff.md](shared-platform-handoff.md) |
| Owned WRITE and secret execution | [owner contract](../../../platform/docs/architecture/contracts/owned-write-and-secret-execution.md) |
| Identity/Access execution substrate | [owner contract](../../../platform/docs/architecture/contracts/identity-access-execution-substrate.md) |
| Minimum shared-owner prerequisite work | [shared-prerequisites.md](shared-prerequisites.md) |
| ENV/scaffold selection and exact versions | [owner contract](../../../platform/docs/architecture/contracts/scaffold-environment-and-generation.md), [dependency baseline](../../../platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md) |
| Fresh-session resume prompt | [next-session.md](next-session.md) |
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
The sole owner explicitly acknowledged the handoff as all owners on 2026-10-14.
Shared planning contracts may be reconciled; code remains unauthorized.

BMAD route: focused existing-project discovery → PRD → UX → architecture →
epics/stories → bmad-sprint-planning readiness → user review → bmad-build/ATDD.
Brainstorming, market research and a separate product brief are unnecessary for the
agreed internal scope. Required epic confirmation menus remain part of the installed
workflow. Use fresh BMAD contexts when resuming, with this index as the input.

Current amendment, 2026-10-13: explicit observation Save only; unfinished typing is
not automatically persisted/recovered. Saved captures remain local and queue for sync.
[Story 1.5](epics.md#story-15-explicitly-save-an-observation-on-this-phone) is planning-approved;
earlier recovery proposals are withdrawn. Questionnaire draft/published versions remain.

Current BMAD checkpoint: all five epics and 19 stories are user-approved.
[Final planning validation](final-planning-validation.md) confirms coverage/dependency
checks; [implementation readiness](implementation-readiness.md) now PASS after shared/execution
planning closure. Stop for plan review; no implementation is authorized.

User approved shared-platform-handoff.md on 2026-10-14 and acknowledged all owners
in the successor session. The shared readiness addendum fixes the selected KDG scope/
target/operator baseline, with fingerprint lifecycle in its owning security contract.
All bounded shared execution choices are recorded; actual delivery/adoption/runtime
evidence and pre-pilot policies remain separate gates.
[next-session.md](next-session.md) preserves planning-only scope and settled choices.
