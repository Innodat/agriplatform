# Story 3.1 bounded own proxy and built-shell host — 2026-10-29

The generated disposable local host now declares GET, POST and PUT separately per exact
route, with a canonical nonnil lowercase UUID slot where needed. KDG adopts the exact
existing own context/provision/history/detail/edit-context/recovery paths, POST capture
and PUT capture, alongside unchanged administrator GET paths. All API owners still
perform authorization. No administrator write route or generic API proxy is exposed.

POST/PUT require JSON with no content encoding. The helper reads streamed UTF-8 bytes
under a declared bound, rejects invalid/oversized input before opening the upstream,
and forwards the original validated bytes with only JSON headers and the caller bearer.
KDG command bodies retain the owner cap of 131,072 bytes. One twelve-second deadline
covers request-body consumption plus upstream response. Existing GET body refusal,
response limits, safe JSON failures, private/no-store handling, redirect refusal and
upstream cancellation remain covered. No cookies, service keys or ambient headers cross.

The separate application-owned `web/scripts/serve-local-shell.mjs` serves only selected
built public files and exact `/` or `/admin` HTML, with no source/config/arbitrary-file
fallback. It uses the same generated proxy and application route inventory as the Vite
host. It requires an absolute real built directory and an explicit input file outside
the application, served root and dependency directories. Exactly five validated public
fields must equal the built index configuration; `api_origin` remains server-side.
Startup reads bounded fixed files, rejects symlinked assets, and does not mutate built
HTML. Only literal 127.0.0.1 is bound; Host must match its actual listening port.

Launch from repository root with retained Node 26.11.1:

```sh
KDG_LOCAL_SHELL_DIST=/absolute/fresh/dist \
KDG_LOCAL_WEB_CONFIG=/absolute/private/synthetic-public.json \
KDG_LOCAL_SHELL_PORT=0 \
"$N" apps/kdg-capture/web/scripts/serve-local-shell.mjs
```

Readiness is one JSON line containing `kind: kdg_local_shell_ready` and the selected
loopback `origin`. There is no provider setup, migration, credential creation or release
activation. SIGTERM closes normally, with a bounded shutdown deadline.

## Observed failures and corrections

The new streamed-write acceptance first failed with `local_entry_host_invalid` because
the old generated route schema accepted GET only. Its initial fixture started the API
before the failing constructor and needed interruption; cleanup now belongs to the test
from fixture creation. During development, raw-client socket reuse and an unframed GET
body produced ECONNRESET/HTTP400. The fixture now uses independent sockets and an
explicit GET Content-Length; valid body-bearing GET still must return422. No application
behavior expectation changed. The built-host test first failed ERR_MODULE_NOT_FOUND
before its application-owned implementation existed.

The existing rendered-test harness returned suspiciously quickly under inherited
`NODE_TEST_CONTEXT`. A standalone emitted run exercised its twelve-second test. Clearing
only the child-runner context and asserting named streamed-write coverage plus ten
executed tests made the nested rendered proof run for12.78seconds. Passing process exit
alone no longer suffices for this proof.

## Final focused verification

Retained safe source-bound receipt:
`platform/deployment/.local/kdg-local-shell-host/final-E0ZuE8/result.json`.
Its `tests.log` and `parity.log` preserve actual output. All fourteen explicitly selected
source bindings remained unchanged through execution. No prohibited fixture or recursive
application-tree copy was used.

```sh
"$N" --test platform/builder-cli/tests/local-host-pattern.test.mjs \
  apps/kdg-capture/web/local-host-tools/test-local-entry-host.mjs \
  apps/kdg-capture/web/tests/local-shell-host.test.mjs
"$N" platform/builder-cli/scripts/sync-kdg-local-host.mjs --check
```

Result:15 top-level tests pass in13.20seconds, including the fresh rendered/installed
helper's ten emitted behavioral tests. Cases cover actual streamed JSON POST/PUT, exact
byte preservation, malformed UTF-8/JSON, empty/oversized bodies, declared-length refusal,
wrong content type/encoding, exact methods/paths, GET compatibility, stalled incoming
and outgoing streams, safe credentials, static file refusal, real CLI readiness and
normal owned-child shutdown. Parity passes. A separate selected-source strict TS7.0.2
`tsconfig.local-host.json` check passes; retained log:
`platform/deployment/.local/kdg-local-shell-host/types-oYESLt/types.log`.

This evidence uses synthetic HTTP and synthetic built files. Actual revisioned built
shell/service-worker/browser and provider/database saved-work delivery are separate
coordinator evidence; these focused tests establish neither installed-device support
nor completed Story3.1 acceptance.

Scaffold: neutral method/body bounding and behavioral tests live in builder templates,
with KDG adoption performed only by `sync-kdg-local-host.mjs --write`. The generated
manifest was never hand-edited. Application routes/static host remain KDG-owned.
Shared UI: unchanged. Agent context: existing guidance suffices. Documentation: this
focused record plus coordinator-owned Story3.1 evidence/handoff. ADR: existing bounded
HTTP, safe diagnostics, authorization and public-only shell decisions apply; no new
architecture decision. Pinned tools were reused with no installation or upgrade.
