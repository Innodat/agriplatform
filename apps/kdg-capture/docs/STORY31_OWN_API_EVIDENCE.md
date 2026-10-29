# Story 3.1 configured own APIs and native provisioning — 2026-10-29

Status: implemented, locally qualified and independently reviewed. Story 3.1 remains
incomplete. This follows administrator portal commit
`5f995f437dc4bcc3d5de66dc5bd0db8a9479ed02`. The Identity native prerequisite was
consumed unchanged. [Safe receipts](evidence/story31-own-api-20261029.json) identify
retained artifacts and hashes; private credentials and business payloads stay ignored.

## Delivery and observed failures

Explicit own database/questionnaire configuration now mounts the seven existing owners:
setup, create, own edit, edit context, operation recovery, own detail and own history.
Context-only and administrator-only configurations remain supported. Configuration is
lazy and requires the restricted runtime role; startup performs no migrations. The
configured export/client preserves owner DTOs with stable namespaces and merges distinct
methods sharing a route while refusing collisions. No administrator write is mounted.

Actual restricted provisioning first failed because storage candidate 0002 allowed
eligibility SELECT but no INSERT. Linked controlled candidate 0003 grants INSERT only
on required columns, binds organization/account/actor/membership/creation evidence in
RLS, and leaves issuance time server-owned and existing eligibility immutable. An
ordinary migration callback failed after real DDL: effects and ledger rolled back,
activation stayed blocked, and explicit forward upgrade/repeat succeeded. The already
running previous administrator consumer still read the original two captures and exact
v1 definition after upgrade. That compatibility observation precedes later new captures.
Applied 0003 bytes still match its upgrade source binding; no applied migration changed.

A native 1,000-child run exposed an actual ten-second timeout. Characterization tests
preceded batching of deterministic existing child locks, a separate post-lock READ
COMMITTED reread and atomic eligibility INSERT. The SQL-count acceptance failure was
8,011 against a bound of 20; no deadline, child cap or authorization was relaxed.
PostgreSQL documents output-expression evaluation after sorting for expressions outside
sort/group/distinct keys ([SELECT List](https://www.postgresql.org/docs/17/sql-select.html#SQL-SELECT-LIST));
the volatile advisory-lock expression follows that rule. Native coordination verifies
post-wait child changes, bounded lock timeout and cancellation before connection return.

The first native harness compared Python tuple-shaped models with JSON lists; its
failed attempt is retained and the oracle now uses JSON serialization. A pre-batch HTTP
attempt refused source drift after provision.py changed during execution. A resumed
HTTP attempt observed 503 without sufficient diagnostic detail to identify its cause;
that attempt remains failed. A subsequent fresh bound run passes. No expected domain
result was changed to hide these failures.

## Actual local qualification

The retained fresh frame is
`platform/deployment/.local/kdg-story31-20261028/fresh-8f3e984596bb453a902adb8710b4860d`.
After environment interruption, selected owned containers reported exit 255. Resume
recorded those observations, restarted only needed owned resources, waited for database
health and reacquired real synthetic provider sessions. It does not claim normal
shutdown for the interruption. Earlier resources, volumes, records and evidence remain.

- Native **16 checks** use real GoTrue/current Access over TLS and restricted PostgreSQL:
  scope/mode/account/actor/membership/permission rejection, server-only time, immutable
  history, role/ledger/write denials, atomic duplicate failure and cleared local settings.
- Load **3 checks**: 1,000 children complete in **0.446 seconds**; legal large UTF-8 labels
  exceed the actual response cap and roll back all 1,000 inserted eligibility rows;
  1,001 children are refused before issuance. All 999 load children remain inactive with
  revisions/evidence retained; none was deleted.
- Coordination **3 checks** observe real PostgreSQL waits, a committed child change
  during the wait, bounded contention and cancellation/unwind without issuance.
- Configured HTTP **11 checks** run runtime.create_app with own and administrator owners:
  latest-v2 setup, independent role matrix, actual existing foreign-organization 404,
  own-owner isolation and account-bound keyset cursors, create/first-committed replay,
  recovery, edit context, committed edit attribution, no-op/retry and administrator refresh
  with exact original v1. The foreign capture is trusted native fixture preparation,
  not a claim of authorized foreign HTTP creation. This HTTP producer journey does not
  establish device-saved PWA synchronization.

All selected native/HTTP receipts bind executed sources and report unchanged sources.
Pinned Python 3.15.0, Psycopg 3.3.6, SQLAlchemy 2.1.4, Alembic 1.20 and retained
Node 26.11.1/TypeScript 7/API generator were reused without installation or upgrade.

## Verification and review

Final affected verification: **420 tests and 81 subtests pass** (104.05 seconds).
The explicit affected test selection and commands are recorded in the delivery spec.
Both configured exporters, generated client freshness, strict generated types, write /
database / native-database template parity and composition check-only pass. Broad
migration-test discovery was not used; the prohibited fixture was never accessed.

Three independent BMAD review lenses completed. Blind and edge reviews found no
supported issues. Verification initially reported missing successful configured detail/
edit wiring coverage; after inspecting the actual HTTP script, real factory and safe
receipts, that reviewer withdrew it as an evidence split. No finding is deferred.

Scaffold: existing generated transaction/migration helpers are consumed unchanged;
batching and eligibility policy remain domain-owned. Shared UI: unchanged. Agent context:
existing guidance suffices. Documentation: API/migration instructions, safe evidence,
matrix and handoff updated together. ADR: existing ownership, authorization, bounded
transactions and controlled migration/recovery decisions apply; no new decision.
Implementation selected Sol High; coordinator/reviewer model timing and usage unavailable.

## Current AC-1–AC-6 matrix

| Criterion | Established evidence | Remaining acceptance evidence |
| --- | --- | --- |
| AC-1 current all-read | Actual mounted SDK/owner path, all-only admission, independent own/all checks, existing foreign-org record denied, account-bound cursors | Final integrated own-PWA boundary regression |
| AC-2 responsive review | Mounted responsive portal, exact original version/owner/answers; real configured create appears after administrator refresh | Saved-on-phone work through actual foreground synchronization and refresh |
| AC-3 administrator audit | Actual committed create/edit executor and server time, original author retained, no-op/retry unchanged; mounted read-only audit | Final integrated producer/portal regression |
| AC-4 portal/PWA split | Offline clears portal; all-record responses remain nonpersistent; restricted own APIs ready | Ordinary capture/My observations UI, durable foreground queue, verified offline host and shell/cache split |
| AC-5 invalidation | Actual provider signout/renewal refusal/expiry, account switch, grant/membership/app loss and owner outage clear portal | Integrated retained pending/conflicting own work through transitions and late-response tests |
| AC-6 accessibility/boundaries | Responsive/keyboard portal and actual role/HTTP boundaries | Integrated own-PWA accessibility, true zoom/assistive technology and actual installed Android/iPhone evidence, recorded separately |

Next execute the ordinary own capture/My observations integration and foreground
synchronization, followed by shell/update/cache qualification. These are locally ready
work, not equipment blockers. Physical-device and assistive-technology results require
actual equipment and cannot be replaced by browser emulation. No production, push,
real-account/credential change or destructive cleanup is included.
