# Authenticated profile columns — bounded ID-B evidence

2026-10-20. Build: `_bmad-output/implementation-artifacts/spec-id-b-profile-fields.md`.
Baseline: `630d1ae86db175c10806a3c3e3662962052aa978`.

Revision8 narrows authenticated INSERT to id/username and UPDATE to username/deleted_at.
Table and explicit column write grants are revoked before exact grants. Effective
PUBLIC/inherited rights fail closed. Existing SELECT absence, DELETE rights, RLS,
Auth hook, shared audit routines, postgres seeds and trusted service_role remain.
No account provisioning, new lifecycle, login/credential, dependency or service.

## Requirement to executed evidence

| Requirement | Proof |
| --- | --- |
| Characterize before narrowing existing grants | Root `characterize.py`, exact committed head7 source, `characterization.json` |
| Protected same-value/mixed/update/insert/upsert refusal; no partial effects | `qualify_profile_fields.py` actual restricted-login matrix and complete Identity row/audit hashes |
| Existing allowed edits/insert, attribution, RLS, helper/service role | Same actual role matrix, source-preserved hooks/defaults/catalog |
| Clean/adoption/head7/no-op/drift/failure/unknown history | Same existing real Alembic route and owner canonical checks |
| Immutable previous source and trusted generated reference | Previous17 exact Git bytes, rollback-only existing recorder, independent new profile pin |

Root proof: `platform/deployment/.local/identity-baseline/profile-fields-vt3hulju/`.
Eight fresh scratch databases use ida_99b7231c0a5b_profile1_ prefix on the retained
native run99b7231c-0a5b-4bdb-98e8-3329564c526a. No existing data/resources removed.
2612 protected original source files are hashed before work. Previous17 files are exact
baseline Git source; previous/failure/unknown execute that unchanged head7 first.

Head7 actual observation: effective table SELECT false, INSERT/UPDATE true. Filtered
username UPDATE refuses42501; unfiltered username, soft-delete and unretire each affect
one self row under RLS. Protected admin/creation-time UPDATE and forged INSERT succeed.
Each characterization operation is rolled back. Missing-profile Auth stub precedes
hook installation; later synthetic Auth inserts exercise the original profile hook.
No new SELECT is supplied to make filtered profile operations work.

Root supplies only synthetic Auth stubs and Auth-schema USAGE matching vendor execution.
Restricted access_runtime LOGIN temporarily SETs authenticated/service_role through
non-inherited SET-only fixture edges; durable private restoration witnesses retain exact
before/after edges. This models database-role execution, not provider/JWT/HTTP verification.
Existing legacy admin RLS still permits its supported profile writes; spoofed admin claims
cannot bypass protected-column ACLs. Live legacy adoption remains separate work.

Existing rollback-only recorder generates profile-reference.json SHA256
66895c8472028250e485fd4ef80846160ec014e6619ba07048fbb5c85f78925e.
Only the new pin is set afterward. All seven historical revisions/references/source pins
remain unchanged. Recorder receipt captures source chain and post-rollback checks.

## Commands and limits

```sh
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/profile-fields-vt3hulju "$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-profile-reference
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/profile-fields-vt3hulju "$OWNER_PYTHON" -I -B services/access/tests/qualify_profile_fields.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Existing frozen Python3.15.0/SQLAlchemy2.1.4/Alembic1.20.0/Psycopg3.3.6/rfc87850.1.4/
pytest9.1.1 are reused. No install/lock change; TypeScript7.0.2 remains selected.
CPU ATDD RED: six focused failures before implementation; subsequent focused suite passes.
Initial actual matrix fails2.56s with source unchanged, retained initial-actual-execution.json:
wrong-account INSERT targeted an already present PK and received23505 before RLS42501.
Diagnostic confirms SQLSTATE without payload/credentials; temporary edges restore exactly.
Fix targets an Auth-backed missing profile and distinguishes retained legacy admin RLS.
No unexplained expectation change or production policy relaxation is permitted.

## Five impacts

Scaffold: extend the existing owner revision/reference/qualifier pattern; no generator.
Shared UI: none. Agent context: existing policy suffices. Documentation: owner runbook,
this evidence, Build, KDG navigation and ownership inventory. ADR: existing ownership,
structural, attribution and release decisions apply unchanged; none superseded.

No frontend change, root build claim, hosted CI/provider/production verification or full
Identity/Access/WRITE/KDG readiness. Original sources, failed frames and resources retained.


## Actual fixture corrections and complete acceptance

Second initial-frame matrix fails13.641s at PUBLIC preflight: the preexisting authority
role guard correctly rejects PUBLIC writes before catalog comparison. Direct live profile
verifier assertions now separately establish the new effective-column refusal. Fresh
profile-fields-final-5q4hk4h8 matrix fails35.516s after successful write/adopt/previous/
PUBLIC/atomic rollback checks: removing a fixture's broad authenticated INSERT also
removes original column INSERT grants. Exact allowed columns are restored and complete
ACL bytes compared. Root records the controlled fixture recovery; subsequent inherited
privilege/refusal/restoration and unknown-history tail passes. All failures are retained.

Complete fresh frame profile-fields-accepted-ds2j_k23: PASS54.756s, source unchanged,
including all corrected fixtures. Original executed source is retained under accepted-source.
Affected regression462 PASS21.68s, no skips; both composer routes exit0. Only profile ACL
catalog categories differ from the immutable previous head; hooks/audit/defaults/RLS and
current-account/target function contracts are unchanged. This proves retained catalog
compatibility and synthetic hook/role behavior, not a new native Auth/provider sequence.

Reviewed-source final result and preservation receipts follow.


Before review an inaccurate SQL comment is corrected; SQL behavior is unchanged. The
initial generated reference and executed revision bytes are retained, and the existing
rollback-only recorder regenerates only the uncommitted profile reference with SHA256
05ccb6afc5c546d18ea16747a59d4e63c6f8576718d885b43ecc03e676779868.
All seven prior references/revisions remain immutable. The live full catalog compatibility
assertion passes against the new pin; no generated artifact is hand edited.


## Final reviewed-source result

Three independent BMAD review layers complete: Blind10 findings, Edge0, Verification0.
One finding is disproved by the preceding canonical anon privilege check; nine local
verification/recovery corrections are applied and verified. Each verdict/evidence is
recorded separately in the Build triage log. No deferred or unresolved findings.

Final fresh retained frame:
`platform/deployment/.local/identity-baseline/profile-fields-reviewed-y531afuh/`.
Exact committed head7 source/characterization repeats before8. Full actual matrix
**PASS43.923s**,22 named stages, source_unchanged true (actual-execution.json and
identity-qualification.json). Source includes final pin and all review corrections.
The matrix now proves same-value writes for every protected UPDATE column, independent
trusted-context spoof attempts, exact new audit IDs/actors/operations/targets, creation
attribution preservation and advancing update timestamp, actual pool return/recheckout
with a different account and cleared app/JWT context, and rollback-only trusted service
INSERT/default/audit compatibility. Private pre-mutation ACL/event/role witnesses and
exact restored receipts accompany all committed fixture mutations; SQL/lock deadlines
apply during cleanup. Injected post-grant/create and snapshot failures have focused
exception/restoration regression coverage.

Final affected suite: **474 PASS17.74s, no skips**, affected-suite.log. Both composer
routes exit0 in composer-legacy.log/composer-owned.log; diff whitespace check passes.
The accepted earlier source and every failed frame/log remain. No original migration,
reference, source pin, lock or concurrent document is replaced.

Normal native stop and final source/protection/secret-absence receipts are retained in
this final frame. Concurrent brainstorming memlog edits observed during the session are
preserved separately from intended changed source. No reset, prune, synthetic database
removal, production/provider/account/access operation, hosted CI, deployment or push.

Final preservation-audit.json verifies2612 originals: none missing, seven intended existing
files changed, one concurrent brainstorming memlog preserved and zero unexpected changes.
Executed source matches current bytes. safe-output-check.json confirms credential URLs,
tokens and password-bearing forms absent from selected outputs; literal short vendor
password coincidences in legitimate role names are excluded. native-stop.json reports
completed/ok with runtime_ready false and retained data. Final source manifest and
reviewed diff are retained; a scoped local commit records this increment only.
