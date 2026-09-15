# ADR-0073: Calm, Practical Visual Direction

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Leave visual and interaction design direction

## Context and decision

The user approved and extended the visual direction with a calm, practical,
low-friction tone; restrained colour; neutral backgrounds; low-contrast decorative
borders; and a single accent reserved for primary actions. Use generous padding
and vertical spacing, avoiding high-density and cluttered views.

Elevate key metrics/balances and primary actions. Mute secondary details and hide
granular explanations inside expandable sections. This does not hide decision-critical
information, required actions, validation errors, or the explicit paid/unpaid
acknowledgement. Preserve the existing WCAG 2.2 AA requirement: subtle decoration
must not make text, functional control boundaries, or keyboard focus imperceptible.
Use clear text and familiar cues for statuses and warnings without colour dependence.

Rely on familiar platform controls and shell primitives rather than custom visual
patterns. Reuse what exists and establish missing shared components through the
repository's prove-then-promote approach. This decision does not claim the planned
shared shell or notification components are already implemented.

Apply [employee home priorities](./0063-employee-home-screen.md),
[submission acknowledgement](./0069-submission-summary-and-unpaid-acknowledgement.md),
and [mobile workflows](./0072-mobile-employee-and-approver-workflows.md).
Follow the platform's [silo boundaries](../../../../../platform/docs/architecture/decisions/0003-application-silo-architecture.md).

## Consequences

- The specification captures palette, spacing, hierarchy, familiar controls, and
  accessible disclosure expectations for subsequent UX documents and verification.
- Detailed layouts, design tokens, and responsive states remain UX design work;
  this direction is not a finished design or a readiness pass.
- Scaffold impact: adopt proven shell/token conventions in templates during delivery.
- Shared-UI impact: generic primitives and tokens belong in shared UI when proven;
  Leave balances, actions, and explanations remain application-specific.
- Agent-context impact: existing accessibility and shared-UI governance suffice.
- Documentation impact: synchronize specification, tracker, ADR index, and memlog;
  carry this direction into the later DESIGN.md and EXPERIENCE.md outputs.
- ADR impact: additive design direction; accepted ADRs remain unchanged.
- Planning only; Phase 1 readiness precedes implementation.
