# Technology review — KDG Capture

Reviewed 2026-10-12: `ARCHITECTURE-SPINE.md`, `discovery.md`, `contracts.md`, actual
package manifests/lockfile and referenced primary documentation. This is source and
design verification, not installation, execution, a dependency audit or device proof.

## Finding

The retained stack fits the proposed bounded MVP. No concrete incompatibility requires
replacing React/Vite/shadcn, FastAPI or PostgreSQL. Native IndexedDB and a shell-only
service worker are plausible foundations for offline capture. Package selection remains
a pre-story gate; published capability specifications remain distinct from implemented
Identity/Access behavior.

## Repository reality checks

| Choice | Verified evidence | Required consuming-story evidence |
| --- | --- | --- |
| React/Vite/TypeScript | `apps/pts/web/package.json` ranges match the spine. Its current lockfile resolves React 19.3.0, Vite 7.3.6, TypeScript 5.9.3 and React plugin 4.7.0; plugin peer range includes Vite 7. These are repository pins, not a recommendation to copy or a claim of latest versions. | Select coherent KDG/build-template pins and run actual type/build/browser checks. |
| Node runtime | Locked Vite requires Node `^20.19.0 || >=22.12.0`; locked Supabase JS 2.117.1 requires `>=22`; their combined floor is 22.12.0. Vite 7 official guidance agrees. [Vite 7](https://v7.vite.dev/guide/) | Pin a supported Node runtime satisfying every dependency and release environment; do not infer compatibility from a successful Python backend. |
| shadcn/shared UI | Expense has concrete Radix/shadcn-style components and Tailwind; official installation supports Vite. Expense declares React 18.3.1 with React 19 typings, while `platform/ui-business` requires React >=19. No complete neutral control library exists. [shadcn Vite](https://ui.shadcn.com/docs/installation/vite) | Extract source through the shared owner; do not copy Expense's package manifest or import its runtime components. Verify theme, radio controls and accessibility. |
| Backend | `apps/pts/requirements.txt` pins FastAPI 0.116.1, Pydantic 2.11.7, SQLAlchemy 2.0.43, Psycopg 3.2.9 and Alembic 1.16.5. Builder requirements are broad ranges and omit owned SQL persistence dependencies. | Compatible KDG pins, generated HTTP types, separate migration history and restricted runtime-role tests. |
| Identity/Access | `services/access/main.py` implements `/v1/check`; the canonical shared contract explicitly describes unimplemented `/v2/check`. KDG account/organization success shape and caller registration remain missing. | Shared-owner handoff, exact closed union, current checks and negative integration tests before server-backed slice. |
| Questionnaire JSONB | PostgreSQL supports relational columns alongside JSONB. JSONB does not retain duplicate object keys; ingress validation must reject them before conversion, as proposed in contracts. [PostgreSQL JSON](https://www.postgresql.org/docs/current/datatype-json.html) | Version immutability, schema/answer validation, tenant-aware references and idempotent writes under actual database constraints. |
| RLS | PostgreSQL table owners and privileged roles can bypass policies. The spine's restricted-runtime direction is appropriate. [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) | Test actual deployed runtime role and pooled transaction context, not only API fixtures or administrator connections. |

## Offline feasibility and limits

IndexedDB provides multi-store transactions, upgrade transactions and a strict durability
hint. Its current API 3.0 publication is a Working Draft; the hint is not a guarantee
against deletion, eviction or device failure. Await transaction completion, keep network
waits outside local transactions, and prove crash/reopen behavior on each target phone.
[IndexedDB specification](https://www.w3.org/TR/IndexedDB/)

WebKit documents storage pressure, origin-wide eviction and heuristic persistent-storage
grants. Installed home-screen operation does not establish a backup. The plan correctly
requires quota failures, no silent reset and physical-device validation.
[WebKit storage policy](https://webkit.org/blog/14403/updates-to-storage-policy/)

Manifest identity/scope supports the chosen installation model. Vite PWA remains an
unselected adapter: its documented prompt update mode fits deferring activation until
input and queue state are safe. Adapter defaults do not implement queue or local-schema
compatibility. [Manifest](https://www.w3.org/TR/appmanifest/),
[Vite PWA prompt updates](https://vite-pwa-org.netlify.app/guide/prompt-for-update)

Supabase documents Azure sign-in configuration; that authenticates an account, not
Khula membership or KDG permissions. Provider/redirect configuration remains an environment
gate. [Supabase Azure](https://supabase.com/docs/guides/auth/social-login/auth-azure)

PtS locks Playwright 1.63.0. Its device emulation changes browser context settings;
it does not prove installed iPhone/Android behavior, OS termination or browser storage
policy. Keep automated and real-device evidence separate.
[Playwright emulation](https://playwright.dev/docs/emulation)

## Disposition

No additional stack-selection decision is required now. Preserve the existing gates for
exact package/runtime pins, minimum supported browser/OS matrix, provider setup, shared
Access/Identity delivery and physical proof. No dependencies were installed, application
code changed or shared contracts modified by this review.
