# ADR-0009: ATDD and TDD Development Loop

**Status:** Accepted  
**Date:** 2026-09-03  
**Scope:** Platform, shared services, builder scaffolding, and applications

## Context

AI-assisted implementation and refactoring can change more code, more quickly, than
manual review can reliably validate. Product specifications and ADRs preserve intent
but do not by themselves prove that running software still satisfies it. Large,
slow test suites also provide poor feedback and consume unnecessary agent time and
tokens when failures are ambiguous.

The platform needs executable acceptance boundaries, fast implementation feedback,
and safe characterization of existing behavior before refactoring.

## Decision

Adopt Acceptance Test-Driven Development (ATDD) as the outer delivery loop and
Test-Driven Development (TDD) as the inner implementation loop.

### Outer loop: ATDD

Before implementation of a user-visible behavior or cross-service contract:

1. Product, engineering, and testing perspectives refine examples and acceptance
   criteria from the approved feature specification.
2. Express those examples as readable, automatable acceptance scenarios.
3. Confirm scope, permissions, privacy, failure behavior, and observable outcomes.
4. Run the scenario and observe the expected failure for the missing behavior.
5. Implement through the inner TDD loop until the scenario passes.
6. Keep the scenario as regression evidence and link it to its requirement.

Acceptance tests exercise behavior through the most stable practical public
boundary. They do not depend on private implementation details. Not every acceptance
criterion must be a browser test: API, contract, worker, database-security, and
component-level acceptance tests are preferred when they provide the same confidence
more quickly and deterministically.

### Inner loop: TDD

For domain rules, calculations, state transitions, authorization decisions,
provider adapters, and defect corrections:

1. Write one small failing test for the next behavior or reproduced defect.
2. Make the smallest implementation change that passes it.
3. Refactor while the focused test remains green.
4. Run the relevant acceptance/contract suite before completing the slice.

Tests are written at the lowest stable boundary that proves the behavior. Coverage
percentage is supporting telemetry, not the objective; meaningful behavior and risk
coverage are the objective.

### AI refactoring rule

Before changing behavior-sensitive code without adequate tests, add focused
characterization tests that capture currently relied-upon behavior. Distinguish
intentional legacy behavior from known defects. Refactor in bounded steps and run
the narrowest relevant suite after each step, followed by affected acceptance and
contract suites. Never update an expected result merely to make an unexplained
failure pass.

### Evidence and traceability

Every substantial change links:

```text
Feature requirement → acceptance scenario → focused tests → implementation → verification
```

Completion evidence records the tests run and their results. A feature is not done
when code exists; it is done when its accepted behavior and relevant safeguards pass.

## Test portfolio

- Pure domain/unit tests for calculations and state machines
- Component tests for accessible UI behavior
- API integration tests through FastAPI with real routing and dependencies
- OpenAPI and consumer/provider contract tests across service boundaries
- PostgreSQL migration, constraint, RLS, and cross-tenant negative tests
- Worker/outbox/idempotency tests using deterministic clocks and controlled retries
- Storage-provider adapter tests and emulated integration tests
- A small browser end-to-end suite for critical role journeys
- Characterization tests before risky changes to insufficiently tested code

## Token- and feedback-efficiency rules

- Test commands are layered and independently runnable by feature and test ID.
- Failure output identifies scenario, expected behavior, actual behavior, and useful
  correlation context without dumping unrelated logs or secrets.
- Agents run the smallest relevant failing test first, then the affected suite, and
  only then broader regression suites at integration/release gates.
- Deterministic fixtures, clocks, IDs, calendars, and provider fakes minimize flaky
  reruns and repeated diagnosis.
- CI publishes concise test summaries and preserves full logs as artifacts.
- Generated apps include the same commands and test structure.

These practices are expected to reduce repeated context gathering and debugging,
but token reduction is an outcome to measure during the pilot, not a guaranteed
property of adding more tests.

## Alternatives considered

- Add tests after implementation
- Use browser end-to-end tests for all acceptance criteria
- Require a coverage percentage without behavior traceability
- Rely on AI review and static analysis without executable acceptance tests
- Freeze existing behavior before every refactor without identifying known defects

## Consequences

- Acceptance criteria must become concrete examples before feature implementation.
- Product and engineering decisions move earlier in the delivery process.
- Builder templates must include test structure, fixtures, commands, examples, and CI.
- BMAD plans/stories and Build specifications must identify acceptance scenarios
  and the intended test boundary before listing implementation operations.
- Refactors may begin with characterization work rather than production-code edits.
- The suite must be curated for speed and signal; redundant or flaky tests are
  treated as defects.

## Revisit when

Measured lead time, escaped defects, flaky-test rate, or maintenance cost shows that
the selected test boundaries or mandatory workflow need adjustment. The outer ATDD
and inner TDD principles remain unless a superseding ADR provides equivalent
executable confidence.
