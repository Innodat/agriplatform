# Prompt Registry
version: 1.0.0

## How to use
1. Always load `base.md`.
2. Find your task below → load the listed task prompt.
3. Load ONLY the listed context files (no extras).
4. Inject only the 1–3 source files directly relevant to the task.

---

## Task Map

| Task | Prompt | Context to load |
|------|--------|-----------------|
| Create a UI page/component | `tasks/create-ui.md` | `context/naming.md`, `context/crud-pattern.md` OR `context/reader-pattern.md` |
| Create an API endpoint | `tasks/create-api.md` | `context/error-payload.md`, `context/naming.md`, `context/rls-notes.md` |
| Create a full feature (UI + API) | `tasks/create-feature.md` | `context/error-payload.md`, `context/naming.md`, relevant pattern |
| Refactor existing code | `tasks/refactor.md` | `context/naming.md` + the files being refactored |
| Fix a bug | `tasks/fix-bug.md` | Only the failing file(s) + error message |
| Generate models / schemas | `tasks/generate-models.md` | `context/rls-notes.md` + live Supabase MCP schema |

---

## Context Snippets (load on demand only)

| File | When to load |
|------|-------------|
| `context/error-payload.md` | Any API endpoint work |
| `context/naming.md` | Any new file/component creation |
| `context/rls-notes.md` | Any DB schema or API auth work |
| `context/crud-pattern.md` | Admin/CRUD UI or API |
| `context/reader-pattern.md` | Bible reader UI or read-only APIs |

---

## Size Budget (enforced by validate-patterns)
- `base.md`: ≤ 50 lines
- Each task prompt: ≤ 40 lines
- Each context snippet: ≤ 30 lines
