# Disposable application shell proof

Baseline `6a094d0aadae0010a308be3950c39d1fe9f8fbbe`. The existing builder renders a
minimal presentational React/Vite web shell and an owning HTTP health shell, reusing
the service templates. Normal generation, current Auth/Access and full P1/SERVICE
remain undelivered; every result keeps bootstrap_only:true/generation_ready:false.

## Requirement-to-test evidence

| Requirement | Evidence |
| --- | --- |
| Preserve service output while reusing templates | application-renderer.test.mjs: whole-map SHA256 characterization taken before refactoring |
| Pure deterministic app file map, valid boundary owner and seed/generated distinction | application-renderer.test.mjs: deterministic application file map, literal identity and explicit ownership |
| Invalid/service/extension/token input refusal | application-renderer.test.mjs: invalid, service, extension and token injection recipes refuse output |
| Missing/relative tools, explicit output argument, wrong versions/cache, no writes | application-generation-guards.test.mjs: explicit refusal tests |
| Fresh failures retain previous output and lock origin | application-generation-guards.test.mjs: retained failed-output/provenance test |
| No hidden checkout dependency fallback; exact pins/local executable identities | application-dependency-proof tests and proof.json web_dependencies |
| Own extended root lock and clean selective offline installation | npm-lock/npm-ci command logs, root_lock base/extended hashes |
| Strict TS7 CSS/import checking and production Vite compilation | web-type-check/web-build logs; renderer asserts strict and selected Vite client types |
| Independent application API lock and wheel-only environment | api-lock/check/sync and four real generated runtime tests |
| Real built UI, keyboard skip focus, Home/reload, desktop/mobile, no external page requests/errors | generated browser-smoke, explicit Chromium identity, screenshots/browser-result.json |
| Actual owner health response | browser smoke's loopback HTTP health check; no authenticated business path claimed |

The smoke starts the generated owner API in an isolated Python interpreter and the
built web output through Vite preview, both on ephemeral127.0.0.1 ports. Browser page
requests stay at preview origin. API health is checked separately by the smoke process;
the UI has no business/Auth request or admission behavior. Desktop/mobile screenshots
are Chromium viewports, not physical-device acceptance. No product/editor fields added.

## Commands and outcomes

Pinned Node26.11.1/npm12.2.0, TS7.0.2, uv0.13.1, CPython3.15.0 and explicitly selected
existing Chromium. README records complete environment/tool/cache selection. The
application resolves its own API lock and extends a copied canonical npm root lock
through npm only. It creates no nested browser lock and never edits the checkout lock.

```bash
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
npm run test:generation --workspace platform/builder-cli
npm run test:generation:application --workspace platform/builder-cli
```

ATDD RED: selected node --test platform/builder-cli/tests/application-renderer.test.mjs
failed exit1 with missing application-renderer.ts before implementation. The original
tool capture, not a redirected raw log, is identified in
deployment/.local/scaffold-application/acceptance-red-record.json.

Implementation checks:21 builder tests, TS7 and schema checks pass. Source-bound
service regression proof-bCsLRv passes both independent environments after template
reuse, with13 current source bindings unchanged. Service output bytes remain identical.

Root first actual app attempt proof-jip1bf: npm lock and selective offline ci succeed
(35 packages), then strict TS7 reports TS2882 for styles.css. Original output/logs
remain. The owning tsconfig template adds selected Vite client types; it does not
disable strict checking or suppress the error. Focused RED/GREEN covers that correction.

Root corrected proof-B5FmrE passes all13 stages in13.485s: copied-root npm lock/ci,
local dependency provenance, strict type/build, own API lock/check/frozen wheel-only
install/tests and real browser checks.32 source bindings and17 output/lock bindings
are recorded, with nine exact local web dependencies and three local executable
identities. Raw commands/results/logs and screenshots are retained in that proof;
root-initial-proof.json and root-corrected-proof.json retain exact top-level argv/status.

Source identity records assume the builder source stays stable for the run, as enforced
by this session's single builder owner and final hash audit. Concurrent builder writes
during module loading are unsupported; this developer proof is not an immutable loader.

Final reviewed verification:28 builder tests pass, with type-check and schema:check
exit0. Fresh proof-Whsv74 passes all13 stages (top-level command19.109s), including
four generated API runtime tests and real desktop/mobile Chromium checks. It records
33 source bindings, nine local dependency identities, three executable identities,
copied installation manifest hashes, and screenshot/result/cleanup hashes. The root
verification records41 unchanged source bindings and exact argv/status/log paths in
deployment/.local/scaffold-application/root-final-verification.json.

Review:11 findings triaged, nine addressed and two low findings rejected with reasons
in the Build spec; nothing deferred. Focused tests cover fetch/XHR and HTTP error
refusal, ordinary and forced API exit confirmation, copied-manifest drift and generic
owner guidance. Real descendant-timeout qualification in scaffold-application/
timeout-ownership/result.json confirms the API and Chromium terminate and the API
port closes after the outer deadline. Browser success is published after teardown.

Preservation audit:2500 pre-existing files outside the six explicitly allowed prior
files remain byte-identical, including concurrent documents. Checkout root lock and
all historical receipts/state/resources remain intact.

## Impact and remaining work

Scaffold: application templates/renderer/proof added to existing builder, sharing the
HTTP templates. Historical browser templates remain untouched. Shared UI: presentational
shell is candidate template output, with no shared UI package promotion or Auth/Directory
behavior. Agent context: generated owner guidance lists commands, ownership and authority
limits; root instructions unchanged. Docs: builder runbook/evidence, mutable contract
and KDG navigation updated. ADR: existing0059/ownership/0031/0023 suffice; no ADR edited.

Next prove safe generation/custom-code preservation through the existing builder.
Normal owner installation/regeneration, current Access and complete shared/app readiness
remain explicit work. No provider/account/migration/Docker/infrastructure/deployment or
real-data action; concurrent documents and all historical proof/resources are preserved.
