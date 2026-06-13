# Task: Create UI Page or Component
version: 1.0.0

## Goal
Scaffold a new React page or component following platform UI patterns.

## Inputs
- Component/page name (PascalCase)
- Target app: `apps/<app-name>/`
- UI tier: `ui-core` | `ui-business` | `ui-app`
- Pattern: CRUD | Reader | Form | Other

## Context to load
See `registry.md` → load `context/naming.md` + relevant pattern context.
Inject: the closest existing similar component as reference (1 file max).

## Steps
1. Determine tier: reusable platform component → `platform/ui-business/`; app-specific → `apps/<app>/src/components/`
2. Check `platform/ui-business/` for an existing component to extend (e.g. `CrudPage`, `ReaderLayout`).
3. If pattern exists → compose it; do NOT rewrite from scratch.
4. If pattern is missing → implement, then propose promoting to `ui-business/` if it will repeat.
5. Use ShadCN components from `platform/ui-core/` as base. No raw HTML divs for layout.
6. No inline styles. Tailwind classes only.
7. Export types; no `any`.

## Output contract
- File: `kebab-case.tsx`
- Exports: named component (PascalCase) + prop types
- Accessibility: aria labels, keyboard nav where interactive

## Do-not
- Do not hardcode per-page data-fetching logic in the component
- Do not import `@supabase/supabase-js` directly (use api-client or hooks)
- Do not create one-off layout structures — reuse or propose abstraction
