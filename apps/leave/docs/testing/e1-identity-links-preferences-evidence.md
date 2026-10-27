# E1-ID-B: person links and account language

2026-10-26. [Execution spec](../../../../_bmad-output/implementation-artifacts/spec-1-5-e1-id-b-person-links-and-preferences.md).
[Machine receipt](evidence/e1-identity-links-preferences-20261026.json) binds selected source, historical preservation, retained logs and native proofs.

**Reviewed delivery complete — 2026-10-26.** All17 externally supplied findings
were individually triaged and corrected; no findings deferred. Final source-bound
owner/release regression: **1,996 passed in112.84s**, one existing deprecation warning.
Generated API/type checks, exhaustive typed conflict handling and both composers pass.
See the [review correction receipt](evidence/e1-identity-links-preferences-review-20261026.json)
and spec triage log for exact sources, commands and retained native frames. Earlier
review-capacity limits are resolved by the three user-supplied review results. No live
activation follows; Access grant integration remains the next delivery gate.

The accepted ID-A foundation is reused; historical Identity revisions and references1–21
remain byte-identical. Identity23 adds to the existing independently owned history inside
Access's service boundary. Applications consume owner APIs; no Leave identity copy or
new runtime service was introduced.

| Requirement | Implementation and verification |
| --- | --- |
| Independent accountless person; verified retained account/person/stable actor link | Revision22, typed `person.create` / `account.link_person`, current exact operator authority, server actor/UTC attribution, protected immutable person/link and compact operation/event evidence. Native person qualifier passes10 stages: exact/changed/stale retry, wrong target, inactive account, conflicting relink, same-person distinct-account actors and concurrent identical command. No implicit membership/employment/grant effects. |
| Existing membership history and manual replacement | Adopted six pinned legacy sources with original three-account profile/org/member/role hashes preserved, then actual current23 adoption. Transition qualifier passes5 stages: three distinct people, explicit replacement sharing the intended person with a distinct actor, two retirement/rejoin cycles, delayed old join/retire retries, concurrent second-org join, legacy role/hook claims and current authority revoked/denied/restored. Old accounts/history remain; replacement does not inherit membership or app access. |
| Own-account language persistence | Authenticated service-and-user GET/PUT, restricted `identity_preferences_runtime`, own account only; en/pt desired locale and decimal-string revision. Native real local Auth + HTTP + PostgreSQL passes8 stages: known absence en0, desired pt, organization independence, other-account isolation, closed inputs, exact retry/original outcome, changed retry/stale conflict, concurrent same-revision writes and current authentication. Tests run before person/link/membership creation. No translation/UI delivery is implied. |
| Missing actor and failure semantics | Supplemental native proof: an unmapped scratch account reads en0; PUT409 `identity.actor_setup_required`, without implicit actor/person/member setup. An injected required business-event failure rolls back person and outcome; exact operation succeeds after explicit trigger restoration. Separate required preference-outcome failure rolls back the preference write. No unavailable result is treated as absence or acknowledged save. |
| Restricted credentials and structural safety | Actual original logins deny raw rows/private ledger/owner DDL, with SQLSTATE42501 required for a privilege proof. Fixed security-definer functions/RLS and composite account/actor FK preserve attribution. Preferences cannot take another account from body/query/JWT. Source tests supplement actual DB checks. |
| Controlled clean/adopt/previous/repeat/failure/recovery | Independently recorded revision22/23 references from always-rollback rehearsal; exact21 restored before publication. Eight controlled upgrade/repeat/late-postcondition-failure/forward-retry commands pass; injected failure restores21 with no person/preferences tables. Additional fresh empty-schema current23 full upgrade passes. Actual release coordinator failure leaves23 unchanged, later owners unattempted and activation false. Failure ordering does not prove later-owner readiness. |

The manual-recreation rehearsal uses synthetic retained/replacement identities, not
production user fixtures. Two retained inputs authenticate through actual local Auth;
the third retained history uses a scratch Auth substrate. A synthetic replacement was
created only in disposable local Auth. Provider deletion, production migration, document
transfer and actual Access app-grant effectiveness were not performed. Later ACCESS
must qualify membership-bound admission/grants before coordinated activation. People
and Leave prove their own retained employment/draft/history integration later.

## Commands and results

Prepared interpreter `P` is
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`;
use `-I -B` and no package installation. Private frame `.local/leave-id-b-20261026/`
contains fixture-only drivers and credentials; never copy private fixtures into evidence.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$P" -I -B services/access/tests/qualify_person_links.py --fixture .local/leave-id-b-20261026/current_clean-person-native-private.json --run-id 88a737dd-ad7b-429a-a83c-5d103716d659 --port 55582 --output .local/leave-id-b-20261026/person-native-final-proof.json
"$P" -I -B services/access/tests/qualify_language_preferences.py --fixture .local/leave-id-b-20261026/language-native-private.json --output .local/leave-id-b-20261026/language-native-proof.json
"$P" -I -B services/access/tests/qualify_identity_transition.py --fixture .local/leave-id-b-20261026/transition-native-private.json --run-id 88a737dd-ad7b-429a-a83c-5d103716d659 --port 55582 --output .local/leave-id-b-20261026/transition-native-proof.json
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Initial delivery owner/release suite: **1,938 passed in66.91s**, one existing Starlette/httpx
deprecation warning. Both composers pass. Owner OpenAPI export/check passes; generated
wire types use the existing pinned local API-client tool, with no hand edits/dependency
changes. The machine receipt retains source/reference/log hashes and exact native-stage
receipts; private operation journals are fsynced before command execution.

Root-owned native drivers, in execution order, are `prepare_native.py`,
`rehearse22.py`, `rehearse23.py`, `qualify_migrations.py`, `current_clean.py`,
`prepare_cohorts.py` (explicit current_clean input), language/person qualifiers,
`legacy_adopt.py`, transition qualifier, `release_gate.py`, `supplement.py`.
Each uses the existing disposable Leave run88a737dd-ad7b-429a-a83c-5d103716d659,
DB55582/Auth55581, and synthetic scratch databases. No connection/mutation to KDG.
Repeated execution requires reviewed fresh fixture/output paths; these are not reset
scripts or a supported live provisioning tool. The normal stack stop preserves volumes.

## Failed attempts and recovery

Failing-first parser rejection and actual API404 are retained in `red.json`; the initial
migration-only environment lacked httpx and is recorded as an environment failure,
not acceptance evidence. New preference tests initially failed17 cases. Native reference
rehearsal exposed the temporary schema permission needed to replace an authority-owned
routine and a PL/pgSQL CASE syntax issue; both were fixed before reference publication.

The first person native attempt committed partial, valid synthetic outcomes before a
restricted-caller error-mapping assertion failed. Its database and receipts were kept;
`person-native-initial-reconciliation.json` records counts and the limitation that its
original random operation IDs were not durably journaled. The corrected final qualifier
uses an exclusive fsynced attempt journal and a fresh prepared current_clean case; no
blind replay, reset or receipt replacement. Source tests observed42501 mapping failure
before its correction. Strict privilege proofs now require42501 rather than accepting
arbitrary SQL/transport failure.

Initial broad regression:1,922 pass/2fail. One test assumed21 remained the head; it now
retains21/22 verification but requires23 for current-head acceptance. The other exposed
FastAPI OpenAPI security merging credentials as alternatives; the generated contract now
requires the same service-and-user conjunction enforced at runtime. Final regression
passes. All earlier logs remain alongside final frames.

## Impact decisions

- Scaffold: owner-local migration/catalog/native fixture patterns proven with this consumer;
  no new generic delivery workflow or scaffold schema/runtime engine is needed.
- Shared UI: none; this delivery supplies persistence/HTTP only. Later user-facing personal
  preferences follow immediate saving conventions and approved failure presentation.
- Agent context: existing ownership, ATDD and migration instructions suffice; no change.
- Documentation: owner migration runbook, mutable inventory, Leave tracker/handoff and this
  requirement/evidence mapping updated together; historical records remain historical.
- ADR: existing accepted decisions cover person/account/actor separation, attribution,
  structural constraints, short transactions and controlled release; no new decision.

## Review corrections and fresh evidence

All17 findings (B1–B10, E1–E3, V1–V4) are recorded individually in the spec. B4/E2
share the typed-error correction; B7/V2 share exact projection verification. The
finding-floor arithmetic is not an additional finding. No intent change or deferred
issue was needed.

- Both head22/23 restore inherited Studies role-member verification; head22 also pins
  revision21 source. Native rollback-only grants prove unexpected owner membership is
  rejected at both heads and fully restored; real migration-login catalog verifies.
- Revision23 adds three composite foreign keys to the stable account/actor mapping,
  protecting preference creation/update and original-outcome attribution. Six actual
  nonexistent-account/foreign-actor alternate-write probes now reject23503; matching
  pairs remain valid. The prior accepted alternate-write probes were rolled back.
- Existing error envelopes now have owning OpenAPI schemas/statuses and generated types;
  consumer compilation proves exhaustive recovery handling. Falsy non-null person event
  IDs are rejected. Native409 assertions distinguish operation and revision conflicts.
- Every qualifier validates actual Leave container/network/loopback binding before
  connections and restricts scratch database names. Language output is exclusively
  reserved before auth or writes; its journal completes short writes before fsync.
- Native language proof successfully persists pt→en revision3, reads en, and replays
  the original pt/revision1 operation while current state remains en/revision3.
- Person proof checks exact person/revision, missing person, missing actor and inactive
  profile; exact one-outcome/one-event relationship; distinct-operation competing links
  with one retained mapping and no losing evidence; exact operator target/execute/lookup
  denial with unchanged rows. Actual CLI main and isolated workers execute/recover both
  new commands through a root-prepared acceptance-only protected target descriptor.
- Transition proof repeats retained membership/rejoin/history, legacy hook/roles and
  both revoked execute/lookup denials, preserving rows and restoring authority.

The revised23 reference is `93b3f573e4df2c92d6c936674e552bdadd8d6b2f68e22a3134c7ceaf9400683f`.
It was independently recorded on a fresh prior21 frame with always-rollback22/23
rehearsal and exact21 restoration. The original23 candidate/reference and proofs remain
in `review-before-fixes/`; no applied frame was silently edited or reset. Revision22
reference and historical revisions/references1–21 are unchanged. Fresh native clean,
previous21/failure/rollback/forward-retry/repeat and preserved legacy adoption pass.
All private review drivers, fixtures, outputs and journals use `review-`/`review_` names
inside the existing local frame; published evidence contains safe hashes/references.

Additional retained attempts: four new language tests failed against preserved prior
source, and receipt/catalog tests failed13 cases before correction. The first direct
person entrypoint failed importing the shared guard under isolated Python, before any
fixture read/DB effects; an explicit path fix and isolated subprocess test now pass.
Two rollback-only invariant-driver attempts compared catalog fingerprints from an admin
session, which differs from original migration-login rendering. All probes/temporary
role edges rolled back; read-only checks under real migration credentials passed on
both review frames, and the corrected driver now verifies through that original login.
These were driver-context failures, not schema repair or relaxed expected results.
An initial sandbox HTTP test process stalled and was stopped by its exact PID; checks
were rerun with required local thread/socket permission. Earlier attempts remain.
