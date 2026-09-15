---
name: Agriplatform
description: Shared visual conventions under development, first exercised through Leave.
status: draft
created: 2026-09-15
updated: 2026-09-15
sources:
  - docs/architecture/decisions/README.md
---

## Brand & Style

This draft records shared visual conventions, not an implemented component library
or finalized theme. Application design documents reference shared conventions and
describe their own visual differences. Only proven, domain-neutral implementations
are promoted to shared UI under existing repository governance.

## Layout & Spacing

Focused create/edit tasks may use a right-side drawer when preserving the
underlying page's context is useful. Give the task sufficient room; switch to a
full-page presentation when the viewport cannot comfortably contain it. The exact
widths, padding, breakpoints, and tokens remain to be validated with the Leave form.

## Components

### Task drawer

Use a right-side drawer as the preferred contextual create/edit presentation,
subject to the exceptions and interaction rules in [EXPERIENCE.md](./EXPERIENCE.md).
Define shared width variants, spacing, backdrop, borders, and responsive treatment
after evaluating the real form content. No numerical values or implemented shared
drawer are claimed by this draft.

## Do's and Don'ts

- Give form content room to remain readable and usable.
- Keep required information in the active surface; background content is context.
- Do not force long, complex, or multi-step workflows into drawers.
- Do not assume a framework's defaults satisfy the final accessibility contract;
  verify the assembled component when implemented.
