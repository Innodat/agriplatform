# Platform Prompts — CHANGELOG

---

## 2026-06-14 — Silo model adoption + builder-cli template

### What was delivered
- **Architecture decision:** Silo model adopted for all apps in `apps/*`. Each app owns its own `backend/`, `web/`, `supabase/migrations/`, `tools/`, `docs/`, `CHANGELOG.md`.
- **apps/bible-web → apps/scribeswell:** App renamed and restructured as canonical silo reference.
- **platform/backend deleted:** All bible backend code vendored into `apps/scribeswell/backend/`.
- **platform/builder-cli/templates/backend/ created:** App-agnostic FastAPI scaffold template (`main.py`, `config.py`, `errors.py`, `auth/jwt_optional.py`, `requirements.txt`, `.env.example`).
- **Zod schema moved:** `platform/shared/schemas/zod/bible/` → `apps/scribeswell/web/src/schemas/bible.schema.ts`.
- **Migration moved:** `supabase/migrations/20260614000000_create_bible_schema.sql` → `apps/scribeswell/supabase/migrations/`.
- **Tools moved:** `tools/py/import_bible.py` + `oshb_morph.py` → `apps/scribeswell/tools/`.
- **`.clinerules` rewritten:** Silo rules, updated backend planning prompt (per-app backend), updated acting prompt (app CHANGELOG + platform CHANGELOG).
- **`docs/tech-spec.md` updated to v1.4:** §2.1 monorepo structure, Important Paths, Document History.
- **`tsc --noEmit` passes** with zero errors in `apps/scribeswell/web/`.

### Deviations
- None from the approved silo plan.

### Remaining TODOs
- Populate `apps/scribeswell/backend/.env` with real Supabase credentials.
- Run `python apps/scribeswell/tools/import_bible.py --source <path/to/hebrew.json>` to populate data.
- Phase 2: generate api-client from FastAPI OpenAPI spec into `apps/scribeswell/web/src/api-client/`.
- Phase 2: add ShadCN UI components to scribeswell web.
- Phase 2: search (Strong's number, word), bookmarks (requires auth).


---

## 2026-06-14 — Phase 1: Hebrew Bible Reader (apps/bible-web)

### Delivered

**Database (Supabase)**
- Migration `20260614000000_create_bible_schema.sql`: new `bible` schema with tables `book`, `chapter`, `verse`, `word`, `morpheme` + `*_read` views.
- RLS: public SELECT for `anon` + `authenticated` roles (no `org_id` — global reference data, documented deviation from multi-tenant rule).

**Import pipeline**
- `tools/py/oshb_morph.py`: full OSHB morphology code parser (language, POS, gender, number, state, verb stem/aspect, person).
- `tools/py/import_bible.py`: full Tanakh importer from OSHB `hebrew.json` → Supabase. Supports `--dry-run` and `--book <OSIS>` flags. Batch upserts (500 rows/batch).

**Backend (`platform/backend/`)**
- `requirements.txt`, `config.py` (pydantic-settings), `errors.py` (consistent `{error, code?, details?}` shape).
- `auth/jwt_optional.py`: `get_optional_user` / `get_required_user` dependencies; `OptionalUser` / `RequiredUser` type aliases.
- `main.py`: FastAPI app, CORS, global error handlers, `/health`, router registry.
- `routers/bible.py`: 5 public GET endpoints (books, book+chapters, chapter+verses, verses+words, word morphology).
- `services/bible_service.py`: service-role Supabase queries, grouped word fetch per chapter.
- `schemas/bible_schemas.py`: Pydantic response schemas.
- `models/generated/bible_models.py`: generated Pydantic row models.

**Shared schemas**
- `platform/shared/schemas/zod/bible/bible.schema.ts`: Zod schemas + inferred TypeScript types for all bible entities and API responses.

**Frontend (`apps/bible-web/`)**
- Vite + React 19 + TypeScript + Tailwind CSS 4 app scaffolded on port 5174.
- Vite proxy: `/api` → `http://localhost:8000` (dev).
- `src/lib/api-client.ts`: typed fetch wrapper over FastAPI; Zod-validates all responses.
- `src/lib/supabase.ts`: Supabase client for Auth only (no data CRUD).
- `src/context/AuthContext.tsx`: optional Auth — reader works signed-out; sign-in for future settings.
- `src/hooks/useBible.ts`: `useBooks`, `useBook`, `useVerses`, `useWordMorphology` hooks.
- `src/components/layout/AppShell.tsx` + `Topbar.tsx`: AppShell with brand + optional Sign In.
- `src/components/auth/SignInDialog.tsx`: email/password modal.
- `src/components/bible/BookList.tsx`: testament-grouped book navigation.
- `src/components/bible/ChapterNav.tsx`: chapter number grid.
- `src/components/bible/VerseReader.tsx`: RTL Hebrew verse display with clickable words.
- `src/components/bible/MorphologyPanel.tsx`: decoded morpheme breakdown panel.
- `src/pages/ReaderPage.tsx`: 3-column reader layout (BookList | VerseReader | MorphologyPanel).
- `src/App.tsx`: BrowserRouter + AuthProvider + AppShell + routes.
- TypeScript: `tsc --noEmit` passes with zero errors.

### Deviations from plan
- `apps/bible-web` used instead of `apps/scribeswell` (confirmed in planning — this is the Hebrew Bible reader app).
- `@platform/api-client` (generated OpenAPI client, Phase 2) not yet generated — `apps/bible-web` uses a hand-written `src/lib/api-client.ts` that wraps fetch + Zod validation. This is the correct Phase 1 approach; generated client comes in Phase 2 once OpenAPI spec is stable.
- Bible RLS uses public `anon` + `authenticated` SELECT (no `org_id`) — documented deviation, approved in planning.

### Remaining TODOs
- Run `python tools/py/import_bible.py --source <path/to/hebrew.json>` to populate data.
- Set `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_JWT_SECRET` in `.env` for backend.
- Set `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` in `apps/bible-web/.env.local` for frontend Auth.
- Phase 2: generate `@platform/api-client` from FastAPI OpenAPI spec; replace hand-written client.
- Phase 2: add ShadCN UI components (currently using plain Tailwind).
- Phase 2: add search (by Strong's number, by word), bookmarks (requires auth).

---

## Earlier entries

_(No prior entries — this is the first CHANGELOG entry for the platform prompt system.)_
