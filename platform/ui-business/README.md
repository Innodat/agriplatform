# platform/ui-business

**Status:** Placeholder — Phase 3

Reusable domain-level components shared across apps. Built on `platform/ui-core`.

## Purpose
- Provide high-level patterns: `CrudPage`, `ReaderLayout`, `StatsGrid`, `FilterBar`
- Encode the implicit UI DSL as explicit, composable components
- Reduce per-app custom layout code

## Planned contents
```
src/
  components/
    crud-page.tsx         ← generic admin/CRUD page shell
    reader-layout.tsx     ← book/chapter/verse reader shell
    stats-grid.tsx        ← summary card grid
    filter-bar.tsx        ← search + filter row
    app-shell.tsx         ← Topbar + Sidebar layout
  index.ts
```

## Phase
Will be seeded in **Phase 3** by extracting patterns from:
- `apps/receipts-web` → CrudPage, StatsGrid, FilterBar
- `apps/bible-web` → ReaderLayout
