---
title: 'Prepare the accepted UI as a frontend release candidate'
type: 'chore'
created: '2026-11-04'
status: 'done'
route: 'oneshot'
context: ['platform/docs/development/bmad-codex-usage.md']
---

<frozen-after-approval reason="continuation of the user-approved UI and concrete release-preparation next step">

## Intent

Prepare a reviewable, isolated frontend candidate containing the accepted Scribeswell
UI. Base it on the actual deployed source
`59e2c8884cad24bb2f6e99fc519b2e6dc5bc9d84`, incorporate only the approved frontend
changes through `8747187cf45127ab3043abaeede54a00e542b861`, and preserve the deployed
launcher/auth integration and PtS frontend. Build Scribeswell at `/` with PtS at
`/pts/`, using the existing release recipe and public production configuration.
Verify built desktop/mobile UI, selector interaction, CSS/fonts, navigation and
artifact identity before presenting the candidate. Local preparation only; publication
and any production mutation require their concrete final approval. Preserve unrelated
dirty work and all historical release evidence.

</frozen-after-approval>

## Implementation Notes

- User's successive "next" messages continue the concrete release-candidate preparation
  described in the preceding handoff. No additional user-facing design choice, migration
  or external side effect is needed. This bounded task reuses implemented code and existing
  verification; no product/API behavior is newly designed. Existing dirty-tree authorization
  applies; use a fresh isolated worktree rather than modifying the shared release checkout.
- Investigation found the main checkout's release handoff stale: the isolated release
  delivery records actual production completion on 2026-11-04. Do not repeat shared
  adoption, owner qualification, image builds or backend deployment. Correct the UI
  handoff to reference that completed baseline.
- Source selection: approved frontend delta is the web subtree diff from common ancestor
  `e16d441ff26cee838f81fe118f980c7971c1745f` to the accepted UI commit. Apply it atop the
  deployed source; retain newer launcher/auth lines where patch context differs. No
  arbitrary dirty files enter the candidate. Record exact candidate and delta inventories.
- Reuse the deployed `platform/deployment/build-release.mjs` and artifact verifier,
  selected existing Node toolchain, and local installed dependencies. Build primary
  (bounded pregranted Studies) and recovery (Studies off), retain both independently,
  and compare PtS outputs to the retained deployed build. Do not print public Auth key
  bytes or read unrelated private runtime credentials.
- Given the isolated exact candidate, when compiled and served locally, then the
  approved UI checks pass against the compiled assets and all browser network calls
  remain local or are intercepted synthetic API/Auth fixtures. Given either variant,
  then root/deep-link/PtS entries and CSS/Hebrew fonts load, release identity binds the
  candidate, and artifact verification passes. A failure stays recorded until explained.
- Verification scope: focused existing polish, selector/workspace and account checks,
  plus rendered desktop/mobile inspection; prior 1,205 workspace checks retain their
  original boundary and are not relabelled candidate proof. No new backend proof claimed.
- Impacts: scaffold/shared UI/agent context/ADRs unchanged; documentation and safe
  candidate evidence updated within this frontend follow-up. No duplicate release engine.
- Workflow: oneshot coordinator preparation with the required independent blind review;
  no new runtime implementation delegation. Usage and final exact commands/results
  recorded at completion.

### Implemented candidate and review scope

- Candidate `7293caf739390857600bafd2d9e2213fecd270ef`, parent deployed59e2c888…,
  lives in `apps/scribeswell/.local/ui-release-20261104/`. Inspect its complete
  `git diff 59e2c8884cad24bb2f6e99fc519b2e6dc5bc9d84 HEAD`:23 web paths. The accepted
  UI source delta is common-ancestor e16d441… through8747187…; Topbar alone needed
  conflict resolution retaining all four deployed launcher/auth changes.
- Local-only orchestration: `/tmp/scribeswell-build-ui-candidate.py` (retained copy
  `.local/ui-release-evidence-20261104/build-driver.py` beneath the app),
  `/tmp/scribeswell-ui-static-server.py`, `/tmp/scribeswell-ui-candidate.config.cjs`
  and `/tmp/scribeswell-ui-candidate-visual.cjs`. They build/serve or fulfill actual
  compiled bytes with synthetic API/Auth and blocked production networking.
- Root documentation changed by this follow-up: `apps/scribeswell/docs/UI_RELEASE_CANDIDATE.md`,
  only the new approved-UI section in `apps/scribeswell/docs/OWNER_READINESS_HANDOFF.md`,
  this spec and the prior completed polish spec's acceptance/handoff paragraph.
  Preserve the hundreds of inherited unrelated changes, including older handoff additions.
- Both primary/recovery release builds and independent artifact verifier passed with
  Node26.11.1; PtS artifacts equal the retained deployed variants exactly. Build runs
  took6.802s/6.801s. Exact tracked source inventory unchanged during compilation.
- Actual HTTP compiled-primary UI checks:31passed/1intentional desktop skip,14.9s.
  First invocation failed before tests on sandbox localhost socket permission;
  approved rerun succeeded. Command and configuration are in the candidate doc.
- Additional visual/smoke command passed7scenario groups and captured20screenshots.
  Coordinator viewed desktop/mobile selector, phone editor and320px delete dialog.
  Both variants' root/deep-query/reload/fonts/PtS checks pass; primary editor/actions/
  confirmation/Retry fit1440/390/320px. External requests were blocked/intercepted.
- Primary/recovery and previous-primary static archives plus the exact binary source
  delta and hashed result receipt are retained under app `.local/ui-release-evidence-20261104`.
  No clean-install, live browser session, backend/native or deployed-site verification
  is claimed. No publication, remote push or production mutation occurred.

### Completion and independent review

- Independent blind reviewer found no supported findings in the23-file candidate;
  verified preserved deployed launcher/auth, approved UI composition,31pass/1skip,
  seven visual groups, matching PtS bytes and receipt hashes. No findings deferred.
  Review inspected retained results rather than rerunning tests. Edge/verification
  layers were skipped under the installed oneshot route.
- Rehashed both final artifacts after browser/visual work: inventories remain exact;
  candidate tracked worktree stays clean. Candidate source commit is7293caf739390857600bafd2d9e2213fecd270ef.
  Safe evidence: `apps/scribeswell/docs/evidence/ui-release-candidate-20261104.json`.
- Selected coordinator inline preparation; exploration used Sol High; required
  reviewer inherited coordinator capability. Actual model/billing and overall elapsed
  are not inferred. Available local usage is collected once at completion.
- Preparation complete. Proposed final action is primary static publication to the
  existing Scribeswell site, using existing release instructions and retained prior
  primary frontend for recovery. Publication remains unexecuted pending the separate
  concrete approval required by the release instructions and prior UI scope.
