---
title: 'ENV: bind planned KDG base images to verified registry manifests'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 150774706869d6d584c600e96bcb63fca694fc51
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/deployment/DEVELOPMENT.md'
---

<frozen-after-approval reason="Standing approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** The pinned CLI/config/tools are prepared, but the planned minimum base
images have no verified manifest identities. Mutable tags and interchangeable mirrors
cannot serve as reproducible image evidence.

**Approach:** Existing ENV owns a guarded `images.py qualify --target <JSON> --run-id
<UUID>` command. For an unchanged prepared target and existing qualified tools, record
four publisher-selected base references, resolve primary ECR manifest metadata and bind
index/Linux-amd64 child digests plus retained bytes into immutable protected run evidence.
This qualifies planned base identities, not a runnable or complete startup image set.

## Boundaries & Constraints

**Always:** Preserve all tree/install/owner-lock changes. Use ATDD then focused TDD.
Use selected CLI2.120.0 and existing preparation/toolchain verification before execution;
missing tools/receipts refuse, never install/repair. Isolate CLI state/config/environment
and use explicit workdir/private nonexistent Docker socket. Cross-check its unlinked
services JSON for PostgreSQL/Auth/PostgREST pins; Kong is sourced from the pinned release.
Chosen evidence registry is only public.ecr.aws/supabase/<image basename>; no fallback
or mirror equivalence. Bound HTTPS requests/deadlines/body sizes, deny redirects and
foreign auth realms, validate exact raw SHA256 digests and media/schema/platform shapes.
Anonymous registry tokens remain memory-only and never enter logs/evidence. Keep target,
prepared/config/tool-receipt/selection/source hashes, raw manifests and explicit limits.
Repeat verifies retained bytes/source bindings without re-resolving tags. No silent repair.
Protect paths, links, modes, concurrent/partial publication and changed inputs; fail closed.
Record requirement-to-test evidence and scaffold/UI/context/docs/ADR impacts.

**Never:** Pull image layers/config blobs, call a real Docker daemon, start containers,
upgrade Docker, run migrations/SQL, change accounts/grants/provider/infra/deployment or
use real data. No generator, generic registry service, app domain or Leave implementation.
Do not alter dev.py/toolchain.py or their source-bound contracts merely to add this item.
Do not claim enabled/startup/helper completeness, container execution/libc, deployment
PostgreSQL compatibility, registry enforcement by the undelivered adapter or runtime readiness.

## I/O & Edge-Case Matrix

| Input/state | Required result |
| --- | --- |
| Prepared run, qualified payload, valid publisher metadata | Protected manifest evidence for all four exact pins, Linux/amd64 child bound to index; runtime_ready=false |
| Bad catalogue, tag, media/schema, digest, platform or registry response | Nonzero safe stage/code; no completed receipt, no fallback/pull/startup |
| Changed target/source/payload/evidence; symlink/mode/extra files | Refuse before registry use or completion; no adoption or repair |
| Existing valid evidence; mutable remote tags changed | Verify retained raw bytes/bindings without registry calls or replacing evidence |
| Concurrent/interrupted collection, timeout or oversized metadata | One writer, bounded failure; incomplete output remains unqualified |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py`: reuse decode/read/directory/read_at/validate_prepared,
  configuration/project identity and safe Refusal conventions. It and toolchain stay unchanged.
- `platform/deployment/toolchain.py`: existing repeat qualifier verifies complete payload,
  prepared/source bindings and immutable receipt. Require receipt/inventory first.
  Existing valid run:0cc4bc48-505e-41c1-8876-25b2d49b5694 under deployment/.local.
- `platform/deployment/qualification/web/prove.py`: existing bounded process-group execute
  helper may be reused as build tooling; never duplicate installed-tool fingerprints.
- New `images.py`, `image-pins.json`, `tests/test_images.py`: owner command, exact selection
  and acceptance/unit tests. Evidence lives only in ignored .local/kdg-base-images/<UUID>.
- Actual CLI `services --output json --agent no` returns name/local/remote; unlinked remote
  fields must be empty. It omits Kong and is not a startup inventory.
- Pinned upstream v2.120.0 commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4:
  apps/cli/src/shared/services/Dockerfile; commands/start/start.gates.ts;
  command-internal/docker-registry.ts (under apps/cli/src). Record URLs/source identity
  in selection/runbook. Planned base: supabase/postgres:17.11.0.004,
  library/kong:2.8.1, supabase/gotrue:v2.197.0, postgrest/postgrest:v16.4.
  Evidence policy: legacy backend, slim off, no dotenv/.temp overrides; this is not an
  implemented startup policy. Current protected config selects PG17, not live target proof.

## Tasks & Acceptance

- [x] `tests/test_images.py`: observe public command acceptance failure before code;
  focused synthetic HTTP/catalogue/persistence tests cover every matrix row.
- [x] `image-pins.json`, `images.py`: implement exact selection, existing owner validation,
  clean CLI capture, bounded metadata-only ECR collection and immutable protected repeat.
- [x] `tests/test_images.py`: prove invalid/auth/redirect/hash/platform/deadline/partial/
  tamper/concurrent cases, no daemon, no token persistence and no repeat registry fetch.
- [x] Actual pinned CLI plus public registry: execute first collection/repeat with existing
  prepared/tool run; retain commands/hashes and metadata evidence. Run affected owner suite.
- [x] Owner runbook/evidence: requirement traceability, five impacts and unresolved gates;
  independent review and local conventional commit, no push.

**Acceptance Criteria:**
- Given actual selected tools and unchanged preparation, when qualification succeeds,
  all four exact publisher references have verifiable retained manifests and platform
  digests; no layer bytes, real daemon or runtime mutation was used.
- Given existing valid evidence or changed/unsafe inputs, when qualification repeats,
  it verifies immutably or refuses; it never refreshes tags or repairs output implicitly.

## Implementation Notes

No intent gaps or irreversible action: public metadata reads and ignored local evidence
are authorized. Full route reflects registry/protected-output risk. Preserve concurrent
Leave documents. Implementation agent owns code/tests/selection/runbook and initial
focused proof; root owns final external verification, KDG navigation/evidence and review.
The deployed DB target and actual startup/helper set stay explicit later gates.

## Spec Change Log

## Review Triage Log

Every finding was classified before grouping; no finding is deferred. B=blind,
E=edge-case, V=verification-gap. All route to bounded patches with no public surface.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Reformatting inventory during collect reproduced successful qualification with an obsolete preparation byte hash; compare captured bytes. Patch, grouped with E1. |
| B2 | medium | A subprocess wrote10,000,000 temporary-file bytes against a1024-byte output limit before polling refused it. Replace disk buffering with bounded capture. Patch. |
| B3 | medium | Injecting a post-link retained-validation failure leaves receipt.json despite the command failing. Preserve an unqualified publication state on failure and test these boundaries. Patch, grouped with B7. |
| B4 | low | document accepts nonempty platform feature requirements while selection names only generic Linux/amd64. Direct correction rejects unsupported requirements; no runtime compatibility claim is introduced. Patch. |
| B5 | medium | Successful persistence fixtures mock existing_tools wholesale; owner response/argument/environment validation is unprotected. Patch, grouped with V2. |
| B6 | medium | The timeout test replaces the entire worker, so actual DNS/header/body phases lack regression coverage through that worker. Add controlled stalls at those stages. Patch. |
| B7 | medium | Artifact-write interruption is covered but pending/link/unlink/fsync boundaries are not; central fail-closed publication regressions could pass. Patch, grouped with B3. |
| B8 | low | Fixed UUID is looked up in real ignored state and can legitimately exist. Use an isolated target tree or fresh UUID; direct test correction. Patch. |
| B9 | medium | Existing hardlink test first trips the extra-filename gate; it does not prove the nlink guard. Add a link outside the evidence directory. Patch. |
| E1 | medium | Independently reproduced semantic-preserving inventory-byte mutation returning success. Patch, grouped with B1. |
| E2 | medium | Changing the evidence directory to0777 during collect reproduced successful publication. Recheck the held directory/ancestor protections before completion. Patch. |
| V1 | medium | Preverified mutation demonstration: all images can fetch PostgreSQL and exact-request/complete-repeat tests still pass. Distinct per-image metadata must bind exact paths/artifact/receipt identities. Patch. |
| V2 | medium | Preverified real owner path is never reached with an existing receipt in tests; removing owner-result refusal would pass. Add controlled failed/changed/successful owner-result cases. Patch, grouped with B5. |

## Verification

Run smallest acceptance red first, focused tests, then actual CLI/registry collection
and immutable repeat, affected deployment tests and scoped whitespace/link checks.
Record exact commands/results; no skipped or metadata-only check becomes runtime proof.

Acceptance red: preimplementation `python3 -m unittest discover -s
platform/deployment/tests -p test_images.py` failed1 because images.py was absent.
Actual CLI smoke exposed generated .temp/cli-latest; a new regression failed before
allowing only that bounded output. Final focused command with `-v`:25 tests pass1.700s.
Affected owner command `python3 -m unittest discover -s platform/deployment/tests
-p 'test_*.py'`:207 tests pass20.902s after permitting synthetic sockets.
Actual public `images.py qualify --target platform/deployment/environments/kdg-local.json
--run-id 0cc4bc48-505e-41c1-8876-25b2d49b5694` first/repeat pass; all10 evidence
files preserve bytes/inodes/mtime/modes. Exact identities, matrix-to-tests and five
impacts: [owner evidence](../../platform/deployment/ENV_BASE_IMAGE_EVIDENCE.md).
Every matrix row has executed passing coverage. Three independent review layers
produced13 finding instances, all fixed, none deferred; the triage log records each.
Final33 focused tests pass3.207s;215 affected deployment tests pass23.190s.
Final public collection/repeat use fresh prepared/tool-qualified run
b3b805d5-adc6-4168-a79c-5945547d3320 and preserve all10 files. Earlier0cc receipt
refuses evidence_binding_changed with unchanged files. Eighteen publication faultpoints,
actual worker-stage timeouts, exact per-image mappings and real owner boundaries pass.
Scoped whitespace and four-document local-link checks pass. Local conventional commit
follows this completed record; no push. Enclosing ENV runtime/bootstrap remains open.
