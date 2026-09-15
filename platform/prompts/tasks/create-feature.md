# Task: Create Full Feature (UI + API end-to-end)
version: 1.1.0

## Goal
Scaffold a complete feature: DB → FastAPI → generated client → React UI.

## Inputs
- Feature name (kebab-case, e.g. `verse-reader`, `expense-report`)
- Target app: `apps/<app-name>/`
- Entities involved (from Supabase schema)

## Context to load
See `registry.md` → load `context/error-payload.md` + `context/naming.md` + relevant pattern.
Inject: approved acceptance criteria, generated schema/contracts, and one reference feature folder.

## Steps
1. Link the feature specification, ADRs, and implementation-plan item.
2. Refine concrete acceptance examples and select the lowest stable test boundary.
3. Add the first failing acceptance test and confirm the expected failure.
4. Query the live schema and refresh generated contracts where required.
5. Implement vertical slices through focused red-green-refactor loops.
6. Regenerate/validate the OpenAPI client and implement UI behavior from the same contract.
7. Run focused, affected acceptance/contract, and required tenant/security suites.
8. Record verification plus scaffold, shared-UI, prompt, docs, and ADR impact reviews.

## Output contract
- `platform/backend/routers/<feature>.py`
- `platform/backend/services/<feature>.py`
- `apps/<app>/src/pages/<feature>/` (page + components)
- `apps/<app>/src/hooks/use-<feature>.ts`

## Do-not
- Do not skip the MCP schema query
- Do not hand-write models that should be generated
- Do not wire complex mutations before scaffold review
- Do not implement user-visible behavior before its acceptance example is agreed
- Do not mark complete without traceable passing acceptance evidence
