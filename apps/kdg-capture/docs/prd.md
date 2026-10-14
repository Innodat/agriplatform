---
title: KDG Capture
status: draft
created: 2026-10-12
updated: 2026-10-13
working_mode: fast-path
---

# PRD — KDG Capture

## Purpose and vision

Repository-owned requirements for product-owner review, UX, architecture, stories and
ATDD. KDG Capture gives Khula Development Group's emotional facilitators a simple
phone form for identified observations about children, even without connectivity.
Useful input and locally saved captures survive ordinary offline close/reopen;
later synchronization makes them available to authorized organization administrators.
Offline capture and editable history are the MVP results experience.

The user supplied the scope; no generic survey discovery, market research or product
brief is required. Runtime claims are in [discovery.md](discovery.md), technical
mechanisms in [contracts.md](contracts.md), behavior in [EXPERIENCE.md](EXPERIENCE.md).

## Users, roles and journeys

Only two application roles. Capturer: create for assigned children, read/edit own
captures. Questionnaire administrator: manage/publish questionnaires, manage children
and facilitator assignments, read/edit all authorized Khula captures, and create.
Organization membership and platform organization administration grant neither role
implicitly. Platform access administration retains its own authority.

Initial organization: Khula Development Group. Initial child: Sinehgomso. Initial
account: Louwnique Kok, explicitly assigned questionnaire administrator with capture
capability. Verify actual account/actor during controlled setup; do not bind by name.
The child is the subject; the authenticated facilitator is the respondent/author.
No People or employment record is required.

- **UJ-1:** Louwnique signs in online, enters fixed authorized Khula context, downloads
  Sinehgomso and published questionnaire, installs/opens KDG Capture, records offline,
  sees Saved on this phone, closes/reopens and sees the capture, reconnects and sees
  Synced plus the server-backed record. A local acknowledgement confirms the phone save;
  a separate server acknowledgement confirms the server copy.
- **UJ-2:** Louwnique edits an older capture using its original questionnaire. Another
  authorized edit produces a conflict; both inputs remain available until reviewed.
- **UJ-3:** Louwnique uses the online portal to save a questionnaire draft and publish
  a new immutable version; a disconnected facilitator's old-version capture remains valid.

- **UJ-4:** Louwnique assigns an active child to an eligible verified facilitator in the
  online portal; saved assignment changes no membership or Access grant.

## Glossary

Organization: platform tenant identified by org_id. Child: KDG observation subject.
Facilitator: authenticated application user, not an employment entity. Assignment:
KDG child/facilitator association, distinct from Access grants. Questionnaire: stable
identity with draft/published versions. Question: stable UUID within that questionnaire.
Capture: editable observation with immutable original owner and referenced version.
Unfinished entry: unsaved in-memory input, not recovered after close/restart.
Questionnaire draft: online administrator configuration awaiting publication. Revision: server
concurrency value, distinct from local edit sequence. Operation: one immutable retriable
command. Synced: server acknowledged the current local capture changes.

## Functional requirements

### Entry and authorization

**FR-1 — Identity and fixed organization.** Authenticate using retained platform Auth;
online setup is required. Resolve current authorized Khula membership and application
admission. No organization switcher, automatic fallback to another organization or
client authority from a supplied org_id. Wrong-organization accounts cannot enter.

**FR-2 — Explicit permissions.** Backend and UI enforce the two roles above, current
membership/admission/grants and capture ownership. Administrator edits preserve the
original owner and identify editor separately. Capturers cannot read another facilitator's
records or manage questionnaires; membership alone grants no capture access.

**FR-3 — Initial provisioning.** A restricted, owner-controlled mechanism supplies the
initial published questionnaire, child and assignment without depending on a full editor.
Shared owners supply verified identity/membership/access; KDG supplies its domain data.

### Capture

**FR-4 — Phone surface.** Application/home-screen name KDG Capture; login screen displays
Khula Development Group; capture subtitle Daaglikse waarnemings. Installable Android/iPhone
PWA, one short scrolling accessible form; no questionnaire editor in capture navigation.
Show Sinehgomso automatically when it is the sole eligible child; select only among
authorized children when more exist. Capturers use assigned children; administrators
may capture for every active Khula child. No eligible child is a setup state, not fake data.

**FR-5 — Initial questionnaire.** Afrikaans wording below is exact. First question is
required integer 1–5 with five large mutually exclusive options, initially unanswered;
1 = Goed, 5 = Nie goed nie. No clinical meanings for 2–4. Questions 2–4 are required
Ja/Nee, with Nee initially selected (user clarification supersedes unanswered wording).
Ja immediately reveals optional multiline Besonderhede below that question. Nee hides
it; temporary editing text returns if toggled back to Ja but hidden details are absent
from the active saved answer. Four primary answers required; details optional.

| Stable seed key | Wording |
| --- | --- |
| attitude | Hoe was haar algehele houding vandag? |
| outbursts | Het sy enige uitbarstings/gedragsprobleme gehad? |
| left-class | Het sy sonder toestemming uit die klas geloop vandag? |
| ran-home | Het sy probeer huis toe hardloop? |

Seed keys are readable planning labels; actual question identity is stable UUID, never
wording/position. Description of intermediate rating values is an outstanding content
decision and does not block displaying their numeric labels.

**FR-6 — Date and multiplicity.** Observation date defaults to today and is editable;
it is distinct from local recording and server creation/update times. Multiple captures
per child/date allowed. If locally known captures exist, offer Edit existing / Add another,
never force deduplication or claim knowledge of records unavailable offline.

**FR-7 — Explicit local Save.** Save observation explicitly validates and commits a
completed capture plus pending sync operation locally. Success follows atomic local
persistence; saved captures can be reopened offline. Unfinished input stays in memory:
no observation autosave/draft/resume workflow. Closing/restarting before Save may lose
input, an accepted simplicity tradeoff. Failed Save retains values on screen with useful
plain guidance and bounded recovery, never a deliberate crash or false saved status.
App-controlled exits use ordinary explicit-form unsaved-change handling, not draft flushes.

### History and questionnaire lifecycle

**FR-8 — History and editing.** Both roles browse/edit own downloaded/local observations
in the offline PWA. Administrators access all permitted organization records only in
the online portal. Preserve original author/time, editor, revision history and observation date.
History presents observation dates and answers with compact sync feedback, without
routine author/editor audit metadata or a revision browser. Preserve attribution
internally; authorized administrator audit presentation is separate. No offline revision archive; retain necessary pending/conflict snapshots and
original questionnaire definitions internally. Immutable server change evidence stays
protected without requiring revision-list UI. Distinguish pending local work and
observations unavailable offline.

**FR-9 — Concurrent edits.** Detect stale revisions; retain saved offline own changes/
bases/conflicts durably, while online administrator attempted changes remain in memory,
and require explicit review/resolution. No silent overwrite or auto-advanced revision.
Repeated conflict re-enters review; account/organization restrictions apply to resolution.
The editor/device holding the saved conflicting proposal resolves it: capturers handle
own edits and administrators their edits to authorized captures. First access grants
no priority; the portal cannot see never-synchronized phone proposals.

**FR-10 — Questionnaire editor.** Online administrator portal adds, reorders, retires,
edits wording/required status for rating, Ja/Nee and text questions, including optional
Ja details. Explicit whole-form Save/Cancel for draft configuration; explicit Publish.
No arbitrary branching, scoring engine or general survey-builder feature set.

**FR-11 — Immutable version compatibility.** Publishing creates an immutable version.
Each capture and open in-memory entry pins its exact version. Original wording, labels and scale remain
visible/editable historically. Old downloaded published versions remain accepted on sync.
After downloading a newer version, new captures use it; open entries are never silently
migrated. Stable question IDs survive wording/reorder edits; incompatible type changes
receive a new question ID. Retired questions remain in historical versions.

**FR-12 — Administration and assignments.** Responsive online portal manages children
and assignments to verified Khula facilitator accounts. Assignment is not membership or
an access grant. Normal account onboarding/role administration uses shared owners; no
parallel user/password/role directory. Offline administration is outside scope.

### Offline and reliability

**FR-13 — Offline provisioning and isolation.** Cache required versions and eligible
child data after successful online setup. Isolate all local saved captures, versions,
history and queue data by account and org_id. Closing/reopening offline preserves
acknowledged local data subject to browser storage limitations.

**FR-14 — Durable sync.** Queue local creates/edits transactionally with captures.
Device-generated capture/operation IDs are stable; interrupted/lost-response retries
produce one server effect. Sync on open, resume, reconnection and Sync now; background
sync is optional. Administrators see other devices' new captures only after synchronization.

**FR-15 — Truthful state.** Distinguish Saved on this phone, Synced and Needs attention.
Local success never implies server backup. Automatic retry is bounded; known denial,
validation/conflict and transient unavailability receive different recovery paths.

**FR-16 — Offline authorization and sessions.** User-approved local access window is
seven days from successful online authorization for the fixed user/Khula context.
Expired login can permit local use within that window; server reads/sync need renewed
authentication and current checks. Membership/grant/assignment revocation cannot be
observed offline; when learned online, block affected new actions, preserve unsynced
work without exposing it to another account, and do not upload by bypassing authority.

**FR-17 — Logout and account change.** Explain pending local work before explicit logout;
offer stay/sync when online or sign out and retain locked pending data for the same
account. Another account cannot browse or submit it. Offline-window expiry locks without
deletion; token expiry alone follows FR-16.
No silent queue deletion or upload as the replacement account.

**FR-18 — Storage and update recovery.** Handle quota/write failures before saved feedback,
storage eviction as possible data loss, incompatible local schema as a blocked update,
and interrupted migrations without discarding pending work. App updates do not automatically
reload active forms or abandon unresolved operations. Explain that never-downloaded history
is unavailable offline. No guarantee against browser/OS storage deletion.

## Quality requirements and validation targets

**NFR-1 — Isolation.** Actual restricted runtime-role RLS, tenant-aware constraints,
backend ownership/grant checks and pooled-context negative tests; zero cross-user/org
disclosure in defined acceptance fixtures. No logs/traces containing child answers,
tokens, payload dumps or full sessions.

**NFR-2 — Save integrity.** Acknowledgement follows atomic local commit; server effects,
revision, history and operation receipt commit atomically. Failed/unknown responses never
become Synced. Local storage loss remains an explicitly disclosed practical limitation.

**NFR-3 — Accessibility.** Proposed WCAG 2.2 AA floor, visible focus and text status,
keyboard/screen reader semantics, 48 CSS-pixel touch targets, 200% text zoom and 320px
viewport without lost controls. Android TalkBack/iPhone VoiceOver checks are physical.

**NFR-4 — Bounded operation.** Proposed targets: local save feedback within 1 second
for seeded form on test devices; foreground cycle at most 30 seconds, each online
request at most 10 seconds; failures leave actionable state. These are review targets,
not measurements. Exact compatible package pins and API limits precede Build readiness.

**NFR-5 — Evolution and release.** Controlled owned migrations, prior-version compatibility,
activation blocked on migration failure, explicit recovery under platform ADR-0020;
queue/API/questionnaire/local-schema versions tested independently. Real installed PWA
checks on both Android and iPhone are required before completing the application.

## Scope and success

MVP: capture PWA, own/authorized organization history, editable captures, conflict
resolution, small online questionnaire editor/publishing, children/assignments and
reliability. One silo/deployment can host both surfaces. Exclude aggregate dashboards,
analytics, exports, notifications, attachments, anonymous/public survey distribution,
supervisor roles, employment dependencies and MVP organization switching.

Success is the full UJ-1 proof on both phones, replay without duplication, no forbidden
record access, and historical/offline-version editing. Do not optimize capture counts
or completion speed at the expense of required answers, access or truthful status.

## Open items and assumptions

- **O-1:** Shared handoff and exact KDG Access variant/schema/operator/generator contracts
  remain readiness gates; coordinator is this session, component owners retain authority.
- **O-2:** Khula approves business history retention and device suitability before pilot
  activation, including lawful processing of children's information, phone pending-data
  retention and explicit privacy restriction handling; the 30-day own offline history
  window is approved. No automatic deletion on ordinary deactivation.
- **O-3:** Afrikaans operational/status/action translations and 2–4 descriptions require
  Khula content review; numeric intermediate options can ship without invented descriptions.
- **O-4:** Identity/Access must declare trusted target-account eligibility evidence for
  initial assignment setup (no user-check account selector). Membership-retirement/rejoin renewal is user-approved with Story 5.2; exact
  authoritative membership-instance evidence remains a shared contract gate. Missing
  current app grants can never be restored by domain assignment alone.
- **A-1 resolved by user:** Administrators create for every active Khula child;
  capturers create only for assigned children.
- **A-2 resolved by user:** Unassignment removes new-create eligibility, but capturers
  retaining current KDG access keep own historical viewing and editing.
- **A-3 resolved by user:** Today's default uses the phone's local calendar date,
  displayed/editable; no employment/work timezone dependency.
- **A-4 revised, 2026-10-13:** Explicit Save observation only; remove unfinished-input
  autosave/recovery as disproportionate for this MVP. Unsaved typing may be lost on
  close/restart. Existing capture edits retain Save/Cancel. See proposed KDG ADR-0001;
  revised Story 1.5 was approved when the user requested the next step.
- **A-5 revised by user, 2026-10-14:** Download recent 30 days of own observations in the
  PWA for either role. Organization-wide administrator review/edit/audit is online only;
  no offline all-record cache or authority. Older own history remains available online. Pending
  work and referenced original versions are retained regardless of that window.
- **A-6 revised by user with Story 5.1:** Ordinary child deactivation removes refreshed
  new-capture choices but accepts pending offline observations from previously provisioned
  eligible-child setup under current access/assignment checks. It retains historical
  read/edit rights. Privacy processing restriction/deletion is a separate policy.

User resolutions are indexed above, including A-6 approved with C.
None of these app policies is an accepted platform decision or runtime claim.

Approved surface split, 2026-10-14: capture PWA = capture and My observations (own
read/edit, offline); online responsive administration = all authorized Khula observations,
editing and audit. Louwnique captures/edits her own observations offline like other
capturers. This supersedes earlier administrator all-history offline wording.

Approved administrator conflict simplification, 2026-10-14: online attempted answers
remain in memory for immediate review; closing/reloading can lose uncommitted input.
No server-stored conflict proposals or administrator resolution drafts. Existing
operation receipts and immutable successful-change evidence remain. Capturer explicitly
saved offline pending/conflicting edits retain their durable local behavior.
