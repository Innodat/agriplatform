# PtS · Swahili Poetry

Protected React reader and FastAPI API for the existing collection, with minimal
shared current-access and private-content owners. Production uses the **existing
Supabase PostgreSQL, Auth and Storage project**. The standalone PostgreSQL container
used in verification is a disposable test fixture only.

For the prepared local Supabase environment, see [sign-in, testing and restart instructions](docs/LOCAL_SETUP.md).

## Local dependencies and commands

From the repository root, create an isolated environment and install the requirements:

```bash
uv venv /tmp/pts-venv
uv pip install --python /tmp/pts-venv/bin/python -r apps/pts/requirements.txt
npm install --prefix apps/pts/web
python3 tools/py/run_compose_supabase.py --check-only
/tmp/pts-venv/bin/python -m apps.pts.tools.verify_archive
```

The original `/mnt/c/wycliffe/PtS/PtS_Poetry_Library` is read-only. Its local copy in
`reference/poetry-library` is deliberately ignored. Do not stage it, publish it, or
serve it with a generic static server. Only the checksum manifest is publishable.
A fresh checkout needs an authorized copy verified by the manifest before import.
Do not use the HTML/SQLite/JSONL alternative snapshots as extra collection rows.

`apps/pts/.env.example` is a configuration catalogue, not an automatically loaded
runtime file. Assign only the variables needed by each process; never source the
entire catalogue into an API. Generate distinct secrets and use TLS between deployed
services. The browser gets only public Supabase Auth configuration and API URLs from
`web/.env.example`. Configure Entra federation and an allowed callback for the reader.
Organization selection comes from current app-directory context or a validated UUID
in a deep link; it never proves access.

| Process | Required server configuration |
|---|---|
| PtS API | PTS_DATABASE_URL, ACCESS_URL, CONTENT_URL, PTS_SERVICE_KEY, PTS_CORS_ORIGINS |
| Access API | ACCESS_DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, PTS_SERVICE_KEY, CONTENT_SERVICE_KEY |
| Content API | CONTENT_DATABASE_URL, ACCESS_URL, CONTENT_SERVICE_KEY, PTS_SERVICE_KEY, PTS_IMPORT_SERVICE_KEY, PTS_IMPORT_ORG_ID, CONTENT_BUCKET, CONTENT_S3_ENDPOINT/REGION/ACCESS_KEY/SECRET_KEY |
| Importer | PTS_IMPORT_DATABASE_URL, CONTENT_URL, PTS_IMPORT_SERVICE_KEY |
| Deployment only | ACCESS_MIGRATION_DATABASE_URL, CONTENT_MIGRATION_DATABASE_URL, PTS_MIGRATION_DATABASE_URL |

Run each API separately, with its own environment (these commands do not migrate):

```bash
/tmp/pts-venv/bin/uvicorn apps.pts.backend.main:app --port 8010 --no-access-log
/tmp/pts-venv/bin/uvicorn main:app --app-dir services/access --port 8011 --no-access-log
/tmp/pts-venv/bin/uvicorn main:app --app-dir services/content-service --port 8012 --no-access-log
npm run dev --prefix apps/pts/web
```

Set `APP_URL_PTS` on app-directory; the default development URL is localhost:5179.
The launcher provides navigation, never PtS authorization. No changes to legacy
Expense or Scribeswell business/storage routes are needed.

## Explicit initial deployment preparation

No deployment, production grants, or Supabase mutation has been executed here.
The following are operator actions against a deliberately selected target, requiring
normal production/destructive-change authorization:

1. Back up the existing Supabase database and record a tested recovery point. Review
   `tools/bootstrap_roles.sql`, provision separate restricted LOGIN credentials and
   schemas, and keep migrator credentials out of APIs. The file intentionally
   creates no passwords and is not blindly replayable against an existing deployment.
   Supabase administrators are not PostgreSQL superusers: after creating the owner
   roles and before creating their schemas, grant the three migrator roles to the
   provisioning administrator so it can assign schema ownership. The local setup
   used `GRANT pts_migrator, access_migrator, content_migrator TO postgres`.
   Do not grant these owner roles to API or importer logins.
2. Apply `services/access/tools/identity_bridge.sql` through the identity owner after
   existing identity migrations. It grants only current organization/member columns
   and adds actor/organization-scoped read policies for access_runtime.
3. Set all three migration URLs and run the coordinator with a fresh evidence path:

   ```bash
   /tmp/pts-venv/bin/python tools/py/deploy_pts.py --release-id REVIEWED_RELEASE --evidence /tmp/pts-release-REVIEWED_RELEASE.json
   ```

4. Provision explicit application grants for the authorized organization/user through
   a reviewed access-owner operation. The maintained Reader permission set is
   `pts.poetry.read`, `pts.poetry.export`, `pts.poetry.documents`. No default reader,
   email allowlist, production UUID or admin bypass is invented. Each access.grants
   row needs organization, user, permission, ID and server actor context. Membership
   must also exist and be undeleted; new grants do not create membership.
5. Create a private Supabase Storage bucket and configure both global and bucket
   size limits for 128 MiB. Give S3 credentials only to Content. Configure signed
   transfers/CORS for the intended origins. With a deployment-only storage admin
   token, run `services/content-service/verify_configuration.py` for the read-only
   bucket check. Verify actual S3 upload expiry (900 seconds), read expiry (300
   seconds), clock tolerance, in-flight behavior and staging replay immutability.
6. Import canonical objects using the restricted importer identity:

   ```bash
   /tmp/pts-venv/bin/python -m apps.pts.tools.import_library --source apps/pts/reference/poetry-library/library.json --org AUTHORIZED_ORGANIZATION_UUID
   /tmp/pts-venv/bin/python -m apps.pts.tools.upload_sources --library apps/pts/reference/poetry-library/library.json --org AUTHORIZED_ORGANIZATION_UUID
   ```

   Repeat safely after an interrupted association. Conflicting records never replace
   stored objects; imports return exit code 2 and preserve incoming versions for
   deliberate review. Resolve them through a separately authorized correction, not
   by editing expected tests or discarding evidence.
7. Run checks in `docs/VERIFICATION.md`, including configured Supabase provider and
   auth checks before activation. Migration success is necessary, not sufficient.
   Public deployment still requires approval and an appropriate rights decision.

## Failure and recovery

A migration failure stops later owners. Evidence always records `activation_allowed: false`;
`migrations_complete` describes only migration completion. The report includes code
revision, dirty-tree status and each owner’s before/after revisions and outcome.
Keep the previous compatible application active. Preserve all applied revisions and
source bytes. Correct the failure with a forward migration/retry and a new release
identifier/evidence path; never automatically downgrade or reset the database.
Do not activate an incompatible application against partially migrated owners.

A pending upload retries with the same hash/content ID. A finalized upload retries
association without uploading again. No cleanup job deletes unassociated files.
If finalization is stuck in `finalizing`, stop the affected finalizer process and
reconcile provider completion first. Inspect the expected hash/size and the sealed
object; never overwrite sealed bytes. To retain a failed attempt and permit a new
identity for the same expected bytes, use content-owner recovery credentials:

```bash
/tmp/pts-venv/bin/python services/content-service/recover_failed.py --org ORGANIZATION_UUID --content-id CONTENT_UUID --actor AUTHORIZED_OPERATOR --finalizer-stopped-and-reconciled
```

`CONTENT_RECOVERY_DATABASE_URL` must use `content_migrator` authority and belongs
only to this explicit operator procedure. It marks a finalizing object `failed`,
records audit atomically and retains its bytes/metadata. Then repeat source upload;
it receives a fresh identity and must pass normal verification. Ready identities
cannot be abandoned or modified. No API runtime has this recovery authority.

A permission denial clears displayed content. A temporary dependency failure returns
retryable 503 without using stale claims. Signed URLs already issued can remain usable
until provider expiry; revocation does not erase downloaded copies.

See [owner design](docs/ARCHITECTURE.md), [specification](docs/SPEC.md) and
[verification evidence](docs/VERIFICATION.md). Original assistant checks are not human
verification, rights clearance, or training readiness.

## Reproduce isolated database verification

Use only a fresh disposable container; the test bootstrap deliberately refuses an
initialized database and requires localhost:55439. These commands do not use Supabase:

```bash
docker run --name pts-verification -e POSTGRES_PASSWORD=pts-disposable -p 127.0.0.1:55439:5432 -d postgres:17
export PTS_TEST_DATABASE_URL=postgresql+psycopg://postgres:pts-disposable@127.0.0.1:55439/postgres
export PTS_TEST_RUNTIME_URL=postgresql+psycopg://pts_runtime:pts-disposable@127.0.0.1:55439/postgres
/tmp/pts-venv/bin/python -m apps.pts.tools.prepare_test_database
/tmp/pts-venv/bin/python -m pytest apps/pts/tests -q
docker stop pts-verification
```

Wait for PostgreSQL readiness before bootstrapping. The fixture includes minimal
identity contracts and real restricted roles; run the separate configured Supabase
checks before deployment. Reuse an existing fixture with `docker start pts-verification`
and run tests without repeating bootstrap.
