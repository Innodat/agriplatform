# Leave authorized entry

Generated bounded web.leave-entry.v1 owner. Follow repository AGENTS.md and accepted ADRs. Business data uses Leave API; browser Supabase is Auth only, Microsoft azure provider with SDK PKCE. No password fallback. Normal sign-in never creates membership/grants. Entry needs no employment; employee actions retain setup checks. Independent tabs own their context.

Node26.11.1/npm12.2.0/Python3.15.0/uv0.13.1. Root workspace lock and independent api/uv.lock. In api/: uv sync --frozen --group test; uv run --frozen pytest; uv run --frozen python export_openapi.py. Root: npm run api:generate --workspace @scaffold/leave-web; api:check, test:entry, test:auth, type-check, build with the same workspace.

Runtime: LEAVE_DATABASE_URL must be leave_runtime; LEAVE_ACCESS_ORIGIN, LEAVE_SERVICE_KEY, LEAVE_CURRENT_SESSION_SERVICE_KEY and LEAVE_PREFERENCES_SERVICE_KEY are private. Web VITE_LEAVE_AUTH_URL/ANON_KEY are public Auth configuration. Callback is the exact current origin/auth/callback; allowlist deliberately outside generation.

Protected setup api/tools/prepare_roles.sql; separate nonlogin leave_owner, leave_migrator and leave_runtime. Controlled api/migrate.py with LEAVE_MIGRATION_DATABASE_URL before activation through platform release tooling. No startup migration, automatic downgrade or reset. Retain immutable selection events for this increment. Packaging uses api/package_production.py and explicit selected tools.

Scaffold: bounded entry composition and neutral Auth/HTTP/migration reuse. Shared UI: platform tokens/launcher; owner-specific picker. Agent context: generated guidance. Documentation: owner commands and evidence. ADR: existing accepted decisions suffice. Local synthetic proof does not establish Entra/device or hosted VERIFY; A1/E1 stay open.


## Optional draft preparation context

This owner explicitly adopts `api.leave-context.v1`. `GET /api/v1/organizations/{org_id}/me/draft-context`
is a private read-only observation using current Access authority and People ownership.
The browser displays loading, setup, editable/read-only, denied and retryable unavailable
states under current execution leases. No working draft or submission action exists.
Missing or invalid work timezone does not prevent otherwise authorized preparation.

Runtime additionally needs `LEAVE_PEOPLE_ORIGIN` (the fixed compose origin is
`http://people:8000`) and the distinct `LEAVE_PEOPLE_SERVICE_KEY`; configure the paired
People caller policy deliberately. Never put service credentials in browser inputs.
Controlled fixture/deployment setup installs `btree_gist` before Leave0003; migration
never bootstraps extensions. Runtime has scoped SELECT only on the four context records.
No settings/profiles are seeded on API startup and no E2 administration surface is added.

Run `test:context` in the web workspace and
`node platform/builder-cli/scripts/prove-leave-context.mjs` with the selected tools.
Actual evidence and remaining scope are in `apps/leave/docs/testing/e1-context-evidence.md`.
A real rollout needs a new Context migration/service/source plan; the earlier A1
c76b28e/0002-only activation packet stays unchanged.

## E1 Choices

The optional `api.leave-choices.v1` composition requires Context. GET
`/api/v1/organizations/{org_id}/draft-choices` uses current own-read only, fixed
100-item UUID pages and independent selected-ID resolution in one local snapshot.
It reads the explicit published pointer without selecting a policy by today.

Protected setup adds `leave_command_owner` (NOLOGIN) and `leave_operator` (restricted
LOGIN); grant the command owner only to `leave_owner` for controlled migration.
Temporarily grant schema CREATE for function ownership transfer, then revoke CREATE.
Bootstrap `leave.operator_principal` with an existing durable actor and exact
`leave.operator_authority` command/organization/optional-type entries using protected
owner custody. Runtime has SELECT only. No browser or public administrative write.

`api/operator_cli.py execute --target PRIVATE_TARGET --command-file COMMAND` and
`outcome --target PRIVATE_TARGET --command leave_type.create --operation-id UUID
--org-id UUID --type-id UUID` support guarded local/CI disposable targets only.
Target files must be mode0600 in an owned mode0700 directory, name the guarded run,
reference its verified environment target digest and hold the restricted operator URL.
Creation uses explicit type/version IDs, normalized code/name, modes/applicability and
expected absence; archive uses exact type/revision. Retry the same operation or look up
its outcome under current authority. Receipts prove configuration commits only.

The canonical input-v1 controlled choice component has a replaceable in-memory host.
There is no date/note editor, draft/save endpoint, saved feedback or submission. D1/D2
own actual guarded save/reopen. Run API `tests/test_draft_choices.py` and
`tests/test_leave_operator.py`, web `test:choices`, builder
`tests/leave-choices-generation.test.mjs` and `scripts/prove-leave-choices.mjs`.

D2-A adopted locally: optional api.leave-draft-input.v1 adds complete PUT input-v1
preservation and compact save outcomes; it does not add an editable form. Use
`npm run test:draft-input --workspace @scaffold/leave-web` and
`apps/leave/api/.venv/bin/python -m pytest apps/leave/api/tests/test_draft_input.py -q`.
The new native proof is `platform/builder-cli/scripts/prove-leave-draft-input.mjs`.
Migration0006 adds an exact input-version check after actual restricted-role0005
characterization; apply through the controlled migrator before activation. The previous
D1 writer/readers remain supported. Source/date and operation/revision guards retain
the original deadlines. Detailed evidence and remaining D2-B/hosted gates live in
`apps/leave/docs/testing/e1-d2-a-evidence.md`. No provider/grant change is required.

## D2-B protected HTTP transport

AccessClient and PeopleClient capture the exact HTTPX default verified TLS context at process start with `trust_env=False`. Each protected operation still creates and closes a fresh AsyncClient, sends current credentials and performs all current authority/People checks under the existing deadlines, response bounds and redirect rules. No client, session or authority-result cache is introduced. Trust configuration changes require controlled process replacement. The D2-B scaffold supplies these API seeds only for fresh generation; adoption preserves existing owner seeds, so this maintained owner was updated explicitly. Generated outbound_http.py and predecessor templates remain unchanged.

Draft preparation checks Current Session and the combined Leave read and manage
decision before People. Activate the additive Access endpoint before Leave. Roll back
Leave before removing the Access endpoint. Verify the selected HTTP contract with
`tests/test_draft_context.py`.
