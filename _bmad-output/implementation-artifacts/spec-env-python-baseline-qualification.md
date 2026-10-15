---
title: 'ENV: qualify the approved Python dependency graph'
type: feature
created: '2026-10-15'
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: cc6f6c037bf5fab407273f5b67b26be2ef71b4fa
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
---

<frozen-after-approval reason="Approved bounded ENV implementation and isolated synthetic verification">

## Intent

ENV has executed its selected Python/uv tools, but the approved Python package graph
has not been resolved, installed or executed. Add an isolated qualification fixture
under `platform/deployment/qualification/python/`, with a thin exact-pinned pyproject,
publisher-generated uv.lock including transitive hashes, and synthetic acceptance tests.
Use already qualified ordinary CPython3.15.0/uv0.13.1, Linux x86_64 GNU. Select the
approved FastAPI0.143.0, Uvicorn0.54.0, Pydantic2.14.1, settings2.15.0, SQLAlchemy2.1.4,
Psycopg3.3.6 with its supported binary extra, Alembic1.20.0, HTTPX0.28.1, RFC8785
0.1.4, PyJWT2.15.1 and pytest9.1.1 as test-only. Require wheels; no implicit source
build, alternate Python, global installation or version downgrade. TypeScript7.0.2
and all other approved pins remain unchanged.

Observe missing-baseline acceptance failure before dependency implementation. Generate
the lock using actual selected uv against PyPI, then clean frozen/locked installs in
ignored isolated environments, with explicit interpreter and cache/config isolation.
Run real native Pydantic/Psycopg/libpq calls, synthetic API validation over actual
Uvicorn+HTTPX loopback HTTP, settings validation, JWT rejection/verification, canonical
JSON safety and PostgreSQL SQL/Alembic offline compilation. No database connection,
schema execution or real user content. Record exact target/tool/lock evidence, test
commands/results and scaffold/UI/context/documentation/ADR impacts.

This fixture proves ENV dependency compatibility, not a shared server implementation
or application/service dependency authority. Independent owners retain their own
pyproject/uv.lock and subset choices; no fixture import becomes a runtime dependency.
No root/owner locks, accepted ADRs, generator or generic offline service are changed.
No Docker upgrade/startup, migration/account/access change, infrastructure, deployment,
Leave/KDG domain/editor implementation or real-data pilot. Runtime readiness remains
false; Docker>=28, images/deployed DB, owner locks and guarded runtime/adoption/provider/
device proof remain open. Preserve concurrent Leave/PtS planning work.

</frozen-after-approval>

## Implementation Notes

bmad-help selects this independent existing ENV qualification obligation before
P1/SERVICE/Identity/Access/WRITE. No intent gap or irreversible action; footprint is a
small dependency fixture/lock/tests and owner evidence/runbook/KDG handoff. Source
runtime preparation/toolchain code stays unchanged, so existing prepared tool receipts
remain source-current. Actual tools are the verified run0cc4bc48-505e-41c1-8876-25b2d49b5694
payloads. This uses Build's small-change route and its required independent review.

## Implementation results

Observed acceptance red on the selected pristine Python: pytest absent, exit1. Added
exact package fixture and generated uv lock with selected0.13.1. Sandbox PyPI DNS failed;
approved retry resolved33 records. Wheel-only first install installed32 packages; the
initial sandbox API test denied socket creation (six passed, one failed). Authorized
loopback rerun passed all7; second fresh offline environment also passed all7. No skip,
mock HTTP replacement, source build or downgrade dismissed those execution constraints.

## Review Triage Log

| Finding | Verdict and resolution |
| --- | --- |
| Documented first destination already exists | medium; unique private mktemp proof root and independent executable existence/symlink checks now precede each sync. Negative preexisting/dangling destination cases refuse without change. |
| Lock check failure does not stop copied recipe | medium; fail-fast subshell wraps the complete sequence. Copied stale-manifest case exits before install and preserves lock. |
| Manifest permits unqualified Python patches | medium; tightened to==3.15.0 and regenerated lock via selected uv, preserving direct package pins. |
| Generic dialect misses SQLAlchemy/Psycopg integration | medium verification gap; construct actual postgresql+psycopg adapter with connect forbidden and compile literal/bound SQL. |
| Alembic only emits supplied text | medium verification gap; compile synthetic create_table/identity/primary-key SQL offline within transaction. |
| JCS misses runtime-sensitive boundaries | medium verification gap; fixed finite float/negative-zero/UTF-16 ordering/safe-integer vectors and rejection cases added. |
| Evidence still incomplete at review | low finalization task; record exact final two-env outcomes, hashes, commands and all findings here and in owner evidence. |
| Offline second recipe requires manual edits | medium; complete second absent-env offline sync and explicit interpreter test commands are now in the same runnable block. |

All eight accepted findings resolved; none deferred. Final exact runbook block extracted
to/tmp/env-python-final-proof.sh passes bash syntax and real execution. Ignored proof
root platform/deployment/.local/python-baseline-qualification/proof-BoPIBbCl: first32
packages269ms/all7 tests1.98s, second32 packages offline366ms/all7 tests2.06s. Negative
stale/existing/symlink cases exit before install and preserve lock/marker/link bytes.
uv pip check reports all32 installed packages compatible. Native GNU/GIL and libpq
checks executed; no actual database/schema operation. Runtime readiness remains false.

## Verification

Exact environment/tool/command sequence and requirement-to-test mapping:
platform/deployment/qualification/python/README.md and ENV_PYTHON_BASELINE_EVIDENCE.md.
Final hashes: pyproject18b784117c7cecea314424561d109f4762defdf8225307af7fccacf59504bcfc;
uv.lock2863e2fe9a3c680444445196510be2f2f94579f9abc5bebdf29bfe71b70ae809;
tests e3d91b5e2c0fcfb43142aa95778999c79b7d3aa67bb8bde24a760c62e9712b2f.
Source/lock33 records pass; final scoped whitespace/local documentation links pass.
Five impacts recorded, KDG handoff/testing/memlog updated, concurrent Leave/PtS excluded.
