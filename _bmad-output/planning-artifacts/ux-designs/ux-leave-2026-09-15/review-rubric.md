# Spine Pair Review — Leave

Reviewed 18 September 2026. Scope: the draft Leave DESIGN.md and EXPERIENCE.md as a downstream contract, their shared-platform inheritance, feature catalogue, and consolidation coverage. This is a documentation review; no rendered-browser or assistive-technology test was performed.

## Overall verdict

The accepted interaction direction is coherent and well preserved: the employee, approval and management journeys fit together, named composites agree between the spines, and references resolve. The pair is still a planning draft rather than a complete implementation contract: visual tokens, some operational journeys and adverse states remain deliberately open, and recurring-entitlement effective dates need one explicit product decision. These are predominantly acknowledged handoff gaps, not regressions or reasons to reopen approved preferences.

Counts: **1 critical, 3 high, 2 medium, 1 low**. Severity describes impact if a downstream consumer treated the draft as complete; it does not imply the prototype is a deployed defective product.

## 1. Flow coverage — thin

Pass 1: extracted the twenty feature-catalogue headings plus Permissions and compared them with the source-to-flow mapping in consolidation-coverage.md. Sixteen named-protagonist flows contain numbered steps, a climax and failure/limits. Feature headings are mapped rather than silently omitted; no UJ identifiers exist to preserve. Mapping alone does not close every required journey.

### Findings

- **[high] UX-R01 — High-impact management journeys lack a complete decision path.** EXPERIENCE.md Information Architecture, lines 51–65, and Key Flows 3, 5, 11 and 15 acknowledge dedicated balance-override/deficit, full employment/setup and profile/configuration gaps. In particular, the balance override is mentioned inside ordinary approval, but the authorized actor's allocation choice, employee acknowledgement handoff and return to the blocked approval are not demonstrated as one complete journey. The employee future-date balance projection is listed in IA but has no end-to-end flow. *Fix:* close the balance-override/revised-acknowledgement and projection journeys, then use the existing coverage inventory to identify which remaining admin actions need dedicated layouts versus established form patterns. Do not create one flow per ledger calculation or a client migration-confirmation page.

## 2. Token completeness — broken

Pass 1: DESIGN.md frontmatter contains five deliberately empty token maps. No actual token references dangle; the literal `{path.to.token}` in explanatory prose is syntax guidance. Shared platform DESIGN.md has no approved token library to inherit. WCAG AA is an explicit target; a single illustrative text pair is not a complete palette verification.

### Findings

- **[critical] UX-R02 — There is no executable visual token contract.** Leave DESIGN.md lines 11–15 and Colors lines 34–41; platform/DESIGN.md Layout & Spacing and Open Visual Decisions. Surface, foreground, primary-action, border and focus combinations have no committed values or resolvable inherited tokens. This is explicitly disclosed and intentional for the draft, but implementations would otherwise invent incompatible palettes and cannot verify the promised contrast. *Fix:* approve a shared starting theme and committed color pairs, map Leave to it, and record typography/spacing/radius and responsive decisions needed by its components. Preserve the draft/readiness gate until then; do not silently adopt mock CSS or add a dark-mode palette unless dark mode is selected.

## 3. Component coverage — adequate

Pass 1: all 26 named EXPERIENCE Component Patterns sections have exact corresponding DESIGN Components rows with meaningful visual rules. Drawers, dialogs, uploads, filters and return navigation inherit explicit platform behaviors. Primitive widget coverage remains weaker than composite coverage.

### Findings

- **[medium] UX-R03 — Date and duration controls remain a composition gap.** DESIGN.md Apply for leave and Agreed wireframe refinements; EXPERIENCE.md Apply for leave, Agreed wireframe refinements and Interaction Primitives. A unified range picker, single-date partial-day controls and a duration input are named, but their complete composition and invalid/incomplete range behavior are not assigned to an approved shared control or documented as an application delta. Manual/keyboard entry is required, which is a useful floor, but does not resolve the input/error behavior. *Fix:* select or document the shared control behavior, then specify only Leave-specific date/duration constraints and examples. Keep the agreed duration-only partial-day model; do not introduce exact times.

## 4. State coverage — thin

Pass 1: every IA group appears in the State Patterns matrix. Employee submission/save/access and approval-staleness handling are comparatively detailed. The matrix honestly lists unfinished loading, publishing, export, configuration-concurrency and notification states.

### Findings

- **[high] UX-R04 — Administrative editing and confirmation lack a committed persistence/recovery contract.** EXPERIENCE.md State Patterns lines 855–859; Key Flows 8–11 and 16; platform/EXPERIENCE.md Open Implementation Details. The shared Close/Back rules explicitly describe autosaved drafts, while policy, entitlement, schedule and custom-role editors have review/confirm actions without establishing whether their unconfirmed edits persist, what happens when leaving, or how a failed/uncertain confirmation and concurrent change are recovered. A consumer could accidentally equate saving editor input with publishing or granting access. *Fix:* define one reusable admin edit → review → confirm state pattern with explicit draft persistence and close semantics, stale-review invalidation and confirmed/unknown-result recovery. Apply domain-specific consequences without changing the separate employee draft policy.

- **[medium] UX-R05 — Collection and secondary-surface fallback treatment is not yet a real inherited contract.** EXPERIENCE.md State Patterns lines 851–860 and Reports lines 760–765; platform/EXPERIENCE.md State Patterns. The Leave matrix describes some loading/empty/error/export feedback as inherited, while the platform says applications still specify it and Reports correctly says shared behavior is used “when established.” This is an unresolved dependency, not an implemented-service defect. *Fix:* establish a small shared loading / empty / filtered-empty / failed-load / retry / failed-export pattern and identify application-specific cases, including team-availability failure inside a decision and notification failure. Never turn a failed fetch into a truthful-looking empty result.

## 5. Visual reference coverage — strong

Pass 1: all 17 `.working/*.html` references are linked from the spines with specific composition purposes; no orphan mock or broken local spine link was found. No promoted mockups/wireframes/imports are presented as complete. EXPERIENCE Foundation states spines win over mocks for presentation, while source requirements and accepted ADRs govern business rules. Explicitly labelled partial/spine-only surfaces remain coverage gaps under Flow and State coverage, not broken links. Promotion and browser verification are unfinished draft work, not contradictory evidence.

## 6. Bloat & overspecification — adequate

Pass 2: the visual spine is restrained and appropriately refuses to turn sample CSS into requirements. The experience spine preserves useful exceptions but sometimes states the same rules several times.

### Findings

- **[low] UX-R06 — Repeated policy-publication rules increase maintenance drift.** EXPERIENCE.md Leave-type and policy configuration, especially lines 687–712, repeats changed values/effective-date/impact review and protection of existing requests; similar brief repetitions occur across Components, State Patterns and Key Flows. *Fix:* keep each detailed rule in one canonical component/state section and retain short linked walkthrough summaries. Preserve meaningful failure paths and source links; do not shorten away approval/acknowledgement safeguards.

## 7. Inheritance discipline — thin

Pass 1 and 2: local sources and Markdown links resolve. Unified Approver terminology, normal-versus-temporary authority, separate document access, missing route versus missing applicant coverage, and platform/application ownership remain coherent. Composite names match exactly. No implementation import or runtime availability is implied by inheritance.

### Findings

- **[high] UX-R07 — “Next leave-period start” is a default in the source but reads as a fixed input in the walkthrough.** features.md §5, lines 240–250, permits effective-dated changes and defaults to next period; EXPERIENCE.md Employee entitlement override lines 637–659 repeats that default but labels the field “Next leave-period start”; Key Flow 10 step 2 supplies the next period without stating whether alternatives are possible. consolidation-coverage.md explicitly identifies non-default midperiod starts as unresolved. This is a known decision gap, not evidence that either alternative was approved. *Fix:* obtain an explicit choice between period-boundary-only recurring changes and an authorized non-default effective date. Then align the field, review and source. If non-default dates remain possible, define their prospective grant/accrual effects without silently resetting current balances or rewriting history.

## 8. Shape fit — strong

Pass 2: DESIGN follows canonical section order. EXPERIENCE contains Foundation, Information Architecture, Voice and Tone, Component Patterns, State Patterns, Interaction Primitives, Accessibility Floor, Responsive & Platform, Inspiration & Anti-patterns and Key Flows. Additional coverage/reconciliation documents earn their place by separating open questions and evidence from approved rules. No invented persona or unnecessary new flow is needed to satisfy the format.

## Mechanical notes

- Read the rubric, design-md-spec, configured three design examples and two experience examples.
- Extracted 26 component headings: each matches a DESIGN table row.
- Checked local links from Leave spines: none missing. All 17 working HTML files referenced.
- All source paths in the pair resolve. No Mermaid blocks require syntax checking.
- Empty YAML token maps are valid syntax but intentionally incomplete design data.
- Draft labels and candid coverage statements are accurate safeguards; retain them through remediation.
- No current official holiday, legal entitlement, implementation-library or accessibility-conformance fact was inferred from illustrative wireframes. Accessibility-specific rendering findings belong to the separate review lens.
