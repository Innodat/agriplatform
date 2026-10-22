---
title: 'Supervised Scribeswell corpus invocation'
type: 'feature'
created: '2026-10-22'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '65eaff51e57df6f993608649d758ef8fdbb5f44c'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-scribeswell-studies/corpus-publication.md'
  - '{project-root}/apps/scribeswell/docs/CORPUS_CONTROLLER.md'
---

<frozen-after-approval reason="continued bounded implementation authorized by the user's next instruction">

## Intent

**Problem:** SQL timeouts do not bound operator connection, transport or COMMIT waits. The dormant controller needs supervised invocation and truthful reconciliation before activation can be considered.

**Approach:** Add an app-local Python supervisor for original execute/outcome inputs, explicit target binding and isolated credential transport. Qualify uncertain outcomes using disposable PostgreSQL; retain production preparation gates.

## Boundaries & Constraints

**Always:** Consume existing parser, source qualifier and transactional adapter. Target is a frozen repr-suppressed value with explicit kind, database URL and binding: Supabase HTTPS project URL or declared local_disposable exact database name. Supabase uses platform/deployment/target_contract.py; local uses literal127.0.0.1/::1, exact operator username, explicit database name and bounded connect timeout through existing URL validation. Reject unknown kinds, options, identity mismatches and malformed targets before spawning; independently recheck in child. Local declaration is not proof of disposable custody. No credential discovery. Use an isolated Python child, credential stdin, scrub PG/Python/Scribeswell credential environment, suppress stderr and bound output. Fixed60-second operation budget includes2-second kill/reap reserve; no public timeout override. Full source qualification must precede connection; worker can requalify through existing adapter. Return existing frozen CommandReceipt only after successful worker commit and parent validation against original command. Lookup returns receipt or None, with None explicitly unresolved. Failures expose stable safe identifiers without driver/payload/secret context. On uncertain execution, keep original input/operation for explicit lookup; never auto retry.

**Never:** Provision caller/actor/grants, verify Identity through local UUIDs, change migration profiles/DDL/references, enable live enforcement, mutate importer, add CLI/HTTP/runtime wiring, use another owner's implementation, change Access/Leave/factory/UX/standalone signup, or claim live readiness. Do not inspect workstation secrets. Preserve all unrelated changes. Only disposable fixture operations are authorized here.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected | Failure |
|---|---|---|---|
| Execute | valid command/source and prepared operator target | committed typed receipt | safe existing denial/conflict |
| Outcome | original command/current authority | original receipt or unresolved None | no source required |
| Invalid input/target | malformed command, source or binding | no database call | safe fixed identifier |
| Child stalls or response lost | connect/query/COMMIT blocked, or committed response absent | bounded termination; uncertain result | unknown_outcome; no new operation |
| Bad IPC | nonzero/oversized/malformed/forged receipt | never return success | unknown_outcome |
| Ambient settings | PG/Python/credential environment injection | selected explicit target only; no argv/output secrets | safe failure |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/backend/corpus_publication.py`: execute_command, lookup_outcome, PublicationError and _receipt; reuse transaction/receipt rules.
- `backend/corpus_publication_input.py`, `corpus_evidence.py`: bounded strict bytes, prepare_command, MAX_SOURCE_BYTES; source must qualify before connect.
- `backend/corpus_database_audit.py`: credential-stdin and sanitized subprocess patterns only; avoid unbounded final communicate and post-buffer size checking.
- `platform/deployment/target_contract.py`: approved pure project/role binding; no service-owner imports.
- `tests/test_corpus_publication.py`: controller_database/enabled/body fixtures, role_url and synthetic actor only; reuse without weakening guards.
- `docs/CORPUS_CONTROLLER.md`: dormant readiness gates remain authoritative.

## Tasks & Acceptance

**Execution:**
- [x] `apps/scribeswell/tests/test_corpus_operator.py` — observe relevant acceptance failure first, then transport/target/TDD negatives and real PostgreSQL qualification.
- [x] `apps/scribeswell/backend/corpus_operator.py` — implement explicit frozen target and execute/outcome supervisor, private bounded worker protocol, safe parent validation and kill/reap.
- [x] `apps/scribeswell/docs/CORPUS_OPERATOR.md`, `docs/CORPUS_CONTROLLER.md` — document API, custody, uncertainty, budgets, actual evidence and open gates.

**Acceptance Criteria:**
- Given an enabled disposable fixture and actual restricted operator credentials, when supervised begin/recover/seal and original-input lookup run, then receipts/history agree with the existing controller and source bytes remain unchanged.
- Given a transaction that committed but its child response was deliberately lost, when explicit same-operation lookup runs, then it recovers the original durable receipt without a repeated transition.
- Given revoked authority, malformed source/target, hostile ambient settings or blocked/malformed child responses, when invoked, then safety, bounded teardown and uncertainty rules hold with no leaked credentials or raw errors.

## Implementation Notes

Root owns canonical and delivery records; implementation agent owns only listed app files. No duplicate BMAD workflow, commit or deployment. Record exact red/green commands. Use `/tmp/scribeswell-studies-tests-py312/bin/python`; actual DB tests need an explicitly owned disposable PostgreSQL17 fixture. No skipped acceptance counts as proof. Fixtures must run sequentially on a cluster; stop the exact owned container afterward. Impact decisions: scaffold/shared UI/agent-context/ADR unchanged; app docs and canonical handoff updated. API remains app-local pending proven reuse.

## Spec Change Log

## Review Triage Log


| Finding | Verdict | Evidence and route |
|---|---|---|
| Root R1: parent source qualification | medium | Full qualification originally preceded the child, so expensive work could not be interrupted. Fixed before review by moving full qualification before connect inside the child; its timeout regression passed. |
| Root R2: pooler multiple hosts | high | Local reproduction accepted comma-separated libpq hosts; seven failing cases reproduced the gap. Single DNS-host validation fixed all seven without changing platform owner code. |
| Blind B1: uppercase schemes | medium | urlsplit accepts uppercase schemes but returned original text reaches libpq, which rejects it. Patch normalization with connection-string parsing regression; no public surface change. |
| Blind B2: implicit workstation credentials | high | Environment scrubbing leaves libpq defaults for client certificates and GSS. Official PostgreSQL connection documentation confirms these defaults. Patch explicit password-auth/certificate/GSS/passfile settings; verify actual kwargs and existing SCRAM fixture path. |
| Blind B3: unverified reap | medium | Existing TimeoutExpired handler discards failed reaping evidence. Patch a fixed structured warning and test it; public result stays unknown_outcome. |
| Blind B4: descendants | low | Trusted worker launches no descendants; immediate-child cleanup cannot support the document's absolute no-detached-work assertion. Patch that wording to the actual worker/direct-child boundary; do not introduce a generic process-tree launcher. |
| Blind B5: total deadline wording | low | Synchronous bounded admission/encoding and Popen are charged to the monotonic budget but cannot be interrupted by the later event loop. Patch documentation to distinguish charged elapsed time from supervised blocking waits; test exhausted admission prevents spawning. |
| Blind B6: actual connect/COMMIT waits | medium | Generic child/source stalls and completed lost COMMIT do not specifically execute blocked connection/COMMIT paths. Patch focused fault-injection acceptance for those call sites, retaining actual response-loss proof. |
| Blind B7: private worker protocol | medium | Child-side tests omit request size, duplicates, exact types, base64 and source-on-lookup negatives. Patch parameterized pre-connect rejection tests; no new protocol fields. |
| Verification V1: conflict/unavailable | medium | Direct adapter tests bypass both new IPC boundaries; removing either allowlisted code would escape current supervisor tests. Patch real competing-begin and disabled-fence failures, exact codes and unchanged protected state. |

All eight independent findings were classified separately before grouping. Each routes
to a small correction/test/documentation patch; no intent or public state changes,
no deferred findings. Edge-case lens returned no findings. Reviewers ran concurrently
with fresh context. Official libpq reference consulted for B2:
https://www.postgresql.org/docs/17/libpq-connect.html (require_auth, sslcertmode,
gssencmode and passfile); no workstation credential files were inspected.

## Verification

Run focused operator tests first, affected controller/input tests next, then app regression. Root independently runs affected acceptance, relevant platform target contract checks and composition check-only. Record commands/results, review findings and remaining activation gates. Baseline revision above is canonical; exclude unrelated work and canonical untracked tree from scoped local commit.

Root pre-implementation evidence: platform target checks passed with
`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_target_contract.py -q`
(2 tests,10 subtests). `python3 tools/py/run_compose_supabase.py --check-only`
passed with no changes. Exact disposable PostgreSQL17 fixture:
`scribeswell-supervisor-20261022`, container
`48a2c59d7ce7bf6c233f7da33b32b4b8cb484ac82832f4a75a5849a076d8a04c`,
image `sha256:212aeeeb8faaef6c46498d86cbec6b9344d8d9492996b174664ff82c562ab685`,
loopback port32773; root owns teardown. All database checks are qualification only.


Implementation evidence (before independent review): acceptance red was
`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_operator.py -q`
with missing corpus_operator module; first actual PostgreSQL acceptance green1 test2.09s.
Commands below use the same interpreter with explicit disposable URL on port32773:
focused operator47 passed4.95s; controller+input287 passed11.04s; full app665
passed144.06s with no skips (one existing Starlette/httpx warning). Root reproduced
multi-host pooler acceptance without connecting;7 new binding negatives failed before
single DNS-host correction, then7 passed0.76s. Final operator54 passed5.59s.
The665 full run predates that correction; root final regression remains required.

Matrix audit: Execute/Outcome are covered by supervised_transitions_and_original_lookup;
invalid target/source by invalid_target_never_spawns, invalid_pooler_single_host_binding_never_spawns,
source_failure_is_safe_and_target_never_connected and child_revalidates_target_and_source_before_connect;
stall/lost response by stalled_child_bounded_killed_and_reaped,
full_source_qualification_is_inside_deadline and committed_response_lost_then_explicit_reconciliation;
bad IPC by bad_child_response_never_success and forged_receipt_validated_against_original;
ambient settings by ambient_credentials_scrubbed_and_stdin_only. All54 current operator
cases actually ran and passed. AC1–AC3 have actual PostgreSQL evidence, not skipped tests.
Root read the full scoped source/test/document diff before review; unrelated dirty
files and canonical/delivery claims are excluded from reviewer content.


Post-review implementation retained all54 original tests and added26 focused cases;
operator80 passed10.42s. Root independently reran the affected acceptance:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32773/postgres timeout 120 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests/test_corpus_operator.py apps/scribeswell/tests/test_corpus_publication.py apps/scribeswell/tests/test_corpus_publication_input.py -q`
passed367/no skips in23.58s. Root read all patched source/test/document content;
B1–B7 and V1 are resolved. B6 uses reached-site fault injection inside the actual
worker at connect and the real transaction's commit-entry generator, not a claim
of a blocked server COMMIT response. Actual successful-COMMIT response loss remains
separately proven. B3's fixed warnings preserve confirmed forced reap vs unverified
termination. B4/B5 documentation now states direct-child and synchronous-work limits.

Root platform verification after review passed25 tests/42 subtests in4.35s:
`/tmp/scribeswell-studies-tests-py312/bin/python -m pytest platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_migrate_adapter.py platform/deployment/tests/test_target_contract.py -q`.
Root link/whitespace checks pass; canonical19 companions resolve and11 capability IDs
remain stable. All8 protected existing corpus/importer/migration/profile files match
their pre-task SHA-256 values. Pre-existing AGENTS.md and Scribeswell README changes
are byte-preserved. A blanket dirty-tree hash assertion detected concurrent owner
activity in epics, KDG next-session and Leave implementation-plan/handoff; inspection
showed concurrent KDG commit `fadbbcac915a161a67b5f9480f03d39db91bedf4`.
Those files were not edited, restored or staged by this delivery. The recorded
baseline remains65eaff51e57df6f993608649d758ef8fdbb5f44c; scoped commit will preserve
the current owner history. No browser/build/image/live-provider/production test was
run or is implied. No generic repository-wide check exists.


Final root full regression:
`SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:32773/postgres timeout 300 /tmp/scribeswell-studies-tests-py312/bin/python -m pytest apps/scribeswell/tests -q`
passed698 tests/no skips in178.52s, with one existing Starlette/httpx deprecation.
All80 current operator cases passed within this full run as well as the independent
367-case affected suite. No code changed after these checks. Exact owned container
`48a2c59d7ce7bf6c233f7da33b32b4b8cb484ac82832f4a75a5849a076d8a04c`
was stopped successfully after verification. All eight independent findings are
resolved, none deferred; no review loopback or public contract expansion occurred.
Canonical corpus/brownfield/acceptance handoff is derived via bmad-spec and remains
outside the scoped commit, as does every pre-existing/concurrent owner change.

Next bounded readiness work: externally verified service-actor/caller preparation
and an exact least-privilege active-state release profile; then coordinated importer
transition and sealed audit/publication/reader proof. Shipped enforcement stays false,
no live actor/caller/authority/attempt exists from this delivery, and standalone
signup/Access/Identity/Leave/factory boundaries remain unchanged. No push or deployment.
