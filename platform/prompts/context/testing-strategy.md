# Context: ATDD and TDD Strategy
version: 1.0.0

## Required loop

```text
Requirement → failing acceptance scenario → focused TDD loop → affected suite → evidence
```

- Agree concrete examples, permissions, failure behavior, and observable outcomes first.
- Test through the lowest stable public boundary that proves the behavior.
- Prefer domain/API/component/contract tests over slow browser tests when equivalent.
- For a defect, reproduce it with a failing test before fixing it.
- Before risky refactoring, add characterization tests for relied-upon current behavior.
- Use deterministic clocks, IDs, calendars, fixtures, provider fakes, and retries.
- Run the narrow failing test first, then affected suites, then broad suites at gates.
- Never weaken an assertion or rewrite an expected result without explaining a changed requirement.

## Required evidence

- Link requirement or acceptance criterion to test/scenario IDs.
- Record the initial expected failure when practical.
- Record commands and final results in completion notes.
- Treat flaky, non-isolated, or ambiguous tests as defects.
- Include tenant/role denial paths and idempotent retry paths where applicable.

See platform ADR-0009 for the complete test portfolio and governance.
