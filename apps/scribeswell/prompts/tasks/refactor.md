# Task: Refactor
version: 1.0.0
source: platform/prompts/tasks/refactor.md@1.0.0
app_overrides: false

## Goal
Improve existing code without changing behaviour: reduce duplication, align to patterns, improve types.

## Inputs
- File(s) to refactor
- Reason: duplication | pattern misalignment | type safety | performance

## Context to load
See `registry.md` → load `context/naming.md` + the files being refactored (inject directly).

## Steps
1. Identify the specific anti-pattern (duplication / direct DB access / missing types / etc.).
2. Check if a platform pattern already exists that replaces it.
3. Make the smallest change that fixes the issue — do not over-engineer.
4. Preserve public API (exports, prop types) unless explicitly changing them.
5. Verify TypeScript compiles (`tsc --noEmit`) after changes.
6. Note any follow-on refactors needed but do NOT do them in this task.

## Output contract
- Modified file(s) only
- No behaviour change
- TypeScript clean

## Do-not
- Do not refactor files outside the stated scope
- Do not introduce new dependencies without justification
- Do not change public APIs without explicit approval
