# Context: Scribeswell App
version: 1.0.0

## Purpose
Scribeswell is a Hebrew Bible reader and study app.

## Primary UX goals
- Preserve reading focus.
- Keep Hebrew text highly readable.
- Avoid bulky persistent navigation where possible.
- Support mixed Hebrew RTL content and English/LTR UI labels.

## App boundaries
- UI calls FastAPI through generated api-client.
- No direct Supabase CRUD from frontend.
- Supabase Auth and Realtime may be used only through approved patterns.
