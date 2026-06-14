# apps/bible-web

**Status:** Placeholder — Phase 1

Hebrew Bible study platform — the first clean reference app built on the platform.

## Domain
```
Book → Chapter → Verse → Word → Morphology
```

## Features (planned)
- Navigate books and chapters
- Read verses with Hebrew text
- Click a word to see morphological analysis (root, part of speech, tense, etc.)

## Architecture
- React + Vite + ShadCN UI
- Data via `@platform/api-client` → FastAPI → Supabase (`bible` schema)
- Supabase client only for Auth (no direct data CRUD)
- Read-only: all data loaded via one-time import pipeline from JSON source

## Data source
Hebrew text + morphology data imported from JSON → Supabase via import script.

## Phase
Scaffolded in **Phase 1** alongside the FastAPI skeleton.
See `platform/prompts/context/reader-pattern.md` for UI patterns.
