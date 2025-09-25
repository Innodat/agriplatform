Using the approved plan and layout:

1) Create the React + Vite structure and router:
   - Implement <AppShell> with Topbar + Sidebar (Departments).
   - Implement <FinanceLayout> for Finance routes.
   - Wire routes for /finance/receipt-capturing with tabs: Overview, Today, Admin (role-gated).

2) Extract components from the provided page.tsx:
   - Shared: HeaderBar, RoleSelector, ExportMenu, StatusBadge, MetricsCard, RecentReceiptsTable
   - Feature-local (modules/finance/receipt-capturing):
     ReceiptForm (with Zod), AddReceiptDialog, TodayReceiptsList, AdminFilters, AdminReceiptsTable, OverviewStats

3) Integrate Zod schemas (from the plan) for form validation and data parsing:
   - Use zodResolver (if using RHF) or custom parse on submit.

4) Supabase integration:
   - Replace mock arrays with functions aligned to the live schema (fetch list, fetch today, insert, approve/reject).
   - Keep code MCP-aware: when unsure of a column/enum, query MCP first.

5) Quality and maintainability:
   - Keep Tailwind classes; ensure accessibility (labels, aria-*).
   - Keep TS strict; define props and types explicitly.
   - Prefer small focused diffs; do not rewrite unrelated files.

6) Deliverables:
   - New files created with full code.
   - Updated references in the dashboard entry point.
   - A short README snippet explaining routes, components, and data flow.

Stop and ask for confirmation after scaffolding, before wiring mutations.