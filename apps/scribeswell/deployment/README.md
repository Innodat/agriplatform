# Direct PostgreSQL transition — prepared, not executed

Production execution requires separate approval of the concrete target, grants,
credentials, configuration, import/verification, activation and recovery plan. Local
implementation does not authorize production SQL, source imports, deployment or
Data API schema removal. Follow platform ADR-0020 and ADR-0023.

Prepare:

1. Inventory every current `scribeswell` and `identity` Data API consumer. Directory
   uses Auth `/auth/v1/user` plus verified claims and its static catalogue; it needs
   no database key. The new Scribeswell API/importer use PostgreSQL exclusively.
2. Rehearse the existing migration followed by `bootstrap/001_direct_database_roles.sql`
   on disposable PostgreSQL with representative data. The bootstrap is an additive,
   idempotent, transaction-wrapped operation with an advisory lock and finite waits.
   It preserves existing tables, IDs, views and old service-role grants. Existing
   elevated roles, memberships, ownership or unexpected table authority fail closed.
   Review PUBLIC/default grants and callable security-definer functions on the actual
   target too: PostgreSQL cannot deny an individual role access granted to PUBLIC.
   Any unexpected target authority must be resolved in the approved target plan.
3. Prepare separate role credentials outside SQL/version control. Runtime receives
   only `SCRIBESWELL_DATABASE_URL` as `scribeswell_runtime`; operator receives
   `SCRIBESWELL_IMPORT_DATABASE_URL` as `scribeswell_import`. Use approved project
   host and TLS. Import role may select/insert/update the five owned tables and use
   their sequences; neither role owns tables or bypasses RLS, and runtime cannot write.
4. Review the exact role SQL, previous-version checks and recovery evidence. The
   deployment registry fingerprints this bootstrap path, invalidating stale bootstrap
   evidence. Host preflight checks runtime project/role and rejects old service keys
   before image activation. It does not apply role SQL or configure passwords.

Apply and verify, only after approval:

1. Apply the reviewed bootstrap with deployment authority, then provision passwords
   using the approved secret channel. If SQL fails, stop activation and reconcile;
   do not automatically reverse prior migrations or revoke old consumers.
2. Perform full canonical dry-run (39 books, 929 chapters, 23213 verses, 306785 words,
   471674 morphemes). Run `seed.py --verify-only` with restricted import authority;
   any approved repair/import is explicit and must finish with a full source audit.
3. Check actual logins, RLS and denials for writes/cross-owner data. Test public books,
   long chapters, morphology, roots/lexicon, occurrence filtering/pagination and missing
   data. Verify shared sign-in/directory and PtS/Auth/Storage remain healthy.
4. Replace runtime env with the reviewed TLS URL and remove service-role keys.
   Record fresh bootstrap/compatibility evidence and deploy the immutable reviewed
   image through the serialized host release. Failure blocks activation.
5. Only after all affected consumers pass, separately approve removal of `scribeswell`
   (and any no-longer-used `identity`) from Data API exposed schemas. Re-run HTTP,
   corpus audit, Auth and Storage acceptance with only public/graphql_public exposed.

Recovery:

Keep the previous image and its private runtime configuration available until
cutover acceptance. Role installation is additive, so before schema unexposure the
previous runtime remains compatible. Restore its reviewed configuration/image only
after checking current database compatibility. After unexposure, restoring the old
PostgREST runtime also requires separately approved restoration of schema exposure.
Do not delete corpus rows, reverse applied schema changes or revoke unrelated grants.
Interrupted imports can be resumed by book; a failed chapter rolls back while prior
chapters and stable IDs remain. Retain source hash, exact commands, counts and safe
release evidence; never capture passwords, SQL parameters or raw database errors.

Image inventory: FastAPI backend, reviewed Hebrew source, lexicon artifacts, seed
wrapper and importer/decoder. The importer is an explicit operator command, never
startup behavior. Runtime image has no credentials; runtime preflight rejects import
URLs. Supabase Auth/shared browser sign-in and public API shapes remain unchanged.

## Production permission inventory — 2026-09-29

Read-only inspection of `gjbsnxmbhxsvcblzgfts` found neither new Scribeswell role.
The target has PUBLIC execute on several legacy security-definer functions. Only
`public.get_user_roles()` also has PUBLIC schema USAGE; identity/finance schemas
have no PUBLIC USAGE. Its live definition reads identity membership roles using
`auth.jwt()` claims, which a direct PostgreSQL session can set. Therefore the new
roles must not inherit its execution privilege, even though a connection with no
claims ordinarily returns no rows.

Before installing the new roles, prepare a separately approved target correction:
revoke PUBLIC execute on exactly `public.get_user_roles()`, preserve explicit
`authenticated` access (the Expense frontend calls it), and inventory/preserve any
other legitimate existing callers. Verify effective permission denial for both new
roles and continued authenticated execution authority. Do not globally revoke
PUBLIC function privileges or change the unrelated legacy functions. Retain prior
ACL evidence for recovery. This is a pending production gate, not an applied change.
