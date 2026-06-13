# Prompt System CHANGELOG

## Rules
- Bump version in the affected file header when rules change.
- Add an entry here with: date, file changed, what changed, why.
- Do NOT add entries for typo fixes — only rule/structure changes.
- AI must not silently expand prompts — propose changes via this log.

---

## v1.0.0 — 2026-06-13

**Initial prompt system scaffold.**

- Created `base.md`: hard rules, stack, repo layout, context loading policy.
- Created `registry.md`: task→prompt→context routing table + size budget.
- Created `tasks/`: create-ui, create-api, create-feature, refactor, fix-bug, generate-models.
- Created `context/`: error-payload, naming, rls-notes, crud-pattern, reader-pattern.
- **Replaces:** `memory_bank/` (archived to `memory_bank/_archived/`).
- **Motivation:** reduce token cost; eliminate always-on large context; make context injection explicit and task-scoped.
