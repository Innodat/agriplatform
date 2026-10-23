---
title: Keep scaffold Auth lifecycle and generated tests aligned with KDG
created: 2026-10-23
type: refactor
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Update the scaffold alongside the proven KDG pattern, including scaffolded behavioral
tests, rather than postponing promotion. New generated applications and KDG must use
the same neutral Auth lifecycle and React lifecycle binding, with owner admission,
configuration, DTO validation, permissions and branding remaining application-owned.

Given an application candidate is rendered/installed, when its generated Auth tests run,
then exercise session bootstrap, event ordering, account changes, guarded refresh,
logout precedence/local scope, disposal, deadlines and stale-result protection through
an injected neutral owner boundary. Given KDG consumes the pattern, then preserve its
existing28 SDK/domain tests, actual SDK/React browser behavior and typed own-context
validation through a thin owner adapter. Do not import another app/runtime server.

Given either template code or tests change, when builder tests/source parity check run,
then detect stale or edited KDG managed copies. Use the existing preservation installer
for narrow new managed paths and a current-template comparison; installer manifest
checking alone does not detect template freshness. Regeneration refuses manual managed
edits and preserves all owner seeds/custom files. No arbitrary output/adoption bypass.
Given future delivery, then require scaffold/code/test impact in the same item and run
parity plus generated/consuming tests for adopted neutral patterns; app-specific code
stays local. Record a clear current adoption inventory and commands.

Retire the unused legacy AuthContext fail closed with migration guidance; it must no
longer offer unsafe copy-and-run Auth. The active renderer remains an internal candidate,
not a public generator or complete Auth/provider implementation. No default credentials,
provider launch/callback/PKCE storage/return navigation or application activation.

Observe generated behavioral acceptance RED before extraction; retain focused TDD and
characterization before refactoring. Verify actual installed generated tests, fresh
application generation/type/build/browser and consuming KDG SDK/React tests. Preserve
prior evidence, concurrent changes and Docker resources; approved dependencies including
TS7.0.2 stay pinned. Synthetic local/CI only; no Leave/editor, real accounts/access,
provisioning/deployment/pilot, fingerprints/HMAC or cleanup. No accepted ADR mutation.
</frozen-after-approval>

## Implementation Notes

- bmad-help selects [BD] bmad-build. One reversible pattern promotion plus its generator,
  consumer and proof, no intent gap/irreversible operation. Dirty concurrent work is
  explicitly authorized to preserve; exclude all Leave/Scribeswell/root AGENTS edits.
- Investigation: application-renderer.ts emits only health shell; legacy templates/web
  is unreferenced by it. Existing installer permits new managed leaf paths in a populated
  KDG web root, so no old-file adoption is needed. Its manifest guards installed bytes,
  not current template identity; add explicit template equality check.
- Extract structural AuthPort/lifecycle generic and reusable React hook in application
  templates; no SDK dependency in generated applications. KDG keeps SDK compatibility,
  context client/DTO/brand and tests. Shared neutral tests live with template and are
  emitted to both apps; existing28 KDG tests stay owner-owned regressions.
- Extend renderApplication file map and existing test:generation:application harness to
  execute test:auth. Narrow internal sync/check command uses installer only for new
  src/auth files and generated script; no public generator/readiness promotion.
- Legacy retirement is explicit, not an assertion that existing apps were migrated.
  Inventory source/contract/UI/tests decisions in builder docs and scoped agent guidance.
- Five impacts: scaffold common code/tests updated now; UI hook reuse only, KDG UI stays
  local; agent guidance scoped builder/KDG/generated; docs additive evidence/handoff;
  ADR existing0059/0031/0032/0023, unchanged. No new runtime service or workflow engine.

- Generated acceptance RED proof-sUs6nl observed signed_out instead of authorized after
  actual render/install; focused seed failures proof-AVCzEK retained. Extracted current
  source initially passed20 neutral/28 owner cases; final neutral suite23 and KDG28
  now run together (51), preserving old28 source bytes. SDK/React15 checks pass.
- Preserved installer used for all real KDG managed writes. Current-template comparison
  supplements manifest hashes with exact generator/template/recipe/source identity,
  inventory and generated classifications. Hook/code/tests tamper and stale-body checks
  preserve owner files and refuse manual edits. No arbitrary target/force option.
- Full application proof reruns after reviewed source/guidance changes; all outputs
  retained. New scoped agent guidance makes same-item code/test maintenance explicit.

## Review Triage Log

Only configured Blind Hunter layer ran, using the available isolated reviewer after
known session thread limits and waiting for its complete nine findings.

- medium, patch: current bytes could pass under unrelated/seed/incomplete manifest;
  observed missing-exception RED; verify full identity, inventory and classifications.
- medium, patch: stale boundary callback could restore old admission; made neutral
  fixture intentionally unguarded and observed RED proof-7GHFqU. Ignore all boundary
  callbacks and publish only returned checked results behind the coordinator epoch.
- medium, patch (same outcome-contract root cause): return-only boundary stayed checking;
  returned outcomes now publish after current-execution guard; added explicit test.
- medium, patch: boundary clear/dispose exceptions could prevent closure/detachment;
  guard cleanup, close state first and detach SDK despite owner failures; regression passes.
- low, patch: hook factory stability unstated; document memoized Auth/boundary/launch
  dependencies with useCallback example in generated guidance; KDG already memoizes.
- low, patch: old application inventories refuse new renderer maps; document refusal,
  preserved old output/fresh candidate/explicit seed-custom port/test procedure and no
  force/in-place migration. This item only adopts newly absent KDG managed paths.
- low, patch: generated recovery lacked TOKEN_REFRESHED superseding return; new
  event-driven unauthenticated outcome test proves exactly one owner launch.
- low, patch: hook omitted from tamper/stale tests; cover all3 managed files, including
  manually edited and older-generated hook bytes.
- low, patch: narrow proof did not enforce Node pin; fail preflight before output on
  unqualified runtime and verify via injected version negative control.

No review finding deferred. Provider/domain-specific readiness remains intentionally
outside this pattern reconciliation; no scope or frozen intent change.

- Final evidence: generated23 tests via real render/install; KDG51 (23 generated+28
  unchanged owner),15 SDK/React proof checks; builder68 plus final focused6 provenance
  checks and strict TS7. Full offline application proof-5grA1c passes exact final source
  custody/type/build/browser/preservation; candidate readiness stays false.
-632 protected files unchanged, including previous evidence and dependency baseline.
  Complete prior handoff retained. Exact source/commands/results in owner receipt.
