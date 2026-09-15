# ADR-0010: BMAD as the Delivery Workflow

**Status:** Accepted  
**Date:** 2026-09-04  
**Scope:** AI-assisted platform and application delivery

**Supersedes:** [ADR-0008](./0008-selective-structured-prompt-driven-development.md)

## Context

The repository began developing a custom SPDD workflow under `platform/prompts`.
BMAD is now installed and provides maintained planning, architecture, story,
implementation, review, project-context, and help workflows across coding agents.
Continuing to build a parallel generic workflow would make the team maintain a
development methodology in addition to the application platform.

The repository already has valuable product specifications, ADRs, ATDD/TDD rules,
scaffold governance, and application architecture. Those are project truth and
engineering policy rather than replaceable agent workflows.

## Decision

Use BMAD as the sole generic delivery workflow. Preserve repository-owned feature
specifications, ADRs, ATDD/TDD policy, test evidence, implementation tracking,
scaffold evolution, and shared-UI promotion rules as authoritative inputs and gates.

Use three proportional paths:

1. **Direct engineering** for obvious, low-risk mechanical work; test behavior when
   behavior changes.
2. **BMAD Build** (`bmad-build`) for bounded, well-understood features, defects, and
   refactors. In the installed catalog this is the standard clarify, plan, implement,
   review, and present flow.
3. **Full BMAD planning and delivery** for new applications, shared services,
   identity/tenancy, migrations, and high-risk domain capabilities: PRD validation,
   optional UX, architecture, epics/stories, sprint readiness, then story-sized Build.

At the beginning and end of every implementation phase, run `bmad-help` in a fresh
context to inspect actual artifacts and recommend the next installed skill. Do not
rely on remembered command names when the installed catalog is authoritative.

`platform/prompts` will be reduced to Agriplatform-specific context, norms,
safeguards, and concise technology patterns consumed by BMAD and other agents. It
will no longer define a competing generic SPDD lifecycle.

BMAD customization must preserve these non-negotiable gates:

- ATDD outer loop and focused TDD inner loop
- Characterization tests before risky refactors of unprotected behavior
- Tenant-isolation, authorization, contract, migration, and idempotency evidence
- Scaffold, shared-UI, agent-context, documentation, and ADR impact decisions
- Human-reviewed changes to accepted product or architecture decisions

## Alternatives considered

- Continue the custom SPDD framework
- Layer full BMAD on top of full SPDD
- Adopt Spec Kit or OpenSpec alongside BMAD
- Replace repository specifications and ADRs with generated BMAD artifacts

## Consequences

- Generic workflow maintenance is delegated to BMAD.
- Existing planning work seeds BMAD validation and decomposition; it is not discarded.
- BMAD skills require project-specific customization for ATDD/TDD and scaffold gates.
- OpenSpec and Spec Kit remain deferred until measured workflow pain justifies them.
- Historical SPDD ADR and changelog entries remain visible but are no longer current policy.
- The installed BMAD catalog/configuration is checked before recommending next steps.

## Revisit when

A two-epic pilot shows BMAD creates more drift, token usage, or process overhead than
the prior approach, or a different maintained workflow demonstrably fits the
repository better.

