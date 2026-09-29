---
status: done
route: oneshot
---

# Production registry token compatibility

## Intent

Continue the approved first production release by accepting GitHub's current stateless installation tokens through the existing private registry credential transport. Preserve stdin-only transport, bounded inputs, temporary credential cleanup and release safety gates.

## Acceptance

- Given a legacy or stateless GitHub token, when CI validates and transports it, both shell and host validators accept its bounded base64url/JWT characters without disclosing it.
- Given whitespace, shell punctuation or an oversized credential, when validation runs, it fails before subprocess execution with a safe diagnostic.
- Existing credential cleanup and cancellation behavior remain tested.

## Implementation Notes

The approved run 36551240426 passed browser, gateway, container and WireGuard checks but exited in 139ms in ci-deploy.sh, before deployment transport. GitHub now issues ghs_APPID_JWT tokens; the prior alphabet excluded dots and hyphens. The precise rejected value is intentionally unavailable; this incompatibility is reproduced with a synthetic token. No raw credentials were examined.

Changed ci-deploy.sh and registry-deploy.py to accept dots and hyphens under the existing 4096-character bound. Added non-sensitive diagnostics for invalid registry credentials/run identifiers. Tests first reproduced both missing format support and silent validation failure, then passed.

Scaffold: release tooling itself owns this change. Shared UI: none. Agent context: no change. Documentation: this delivery record. ADR: existing release and sensitive logging decisions retained; no new decision. Database, application behavior and authorization: unchanged.

## Verification

`python3 -m unittest discover -s platform/deployment/tests -p test_registry_auth.py`: before fix, 2 failures of 8; after fix, 8 passed. The full deployment suite passed 112 tests outside the sandbox (the sandbox blocks the TLS fixture from binding a local port). The complete shell/SSH/parser fixture uses a stateless token and asserts it never appears in arguments or output.

## Review Triage Log

- Low, patched: stateless fixture now traverses the complete shell/SSH/main-parser test; exact hash and secret absence verified.
- Low, patched: accepted 4096-character boundary now tested through shell validation and main's bounded reader; 4097 rejection already covered.
- Low, patched: missing, empty and malformed run IDs/attempts now assert safe diagnostics without token disclosure.

Final focused registry suite: 10 passed. No runtime behavior outside registry input compatibility changed; no deferred findings.
