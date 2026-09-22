<!-- bmad:context -->
<!-- Verified 2026-09-06 against 5f1c2d5. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## Agriplatform

A TypeScript/React and Python/FastAPI workspace with Supabase-backed applications. Applications are self-contained silos; generic build-time packages and scaffolding live under `platform/`, while reusable runtime capabilities live under `services/`. Product truth and delivery tracking remain in repository-owned specifications and ADRs; BMAD supplies the generic delivery workflow.

## Policy

- Use BMAD as the sole generic delivery workflow; do not create a competing lifecycle or duplicate feature specifications and ADRs in generated planning artifacts.
- Use ATDD as the outer loop and focused TDD as the inner loop. Observe the relevant acceptance failure before implementing user-visible behavior or cross-service contracts.
- Add characterization tests before risky refactoring of behavior that lacks adequate protection; never change an expected result merely to dismiss an unexplained failure.
- For every feature, record scaffold, shared-UI, agent-context, documentation, and ADR impact decisions. Update reusable artifacts in the same delivery item when applicable.
- Keep applications as silos. Expose reusable runtime capabilities as HTTP services; never import another application's or service's server implementation.
- Accepted ADRs are immutable. Change a decision with a linked superseding ADR, and link application ADRs to platform decisions instead of copying them.
- Do not implement the Leave application until its remaining Phase 1 BMAD planning and readiness work authorizes implementation.

## Where things are

- Platform decisions and governance: `platform/docs/architecture/decisions/README.md`
- Leave product truth and tracker: `apps/leave/docs/features.md` and `apps/leave/docs/implementation-plan.md`
- Leave-specific decisions: `apps/leave/docs/architecture/decisions/README.md`
- Agriplatform safeguards under transition: `platform/prompts/README.md`
- Application scaffolding: `platform/builder-cli/`; verify what exists before using it because the CLI, generation tests, and validation commands are not implemented yet.

## Running and verifying

- Run the smallest relevant failing test first, then the affected acceptance or contract suite, and only then broader regression checks. Record requirement-to-test traceability and the exact commands and results.
- Do not treat root `npm run dev` or `npm run build` as application or repository-wide verification; they route through a stale Tailwind wrapper targeting the missing `apps/receipts-web`.
- There is no root test, lint, type-check, or CI command. Read the affected package manifest or component documentation and report verification gaps explicitly.
- Use `python3 tools/py/run_compose_supabase.py --check-only` to verify database composition. The root npm wrapper currently fails where `python` is unavailable because both it and the dispatcher require that executable name.

## Conventions that differ from defaults

- Application frontends use their silo's FastAPI API for business data; browser Supabase access is limited to authentication and explicitly approved realtime use.
- Promote only proven, domain-neutral UI into `platform/ui-core` or `platform/ui-business`; keep application-specific components in their silo.
- Never hand-edit files carrying a generated-file warning; update the owning generator or template.

<!-- /bmad:context -->

## Platform-wide release safety

All application and shared-service delivery must follow
[platform ADR-0020](platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md):
controlled and coordinated migrations before release activation, compatibility with
the previous running version for ordinary releases, activation blocked on migration
failure, and explicit recovery. Do not run migrations independently on API/worker
startup or automatically reverse applied migrations after failure. Incompatible
changes require a planned maintenance window and recovery procedure. Include the
ADR's evidence requirements in BMAD delivery and shared scaffold/release tooling.

## Platform-wide transaction boundaries

Follow [platform ADR-0022](platform/docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md):
keep transactions short and external service waits outside business coordination/write
locks by default. Preserve current authorization and domain validation; commit required
outbound intent atomically and deliver it after releasing locks. Document justified
exceptions with bounded timeouts, consistency and failure/retry behavior in the owning
design; no separate user approval flow is introduced.

## Platform-wide operational logging

Follow [platform ADR-0023](platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md):
use selected structured diagnostic fields and operation/trace links. Never log sensitive
business content, credentials, full signed URLs or request/response payload dumps,
including through exception paths or debug settings. Keep authorized business audit
separate; expose only safe references in optional user-facing support details.

## Platform-wide record attribution

Follow [platform ADR-0025](platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md)
when designing or scaffolding tables: mutable business records use server-managed
creation/update actor IDs and UTC timestamps; immutable records use creation attribution.
Actors may be people or services; preserve initiator/executor distinctions. Last-change
fields do not replace immutable consequential audit. Operational audit records command
and release identifiers; source line numbers belong to diagnostics.

## Platform-wide worker operations

Follow [ADR-0026](platform/docs/architecture/decisions/0026-worker-service-identity-and-ngo-scope.md)
for owner-specific restricted worker identity, narrow discovery and per-item NGO scope;
no universal platform credential or default per-NGO keys. Follow
[ADR-0027](platform/docs/architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md)
for bounded recoverable shutdown and supervisor-recorded warnings. Claim recovery or
resumed processing only when verified; preserve evidence of forced termination.

## Platform-wide durable event compatibility

Follow [ADR-0028](platform/docs/architecture/decisions/0028-event-payload-versions-and-queued-work-compatibility.md):
events carry explicit type/version; releases preserve supported interpretation of
queued, in-flight and failed/retryable work and active producers. Retain unsupported
versions for investigation. Do not remove old handlers solely because the ready queue
is empty; include payload compatibility in release verification.
