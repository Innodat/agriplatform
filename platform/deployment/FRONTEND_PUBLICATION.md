---
status: done
route: oneshot
---

# Publish the assembled platform frontend

## Intent

Complete the approved first production release by making Netlify publication independent of monorepo application discovery. The production run 36555147676 activated the backend successfully, then Netlify CLI 23.6.0 rejected publication with “Projects detected” because the repository contains several workspace packages. The assembled artifact contains both PtS and Scribeswell and must not select just one silo.

## Acceptance

- Given the verified assembled artifact, when CI publishes after backend activation, Netlify runs outside the workspace with both applications, redirects and original configuration intact, using --prod --no-build.
- Given a missing release identity, when publishing is attempted, no provider command runs.
- Given successful publication, the existing recorder still verifies provider identity, configuration and public APIs before marking the release complete.

## Implementation Notes

Added publish-frontend.py to copy only the prebuilt artifact and netlify.toml to a temporary directory, execute the pinned CLI there and preserve its JSON result in the original working directory. Workflow uses this helper after the unchanged activation gate. README recovery command uses the same helper. No backend, database, authorization or content changes.

Scaffold: shared release tooling changed directly. Shared UI: none. Agent context: none. Documentation: recovery instructions and this delivery record. ADR: existing coordinated release policy preserved; no new decision.

## Verification

Observed the original real CLI failure in production CI. The new acceptance test for CI wiring failed before the workflow edit, then all three publisher tests and four workflow tests passed. Tests verify both app artifacts, redirects, configuration, deployment flags and evidence output.

## Review Triage Log

- Medium, patched: output uses exclusive creation and recovery selects netlify-retry.json, preserving original evidence.
- Medium, patched: timeout terminates the dedicated process group and waits for the CLI parent before removing temporary files. Covered group termination and failure cleanup.
- Low, patched: publication uses explicit /tmp rather than environment-selected TMPDIR; current repository and runner checkouts are outside /tmp publication directories.
- Verification gap acknowledged: mocked acceptance does not establish actual provider behavior. The next real CI publication must pass before release success is claimed. Original CLI failure provides baseline evidence; five publisher tests now pass, with live verification still pending.

Full deployment regression before review corrections: 117 passed. Subsequent focused publisher tests: 5 passed. No database or frontend artifact content edits.

Live confirmation: production run 36557197420 successfully published with pinned CLI 23.6.0, verified provider identity and public API configuration, and passed real public-browser checks. Final deployment regression suite: 119 passed.
