# platform/ui-core

**Status:** Placeholder — Phase 3

Base ShadCN UI wrappers and primitive extensions shared across all apps.

## Purpose
- Wrap ShadCN components with platform-specific defaults (theme tokens, variants)
- Provide a single import point: `@platform/ui-core`
- No business logic — pure presentational primitives

## Planned contents
```
src/
  components/
    button.tsx        ← ShadCN Button with platform variants
    card.tsx
    dialog.tsx
    data-table.tsx    ← TanStack Table wrapper
    form/             ← React Hook Form + Zod integration helpers
  index.ts
```

## Phase
Will be populated in **Phase 3** (Builder CLI + UI tiers).
Until then, apps use ShadCN components directly from their local `components/ui/`.
