---
title: 'ENV: prepare protected run-local Supabase configuration'
type: feature
created: '2026-10-14'
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: 9db5bacf7a135f7283a54b83d568092165763446
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Approved bounded ENV implementation and synthetic local verification">

## Intent

ENV preparation currently reserves identities but produces no run-local configuration.
Extend existing `platform/deployment/dev.py prepare` to install deterministic protected
`supabase/config.toml` beside its inventory under the ignored run UUID. Bind exact config
bytes in inventory and verify them on prepare repeat and read-only startup preflight.
Use the selected CLI2.120.0's proven configuration keys: run-derived project ID, approved
API/database/shadow/Studio/mail ports, publisher default PostgreSQL17, desktop localhost
site/app-return URLs, Auth enabled with public/anonymous signup and manual linking off,
no exposed business schemas or automatic table exposure. Disable unused pooler,
realtime, Studio, local SMTP, Storage/S3/vector/analytics, edge runtime and diagnostics
analytics. Explicitly disable CLI repository migrations/seeds with empty path lists.
Do not materialize SQL, roles, secrets, credentials, provider bindings or device TLS.

Require exact run/supabase contents, private ownership/modes and no links; reject
changed/missing/unexpected files without overwriting or repair. Publish the inventory
only after config is fsynced; interrupted/incomplete runs remain refused evidence.
Keep existing target/source/port/UUID/confirmation safeguards and Docker>=28 gate.
Old source-bound runs/receipts are not migrated. Existing tool pins, including TS7.0.2,
stay unchanged. Runtime readiness is always false; no container/image/network/volume
operation, migration/account/access change, daemon upgrade, infrastructure, deployment,
Leave or KDG domain implementation. No new generator, generic service or delivery flow.

Prove preparation behavior with public acceptance red first and focused TDD. Check
the final config with the actual pinned CLI against a synthetic local Docker API,
including an invalid-config control; never count services exit0 alone as parse proof
because this version reports invalid TOML on stderr yet still exits0. This is parser
and configuration evidence only: image digests, deployed PostgreSQL compatibility,
actual SQL/role/fixture behavior, live network binding, Auth/provider and devices remain
runtime obligations. Future startup must select explicit workdir/private state and
verified run-owned network, not root project discovery or defaults.

</frozen-after-approval>

## Implementation Notes

bmad-help selects existing ENV before P1/SERVICE/Identity/Access/WRITE. This small
single-goal change has no human intent gap or irreversible action. Files: dev.py,
new focused config tests, narrow existing inventory-content assertions, owner evidence/
runbook and KDG navigation/memlog. The CLI init output and services probes in isolated
/tmp established current config keys and PostgreSQL17 default without starting a stack.
Keep existing16 preparation/15 daemon/23 toolchain tests as affected characterization.
Record exact requirement-to-test evidence and scaffold/UI/context/docs/ADR impacts.

Public acceptance red preceded implementation: four config tests had two failures/nine
subcase errors because no config existed. Existing16 preparation tests passed2.546s.
The first config implementation passed four tests0.986s and owner177 tests18.073s.
Actual pinned CLI probes showed services exits0 even on invalid TOML, ping negotiation,
and40-character project truncation. Hex UUID output still exceeded the cap; a targeted
identity regression failed before reversible22-character URL-safe UUID encoding with
the existing17-character prefix. Actual CLI preserved the final39-character name.
Only intended inventory-content/name assertions changed in existing tests. Pinned tools
and baseline versions remain unchanged. Canonical UUID command arguments/paths remain.

## Review Triage Log

| Finding | Verdict and resolution |
| --- | --- |
| Fresh installed config not checked before inventory | medium; reproduced prepare exit0 after install mutation. Validate actual bytes/protection/contents immediately and again before inventory publication; recheck source/target. |
| Directory/file pathname replacement during config read | medium; reproduced detached directory accepted before daemon call. Compare current directory/file identities and metadata across read, including modes/timestamps, then exact directory contents. |
| Tool qualification omits new config observations | medium; reproduced receipt success after execute changed config. inputs_current now calls read-only validate_prepared at every existing check; regression preserves old receipt on refusal. |
| Actual CLI fixture omits UUID punctuation | medium verification gap; add retained valid-punctuation fixture with mixed case, underscore/hyphen and exact expected lookup. |
| Required settings lack focused assertions | medium verification gap; assert API/TLS/Auth/rotation and email/SMS signup settings explicitly. |
| Only inventory-link interruption tested | medium verification gap; add config write/flush/file-fsync/directory-fsync fault injection, no complete inventory and unchanged partial evidence after repeat/up refusal. |
| Rejected-tree non-repair not fully asserted | medium verification gap; snapshot modes/content/link targets before repeat/up and require exact preservation. |

All seven findings were accepted and fixed, none deferred. Review config regression
reproduced two failures; toolchain mutation regression reproduced one failure before
fixes. Final config eight tests pass1.659s and toolchain24 tests pass2.799s. Actual CLI
fixture passes both valid cases with two metadata reads each and invalid case with none.

## Final verification

Owner regression:182 tests pass19.901s. Focused config eight pass1.659s; toolchain24
pass2.799s. Retained actual CLI parser proof passes ordinary/punctuation UUID cases
(two expected metadata reads each) and invalid TOML (zero requests). Scoped whitespace
and documentation links pass. No findings deferred or tests skipped.

Fresh final-source run0cc4bc48-505e-41c1-8876-25b2d49b5694: actual prepare/repeat exit0;
config hash1fec9990e0d128043e0b543ebed17d2fe961ef01831fdd322fa43688af3cfa12 matches
inventory, directory0700/config0600/inventory0600. Actual up expected exit2 with
Docker28 requirement; actual six-tool qualification exit0 with runtime_ready=false.
Qualification receipt SHA2564efad618046ecda6459da9680b23e9cd47375181a059b33f6838ad8acde6ecc2.
See ENV_CONFIGURATION_EVIDENCE.md for exact commands, traceability and five impacts.
Concurrent Leave/PtS planning changes are preserved and excluded from this delivery.
