# Editorial review — KDG Capture planning

These documents help the product owner assess the agreed scope and implementers find
the requirements, UX behavior and technical boundaries without confusing proposals with
runtime evidence. Review date: 2026-10-12. Suggestions only; core documents are unchanged.

Applied installed `bmad-review` **structure**, then **prose**, using resolved human-reader
and Microsoft Writing Style Guide defaults. Read `editorial-common.md`, `structure-models.md`,
`lens-structure.md` and `lens-prose.md`. Structure models: Strategic/Context for PRD;
Reference for DESIGN/EXPERIENCE. Architecture spine was checked for consistency only:
the architecture skill reserves prose polish for human-facing companions, not the spine.

Exact installed `word_metrics.py` counts at review: PRD 1,882; DESIGN 514; EXPERIENCE
1,656; architecture spine 1,587 words. No length target was requested. Existing terse
technical voice, named requirement IDs, state tables, diagrams and deliberate separation
of product/behavior/mechanism are useful and should be preserved.

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | PRD §Open items and assumptions — 214 words, currently last | MOVE before §Functional requirements, retaining identifiers and wording | Put unresolved gates and proposed defaults where reviewers see them before detailed requirements. Word impact: 0. |
| structure | EXPERIENCE §Key Flows — 219 words, currently after technical state/accessibility patterns | MOVE immediately after §Information Architecture | Gives a human reader a concrete journey before the detailed component/state reference. Word impact: 0. |
| structure | PRD/EXPERIENCE repeat UJ journeys; architecture/contracts repeat safety boundaries | PRESERVE | Cross-document reinforcement serves each audience and prevents unsafe interpretation. No cut recommended; word impact: 0. |
| prose | PRD UJ-1: “A local acknowledgement is the offline climax; a separate server acknowledgement establishes backup.” | “A local acknowledgement confirms the phone save; a separate server acknowledgement confirms the server copy.” | Replace the narrative term and make the two acknowledgements concrete without promising operational backup recovery. |
| prose | EXPERIENCE §State Patterns: “Surface closure: sign-in/setup has checking/denied/unavailable/incomplete states” | “Required loading and failure states: sign-in/setup has checking/denied/unavailable/incomplete states” | Explain the uncommon shorthand at its first use. Keep the complete state inventory. |
| prose | DESIGN final paragraph: “All screens are currently spine-only.”; EXPERIENCE §Visual coverage: “All eight IA surface groups are spine-only in this fast-path draft” | “All screens currently have written specifications only.”; “All eight navigation surface groups have written specifications only in this fast-path draft” | Make the absence of mockups clear to the product owner; use the expanded phrase consistently across both surviving locations. |

Six recommendations, including one explicit preservation finding. Structure changes
reduce 0 words (0% of 4,052 words in the three editable documents). Minor prose expansions
are intentional; no length target or comprehension trade-off calls for deleting safety
requirements. No content decisions or implementation-readiness claims are changed.
