# Existing-project discovery and shared handoff

Evidence date: 2026-10-12, current working tree. Source inspection establishes
implementation in the repository, not deployed functionality or passed runtime tests.

## Runtime evidence

| Capability | Implemented source | Limits / missing implementation |
| --- | --- | --- |
| Account profiles, organizations | `platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql`, identity.users / identity.org | Legacy SQL assets, not accepted actor registry or adopted Alembic baseline |
| Memberships / roles / token hook | `platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql`, org_member/member_role/hook | Current unique org/account membership is not the accepted historical retirement/rejoin design; JWT roles are not current authority |
| Shared Access service | `services/access/main.py`, `migrations/versions/0001_initial.py`, `tools/identity_bridge.sql` | `/v1/check` supports three legacy PtS permissions and restricted PtS/Content callers; no KDG checks or admission registry |
| Sign-in/session client | `apps/pts/web/src/auth.ts` | Supabase sign-in, app-specific storage, bounded requests, same-user return validation; not offline authorization or KDG provider configuration |
| React/Vite/shadcn lineage | `apps/pts/web/package.json`, `apps/expense/web/package.json`, Expense local UI components | Packages have differing pins; retaining stack is appropriate, copying unverified templates is not |
| Shared UI | `platform/ui-business/src/index.ts` and AppLauncher components | Launcher exists; `platform/ui-core` is a placeholder; generic sync/form/offline controls absent |
| Discovery | `services/app-directory/routers/apps.py` | `/me/apps` returns enabled catalogue entries to signed-in callers; JWT context and ungated `/apps` do not satisfy accepted current admission |
| Migration/release coordinator | `platform/deployment/release.py`, release/migration tests | Existing ordered migration/failure handling can be reused; KDG owner registration, fixtures and release verification absent |
| Scaffold | `platform/builder-cli/README.md`, `templates/web/` | Placeholder CLI, no runnable generator or generation suite; templates have omissions and unverified TypeScript pin |
| Offline PWA | Repository search of apps/platform/services for serviceWorker, IndexedDB and vite-plugin-pwa | No implemented foundation located; mobile screenshots are not evidence of an installable PWA |

Do not adopt Expense's legacy browser business-role RPC or full-session logging in
`apps/expense/web/src/contexts/AuthContext.tsx`. Those violate the new consumer's
API/logging direction. No runtime audit/refactor is performed in this planning item.

## Accepted designs, not runtime evidence

Accepted platform ADRs remain immutable; link the [ADR index](../../../platform/docs/architecture/decisions/README.md).
Relevant constraints: 0001–0003 API/Auth/silo; 0007 promotion; 0009–0010 BMAD/ATDD;
0011 roles; 0012–0013 operations/revisions; 0014–0018 DB/migrations/runtime/RLS;
0019–0023 authorization, release safety, execution, transactions, logging; 0025
attribution; 0028 queued-version compatibility; 0031–0033 errors/session/drafts;
0035 constraints; 0039 organization; 0046/0053 admission/capability scope;
0050–0051 saving; 0056 actors; 0057 onboarding; 0059 scaffold inputs.

The [identity/access contract](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
explicitly states canonical `/v2/check` is unimplemented. Its closed success union
currently contains PtS account and Leave organization-own-person variants. KDG needs
an organization variant using account/actor/membership, without person/employment.
The [admission contract](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md)
and [controlled provisioning contract](../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md)
remain subject to concrete schemas, operator identity binding and validation.

## Minimum dependency register and ownership

User-appointed coordinator: this KDG session. Component ownership below is the existing
repository boundary, not a claim that another session accepted a handoff.

| ID | Existing / remaining | Owner and reference | KDG independence / gate |
| --- | --- | --- | --- |
| P-ID | Legacy identity/membership exists; adopted baseline, stable account actors, current membership lifecycle/read and trusted operator adapter remain | Identity maintainer, existing Leave ID-A/ID-B; ADR-0015/0056; identity migration inventory and controlled provisioning contracts | KDG needs account actor + membership only. Can consume bounded owner delivery without People/person links; shared handoff first |
| P-ACCESS | v1 exists; capability registry, org enablement, exact grants, current v2 KDG variant/caller policy remain | Existing services/access owner; Leave ACCESS-A/B; ADR-0011/0019/0046/0053 | Required before server-backed slice; do once with Leave/PtS consumer compatibility |
| P-SCAFFOLD | Templates exist; runnable minimal app/service generator, schema-validated recipe, API clients, restricted owned-write/RLS pattern and generation tests remain | Platform builder/environment owner; Leave ENV/P1/SERVICE/WRITE; ADR-0007/0014–0018/0059 | Reuse minimum applicable foundation, exclude optional People/Content/worker features; no second generator |
| P-ENV | Release coordinator exists; isolated local/CI target, callback/provider fixture, compatible pins, shared-owner migration registration remain | Platform environment/release owner; ADR-0020; Leave testing/e1-environment-and-dependencies.md | Physical-device proof needs a reachable nonproduction HTTPS target; hosted verification app is not a prerequisite |
| P-SETUP | Accepted owner-local operator design; executable account/membership/grant setup not yet delivered | Identity and Access respective owners; controlled provisioning contract | Initial named user must bind to verified account, not name/email guessing. KDG owns child/version/assignment setup separately |
| P-INVITE | Invitation/default-off trusted enrollment accepted; normal onboarding wire/provider/lifecycle not finished | Identity owner; ADR-0057/0058 | First one-user slice can use restricted bootstrap. Normal new facilitator onboarding must wait for its bounded shared invitation delivery; automatic enrollment/prepared grants unnecessary for MVP |
| P-DIRECTORY | Catalogue/listing exists; current Access-filtered listing not delivered | Directory/Access owner; ADR-0046/0053 | Direct KDG URL avoids a launcher dependency. Do not publish a protected launcher entry until its checks work |
| P-OFFLINE | No reusable implementation; KDG first consumer must prove bounded storage/queue/update/status/test helpers | KDG delivers, platform coordinator promotes proven neutral mechanisms | Can plan independently; shared changes follow handoff agreement, not all Leave planning |

Before any shared mutation, give Leave the register with exact proposed owner/story
boundaries; record its acknowledgement and relinquished/retained first-consumer work.
Agree ownership for schema/API/client fixtures and generator promotion. No shared
contract is edited in this package. If handoff is unavailable, app planning continues
and shared implementation stays gated. Do not copy Leave's requirements, rewrite its
first slice, or treat its unfinished contracts as completed.

## Proposed shared delivery order for the first KDG slice

This is a handoff proposal, not agreement with the concurrent Leave session. Existing
owner story IDs remain authoritative; no shared implementation story is duplicated here.

| Order | Existing owner work | Minimum consumer evidence / timing |
| --- | --- | --- |
| 0 | KDG coordinator + Leave/platform owners | Acknowledge owner/story boundaries, common working-tree baseline and first-consumer promotion responsibility before any shared mutation |
| 1 | P-ENV and minimum P-SCAFFOLD | Isolated local/CI target, supported Auth callback, coherent web/API generation and typed errors; sufficient for online entry without optional employment/Content/worker generation |
| 2 | P-ID | Verified Identity migration ownership/baseline, stable account actor/current membership and restricted synthetic fixture commands; no person/employment linkage required |
| 3 | P-ACCESS configuration and current checks | KDG capability/default-role registry, global/Khula enablement, exact membership-bound grant, KDG caller/resource variant and current v2 check/negative fixtures; retain coordinated supported consumers |
| 4 | P-SETUP owner verification | Provision synthetic account/actor/membership and explicit KDG role through each owner's trusted command; verify effective current entry, not just setup receipts |
| 5 | KDG Story 1.1 | Real app online sign-in/current fixed-org entry consumes those delivered foundations; domain setup remains a later independent KDG increment |
| Before domain write slice | P-WRITE proof within existing scaffold/write ownership | Restricted app runtime role, tenant-local context/RLS, atomic operation/revision/attribution and controlled migrations before KDG capture persistence; not an artificial prerequisite for the read-only context endpoint |

After this baseline, KDG owns the initial questionnaire/child/assignment setup and PWA
capture/sync proof. Shared offline pattern promotion follows KDG evidence through the
agreed platform owner. P-INVITE is needed for normal added-facilitator onboarding later;
P-DIRECTORY is optional until launcher publication. Neither blocks one-user direct entry.

Handoff acknowledgement must identify retained/transferred work and who updates shared
schemas/clients/generator/tests/runbooks. Runtime delivery and migration prerequisites
remain required before their consumer; no source design is marked operational by this order.

## Assignment target-verification handoff

Story 1.3 requires current verified target account/Khula membership/capture-capability
evidence from existing Identity/Access owners for its protected setup command. Canonical
v2 user checks derive subject from bearer, so operator identity cannot act as a target
selector. No supported narrow operator target-check wire has been established for KDG
in this package. Resolve its policy/models/fixture evidence with shared owners before
Build; do not query their tables, infer from names/emails or use People as a workaround.
KDG's assignment remains a non-authorizing local domain association.

## Working-tree preservation

Read the uncommitted `apps/leave/docs/implementation-plan.md`, global
`_bmad-output/planning-artifacts/epics.md`, and untracked
`apps/leave/docs/planning-handoff-e3.md`. Preserve those and the unrelated modified
`apps/pts/backend/acquisition_catalogue.json`. No separate worktree was created;
therefore accepted and uncommitted planning inputs remain available. Delivery should
capture a reviewed common baseline before creating a separate implementation worktree.

## Technical feasibility sources

Native IndexedDB offers transactional structured storage and a strict durability hint;
physical-device checks must establish actual browser behavior. [W3C IndexedDB](https://www.w3.org/TR/IndexedDB/).
Home-screen installation can influence persistent-storage permission, but browser quotas,
eviction and user deletion remain practical constraints. [WebKit storage policy](https://webkit.org/blog/14403/updates-to-storage-policy/).
Manifest name/start URL/scope support install identity; use no personal data in those
values. [W3C manifest](https://www.w3.org/TR/appmanifest/).
Vite PWA is a candidate build adapter; its automatic reload can interrupt forms, so the
proposal uses deferred prompt updates. No package/version is approved or installed.
[Vite PWA update guidance](https://vite-pwa-org.netlify.app/guide/auto-update).
Retained Supabase Azure sign-in needs verified provider and redirect configuration;
provider authentication does not establish Khula membership.
[Supabase Azure](https://supabase.com/docs/guides/auth/social-login/auth-azure).
