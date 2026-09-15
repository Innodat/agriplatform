# Platform Agent Context (SPDD Prototype Under Transition)

> **Current direction (2026-09-04):** BMAD is the generic delivery workflow under
> [ADR-0010](../docs/architecture/decisions/0010-bmad-as-delivery-workflow.md).
> The SPDD material below is retained as useful history and candidate Agriplatform-
> specific context until the Phase 1 alignment task removes duplicated workflow.

`platform/prompts` currently contains the repository's earlier Structured
Prompt-Driven Development (SPDD) prototype. Its long-term role is portable,
Agriplatform-specific norms, safeguards, and focused context consumed by BMAD and
other coding tools—not a second generic delivery methodology.

The governing decision is
[ADR-0008](../docs/architecture/decisions/0008-selective-structured-prompt-driven-development.md).
The mandatory acceptance and implementation feedback loops are defined by
[ADR-0009](../docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).

## Artifact hierarchy

```text
Feature specification  → user intent and acceptance
ADR                    → accepted architecture and consequences
SPDD canvas/task prompt → executable implementation contract
Tests/contracts         → executable evidence
Code                    → implementation
```

Prompts link to the source feature specification and ADRs instead of copying large
sections. When implementation exposes a wrong assumption, update the owning artifact
first, then synchronize downstream artifacts. Never reverse-sync code into an
accepted product or architecture decision without human review.

## Choose the workflow

Use a full SPDD analysis and implementation canvas for:

- End-to-end features
- New applications or shared services
- Database/schema/data migrations
- Authentication, authorization, tenancy, privacy, or security changes
- Cross-application contracts
- Complex refactors or changes with meaningful rollback concerns

Use a lightweight task prompt for:

- Localized, reproducible bug fixes
- Documentation-only changes
- Mechanical formatting or generated refreshes
- Small dependency maintenance
- Narrow refactors with no public contract or architecture change

Escalate a lightweight task to a full canvas when investigation discovers broader
risk or design choices.

## Substantial-change workflow

1. Link the approved feature specification, relevant ADRs, and implementation-plan item.
2. Analyze the affected domain and current code; record assumptions and unknowns.
3. Define the implementation contract: rationale, expected outcomes, approach,
   structures/contracts, ordered operations, norms, and safeguards.
4. Refine acceptance examples, automate the first scenario, and confirm it fails for
   the expected missing behavior.
5. Review the contract before production implementation.
6. Implement in small red-green-refactor slices, updating generated contracts.
7. Run affected acceptance, contract, authorization, and integration suites.
8. Perform scaffold, shared-UI, prompt, documentation, migration, and ADR impact reviews.
9. Synchronize approved implementation facts back into the prompt and owning docs.
10. Record test commands/results and update `CHANGELOG.md`.

## Prompt impact review

Every substantial feature asks:

- Did this work prove a reusable engineering norm or safeguard?
- Did a task strategy or context snippet become incorrect or incomplete?
- Did repository layout, ownership, commands, dependencies, or generated paths change?
- Should the registry route a new task type or context source?
- Do app-local prompt packs or builder templates need the same update?
- Did an acceptance example, regression, or characterization test reveal a reusable safeguard?

If yes, update the prompt artifact, registry, validation/tests, version, changelog,
and generated/app-local copies in the same delivery item. If no, record
`No prompt change — no reusable delivery guidance affected` in completion notes.

## Current components

- `base.md`: minimal rules that truly apply to almost every implementation task
- `registry.md`: task-to-strategy and context routing
- `tasks/`: focused task strategies
- `context/`: small, authoritative context snippets
- `CHANGELOG.md`: applied prompt-system changes, not a backlog of recommendations

## Alignment work required before Leave implementation

The current files are a useful prototype but are not yet authoritative for the new
Leave implementation. Phase 1 must reconcile at least:

- Current `apps/<app>/{backend,web,supabase,docs}` silo paths
- `services/` ownership and service templates
- App-local versus platform-generated schemas and clients
- Provider-neutral identity context and multi-NGO switching
- Current error contract, avoiding `any`
- Content Service and notification/outbox client patterns
- Continuous scaffold and shared-shadcn promotion rules
- Generator/test commands that exist and run in this repository
- Removal of stale Receipt/Bible-specific assumptions from generic guidance

Do not enforce arbitrary prompt length limits when they remove necessary safeguards.
Prefer concise routing and focused context, but validate usefulness and correctness
before line count.
