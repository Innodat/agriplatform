# ENV Python dependency qualification — 2026-10-15

This qualifies the selected Python dependency graph in an isolated ENV test fixture,
under the existing [dependency baseline](../docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md)
and [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-python-baseline-qualification.md)
records implementation and review. It does not close runtime/bootstrap or P1/SERVICE.

## Actual qualified scope

Ordinary CPython3.15.0 and uv0.13.1 are the already qualified binaries from protected
run0cc4bc48-505e-41c1-8876-25b2d49b5694. The fixture resolves the exact approved FastAPI,
Uvicorn, Pydantic/settings, SQLAlchemy, Psycopg with binary extra, Alembic, HTTPX,
RFC8785 and PyJWT versions, plus pytest in its test-only group. No pin was downgraded.
TypeScript7.0.2 and existing owner/root manifests/locks remain unchanged.

Actual uv resolution against `https://pypi.org/simple` produced33 lock records, including
the virtual fixture;32 packages installed. The generated lock records publisher hashes
for transitives and artifacts. Linux x86_64 GNU/ordinary CPython3.15 is the supported
resolution target. Two fresh virtualenvs installed with `--frozen --no-build --link-mode
copy --no-install-project --group test`, explicit selected interpreter, clean environment
and private workspace cache; the second installed with `--offline`. Pydantic core2.50.1
and psycopg-binary3.3.6 installed from wheels and executed, including bundled libpq FFI.
No source build, substitute interpreter, global/owner virtualenv or application import
was used. These are fixture locks, not application/service dependency authority.

## Requirement-to-test evidence

| Requirement | test_baseline.py |
| --- | --- |
| Exact ordinary CPython/Linux target and direct pins actually loaded | test_selected_runtime_and_exact_direct_packages |
| Native validation, binary Psycopg/libpq and identifier escaping | test_native_validation_and_psycopg_binary_calls |
| Actual loopback Uvicorn/HTTPX valid/invalid HTTP, bounded teardown | test_real_uvicorn_httpx_valid_and_rejected_request |
| Explicit synthetic settings and invalid-value rejection | test_settings_validate_explicit_synthetic_environment |
| JWT signature/issuer/audience/expiry/algorithm checks | test_jwt_signature_issuer_audience_and_expiry_are_checked |
| Canonical bytes and nonfinite rejection | test_canonical_json_bytes_and_nonfinite_rejection |
| PostgreSQL compilation and Alembic offline transaction output | test_postgres_sql_and_alembic_offline_output_without_database |

Exact commands and isolation flags are in the
[fixture runbook](qualification/python/README.md). Before manifest/lock implementation,
the selected Python's pytest acceptance command exited1 with `No module named pytest`.
After lock resolution and wheel install, six tests passed in the normal sandbox and
the HTTP test failed on denied socket creation; it was not skipped or mocked. With
isolated loopback permission all seven passed in2.38s. Final second-install/review results are recorded below.

The initial sandbox metadata fetch failed DNS; the approved network retry resolved33
packages in3.39s. First wheel preparation took9.11s and installation416ms. A second
fresh virtualenv installed all32 packages offline in278ms. `uv lock --check --offline`
passed (33 packages,2ms). A copied temporary fixture with a changed FastAPI requirement
was refused by that check (exit1), and its lock bytes remained unchanged. No source
expectation was weakened to dismiss a dependency failure.

Final verified hashes:

- pyproject SHA256 `18b784117c7cecea314424561d109f4762defdf8225307af7fccacf59504bcfc`
- uv.lock SHA256 `2863e2fe9a3c680444445196510be2f2f94579f9abc5bebdf29bfe71b70ae809`

## Five impacts and limits

- **Scaffold:** ENV gains a disposable dependency compatibility fixture and generated
  hash lock. Independent owners/generator retain their own locks, packaging and subset
  choices; no runtime owner or candidate pattern is promoted.
- **Shared UI:** none; no frontend package, screen or saving behavior changes.
- **Agent context:** root rules suffice. The fixture/runbook lists actual tool/install/
  test commands and bounds; no generated application context exists.
- **Documentation:** this evidence and owner runbook plus KDG navigation/memlog distinguish
  package execution from owner/runtime readiness.
- **ADR:** existing ownership/scaffold/ATDD/release decisions govern; no new decision
  or edit to an accepted ADR is needed.

This is a synthetic compatibility probe, not a deployable service, shared Identity/
Access/WRITE implementation, owner schema or migration test. PostgreSQL/Alembic output
was compiled offline; no database connection or SQL execution occurred. JWT checks do
not establish current admission/grants or all shared verification policies. Linux host
wheel success is not container-image, deployment-target or other-architecture proof.

Docker>=28 and run-owned loopback isolation, complete publisher image identities,
deployed PostgreSQL compatibility, owner locks, controlled migration/adoption/fixture
coordination, actual Auth/provider/device and generator/consumer proof remain open.
No runtime-ready receipt, daemon upgrade/startup, production migration/account/access
change, infrastructure, deployment, Leave/KDG domain/editor or pilot action occurred.

## Final review and reproducible proof

All eight review findings were fixed; none deferred. The executable Bash runbook now
creates a unique private proof directory, checks each destination's absence, stops on
any failed lock/install/test and includes both independent installs explicitly. The
manifest is restricted to exactly CPython3.15.0; selected uv regenerated the lock without
changing package pins. A lock check refused the changed manifest before regeneration.

Final tests also construct the actual SQLAlchemy Psycopg adapter while blocking its
connection function, compile an Alembic table operation offline, and check canonical
finite floats/negative zero, UTF-16 key ordering and integer limits. The JSON cases
follow [RFC8785](https://www.rfc-editor.org/info/rfc8785/); they do not implement an owner
WRITE contract. No database connection or schema execution occurred.

The exact Bash block in qualification/python/README.md was extracted unchanged to
`/tmp/env-python-final-proof.sh`, syntax checked with `bash -n`, then executed with
isolated loopback/network permission. Its final proof directory is ignored
`platform/deployment/.local/python-baseline-qualification/proof-BoPIBbCl/`.

- Source/lock check:33 records,0.99ms; lock remained unchanged.
- First absent environment:32 wheels installed269ms; all7 tests passed1.98s.
- Second absent environment:32 packages installed offline366ms; all7 tests passed2.06s.
- Final test source SHA256: `e3d91b5e2c0fcfb43142aa95778999c79b7d3aa67bb8bde24a760c62e9712b2f`.
- Copied runbook negative cases (stale FastAPI requirement, existing destination,
  dangling-symlink destination): all exit nonzero before any installation; lock or
  marker/link state stays unchanged. These fixture-local copies never alter owner files.
- `uv pip check` on the installed graph:32 packages compatible. Native wheel tags
  observed cp315/cp315 manylinux2.17 x86_64 for Pydantic core/Psycopg binary;
  host glibc2.39, Py_GIL_DISABLED=0, binary libpq version180006. That is client-library
  evidence, not a change to or qualification of the selected PostgreSQL server major.
- Final pyproject/lock hashes above were rechecked after both installs. Scoped whitespace
  and relative documentation links pass. No test was skipped in the acceptance runs.
- Structural lock check: all32 registry package records use PyPI; all75 recorded wheel/
  source artifacts have HTTPS publisher URLs and SHA256 hashes. Installs selected wheels
  only; this does not claim execution of every artifact recorded for alternative tags.

Preparation/toolchain/runtime source and owner/root locks were not edited, so prior
source-bound tool receipts remain current. The affected fixture suite is the verification
command for this increment; earlier deployment regression results are not relabeled as
new package-integration proof. No deployment-ready or full ENV acceptance is claimed.
