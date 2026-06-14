# Scribeswell — Technical Documentation

**App:** `apps/scribeswell`  
**Architecture:** Silo (self-contained; extractable to own repo)  
**Status:** Phase 1 complete

---

## Structure

```
apps/scribeswell/
├── backend/            # FastAPI — bible API (port 8000)
│   ├── main.py         # App entry point
│   ├── config.py       # pydantic-settings (reads backend/.env)
│   ├── errors.py       # Consistent error shape {error, code?, details?}
│   ├── auth/           # Optional JWT (Supabase)
│   ├── routers/        # bible.py — 5 public GET endpoints
│   ├── services/       # bible_service.py — Supabase queries
│   ├── schemas/        # bible_schemas.py — Pydantic response models
│   └── models/generated/ # bible_models.py — GENERATED row models
├── web/                # Vite + React 19 + TypeScript + Tailwind (port 5174)
│   └── src/
│       ├── schemas/    # bible.schema.ts — Zod schemas (app-owned)
│       ├── lib/        # api-client.ts (fetch+Zod), supabase.ts (Auth only)
│       ├── hooks/      # useBible.ts
│       ├── components/ # BookList, ChapterNav, VerseReader, MorphologyPanel
│       └── pages/      # ReaderPage (3-column layout)
├── supabase/
│   └── migrations/     # 20260614000000_create_bible_schema.sql
├── tools/
│   ├── import_bible.py # Full Tanakh importer (OSHB hebrew.json → Supabase)
│   └── oshb_morph.py   # OSHB morphology code parser
├── docs/               # This file
└── CHANGELOG.md
```

---

## Database Schema

**Schema:** `bible` (Supabase)  
**RLS:** Public SELECT for `anon` + `authenticated` (no `org_id` — global reference data).

```
bible.book        id, osis_id, name_en, name_he, testament, book_order
bible.chapter     id, book_id→book, chapter_num
bible.verse       id, chapter_id→chapter, verse_num, book_id(denorm), chapter_num(denorm)
bible.word        id, verse_id→verse, position, surface_he, display_he, lemma_strong, morph_code
bible.morpheme    id, word_id→word, segment_index, language, part_of_speech, pos_code,
                  gender, number, state, verb_stem, verb_aspect, person
```

Read views: `bible.*_read` (filter nothing — pass-through for consistency).

---

## API Endpoints (all public)

```
GET /health
GET /api/bible/books
GET /api/bible/books/{osis_id}
GET /api/bible/books/{osis_id}/chapters/{n}
GET /api/bible/books/{osis_id}/chapters/{n}/verses
GET /api/bible/words/{word_id}/morphology
```

OpenAPI docs: `http://localhost:8000/docs`

---

## Running locally

**Backend:**
```bash
cd apps/scribeswell/backend
cp .env.example .env          # fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Import data (one-time):**
```bash
cd apps/scribeswell
python tools/import_bible.py --source <path/to/hebrew.json>
# Options: --dry-run, --book Gen
```

**Web:**
```bash
cd apps/scribeswell/web
cp .env.example .env.local    # fill in VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY
npm install
npm run dev                   # http://localhost:5174
```

---

## OSHB Morphology Codes

Format: `<H|A><POS>[features][/<POS>[features]...]`

- `H` = Hebrew, `A` = Aramaic
- POS: `N`=noun, `V`=verb, `C`=conjunction, `T`=particle, `R`=preposition, `A`=adjective, `P`=pronoun, `D`=adverb
- Example: `HC/Td/Ncbsa` → Conjunction / Article / Noun-common-both-singular-absolute

Parser: `apps/scribeswell/tools/oshb_morph.py`

---

## Silo note

This app is designed to be extractable into its own repository. It has no runtime imports from `platform/*`. The backend scaffold was generated from `platform/builder-cli/templates/backend/` and is now fully owned by this app.
