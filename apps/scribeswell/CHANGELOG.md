# Scribeswell — CHANGELOG

---

## 2026-06-28 — Bible response contract alignment

### Delivered
- Fixed Scribeswell Bible frontend Zod schemas to match the actual FastAPI response envelopes from `apps/scribeswell/backend`.
- Updated reader page consumers to read book and verse lists from `{ data, total }` instead of non-existent `{ books }` / `{ verses }` properties.
- Verified `npm run build` succeeds after the schema/client alignment.

### Deviations from plan
- None.

### Remaining TODOs
- Start `services/app-directory` on port `8001` if you want the app launcher to populate without `ERR_CONNECTION_REFUSED` in the browser console.

## 2026-06-28 — Workspace dependency fix

### Delivered
- Updated `web/package.json` to use a local `file:` dependency for `@platform/app-directory-client` so npm resolves the monorepo-local package instead of querying the public registry.
- Confirmed the existing TypeScript/Vite alias setup remains the source-resolution mechanism for local development.
- Updated the root workspace entry to target `apps/scribeswell/web`, which is the actual npm package boundary.

### Deviations from plan
- None.

### Remaining TODOs
- Run `npm install` from the monorepo root (`c:\repos\innodat\agriplatform`) so npm can link the local `file:` dependency correctly.

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
