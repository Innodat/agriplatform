---
name: KDG Capture
description: Mobile observation capture and a small online administration portal, inheriting shadcn/ui.
status: draft
created: 2026-10-12
updated: 2026-10-12
sources: [prd.md]
colors: {}
typography:
  body:
    fontFamily: system-ui, sans-serif
    fontSize: 16px
    lineHeight: '1.5'
rounded: {}
spacing:
  control-min: 48px
  gutter: 16px
  question-gap: 24px
components:
  choice:
    minHeight: '{spacing.control-min}'
  details:
    minRows: 3
---

# KDG Capture — visual contract

## Brand & Style

Simple phone form with generous touch targets; inherited shadcn/ui visual conventions.
KDG Capture is the app and home-screen name. Khula Development Group appears on login;
Daaglikse waarnemings is the capture subtitle. No new brand palette or logo is inferred.
User-provided visual direction can replace this unbranded draft without changing behavior.

## Colors

Inherit semantic shadcn background/foreground, border, ring and selected/disabled
tokens from the existing Expense shadcn lineage (`apps/expense/web/src/components/ui`
and `apps/expense/web/src/index.css`), as source reference only, never an application runtime import.
The scaffold owner extracts/verifies a coherent neutral theme before generation.
No override is selected. Selection and sync state use text/icon/border together,
never color alone. Measure contrast after actual tokens are selected; defaults are
not proof of contrast in the implemented app. Proposed thresholds: 4.5:1 ordinary text,
3:1 large text, controls and visible focus. Rating numbers do not use clinical
red/green gradients or invented meanings.

## Typography

Use {typography.body.fontSize} minimum input/body text with {typography.body.lineHeight};
system fonts remain available offline, avoiding a required network font. Labels wrap,
retain Afrikaans punctuation, and scale at 200% without clipped choices.

## Layout & Spacing

One vertical capture column, {spacing.gutter} horizontal mobile gutter and
{spacing.question-gap} between question groups. Six rating options form a wrapping
grid with all six available together; Ja/Nee pairs sit adjacent where width allows.
Each control meets {spacing.control-min}. Details sit directly below their Ja/Nee group.
On larger screens constrain reading width rather than stretching the questionnaire.
Admin forms use the same responsive controls with desktop room for ordered questions.

## Elevation & Depth

Use inherited shadcn sheet/dialog elevation only for overlays. Capture remains a flat
scrolling form; no card nested inside every question or decorative layer is required.

## Shapes

Inherit shadcn radii. Selected choices have a clear border/check plus accessible state;
large labels and touch area are the important delta.

## Components

Rating group: six integer radio choices, visible endpoint meanings. Boolean group:
two radios, Nee initially selected for the initial questionnaire. Details: labeled
multiline input immediately below a Ja. Sync status: text and icon distinct from form
validation. History row: child/date/owner where permitted/local or synced status.
Revision comparison: labeled local/current server values in stacked mobile sections.
Admin question editor: bounded type selector, wording, required, move up/down, retire;
drag is optional, never the only reorder control.


| Component | Visual contract | Behavioral contract |
| --- | --- | --- |
| Child/date controls | Visible label and inherited select/date styles | Sole child automatic; additional assigned options only; editable calendar date |
| History row | Child/date/authorized author plus text status | Keyboard/touch activation; return retains scroll and initiating focus |
| Revision comparison | Stacked labeled base/local/current sections | No automatic merge; fresh server read and explicit choices |
| Admin question editor | Labeled bounded fields, visible move controls | Whole-form Save/Cancel, position announcement, immutable published view |
| Assignment form | Named child/facilitator and inline eligibility/errors | Required online eligibility, explicit Save/Cancel, no implicit grants |
| Exit/publication dialog | Inherited Dialog/Sheet, visible title/actions | Focus trap/restore; Escape respects unconfirmed-exit/unsaved rules |
| Sync status/attention | Icon plus textual local/server/attention state | Polite meaningful announcements; per-item action; no focus theft |

## Do's and Don'ts

Keep controls reachable with phone keyboard open and respect safe-area insets. Use
visible labels, visible focus and text feedback. Keep admin tools out of capture
navigation. Do not imply a locally saved capture is backed up; do not show inaccessible
child/author names or sensitive answers in install icons, notifications or support text.

All screens currently have written specifications only. No mockups or implemented accessibility evidence
exist. [EXPERIENCE.md](EXPERIENCE.md) owns behavior; these spines win over future mocks.
