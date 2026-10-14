---
name: KDG Capture
status: draft
created: 2026-10-12
updated: 2026-10-13
sources: [prd.md, DESIGN.md]
---

# KDG Capture — experience contract

## Foundation

React/Vite/shadcn responsive web, installable capture PWA on Android and iPhone.
DESIGN.md owns visuals; this document owns behavior. A single authorized fixed Khula
context is resolved after sign-in; no selector or switching exists. Online admin route
may share this deployment. First setup requires internet, protected actions use KDG API.
Seven-day offline local-use window is agreed, not authority for any server operation.

## Information Architecture

| Surface | Entry | Purpose and availability |
| --- | --- | --- |
| Sign-in/setup | First launch or local-access expiry | Khula branding, retained platform sign-in, current admission, initial download; online |
| Capture | Installed app open / New observation | Eligible child, date, pinned questionnaire, explicit Save; offline after setup |
| History | Capture navigation | Own/all-permitted downloaded records; explicitly partial offline history |
| Record details/edit | History row or known same-day prompt | Original questions/observation date; compact status; local offline edit |
| Sync status/attention | Status or Sync now | Pending operations, sign-in needed, rejected/conflicting changes; no answers in summary |
| Conflict review | Attention item | Local vs current server comparison and explicit resolution; fresh server state needed |
| Questionnaire list/editor | Admin portal | Draft Save/Cancel, explicit publish, immutable published-version view; online |
| Children/facilitator assignments | Admin portal | Child availability, verified facilitator account, assignment form; online |

Capture navigation contains capture/history/status, never questionnaire management.
Administrator role exposes a separate Go to administration action; capturer does not
see it. Local admin history is limited to downloaded permitted records, not a promise
to have the entire organization corpus. No aggregate-results screen.

## Voice and Tone

Question text/Ja/Nee/Besonderhede is Afrikaans from FR-5. Required literal brand names
remain exact. Proposed action/status text uses the agreed English labels until Khula
approves Afrikaans translations; do not invent approved translations. Use Afrikaans
language metadata for questionnaire content and explicit English spans for untranslated
status/action examples; final copy requires Khula review.

| State | Message/action |
| --- | --- |
| Confirmed local capture | Saved on this phone; waiting to sync |
| Current local content server-acknowledged | Synced |
| Action required | Needs attention with specific safe reason |
| Explicit Save not confirmed | Latest changes not saved; keep values visible, safe guidance and Retry after recovery |
| No downloaded older results | This history is not available on this phone |
| Authentication required | Sign in again to sync; preserve same-user work |
| Access check unavailable | Could not check access / Retry; no false denial |

## Component Patterns

- Rating group uses radio semantics, six options 0–5; initially no rating. Endpoint
  labels are Goed/Nie goed nie; intermediate options are numeric pending content.
- Initial Ja/Nee groups start at Nee. Ja reveals optional details immediately below.
  Toggling Nee hides details, removes them from active capture answers, and retains a
  in-memory editor buffer while the form stays open. Cancel/complete
  ends the buffer. Restoring buffer is not uploading hidden details.
- Child is displayed automatically when only one is eligible. Capturers choose among
  assignments; administrators choose among all active Khula children. The date is editable; original author never is. Multiple same-day captures
  offer Edit existing/Add another only from locally known history.
- New observation uses explicit Save observation for all input; existing capture edits
  use whole-form Save/Cancel. No unfinished observation is autosaved or recovered after
  restart. Completed local capture and pending operation commit atomically before
  Saved on this phone. Distinct captures per child/date remain allowed.
- Temporary hidden details stay in memory and never enter a false saved answer.
  Synced appears only when the current local content is server-acknowledged.

- Administration uses whole-form Save/Cancel; Publish is a separate reviewed action.
  No descriptive field writes while another field awaits Save. Published versions
  are view-only; Edit creates a new draft version rather than altering old definitions.


| Component | Visual contract | Behavioral contract |
| --- | --- | --- |
| Child/date controls | Visible label and inherited select/date styles | Sole eligible child automatic; capturer assignments/admin active-child options; editable calendar date |
| History row | Child/date/authorized author plus text status | Keyboard/touch activation; return retains scroll and initiating focus |
| Revision comparison | Stacked labeled base/local/current sections | No automatic merge; fresh server read and explicit choices |
| Admin question editor | Labeled bounded fields, visible move controls | Whole-form Save/Cancel, position announcement, immutable published view |
| Assignment form | Named child/facilitator and inline eligibility/errors | Required online eligibility, explicit Save/Cancel, no implicit grants |
| Exit/publication dialog | Inherited Dialog/Sheet, visible title/actions | Focus trap/restore; Escape respects unconfirmed-exit/unsaved rules |
| Sync status/attention | Icon plus textual local/server/attention state | Polite meaningful announcements; per-item action; no focus theft |

## State Patterns

| Condition | Behavior |
| --- | --- |
| Offline after complete setup and within seven days | Open cached shell and authorized partition; local capture/history/edit remain available |
| Offline before setup, missing version, or expired local access | Explain online setup/sign-in needed; no fake empty questionnaire or old-account access |
| Local write fails / quota exhausted | Keep values visible; bounded recovery/safe disposable-cache reclamation where available, then plain guidance with inline Retry. Persistent quota failure suggests freeing phone storage while keeping the form open; no forced restart or false saved feedback |
| Confirmed local save, server unreachable | Close immediately; record remains Saved on this phone; no exit warning merely for unsynced work |
| Changed explicit-Save form on departure | Ordinary unsaved-change confirmation on app-controlled navigation; no autosave flush/recovery promise on OS termination |
| Known permission/membership loss | Lock affected content and stop synchronization; retain pending partition for same-user recovery, no cross-account exposure |
| Assignment/child availability changed | Stop new creation for that child; preserve rejected local captures as attention items; no automatic author/child reassignment |
| Session expired, local window valid | Continue local use; online renew/re-auth needed to sync, same-account restore only |
| Lost server response | Pending outcome; same operation/payload lookup/retry, no new operation |
| Conflict | Preserve local/base/server versions; show comparison; explicit Use current record or Save reviewed changes with current revision |
| Update available | Offer update when locally persisted and sync idle; do not force page reload or wipe queue |
| Browser storage removed | Explain unavailable local work; re-provision online. Cannot recover unsynced bytes that no longer exist |

Required loading and failure states: sign-in/setup has checking/denied/unavailable/incomplete states; failed
provision keeps setup incomplete. Capture with no assignments gives online setup guidance.
History distinguishes downloading/empty/partial/error and preserves pending overlays on
refreshed records. Details distinguishes loading/not-downloaded/missing/denied with safe
Back. Sync distinguishes empty/progressing/uncertain/failed/denied. Conflict replacement
requires current authorized server details; failed load offers Retry and keeps inputs.
Questionnaire list/editor distinguishes loading/empty/denied/error and blocks writes if
required load fails. Children/assignments distinguishes loading/empty/not-eligible/denied/
error; unavailable eligibility is never an empty eligible list. Denied screens reveal no data.

Failed local migration shows App update could not complete / Retry, retains prior stores
and blocks incompatible writes. Other open instances get Close other KDG Capture windows
to update; no delete/reset shortcut. Failed admin writes preserve values and distinguish
known rejection from uncertain outcome.

## Interaction Primitives

Use native form/radio keyboard interaction. Save observation validates and persists the
whole new capture; Save/Cancel applies to existing edits/admin. A controlled exit warns
about unsaved changes; it does not attempt a draft flush. OS/browser termination cannot
be assumed to show a warning. Cancellation never reverses an acknowledged save.
Reauthentication restores permitted saved-record context, not unfinished typing, and
never automatically saves/submits an observation. Keep explicit sign-out pending-work
checks for acknowledged captures/uncertain Save operations; other accounts cannot use them.
No unfinished-input persistence or resume interface is required.

## Accessibility Floor

Proposed WCAG 2.2 AA, controls at least {spacing.control-min}, labels associated with
inputs, fieldset/legend for radio groups, live polite status with errors focused where
useful. Announce selected state and details expansion without moving focus unexpectedly.
Dialogs trap/restore focus; form errors link to inputs. Touch, keyboard, TalkBack and
VoiceOver all reach Save, Retry and conflict choices. 320px viewport and 200% text zoom
retain reading order and controls; keyboard/safe-area do not cover final action.

Component mapping: shadcn RadioGroup for choices, Label/Textarea for details, Button for
Save/Retry/reorder, Dialog/Sheet for exits/reviewed publication, Alert/status for persistence,
and semantic lists/tables for history. Existing ui-core does not supply these components;
extract/prove neutral controls through platform owner. Escape/dismissal respects unsaved
exit rules and restores invoking focus. Reorder announces position and retains question
focus; error summaries link to fields. Sync updates never steal typing focus.

## Key Flows

### UJ-1 — Louwnique records Sinehgomso offline

1. Sign in online, verify fixed Khula access, download child/version in the installed app.
2. Disconnect, open KDG Capture, choose rating and confirm/change Nee defaults.
3. Save observation. **Local success:** Saved on this phone appears only after commit.
4. Fully close/reopen offline and open that capture in history/details.
5. Reconnect/Sync now. **Server success:** Synced, then read server-backed capture.

Failure: storage failure produces no saved state; unreachable server keeps local record.

### UJ-2 — Louwnique reviews concurrent edits

1. Open original-version record; edit and Save locally.
2. Sync detects another editor's revision; Needs attention retains local/base/server values.
3. Compare current authorized server details and explicitly select complete resolution.
4. **Success:** revision-checked acknowledgement appears in history, preserving author.

Failure: another intervening edit repeats review; descendants remain paused and inputs retained.

### UJ-3 — Louwnique publishes

1. Open online portal and edit a new questionnaire draft.
2. Save/Cancel whole form, then explicitly review and Publish.
3. **Success:** immutable version is available for next downloads.

An already open entry stays on its original version; next new capture after download uses latest.
Failure: uncertain publish keeps original operation; no second version from a blind retry.

### UJ-4 — Louwnique assigns a child

1. Open online administration, Children/assignments.
2. Select active Khula child and eligible verified facilitator account.
3. Save whole form. **Success:** committed assignment shown; membership/grants unchanged.

Missing account/admission links shared onboarding/access where available, not grant creation.
Failure: failed eligibility load blocks Save with Retry; changed eligibility rejects stale Save.

## Responsive & Platform

Capture remains single-column on phones and computer. Administration is responsive,
using sheets on small screens where needed and explicit up/down reorder controls.
Use manifest standalone mode, app-specific scope/start URL and icons. iPhone install
instructions use supported Add to Home Screen; Android install UI depends on browser.
Do not assume browser-tab setup automatically transfers every cached byte/session to an
installed iPhone PWA: test provisioning within the installed context. Physical-device
matrix and app update checks live in testing.md.

## Observation saving simplification — 2026-10-13

The user rejected automatic unfinished-form recovery for the four-question MVP. Use
explicit Save only; before-Save typing may be lost on close/restart. Completed captures
still persist offline/queue for sync. Questionnaire administrator draft/published versions
and capture conflict resolution remain in scope. Proposed [KDG ADR-0001](architecture/decisions/0001-explicit-observation-save.md)
records the application rationale; [revised Story 1.5](epics.md#story-15-explicitly-save-an-observation-on-this-phone)
is now planning-approved. Implementation/readiness remain separate.

## Visual coverage

All eight navigation surface groups have written specifications only in this fast-path draft; no visual mock is
claimed. Capture/rating/details and conflict comparison are the highest-value optional
mocks. A mock is not required for runtime/device acceptance, and cannot override spines.

Scope simplification, 2026-10-14: history means saved observations, not a revision
browser. No revision downloads or per-revision availability prompts. Keep creation
and last committed modification attribution internal for administrator audit; show
observation date/answers in capture details and competing saved versions only when
resolving conflicts. Original questionnaire definitions are selected internally.

Approved conflict responsibility: the editor/device holding saved conflicting changes
reviews its own proposal under existing permissions. Administrators handle their own
conflicting edits; no first-reader priority or portal access to unsent phone proposals.
