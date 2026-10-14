# Architecture rubric review — KDG Capture

Date: 2026-10-12. Reviewed architecture spine, PRD, EXPERIENCE and discovery; contracts were prospective at review time. These are planning findings, not demands for completed runtime evidence.

## Verdict

Adequate planning spine with concrete rules for the major offline/server divergences. The tenant, actor, version, local-save, retry and release boundaries are coherent with the accepted platform. Three seams need explicit rules before their consuming stories can be ready.

## Findings

- **high — Offline authorization renewal is insufficiently scoped (AD-7).** “Last successful online authorization” could mean a successful own-read check renews cached administrative rights and assignment observations for another seven days. *Fix:* define the exact complete provisioning/renewal observation set, capability-specific validity and when partial refresh can update or invalidate observations. Never renew unobserved admin/create authority from an unrelated successful request. Keep server checks independent.
- **medium — Download reconciliation is silent (AD-4/5/8).** The spine owns both server history downloads and local pending snapshots but does not prohibit a refreshed server record replacing pending local edits/drafts/conflict evidence. *Fix:* specify a separate server baseline and pending overlay; downloads update the baseline through a revision-aware merge, preserve local proposals, and create attention/conflict state where needed.
- **medium — Queue ownership across tabs is unspecified (AD-5/9).** “Serialize per record” needs an enforceable local owner mechanism when two tabs/installed instances resume concurrently, including interrupted claim recovery. Server idempotency prevents duplicate effects but alone does not prevent two different record commands racing. *Fix:* declare a transactional claim/lease or equivalent single drainer with crash recovery, preserving per-record order and conditional local acknowledgement.

## Rubric judgments

| Dimension | Judgment |
| --- | --- |
| Real divergence points | Most covered; findings above address authority renewal, replica merge and local drainer ownership |
| Enforceable Binds/Prevents/Rule | Strong for AD-1–6/8–10; AD-7 renewal needs specificity |
| Inherited invariants | No apparent weakening of server current checks, restricted DB roles, sensitive logging or release safety |
| Brownfield fit | Extends existing Access/Identity/builder owners, explicitly excludes employment and imported service implementations |
| Capability coverage | FR/NFR mapping is present; optional details, multiplicity and first seed remain domain companions rather than generic platform rules |
| Operational envelope | Dedicated origin, nonproduction HTTPS, owned migrations and setup separation present; operator trust and final deployment configuration honestly gated |
| Deferred dimensions | Package pins, shared schemas, download/retention and saving assumptions are acknowledged gates, not silently decided |
| Technology verification | Existing stack ranges are correctly labeled source evidence; optional PWA adapter remains unselected; physical-device proof is planned |

## Mechanical notes

AD-1–AD-10 are contiguous, with Binds/Prevents/Rule. ADOPTED labels should be understood as adopted proposal/user-or-platform baseline within a draft spine, not acceptance of every new technical rule. Missing exact pins are already stated pre-build inputs; do not invent pins to satisfy a planning linter. Verify companion links when contracts/testing are written.
