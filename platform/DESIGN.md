---
name: Agriplatform
description: Shared visual conventions under development, first exercised through Leave.
status: draft
created: 2026-09-15
updated: 2026-09-20
colors:
  page: '#F5F5F5'
  surface: '#FFFFFF'
  text: '#292929'
  text-secondary: '#626262'
  border-subtle: '#DEDEDE'
  border-control: '#858585'
  primary: '#17685C'
  on-primary: '#FFFFFF'
  focus: '#294E47'
  emphasis: '#E8F0ED'
typography:
  body:
    fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: '1rem'
    lineHeight: '1.5'
  input:
    fontSize: '1rem'
    lineHeight: '1.5'
  label:
    fontSize: '0.875rem'
    lineHeight: '1.5'
  secondary:
    fontSize: '0.875rem'
    lineHeight: '1.5'
  heading:
    fontSize: '1.5rem'
    lineHeight: '1.3'
  balance:
    fontSize: '2rem'
    lineHeight: '1.25'
rounded:
  sm: '4px'
  md: '6px'
  lg: '8px'
spacing:
  form-section: '24px'
  label-gap: '8px'
  task-padding-desktop: '32px'
  task-padding-mobile: '20px'
  form-padding-vertical: '24px'
components:
  task-drawer:
    width: '560px'
    borderWidth: '1px'
    borderColor: '{colors.border-subtle}'
    backdropColor: '#00000006'
    boxShadow: '-6px 0 20px #00000006'
  form-control:
    borderRadius: '{rounded.md}'
    borderWidth: '1px'
    borderColor: '{colors.border-control}'
    minHeightDesktop: '2.75rem'
    minHeightMobile: '3rem'
  card:
    borderRadius: '{rounded.lg}'
    borderWidth: '1px'
    borderColor: '{colors.border-subtle}'
  small-dialog:
    borderRadius: '{rounded.lg}'
  status-marker:
    borderRadius: '{rounded.sm}'
  icon:
    family: 'Lucide'
sources:
  - docs/architecture/decisions/README.md
---

## Brand & Style

This draft records shared visual conventions, not an implemented component library
or finalized theme. Application design documents reference shared conventions and
describe their own visual differences. Only proven, domain-neutral implementations
are promoted to shared UI under existing repository governance.

## Colors

Selected light-mode palette: **Neutral + Quiet lagoon**, chosen through Leave.
The initial shared theme delivered for Leave MVP is light mode only. Keep colours
in semantic tokens so dark mode can be designed and verified later; do not expose
a dark-theme switch or infer a dark palette from automatic inversion. This scope
does not disable browser accessibility features or dictate existing apps’ themes.
Use the neutral page, white surfaces and charcoal text from the shared tokens.
Deep teal is reserved for primary actions. Subtle lagoon-tinted emphasis supports
selected controls and informational highlights, accompanied by clear labels and
borders; it does not imply success or an error. Status labels remain neutral.

The selected palette’s measured white-on-primary contrast is 6.62:1; secondary
text on white is 6.10:1 and on emphasis is 5.26:1. These numerical pairs do not
establish full accessibility compliance. Dark mode is deferred for this MVP;
additional interactive states still need verification. Do not invent their tokens
from unrelated prototypes.

## Typography

The user selected the larger typography study: system fonts, 16px-equivalent body,
inputs and action text; 14px labels/secondary text; 24px headings and 32px balance
figures at the normal browser base. Use relative units so preferences can enlarge
text. Form controls target minimum 44px desktop and 48px mobile height, growing
where wrapping or enlarged text requires it. Preserve normal one-line action labels
without squeezing buttons; do not impose a fixed height that clips enlarged text.

The selected study supplies the line-height values above. This scale is an approved
design choice, not a claim that the sizes alone establish accessibility compliance.
Validate actual controls, zoom, translation expansion and responsive reflow.

## Layout & Spacing

Focused create/edit tasks may use a right-side drawer when preserving the
underlying page's context is useful. Give the task sufficient room; switch to a
full-page presentation when the viewport cannot comfortably contain it. The user
selected a standard 560px drawer, 32px desktop horizontal padding, 20px mobile
horizontal padding, 24px between form sections and 8px between labels and inputs.
Form vertical padding is 24px. These are starting defaults, not fixed containers
that may clip enlarged text. The precise content-driven responsive threshold and
additional width variants still need rendered validation.

## Elevation & Depth

Keep the white drawer’s separation from the off-white page subtle. Soften background
dimming before changing surface colours; use a fine divider and restrained shadow.
The background remains recognizable and inactive. Exact overlay/shadow values are
recorded in {components.task-drawer}; they carry forward the approved softened
reference. Rendered contrast, focus and reflow checks remain required.

## Shapes

Use {rounded.md} for buttons/inputs and {rounded.lg} for cards and small dialogs.
Calendar/timeline markers use the modest {rounded.sm} radius; continuation edges
retain their open edge and chevron. Borders use the recorded 1px component tokens,
with stronger control colour wherever the border identifies an interactive control.
Icons use Lucide, already used by platform/ui-business. Prefer established icons
with accessible names; decorative icons do not replace status text or patterns.

These defaults apply to the shared foundation used by Leave. Existing applications
adopt them deliberately; this approval does not mutate their styling or implement
the planned shadcn wrappers under platform/ui-core.

## Components

### Collection toolbar and mobile filter sheet

Place desktop view toggles at the opposite end of the heading from the title.
Arrange data controls in compact purpose-based groups with restrained separators,
using available width before adding rows. Legends remain visually secondary beside
their data. Avoid giving every filter an independent full-width row on desktop.

On mobile, use a bottom sheet for grouped filters: clear heading, close and reset
controls, generously spaced labelled fields, and a persistent Apply action. Keep
the background recognizable but inactive. Let content scroll without obscuring the
header or footer. Exact sizing, breakpoints, and tokens require validation; behavior
and application ownership are defined in [EXPERIENCE.md](./EXPERIENCE.md).

### Task drawer

Use a right-side drawer as the preferred contextual create/edit presentation,
subject to the exceptions and interaction rules in [EXPERIENCE.md](./EXPERIENCE.md).
Use the selected standard width and spacing above. Additional width variants,
backdrop/shadow values and responsive thresholds remain to be validated against
real content. This draft specifies defaults, not an implemented shared drawer.

### Shared control composition

| Component | Visual direction |
|---|---|
| Role selection | Plain role names and brief descriptions; capability details expand beneath the role |
| Custom-role editor | Application context above name/description and labelled capabilities; no mandatory template selector |
| Access-change review | Separate additions/removals and affected holders clearly, keeping technical identifiers secondary |
| Related-record navigation | Contextual Back text names the originating surface; do not rely only on browser history |
| Date inputs | Familiar unified range or single-date controls with readable typed values and adjacent validation messages |
| Upload control | Familiar browse control with a drop region where appropriate; visible progress/error feedback |
| Notification panel | Compact desktop list and full-width mobile sheet; unread marker, event title, permitted context and muted time; quiet Mark all as read action |
| Draft status | Persistent adjacent status near actions, distinct from ephemeral confirmation messages |

These are composition conventions, not numerical theme overrides. Use established
platform primitives when implemented; do not copy prototype CSS as a token catalog.

## Do's and Don'ts

- Give form content room to remain readable and usable.
- Keep required information in the active surface; background content is context.
- Do not force long, complex, or multi-step workflows into drawers.
- Do not assume a framework's defaults satisfy the final accessibility contract;
  verify the assembled component when implemented.
