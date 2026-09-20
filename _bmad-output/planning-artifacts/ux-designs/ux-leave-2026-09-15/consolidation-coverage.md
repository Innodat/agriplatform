# Leave UX consolidation coverage — 17 September 2026

This is the proactive Finalize Pass 1 coverage check, not an opt-in formal review,
a reviewer verdict, or an implementation-readiness claim. Both spines remain draft;
all HTML remains in `.working/`. No artifacts were promoted, no runtime was changed,
and no browser or assistive-technology verification was performed in consolidation.

## Inputs and precedence

Read the prior spine pair, full decision memlog, all 17 HTML references, the skill's
canonical shape/specification and all five design/experience examples. Reconciled
relevant current feature-catalogue/UX/state requirements and latest approval ADRs.
Product requirements and accepted superseding decisions govern business behavior;
spines govern presentation when a mock differs. The platform drafts are inherited
by reference and were not edited by this distillation task.

The latest accepted choices retained include duration-only partial days; Close with
saved-draft recovery; inline unpaid emphasis; one draft per employee/NGO; single
Approver role; scoped authority conferred by temporary appointment; directional
absence fallback and supervisor return; one assigned profile with explicit overrides;
one-off versus continuing entitlement; review for high-impact adjustments; no
repeated entitlement-form summary; simple custom-role creation with separate
Duplicate; assigned-holder review/deletion constraints; consultant/email import
approval and cutover procedure. Missing configured approval route blocks submission
while preserving the draft; missing applicant coverage permits submission but gates
final approval. These are different conditions.

## Pass 1 results

| Check | Result | Remaining gap / location |
|---|---|---|
| Flow coverage | Sixteen named-example flows with numbered steps, climax and failure/limits; no UJ/FR IDs exist in source | Not every catalogue requirement has a separately closed journey; organization/employment administration, full setup and some balance/attachment/operational tasks remain partial |
| Token completeness | Frontmatter contains required name; no invented token values or dangling token references | DESIGN Colors/Typography/Layout/Shapes: final palette and scales absent. Empty token maps are an explicit implementation blocker, not a complete machine-readable theme |
| Component coverage | All 26 named EXPERIENCE Component Patterns sections have matching DESIGN Components rows | Shared primitives inherit platform rules; complete component/state implementation specs remain unproven. Composite coverage does not demonstrate every widget |
| State coverage | EXPERIENCE State Patterns maps every IA group and preserves detailed accepted lifecycle/save/access states | Cold-load, configuration failures/concurrency, detailed export/upload/notification and some empty states are unresolved rather than invented |
| Visual reference coverage | Every one of 17 `.working/*.html` files is linked inline; no orphan mocks; local links resolve | Most refs have no browser verification; several IA surfaces have only partial or spine-only coverage. No imports/mockups/wireframes directory artifacts were supplied to promote |

## Source requirement to flow mapping

Names below mirror `apps/leave/docs/features.md` headings. A mapped flow demonstrates
entry and approved behavior, not exhaustive requirement satisfaction. Long ledger,
permissions and operational requirements remain authoritative at source.

| Feature catalogue heading | Key Flow | Coverage limit |
|---|---|---|
| 1. Identity, NGO context, and onboarding | 14, 15 | Shared shell; invitation/provisioning settings not fully visualized |
| 2. Organization and employment structure | 7, 11, 15 | Complete employee/team/location/supervisor CRUD forms open |
| 3. Jurisdictions and workplace calendars | 11 | Partial profile/calendar editors; no assumed country rules |
| 4. Leave types and policy management | 8 | Full field catalogue/editor and archive states open |
| 5. Employee entitlement overrides | 10 | Non-default midperiod effective-date choice unresolved |
| 6. Balance ledger and accrual | 1, 5, 9 | Full ledger/projection and all policy calculations not redefined in UX |
| 7. Leave application experience | 1 | Complete duration/validation/upload states open |
| 8. Hourly and half-day leave | 1 | Duration-only choice retained; dedicated widget visual coverage partial |
| 9. Insufficient-balance override | 3, 4 | Separate override detail and revised-acknowledgement layouts spine-only |
| 10. Configurable approval workflows | 3, 7, 8 | Snapshot/concurrency/service mechanics remain architecture work |
| 11. Request lifecycle | 2, 4 | Several confirmation/detail states spine-only |
| 12. Attachments | 1, 3 | Upload appears; complete verification/rejection/retention UI absent |
| 13. Notifications | 4, 7, 9, 14 | Compact inbox behavior captured; shared rendering/admin states absent |
| 14. Employee workspace | 1, 2, 14 | Projection/ledger composition incomplete |
| 15. Approver workspace | 3 | One Approver role; supervisor remains assignment source |
| 16. Final-step context in the Approver workspace | 3, 7 | Same queue/role; final remains workflow position |
| 17. Leave Manager workspace | 4–13, 15 | Several management review layouts still partial |
| 18. Calendars and privacy | 2, 3, 6, 11 | Marker/privacy rules recorded, accessibility verification pending |
| 19. Reports and exports | 12 | One report pictured; all six definitions/query contracts remain source-owned |
| 20. Audit and operational administration | 13 | Operational administration beyond audit list not fully designed |
| Permissions; shared application roles | 16 | Effective-grant catalogue, dependencies and assignment contracts pending |

## Surface to mock inventory

The EXPERIENCE Information Architecture table is the complete destination inventory.
These 17 artifacts are all partial prototypes with illustrative values and no
production authorization, persistence, approval, export or policy engine.

| Mock | Surface / decision illustrated |
|---|---|
| [apply-wireframe.html](./.working/apply-wireframe.html) | My Leave background; desktop drawer/mobile application; funded and unpaid breakdown |
| [approval-review-wireframe.html](./.working/approval-review-wireframe.html) | Queue context, decision hierarchy and team availability |
| [organization-overview-wireframe.html](./.working/organization-overview-wireframe.html) | Timeline/list, sticky names/dates, statuses/continuations, mobile filters |
| [leave-manager-home-wireframe.html](./.working/leave-manager-home-wireframe.html) | Attention queues, desktop tools column and mobile tools sheet |
| [leave-correction-wireframe.html](./.working/leave-correction-wireframe.html) | Returned-early comparison, restoration/reservation and reason |
| [policy-review-wireframe.html](./.working/policy-review-wireframe.html) | Current/scheduled summaries and publication impact review |
| [temporary-approver-wireframe.html](./.working/temporary-approver-wireframe.html) | Dates, responsibilities, pending transfers and conditional expiry return |
| [employee-history-wireframe.html](./.working/employee-history-wireframe.html) | Year/month/list, employment bounds and corrected history |
| [balance-adjustment-wireframe.html](./.working/balance-adjustment-wireframe.html) | One-off grant and concise review |
| [employee-entitlement-wireframe.html](./.working/employee-entitlement-wireframe.html) | Recurring policy/override choice; no duplicate editing summary |
| [employee-schedule-wireframe.html](./.working/employee-schedule-wireframe.html) | Assigned profile, inherited fields and restoring an override |
| [application-access-wireframe.html](./.working/application-access-wireframe.html) | Shared person/application role selection and change review |
| [approval-workflow-wireframe.html](./.working/approval-workflow-wireframe.html) | Ordered supervisor/selected approver and directional absence setting |
| [reports-wireframe.html](./.working/reports-wireframe.html) | Report selector beside balance results; filters/export concept |
| [audit-history-wireframe.html](./.working/audit-history-wireframe.html) | Chronological expandable actor/reason/before-after events |
| [holiday-calendars-wireframe.html](./.working/holiday-calendars-wireframe.html) | Configured calendar list and organization-closure edit preview |
| [custom-role-wireframe.html](./.working/custom-role-wireframe.html) | Empty creation form, business capabilities and separate duplication concept |

## Load-bearing open items

1. **Visual contract:** approve final platform/app tokens, typography, spacing,
   drawer widths, breakpoints and contrast combinations. Reconcile them into
   DESIGN frontmatter before implementation consumes machine-readable tokens.
2. **Surface closure:** finish complete policy/profile/organization/employee/setup
   layouts, balance projections/ledger, on-behalf entry, deficit/override review,
   temporary termination and role-edit/delete review as needed. IA labels these
   partial instead of treating home-page destination dialogs as finished screens.
3. **State closure:** complete the remaining state matrix, especially stale
   configuration/role changes, upload failures, export failures, and cold/empty/error
   variants. Validate actual focus/return, phone keyboard, zoom, status announcement,
   translated text and timeline/calendar access.
4. **Recurring entitlement source reconciliation:** next-period default and no
   automatic end date are accepted. Whether an authorized non-default midperiod
   recurring start remains exposed, and its financial effects, is not resolved here;
   source rules retain precedence. Do not treat a mock's fixed next-period date as
   a newly approved universal restriction or allow an unreviewed recalculation.
5. **Role/snapshot mechanics:** unified Approver capability must be scoped to assigned
   steps, with temporary grants and sensitive-document access separate. Full
   effective-grant/dependency catalogue, concurrent return/decision consistency and
   related architecture contracts remain unresolved implementation dependencies.
6. **Mock differences and evidence:** old access-mock prose suggests creating from
   an application role; accepted creation is empty and Duplicate is separate.
   Static policy/workflow examples do not prescribe universal entitlements, dates,
   reminders beyond the approved starter, or hard-code a CEO. Some mock actions are
   previews in dialogs while the shared final surface uses drawers/pages. Browser
   Back, real filtering, lists of all states and server effects are commonly absent.
   Parent source-reconciliation work should retain any further source contradictions.

## Documentation-only and deferred exceptions

Consultant import validation, exact-batch client email approval, source balance-date
and reservation conventions, and export-to-cutover reconciliation live in the
[migration runbook](../../../../apps/leave/docs/operations/migration-runbook.md).
No client confirmation page, Confirm balances action, separate authentication or
self-service importer is added. Executable tooling and rollback remain future work.

The personal cross-app task inbox waits for another application; shared Microsoft
Graph supervisor synchronization and calendar integration remain future capabilities.
The notification inbox and several short lifecycle confirmations have accepted
spine-only behavior but no dedicated visual approval. This document records that
fact; it does not claim the user waived further visual review.

## Verification performed

Python local-link existence and `.working` coverage checks passed: no missing local
spine links and no unlinked HTML references. Component-name correspondence and
canonical section order were checked against the skill shape. This documentation
change did not run application tests or claim HTML rendering, UX validation, final
status or Phase 1 implementation authorization.

## Subsequent decision — 19 September 2026

The user resolved the recurring-entitlement date question: MVP changes are restricted
to leave-period boundaries, defaulting to the next boundary. Immediate changes use
separate adjustments. See Leave ADR-0083 and the updated source/experience contract.
Earlier open-item statements above are retained as the consolidation snapshot.

The user also deferred the standalone balance projection interface under ADR-0084.
The earlier projection-layout gap is superseded: retain calculations in Apply and
expandable explanations. Other incomplete management journeys remain open.

The user accepted shared accessibility behavior clarifications on 19 September:
result-heading focus, responsive field preservation, error navigation, consequential
status announcements and nonvisual calendar selection. A11Y-01–04 are addressed
in the design contracts; implementation and rendered accessibility verification
remain outstanding. No new screens or approval steps are introduced.

The user accepted shared collection/loading/empty/error/export behavior on
19 September. UX-R05 is addressed at design-contract level with Leave wording and
team-availability handling; runtime data contracts and rendered checks remain open.

The user accepted shared date-entry behavior and Leave duration composition on
19 September: unified full-day range with typed/calendar entry; one date for
half-day/hourly duration; incomplete/reversed-range feedback and a no-working-time
explanation. UX-R03 behavior gap is addressed; concrete control selection and
rendered verification remain delivery work.

The user selected Neutral + Quiet lagoon. Shared light-mode colour values are now
recorded in platform/DESIGN.md, with Leave inheriting without local overrides.
UX-R02 colour-palette gap is addressed; non-colour scales and unverified states
remain open. A softer-overlay preview was produced for visual review.

On 20 September the user selected the proposed type/control scale. Shared typography
and control minima are recorded in platform/DESIGN.md; Leave inherits them. The
reported Leave type visibility issue is not reproduced in a browser: markup retains
it first; comparison scroll reset and a dedicated selected reference mitigate
preview scroll/layout ambiguity. Rendered verification remains outstanding.

On 20 September the user selected Suggested in the layout comparison: standard
560px drawer, 32px desktop / 20px mobile horizontal padding, 24px section gaps and
vertical form padding, and retained 8px label gaps. Shared tokens are recorded;
selected-design.html combines approved palette/type/layout. Responsive thresholds,
additional variants and browser verification remain open.

On 20 September the user approved the dedicated policy-editor layout: four directly
reachable groups, expandable advanced rules, effective date/reason and changed-value
review. Conditional cap/carry-over/rounding controls and the real second-approver
picker remain incomplete. Approval of the layout does not approve sample defaults
or complete the policy field catalogue or runtime impact assessment.

The user approved conditional advanced-field behavior and the illustrative
strictly-greater-than document threshold example. Expiry input design and full
conditional layouts remain open; sample values are not jurisdiction defaults.

The user approved the second-step picker: search eligible current-NGO people with
identity context, no preselected CEO, explicit selection, empty-eligibility guidance
and authorized access-management navigation. Preview lookup is illustrative;
production permission enforcement is not implemented.

Setup layout approved with correction: consultant email-approval status and the
standard opening-balances row are removed. Email interaction stays operational;
Leave shows actual balances and detected data issues. The preview now has three
setup areas and two areas needing attention in the illustrative existing-data case.
This supersedes the earlier read-only consultant-status UI proposal.

On 20 September the user approved the employee Leave-settings layout and shared
identity explanation. The three groups, focused edits, distinct balance actions
and read-only visibility are captured in product truth/tracking. Runtime identity
contracts, impact calculations and browser/mobile routing verification remain open.

On 20 September the user approved work-profile list/edit/review, including separate
inherited effects, retained employee overrides and existing-request attention.
Profile creation/archive/default actions and actual impact calculation remain open.

On 20 September the user approved the balance-explanation layout: current balance
breakdown, separate pending reservations linked to requests, expandable entitlement
history with actor/reason and hours, and history-year filtering without changing
current balances. The arithmetic example reconciles; runtime and rendered
accessibility verification remain outstanding.

On 20 September the user approved the revised-unpaid acknowledgement preview:
before/after allocation, recorded actor explanation, exact-amount checkbox and
separate eligible withdrawal. Acknowledgement allows approval to continue; it is
not approval. Runtime amount revalidation and rendered checks remain outstanding.

On 20 September the user approved balance-deficit review: cause and before/after
balance, four existing outcomes, employee-visible explanation and reviewed
decision distinct from separately authorized adjustment. Browser/runtime checks
remain outstanding.

The user approved allocation review and reaffirmed one request with an explicit
paid/unpaid split. Paid entitlement remains constrained; additional paid funding
requires an authorized recorded exception. Discretionary grant amount is editable,
not fixed at one day. Full multi-source editing remains outside the preview.

The user approved the compact shared notification panel and full-width mobile
sheet: newest first, unread markers, minimal permitted context, secondary time
and active-NGO Mark all as read. Reading does not complete required actions.
Shared platform DESIGN/EXPERIENCE now hold this layout direction; no rendered
notification mock or runtime implementation is claimed.

The user approved stale-request presentation: confirmed withdrawal removes
approval actions and offers Back to approvals; an edited request requires Review
latest version. Unsent comments are preserved locally without automatic submission.
Shared behavior and Leave-specific copy are recorded; runtime concurrency and
rendered accessibility verification remain delivery work.

The user approved attachment feedback beneath Supporting document: uploading
with Cancel, failure with Retry/Remove and Attached with Remove. Failures preserve
form input; required files must be ready and optional failed files are not silently
omitted. Shared guidance and Leave inheritance updated; production upload behavior
and rendered accessibility remain unverified.

The user replaced automatic post-submit request details with automatic return to
My Leave after confirmed success, preserving context/scroll, brief confirmation
and optional View request, updated list status and removed draft indicator.
ADR-0087 partially supersedes immutable ADR-0070. Confirmed failure/unknown outcome
retain the form; check unknown outcomes before retry. Product truth, tracker and
UX focus/navigation contracts are synchronized. Runtime and rendered checks remain
outstanding; historical wireframes may still show the superseded success route.

The user approved My Leave partial-load behavior: independent section loading and
retry, retained usable authorized sections, no fabricated zero/empty results, and
Apply remaining available. Submission waits only if its required authoritative
calculation/checks cannot complete. Shared and Leave guidance updated; actual data
contracts, rendered states and runtime recovery remain delivery work.

The user selected light mode only for MVP. Shared theme direction and Leave DESIGN
record that dark mode is deferred, with semantic colours retained for future work.
The current IA coverage table now links the subsequently approved balance,
acknowledgement, deficit/allocation, policy, profile, setup and employee previews.
The older initial coverage snapshot above is historical. The user has not yet
confirmed which remaining surfaces may rely on written patterns without another
visual walkthrough.

The user confirmed the remaining walkthrough scope: Apply on behalf, then assigned
custom-role changes/deletion. Routine profile creation, archive confirmations,
temporary-approver changes and loading/error states may use the approved patterns
and written rules without extra mockups. This does not waive implementation or
verification, decide unspecified business rules, or finalize Phase 1 readiness.
The on-behalf preview is now linked and awaits feedback.

The user approved the on-behalf layout: employee first, separate recording actor,
required reason, review, and explicit distinction between submission-only and
satisfying the actor’s own assigned approval step. The assigned-custom-role
lifecycle preview is the final planned visual walkthrough and awaits feedback.

The user approved the assigned-custom-role lifecycle preview on 20 September:
capability additions/removals, affected holders, related-person navigation with
preserved edits, deletion blocked while assigned and separate unassigned deletion
confirmation. Both remaining requested visual walkthroughs are now approved.
Routine variants retain the previously accepted written-pattern coverage. This
closes the agreed walkthrough list, not the remaining token/contract questions,
final document validation, artifact promotion or implementation-readiness gate.

Post-review update: [review resolution](./review-resolution.md) records seven
findings addressed in documentation/reference source and two remaining decisions
(setup status criteria and shared visual defaults). Twenty-eight approved
composition references now have stable mockups links and an inventory; seven
comparison studies remain historical. Prototype accessibility fixes passed static
and simulated-handler checks, not browser/AT verification. Both spines remain draft.

UX-R10 resolved by user decision: setup status derives from saved settings and
validation (Not started, Needs review, Ready, Couldn’t check with Retry). People
stays Not started with no employees. Reassess affected sections on changes; no
manual completion or consultant-email state. Product requirements, tracker and
keeper copy updated. Only UX-R08 remains a user design decision; runtime assessment
and accessibility verification remain separate delivery work.

UX handoff finalized on 20 September 2026. All nine review findings have a recorded
source correction or approved decision; final structure/prose polish is applied.
The two Leave spines are final, 28 keepers are promoted, seven comparison studies
remain historical, and accepted written-pattern coverage is indexed. Phase 1 UX
task is complete; requirements validation, architecture, stories/readiness and
technical foundation remain. Source checks passed; browser/AT verification is not
claimed. See handoff-coverage.md and review-resolution.md for current disposition.
