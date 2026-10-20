# App-owned OpenAPI client proof

Baseline:20620682f15afd004093b67c0a1433437d65b9dc. Delivered through the existing
build-tool and scaffold owners. Public generation remains generation_ready:false.

## Requirement-to-test evidence

| Requirement | Evidence |
| --- | --- |
| Owner OpenAPI produces app-owned contracts | Service runtime exporter test; actual application api-export/check and client-generate/check pass |
| App TS7 with isolated tool compiler | Fresh installation qualifies upstream0.99.0, tool6.0.3 and app7.0.2 payloads; ordinary app tsc passes |
| DTO drift requires regeneration | Optional proof_note owner DTO edit; api:check fails api_client_stale; TS7 fails naming proof_note; regeneration/check/strict TS7/build pass |
| Check/conflicts preserve target and custom code | Seven actual CLI tests; real tampered copy refuses scaffold_conflict unchanged; original owner/import hashes survive regeneration |
| Real browser own-API HTTP | Desktop/mobile Chromium before/after reload: four successful health responses, availability text and imported owner text; keyboard/responsive checks pass |
| Safe failure and teardown | Owner adapter test covers HTTP, malformed body and network errors without sensitive text; actual stopped API produces502 and API unavailable; no unexpected errors; ordinary TERM and all server/browser cleanup confirmed |
| Declared clean installation | Fresh copied workspace/root lock, offline selective npm ci, local executable/payload qualification and installation-manifest audit pass |

## Exact verification and retained receipts

All directories below are under platform/deployment/.local/. They contain exact argv,
selected explicit environments, exit codes and log/tool/source/output/lock hashes.
No production credentials, database/account/Docker changes or implicit downloads.

- `scaffold-api-client/tests-s5g27y7l/result.json`: selected Node26.11.1
  `--test platform/builder-cli/tests/*.test.mjs`:62/62 pass; health-client tests2/2, including concurrent real native header/body stalls and teardown.
  After the outage assertion correction, focused browser guard tests2/2 pass.
- `scaffold-api-client/focused-direct6-m4ns9ln5/result.json`: copied current tool
  sources and declared disposable installation: `node --test .../client.test.mjs`
  7/7; TS7 `tsc --project .../builder-cli/tsconfig.json` and
  `node .../src/export-schema.ts --check` pass. This focused run explicitly borrows
  both installed owner dependency directories, rather than claiming another clean install.
- `scaffold-application/proof-dI2Gy9/proof.json`: complete
  `node platform/builder-cli/scripts/test-generation-application.mjs` with the
  selected tools/caches documented in builder README. All25 stages pass, including
  three deliberately nonzero stale-check/type/tamper stages with matching identifiers.
  Seven API tests pass.46 source bindings and30 output bindings verify unchanged.
  browser-result.json, browser-cleanup.json and desktop/mobile screenshots retained;
  screenshots visually inspected. Actual browser response counts4 success/1 outage.
- `scaffold-generation/proof-LwF429/proof.json`: selected
  `node platform/builder-cli/scripts/test-generation.mjs` passes. Two independent
  frozen offline wheel-only Python installations each pass7 actual HTTP/export tests.
  All14 source bindings remain current.
- `scaffold-api-client/root-lock-k7k799ci/result.json`: npm12.2.0 resolved the
  canonical root extension in a disposable manifest copy.36 added records;771 existing
  identities/version/URLs/integrities/edges preserved.39 existing dev:true flags removed
  because the private build-tool dependencies are shared. No override/nested web lock.
- `scaffold-api-client/preservation-audit.json`:2533 preexisting nonignored files
  snapshotted;25 intentional existing edits;2508 other files unchanged, including
  concurrent brainstorming/Expense/Leave/PtS work. Historical state/resources preserved.

## RED and dependency qualification

The browser request-guard acceptance test first failed business_request for the intended
health GET, then passed with the narrowly allowed method/path/origin. Exporter import/symlink and malformed-JSON RED failures were observed in the
implementation tool transcript before their review fixes. Actual stale DTO
and tampered-output expected failures above are the outer acceptance loop.

`scaffold-api-client/ts7-1ksu1i6h` installs the pinned upstream tool with7.0.2 then fails
legacy SyntaxKind access. `compat6-rmrh9tb3` passes through compatibility shim6.0.2.
Fresh `scaffold-application/proof-kuDIrM` rejects that shim's actual global tsc-bin
collision. The shim forwards to real6.0.3; direct exact tool-owner6.0.3 removes the
wrapper/range/collision. `direct6-layout-nm9xpv2e` qualifies root/app7, nested tool6,
root TS7 bin and real upstream CLI success. Only that CLI child loads the narrowly
scoped Node26 compiler resolution hook. Normal app/builder commands remain7.0.2.

`proof-ODWZhw` passed export/drift/regeneration/type/build/tamper but its browser
assertion expected500. Inspection of installed Vite8's proxyMiddleware confirms502
for connection refusal; final proof asserts exactly that, rejecting other failures.
Its completed ordinary cleanup and failed receipt remain intact. The first focused
check directory `focused-direct6-rvmxjb6y` omitted the builder's nested installed Zod
path and failed type/schema checks; the corrected focused run records both owner
installation directories explicitly. No unexplained application expectation was relaxed.

## Impact decisions

Scaffold: extend existing renderer/templates/proof with owned OpenAPI, thin client
and HTTP consumption; reuse the existing installer for derived output. Shared UI:
no promotion; synthetic shell availability only. Agent context: root rules unchanged;
generated owner guidance records actual commands and boundaries. Documentation: tool
runbook, dependency supplement, mutable scaffold contract and KDG handoff. ADR:
0001/0059/0031 and existing ownership apply; accepted decisions unchanged.

Identity/Access/WRITE, server-backed KDG/Leave/editor, normal public scaffold generation
and full P1/SERVICE readiness remain pending. Health client output is no authorization.

## Review outcome

All three BMAD layers completed. Twelve findings received individual verdicts in the
Build spec: seven patch groups, three low rejections under the current bounded/lean
scope, one false outdated-handoff claim, and no deferrals. Duplicate safe-import
findings share one patch. Final proofs above were rerun after all patches. Safe
export/import and symlink refusals, stale-schema preservation, malformed-response
classification, real native header/body deadlines and wrapper input/output refusal
cases now have focused coverage. Runtime proxy prerequisites are explicit.

`final-source-audit.json` binds the final application/service proof documents and
confirms all46/14 checkout source hashes current. The separate preservation audit
confirms all2508 unrelated prior files unchanged. No root repository-wide test or
CI claim: checks are the affected owners and isolated local/CI-compatible harnesses.
