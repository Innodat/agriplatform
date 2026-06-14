# Scribeswell — Supabase Migrations

Migrations in this directory apply to the **shared Supabase project** (same instance as the rest of the monorepo).

They are kept here (silo'd) so that if Scribeswell is extracted to its own repo, the migrations travel with it.

## Current migrations

| File | Description |
|------|-------------|
| `20260614000000_create_bible_schema.sql` | `bible` schema: book, chapter, verse, word, morpheme tables + `*_read` views + RLS |

## Applying migrations

```bash
# Apply to local Supabase
supabase db push --local

# Apply to remote (staging/prod)
supabase db push --db-url <connection-string>
```

## Note on DB isolation

Currently Scribeswell shares the Supabase project with other apps. True isolation (separate Supabase project) is a future step when the app is extracted to its own repo.
