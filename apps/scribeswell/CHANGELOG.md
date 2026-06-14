# Scribeswell — CHANGELOG

---

## 2026-06-14 — Phase 1 restructure: silo architecture

### What changed
- App renamed from `bible-web` → `scribeswell` (silo model adopted for all apps).
- Backend moved from `platform/backend/` → `apps/scribeswell/backend/` (app-owned).
- Zod schema moved from `platform/shared/schemas/zod/bible/` → `apps/scribeswell/web/src/schemas/bible.schema.ts`.
- Bible migration moved from `supabase/migrations/` → `apps/scribeswell/supabase/migrations/`.
- Import tools moved from `tools/py/` → `apps/scribeswell/tools/`.
- `@platform` alias removed from `vite.config.ts` + `tsconfig.app.json`; imports now use `@/schemas/`.
- `platform/builder-cli/templates/backend/` created as the canonical scaffold template.
- `tsc --noEmit` passes with zero errors.

### Deviations
- None from the approved silo plan.

### Remaining TODOs
- Populate `.env` in `apps/scribeswell/backend/` with real Supabase credentials.
- Run `python apps/scribeswell/tools/import_bible.py --source <path/to/hebrew.json>` to populate data.
- Phase 2: generate api-client from FastAPI OpenAPI spec into `apps/scribeswell/web/src/api-client/`.
- Phase 2: add ShadCN UI components.
- Phase 2: search (Strong's number, word), bookmarks (requires auth).

---

## 2026-06-14 — Phase 1: Hebrew Bible Reader (initial build)

### Delivered
- DB migration: `bible` schema (book/chapter/verse/word/morpheme + RLS).
- OSHB morphology parser + full Tanakh importer.
- FastAPI backend: 5 public bible endpoints.
- Vite + React 19 + TypeScript + Tailwind CSS 4 reader UI.
- 3-column layout: BookList | RTL VerseReader | MorphologyPanel.
- Optional Supabase Auth (reader works signed-out).
