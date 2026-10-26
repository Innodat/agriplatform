# Technology and brownfield reality review

2026-10-21. Scope: `ARCHITECTURE-SPINE.md` and `brownfield.md`, checked against current application/service source, manifests and owner contracts. Read-only review; no runtime, database, credential or application changes. No technology upgrade or new stack was evaluated or selected.

**Verdict: Changes requested.** The inherited stack and most existing-versus-planned distinctions are accurate. One owner-boundary inconsistency needs correction before treating the spine as a convergent build substrate. This is not implementation readiness approval.

## Finding T-1 — Medium: the spine silently selects a direct Identity HTTP integration

**Location:** `ARCHITECTURE-SPINE.md:20`, `:47`, AD-1 and D-1.

The paradigm says Identity, Access and notifications are independent owners reached through HTTP; the diagram gives Scribeswell separate direct Identity and Access edges. That makes a separate Identity HTTP integration appear adopted. The authoritative Identity account/actor contract instead places current-account resolution behind Access through an Identity-owned restricted projection, and explicitly says “no extra identity runtime service is introduced.”

Evidence:

- `platform/docs/architecture/contracts/identity-access-employment-e1.md`, “Resolution and controlled setup” (lines 1035–1057): authenticate and establish capability authority, resolve the stable actor through the restricted Identity projection, and expose account/actor evidence to Access without an extra Identity runtime service.
- `platform/docs/architecture/contracts/identity-access-execution-substrate.md`, “Current Identity projections and target-query isolation”: current-account SQL projections are internal owner contracts consumed by the restricted Access runtime; they are not browser RPCs or arbitrary account selectors.
- `services/access/identity-migrations/versions/0003_current_account_actor.py` and `services/access/IDENTITY-MIGRATIONS.md`: the implemented owner-local account projection is distinct from adoption in Access HTTP. The repository has `services/access/`, no separate `services/identity/` runtime.

**Consequence:** Independent consumers could build an unnecessary Identity HTTP service or choose competing ways of obtaining authoritative account/actor context. Recipient binding is genuinely unresolved, but that does not authorize a new account-resolution runtime boundary.

**Requested correction:** Show Scribeswell consuming verified current-account/actor evidence through the owner-selected Access HTTP contract, with Identity projections internal to that owner integration. Keep recipient-proof delivery/transport explicitly open under D-1 unless the Identity owner deliberately selects an additional contract. Link the actual Identity/Access owner contracts from D-1/brownfield so their migration/privilege boundaries remain visible. Do not allow Scribeswell to query Identity tables or invoke its internal SQL projection directly.

## Verified brownfield facts

| Area | Observed repository reality | Assessment |
| --- | --- | --- |
| Existing stack | Scribeswell web manifest declares React/React DOM, TypeScript, Vite and Supabase JS; backend requirements declare FastAPI/Pydantic and psycopg pool. | Retaining the existing stack and leaving versions to existing manifests/locks is accurate. No current-version claim or package choice requires outside research. |
| Access API | `services/access/main.py` exposes `/v1/check` with mandatory `org_id`, only the three PtS permissions, and PtS/Content service callers. It joins organization membership/org and `access.grants`; it does not provide a Scribeswell account capability or recipient binding. | AD-2 and D-1 correctly deny readiness/reuse of this legacy route. Do not infer that the newer Identity persistence delivery has upgraded this HTTP implementation. |
| Current public database | `apps/scribeswell/backend/database.py` uses an owner-local psycopg pool, explicitly validated `scribeswell_runtime` role and a fixed corpus-table allowlist. The direct database record separates runtime read and corpus-import authority. | AD-3 correctly proposes a new private role/pool instead of extending the corpus reader. Existing private persistence is not claimed. |
| Deployment | `apps/scribeswell/deployment/manifest.json` has no service dependencies, a single corpus database role/environment URL and public GET/OPTIONS `/api/bible/*`. No private pool or notification worker is declared. | AD-13 and D-5 correctly require new restricted routing/configuration and release evidence. The current manifest is not evidence of protected-feature readiness. |
| Authentication | `backend/auth/jwt_optional.py` verifies HS256 with audience verification disabled and returns decoded payloads; it supplies no current Access/resource decision. | Brownfield correctly flags review before protected reuse and does not equate JWT payload with current permission. |
| Identity migration ownership | `services/access/identity-alembic.ini` and `identity-migrations/` own Identity history separately from Access `alembic.ini`/`migrations/`, despite the shared repository location. | The spine's owner-specific migration/release requirement is compatible; no permission to put Identity DDL in Access or Scribeswell history is implied. Add the authoritative links as part of T-1. |
| Shared notifications | Services currently contain Access, app-directory and Content; no shared notification runtime is present. ADR-0006 selects asynchronous common capability, application intent/outbox and shared delivery; it starts modularly and defers separate deployment. Leave's E3 handoff explicitly calls notifications planned prerequisites. | Brownfield, AD-11 and D-3 accurately describe planned work and preserve account-versus-organization scope. The opening blanket HTTP wording should not be read as settling notification deployment; AD-11/D-3 remain the controlling deferred integration choice. |
| Readiness/release | Spine explicitly gates owner contracts, private persistence, selected channels, role provisioning and release rehearsal; no target execution is authorized. | No premature full runtime or production readiness claim found. |

## Review limits

This review inspected source and documentation only. It did not run tests, connect to a database, inspect live ACLs, test provider identity or validate production deployment. Existing owner evidence records are not proof that this new feature is implemented. D-1–D-5 remain required delivery gates after T-1 is resolved.

## Correction verification — 2026-10-21

**Final verdict: Pass for the reviewed technology/owner-boundary passages; no remaining finding.** Rechecked only the corrected paradigm/Identity diagram and AD-10, as requested.

- T-1 is resolved: the paradigm explicitly excludes a separate Identity HTTP service and the diagram now routes Scribeswell through Access to the restricted Identity-owned projection. This matches the existing authoritative owner contract and preserves separate migration ownership without adding a runtime owner.
- AD-10 now obtains remote account/capability/recipient evidence outside local write locks, distinguishes the local atomic invitation/share transition from remote revocation, and requires fresh authorization on restarted execution. ADR-0021 governs bounded already-executing authority; D-1 retains exact execution/evidence bounds as a pre-delivery contract gate. The text no longer implies distributed atomicity or external waits under the local write lock.
- No new stack/version, production-readiness or implemented account/notification capability claim was introduced by these corrections. Original D-1–D-5 gates and review limits remain binding.
