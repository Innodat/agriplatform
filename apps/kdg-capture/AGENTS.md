# KDG scaffold parity

Follow the root policy and current docs/next-session.md scope. When fixing reusable
neutral behavior, update the builder-owned template and its generated behavioral tests
alongside the KDG consuming regression. Keep KDG API contracts, permission/fixed-org
checks, domain workflows and branding local. Record every scaffold/UI/context/docs/ADR
impact in the delivery item; do not wait until KDG completion to reconcile the scaffold.

Managed Auth runtime/hook under web/src/auth and web/scripts/test-auth-lifecycle.mjs
come from platform/builder-cli/templates/application/web. Never hand-edit these or
web/.generated-files.json. Use selected Node26.11.1 from repository root:

- `node platform/builder-cli/scripts/sync-kdg-auth.mjs --check`
- `node platform/builder-cli/scripts/sync-kdg-auth.mjs --write` after template changes;
  manual managed edits are refused and must be reviewed, never force-overwritten.
- `node --test platform/builder-cli/tests/auth-pattern.test.mjs`
- `node apps/kdg-capture/web/tests/auth-proof.mjs` for generated and KDG SDK/browser tests.

See web/README.md for retained tool paths and proof limits. Parity covers adopted
neutral files and tests, not every application-specific source file. New reusable
patterns must be deliberately added to the scaffold, consuming adoption and test map.
Preserve old evidence and concurrent work; no new dependency or provider assumptions.

Memoize the boundary factory and interactive launch for the generated React hook.
Owner boundaries return validated outcomes; callbacks are not admission publication.
