# E5 contract artifacts and verification ownership

**Status:** G6 planned artifact/package/check strategy bound; C6 atomic coverage, actual
external order and final single-agent sizing remain open.  
**Date:** 2026-10-25  
**Owners:** Each actual API/source/worker consumer, shared tool owners and Leave acceptance

This is an execution-evidence map for the approved BMAD delivery boundaries, not a second
feature specification, test-result claim or permission to implement Leave. Current
`apps/leave/README.md` confirms planning only. Inspection found no Leave pyproject/package
manifest, Python application, migration or SQL files. No proposed paths below exist merely
because they are listed here. Product expected behavior comes from Features/accepted ADRs
and owning contracts, never generated code or observed implementation outputs.

## Current implementation to reuse and its limits

| Existing inspected owner | Available code/artifact/evidence | Exact reuse limit |
| --- | --- | --- |
| Access | services/access/pyproject.toml, export_openapi.py, openapi.json; registry/registration/org admission/grant commands, organization_check.py and owner evidence | Existing real owner foundation, not another Leave implementation story. Current organization HTTP/SQL is KDG-specific; People/Leave context/resource/check additions still needed |
| API client build tool | platform/api-client/README.md, package.json, src/cli.mjs and EVIDENCE.md | Existing app-owned OpenAPI-to-TS tooling, generated ownership/preservation, stale/tamper refusal; health-client proof is not Leave DTO/error/recovery integration |
| Active application scaffold | platform/builder-cli/src/application-renderer.ts and templates/application; bootstrap/API-client/Auth evidence | Internal candidate renderer and installed-pattern maintenance exist; public complete Leave generation is not ready. Use active renderer, not retired templates/web AuthContext |
| Auth lifecycle | builder AUTH_PATTERN_EVIDENCE.md, src/auth-pattern.ts and managed KDG consuming files/tests | Already shared neutral lifecycle/hook/test pattern; Leave owns actual session/access/draft/operation adapters. Preserve code/test parity with first consumer fixes |
| Atomic owner write candidate | builder examples/owned-service and WRITE_ATOMIC_EVIDENCE.md | Bounded transaction/context/outcome candidate; prove actual Leave effects/rollback. KDG first-committed-wins/HMAC follow-ups do not replace Leave SHA/JCS payload comparison |
| Migration helper | platform/docs/development/migration-verification.md and active application database/native templates | Small PostgreSQL/Alembic wrapper/native fixture pattern exists. KDG initial-ledger proof is not Leave business constraints/RLS or coordinated activation/recovery |
| Shared UI | platform/ui-business package and app-launcher components | Existing proven surfaces only; package presence does not implement all planned collection/form/history panels |
| Content | services/content-service/main.py, provider.py, migrations and deployment files; shared Content contract | Actual service exists. It has no inspected standalone pyproject/exporter here; current Dockerfile borrows apps/pts requirements. Do not pretend it has an independent locked contract/test toolchain yet |
| People / notification / Leave worker | Owning shared contracts and approved E1/E2/E3/E5 stories | No People package or generic notification/Leave worker runtime found in inspected owners. Interface design is not implemented runtime proof |

Version/tool selection comes from actual owning manifests/qualified toolchains at delivery,
not copied global environment guesses. API-client tooling currently isolates its qualified
TS6 compiler while applications use TS7; preserve that owner mechanism rather than override
workspace peers or download an unpinned alternative. Root npm build/dev are not verification.

## Selected future owner artifacts

These paths are selected delivery targets, not edits or claims of existence. Create only
what the first actual consumer needs after readiness authorizes implementation.

| Planned target / actual first owner | Responsibility |
| --- | --- |
| apps/leave/api/pyproject.toml and uv.lock; web/package.json under existing root workspace lock | E1 application/service consumer owns locked Python package and web/tool scripts. No nested arbitrary npm lock or hidden checkout dependency fallback |
| apps/leave/api/main.py and owner DTO/router modules | Actual first API story owns closed typed input/result/error variants. All browser business requests remain Leave API calls; no browser People/Access/Content control-plane SDK |
| apps/leave/api/export_openapi.py and openapi.json | Reuse actual offline owner export pattern; importing/exporting must require no live auth/provider/DB call or business mutation. Export defines real routes/variants and safe error response models |
| apps/leave/web/src/api/generated/ | Existing platform-api-client owns generated types.gen.ts/index.ts/ownership metadata. Never hand-edit generated files/manifest; no handwritten duplicate API DTOs |
| apps/leave/web/src/api/ owner adapter | Thin authorized same-origin Leave HTTP/error/outcome adapter using generated wire types; preserves current context/typed validation, read versus mutation recovery and original operation identity |
| apps/leave/api/tests/ | pytest domain/API/contract/real database acceptance; real owner fixtures and retained safe results. Synthetic request fixtures let foundations work before later producers |
| apps/leave/web/tests/ and Playwright configuration | Select TypeScript Playwright Test for actual browser acceptance; existing generated health smoke remains limited to health. Do not maintain a duplicate Python browser suite |
| Focused owner UI tests where needed | Use focused React interaction tests only for meaningful isolated behavior; no new suite merely mirroring rendering or reversible document edits |
| Actual Leave migrations, native fixture and release adapter | Owner Alembic history/restricted identities and evidence under P-0020; exact file names/history derive from actual first source package, not a speculative full database script |
| Existing shared owner DTO/OpenAPI/consumer files | Actual Access/People/Content/notification first consumer adds its declared variants and tests in that owner, preserving supported earlier consumers; application code never imports another owner's server |

A generated type is compile-time shape, not runtime validation/current authorization.
Model actual operation/status unions and safe error details in API schemas and validate
received discriminator/identity consistency in the thin adapter. Do not parse English or
turn unknown response shape into mutation success. JSON decimal-string counters/minutes,
UUID/date/time/closed version constraints must survive export/client generation unchanged.
Pydantic and generated TS schemas are derived from one actual owner contract, not another
manually kept E5-specific schema registry.

## Command inventory and preconditions

No commands below were run for this documentation task. `P` means the explicit owning
locked Python interpreter, `N` the explicitly selected qualified Node executable. Resolve
those from current owner tooling; they are not a newly installed environment or secret.
Never substitute a credential-bearing environment dump or an unverified system binary.

| Working directory / command | Current existence and what it proves |
| --- | --- |
| services/access: `P -I -B export_openapi.py --check` | Existing exporter/check, with owner import environment and dependencies. Detects stale current Access schema, not new People/Leave behavior |
| repo root: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest services/access/tests/test_organization_check.py -q -p no:cacheprovider` | Existing current-check test file/recorded owner command. Run only for affected Access change, then actual new consumer cases; not proof People already supported |
| repo root: `N --test platform/api-client/tests/*.test.mjs` | Existing tool suite, qualified declared dependency installation required. Appropriate for generator/preservation changes, not necessary to repeat for unchanged planning |
| platform/builder-cli: `npm run type-check`, `npm run schema:check`, affected `N --test tests/*.test.mjs` | Existing scripts/tests. Select relevant tests when templates change; same consuming item updates managed copies/code/tests |
| repo root: `N platform/builder-cli/scripts/sync-kdg-auth.mjs --check` | Existing current-template/managed-copy parity check. Use with actual shared Auth changes; no generated hand-edit |
| future Leave api: `P -I -B export_openapi.py --check` | Planned same exporter semantics, not currently runnable in Leave |
| future Leave web: `npm run api:generate`, `npm run api:check`, `npm run test:client`, `npm run type-check`, `npm run build` | Exact active scaffold script names already exist in its template; planned Leave package gets them through actual authorized bootstrap/owner maintenance |
| future Leave api: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest tests -q -p no:cacheprovider` | Planned package-local pytest invocation, after actual fixtures/import setup/locked dependencies exist; exact focused node IDs are assigned with acceptance cases, not fictional passing tests |
| future Leave web: `playwright test` through its declared package script | Selected runner, actual package script/config/browser/install/proxy/auth fixture must be declared by the first browser consumer. Current generated test:browser is health smoke and must not be mislabeled full Leave acceptance |
| actual owner native migration/DB qualification and coordinated release checks | Read owning fixture/runbook and record exact isolated target command during delivery. No unsafe generic command connects to a shared DB; no root composition check alone proves RLS/rollback/release safety |

Export/generation order during actual DTO changes: owner tests and export -> owner schema
check -> generated client regeneration/check -> adapter/client tests -> consuming type-check
and affected browser proof. A deliberate DTO/schema drift must fail before regeneration;
check is read-only. Owner implementation changes remain normal owner code; template-owned
files are changed through their generator/installer. G6 records exact command strategy,
not guessed future test names, fake execution logs or installation during planning.

## First-consumer contract/acceptance allocation

| Interface cluster | Foundation/first actual owner | Actual integration owner, without duplicate machinery |
| --- | --- | --- |
| Request state/current audience read | 5.10-A actual scoped records/read/permission fixture | 5.11/12 first own rows, 5.18 assigned read, 5.30 formal detail/history |
| Request receipt/result/unknown recovery | Existing E1 receipt then 5.10-C target/client extension | 5.11/12/18/19/20/13/24 actual mutation envelope and lost-response consumer |
| Effective source/work/rules | E2/E3 actual source owners and 5.1–9 narrow adapters | 5.15 actual source variants, 5.17 query, submit/finalization current protected checks |
| Date/source funding/provenance/evidence | E3 3.9/3.17-A/3.18 then 5.8-A actual commitment extension | 5.10-B consume, 5.19 release, 5.13 reallocation, 5.15 source history consequences |
| People source preparation/cancel/admission | Existing KDG Access substrate reused; actual People/Access and P-0062 consumers | 5.15-K, 5.24-C/E real producer/fence/recovery/current transfer |
| E4 associations/private reads | 4.4/4.7/4.13 actual owner pipeline | 5.12/20 target extension, 5.9 readiness, 5.32-H actual continuity not second pipeline |
| Timed payload/current claim/clock/occurrence | 5.23 first expiry and E3 worker/outbox, 5.25/26/27 real consumers | 5.21/22 producer/revision change, 5.28 gap projection, actual notifications/inbox |
| Queue/calendar/attention/My Leave/preference | Existing minimum reads plus 5.16/17/27/28/29/30/31 residual owners | Browser partners test actual typed results/independent errors/navigation, not replay whole domain suites |

Record each atomic acceptance case's source requirement/ADR/clause, one primary delivery
owner and automated boundary, referenced existing proof versus new actual producer proof,
exact fixture/setup, expected failing observation, final command/result and limits. C6
will reconcile this against all approved boundaries and unsuffixed foundations; this
cluster table alone is not atomic requirement coverage or a single-agent sizing PASS.
Actual implementation uses ATDD then focused TDD and real restricted DB/HTTP/browser
proof where relevant. Runtime failure-before-code happens in authorized delivery, not by
implementing Leave now to manufacture planning evidence.

## Verification limits, promotion and closure

No unit/contract/browser/runtime/DB suite was run in this planning pass. Scoped document
checks and reference/80-boundary integrity are the only current verification. Recorded
existing owner proof is cited at its original scope, not counted as a fresh PASS or live
People/Leave activation. Synthetic health/doubles/empty-ledger proofs do not establish
business authority, transaction rollback or cross-org/owner protection.

Every actual consumer records scaffold/shared UI/agent-context/docs/ADR impacts. Promote
only proven domain-neutral patterns and fixtures in the same item, with consuming tests;
keep Leave calculations/workflows as owner code. No automatic migration of other apps.
P-0059 scaffold input can reference actual proven pattern/owner/scope/tests but cannot
claim a full generator exists or embed a parallel DB/API specification. Native DB checks
follow the focused migration guidance, no universal schema object whitelist.

G6 artifact/package/generation/test-command design is bound. C5 design register G1–G6
is now mapped to owning interfaces and actual delivery artifact responsibilities; a
complete executable OpenAPI/constraint suite is a future first-consumer deliverable.
C6 still must perform final atomic requirement/test allocation, delivered-external-work
reconciliation, topological delivery order, duplication removal and single-agent sizing,
then user epic-completion confirmation. All later planning/readiness gates and E6 remain
open; no Leave implementation, migration, grant, deployment or commit authorized here.
