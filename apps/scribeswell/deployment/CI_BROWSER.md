---
title: Fix first-release browser acceptance failures
type: bugfix
created: 2026-09-29
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: b0c23b7c432d072c6309f3f95852eda6cf3e9d38
context: []
---

<frozen-after-approval reason="Owner authorized autonomous fixes and coordinated production release">

## Intent

Unblock first production release without weakening the existing privacy or keyboard
navigation guarantees. A clean CI checkout lacks the intentionally ignored poetry
library; the existing filesystem-denial test therefore requests a nonexistent file
and sees the SPA fallback. Separately, mobile dictionary Back can fail to restore
the expanded Strong's details/link focus. Reproduce and correct the underlying
state/timing issue. Preserve genuine source material and never publish it to make
CI pass. No database/auth/rights changes or added dependencies are needed.

</frozen-after-approval>

## Implementation Notes

Small reversible footprint: reader.spec.cjs should create a unique synthetic file
outside Vite's allowlist and remove only that owned file in finally, asserting403
for a real file independent of private source availability. WordStudy.tsx and
lexicon.spec.cjs need a deterministic regression for native details toggle timing
and Back navigation, then the smallest correction based on observed evidence.
Run focused failing tests first, affected browser suite and frontend build. Record
exact outcomes. Shared UI/scaffold/context/ADR impacts: none; silo-only UI and tests;
accepted ADRs unchanged. Local implementation/review are within prior authorization.

## Review Triage Log

- Documentation verification record absent: low; normal finalization was pending.
  Exact failures, commands and results recorded below before completion.
- Reverse disclosure race lacked coverage: medium verification gap; added the
  collapsed-state variant so an always-expanded implementation cannot pass.
- Privacy assertion coupled to launcher assertions: low; pre-existing coupling
  exposed by this change. Split into its own test as a direct correction, keeping
  actual-file403 and owned cleanup requirements.

## Verification

CI run36545702408 failed before activation/publication: missing private-file fixture
returned SPA200 and mobile Back lost disclosure/link focus. Deterministic new test
failed on both desktop/mobile before implementation. Focused six cases then passed.
Full Scribeswell browser suite before review additions:94 passed; production frontend
build passed. Review added collapsed-state regression and isolated privacy test.
No shared UI/scaffold/agent-context/ADR or database changes.

Review additions: eight focused desktop/mobile cases passed, including expanded
and collapsed disclosure restoration. The nonexistent favicon.svg link reported
on the old public site was also removed from index.html; no favicon asset existed.

Commands: `node_modules/.bin/playwright test --config
apps/scribeswell/web/playwright.config.cjs` (94 passed before review test additions);
focused `--grep 'navigation precedes|actual entry 10|private workspace'` (8 passed
after review additions). Isolated production build completed successfully;
`git diff --check` passed. Release retries remain under the owner's active approval;
no migration or production-authority change is introduced.
