# Collection summaries and acquisition priorities

Repository-owned PtS delivery record, 12 October 2026. User authorised reversible
implementation and further resource gathering in the ongoing Psalm AI project.

## Outcome and acceptance

- Filtered results show distinct works, ready works, short/medium/substantial texts,
  missing texts, word count and record versions. Duplicate work IDs count once.
- Each text-bearing poem shows its length band, stored verse lines, approximate
  words and explicit incomplete/unconfirmed status. Main poetry remains visible.
- Sources supports title/origin/reason search and a priority-only checkbox.
  Acquisition leads are separate from the stored corpus and never inflate counts.
- High priority and Promising are assistant research judgments backed by reasons,
  next steps, source evidence, assessed date and contact routes where established.
  Contacts are not presumed to control all contributor/edition rights.
- Collection targets are internal working notes, not reader-facing UI. The user
  corrected the initial placement on 12 October; target prose was removed and the
  reader build passed again. No auth changes made by this UI feature.

## Counting definition

Short <=12 nonempty stored lines, medium 13-39, substantial >=40. Number-only
stanza labels and blank lines excluded. Stored half-lines/speaker labels can affect
the category; text length is not genre and an excerpt is not a full short lyric.
Deduplication favours a ready version, then a source-checked complete version,
then the most words. Missing metadata never grants readiness. Empty results show
zeroes. Counts cover the current filtered selection, not the whole collection.

## Acquisition research

Private /api/sources supplies a curated, versioned bibliographic catalogue:
12 external collection leads plus 3 priorities on already catalogued sources.
The six new collections are Nassor Hilal Kharusi's Mama Usihuzunike, Diwani ya
Barsheba: Safari, Hisia Zangu, Siku Zapishana; Ahmed Hussein Ahmed's Haile Ngoma
ya Wana; and Tunu Mpya (publisher listing forthcoming; availability to confirm).
The first four offer Zanzibar material; exact dialects are not assumed. Publisher
explicitly identifies Haile as Kimvita from Mombasa. The multi-author anthology
requires contributor-by-contributor rights attention. None is newly AI-cleared.

Primary evidence and public contacts are retained in backend/acquisition_catalogue.json.
Some Kharusi edition years differ between university bibliographies; confirm an
edition before importing. No direct Kharusi email found. Publisher contact page,
SOAS's official special.collections email, York's Philip Burnett email and the
author's own website are used as contact routes. No messages or purchases made.

## Impact decisions

Scaffold: none; this is poetry-specific display and acquisition metadata.
Shared UI: none; retain these domain-specific components within PtS.
Agent context: no change to AGENTS; no new generic workflow.
Documentation: this repository delivery record owns requirements and evidence.
ADR: no new architecture decision. Existing protected API, source-level rights,
private Content/download and stored collection boundaries remain binding.
API: additive optional acquisition fields; TypeScript generated with the owning
generator. Ratings cannot alter source_usage or poem_usage decisions. Curated
metadata lives in backend configuration, not a new DB schema or poem records.

## Verification and traceability

Observed four desktop/mobile acceptance failures before implementation: missing
summary region and missing acquisition cards. Implemented the requested behavior.
`npm run test:browser -- tests/reader.spec.cjs tests/sources.spec.cjs`: 28 passed.
New reader case covers duplicates, missing texts, length boundaries, unfinished
text warning, rights eligibility, changing filters, screenshots and mobile fit.
New source case covers priority-only filtering, reason/access/rights separation,
verified contact route, screenshots and mobile fit. Existing cases retain source
downloads, citations, export, navigation, sign-out and stale-authority protection.
`python -m pytest apps/pts/tests/test_api.py apps/pts/tests/test_collection.py
apps/pts/tests/test_acquisition.py -q`: 11 passed. API/collection behavior remains
protected; catalogue test proves unique acquisition IDs and no poem/rights grants.
`python apps/pts/tools/generate_contracts.py`: generated successfully after fixing
the invocation's repository module path. Never hand-edited generated DTOs.
`npm run build`: passed. Existing large-bundle advisory remains.
Desktop/mobile browser checks passed; mobile screenshots visually reviewed for layout.
Local PtS API on port 8010 restarted with its original configuration; health and
new source acquisition response contract confirmed. No public or cloud deployment
performed. The frontend build is ready; refresh the running development app.

## Follow-up collection batch, 12 October 2026

Five anonymous traditional song-poems from Velten 1903, printed pp.84–85, were
added with unchanged historical spelling, source-level conditional private-project
rights and a privately attached full source PDF. Every Swahili line was visually
checked; completeness means complete quoted passages in the printed witness, not
proof of complete oral performances. Individual origins/dialects unverified.
Import preserved all existing payloads and replay was idempotent. Current distinct
counts: 224 rights-eligible under recorded scope and 108 checked complete in witness.
This was a local corpus update; no production/cloud deployment occurred.
