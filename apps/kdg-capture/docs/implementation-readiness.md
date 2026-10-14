# KDG Capture — implementation readiness

Date: 2026-10-13. Installed gate: bmad-sprint-planning, readiness-only intent.
**Current verdict: FAIL — planning workflow and load-bearing prerequisites are incomplete.**
This is a planning finding, not a failed runtime test. No implementation is authorized.

## Inventory and gate findings

Focused PRD, both UX spines, architecture, proposed technical contracts, source-backed
discovery and 22 acceptance groups exist. Independent PRD, UX, architecture rubric,
adversarial, technology and editorial reviews were run; concrete findings are reconciled
in review-resolution.md. Architecture deterministic lint reports zero findings.

| Severity / gate | Evidence and required next action | Owning workflow/owner |
| --- | --- | --- |
| High — required BMAD epic checkpoint | epics.md contains 18 FR, 5 NFR, 14 UX items; requirements and five-epic structure approved; all seven E1 scopes/closure approved; all four E2 stories/closure approved; candidate 3.1 drafted; remaining story review/sizing and final completeness steps remain | bmad-create-epics-and-stories |
| High — shared ownership agreement | User appointed KDG coordinator; Leave acknowledgement/handoff and component-first-consumer ownership not yet agreed. No shared files changed | Coordinator + Leave/platform session |
| High — current Access / Identity variant | Current v1 does not support KDG; canonical v2, account-actor/membership evidence, exact KDG scope, registry/grant constraints and caller/consumer fixtures and narrow assignment target-verification path not implemented or finalized for this consumer | Existing Identity/Access owner; shared contract closure then bmad-build |
| High — controlled setup / scaffold readiness | Operator trust binding/commands, generator/recipe schema and compatible package/environment foundation are pending; a README is not a runnable command | Platform builder/environment + Identity/Access owners |
| Resolved — requested application policies | Administrator create-all, own history viewing/editing after unassignment, phone-local today, 30-day download and saving classification approved; child-deactivation historical editing approved with Story 2.2/A-6 | User agreement recorded in memlog/PRD |
| Medium — Story 1.5 rework | User rejected unfinished recovery; explicit Save scope/rationale recorded, explicit-Save Story 1.5 approved; implementation/readiness still gated | KDG UX/PRD/story planning |
| Medium — exact execution and sensitivity choices | Proposed limits/deadlines/fingerprint and local privacy/retention policy need review before affected story/pilot readiness | KDG contracts + platform owner |
| Release gate — provider/host/recovery | Verify supported sign-in/callback, HTTPS phone target, runtime/migration owner registration and backup/recovery targets before pilot; no production mutations now | Environment/release owners |

## Readiness scope and sequencing

KDG may complete its own planning without all Leave planning. Its first domain slice
requires only the bounded shared Identity/Access/scaffold/environment setup it consumes.
Do not depend on People, Content, notifications, complete Leave E1, hosted verification
application, a full questionnaire editor or automatic tenant enrollment.

Unavailable runtime dependencies are not proof that planning itself cannot finish:
owning prerequisite stories may be planned and approved first. Their concrete contracts
and shared handoff must be resolved before their Build gate, and runtime prerequisites
must be delivered/tested before the dependent server-backed KDG slice. No acceptance
test must already pass before writing authorized implementation; ATDD first observes the
expected failure in the owning story. Do not claim PASS merely because draft files exist.

Initial first slice is the user-requested sign-in → fixed Khula → published version/child
provision → offline capture → close/reopen/history → reconnect/idempotent sync → server
record, followed by early physical Android/iPhone proof. Detailed story sequencing is
approved at epic level in epics.md; story detailing remains in progress.

## Planning verification executed

- `git status --short`: original Leave/global-epic/PtS changes preserved; new KDG docs only.
- BMAD `resolve_config.py` and `resolve_customization.py` for applicable skills: read the
  installed catalog/workflow; no activation prepend/append overrides configured.
- BMAD `memlog.py init/append`: app-local audit created; no hand-edited memlog.
- `uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace apps/kdg-capture/docs`:
  PASS, zero findings. One cache-lock sandbox failure was rerun successfully through
  approved uv escalation; no dependencies were installed.
- Root `git diff --check`: reports pre-existing trailing whitespace in the unrelated
  `apps/pts/backend/acquisition_catalogue.json`. Do not fix that file in this task.
- App-owned link/whitespace scan after E3 candidate 3.1 drafting: 41 Markdown files, zero
  findings. E1 planning closed with seven approved stories; all four E2 stories/closure approved; six
  candidate 3.1 acceptance groups checked; 3.1 remains unapproved. Independent
  rechecks resolve material document findings in review-resolution.md. No runtime tests
  or physical-device checks ran.

## Next installed workflow

Continue bmad-create-epics-and-stories step 3 with E3 candidate 3.1 administrator-read review, then
remaining E3 stories and subsequent epics before final validation. Rerun bmad-sprint-planning readiness after blockers
are addressed; generate KDG-only tracking only on PASS. Stop for user review before any
Build. After approval and applicable prerequisite readiness, use installed bmad-build
full flow with ATDD outer loop and focused TDD. No alternate delivery lifecycle is added.

Earlier independent reviews assessed the old saving scope. Reconcile explicit Save at
final readiness; do not claim those reviews validate revised capture/queue criteria.
No implementation or runtime evidence has been produced.
