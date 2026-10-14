---
story: '3.1'
epic: 3
status: proposed-awaiting-user-review
updated: 2026-10-14
sources: [../prd.md, ../EXPERIENCE.md, ../contracts.md, ../testing.md]
---

### Story 3.1: View authorized Khula observations and administrator audit details

As a questionnaire administrator,
I want to view organization observations and who recorded or changed them,
So that I can review facilitator captures without putting audit details in the capture form.

**Scope:** Responsive administrator history/detail and a compact online audit section;
current `capture.read.all` checks, bounded organization history downloads and exact
all-read local observation. Reuse E2 record/history components with a distinct authority
boundary. No administrator edit action until the next story, questionnaire/assignment
management, exports, dashboards or general revision browser.

**Requirements:** Administrator read portion FR-2/8, FR-11/13/15–17; NFR-1–4.
UX-DR4/7/8/10–13; AD-2/3/4/7/8/9. Questionnaire administrator is an app role, not
platform organization administration or employment.

**Acceptance Criteria:**

**AC-1 — Current all-record authorization**

**Given** authenticated fixed-Khula membership, app admission and explicit read.all,
**When** the administrator requests history or a record,
**Then** the API checks current authority and returns only that organization's records,
**And** capturer-only, membership-only and platform-admin-only accounts cannot use this
all-record surface or enumerate another author's records by ID, query or pagination,
**And** client owner/organization selectors never supply authority. Scope follows
capability at the action boundary; no silent own-scope fallback after all-read denial.

**AC-2 — Simple responsive review**

**Given** permitted server-backed observations,
**When** the administrator opens the portal on phone or computer,
**Then** show observation date, child and original capturer with ordinary record details,
**And** render answers under the exact original questionnaire, not the latest definition,
**And** distinguish genuinely empty results from failed/partial downloads,
**And** new facilitator captures appear only after their devices synchronize and an
administrator refresh succeeds. No promise to see never-synchronized phone work.
The ordinary capture interface retains its approved simple date/answers/status display.

**AC-3 — Audit stays on the administrator surface**

**Given** fresh read.all and a permitted record,
**When** the administrator expands Audit details online,
**Then** show original creator/creation time and latest committed modifier/modification
time, with a bounded list of committed create/edit events and actual editor/server time,
**And** original author is preserved, no-op/retry does not create a fictitious event,
**And** operational logs, credentials, payload dumps and unrelated records are excluded.
No snapshot-version picker, restore, export or audit download to phones. Audit list is
read-only; answers already appear in record details and need not be duplicated in it.

**AC-4 — Bounded authorized offline record access**

**Given** successfully verified read.all and its exact seven-day local observation,
**When** organization history is downloaded and later opened offline in the capture PWA,
**Then** reuse the approved 30-observation-day default and honest downloaded-record limits,
**And** use the same user's Khula partition with explicit all-read authority; own-read
success cannot mint or extend it, and ordinary own history cannot expose other authors,
**And** referenced definitions and attribution needed by current records are cached,
not the full audit/archive. Configuration administration still requires internet.
The responsive portal itself need not promise offline operation; the PWA provides
locally authorized downloaded history. Older records are requested online.

**AC-5 — Role loss, account changes and safe refresh**

**Given** revoked all-read, membership/app disable, expired local observation or another
account signing in,
**When** current verification or cached rendering is attempted,
**Then** affected all-record access is locked and no prior-user or lost-role records render,
**And** unavailable verification is distinct from explicit denial; unknown offline
revocation is bounded by the accepted window, not claimed immediately detectable,
**And** retained data does not confer rights or overwrite/delete pending/conflicting work.
Late responses and background refresh are bound to the original account/scope/session;
no renewed own-read check unlocks all-record data after known all-read denial.

**AC-6 — Accessible review and boundary evidence**

**Given** keyboard, zoom, phone touch or assistive technology,
**When** history, details and optional Audit details are used,
**Then** labels, focus, pagination/loading/failure feedback and responsive layout are usable,
**And** API/browser/real runtime-role tests prove foreign-owner allowed only under
current all-read, cross-org denied, original labels/owner retained and role-loss locking.
Automated scenarios and actual installed-device extension results are recorded separately.

**Contracts:** Extend existing history/detail handlers with explicit own/all authorization
modes and bounded queries, never permission inferred from a client role or actor ID.
Verify read.all independently in provisioning/history so exact all-scope observation is
available; no all-edit authority is minted here. Use existing Keyset pagination/private
no-store responses, original-definition retrieval and partitioned transactional cache.
Audit events use a narrow record-owned online read such as
`GET /api/v1/captures/{id}/audit`, protected by current read.all on every bounded page.
Concrete DTO/cursor/actor-display contract and server evidence minimization gate Build.
This is an app endpoint over app-owned evidence, not a new shared audit service. No
external waits under business locks or cross-service table reads.

**Dependencies:** Approved E1/E2 and existing shared Identity/Access prerequisites;
read.all registry/caller/schema fixtures, exact local capability context, actor-display
mapping and bounded audit DTO. These need owner closure before Build; E4 questionnaire
editor and E5 assignments/onboarding UI are not prerequisites. Controlled setup may
supply synthetic additional facilitators and children for acceptance proof.

**ATDD:** KDG-A02.admin-read/own-denied, A14.admin-read-org/account,
A15.admin-read-window, A16.admin-read-role-loss, A18.admin-history-partial,
A12.admin-original-definition, A21.admin-audit-attribution and A19.admin-review-accessible.
First observe missing A02.admin-read after approval, then focused authorization/read/
cache/audit tests and affected API/browser/runtime-role suites. No implementation or
physical-device execution occurs during planning.

**Impacts:** Scaffold: prove scoped pagination/attribution-read and exact local-observation
patterns with existing owners. Shared UI: responsive record list, optional audit section
and scope-aware state only after proven reuse; KDG labels remain application-owned.
Agent/docs: platform roles vs app capability, own vs all, portal vs offline PWA, no
central intake of phone proposals. Contracts: exact read mode/audit DTO/errors/cache
metadata and generated types together. ADR: inherit scoped Access, actor attribution,
privacy and bounded offline policy; no accepted platform contracts/ADRs changed here.

**Review checkpoint:** Proposed scope/criteria await confirmation before formal append.
Administrator editing/conflict handling follows as an independently reviewed increment.
