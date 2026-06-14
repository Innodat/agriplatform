# Scribeswell — CHANGELOG

---

## 2026-06-14 — Phase 2: Multi-App Foundation

### Delivered
- **AppLauncher integrated into Topbar** — burger menu (LayoutGrid icon) appears left of brand when user is signed in; shows all enabled apps from the app-directory service.
- **`src/components/layout/AppLauncher.tsx`** — vendored from `platform/ui-business`; generic, data-driven, accessible (aria-expanded, role="menu", Escape-to-close, click-outside-to-close).
- **`src/hooks/useMyApps.ts`** — fetches `/api/me/apps` from app-directory service; silently degrades if service is unavailable.
- **`src/lib/app-directory.ts`** — singleton app-directory client wired with Supabase session token.
- **`src/schemas/bible.schema.ts`** — silo-local Zod schemas (migrated from `@platform/shared/schemas/zod/bible/bible.schema`).
- **`src/vite-env.d.ts`** — added Vite client types reference.
- **`tsconfig.app.json`** — added `@platform/app-directory-client` path alias.
- **`vite.config.ts`** — added `@platform/app-directory-client` Vite alias.
- **`.env.example`** — added `VITE_APP_DIRECTORY_URL`.
- **`package.json`** — renamed from `bible-web` → `scribeswell-web`; added `@platform/app-directory-client` dep.
- **`tsc --noEmit` exits 0** — all pre-existing TS errors resolved.

### Deviations from plan
- None.

### Remaining TODOs
- Set `VITE_APP_DIRECTORY_URL` in `.env.local` (default: `http://localhost:8001`).
- Start `services/app-directory` locally to see the launcher populate.
- Phase 3+: AppLauncher will show more apps as they are built and enabled in the catalog.
