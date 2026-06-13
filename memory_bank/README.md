# memory_bank — ARCHIVED

The memory_bank approach (always-on large context) has been replaced by the minimal prompt system.

## New system
See `platform/prompts/` for the replacement:
- `base.md` — always-loaded hard rules (minimal)
- `registry.md` — task → prompt → context routing
- `tasks/` — task-specific prompts
- `context/` — on-demand context snippets

## Archive
The original memory_bank files are preserved in `_archived/` for historical reference.
They are **not** auto-loaded by any AI workflow.

## Why
- Reduced token cost
- Higher relevance per task (only load what's needed)
- Explicit context injection instead of always-on dumps
