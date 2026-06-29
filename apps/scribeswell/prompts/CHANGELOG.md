# Platform Prompts — CHANGELOG

---

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
