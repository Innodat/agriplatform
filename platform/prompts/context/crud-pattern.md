# Context: CRUD Pattern
version: 1.0.0

## UI structure (admin/CRUD pages)
```
<CrudPage entity="receipts">        ← ui-business component (future)
  <StatsGrid />                     ← summary cards
  <FilterBar />                     ← search + filters
  <DataTable columns={...} />       ← sortable, paginated table
  <CrudDialog mode="create|edit" /> ← form in dialog
</CrudPage>
```

## File layout (per feature)
```
apps/<app>/src/
  pages/<feature>/
    index.tsx          ← page entry, wires hooks → components
    components/
      <feature>-table.tsx
      <feature>-form.tsx
      <feature>-dialog.tsx
  hooks/
    use-<feature>.ts   ← data fetching (calls api-client)
    use-<feature>-mutations.ts
```

## Data flow
```
Page → Hook → api-client (generated) → FastAPI → Supabase
```

## Key rules
- Page components are thin: no business logic, no direct API calls.
- Hooks own all data fetching + mutation state.
- Forms use React Hook Form + Zod resolver.
- Tables use TanStack Table (or ShadCN DataTable wrapper).
