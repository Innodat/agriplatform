# Lean local ENV course correction — 2026-10-20

Status: implemented and verified through the thin native route; authorized by the user's “Yes please”
and instruction to keep the repository lean and build only present practical needs.
Batch analysis; no repeated requirements interview or owner acknowledgement.

## Issue and evidence

ENV delivery has accumulated individual Docker request/config/lifecycle qualifiers
while the public start command still refuses runtime_adapter_unqualified. The latest
GoTrue prerequisite (5e237640471083f71f0ec8e98ce5a4401cf3a849) demonstrates that gap:
88 selected tests pass but no public Supabase stack is usable. The user approved
trusting the supported local CLI and limiting repository code to target selection,
isolation, configuration and explicit destructive-command protection.

## Impact

Read KDG PRD, all19 stories/five epics, architecture spine and both UX documents.
Product requirements, story acceptance, offline behavior and UX remain unchanged.
Change the mutable ENV contract, runbook and KDG prerequisite/handoff navigation.
Keep Supabase CLI2.120.0/PG17 and the approved dependency baseline including TS7.0.2.
Identity/Access/WRITE and application migration/fixture ownership are unchanged.
Accepted ADRs are unchanged: Auth retention, short controlled migrations, current
access and safe sensitive logging remain binding. No new service/generator/UI.

## Selected approach

Direct adjustment, moderate delivery-plan change with a small developer handoff.
Let the pinned CLI own start/status/stop and explicit local DB reset. A thin route in
the existing dev.py entry point selects a validated disposable target/run and
executable, uses the existing configuration renderer, guards local Docker routing and
loopback network defaults, and emits safe outcome summaries. Native CLI work uses a
fresh run with a small target/config marker, not all historical source receipts.
Old qualifiers remain historical/compatibility paths; they are no longer prerequisites
for this route. Preserve their receipts/state/resources and source; deletion is a
separate reviewable cleanup. No blanket rollback or product MVP reduction.

Effort: one bounded wrapper/test/documentation item, then observable integration
qualification and existing owner work. Main risk is confusing Supabase availability
with application readiness; report the stages separately. No completion date promised.

## Explicit edits

| Artifact | Before | After / reason |
| --- | --- | --- |
| ENV dependency/lifecycle contract | Exact vendor internals and source-bound owner qualifiers gate startup | Pinned vendor CLI owns service lifecycle; observable local readiness and practical target guards |
| ENV command table | up also coordinates application migrations/fixtures | Startup and status are distinct from existing owner migration/fixture commands |
| ENV reset | Ambiguous environment disposal/recreation | Explicitly confirmed local Supabase database reset; no remote reset, no Docker prune or application migration takeover |
| DEVELOPMENT | Custom qualification sequence is the active delivery path | Short normal-CLI commands first; historical diagnostics remain available |
| KDG shared prerequisites/handoff | Next GoTrue interception boundary work | Finish thin CLI path, qualify reachable DB/Auth, then retained owner/scaffold work |
| PRD/epics/UX/accepted ADRs | Existing product/ownership/safety contracts | No edit needed |

## Handoff and acceptance

Developer implements through bmad-build with ATDD and focused tests. Reuse dev target
validation, project naming, configuration and port checks. Do not add another generic
orchestration engine. Require fixed --workdir and network on every CLI lifecycle
command; stop retains data; reset requires target confirmation and --local/--no-seed.
Capture vendor output because status prints local credentials. Test unsafe target,
changed config, wrong CLI version, remote environment contamination and vendor failure.
Qualify only isolated synthetic local behavior; production/account/provider changes
and real-data use remain outside approval. No historical resource cleanup here.

## Checklist / approval record

[x] 1.1–1.3 Trigger, misinterpreted implementation scope and concrete evidence recorded.
[x] 2.1–2.5 ENV delivery sequence changes; five KDG epics/19 stories remain viable.
[x] 3.1–3.4 PRD/UX unchanged; mutable environment/test/runbook strategy adjusted.
[x] 4.1/4.4 Direct adjustment selected: reduced maintained orchestration surface.
[N/A] 4.2 Blanket rollback: preserve historical work and resources instead.
[N/A] 4.3 Product MVP reduction: user goals unchanged.
[x] 5.1–5.5 Specific edits, developer handoff and success criteria above.
[x] 6.1–6.3 Direction explicitly approved in this conversation; no renewed approval.
[N/A] 6.4 No epic/story renumbering or global Leave sprint-status changes.
[x] 6.5 Proceed with the bounded Build; record tested outcome and remaining gates.


Completion:52 affected tests pass; real native start/repeat-start, persistence,
local reset of new synthetic data, loopback DB/Auth reachability and stop verified.
Review complete with8 patches,1 low rejection, no new deferrals. Existing evidence/
resources/concurrent source preserved. The integration's final ID/name assertion
and read-only reconciliation are recorded candidly in ENV_NATIVE_CLI_EVIDENCE.md.
Continue existing owner/scaffold integration; no per-service interception gate returns.
