# P1/SERVICE recipe preflight evidence

Bounded input preflight only, based on
`82e508981ff7f259ea54df7508ff68b41d457c37`. The existing builder now checks an
explicit version1 recipe. A passing check reports `recipe_valid:true` and
`generation_ready:false`. No generator, runtime authorization or template proof is
claimed. All six catalogue entries remain candidates.

## Requirement-to-test evidence

| Requirement / matrix row | Executed test |
| --- | --- |
| App/service explicit patterns; absent first manifest; adjacent extensions; read-only CLI | recipe.test.mjs: acceptance: app and service CLI validate without output or authority |
| Documented npm command honors caller-relative configuration | recipe.test.mjs: documented npm workspace command resolves config relative to invocation directory |
| Closed keys, types, bounds, duplicates, unsupported pattern composition | recipe.test.mjs: strict shape, bounds, uniqueness and unsupported combinations |
| Missing/traversing/absolute/symlink references; extension overlap and owner boundaries | recipe.test.mjs: unsafe references, extension overlap and owner manifest boundaries |
| Missing/unknown/duplicate CLI arguments; malformed JSON; safe diagnostics | recipe.test.mjs: CLI misuse and malformed JSON yield safe stable identifiers |
| Absent/regular manifest accepted; directory/symlink/blocked ancestor refused | references.test.mjs: manifest permits absent and regular owner-local files; refuses symlinks, directories and blocked ancestors |
| Exported structural JSON Schema matches Zod authority | schema.test.mjs: exported schema matches authoritative Zod source |
| Candidate catalogue IDs/status and existing contract/test references | schema.test.mjs: catalogue has exactly six candidates with actual contract/preflight test references |

The CLI tests snapshot their synthetic fixture before/after each recipe check. They
invoke the actual CLI with repository-relative authority references and both caller-
relative and absolute configuration paths. Semantic and filesystem refinements are
additional to exported structural JSON Schema, explicitly documented in the runbook.

## Commands and results

Verified Node26.11.1 and npm12.2.0 from the retained toolchain payload:
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/`.
Use its node/bin first on PATH and node/bin/node npm/bin/npm-cli.js for npm commands.
Normal offline npm workspace installation used the existing qualification cache;
the lock adds only the builder workspace/link and its exact Zod4.6.7 resolution.
TypeScript7.0.2 and @types/node26.6.5 are exact builder declarations.

ATDD RED: qualified `node platform/builder-cli/tests/recipe.test.mjs` before CLI
implementation failed four tests; the app/service acceptance reported missing
`src/cli.ts`. This original output was captured in the implementation conversation,
not retained as a raw disk log. The tool reported exit0 for that direct-file
node:test invocation despite four failed assertions; RED is the assertion output,
not a claimed nonzero process result. A sandbox subprocess attempt also encountered EPERM;
actual CLI subprocess verification ran with authorized local escalation.

Implementation GREEN: seven tests pass, no skipped/cancelled tests; type-check and
schema:check exit0. Exact argv/results and raw logs are retained under
`platform/deployment/.local/scaffold-recipe/implementation-verification.json` and
`implementation-{test,type-check,schema-check}.log`.

```bash
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
```

Final root verification:8 tests pass, zero skipped/cancelled, in8.351s; type-check
and schema:check exit0. The actual documented npm invocation with a repository-
relative config also exits0. All11 code/schema/test/manifest/lock bindings remained
unchanged during checks; exact hashes, argv and results are in
`platform/deployment/.local/scaffold-recipe/final-verification.json` and final logs.
No Docker invocation, migration or production action occurred.

Three independent reviews raised ten findings. Eight findings were addressed across
caller-directory handling, stronger read-only/type/path tests and documentation.
Two low findings were rejected to keep this increment proportional: recursive
extension-content admission belongs with actual generation, and special-file/size
guards are unnecessary for the current explicit local developer-file input. No new
deferrals. Every verdict is recorded separately in the Build record.

The npm path regression had a new observed acceptance RED before correction:
`caller-relative-acceptance-red.log` retains exit1/config_unreadable. Focused GREEN
and the root's actual command RED/GREEN JSON remain alongside it. CLI resolves npm's
invocation directory only in the builder validate:recipe lifecycle; direct Node calls
continue to use their caller directory.

Preservation audit:2475 pre-existing files outside the five explicitly owned prior
files are unchanged, including concurrent Expense/brainstorming documentation and
existing template sources. Snapshot/audit retained in the same evidence directory.
Historical ignored runtime resources/receipts were not used as output or mutated;
no broad filesystem/Docker cleanup or root repository-wide build claim.

## Impact decisions and remaining work

Scaffold: schema/source, candidate catalogue, read-only command and tests added to
the existing builder. Existing templates remain unchanged/unproven. Shared UI: no
runtime surface, no promotion. Agent context: root rules suffice; generated owner
guidance belongs with actual output. Documentation: builder runbook, this evidence,
mutable contract and KDG navigation updated. ADR:0059 applies; no accepted ADR edit
or new architecture decision.

Next bounded scaffold work is initial disposable generation through this builder,
proving owner output and preservation before promotion. Full P1/SERVICE acceptance
still requires regeneration/custom preservation, declared locked dependencies,
install/type/build/start and current narrow Access paths. Identity/Access/WRITE,
application migration/fixture ownership, provider/device and server-backed KDG remain
separate work. The local Supabase foundation stays available through its normal CLI
route; historical interception qualifiers do not return as prerequisites.
