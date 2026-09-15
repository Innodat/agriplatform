# Task: Create UI Page or Component
version: 1.1.0

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
1. Define accessible observable behavior and add a failing component/acceptance test.
2. Determine tier and check for an existing shared component to compose or extend.
3. Implement the smallest behavior through red-green-refactor using shadcn foundations.
4. Test keyboard, focus, labels, errors, loading, empty, and permitted states as applicable.
5. Promote only proven domain-neutral components, with catalogue and regression coverage.
6. Export strict types; use the generated API contract and no `any`.
7. Run focused component tests before affected browser journeys.

## Output contract
- File: `kebab-case.tsx`
- Exports: named component (PascalCase) + prop types
- Accessibility: aria labels, keyboard nav where interactive

## Do-not
- Do not hardcode per-page data-fetching logic in the component
- Do not import `@supabase/supabase-js` directly (use api-client or hooks)
- Do not create one-off layout structures — reuse or propose abstraction
