---
status: done
route: oneshot
---

# Sources view

## Intent

Provide an authorized Sources view within PtS → Swahili Poetry, independent of poem filters. Show all collected source descriptions, recorded copyright/reuse assessments and notices, private document downloads and original online links. Preserve collection leads, incomplete scans, shared document references and HTML documents without inventing PDF availability or rights clearance. Reuse existing read/document permissions and session recovery; no new import, migrations or production changes.

## Acceptance and verification

- The protected sources endpoint returns exactly all 19 sources, 19 rights records and 30 document records, including sources with no collected poems; API tests assert original JSON equality, no-store and denied access.
- Desktop/mobile navigation, direct links and Back work; descriptions and nested/scalar rights render; PDF/HTML labels differ and original links are safe HTTP(S).
- Downloads use the existing authorized document endpoint. Revocation and sign-out remove protected content.
- Existing reader/login tests and generated contracts remain valid.

## Implementation notes

Owner-local React view and additive FastAPI contract; reuse organization-scoped repository and content service. Scaffold, shared UI, agent context and ADR: no changes needed, this is an application-specific presentation of existing contracts. Documentation: this delivery record and reader instructions. No source collection changes or new legal assessments.

Red: ` /tmp/pts-venv/bin/python -m pytest apps/pts/tests/test_api.py -q` — 2 failed (new endpoint missing), 2 passed.

## Review triage log

- Medium, patched: repeated selection of the active view cleared content without triggering a fetch. Redundant navigation now returns; browser regression covers it.
- Low, patched: summary text locators also matched collapsed full metadata. Scoped assertions to the summary occurrence; no expected behavior changed.
- Medium, patched: superseded navigation requests could report stale errors. Obsolete responses no longer affect the new view; current authorization failures still clear content and report errors. Delayed-response browser test added.
- Low, patched: sources endpoint loaded poem/witness content unnecessarily. Dedicated repository query now reads only the three source tables in the same organization-scoped consistent transaction.
- Medium, patched: Sources password-return context lacked coverage. Added same-user recovery test; existing account-replacement regression continues to cover clearing prior-account context.

## Verification

- `/tmp/pts-venv/bin/python -m pytest apps/pts/tests/test_api.py apps/pts/tests/test_contracts.py apps/pts/tests/test_collection.py apps/pts/tests/test_archive.py -q`: 12 passed. Checks canonical metadata equality, authorization, exports/citations, archive and generated contracts.
- `npm run build --prefix apps/pts/web`: passed TypeScript and production build. Existing large-bundle warning remains (530 kB main chunk).
- Browser testing initially found ambiguous test locators (2 failed, 38 passed); after correcting selectors, source-only suite passed 4/4. Review added active-navigation and delayed-response regression coverage and Sources password recovery.

## Opening the view

Open PtS → Swahili Poetry → Sources, or `http://localhost:5179/?view=sources`. Existing login and organization access apply. Stored PDFs use Download PDF; the stored HTML source has a separate label. Visit online source / Open online PDF opens the recorded external address. Online availability has not been re-researched. Recorded copyright notes do not establish new reuse permission. No database migration or production configuration is required for this view.

- Final `LD_LIBRARY_PATH=/tmp/pts-browser-libs/usr/lib/x86_64-linux-gnu apps/pts/web/node_modules/.bin/playwright test --config apps/pts/web/playwright.config.cjs`: 44 passed (27.1s), desktop and mobile.
- Live local Supabase/API check: authenticated Sources returns 19/19/30; a stored reference PDF downloads with attachment disposition and PDF signature; unauthenticated Sources returns 401. Local PtS API restarted, other services unchanged.
- Review: oneshot blind review completed; all five findings patched, nothing deferred. No additional review layers prescribed for this route.
- `git diff --check`: passed. No production changes, migrations, new source material or source rights edits.
