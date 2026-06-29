# Task: Fix Bug
version: 1.0.0
source: platform/prompts/tasks/fix-bug.md@1.0.0
app_overrides: false

## Goal
Fix a specific, reproducible bug with minimal blast radius.

## Inputs
- Error message or description
- File(s) where the bug occurs
- Steps to reproduce (if known)

## Context to load
Inject ONLY: the failing file(s) + error message. Nothing else unless the bug spans multiple files.

## Steps
1. Read the error carefully — identify root cause before touching code.
2. Fix only the root cause. Do not refactor surrounding code.
3. If the fix requires a pattern change, note it separately and fix only the immediate bug now.
4. Verify TypeScript compiles after fix.
5. Note if a test should be added (do not write the test in this task unless trivial).

## Output contract
- Minimal diff — only lines that fix the bug
- TypeScript clean
- One-line comment explaining the fix if non-obvious

## Do-not
- Do not fix multiple bugs in one task
- Do not refactor while fixing
- Do not change unrelated files
