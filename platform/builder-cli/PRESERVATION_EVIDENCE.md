# Disposable scaffold preservation proof

Baseline:23f6e209c17df024a6b4aaf905829725c812d192. This increment implements internal
installation/reruns of existing candidate shell output. Public generation, extension
import and current Auth/Access remain separate; generation_ready stays false.

## Requirement-to-test evidence

| Requirement | Executed evidence |
| --- | --- |
| Initial installation preserves unrelated files and refuses planned collisions | scaffold-preservation.test.mjs initial/collision cases pass |
| Edited owner seeds/custom files survive rerun | scaffold-preservation.test.mjs rerun/update case; proof-874WQD preservation hashes |
| All generated files preflight before any writes | later generated conflict/missing-file case passes; earlier file remains unchanged |
| Unsafe paths/metadata/ownership are refused | unsafe map, metadata/ownership, leaf/output/ancestor symlink cases pass |
| Failed/interrupted writes restore prior complete generated set | write-failure rollback and real SIGKILL child/recovery cases pass; uncertain/malformed state refuses |
| Competing writer refused | live installer/recovery exclusion assertions pass inside held writer |
| Regenerated custom shell still types/builds/runs | proof-r5WUAZ type/build/API/desktop/mobile Chromium; preserved shell hashes |
| Unsupported recipes/extensions refuse | executed application/service renderer rejection tests |
| Build admission rejects drift | direct checkScaffold edited/missing generated and malformed manifest cases; edited seed accepted |
| Initialization/staging failure preserves reusable prior state | actual ENOSPC owner/journal failures, partial scratch recovery and whole-file snapshots |
| Ownership keys remain round-trippable | own __proto__ path install/check/rerun case |

## Verification

Acceptance RED: selected Node26.11.1 --test tests/scaffold-preservation.test.mjs
fails ERR_MODULE_NOT_FOUND for the absent installer; red.log retains it. Focused GREEN:
--test --test-isolation=none tests/scaffold-preservation.test.mjs passes10/10, retained
in green.log. The default full suite attempt in the restricted execution context was
stopped exit130 with no result; its empty builder-tests.log is retained, cause unproven.

Normal root verification uses the explicit pinned Node/npm, uv/Python and Chromium/cache
selection in README, with permission for synthetic local sockets/processes. Commands:

```bash
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
npm run test:generation --workspace platform/builder-cli
npm run test:generation:application --workspace platform/builder-cli
```

All exit0. Builder38/38 tests pass (13.004s command); type/schema checks pass. Service
proof-5XZDuI passes both independent installations/four runtime tests each (16.761s).
Pre-review application proof-874WQD passes all13 stages (20.707s), four generated API runtime
tests and desktop/mobile real Chromium checks after preserved owner customization.
The visible custom text appears in the retained mobile screenshot, manually inspected.
The pre-review commands/results and44 unchanged source bindings are retained under
scaffold-preservation/pre-review/. No dependency/browser download.

Review:12 individual findings triaged;11 addressed, one low cleanup-window finding
rejected with fail-closed limitation documented; nothing deferred. Patches claim exclusive
recovery ownership, preserve known pre-mutation state after I/O failure, accept partial
scratch without trusting it, and round-trip special ownership keys. Focused18/18 tests
pass in review-fixes.log; added cases cover all write positions, initial SIGKILL rollback
and reinstall, real competing child refusal, ENOSPC and direct build-admission denial.

Final reviewed-source verification:46/46 builder tests pass; type-check and schema:check
exit0. Fresh proof-r5WUAZ passes all13 stages, including four API runtime tests and actual
desktop/mobile Chromium after custom preservation. It binds35 sources and20 output/lock/
custom/ownership files. The source-identical service proof-5XZDuI remains current on13
bindings. Exact commands, results/timings, logs and44 unchanged verification source hashes
are in platform/deployment/.local/scaffold-preservation/root-final-verification.json.
Previous proof directories/logs remain intact. Preservation audit confirms2521 pre-existing
files outside five intended prior-file edits unchanged, including concurrent documents;
root package/lock, accepted ADRs and all historical resources/state are preserved.

## Impact decisions

Scaffold: add a small internal installer to the existing builder, consuming the existing
explicit ownership maps and proof harness. Shared UI: no component change/promotion;
synthetic owner edits exercise preservation. Agent context: no root instruction change;
existing generated owner guidance already explains create-once seeds and generated ownership;
no generated context change is needed.
Documentation: builder runbook, mutable scaffold contract and KDG handoff updated with
actual scope and remaining gates. ADR:0059 and existing ownership decisions apply; no
accepted ADR changed or new architecture decision required.

No production/account/provider changes, migrations, Docker resources, infrastructure,
deployment or real data. Source, historical proof/state/resources and concurrent work
remain protected. This local developer proof assumes stable builder source and exclusive
use of the disposable target; it is not a hostile-filesystem or power-loss guarantee.
