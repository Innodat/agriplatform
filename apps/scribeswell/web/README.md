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

## Running locally

### Backend

`main.py` defines the FastAPI application but does not start a server when run
directly. From the repository root, install the Python dependencies and launch
the application with Uvicorn:

```bash
cd apps/scribeswell/backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

The backend loads its configuration from `apps/scribeswell/backend/.env` or
`.env.local`. Once running, the following endpoints are available:

- API: <http://localhost:8000>
- Health check: <http://localhost:8000/health>
- Swagger documentation: <http://localhost:8000/docs>
- ReDoc documentation: <http://localhost:8000/redoc>

### Frontend

In a second terminal, run the frontend from the repository root:

```bash
npm run dev --workspace=apps/scribeswell/web
```

The frontend runs at <http://localhost:5174> and proxies `/api` requests to the
backend at `http://localhost:8000`.

## Phase
Scaffolded in **Phase 1** alongside the FastAPI skeleton.
See `platform/prompts/context/reader-pattern.md` for UI patterns.
