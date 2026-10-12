# Leave planning handoff — E3

**Checkpoint:** 2026-10-12. This is a navigation/handoff note, not a new feature spec,
architecture or implementation permission. Re-read current working-tree authority and
resolve later changes from their owners rather than treating this snapshot as superior.

## Resume point

**Later checkpoint — 2026-10-12:** The user has now approved the nine E3 delivery
groups with two clarifications: group 2 covers policy applicability/assignment/settings,
while group 7 owns recurring override mutations; every policy/entitlement mutation
requiring notification follows group 5's business-delivery foundation. See the current
epics and implementation plan. The earlier proposal/new-session text below is historical
at this point. Continue with collaborative Story 3.1 discussion; no individual E3 story,
final sizing/coverage, readiness PASS or implementation authorization is established.

**Story checkpoint — 2026-10-12:** Story 3.1 create/view organization leave types is
now agreed and recorded in epics. Its clarified criterion permits selecting a newly
created type and saving unfinished draft input without bypassing later policy/eligibility
checks. Continue with Story 3.2 discussion; technical contracts, source/test mapping,
final sizing and readiness remain open.

**Story checkpoint — 2026-10-12:** Story 3.2 policy summary/version history is now
agreed and recorded in epics. Continue at Story 3.3 discussion. Its controlled owner
fixtures avoid a future editor/calculator dependency; read/date/disclosure contracts,
test mapping, final sizing and readiness remain open.

**Story checkpoint — 2026-10-12:** Story 3.3 initial policy configuration/publication
for an unused type is now agreed. Contract terminology retained after explanation;
complete field/validation/publication contracts and final agent sizing remain open.
Continue at Story 3.4 discussion; no code or readiness authorization.

**Story checkpoint — 2026-10-12:** Story 3.4 reviewed starter examples is now agreed,
with concise example labelling and authorized Leave Manager confirmation in the existing
publication review. E3 has four agreed discussion scopes; continue to group 2 at Story
3.5 discussion. Exact contracts, source/test coverage, final sizing and readiness remain open.

**Story checkpoint — 2026-10-12:** Story 3.5 employee policy applicability explanations
is now agreed. Reject conflicting applicability at save; dependency outages produce
Couldn't check / Retry, not ineligibility. Continue at Story 3.6 discussion; matching,
input ownership/tenure/date contracts, source/test coverage, sizing and readiness remain open.

**Later decision — 2026-10-12:** User approved filters plus explicit policy assignment
for MVP under Leave ADR-0126, deferring automatic eligibility. Current features/spine/UX/
tracker and epics record the amendment to Stories 3.3/3.5. Filters/fact changes/new employees
do not silently alter assignments; backend enforcement and consequential effect/history/
notification protections remain. Continue Story 3.6 discussion with this authority; all
contract/test/sizing/readiness gates remain open.

**Story checkpoint — 2026-10-12:** Story 3.6 policy employee list/filter/selection is
agreed. Continue with bounded working-time/calculation Story 3.7 discussion. Committing
assignments remains a separate group 2 write obligation after required calculation/
notification foundations; group 2 mutations are not declared complete. Six E3 discussion
scopes agreed, with technical/test/sizing/readiness gates still open.

**Story checkpoint — 2026-10-12:** Story 3.7 effective-schedule duration calculation
is agreed. Continue at Story 3.8 discussion. Seven E3 discussion scopes agreed; all
technical/test/sizing/readiness gates remain open. Preview and consequential aggregate
daily-capacity enforcement retain later owners; no runtime implementation/tests.

**Story checkpoint — 2026-10-12:** Story 3.8 daily earning component is agreed.
Continue at Story 3.9 discussion. Eight E3 discussion scopes agreed; precise earning
components still need cap/expiry/actual-event consumers before available-balance claims.
All contract/test/sizing/readiness gates remain open; no implementation/tests.

**Story checkpoint — 2026-10-12:** Story 3.9 ordered immutable actual balance history
is agreed. Continue at Story 3.10 discussion. Nine E3 discussion scopes agreed; actual
mutation consumers still own their domain/evidence/notification safeguards. No generic
event API, ledger editor, posted accrual or implementation/readiness permission.

**Story checkpoint — 2026-10-12:** Story 3.10 daily accumulated-cap calculation is
agreed, including the explained pending-request reservation/consumption distinction.
Continue at Story 3.11 discussion. Ten E3 scopes agreed; actual expiry/rollover and
request-producer integrations, exact contracts/test coverage/sizing/readiness remain open.

Continue the already invoked bmad-create-epics-and-stories collaboratively, in its current
story-generation step. Eight epic groupings/delivery sequence were approved, including
E5. E1 has 24 agreed candidate scopes; E2 has 26 agreed story scopes. Their detailed
technical inputs, final source/test coverage and agent-size validation remain pending.
The nine E3 delivery groups were proposed at the end of the previous session and have
NOT yet been approved; begin by confirming/refining that sequence, then detail Story 3.1.
E4–E8 still need individual story decomposition. Do not restart the approved architecture
consolidation/review or repeat settled behavior decisions as new questions.

No SP readiness PASS, finalized global atomic requirement inventory or completed workflow
steps is established by those counts. Do not set stepsCompleted to completed merely from
this handoff. Source-indexed inventories and historical candidate labels remain proposals;
finalize numbering/dependencies/sizing and pre-story inputs before affected implementation.

## Read first, using current files and their references

1. Root AGENTS.md and applicable nested instructions.
2. apps/leave/docs/features.md — authoritative product requirements.
3. apps/leave/docs/architecture/ARCHITECTURE-SPINE.md — consistency/contract gates.
4. apps/leave/docs/implementation-plan.md — authoritative delivery tracker/gate timing.
5. _bmad-output/planning-artifacts/epics.md — approved scope/discussion and E3 proposal.
6. Platform and Leave accepted ADR indexes, then referenced decisions/owner contracts.
7. Platform DESIGN.md/EXPERIENCE.md and
   _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/{DESIGN,EXPERIENCE,handoff-coverage}.md.
8. Existing identity/admission/provisioning/content/reference scaffold contracts and
   apps/leave/docs/testing/e1-acceptance-map.md plus e1-environment-and-dependencies.md
   as relevant to dependencies; platform/builder-cli/README.md for actual scaffold state.

Follow accepted ADR references, including platform ADR-0038 finalized-byte identity.
Latest relevant additions at this checkpoint are platform 0057 (invitation/trusted tenant
admission), 0058 (explicit access prepared before first sign-in), 0059 (thin scaffold JSON)
and Leave 0125 (supervisor-derived teams). Accepted predecessors are immutable; historical
text/preview counts do not override linked newer decisions. Exact production state is
not inferred from code/templates or this handoff.

## Decisions to carry forward without rediscovery

- General tenant is organization, never NGO in generic code. Nonprofit/Christian Africa
  is the user's vision/market focus; accepted support includes other organization types.
- Identity owns person/account/membership/actor attribution. People is shared employment
  HTTP service, not an imported module/second Leave employee directory. One enduring
  employment per person/organization with periods; accountless employees supported.
- Shared optional department/location/supervisor are People facts. Department/location
  current changes apply on Save with server-recorded history, no scheduling UI. Simple
  Active/Inactive presentation where appropriate, retained actor/time/reference evidence.
- Leave MVP teams are supervisor direct reports. Named/project teams and team-profile
  defaults are deferred. Grouping never grants data/approval rights or reroutes requests.
- New membership on re-admission means a new access relationship, not a new person/login/
  employment. Old grants do not resume; old retries cannot affect replacement membership.
- Normal organization onboarding is invitation-based until verified Entra tenant enrollment
  is explicitly enabled, default off. Enrollment creates no roles/employment by itself.
  Explicit administrator-prepared roles can activate automatically after verified admission;
  mismatched/withdrawn/changed approval stays pending/needs review. No email-only binding.
- Current PtS capabilities are account-scoped; Scribeswell is public at scribeswell.com,
  shown in the launcher only with current PtS account access. No Scribeswell Boabab alias.
  Frontends share npm workspace/root-lock direction but have independent publication.
- Application permissions are independent explicit capabilities; actual action/ownership
  checks remain current. Role assignment uses shared desktop right drawer/mobile full-screen
  sheet; role definitions use a dedicated editor. Equivalent other grants remain on removal.
- Supervisor selection records actual reporting facts, not implicit Leave roles. Leave
  shows approval eligibility guidance. New submissions resolve/snapshot the eligible route;
  pending/completed steps require explicit reasoned rerouting. Focused Replace supervisor
  acts on selected employees with review/effective date, not a general bulk spreadsheet.
- Mutable records use current creation/update actor/time; consequential changes have compact
  owner-local immutable events in the same transaction. Common scaffold envelope/writer/
  typed event pattern, one People employment-change family, no duplicate audit/activity or
  universal runtime audit server/whole-payload capture. Actual outcome receipts remain distinct.
- Work profiles/calendars/versioned settings are Leave-owned. Net working hours are default;
  detailed work/break timetable is Advanced. Standard-day conversion differs from daily
  working hours. Schedule versions preserve earlier applicable settings; submitted results
  keep snapshots. Explicit profiles/overrides survive defaults/profile switches; per-field
  Reset returns to inheritance. Deactivation respects current/scheduled/default dependencies.
- Leave setup derives section badges from actual configuration/API observations, not stored
  manual ready flags. Reuse existing forms/drawers. E2 provides its current sections; E3
  adds real policy/entitlement assessment and employee-summary entitlement group. Employee
  summary lives in Leave → Manage Leave → Employees → employee → Leave settings, with
  permitted links from shared People and Leave setup.
- Saving convention: whole-form explicit Save/Cancel for business settings; request draft
  autosave plus separate submission; immediate simple personal preferences on separate
  surfaces. Inline/drawer/page is presentation, not a fourth persistence category.
- First Leave slice remains sign in → select organization → create/resume draft → autosave
  → close → reopen. Preserve input beyond selected dates; light preservation independent
  of setup, authorized obsolete-choice clearing with notice, no administrator-contact burden
  solely to save. Draft failure is inline Changes not saved/Retry; unconfirmed exit only
  Stay/Close anyway (switch: Stay/Switch anyway). Ordinary autosave uses attribution/outcomes,
  not duplicate audit logs; discard/closed lifecycle prevents resurrection.
- One maintained platform reference test/demo app: REF first create/read proof then VERIFY
  hosted paths; added examples follow proven consumers. Actual app synthetic journeys run
  in actual apps with dedicated scoped test accounts/data. No fake domain implementation.
- Thin schema-validated scaffold JSON records approved pattern/scope/history/saving/source
  choices; specs/ADRs/UX remain authority. Exact schema/generator is not implemented. Prove
  required behavior/generation with tests, preserve custom extensions. Builder is a placeholder;
  do not claim runnable CLI/validators from README sketches.
- Naming exploration is parked. No brand/domain rename is authorized.

## Proposed E3 delivery sequence — confirm before individual stories

1. Leave types/initial versioned policies, including required request/eligibility/privacy/
   document/approval-rule configuration and reviewed starter examples.
2. Policy applicability and employee policy/entitlement settings.
3. Authoritative working-time/earning/events/balance rules, decomposed into bounded stories.
4. Date-by-date projection/allocation and request preview, with no reservation effects.
5. Required first business-notification/outbox/worker foundation.
6. One-off Add/Deduct adjustment, reason/date/review, immutable effects and employee notification.
7. Recurring entitlement override/return to policy at correct leave-period boundary.
8. Employee balance explanations plus real E3 setup/employee-summary extension.
9. Used-policy/type edit/deactivation with actual impact/version/history protection.

These are discussion groups, not nine agent-sized stories. Use existing BIZ/CALC/FLOW/PRIV
inventories and exact feature/ADR acceptance examples without recreating business truth.
E5 owns submission/reservations/approvals; E6 broader historical corrections; E8 import/pilot.
Do not postpone notifications required by E3 mutations or introduce worker-posted daily
accrual, speculative balance-cache/HR/workflow engines or inferred legal defaults.

## First code and parallel-app boundaries

The current Leave plan is not implementation-ready. Complete required planning/contracts,
final source coverage/sizing and bmad-sprint-planning PASS before bmad-build implementation.
The first planned E1 implementation items are ENV/P1/SERVICE and Identity/Access foundations,
not entitlement UI. Runtime acceptance/CI/provider evidence belongs to authorized delivery;
do not demand finished application code as proof before its implementation gate.

User is considering a much smaller app in parallel. Its purpose/scope has not been supplied,
and no app/worktree/readiness/implementation scope was created here. Recommend separate
Codex sessions/worktrees with its own proportionate approved planning/readiness. It may
prove shared foundations needed by both apps after its own authorization; it cannot treat
Leave's blocked/unfinished contracts as already working or invent a second scaffold/identity
stack. Do not silently replace Leave's agreed first slice or bypass its gates.

Worktree creation starts from committed state and does not automatically copy these
uncommitted planning edits. First preserve a reviewed common baseline or explicitly carry
approved docs into the other worktree. Separate app-owned changes and one coordinated owner
for shared manifests/templates/ADRs/AGENTS/services; reconcile shared adoption notes/tests.
Never reset/revert unrelated working-tree changes. No commit, merge, deploy or production
mutation was requested/performed in this handoff.

## Copyable new-session prompt

```text
Use bmad-create-epics-and-stories to resume Leave story planning at E3.

Read AGENTS.md, then apps/leave/docs/planning-handoff-e3.md, and follow its
references to the current feature specification, architecture spine, delivery
tracker, epics, accepted platform/Leave ADRs and approved UX.
Use current working-tree files, including uncommitted changes.

E1 has 24 agreed candidate scopes and E2 has 26 agreed story scopes.
E3's proposed nine delivery groups are not yet approved. Start by confirming
or refining that sequence, then detail stories collaboratively one at a time.
Do not restart architecture consolidation or re-open settled decisions.

Preserve authoritative documents and requirement/test traceability. Retain the
first slice: sign in → select organization → create/resume draft → autosave
→ close → reopen. Explicit pre-story contracts, final sizing/coverage and BMAD
implementation-readiness gates remain binding. Do not implement application
code, run migrations, change providers, or deploy during this planning scope.

Record scaffold/shared UI/agent/docs/ADR impacts and updates with decisions.
Make routine technical choices within approved constraints; raise meaningful
business/security/ownership changes for discussion. Naming is parked.
A smaller app may be planned separately; coordinate shared platform contracts
rather than assuming unimplemented scaffolding/services exist.
```
