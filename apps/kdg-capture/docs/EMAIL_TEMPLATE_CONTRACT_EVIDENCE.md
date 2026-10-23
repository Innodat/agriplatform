# Numeric-code email template/configuration contract — 2026-10-23

The next slice after existing-account email entry qualifies a shared, unactivated
[platform candidate](../../../platform/deployment/fixtures/email-code-v1/README.md).
It adds a code-only email artifact and configuration fragment, verified against the
pinned CLI 2.120.0 pure GoTrue and Kong builders. It does not change KDG browser/API
runtime, native preparation, historical vendor snapshots or running Auth services.

The distinction found during investigation matters: email-provider enablement is
required for sign-in, while global signup must remain disabled. The candidate maps
email.enable_signup=true to EXTERNAL_EMAIL_ENABLED=true and auth.enable_signup=false
to DISABLE_SIGNUP=true. KDG's existing SDK still sends shouldCreateUser:false. Native
closed fixtures remain inactive with email disabled; they are not functional email
sign-in evidence. Anonymous/manual linking stay off; no membership or grant is created.

The neutral HTML contains one Token variable, no sign-in links or external resources.
The fragment selects six digits, 3600-second expiry and 60-second resend intent; the
publisher formats the latter as 1m0s. Its relative content path is for a future explicit
copy into a qualified disposable project; nothing here performs that copy. The test
supplies resolved input and a synthetic mount path. It proves neither configuration
parser/path-reader behavior nor actual server rendering, SMTP, expiry, single-use,
resend invalidation or unknown/unconfirmed-account behavior.

Existing [email-entry evidence](EMAIL_CODE_ENTRY_EVIDENCE.md) retains SDK/browser
persistence, safe error, retry, cancellation, reconnect and current-access coverage.
Those injected tests do not become Auth-backed delivery evidence through this slice.
The platform candidate README provides the scenario/evidence/remaining-work matrix.

ATDD observed missing candidate/template acceptance failures before adding artifacts.
Focused checks validate code-only content, closed account-creation policy with email
login enabled, and actual pinned publisher URL/mount/length/expiry/throttle mapping.
The [durable receipt](evidence/email-template-contract-20261023.json) binds exact
commands, RED/GREEN logs, sources and preservation. Ordinary discovery without a Node artifact selector explicitly skips the publisher
comparison; it is never qualification. With KDG_EMAIL_CODE_REQUIRE_PUBLISHER=1,
missing selection fails qualification with zero skips, as the negative control proves.

Scaffold impact: generated guidance references the shared platform artifact and tests,
with no automatic method selection, copying or activation. Shared UI: none; this is an
email artifact, current KDG presentation unchanged. Agent context: existing ownership/
parity guidance sufficient, no edit. Documentation: new evidence/receipt, platform
fixture guidance and prepended handoff. ADRs unchanged; operational logging/session
principles 0023/0032 remain binding. No migration/release activation occurs.

Synthetic local/CI only. No email, real account/access, provisioning, Docker command,
production, deployment/pilot, Leave/editor, cleanup or fingerprints/HMAC work. Concurrent
changes, historical artifacts and approved dependencies including TS 7.0.2 are preserved.

Final verification: 28 affected Python tests pass, including all five contract tests
with zero skips; 68 builder tests pass. Missing-selector strict-mode negative control
refuses qualification with zero skips. All five review findings are patched, no
deferrals. Follow-up review was static; the final test runs are recorded in the receipt.
Prior runtime/browser proof is preserved and was not rerun for this artifact-only slice.
