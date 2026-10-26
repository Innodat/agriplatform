# Workspace-tabs architecture review — technology reality check

Date: 2026-10-22. Scope: the tabs/four-pane update to `ARCHITECTURE-SPINE.md`, its D-4 companion and the existing application substrate. This is a source/document review, not execution evidence or implementation readiness.

**Verdict: PASS for the draft update. No blocking technology findings.** The proposal retains the installed stack, identifies the current two-pane implementation accurately and gates new behavior on qualification. It selects no new library whose present capabilities or release version need external verification.

## Evidence checked

| Architectural assertion | Repository reality check | Assessment |
| --- | --- | --- |
| Existing React/TypeScript frontend and FastAPI backend remain the substrate. | `apps/scribeswell/web/package.json` declares React, React Router, TypeScript and Vite; `apps/scribeswell/backend/main.py` constructs FastAPI; backend requirements and `database.py` use psycopg/pool. Root lockfile contains the corresponding frontend packages. | Supported. The spine correctly defers exact versions to manifests/lockfiles and requests no upgrade. |
| Four-pane workspaces are new work, rather than an existing generalized reader capability. | `ReaderPage.tsx` uses `type Pane = 1 | 2`, pairwise URL keys and two explicit `PassagePane` instances. `PassagePane.tsx` likewise restricts `number` to `1 | 2`; `toggleComparison` creates/removes pane 2. | Supported. AD-12 and D-4 are design commitments; the draft never claims existing code already supplies tabs or four panes. |
| Existing chevrons navigate chapters, not independent history ledgers. | `components/bible/PassagePane.tsx` labels the controls `Previous chapter` and `Next chapter` and calls `useChapterNavigation` results through `onNavigate`. | Supported. Retaining these controls while superseding the proposed pane histories matches actual code. |
| Note state must outlive the keyed analysis component. | `ReaderPage.tsx` renders `WordStudy` keyed by pane plus selected word ID and conditionally removes the entire inspector when selection/focus changes. | Supported. A controller-owned global per-note lane avoids relying on the lifetime of this existing subtree. This is an ownership rule, not a claim that an editor/state library already exists. |
| New navigation must preserve current URL attribution, target-generation and viewport protections. | `ReaderPage.tsx` validates selection against URL-derived book/chapter, increments `targetRevision` for explicit verse seeks and has focus-mode scroll anchoring. `PassagePane.tsx` applies target seeks once and waits for visible geometry/data using `ResizeObserver`. | Supported. The new draft explicitly calls for stable tab/pane/navigation identities and generation-gated reapplication after mounting. |
| Existing authentication helpers do not settle current account admission. | `backend/auth/jwt_optional.py` uses a configurable HS256 secret and disables audience verification; it does not call Access. Access currently exposes `/v1/check`, while `account_actor.ensure` exists in restricted operator code. | Supported. Brownfield and D-1 explicitly require review/new protected contracts instead of treating these helpers or operator privileges as sufficient. |
| Private studies cannot reuse the public corpus runtime authority automatically. | Existing `backend/database.py` implements the public corpus pool and role validation. The reviewed documents label the private restricted pool/roles and migrations as required new work. | Supported. No existing private persistence is presumed. |

## Nonblocking qualification items already covered by the draft

1. **Browser history and resource bounds remain proposals.** The `reader` URL JSON, `history.state` namespace, 12-tab cap, byte limits and closed-tab replay are not derived from an existing implementation. The companion consistently marks them proposed and requires executable qualification before consuming code. Keep that status until parser/replay/capacity sequences demonstrate the contract; this review does not validate those numeric bounds.
2. **Unmounting inactive views needs characterization.** The existing pane's applied-target marker and scroll references are component-local. Unmount/remount will reset those values, so the future controller must restore the approved anchor without accidentally repeating a direct-link seek. D-4 already requires the matching generation/anchor tests; no current-code compatibility guarantee is inferred.
3. **Four-pane geometry and native selection have no new runtime proof.** No framework claim establishes readable three/four-pane layouts, bounded requests, Hebrew touch selection or keyboard/caret retention. The architecture correctly leaves responsive, resource, accessibility and real-device evidence in D-4, rather than converting the mockup into acceptance evidence.

## Review boundary

No production technology/provider or package was selected, no migrations were executed and no application/browser test was run by this reviewer. Source reads establish the existing substrate and the need for the proposed seams; they do not close D-1–D-5 or prove implementation performance/security. No corrective edit to the architecture is required for this technology lens.
