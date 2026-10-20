---
title: 'P1/SERVICE scaffold recipe preflight'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: '82e508981ff7f259ea54df7508ff68b41d457c37'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
---

<frozen-after-approval reason="standing user approval for bounded prerequisite implementation">

## Intent

The existing builder has templates but no runnable recipe validation. Implement the
first bounded P1/SERVICE input preflight, so developers can check explicit scaffold
choices without pretending templates or application authorization are delivered.
The user authorized implementation and continuation while preserving concurrent work;
this increment follows the approved lean direction and requires no external action.

## Boundaries & Constraints

Always use the existing builder owner and root npm workspace/lock. Use Zod4.6.7 as
the single schema authority, exporting versioned JSON Schema; TypeScript7.0.2,
Node26.11.1/npm12.2.0 and @types/node26.6.5 remain the approved tools. Keep code
small: ordinary schema refinements and filesystem checks, no generic validator engine.
Success means recipe_valid:true, generation_ready:false; candidates are never proof.
All validation is read-only, errors contain safe identifiers rather than input values.

Never implement generation, DB/API fields, grants, service behavior, Leave, an editor,
Docker operations, migrations, remote calls or a readiness/receipt engine. Preserve
historical resources/state and unrelated work. Do not edit accepted ADRs or existing
template behavior. No public candidate bypass or generate stub.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Result |
| --- | --- | --- |
| Application/service | Complete supported recipe, existing refs | Successful validation with generation_ready:false; no files written |
| Invalid shape | Unknown keys, version/type/bounds/duplicate violations | Nonzero, stable safe error identifier |
| Unsupported composition | Unknown patterns, conflicting auth, missing saving.none, wrong owner variant | Refuse; infer no default |
| Unsafe references | Missing authority file, traversal/absolute/symlink path, missing custom directory | Refuse without writes |
| Extensions | Escaping or overlapping destinations/sources | Refuse; adjacent distinct extensions accepted |
| First generation manifest | Safe owner-local manifest path absent | Accept reference only, no manifest created |
| CLI misuse | Missing/unknown/duplicate args or malformed JSON | Nonzero safe diagnostic, no payload echo |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/README.md`: placeholder status and stale ENV introduction;
  update only active status/commands and boundaries, keep historical guidance.
- `platform/builder-cli/templates/`: unproven existing source; do not change/promote.
- `package.json`, `package-lock.json`: root already owns platform/* workspace discovery;
  add builder package through normal npm lock tooling, preserve other dependencies.
- `platform/env-web-qualification/package.json`: exact selected package versions;
  root node_modules may contain older Zod, never silently test against it.
- `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/`:
  retained qualified node/bin/node, npm/bin/npm-cli.js and packages/node_modules tools.
- `platform/deployment/.local/scaffold-recipe/protected-before.json`: root's preservation
  snapshot; root owns audits, handoff/shared-prerequisite updates and commit.

## Tasks & Acceptance

**Execution:**
- [x] `platform/builder-cli/tests/`: write CLI acceptance first, observe meaningful RED,
  then focused tests for every matrix row. Keep commands/results in implementation notes.
- [x] `platform/builder-cli/package.json`, `tsconfig.json`, `src/`: add validate:recipe,
  test, type-check and schema export/check scripts. CLI accepts exactly --config <path>,
  relative to caller or absolute; resolve references against repository root. No output option.
- [x] `platform/builder-cli/schema/`: export scaffold-v1.json from Zod source,
  check drift; patterns-v1.json lists only six initial candidate IDs: api.owner-http.v1,
  web.react-shell.v1, auth.organization-account.fixed.v1, auth.service-owner.v1,
  errors.safe-envelope.v1, saving.none.v1. Record template version and actual authoritative
  contract/test references; explicitly candidate status, no fabricated proof.
- [x] Enforce exact contract recipe keys/types and bounds. Require api/errors/saving.none;
  applications require web/account.fixed, services require service-owner and exclude web.
  Other patterns remain unsupported until consuming implementation. Sources/contracts
  are distinct existing regular files, extensions sources existing directories, destinations
  normalized output-relative paths; reject symlinks and escapes. Manifest is below
  apps/<owner>/deployment or services/<owner>/deployment (owner underscores may map to
  hyphens); absence permitted, existing path must be regular and safe. Refuse extension
  nesting/overlap; no reading referenced file contents or output creation.
- [x] `package-lock.json`: normal npm workspace resolution, no manual lock editing or
  unrelated baseline upgrades. Offline install/cache permitted; report unavailable tools.
- [x] `platform/builder-cli/README.md`: actual commands/status and impact decisions.
  Root updates handoff/shared-prerequisites and evidence after independent verification.

**Acceptance Criteria:**
- Given app/service synthetic fixtures, when the documented npm command runs, then
  matrix behavior is proven through the actual CLI and file snapshots remain unchanged.
- Given a structurally valid recipe, when checked, then it grants no authority, generates
  no output and explicitly reports generation_ready:false.
- Given checked-in schema, when export check runs, then it matches the authoritative source.

## Implementation Notes

Investigation found no existing generator command. This is partial P1/SERVICE delivery.
No intent gaps or irreversible actions; new CLI/schema warrant dispatch. Implementation
agent owns builder paths and npm lock only. Do not commit; root handles review/docs/commit.

Implementation GREEN:7 tests, type-check and schema:check pass with pinned tools.
Exact logs/argv in platform/deployment/.local/scaffold-recipe/. RED was the direct
recipe.test.mjs invocation before CLI existed: four failed assertions reported missing
src/cli.ts; tool exit was0 despite node:test failures. Original output is in the
implementation conversation only. Matrix rows audited against all seven executed
tests; no implementation or generated-output readiness claimed.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: npm caller-relative path | medium / patch | Root reproduced documented invocation returning config_unreadable for existing valid recipe; caller-relative-red.json retained. |
| Blind2: nested symlinks in extension tree | low / reject | Directory itself/ancestors are checked, contents are not read/copied in this preflight. Recursive tree admission belongs with generation; adding a tree walker now adds complexity for an unconsumed tree. Document boundary. |
| Blind3: FIFO/oversized config | low / reject | CLI reads explicit local developer config without regular-file/size guards. No untrusted ingestion exists; special-input guards add branches for uncommon developer misuse. Keep proportional to present use. |
| Blind4: read-only destination coverage | medium / patch | Fixture snapshots exclude manifest destination; explicit absence assertion closes a real regression gap. |
| Blind5: six versus ten candidates | low / patch | Mutable contract needs to distinguish six implemented input choices from proposed catalogue expansion. |
| Blind6: missing shape/type/path boundary cases | low / patch | Existing 18/21 mutation sets omit representative wrong types, missing keys and equal destinations. Add direct cases without changing behavior. |
| Blind7: no complete runnable recipe | low / patch | README has field descriptions but no full valid input; one example using real authority references makes command usable. |
| Edge1: npm caller-relative path | medium / patch | Same reproduced cwd defect as Blind1; group same fix. |
| Verification1: manifest noncreation coverage | medium / patch | Filed regression evidence establishes test blind spot; group with Blind4. |
| Verification other1: npm caller-relative path | medium / patch | Reviewer reproduced direct versus npm different results; group with Blind1/Edge1. |


## Verification

Use pinned Node/npm above, npm workspace test/type-check/schema-check, CLI fixtures,
then focused native ENV regression only if shared files change. Record actual versions,
RED/GREEN and matrix-to-test evidence. Root audits protected files with owned docs/lock
exceptions. Scaffold impacted; shared UI and root agent context unchanged; docs updated;
ADR0059 applies, no new decision needed. Full generation/install/build/start/current
Access, provider/device and Identity/Access/WRITE remain separate undelivered work.

Final root verification:8 tests pass, type-check/schema:check and actual npm caller-relative command pass. Eleven bound code/schema/test/manifest/lock files unchanged during checks. Three reviews:10 findings individually triaged,8 addressed and2 low rejected; no new deferrals. Preservation audit:2475 protected pre-existing files unchanged. Exact logs/hashes retained in platform/deployment/.local/scaffold-recipe/.
