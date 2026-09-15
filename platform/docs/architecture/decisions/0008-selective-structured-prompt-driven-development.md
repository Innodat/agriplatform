# ADR-0008: Selective Structured Prompt-Driven Development

**Status:** Superseded by [ADR-0010](./0010-bmad-as-delivery-workflow.md)  
**Date:** 2026-09-01  
**Scope:** AI-assisted platform and application delivery

## Context

The repository already contains a lightweight, versioned prompt system under
`platform/prompts`, while product specifications and ADRs record product intent and
architecture. AI-assisted delivery benefits from explicit implementation contracts,
safeguards, ordered operations, and design-to-code traceability. Requiring a large
prompt canvas for every small change, however, would add process without comparable
value and duplicate existing source documents.

## Decision

Adopt Structured Prompt-Driven Development (SPDD) selectively for substantial
features, services, schema/data migrations, security-sensitive changes, and complex
refactors. Use a lightweight task prompt for localized bug fixes, documentation,
dependency updates, and mechanical changes unless their risk warrants a full canvas.

`platform/prompts` is the repository-owned implementation of the approach. OpenSPDD
is a methodological and tooling reference, not a runtime or mandatory CLI dependency.
The repository may later pin and automate the CLI only after a pilot demonstrates
that it fits the existing workflow without creating duplicate artifacts.

The artifact hierarchy is:

1. Product feature specifications define user-visible intent and acceptance.
2. ADRs define accepted architectural decisions and consequences.
3. SPDD analysis/canvases define the executable contract for an implementation slice.
4. Tests and generated contracts provide executable evidence.
5. Code implements the approved contract.

Prompts link to specifications and ADRs; they do not copy them wholesale. When
implementation reality exposes a missing or invalid assumption, update the owning
artifact first and then synchronize prompt, tests, code, scaffold, and documentation.
Synchronization is human-reviewed and must not silently rewrite accepted ADRs or
product decisions from code.

Every substantial delivery item includes a **prompt impact review**, analogous to
the scaffold impact review. A reusable norm, safeguard, workflow, or context snippet
must update `platform/prompts`, its validation/tests, registry, version/changelog,
and relevant generated app-local prompt packs in the same delivery item.

## Alternatives considered

- Use ad-hoc conversational prompts only
- Adopt the OpenSPDD CLI and templates unchanged for every task
- Treat implementation plans as sufficient executable prompts
- Maintain prompts centrally but update them only after a release

## Consequences

- Important implementation intent becomes reviewable, versioned, and reusable.
- Feature specs, ADRs, canvases, tests, and code have explicit ownership rather than
  competing as duplicate sources of truth.
- Prompt maintenance becomes part of feature completion and phase exit gates.
- The current prompt pack requires an alignment pass before acting as authoritative
  guidance for the Leave implementation.
- Teams must choose and record the full or lightweight path at task intake.
- Reverse synchronization remains deliberate; accidental code drift is not promoted
  into policy automatically.

## Pilot and success criteria

Pilot the approach on the Leave Phase 1 scaffold vertical slice and the FastAPI
Content Service. Continue or expand automation when the pilot shows:

- Fewer implementation corrections caused by missed constraints
- Traceable links from delivery work to feature requirements and ADRs
- Prompt/scaffold changes delivered with the feature that proves them
- Acceptable authoring and review overhead
- Successful use by more than one coding tool or contributor where applicable

## Revisit when

The pilot shows unacceptable duplication or overhead, the repository adopts a
different governed spec system, or OpenSPDD CLI integration provides measurable
validation/synchronization value beyond the repository-owned workflow.
