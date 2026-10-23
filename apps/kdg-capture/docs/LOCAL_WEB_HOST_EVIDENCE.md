# Explicit local web host — 2026-10-23

bmad-help [BD] selected the next missing local runtime prerequisite after actual startup:
serve the real frontend through explicit Vite configuration with same-origin KDG API
routing. bmad-build implements this freeform prerequisite, not complete Story 1.1.
The owner file validates exact existing public fields plus a loopback API origin from
an explicit bounded file outside served roots. No config search, root workspace, lock,
dependency, provider, environment activation or shared infrastructure change occurs.

Canonical neutral helper/tests are emitted through the application renderer. KDG adopts
them through the preservation installer in a separate managed local-host-tools root;
the existing fixed Auth inventory remains untouched. CI checks exact source/identity/
classification/inventory and rejects manual generated edits. Owner policy/branding/
API route and config file validation remain in local-host.config.ts. Shared UI unchanged;
agent context existing ownership guidance sufficient; docs and additive handoff updated;
ADRs unchanged, applies 0023/0031/0032. No migration or release activation.

The behavioral acceptance RED starts actual FastAPI and Vite without the new host,
then fails waiting for Sign in. The unconfigured host cannot reach usable entry; later
module diagnostics also identify stale root TypeScript discovery. This RED does not
isolate null-config UI behavior (the prior startup proof covers that).
Focused GET-body forwarding and malformed/truncated response tests failed before fixes.
Initial missing-manifest-ownership/type/module-discovery attempts are retained diagnostic
frames, not extra behavior claims. Runtime discovery found Vite inheriting stale root
project references; the owner now explicitly selects tsconfig.auth.json.

The proof copies source into a new private capsule, verifies hashes before execution and
afterwards, and uses retained approved dependencies. It launches actual Vite CLI with
actual owner config and actual KDG FastAPI/Uvicorn over loopback. KDG uses its existing
explicit synthetic httpx Access seam; no shared service implementation is imported.
Browser Auth OTP/verify is synthetic loopback HTTP, not a real Supabase/SMTP runtime.
The browser performs actual SDK sign-in, same-origin context admission, reload/current
denial and an actual API-process outage. Selectors and unknown API paths fail safely.
Invalid/missing/oversized/extra/private/remote/inside/dependency/symlink configs and
unsafe --host overrides fail before listening. Ambient VITE values and private config
file reads are refused. Browser errors/statuses and process log sentinels are checked,
including the exact generated synthetic bearer. Owned child exits, failed frames and
all earlier evidence are retained; no Docker lifecycle or resource cleanup occurs.

Neutral tests cover inert HTML-safe serialization, invalid policy, route/header/body
restrictions, redirect/size/type/UTF-8 JSON refusal, upstream outage and actual 12-second
stalled-response termination. Renderer+installer output executes emitted tests; KDG
parity/tamper tests run alongside builder regression. Existing Auth/API tests remain
regression evidence and are not relabeled as new provider/runtime qualification.

[Durable receipt](evidence/local-web-host-20261023.json) records exact commands/results,
source/proof hashes, RED/GREEN classification, review triage and preservation checks.
This proof qualifies a retained-capsule local command only; a normal installed KDG
workspace/root dev command, real Access/SQL in this composed run, actual Auth/SMTP
rendering/delivery/expiry/reuse/resend invalidation, actual BFCache and device/LAN HTTPS
remain unqualified. Historical native API/Access proof remains separate and unchanged.
Synthetic local/CI only: no real accounts/access, production, Leave/editor, provisioning,
deployment/pilot or cleanup. Fingerprints/HMAC and TypeScript 7.0.2 baseline stay intact.

Final runtime capsule: proof-ec214ec7-49c7-4171-85e5-d30600eaf409, 10 checks with
strict host TS 7.0.2, exact source-copy bindings and confirmed unforced child exits.
Neutral host: 5 tests, including the actual stalled-response deadline. Builder: 70 tests
and strict types. Existing Auth: 170 tests / 71 checks. Existing API: 79 tests with the
known upstream Starlette/httpx deprecation warning. Fresh offline generation:
proof-tyQXOu, bootstrap_only=true, generation_ready=false. Review: seven original and
two follow-up findings patched; final read-only follow-up found no remaining concrete
issues. Full command/result/source preservation details are in the receipt.
