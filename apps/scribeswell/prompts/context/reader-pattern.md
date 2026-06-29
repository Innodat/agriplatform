# Context: Reader Pattern
version: 1.0.0

## Domain model

Book → Chapter → Verse → Word → Morphology

## Data flow

Page → Hook → generated api-client → FastAPI → Supabase scribeswell schema

## Navigation
- Navigation state lives in URL params: `?book=GEN&chapter=1`.
- Prefer compact book/chapter selector in header or breadcrumb area.
- Avoid bulky persistent sidebars unless the screen size/design clearly benefits.

## Hebrew / RTL rules
- Hebrew Bible text is RTL.
- Preserve Hebrew readability as the primary UX goal.
- Mixed Hebrew/English UI must handle direction, spacing, and focus order deliberately.
- Interactive selectors must remain keyboard accessible.