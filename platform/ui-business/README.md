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

## App launcher

`AppLauncher` is implemented as a build-time React component, shared by PtS and
Scribeswell. Import it from `@platform/ui-business`; its namespaced CSS is bundled
with the component and does not require Tailwind. Supply directory-provided `apps`
and optional `currentAppId`, `isLoading`, and `label`. Links open a new tab.

The menu supports Enter/Space, Arrow Up/Down, Home/End, Escape, Tab and outside
pointer dismissal. `AppLauncherItem` is a menuitem link and uses the catalogue's
`book-open`/`library` icon or a generic grid fallback. Consumer apps must not override
its internal layout with broad menu/link selectors. Browser acceptance coverage
lives in the PtS launcher suite and Scribeswell reader suite.

Set `iconOnly` to render only the grid icon in the trigger (Scribeswell). The
default is `false`, retaining the Apps text and chevron (PtS). The accessible
label, hover title, keyboard interaction and touch target are preserved.
