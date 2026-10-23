# Builder first-consumer maintenance

When a consuming app proves or fixes a reusable neutral pattern, update its owning
scaffold template and generated behavioral tests in the same delivery item. Keep
application DTOs, admission policy, branding and workflows in owner seeds/adapters.
Do not postpone applicable corrections until the app is complete or copy app policy
into a default template. Record why each new pattern is shared or remains app-owned.

For the adopted KDG Auth pattern, run the selected Node26.11.1 executable with:

- `scripts/sync-kdg-auth.mjs --check` from this directory (or repository-relative path).
- `--write` through that same script to update unedited managed copies using the
  preservation installer. Never edit generated runtime, hook, tests or manifest by hand.
- `node --test tests/*.test.mjs` here: includes current-template/KDG parity and tamper tests.
- `scripts/prove-auth-lifecycle.mjs` for actual rendered/installed neutral tests, then
  the affected KDG SDK/browser proof and full application proof as changes warrant.

Use repository-root command paths in README.md for the proof scripts. No public
runtime generator, migration of existing apps or provider configuration follows from
candidate helper qualification. Legacy templates/web is retired for new copying.
