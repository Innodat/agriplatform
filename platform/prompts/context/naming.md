# Context: Naming Conventions
version: 1.0.0

## Files & Folders
- All files: `kebab-case.ts` / `kebab-case.tsx` / `kebab-case.py`
- Folders: `kebab-case/`

## TypeScript
- Components: `PascalCase` (e.g. `VerseReader`, `CrudPage`)
- Services: `PascalCase` suffix `Service` (e.g. `VerseService`) — or named exports
- Hooks: `camelCase` prefix `use` (e.g. `useVerses`, `useReceiptMutations`)
- Types/Interfaces: `PascalCase` (e.g. `VerseRow`, `ReceiptFilters`)
- Zod schemas: `camelCase` suffix `Schema` (e.g. `verseRowSchema`)
- Constants: `SCREAMING_SNAKE_CASE`

## Python (FastAPI)
- Modules/files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Pydantic models: `PascalCase` (e.g. `VerseRow`, `VerseInsert`)

## Git commits (conventional)
`feat:` `fix:` `refactor:` `docs:` `chore:` `test:`
