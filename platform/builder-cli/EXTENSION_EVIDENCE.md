# Explicit custom-module import evidence

Baseline:f85d8e510b3fc66827155403eae46d17ea26fcc9. Internal disposable import through
the existing builder; candidate readiness stays false. Implementation and review complete.

## Requirement-to-test evidence

| Requirement | Evidence |
| --- | --- |
| Initial safe exact import/custom provenance | explicit import/provenance exact-byte acceptance test |
| Rerun preserves owner edits/additions/deletions without original source | owner maintenance/no-source instrumentation tests; proof-GyYZQO preservation and absence assertions |
| Unsafe source/path/type/limits and overlapping destinations refuse | unsafe sources/declarations and destination collision matrix tests; source duplicate/nesting refusal |
| Existing output and manifest compatibility | legacy no-import rerun, adoption/ownership/version refusal tests; prior renderer characterization |
| Initial import rollback/interruption retains prior state | caught failure, real SIGKILL at imported/manifest writes, unknown-edit refusal and actual ENOSPC tests |
| Real typed imported behavior survives build and browser reload | proof-GyYZQO TS/build/API and expected imported text before/after reload in desktop/mobile Chromium |

## Verification

Initial acceptance RED used host Node24.11.1 by mistake: node --test failed without
child detail, direct execution failed ENOENT for the missing imported file. Original
acceptance-red.log and exact host-node24-attempt.txt remain. The untouched HEAD
installer was replayed under selected Node26.11.1 after initial edits and fails the
expected-import assertion (acceptance-red-qualified.log). This is a baseline replay,
not a claim of selected-tool RED preceding those edits. Focused selected-tool GREEN:
extension/preservation28/28; type-check passes.

Root commands use the explicit qualified Node/npm/uv/Python/Chromium/cache selection
from README:

```bash
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
npm run test:generation --workspace platform/builder-cli
npm run test:generation:application --workspace platform/builder-cli
```

Pre-review, all exit0:56/56 builder tests (10.182s), type/schema checks, service proof-ZxlpHi
(16.393s; two independent environments, four runtime tests each), and application
proof-UkL6wo (21.490s; all13 stages, four API runtime tests and actual desktop/mobile
Chromium). Imported owner text is asserted before/after reload; mobile screenshot
manually inspected. Original source location is absent and changed source is retained
separately.36 application source bindings and22 output/lock/custom/ownership hashes,
initial import provenance and owner edit/addition/deletion evidence are retained.

Negative browser run deliberately expects wrong synthetic text. It fails toBeVisible,
keeps status incomplete and confirms API/browser teardown; original passing output
hashes remain unchanged. Exact command/environment/result/log/cleanup are in
platform/deployment/.local/scaffold-extensions/browser-negative-proof-UkL6wo/.
Pre-review exact commands/logs and45 unchanged source bindings remain under
scaffold-extensions/pre-review/. The negative browser receipt remains valid for the
unchanged browser assertion template; review patches touch installer/tests/README.

Review:12 individual findings triaged; six patched, five low findings rejected with
controlled-source/text-file scope documented, one false for the qualified Linux
case-sensitive filesystem; nothing deferred. Patches compare declaration fields,
bound directory iteration, validate every import directory/child before restoring,
publish initial files exclusively and test multiple successful imports. Regression
RED/GREEN retained in revision-red.log/revision-green.log; focused32/32 pass.

Final reviewed-source verification:60/60 builder tests and type/schema checks pass;
fresh application proof-GyYZQO passes all13 stages, four API runtime tests and actual
desktop/mobile Chromium, including expected imported owner behavior before/after reload.
It binds36 sources and22 output/lock/custom/ownership hashes. Service proof-ZxlpHi
retains13 matching source bindings and needs no rerun. Exact argv/status/timings,
raw logs and45 unchanged verification hashes are in scaffold-extensions/
root-final-verification.json. All seven matrix rows map to executed cases/actual proof.
Preservation audit confirms2523 protected pre-existing files unchanged outside seven
intended prior-file edits, including concurrent work; root lock, accepted ADRs and
all previous receipts/state/resources remain intact.

## Impact decisions

Scaffold: bounded explicit import in existing installer/journal and application proof;
no alternate generator. Shared UI: no promotion; typed fixture remains disposable owner
code. Agent context: root rules unchanged; existing generated ownership guidance is
retained: it already directs owner seed/custom work and generated-template ownership;
no generated context change needed. Documentation: builder runbook, mutable
contract and KDG handoff record actual capability and limits. ADR:0059/ownership decisions
cover this build-time change; no accepted ADR edited or new architecture required.

No production/account/provider changes, migrations, Docker resources, provisioning,
deployment or real data. Later imports/upgrades, binary assets/dependency inference,
normal generation and current Auth/Access remain explicit consuming work.
