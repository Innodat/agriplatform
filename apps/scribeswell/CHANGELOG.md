# Scribeswell — CHANGELOG

---

## 2026-06-29 — Reader UI polish: RTL fixes, verse layout, selector position

### Delivered
- **`VerseReader.tsx`** — four fixes:
  - Removed leftover duplicate `<p>` block from interrupted edit session.
  - Removed debug `console.log`.
  - Spacing tightened: `space-y-4` → `space-y-1`; `text-2xl leading-loose` → `text-xl` with `lineHeight: 1.9`.
  - Verse number moved to visual left: row flipped to `flex-row-reverse items-baseline`. DOM order is `[<p> Hebrew text][<span> verse num]`; `flex-row-reverse` puts the number on the left visually without fighting RTL text flow.
- **`book-chapter-selector.tsx`** — three fixes:
  - Chapter grid container now has `dir="rtl"` — CSS `auto-fill` grid now flows right-to-left so א appears top-right.
  - `normaliseTestament()` utility added — defensively maps any API testament string variant (`"nevi'im"`, `"neviim"`, `"Nevi_Im"`, etc.) to a known key, fixing the empty book list.
  - `ChapterPanel` loading guard tightened: spinner only shows when `loading && !bookData` — avoids a flash of "Loading…" on first open when `hoveredOsisId` is null.
  - Dropdown anchors from `right-0` (opens leftward from trigger) — correct for RTL-primary layout.
- **`ReaderPage.tsx`** — selector header row changed to `justify-end` so the trigger sits on the right/RTL-start of the page.

### Deviations from plan
- None.

### Remaining TODOs
- Delete `BookList.tsx` and `ChapterNav.tsx` (dead code).
- Remove unused path routes from `App.tsx`.

## 2026-06-29 — Compact book/chapter selector — replace sidebar navigation

### Delivered
- **`src/lib/hebrew-ordinal.ts`** (new) — pure `toHebrewOrdinal(n)` utility; full gematria mapping 1–150 using greedy algorithm; special-cases 15→טו and 16→טז to avoid divine names. No external dependencies.
- **`src/components/bible/book-chapter-selector.tsx`** (new) — `BookChapterSelector` compact dropdown component replacing the old left-sidebar `BookList + ChapterNav` pattern:
  - Trigger button shows active book name + Hebrew chapter gematria letter + `ChevronDown`.
  - Dropdown opens as a two-panel overlay: left = book list (Torah / Nevi'im / Ketuvim), right = chapter grid for hovered/active book.
  - Hover (desktop) or click (touch) on a book row fetches and shows that book's chapters via `useBook()`.
  - Chapter buttons labeled with Hebrew gematria (א, ב, כב, קנ…) using `toHebrewOrdinal`.
  - Active book highlighted amber-100; active chapter highlighted amber-500/white.
  - Escape key and click-outside close the dropdown; focus returns to trigger on close.
  - `aria-haspopup`, `aria-expanded`, `aria-current`, `aria-label`, `dir="rtl" lang="he"` on all Hebrew text.
  - No new npm dependencies — Tailwind + Lucide (`ChevronDown`) only.
- **`src/pages/ReaderPage.tsx`** (refactored):
  - Removed left `<aside w-56>` sidebar (BookList + ChapterNav) entirely.
  - Removed decorative breadcrumb.
  - Added `useSearchParams` (react-router-dom) — navigation state now lives in URL: `?book=Gen&chapter=1`.
  - Dropped unused `useBook` call; `BookChapterSelector` manages its own internal hover-book fetch.
  - `VerseReader` and `MorphologyPanel` are completely unchanged.
  - All hooks (`useBooks`, `useVerses`, `useWordMorphology`), api-client, and Zod schemas untouched.
- `tsc --noEmit` exits 0 (zero TypeScript errors).

### Deviations from plan
- `BookList.tsx` and `ChapterNav.tsx` left in place as dead code (not deleted) to keep this PR focused. Flagged for removal in a follow-up.
- `App.tsx` route params `/:osisId` and `/:osisId/:chapter` left in place as dead routes; query params (`?book=&chapter=`) are the live navigation mechanism per spec.

### Remaining TODOs
- Delete `src/components/bible/BookList.tsx` and `src/components/bible/ChapterNav.tsx` in a follow-up cleanup PR.
- Remove unused path routes from `App.tsx` (`/:osisId`, `/:osisId/:chapter`) in the same cleanup.
- Consider adding a platform-level prompt note about `toHebrewOrdinal` being available in `scribeswell/web/src/lib/`.

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
