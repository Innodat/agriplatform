---
title: 'Compare up to four public passages without losing reading or writing context'
type: 'feature'
created: '2026-10-26'
status: 'in-review'
baseline_commit: 'fe3fb611f5d8f40be3e6954d768228726373e6f6'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/apps/scribeswell/docs/FOUR_PASSAGE_LAYOUT_V1.md'
  - '{project-root}/apps/scribeswell/docs/NOTE_REFERENCES_V1.md'
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The binary comparison reader cannot provide the approved four independently navigable passages or safely retain their public positions through browser navigation.

**Approach:** Deliver one stable-keyed public layout controller with one to four panes, semantic add/open/close/capacity actions and bounded validated URL/history recovery under CAP-6/ST-16/ST-31/ST-34. Keep current writing mounted.

## Boundaries & Constraints

**Always:** Preserve public reading/analysis, complete canonical ranges/reference-only entries, independent scroll/errors, exact origin identity, focus/IME and existing Studies lane/operation identity. Preserve dirty/concurrent README, canonical, Leave/KDG/platform work. ATDD outer, focused TDD inner; characterize risky refactoring first. Consume adopted FOUR_PASSAGE_LAYOUT_V1.md technical contracts.

**Never:** Private data in public URL/history; implicit replacement at capacity; final-pane closure; separate pane-history arrows; competing Access/Identity/Notification paths; layout-triggered note mutations. Tabs/per-tab associations/durable same-device restoration are subsequent deliveries, not removed requirements. No Leave/factory, native SQL/migrations/actual-owner/session integration, KDG55481/55482, live provider/activation/deployment or production mutation.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| One to three panes; Add versus Open beside | Insert adjacent to active; Add duplicates its full reference/opens picker; Cancel retains new pane. Beside opens supplied reference. Identical refs are independent. |
| Four panes; request another; Cancel or explicitly choose replacement | Name targets, never choose silently; Cancel changes nothing, selection replaces only chosen pane with fresh seek. No unavailable new-tab action. |
| Close any pane including active/final | Keep survivor identities/positions, active chooses nearest neighbor; hide and semantically refuse final close. No editor exit or data deletion. |
| Legacy/new/malformed links; ranges/reference-only | Closed codec retains valid legacy, new precedence and safe invalid default; malformed fallback stays uncollectable until valid navigation, no entry rewrite/fabricated corpus fetch. Preserve unrelated query/hash. |
| Navigate/add/close/replace; activate/scroll/type/tool; Back/Forward | Checkpoint public anchors then one push for deliberate transitions; other actions no push. Replay restores matching public context without push/private change; unrelated Router/user state survives. |
| Same reference twice, repeated Open, hidden pane or late chapter/morphology/seek/checkpoint | Exact pane/navigation/selection identity, once-per-generation ready/visible seek, no stale focus/tool activation or position rewind. |
| Three/four panes with tools, phone/reduced height; current unsent/composing/unknown save | Available-container geometry and named switcher preserve positions; reader layout changes preserve editor/IME/original operation. Viewport tests do not qualify actual phones. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `W=A/web/src`. `W/pages/ReaderPage.tsx`: replace binary URL/selection arithmetic; preserve focus clamp/Escape. `W/components/bible/PassagePane.tsx`: isolated hooks/scroll/ready seek; reuse BookChapterSelector startOpen/cancel. `VerseReader.tsx`: add one-based word-position metadata. `WordStudy.tsx`: semantic callbacks instead of opposite-pane arithmetic; retain origin header. `W/lib/passage-references.ts`: canonical validator. Existing Zod/Router suffice; contract defines native key/idx/usr preservation. Keep StudiesContext/editor outside pane lifecycles; do not refactor saving.

## Tasks & Acceptance

- [ ] `A/web/tests/reader.spec.cjs`, `personal-notes.spec.cjs`: characterize range/scroll/errors/late work/focus and editor/IME/operation identity before refactoring; observe runnable Add/four-pane acceptance reds.
- [ ] `W/lib/reader-layout.ts`, `W/hooks/useReaderWorkspace.ts` and focused browser codec/controller tests: red then implement closed URL/snapshot validation, legacy handling, bounds, Router push/checkpoint/replay and stale-entry guards; test non-record usr/default-key preservation.
- [x] `W/pages/ReaderPage.tsx`, `W/components/bible/{PassagePane,VerseReader,WordStudy}.tsx`: wire semantic actions, stable identity/provenance/scroll/seek, capacity/final-close guards and responsive grid/switcher. Retain mounted Studies/editor/account boundaries.
- [x] `A/web/tests/reader.spec.cjs`, `personal-notes.spec.cjs`, new focused codec/controller tests: cover matrix desktop/mobile, interleaved history/independent anchors/repeated Open/stale callbacks/short geometry. Change superseded Compare/emitted-wire assertions only with evidence.
- [x] `A/docs/FOUR_PASSAGE_LAYOUT_EVIDENCE.md`, adopted contract and delivery record: map requirements to tests, exact commands/results/chronology and scaffold/shared-UI/context/docs/ADR decisions. Do not mark final integration or device gates passed. Parent owns canonical/audit/reviews/checkpoint.

## Implementation Notes

Implemented the closed public codec and stable-keyed workspace controller, one-to-four
panes with complete-reference Add, semantic here/beside, explicit capacity replacement,
active target cue, nearest-survivor Close and final-close refusal. Router ownership,
foreign structured user state/default-key handling, bounded anchors/cache and repeated
POP recovery are retained. Available-container geometry and pre-paint ready targets
cooperate with focus restoration. Studies save lanes/editor remain outside pane lifecycles.

The first two chronology-bearing checklist items remain unchecked: codec/controller
drafts preceded focused tests, and only late-chapter/retry characterization plus the
missing-Add acceptance red preceded UI wiring. Later coverage is complete for the
bounded component matrix, but cannot repair that historical ordering. See the evidence
for every failed attempt, contaminated run, observed audit red and source-frozen result.
No frozen intent was changed.


## Spec Change Log

## Review Triage Log

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| B1 | medium | patch | add() unconditionally sets the duplicated pane valid and clears workspace.invalid; Add then picker Cancel serializes the display fallback as a valid requested layout. Retain unresolved-input provenance until actual valid passage selection/navigation while preserving Add/Cancel layout and history semantics. |
| B2 | medium | patch | ReaderPage observes grid dimensions only, so control wrapping/navigation-error height changes inside a fixed grid leave chrome stale. Qualify dynamic controls and preserve200px usable rows without a resize feedback loop. |
| B3 | medium | patch | PassagePane chooses anchor verse first; if absent, node is null and it seeks0 even when explicit targetVerse exists. get_verses validates present word sequences but does not require every canonical verse row, so this state is reachable. Follow anchor word/verse then explicit verse then chapter fallback. |
| B4 | medium | patch | close() only commits layout, and the Close button unmounts without focus handoff. No caller restores surviving reader focus. Preserve active survivor and move displaced keyboard focus to its appropriate control without extra history or stealing unrelated focus. |
| B5 | medium | patch | Checkpoint intent expires after1000ms; no pointermove/up/gesture-completion tracking renews a prolonged scrollbar drag, so late deliberate positions can remain absent from native refresh snapshot. Preserve latest gesture position under existing entry/geometry guards. Repeated touchmove itself already refreshes intent; not every touch motion is affected. |
| B6 | medium | patch | Referenced exact stdout logs exist only as ignored workspace files and are absent from the reviewable repository artifact; a repository-only handoff cannot retrieve them. Include this delivery's safe synthetic/public logs through a narrowly scoped ignore exception or durable equivalent. Preserve exact bytes/failed runs. |
| B7 | medium | patch-parent | Complete reviewed-source browser regression remains outstanding, as evidence expressly says. Parent runs all .spec suites once after corrections, freezes sources and records exact results; no wider worker rerun. This is an existing final-verification task, not a false prior green claim. |
| B8 | low | reject-low | The internal final-pane guard has no direct invocation test; actual controller returns before mutation when one pane remains and UI exposes no final Close/alternate command. Hidden final control is browser-tested and the guard's source-only coverage is disclosed. Adding a harness solely for this trivial internal guard creates complexity for an unreachable everyday UI path; do not claim direct invocation proof. |
| B9 | medium | patch | New editor/atom identity assertions do not inspect caret/range endpoints, despite the adopted preservation contract. Add actual retained selection/caret evidence across add/close/replay and composition completion; repair only a demonstrated failure using existing editor selection ownership. |
| B10 | low | patch | New codec/controller are already formatted, refuting that portion, but new matrix tests and added cases contain multi-kilobyte single lines. This impedes transition-order breakpoints and source diagnosis in the new history/geometry tests. Directly format new test code/added blocks; no helper framework or unrelated legacy reformat. |
| E1 | medium | patch | Independently identifies the same missing anchor-verse→explicit-start fallback as B3. Exact current branch chooses0 when anchor verse missing although explicit target exists; group only after retaining this individual row. |
| E2 | medium | patch | Independently identifies the same grid-only chrome observer as B2: control wrapping/errors can reduce text height without outer dimension change. Group only with that exact root. |
| V1 | medium | patch | Pre-verified regression gap accepted as filed: existing replay fixture has only position1 per verse; wrapped multiword focus case never executes history restore. Add wrapped-verse replay to a later source position distinct from DB ID and assert captured offset. |

All three context-free same-model review layers completed before triage. The third launch initially hit the agent thread limit and was retried when capacity released; no layer was skipped and no findings were processed before all three reported.13 individual rows precede grouping. B3/E1 and B2/E2 are the only shared roots.12 surviving rows form10 roots, including the parent's outstanding final browser verification; B8 is rejected under the low/complexity rule. No frozen-intent change or wire extension is authorized by these repairs.

Parent actual diff/matrix audit read all changed runtime/test sources plus app contracts/evidence against fe3fb611f5d8f40be3e6954d768228726373e6f6. Eight historical before/after hash pairs match; final10 runtime/test hashes match current files. Global160-source handoff inventory d6c1529d1bcb62167a8746e646a11aa219bbb1969ab1158e123f9af6ffcd45ef captured. The only runtime delta after the86-case84/2 run is exactly four spaces removed from one blank PassagePane line, independently reconstructed to its recorded SHA256. The54-pass selection and84 passing checks thus cover current functional sources; two withdrawn synthetic prepaint assertions remain disclosed failures. Chronology-bearing first two tasks stay unchecked rather than inventing prior test-first/pre-characterization evidence. Functional implementation proceeds to independent corrective review/final verification under the user's continuing authorization, with this non-remediable historical limitation retained and no final acceptance claimed.

### Additional parent coupling audit

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| P1 | medium | patch | `lib/account-entry.ts` publicAccountReturn permits only legacy fields. Deliberate four-pane actions now emit only reader, so signup emailRedirectTo loses the active public arrangement. Reuse the qualified closed public codec for valid new links, fixed origin/app-root and no private fields; invalid supplied new input cannot blend legacy. Preserve absent-reader legacy behavior. Observe intercepted signup red before implementation; no provider change. |

This is an additional parent finding after the three independent review layers,
not an invented reviewer result. Total14 individually triaged rows/11 surviving
roots including parent full regression,10 worker repair roots,1 low rejection.
The current focused run remains frozen; this repair starts only after it finishes.

### Inactive-pane gesture recheck

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| P2 | medium | patch, B5 root | Root capture pointerdown records gesture entry before inactive pane's React activation replaces the Router entry. After one second the captured entry mismatches, so final scroll/pointerup cannot checkpoint. Parent public-only probe reproduced expected verse8/offset−14 versus stored verse4/offset−6. Preserve ownership through activation-only identity transfer, while real navigation continues invalidating it. |

Retain this individual row before grouping P2 with the incomplete B5 repair.
Total15 rows/11 surviving roots,10 worker repairs including this reopened root,
1 parent full regression and1 low rejection. The680-case parent attempt was
intentionally stopped after the separate reproduced failure:302 passed/1 skipped/
2 interrupted/375 not run,5.3min, exit130;160-source hashes stayed frozen.
This is not a completed or failed-product full-suite result. Only the verified
owned Playwright descendant received graceful SIGINT; no shared process/port used.
Fresh full regression follows the correction; previous logs/manifests retained.

### Current-position resize race

| ID | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| P3 | medium | patch | Full686 run reproduced second clamp assertion: expected latest120, received old921. Public-only trace then reproduced exact sequence: latest setter120 precedes resize; native scroll arrives with changed height and moved() returns; Pane ResizeObserver explicitly reapplies old held921. Preserve a newer position while distinguishing native geometry clamp; keep original expectations and qualify real intermediate geometry. This does not establish the historical initial921→0 cause. |

P3 is a separate position-ownership defect from row-height measurement or missing
anchor fallback. Total16 individual rows/12 surviving roots:11 worker corrections,
parent full verification and1 low rejection. The current full run stays frozen
until completion; source/test repair follows its retained result. Three public
trace attempts yielded120,120,921; first two coalesced intermediate viewport layout
and therefore were not actual clamp-branch proof. Trace prototype instrumentation
can affect timing; the original uninstrumented full failure independently establishes
the defect. No sleep/expectation relaxation or source editing during this run.

## Verification

Parent final frozen component run: **686 passed / 2 expected native-browser skips,
13.5min**,688 registered cases across all five `.spec.cjs` suites. Command:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- --workers=2
```

The160-source before/after manifest matches, SHA256
`04b1c8998c46e4b2c29738836492c55ebf11e4f8e27d09980418eaa09718847d`.
Final TypeScript/Vite build passed1.86s (existing bundle advisory). Scoped source/docs
whitespace checks pass; exact raw artifact output is preserved. App evidence retains
all intermediate failures, contamination, interrupted680 attempt and failed686 run,
registered repair reds and final focused54/12/26/54 selections on their own hashes.

Three independent review layers and parent source/matrix audits complete:16 individual
rows/12 surviving roots,11 worker repairs plus parent full verification addressed;
one low guard-harness finding rejected with source-only limit disclosed. Source and
new matrix assertions were audited directly. Initial two chronology tasks remain
unchecked and no complete method-ordering claim is made. Historical initial921→0
cause remains unproven; latest120→921 cause was traced and deterministically fixed.

Scaffold/shared UI/agent context/ADR impact: no change; app docs/evidence and canonical
handoff updated. No backend/API/migration change or new Python execution. Delivery
stays in-review under the user's final-integration ordering, despite the generic
workflow's done default: actual native/owner/session/devices/signup/default Access/
release gates remain open. Local scoped checkpoint follows, no push. All11CAP/38ST
remain. Workspace tabs follow separately under the approved continuation.
