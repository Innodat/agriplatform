# ENV PostgreSQL create-request construction evidence

2026-10-16. Bounded existing ENV owner increment selected through bmad-help and
bmad-build with ATDD/focused TDD. [Build record](../../_bmad-output/implementation-artifacts/spec-env-postgres-create-request.md)
and [runbook](DEVELOPMENT.md) retain scope. ENV runtime readiness remains false.

## Scope and authority

Construct one closed in-memory API1.48 PostgreSQL create request after original CLI
profile validation and qualified immutable child selection. The existing refused-create
boundary validates the returned request and caller-input custody before retaining a
safe boolean construction fact. Request body, environment and bootstrap content are
never saved, hashed or emitted as observed runtime evidence. No dispatch is enabled.

The constrained ENV profile deliberately selects Linux/amd64 and explicit127.0.0.1
publishing. It does not claim byte-identical Docker CLI serialization. Primary field
mapping authority is [Docker CLI28 opts.go](https://raw.githubusercontent.com/docker/cli/v28.0.0/cli/command/container/opts.go),
[Moby28 container_create.go](https://raw.githubusercontent.com/moby/moby/v28.0.0/client/container_create.go)
and [API1.48](https://raw.githubusercontent.com/moby/moby/v28.0.0/docs/api/v1.48.yaml).
The existing pinned Supabase profile remains the argv/bootstrap authority.

Bootstrap semantic/secret safety and volume freshness/reuse remain open. In particular,
[pinned start-database.ts](https://raw.githubusercontent.com/supabase/cli/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/start-database.ts)
checks volume existence before fresh setup: a pre-acquired volume takes its existing
volume path and skips runFreshDbSetup. Request construction does not solve that
remaining integration boundary. KDG fingerprint keys are a separate consuming input;
no secret provisioner or inferred bootstrap policy is introduced here.

## ATDD RED

Before production edits, root ran:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_create_profile.py' -k test_refused_create_proves_closed_execution_request
```

One test failed, exit1 in0.004s, `KeyError: create_request_proven` at line36. The
implementer waited for this observed acceptance failure before production changes.

## Required impact decisions

- Scaffold: extend the existing fixed PG profile and refused-create scaffold; no generic
  parser/client/service/generator and no expansion of real Docker request admission.
- Shared UI: no UI surface or reusable UI change is involved.
- Agent context: existing owner, ATDD, sensitive-log and release rules suffice; no root
  or generated instruction changes. Generated command evidence remains a future consumer.
- Documentation: profile mapping, runbook, this evidence, Build record and KDG handoff/
  memlog record construction scope, verification and remaining gates.
- ADR: existing ownership, isolation, operational-log and release decisions apply;
  no accepted ADR edit or new architectural decision is required.

## Focused verification and matrix audit

Root ran these suites serially outside the restricted socket sandbox:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_create_profile.py'
python3 -m unittest discover -s platform/deployment/tests -p 'test_startup_adapter.py'
python3 -m unittest discover -s platform/deployment/tests -p 'test_startup_lifecycle.py'
```

Profile17 tests in14.111s, startup38 in13.046s and lifecycle13 in36.222s passed, exit0.
The implementer's earlier lifecycle run had a sandbox socketpair PermissionError;
the external rerun passed without changing that expectation.

| Requirement | Executed test evidence |
| --- | --- |
| Complete fixed request, no shared mutable result | Independent full oracle and detachment test |
| Only selected pinned PostgreSQL child | Direct tag/foreign/malformed/unselected image rejection |
| Original profile and owned network/volume | Existing every-operand/env guards; coherent network mutation and startup volume descriptor tests |
| Exact nested keys/values/types | Every-node missing/extra/value/primitive substitution matrix; boolean/integer custody regression |
| Ambient exclusion and safe proof only | Ambient canary test, real wrapper safe output and exact safe fact-key test |
| Input custody at constructor boundary | Argument/environment/fixture and caller-side mutation cases; no positive events |
| No transport activation | Constructed request rejected by existing Docker transport before socket access |
| Existing lifecycle retained | Full lifecycle suite; existing refused create/transfer/refused first-start sequence |

## Independent review and additional RED

Three review lenses filed seven finding instances. Port typing was reported twice;
other findings covered negative-control baseline distinction, shallow environment
custody, premature helper attestation, possible future mapping drift and missing final
evidence. Each received its own verdict before grouping in the Build record. The
mapping-drift claim was disproved for this change: current fixed mappings agree and
independent complete oracles plus pinned CLI proof protect them; no present mismap was
identified. Remaining findings use small local patches/tests/documentation, with no
new public execution surface.

Before review fixes, root ran:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_create_profile.py' -k review_
```

Four tests failed in0.031s, exit1, with12 failures: eight invalid port representations,
unchanged-baseline failure mistaken for intended corruption, mutable nested environment
custody and unconstructed facts claiming request proof. The nested test also caught a
positive event after the undetected mutation. Production fixes followed observed RED.

Final review-fix suites passed serially outside sandbox: profile21 tests in18.898s,
startup38 in7.052s and lifecycle13 in31.503s, exit0. The new four review regressions
execute both nested-custody seams, constructor/validator baseline failures, strict port
representations and unconstructed helper facts. Deep environment snapshots preserve
caller comparisons; actual attestation is set only after validation. Six retained review
finding instances are fixed, one disproved, none deferred.

## Frozen-source public qualification

Fresh run `43033cc0-d1af-4231-94db-25bd4b35e09c` passed preparation, all six pinned tools
(including TypeScript7.0.2) and primary-registry image-manifest qualification with the
final source bindings. Exact entry commands:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 43033cc0-d1af-4231-94db-25bd4b35e09c
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 43033cc0-d1af-4231-94db-25bd4b35e09c
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 43033cc0-d1af-4231-94db-25bd4b35e09c
python3 /tmp/env-pg-request-public-proof.py 43033cc0-d1af-4231-94db-25bd4b35e09c
```

The temporary harness invokes the existing `tests/qualify_startup.py --target <same>
--run-id <same> --control <control>` entry point. It checks exact exit/result pairs,
positive fact/event counts, unchanged custody, safe output and no observed request
content. This orchestration is not a new delivery entry point or generator.

| Control | Exit | Code |
| --- | --- | --- |
| positive | 0 | synthetic_boundary_proven |
| invalid-create-script | 2 | expected_create_profile_rejected |
| invalid-create-environment | 2 | expected_create_profile_rejected |
| invalid-create-routing | 2 | expected_create_profile_rejected |
| invalid-create-request | 2 | expected_create_profile_rejected |
| lifecycle-positive | 0 | synthetic_boundary_proven |

All **six public checks passed**. Both positives recorded create_request_proven=true,
nine/eleven events respectively and container_executed=false; lifecycle retains
validated transfer/refused start. Every result kept runtime_ready=false. No stderr,
checked canary, environment name, request-body structure or bootstrap content appeared.
All thirteen retained evidence files preserved hashes, inodes, modes and mtimes;
preparation/startup source snapshots also remained identical.

Protected result record:
`.local/pg-create-request-qualification/43033cc0-d1af-4231-94db-25bd4b35e09c.json`
SHA-256 `612519a4feb7ec41c8198a6bc2105e2f2110d45ed12584e883ea07f473f86de8`.

## Final regression and closure

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **397 tests in182.029s**, exit0. Output retained at
`/tmp/env-pg-request-regression.log`. All matrix rows and review regressions ran.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 43033cc0-d1af-4231-94db-25bd4b35e09c` exited2 with `docker_28_required`,
`runtime_ready=false`. No host upgrade, real container, SQL, image layers, owner
migrations, accounts, access or infrastructure changed. Supported Docker would still
refuse the unqualified runtime adapter.

Affected Python syntax, scoped whitespace and local Markdown links passed. Six review
finding instances fixed, one disproved, none deferred. Requirement/test and all five
impact decisions are recorded above. Current concurrent epics.md and Leave features/
implementation-plan/planning-handoff edits remain outside the scoped commit.

Remaining ENV gates include bootstrap semantics and secret lifecycle, fresh/initialized
volume reuse and skipped-setup integration, execution-time enforcement, real health/
stop/reset/recovery and target PostgreSQL compatibility. P1/SERVICE and owner/provider/
device qualification remain open before dependent Identity/Access/WRITE/KDG consumers.
