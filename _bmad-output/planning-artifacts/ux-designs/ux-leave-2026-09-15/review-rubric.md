# Spine Pair Review — Leave

Reviewed 20 September 2026. Scope: current Leave DESIGN.md and EXPERIENCE.md, inherited platform spines, product feature catalogue, relevant accepted decisions, and the approved walkthrough coverage. This replaces the 18 September rubric snapshot. This is a source review, not rendered-browser, keyboard, assistive-technology or implementation testing.

## Overall verdict

The approved employee, approval and management journeys now form a coherent design contract, including the previously missing allocation/acknowledgement, deficit, employee settings, on-behalf and role-lifecycle cases. Remaining findings concern a small set of unsettled visual defaults, one derived setup-status rule, ambiguous approval-gating wording and document handoff hygiene; they do not justify reopening approved layouts or demanding more routine mockups. The spines should remain draft until these handoff decisions are resolved; runtime contracts and browser verification remain separate delivery work.

Counts: **0 critical, 0 high, 4 medium, 2 low**. Severity describes downstream impact, not implementation readiness. The earlier palette, administrative persistence and period-boundary findings are resolved at design-contract level.

Locations below are relative to this workspace unless prefixed with a repository path. Line numbers refer to this review's source snapshot.

## 1. Flow coverage — adequate

Extracted all twenty feature-catalogue headings plus Permissions from `apps/leave/docs/features.md`, using the source-to-flow mapping in consolidation-coverage.md:40–63. EXPERIENCE.md:1321–1460 contains sixteen numbered flows plus Flow 3a, with named participants, numbered steps, climax and failure/limits. Sources supply no UJ IDs. Features such as hourly leave, attachments, final-step context and insufficient-balance override are incorporated into relevant journeys rather than requiring duplicate flows for each heading.

The current component sections additionally cover employee settings, apply on behalf, profile lifecycle, deficit outcomes, exact-amount acknowledgement, policy publication and role deletion. Organization/team/location administration and detailed policy calculation contracts remain partial or source-owned; this is disclosed, not evidence of completed delivery. The user accepted written-pattern coverage for routine profile creation/archive, temporary-approver variants and loading/error variants. No new visual walkthrough is required by this review.

No additional flow finding. ADR-0087 and EXPERIENCE.md:1207–1223/1321–1328 correctly make confirmed submission return to My Leave. One mixed paid/unpaid request remains explicit in EXPERIENCE.md:405–410; acknowledgement does not authorize extra paid entitlement.

## 2. Token completeness — thin

The empty Leave token maps are valid inheritance, not missing colour specifications: DESIGN.md:35–44 names the shared tokens, and platform/DESIGN.md:7–50 supplies ten hex colours, six typography roles, five spacing defaults and drawer/control dimensions. No `{path.to.token}` references dangle. Body font inheritance is explicit. Light-mode-only is accepted; absence of dark tokens is not a gap. The text/primary/emphasis contrast pairs are recorded, and WCAG 2.2 AA is a target rather than a claim of rendered compliance.

### Findings

- **[medium] UX-R08 — Remaining visual defaults have no committed inheritance source.** DESIGN.md:98–109 explicitly leaves shadow/elevation, corner radii, icon family and marker geometry uncommitted; platform/DESIGN.md:102–107 leaves drawer overlay/shadow values unresolved. EXPERIENCE.md:17–20 says no specific component library has been selected, so “familiar controls” cannot resolve those values by inheritance. *Fix:* choose a small shared default set or identify a concrete approved primitive/theme that owns it, then name only Leave-specific deltas. Do not copy incidental prototype CSS wholesale. Content-driven responsive thresholds may remain rendered-validation work; no new dark theme or width catalogue is needed.

## 3. Component coverage — adequate

Extracted 27 component-pattern headings from EXPERIENCE.md:90–1013. Twenty-six have matching DESIGN Components rows with real composition rules; shared primitives have explicit platform references. Date/duration entry, upload feedback, administrative persistence and notification behavior now have reusable contracts. More granular component implementation remains delivery work, not a demand for a separate row for every native input.

### Findings

- **[low] UX-R09 — Apply on behalf is missing from the visual component table.** EXPERIENCE.md:641 names this composite, but DESIGN.md:118–145 has no corresponding row despite claiming name correspondence at lines 113–116. The approved visual rules exist in prose at DESIGN.md:154–160, so this is an extraction/index defect rather than an absent design. *Fix:* add the matching row pointing to the existing approved preview and its employee/recording-actor/review hierarchy; avoid duplicating the narrative.

## 4. State coverage — adequate

Walked the IA surfaces at EXPERIENCE.md:42–66 against the state matrix at lines 1022–1032 and the detailed patterns through line 1240. Current contracts cover empty versus filtered-empty versus failed loads, independent My Leave sections, expired sessions, no access, autosave recovery, stale records, uncertain mutations, upload failure, exact acknowledgement, withdrawal/cancellation and export recovery. Shared administrative Edit → Review → Confirm and leave/discard behavior are committed in platform/EXPERIENCE.md:256–272. Routine variants can inherit these rules under the user's accepted coverage choice; lack of separate rendered examples is not a state-design defect.

### Findings

- **[medium] UX-R10 — Setup status needs a rule for when it becomes Ready.** EXPERIENCE.md:926–940 requires completion/unresolved-issue status, but the state matrix explicitly leaves “Checklist failures/completion criteria” open at line 1032. The approved setup preview illustrates Ready/Needs review/Not started and says progress derives from underlying settings with no separate completion action. Neither spine defines how having a saved calendar/profile is distinguished from its rules being reviewed for this NGO; policy guidance also requires client confirmation at lines 742–748. *Fix:* document a concise predicate or source of truth for each of the three checklist statuses, including incomplete/unavailable assessment. Tie status to existing settings/review evidence; do not introduce a client email workflow, separate activation button, or mark-complete mechanism. Database/API realization remains architecture work.

## 5. Visual reference coverage — thin

All 35 `.working/*.html` files are linked by at least one spine and described in context; no orphan working HTML was found. There are no files under mockups/, wireframes/ or imports/. All 110 relative Markdown file links across the four spines resolve in the parent mechanical check. EXPERIENCE.md:25–28 clearly states presentation precedence and the authority of product requirements/accepted ADRs. Historical colour/layout comparisons are identified as alternatives, not competing selected designs.

### Findings

- **[medium] UX-R11 — Approved visual references have not been promoted for handoff.** DESIGN.md:46–96 and 118–191 and EXPERIENCE.md's IA table still point exclusively into `.working/`, including selected-design.html and the approved final on-behalf/role-lifecycle references. The coverage document still explicitly records no promotion, while its final entries now close the approved walkthrough list. *Fix:* promote the approved keeper set to stable mockups/ or wireframes/ destinations and update links; retain historical studies separately with their status explicit. Include a short inventory distinguishing approved composition, historical comparison and accepted spine-only coverage. This is artifact organization, not a request to redraw or browser-approve every mock.

## 6. Bloat & overspecification — adequate

Most detailed prose preserves consequential domain distinctions. Repetition between a canonical component rule and a short illustrative flow is useful; repeating historical approval commentary and obsolete open-item labels is less useful. The spines correctly avoid elevating all sample CSS/data into requirements.

### Findings

- **[low] UX-R12 — Stale status prose obscures which decisions remain open.** DESIGN.md:57 says dark mode still needs resolution after light-only was selected at lines 35–38; platform/DESIGN.md:75–76 repeats this. EXPERIENCE.md:140 says widths remain open despite the selected standard 560px width, and platform/EXPERIENCE.md:366 similarly leaves drawer dimensions open. DESIGN.md:143 calls setup spine-only although its approved preview is described at lines 169–177. The state matrix at EXPERIENCE.md:1025–1032 still lists some extra layouts as unresolved without distinguishing the accepted no-further-mockup choice. Policy configuration also repeats review/publication rules at lines 802–827. *Fix:* consolidate current status in the IA/state inventory, replace obsolete statements with the precise remaining validation/architecture work, and retain decision history in the memlog/coverage record. Do not reinterpret deferred dark mode or accepted written-pattern coverage as unfinished user decisions.

## 7. Inheritance discipline — adequate

All source paths resolve; both spines reference the authoritative feature catalogue and accepted ADR collection. The named roles, employee identity boundary, NGO scope, temporary authority, separate sensitive-document permission and recurring period-boundary decision are consistently inherited. Shared UI is described as planned, not implemented, and application business rules are not moved into a shared runtime by implication. No token-name resolution errors were found.

### Findings

- **[medium] UX-R13 — Renewed acknowledgement ambiguously blocks all approval rather than final approval.** EXPERIENCE.md:413–417 says the approver “cannot complete approval” until acknowledgement, and Flow 3a:1351–1354 implies the remaining workflow resumes only afterward. By contrast EXPERIENCE.md:359–363, `apps/leave/docs/features.md`:714–739 and accepted ADR-0032 explicitly gate **final approval**, preserving prior decisions. In a two-step workflow, consumers could interpret the less precise wording as also disabling an outstanding intermediate decision. *Fix:* use “final approval cannot complete” consistently and state the behavior of remaining intermediate steps by reference to the accepted finalization rule. If the intended restriction is actually broader, obtain an explicit product decision rather than expanding the gate through copy. This is a design-contract wording ambiguity, not a demonstrated runtime bug.

## 8. Shape fit — strong

Leave DESIGN uses canonical order: Brand & Style, Colors, Typography, Layout & Spacing, Elevation & Depth, Shapes, Components, Do's and Don'ts. EXPERIENCE contains every required default plus Responsive & Platform and Inspiration & Anti-patterns. The latter records relevant rejected patterns without inventing external products as visual authorities. Coverage and migration documents earn their separate place; no extra client-facing import screen or new personas are needed.

## Mechanical notes

- Read the rubric, design-md-spec and all three design/two experience examples before review.
- Read current Leave/shared spines, feature headings and relevant detailed requirements, coverage updates and ADR-0032/0087 context.
- Twenty-seven component headings; one missing matching visual table row, with its visual prose already present.
- Thirty-five working HTML references; all linked from at least one spine. No promoted mockups/wireframes/imports.
- Parent verified 110 relative Markdown file links across Leave/shared spines; all resolve. Source paths resolve. No token-path or Mermaid syntax defects found.
- Numerical contrast evidence is limited to the recorded pairs; no browser, keyboard or assistive-technology verification is implied.
- No finding asks for deferred dark mode, a future balance calculator, a generic task inbox, new routine mockups, a client migration-confirmation page or premature Leave implementation.
- Current draft labels and the Phase 1 implementation-readiness gate remain appropriate. Runtime concurrency, exact schema, permission catalogue, calendar arithmetic and rendered accessibility are deliberately separate implementation/architecture work.
