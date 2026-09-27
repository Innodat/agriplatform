---
title: Simplify word inspector controls
type: bugfix
created: 2026-09-27
status: done
route: oneshot
---

<frozen-after-approval>
## Intent

Give clickable dictionary and root references the hand cursor (`cursor: pointer`). Remove the bottom Source details disclosure and the duplicate Close word study control in Occurrences. Retain the header close action on both tabs, readable grammar, dictionary attribution, and dictionary navigation/history. This is the requested reversible UI polish before production preparation.
</frozen-after-approval>

## Implementation Notes

Small local change with no intent gaps or irreversible actions. Remove obsolete disclosure state from WordStudy snapshots as well as its rendering. Update affected existing acceptance checks and verify visible cursor behavior and the surviving close button. Source codes remain in the API and original collection; dictionary attribution remains visible. No scaffold/shared-UI/agent-context/ADR changes; application-only behavior. Documentation: this delivery record. Production target discovery is ongoing separately and requires target information and final approval before production changes, as requested by the user.


## Verification and review

Acceptance traceability: `lexicon.spec.cjs` scenario “dictionary controls show hand cursors and header closes either tab without duplicate actions” checks both root/BDB cursor styling, disclosure absence, no duplicate footer control, full occurrence-page scrolling, header-close viewport visibility, inspector removal and selected-token clearing on desktop/mobile. Existing participle and history tests now assert raw source disclosure absence while retaining grammar and expansion/history checks.

- Before implementation, focused browser acceptance failed twice on computed `cursor: default` instead of `pointer` (log `/tmp/inspector-polish-red.log`).
- `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web > /tmp/inspector-browser.log 2>&1`: 92 passed.
- After review expanded the scrolling/close assertions, the focused scenario initially failed because the added occurrence fixture omitted required nullable `display_he`. Corrected the fixture to `display_he: null`, preserving the production contract. `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu npm run test:browser --workspace=apps/scribeswell/web -- --grep 'dictionary controls show hand' > /tmp/inspector-polish-green.log 2>&1`: 2 passed.
- `npm run build --workspace=apps/scribeswell/web > /tmp/inspector-build.log 2>&1`: passed; existing bundle-size advisory.
- `python3 tools/py/run_compose_supabase.py --check-only`: passed without mutations; this is local composition validation, not production readiness. `git diff --check`: clean.

One-shot blind review only; no separate edge/contract reviewers for this small UI change.

| Review finding | Verdict and resolution |
| --- | --- |
| Sole header close untested after full occurrence-page scroll | Low verification gap; expanded fixture to 25 rows and asserted viewport visibility/clickability on both sizes; passed. No product defect established. |
| Close assertion checked only tablist rather than full inspector/selection | Low verification gap; assert aside removed and selected token cleared; passed. |
| Delivery record lacked exact results and traceability | Low documentation gap during in-progress review; completed evidence above. |

No UI findings deferred. First-release preparation is recorded in `apps/pts/deployment/RELEASE_PREPARATION.md`; deployment awaits the owner's target details and final production approval under the original request. No production actions occurred.
