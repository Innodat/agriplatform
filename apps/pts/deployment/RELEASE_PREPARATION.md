# First PtS and Scribes’ Well production release

Application preparation only; infrastructure status updated 28 September 2026.
The approved Hetzner host and firewall now exist; no production database connection,
schema change, application-account creation, upload, DNS change or public app deployment
has been performed. The owner selected Supabase project `gjbsnxmbhxsvcblzgfts`
(`https://gjbsnxmbhxsvcblzgfts.supabase.co`). The owner confirms Pro in West EU (Ireland); its existing schema and data have
not been inspected. The owner confirmed `scribeswell.com`, prefers Netlify Free for the frontend
(or hosting it on the backend server), and Hetzner for the APIs and future workers.
APISIX is the requested gateway; DNS is managed at Dynadot. Netlify and Hetzner accounts are ready; the
initial size is CPX12 (1 shared vCPU, 2 GB RAM), subject to actual capacity checks.
Host provisioned in Nuremberg; trusted SSH identity and host bootstrap are verified.
Runtime configuration remains pending. See [production status](../../../platform/deployment/PRODUCTION_STATUS.md).
The owner requires platform-wide CI/CD and has chosen production only for the first
release: main deploys production after all checks; no staging server or branch is needed.
Shared implementation: [original deployment evidence](../../../platform/deployment/SPEC.md);
current scope: [production-only adjustment](../../../platform/deployment/PRODUCTION_ONLY.md).
This checklist accompanies the existing owner tooling; it is not a new deployment
system or an authorization to execute production writes.

## Runtime and routing inventory

Serve both frontends on one trusted HTTPS origin to retain shared sign-in:
PtS at `/` and Scribes’ Well at `/scribeswell/`. Build each app separately; the
root npm build is not a platform build. Development Vite proxies are not a
production gateway.

| Component | Runtime / route | Release requirement |
| --- | --- | --- |
| PtS web | `apps/pts/web/dist`, root SPA | Public Auth key only; canonical API/directory URLs |
| Scribeswell web | `apps/scribeswell/web/dist`, `/scribeswell/` SPA | `VITE_APP_BASE=/scribeswell/`; same Supabase project/origin |
| PtS API | `apps.pts.backend.main:app`; `/api/poetry`, `/api/sources`, `/api/exports`, `/api/documents/*` | Restricted runtime DB login; access and content HTTP services |
| Scribeswell API | `main:app` in `apps/scribeswell/backend`; `/api/bible/*` | Gateway forwards `/scribeswell/api/bible/*` with `/scribeswell` removed; server-only Supabase key |
| App directory | `main:app` in `services/app-directory`; `/api/me/*`, `/api/apps` | Canonical `APP_URL_PTS` and `APP_URL_SCRIBESWELL`; project Auth/identity configuration |
| Access | `main:app` in `services/access` | Private service network, narrow runtime DB login and service credentials |
| Content | `main:app` in `services/content-service` | Private service network, private bucket and server-only S3 credentials |
| Supabase | Existing selected hosted project, or separately approved target | PostgreSQL, Auth and Storage; no new standalone database |

Exact public API prefixes and service ingress rules will be rendered for the
selected host. Static publication must use only built frontend artifacts, never
the repository root. Keep `apps/pts/reference/poetry-library`, env files, source
PDFs, credentials and migration tooling outside public web roots. The Scribeswell
API release includes `data/hebrew-lexicon` and `scripts/hebrew.json` as documented
in its [artifact build notes](../../scribeswell/data/hebrew-lexicon/BUILD.md).

## Database, identity and collected material

1. Identify the exact project and inspect its migration history/read-only state.
   Establish a recovery point and test restoration before schema changes. Record
   release revision, existing consumers, compatibility and recovery evidence under
   [ADR-0020](../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md).
2. Review the composed platform identity and Scribeswell migrations against that
   state. `python3 tools/py/run_compose_supabase.py --check-only` passes locally but
   does not establish target compatibility. Do not run the legacy
   `scripts/deploy.sh`: it blindly pushes/seeds and is not a coordinated release.
3. Follow [PtS initial deployment preparation](../README.md#explicit-initial-deployment-preparation)
   for owner/runtime roles, identity bridge and the access → content → PtS
   migration coordinator. Preserve its per-owner outcome evidence and block
   activation on failure. It does not apply the platform/Scribeswell histories;
   those require explicit ordered steps in the target-specific release plan.
   Never reset production or auto-downgrade after partial migration.
4. Provision organization **PtS**, description **Psalms that Sings**, from
   `organization.json`. Resolve production Auth identities; do not copy local
   account UUIDs or credentials. Grant membership and the explicit PtS Reader
   permissions through their owners. See the
   [organization provisioning checklist](../docs/LOCAL_AUTH_CONNECTIVITY.md#requested-organization-and-production-release).
5. Configure Auth Site URL, allowed recovery/invite callback, mail delivery and
   disabled public signup for administrator-provisioned accounts. Microsoft is
   optional. Verify sign-in, recovery and cross-app sign-out on the final origin.
6. Use a private Storage bucket with global and bucket limits of at least 128 MiB.
   The existing approximately 85 MiB PDF exceeds hosted Supabase Free's 50 MB
   per-file cap. Hosted Supabase requires Pro or higher for this file; confirm the
   selected project's plan before uploads. [Official file limits](https://supabase.com/docs/guides/storage/uploads/file-limits).
   Verify actual signed upload/download expiry, byte integrity and replay behavior
   through the Content owner before activation.
7. Import only the canonical existing poetry JSON and the library's source files
   using the existing restricted import/upload tools. Expected: 312 records,
   190 with text, 33 assistant-checked complete transcriptions, 275 witnesses and
   19 source/rights pairs. Repeated import must preserve reviewed content; conflicts
   stop for deliberate review. Preserve all notices/restrictions; authorization to
   access the app does not confer permission to redistribute a source.
8. If the target lacks Bible data, use the existing Scribeswell importer against
   the checked-in corpus after approval, then `--verify-only`; if already present,
   audit before any write. Expected: 39 books, 929 chapters, 23,213 verses,
   306,785 words and 471,674 morphemes. The canonical decoder now corrects participle
   and Aramaic features; an existing older import may need a separately reviewed
   derived-data refresh. Never dismiss an audit discrepancy by changing expectations.

## Activation evidence

Build using explicit production configuration, without inheriting local `.env.local`
values. Test the packaged gateway and APIs before changing public routing: direct
SPA links and refresh; public Bible reading, comparison, focus mode, dictionary
links/Back and occurrences; shared Auth; PtS search/filters/citations/exports/PDFs;
anonymous and unauthorized denial of all protected data and documents. Verify
signed URLs, private bucket policy, revocation and organization isolation on the
actual provider, not solely browser fixtures. Keep operational logs free of tokens,
signed URLs and protected source content.

The latest inspector UI changes require no new migration. The first application
release still needs the existing schemas, organization, content and infrastructure
above. Final approval must identify the actual target, code revision, proposed
mutations, verification evidence and recovery action before production writes or
public activation, following the user's explicit instruction.
