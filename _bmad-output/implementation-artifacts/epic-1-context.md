# Epic 1 Context: Start and safely resume my leave draft

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Deliver the first working Leave journey: sign in, select an authorized organization, create or resume a draft, enter details, autosave, close and reopen. Prove current access, organization isolation and recoverable desktop/mobile persistence. Establish only the shared foundations this journey consumes; no entitlement reservation or submission. The consolidated planning package is approved and readiness passed; historical candidate/open-planning labels are superseded by the recorded final adoption. Begin implementation with E1-ENV only, crediting existing shared work through actual verification.

## Stories

- Story 1.1 (E1-ENV): Reproduce an isolated development and acceptance environment
- Story 1.2 (E1-P1): Generate a runnable application foundation safely
- Story 1.3 (E1-SERVICE): Generate an independently owned internal service
- Story 1.4 (E1-ID-A): Establish a verified identity migration baseline
- Story 1.5 (E1-ID-B): Link accounts to people and preserve membership history
- Story 1.6 (E1-ACCESS-A): Configure application admission and grants safely
- Story 1.7 (E1-ACCESS-B): Enforce current application and user access
- Story 1.8 (E1-CONTENT-READ): Protect owned files and stream private reads
- Story 1.9 (E1-DISCOVERY): Discover currently accessible organizations and apps
- Story 1.10 (E1-PEOPLE): Resolve shared employment for the selected organization
- Story 1.11 (E1-WRITE): Prove safe owned writes for generated backends
- Story 1.12 (E1-LAUNCHER): Show accessible apps with honest discovery states
- Story 1.13 (E1-REF): Prove a generated authenticated application against real persistence
- Story 1.14 (E1-A1): Sign in and enter an authorized Leave organization
- Story 1.15 (E1-PTS-ADOPT): Use PtS through individual platform access
- Story 1.16 (E1-VERIFY): Exercise the shared reference journey in hosted environments
- Story 1.17 (E1-CONTEXT): Explain whether a Leave draft can be started or edited
- Story 1.18 (E1-CHOICES): Choose a leave type and permitted duration mode
- Story 1.19 (E1-D1): Create or resume an application draft
- Story 1.20 (E1-D2-A): Save and read draft input safely
- Story 1.21 (E1-D2-B): Edit, autosave, close and reopen a draft
- Story 1.22 (E1-D3): Switch organizations without losing or mixing draft data
- Story 1.23 (E1-D4): Deliberately discard a draft and start again
- Story 1.24 (E1-D5): Return safely to a draft after sign-in expires

## Requirements & Constraints

Use BMAD delivery, acceptance failure before implementation and focused TDD. Keep product truth and tracking in repository-owned sources. Record exact commands/results and requirement-to-test evidence; assess scaffold, shared UI, agent-context, documentation and ADR impacts in each delivery item. Planning approval proves no runtime, browser, database or release result.

Use disposable local/CI targets with explicit identity, isolated names/ports, synthetic accounts and two organizations including a for-profit organization. Refuse foreign/unapproved targets; preserve existing application environments. Separate setup credentials from restricted runtime identities and enforce owner-controlled migrations/fixtures. ENV proves the base foundation using an available fixture; future People/Leave/browser consumers supply their own integration evidence. No production fallback or live provider/grant/deployment changes are authorized by this implementation handoff.

Local synthetic Auth is distinct from real Entra callback qualification. Playwright engine/emulation results are distinct from actual supported-browser/device qualification. Use real PostgreSQL for permissions, RLS, constraints and concurrency; injected authentication or mocked commits cannot establish service-boundary evidence. Healthy-network draft qualification targets are p95 open/close within three seconds and save acknowledgement within two seconds; record workload, failures and measured assumptions when the consuming journey exists.

## Technical Decisions

Keep applications as silos. React business calls go through Leave FastAPI; shared Identity, Access and People are consumed over authorized HTTP. Browser Supabase access is for authentication and explicitly approved realtime. Identity owns person/account and durable actor attribution; People owns common employment; Leave owns domain settings and drafts. Employment or account linking never grants application authority. Use organization and established `org_id` conventions.

Reuse the thin pinned Supabase CLI lifecycle route rather than building another environment manager or reinstating historical vendor-interception gates. Explicit disposable target/run binding, local Docker, loopback routing, protected credentials, safe diagnostics and destructive-command guards remain required. CLI readiness establishes service availability; owner migrations, authenticated SQL and authorization checks remain separate. Use the approved dependency baseline with deliberate recorded pin changes and clean-install compatibility evidence. Frontends share the root npm workspace/lock; Python owners retain independent dependency/lock/environment authority.

Generate and prove minimal app/service patterns with their first consumers; documentation describing a generator does not establish executable generation. Promote only proven neutral patterns. Owner migrations run under controlled coordination before activation, with compatible prior-version behavior, failure blocking and recovery; never on API startup or by automatic reverse migration. Runtime identities cannot migrate or acquire setup authority.

Check current typed capability/admission scope at action boundaries. Leave requires organization enablement, current membership and explicit authority; PtS current grants are account-scoped. Scribeswell public reading is independent, while launcher visibility requires current PtS access. Content enforces stored application/resource ownership; private reads stream through authenticated application routes.

Enforce one active draft per organization/employment with database uniqueness and atomic create-or-resume. Save checks revision and active lifecycle together, with durable operation recovery; late saves/retries cannot resurrect discarded drafts. Preserve bounded incomplete input without inventing submission validity, balances or reservations. Keep external waits outside database locks; bounded shared-input observations apply only to the declared draft-save execution. Use stable machine-readable errors, server-managed actor/UTC attribution and sensitive-content-free diagnostics.

## UX & Interaction Patterns

Inherit shared semantic visual tokens, shadcn-based primitives and Lucide icons: light-mode Neutral + Quiet Lagoon, responsive task drawer on desktop and full-page task on narrow screens. Prove rendered keyboard/focus/zoom and accessible status/error behavior with the actual consumer.

Autosave unfinished input with accurate Draft saved feedback. Acknowledgement covers only confirmed input; preserve partial date/duration text. Show inline Changes not saved with Retry. Prompt Stay / Close anyway only when exit cannot confirm bounded saving; organization switching uses Stay / Switch anyway. Confirmed saved input closes immediately. Re-authentication restores the same authorized user's validated organization/page/form context, rechecking authority and preventing prior-user disclosure or automatic consequential actions.

## Cross-Story Dependencies

Use the sprint source map's exact leaf dependencies and tracking ordinals; retained parent scopes are not extra stories. ENV precedes P1, then SERVICE and identity/access foundations. Current Access enforcement precedes discovery, owned-write and employment consumers; generated-reference proof precedes the assembled autosave UI. Context/choices precede draft creation, then server persistence, UI and switching/discard/session recovery. Content-read/PtS adoption and hosted-reference verification are explicit E1 leaves, without adding attachments, submission or pilot activation. Full E2/E3 administration is unnecessary for the draft slice: authorized minimal fixtures may supply its configuration.
