# Platform Prompts — CHANGELOG

---

## 2026-09-04 — BMAD adopted as generic workflow

### Applied

- Superseded the custom generic SPDD direction with BMAD under ADR-0010.
- Marked this directory as an SPDD prototype transitioning to portable,
  Agriplatform-specific agent context and safeguards.
- Added Phase 1 work to reconcile the existing content rather than deleting useful
  rules or duplicating BMAD workflows.

## 2026-09-03 — ATDD and TDD made core delivery loops

### Applied

- Adopted ATDD as the outer feature loop and TDD as the inner implementation loop.
- Added ADR-0009 and `context/testing-strategy.md`.
- Routed feature, API, UI, bug-fix, and refactor work through the testing strategy.
- Required failing acceptance/regression behavior before production implementation.
- Required characterization tests before risky AI refactoring of insufficiently
  tested behavior.
- Added focused-to-broad test execution and concise verification-evidence rules to
  reduce ambiguous failures, unnecessary reruns, and avoidable agent context usage.

## 2026-09-01 — Selective SPDD governance adopted

### Applied

- Adopted selective Structured Prompt-Driven Development for substantial features,
  services, migrations, security changes, and complex refactors.
- Added `platform/prompts/README.md` defining artifact ownership, full versus
  lightweight workflows, synchronization, and recurring prompt-impact review.
- Recorded the approach in platform ADR-0008.
- Identified the current prompt pack as a prototype requiring alignment with the
  silo, service, identity, content, notification, scaffold, and UI decisions before
  the Leave implementation uses it as authoritative guidance.

### Next alignment milestone

- Reconcile `base.md`, `registry.md`, tasks, and context snippets during Leave Phase 1.
- Add prompt validation and generated/app-local prompt-pack checks alongside builder
  generation tests.

## 2026-06-28 — Workspace dependency resolution guidance

### Platform-level decisions recorded
- Internal platform packages consumed inside the monorepo should declare a local-link dependency (`workspace:*` where supported, otherwise `file:`) instead of `*` to prevent accidental npm registry lookups.
- npm workspace installs should be run from the repository root when linking unpublished `platform/*` packages.

### Prompt/rule updates recommended
- Add a monorepo dependency rule: unpublished internal packages must use a local-link specifier (`workspace:*` or `file:`) in `package.json`.

## 2026-06-14 — Phase 2: Multi-App Foundation

### Platform-level decisions recorded

**New `services/` tier adopted:**
- Top-level `services/` directory for cross-app runtime services (not silo apps, not platform packages).
- First service: `services/app-directory` — JWT-optional entitlement + app catalog.
- Services are called over HTTP; apps never import from them at build time.

**`platform/app-directory-client` sanctioned as shared FE service client:**
- The one exception to "no shared packages" — it's a typed HTTP client with a clear API contract.
- Apps resolve it via tsconfig `paths` + Vite alias (no npm workspace link needed in Phase 2).

**`platform/ui-business` seeded early (Phase 3 placeholder → Phase 2 partial):**
- `AppLauncher` + `AppLauncherItem` components written as the canonical reference.
- Apps vendor a copy per silo rules (no runtime import from `platform/*`).

**`platform/builder-cli/templates/web/` added:**
- Stampable web scaffold with `{{PLACEHOLDER}}` tokens.
- Template files are not compiled in-place (tsconfig excludes all files).

**Bible schema migration:**
- `@platform/shared/schemas/zod/bible/bible.schema` → `apps/scribeswell/web/src/schemas/bible.schema.ts`.
- Silo rule enforced: schemas live in `apps/<app>/web/src/schemas/`.

### Prompt/rule updates recommended
- Add `services/*` tier to `.clinerules` Repo Layout Rules.
- Document `platform/app-directory-client` as sanctioned shared FE client.
- Note that web scaffolds come from `platform/builder-cli/templates/web/`.
- Note that template `.ts`/`.tsx` files show VS Code TS errors (expected — no node_modules in template dir).
