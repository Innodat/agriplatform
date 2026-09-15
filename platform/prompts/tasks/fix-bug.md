# Task: Fix Bug
version: 1.1.0

## Goal
Fix a specific, reproducible bug with minimal blast radius.

## Inputs
- Error message or description
- File(s) where the bug occurs
- Steps to reproduce (if known)

## Context to load
Inject ONLY: the failing file(s) + error message. Nothing else unless the bug spans multiple files.

## Steps
1. Reproduce the defect with the smallest stable failing regression test.
2. Confirm the failure represents the reported behavior, then identify the root cause.
3. Make the smallest production change that passes the new test.
4. Refactor only when needed while the focused test remains green.
5. Run affected tests and static checks and record the commands/results.
6. Perform prompt/scaffold impact review if the defect exposes a reusable safeguard.

## Output contract
- Minimal diff — only lines that fix the bug
- TypeScript clean
- A durable regression test plus the minimal production diff

## Do-not
- Do not fix multiple unrelated bugs in one task
- Do not refactor while fixing
- Do not change unrelated files
- Do not change the expected result merely to make the failure disappear
