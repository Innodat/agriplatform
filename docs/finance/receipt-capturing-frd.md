# Finance • Receipt Capturing — Functional Requirements Document

Version: 0.2 (Pending approval)
Owner: Finance Module
Scope: Frontend (React+Vite+ShadCN) + Supabase (direct; no custom backend)

## Overview
Employees log spend by creating a Receipt (header: supplier, currency, reimbursable, date, status) and adding one or more Purchase items (line items: expense category/type, amount, optional Other category when "Other" is chosen). Admin moderates status at the receipt level.

## Objectives
- Multi-item receipt capture with clear parent/child editing.
- Receipt moderation (pending/querying → approved/rejected) with default pending.
- Derived description "Category - Item" via deep select joins.
- Supplier captured as string on receipt, indexed for filtering.
- Standard audit columns auto-managed via centralized triggers.

## Entities & Relationships (finance schema) — Mermaid ER
```mermaid
erDiagram
  RECEIPT ||--o{ PURCHASE : has
  PURCHASE }o--|| EXPENSE_TYPE : classified_as
  EXPENSE_TYPE }o--|| EXPENSE_CATEGORY : belongs_to
  PURCHASE }o--|| CURRENCY : in

  RECEIPT {
    int8 id PK
    text supplier  "indexed for filtering"
    receipt_status status "pending|querying|approved|rejected"
    bool is_active
    timestamptz created_timestamp
    text created_user_id
    timestamptz modified_timestamp
    text modified_user_id
  }

  PURCHASE {
    int8 id PK
    int8 receipt_id FK
    int8 expense_type_id FK
    text other_category
    int8 currency_id FK
    uuid user_id
    numeric amount
    bool reimbursable
    timestamptz captured_timestamp
    bool is_active
    timestamptz created_timestamp
    text created_user_id
    timestamptz modified_timestamp
    text modified_user_id
  }

  EXPENSE_TYPE {
    int8 id PK
    int8 expense_category_id FK
    text name
  }

  EXPENSE_CATEGORY {
    int8 id PK
    text name
  }

  CURRENCY {
    int8 id PK
    text name
    text symbol
  }
```

## Key User Flows — Mermaid Sequence
```mermaid
sequenceDiagram
  autonumber
  actor E as Employee
  participant UI as Web UI
  participant SB as Supabase

  E->>UI: Open "Today's Receipts"
  UI->>UI: Enter Receipt header {supplier, currency, reimbursable, date}
  E->>UI: Add 1..N line items {category/type, amount, optional other_category}
  UI->>SB: INSERT finance.receipt (status='pending')
  loop for each line item
    UI->>SB: INSERT finance.purchase { receipt_id, expense_type_id, amount, currency_id (from header), reimbursable (from header), captured_timestamp }
  end
  SB-->>UI: Success
```

## Status Lifecycle — Mermaid State
```mermaid
stateDiagram-v2
  [*] --> pending
  pending --> approved: Admin Approve
  pending --> rejected: Admin Reject
  querying --> approved: Admin Approve
  querying --> rejected: Admin Reject
  approved --> [*]
  rejected --> [*]
```

## UI Architecture — Mermaid Graph
```mermaid
graph TD
  AppShell[AppShell: Topbar+Sidebar]
  FinanceLayout[FinanceLayout]
  Tabs[Tabs: Overview </br> Today </br> Admin]
  Overview[OverviewPage]
  Today[TodayPage]
  Admin[AdminPage]
  Editor[AddReceiptDialog: ReceiptHeaderForm + LineItemsEditor]
  Items[ReceiptItemsTable]

  AppShell --> FinanceLayout --> Tabs
  Tabs --> Overview
  Tabs --> Today --> Editor
  Tabs --> Admin --> Items
```

## Data Contracts (Zod)
- Tables (finance.*): ReceiptTable (adds supplier + status), PurchaseTable, ExpenseType, ExpenseCategory, Currency.
- Deep row: PurchaseDeep = PurchaseTable + expense_type(expense_category) + currency.
- UI models: PurchaseSchema with derived description "Category - Item"; ReceiptWithAggregates includes supplier, totals, items.
- Role: employee display name from auth user metadata (client only).

## Queries
- Deep select example (PostgREST):
  - from finance.purchase select: id, amount, status, captured_timestamp, expense_type(id,name,expense_category(id,name)), currency(id,name,symbol)
  - Aggregate by receipt_id for lists; JOIN via receipt_id; supplier filter via ilike on finance.receipt.supplier (prefix when possible).
- Supplier suggestions: SELECT DISTINCT supplier FROM finance.receipt WHERE supplier IS NOT NULL ORDER BY supplier LIMIT 20

## Audit Policy (Centralized Functions & Triggers)
- actor_name() returns:
  coalesce(app.actor_override, jwt.user_metadata.name, jwt.email, current_user, 'system')
- set_audit_fields() BEFORE INSERT/UPDATE:
  - INSERT: created_user_id := coalesce(provided, actor_name()); modified_user_id := created_user_id; created_timestamp := coalesce(provided, now()); modified_timestamp := now()
  - UPDATE: modified_user_id := actor_name(); modified_timestamp := now()
- Trigger convention:
  create trigger trg_<schema>_<table>_audit before insert or update on <schema>.<table> execute function set_audit_fields()
- Bootstrap migration attaches triggers to all existing tables that have all 4 audit columns.

## Validation Rules
- Receipt must contain ≥ 1 line item.
- Amount > 0; if type == "Other", other_category required.
- Supplier is required; case-insensitive filtering supported.

## Admin Rules
- Approve/Reject per receipt; filter by supplier and status.

## Non-Goals
- No supplier table at this stage.
- No purchase.description column; description is UI-derived.

## Future Work
- Optional: separate profile table for richer display names; current display uses user metadata.
