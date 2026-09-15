# Task: Refactor
version: 1.1.0

## Goal
Improve existing code without changing behaviour: reduce duplication, align to patterns, improve types.

## Inputs
- File(s) to refactor
- Reason: duplication | pattern misalignment | type safety | performance

## Context to load
See `registry.md` → load `context/naming.md` + the files being refactored (inject directly).

## Steps
1. Identify the behavior and public contracts that must remain unchanged.
2. Assess existing coverage; add characterization tests for relied-upon gaps.
3. Confirm tests pass before changing code and identify known defects separately.
4. Refactor in bounded steps, running the narrow relevant suite after each step.
5. Preserve public contracts unless an approved requirement explicitly changes them.
6. Run affected acceptance/contract suites and static checks; record evidence.
7. Complete prompt/scaffold impact review for any newly proven pattern.

## Output contract
- Modified file(s) only
- No behaviour change
- TypeScript clean

## Do-not
- Do not refactor files outside the stated scope
- Do not introduce new dependencies without justification
- Do not change public APIs without explicit approval
- Do not approve changed behavior by editing expectations without a requirement decision
