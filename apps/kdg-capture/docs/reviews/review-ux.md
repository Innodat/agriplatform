# KDG Capture — UX coverage and accessibility review

Date: 2026-10-12. Scope: repository-only inspection of `prd.md`, `DESIGN.md`,
`EXPERIENCE.md`, the original agreed request and subsequent approved Nee default,
seven-day offline window and fixed Khula organization. Lens: BMAD UX validation
coverage, IA state closure and accessibility. No runtime, contrast measurement,
screen-reader or physical-device checks were performed. Spines were not edited.

## Verdict

Core capture, historical versions, truthful local save, explicit conflict resolution,
fixed organization and online-only administration are adequately represented. The
spines are usable for planning, but visual inheritance, surface states and component
closure need refinement before their consuming stories are implementation-ready.
The draft saving classification remains explicitly proposed, not user-approved.

| Category | Verdict |
| --- | --- |
| Flow coverage | adequate |
| Token completeness | thin |
| Component coverage | thin |
| State coverage | thin |
| Visual reference coverage | strong: no visual assets claimed |
| Bloat and overspecification | strong |
| Inheritance discipline | adequate |
| Shape fit | adequate |
| Accessibility specification | adequate, with open verification and language rules |

Findings: 0 critical, 2 high, 4 medium, 1 low. These are document gaps, not evidence
of defects in an implemented application.

## Findings

### High

1. **Inherited visual tokens lack a resolvable owner source.** `DESIGN.md:8,35–41,65`
   names shadcn semantic tokens but does not identify the selected repository stylesheet,
   version or supported theme. shadcn inheritance is allowed by BMAD's design spec;
   it is not a selected universal palette. Contrast remains unmeasurable from this
   contract. Fix: select and link an actual authoritative token set, list semantic
   mappings including focus/selected/error states, declare the supported theme, and
   specify contrast targets for text and necessary non-text controls. Do not invent
   a new brand palette or claim the inherited defaults pass. No new literal color
   token is declared, so the missing-hex rule does not itself create a critical finding.

2. **IA surface state closure is incomplete.** `EXPERIENCE.md:23–30,76–91` has useful
   global reliability states, but no complete cold-load/empty/failure/denial outcomes
   for history, questionnaire administration or child/facilitator assignment forms.
   PRD FR-4 explicitly identifies no assigned child, which is absent from the state
   table. Fix: add compact per-surface state rules following the closure table below;
   distinguish a genuine empty result from a failed/incomplete download.

### Medium

3. **Component visual/behavior counterparts are uneven.** `DESIGN.md:70–76` lists
   History row, Revision comparison and Admin question editor; `EXPERIENCE.md:53–74`
   covers their semantics elsewhere but gives no named component rules for selection,
   revision comparison or reorder focus. Child/date controls, dialogs and assignment
   forms have no explicit visual counterpart. Fix: use matching compact component
   rows in both spines. Include accessible history activation, retained scroll/focus
   on return, labeled local/base/server comparison, reorder feedback and error states.

4. **Accessible mixed-language handling is unspecified.** `EXPERIENCE.md:39–41,109–114`
   deliberately retains English operational text alongside Afrikaans questions. Fix:
   identify page language and `lang` for differing questionnaire/status passages so
   TalkBack/VoiceOver pronounce Afrikaans correctly; required/optional indications
   and error association must use accessible text, not color or an unexplained symbol.
   Content approval remains separate from implementation verification.

5. **Admin assignment journey lacks a concrete success/failure beat.** All three PRD
   UJs appear at `EXPERIENCE.md:118–132`, but FR-12's managing children/facilitator
   assignments has only an IA entry. Fix: add a short named administrator flow covering
   verified eligible account selection, staged Save/Cancel, confirmed saved assignment,
   invalid/revoked eligibility and retry without accidental duplicate association.
   State explicitly that assignment creates neither membership nor Access grants.

6. **Interrupted local schema migration lacks a user-facing state.** PRD FR-18 names
   incompatible/interrupted migration and `EXPERIENCE.md:90` only addresses update
   availability. Fix: define a safe blocked-update/retry presentation which preserves
   pending work, does not claim save/sync success and does not recommend clearing
   storage as recovery. Link actual migration fixtures in the consuming story.

### Low

7. **Key flows use arrow prose rather than BMAD's numbered steps.**
   `EXPERIENCE.md:118–132` names the protagonist and meaningful success/failure beats;
   coverage is present, but downstream acceptance extraction would be clearer with
   numbered steps, especially the separate local/server acknowledgements in UJ-1.
   Fix: number existing beats without expanding requirements discovery.

## IA surface closure

| Surface | Covered | Missing or requiring explicit closure |
| --- | --- | --- |
| Sign-in/setup | online prerequisite, fixed Khula, expiry, unavailable authorization, partition isolation | setup progress/interrupted download, confirmed wrong-org/denied state, retry without partial setup acknowledgement |
| Capture | radio defaults, details, sole/multiple child, same-day offer, local save, quota, exit flush | no assigned child, questionnaire download incomplete, required-input error presentation |
| History | own/admin scope, partial offline corpus, never-downloaded notice | real empty history, cold-load/progress, failed online page/download, accessible row/open/return behavior |
| Record details/edit | original version/owner, local Save/Cancel, revision conflict | record not downloaded/missing, current denial, visible creation/editor/revision-history arrangement |
| Sync status/attention | meaningful status, pending outcome, expired session, denied assignment, manual trigger | empty queue/sync progress, per-item retry/action placement, resolved item focus/announcement |
| Conflict review | local/base/server retention, fresh revision, explicit resolution, repeated conflict | base visibly named in visual comparison, server fetch unavailable, permission loss while reviewing, focus after another conflict |
| Questionnaire list/editor | draft Save/Cancel, reviewed Publish, immutable versions, type/reorder/retire | empty/cold-load/failure/denial, draft validation, publish failure recovery and reorder focus/announcement |
| Children/facilitator assignments | online portal, verified account/child, no implicit grants | empty/failed eligibility list, no eligible facilitators, changed eligibility on Save, staged changes/discard, success feedback |

## Requirement coverage and approval reconciliation

- FR-1–3 and FR-13/16/17: fixed Khula with no switcher is preserved; first setup
  online and seven-day local use do not grant server authority. Reauthentication,
  known revocation and locked pending data remain distinct. No employment dependency.
- FR-4–7: exact brand strings, single scrolling form, six scores, Nee default,
  optional details, local-only duplicate offer and transactional save feedback are
  covered. Nee is the approved clarification; do not restore the original conflicting
  requirement of initially unanswered boolean choices.
- FR-8/9/11: own/all-permitted history, original-questionnaire editing, immutable
  version pinning and preserved conflicting inputs are covered. No offline history
  guarantee or silent version migration appears.
- FR-10/12: bounded editor and online assignment surface are covered; administration
  has the state/journey gaps above. No supervisor, public distribution or analytics.
- FR-14/15/18: foreground/manual sync, truthful states, retained pending work and
  eviction limitations are covered; migration-state closure remains open.
- PRD A-1–5 remain assumptions requiring their stated consumption gates. In particular,
  administrator create scope, post-unassignment historical rights, local-date default,
  saving classification and 30-day history cache are not silently approved by this review.

## Accessibility and verification closure

Strong planned rules: 48px controls, fieldset/legend radios, non-color status, visible
focus, preserved focus on details expansion, native keyboard controls, focus-managed
dialogs, non-drag reorder alternative, 320px/200% layouts, and safe-area/keyboard
reachability. Add language rules, actual inherited token references, explicit contrast
targets and surface/component focus behavior as above.

Automated future checks: labels/roles/states, keyboard operation, error associations,
no hidden-detail submission, layout/reflow, focus restoration, meaningful status
announcements and token contrast checks against implemented styles. Physical checks:
installed Android/iPhone offline reopen, TalkBack/VoiceOver pronunciation and controls,
keyboard/safe-area reachability, text scaling and update/recovery behavior. Emulated
browser results must not substitute for these physical checks.

## Mechanical notes

Frontmatter sources resolve locally. All explicit `{typography.*}` and `{spacing.*}`
references resolve in DESIGN frontmatter, including EXPERIENCE's control minimum.
Canonical DESIGN section order and EXPERIENCE defaults are present; Responsive &
Platform is included. No Mermaid, orphaned visual assets or external mock references
appear in the reviewed spines. Exact visual assets are optional, and their absence
alone is not a readiness failure.
