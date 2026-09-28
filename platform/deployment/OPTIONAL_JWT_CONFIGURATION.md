---
title: Optional legacy JWT deployment configuration
type: bugfix
created: 2026-09-28
status: done
route: oneshot
review_loop_iteration: 0
---

<frozen-after-approval reason="human-owned intent">

## Intent

Production preparation must use the actual Supabase authentication configuration,
without inventing a legacy signing secret to satisfy deployment validation.
Make the legacy JWT secret optional for Directory's existing asymmetric Auth
verification and Scribeswell's public reader, while preserving explicit legacy
HS256 configuration and all existing authorization and target validation.

</frozen-after-approval>

## Implementation Notes

- Production public JWKS advertises ES256. Directory already verifies asymmetric
  tokens with the configured Auth endpoint; Scribeswell's Bible routes are public.
- Small local correction only: two manifests, two environment examples, deployment
  README and focused preflight regression coverage. No Auth implementation edits,
  new APIs, production mutations or activation belong to this correction.
- Scaffold/shared UI/agent context/ADR impacts: none; no new architectural decision.
  Existing runtime defaults already omit the legacy secret. Document optional input.

- Acceptance regression: `python3 -m unittest discover -s platform/deployment/tests -p test_host.py`
  failed on missing runtime input before the manifest correction. Full deployment suite:
  `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`: 79 passed.
- `apps/scribeswell/.local/venv/bin/python -m pytest services/app-directory/tests/test_supabase_auth.py -q`:
  sandbox HTTP test client stalled; interrupted and approved outside-sandbox retry:
  14 passed, one existing Starlette/httpx deprecation warning.
- `python3 platform/deployment/tests/container_smoke.py`: all five real non-root API
  containers healthy without outbound network; Directory and Scribeswell omit legacy
  JWT secret. `python3 platform/deployment/release.py check` and `git diff --check` passed.
- Existing deployment examples, service-owned example/docs and tests updated; runtime
  verifier and its generated template unchanged. Legacy signing still fails closed
  when the secret is absent; ES256/RS256 authenticated context tested with no secret.

## Review Triage Log

Only the oneshot blind review layer is required; dispatch edge/verification layers
were not run. All three findings checked against callers and patched:

- Medium: smoke fixtures still supplied legacy secret. Removed from both fixtures;
  real image startup verified without it.
- Medium: asymmetric tests did not prove absent-secret behavior. Parameterized both
  algorithms with/without secret; authenticated endpoint tested without it, legacy
  omission explicitly denied.
- Low: service documentation/example contradicted deployment contract. Updated
  public Auth inputs and legacy-only comments, including local quickstart. No deferrals.
