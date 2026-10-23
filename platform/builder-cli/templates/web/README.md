# Retired legacy web template

Do not copy this directory into an application. It predates the pinned application
candidate, safe Auth lifecycle and generated behavioral tests. Its AuthContext exports
now refuse execution with legacy_auth_template_retired; existing copied applications
are not automatically migrated by this source change.

Use the internal application renderer at ../../src/application-renderer.ts and the
managed src/auth/lifecycle.ts, src/auth/use-lifecycle.ts and scripts/test-auth-lifecycle.mjs
under ../application/web. Those files accept an owner Auth client, interactive action
and current application admission boundary. They never create grants, select an
organization or configure a provider. Public generation remains gated.

See ../../AUTH_PATTERN_EVIDENCE.md and ../../README.md for generation, consuming KDG
parity, preservation checks and the exact synthetic qualification limits. Legacy
manifests remain historical; they are not the approved dependency baseline.
