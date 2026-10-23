# Actual local frontend startup — 2026-10-23

The actual owner index/main now connects inert public configuration to the local route
mount. Default HTML contains null configuration and stays closed. Exact versioned local/
CI fields and loopback host/Auth rules are KDG-owned; the bounded inert-script reader and
emitted tests are scaffold-owned and synchronized in the same item. No default target,
URL/browser-store/environment override or root dependency/workspace change is added.

Pure validation rejects unknown/invalid fields, private keys, non-loopback hosts/Auth
origins, noncanonical orgs and unsupported environment kinds. The neutral reader requires
one application/json script, no src, <=8192 UTF-8 bytes and safe parse; all errors are
opaque. Root absence/duplication fails closed. Startup uses the existing branded failure
and route scrub surface. Same-origin KDG API admission remains mandatory.

An early instrumented actual-build run found SDK import-time storage reads/writes even
with no client constructed. Validation was separated into a pure owner module; startup
now observes config/route/connectivity before dynamically importing the Auth mount. A
started import can still finish after cancellation; current checks prevent stale mount,
not retroactive cancellation of SDK import side effects. Default/invalid initial inputs
perform zero Auth/API/storage work in the actual browser proof.

The host validates first and creates a React Root once; preflight observation is disposed
before handing ownership to LocalEntryRoute so its scrub cannot be reinterpreted by a
second observer. Pagehide disposes active work/root; persisted pageshow restarts and
rechecks current context. No cached authorization or unfinished-input retention promise
is added. Real SDK/session and route behavior from previous evidence remains binding.

Proof builds the copied actual app directory/index/main as a second Vite input, not a
synthetic replacement entrypoint. Browser storage instrumentation runs before modules.
The server supplies synthetic inert config variants with safe serialization, explicit
SPA fallback, synthetic loopback Auth OTP/verify responses and current-context API data.
A virtual remote host is fulfilled from local proof files without external requests,
proving host refusal. Default/missing/malformed/oversized/duplicate/wrong-type/src/extra/
org/key/remote-Auth/root/callback/query/fragment/offline cases are checked. Valid startup
uses actual SDK HTTP, reload/current denial and real Back reload with fresh API. The
retained headless shell reports BackForwardCacheDisabledForDelegate through CDP;
actual BFCache restoration is unqualified. A separate explicitly simulated persisted
pagehide/pageshow checks current denial, an empty root before restart and no old
admission after restart. Held/rejected lazy chunks cover disposal, offline/route
refusal, explicit recovery and safe import failure.
This is not a real Supabase Auth server, SMTP rendering/delivery, one-use/expiry/device
or full Story1.1/environment qualification.

ATDD observed missing scaffold reader and actual startup behavior before implementation.
Initial owner-test capsule import-path failures are retained diagnostic frames, not
behavioral RED. Focused parser tests exposed array environment coercion and trailing
newline org acceptance; both were fixed without relaxing expectations. Import-time
storage probe failure is retained with the successful preflight proof.

[Durable receipt](evidence/local-frontend-startup-20261023.json) binds exact commands,
RED/GREEN/source/proof hashes, review triage and concurrent/historical preservation.
Scaffold impact: neutral reader/tests/guidance, unchanged managed inventory. Shared UI:
owner ClosedEntry extracted/reused, no platform package promotion. Agent context unchanged;
existing ownership guidance sufficient. Docs: owner/scaffold README, evidence/receipt and
prepended handoff. ADRs unchanged; applies 0023/0032, no migration/release activation.
Synthetic local/CI only; no real email/account/access, provisioning, production,
deployment/pilot, Leave/editor, Docker or cleanup. Fingerprints/HMAC remain deferred.

Final owner capsule: auth-80debba7-f84b-4c11-b672-e9b8b0315ca5, with 108 emitted,
48 existing owner and 14 configuration tests (170 total), 71 compiler/SDK/React/browser
checks, unchanged sources and stopped server. Neutral: proof-heQYzO, 108 tests. Builder:
68 tests and strict TS 7.0.2. Managed parity and fresh offline generation are recorded
in the receipt; generation remains bootstrap-only, generation_ready=false. All eight
review findings and the follow-up deterministic-import checkpoint gap resolved.
