---
status: done
route: oneshot
---

# Private Psalm AI research reader

## Intent

Simplify PtS → Swahili Poetry for the user's specified private, noncommercial team objective: training AI to generate Psalms. A changed purpose, public dataset/model release, or publication needs its own rights assessment. Swahili is the language; Kiunguja is a dialect and Zanzibar is an origin/collection association, not an automatic dialect assignment.

## Acceptance

- Default to Ready for team research; show search, dialect and More filters. Turning Ready off browses all texts. Preserve all existing filters in one accessible drawer on desktop and mobile, including draft/apply/close and Back behavior.
- Display poem text first, an understandable private-project usage label, and a separate text-review label. Source checks never imply rights clearance.
- Assess recorded source terms for this private scope. Valid direct CC 4.0 licences, including ND, can support private noncommercial copying/training; preserve conditions and do not assess public release implicitly. Hold uncertain or separately quoted poem rights. Treat the Wastara PDF NC-SA notice as the working terms, broader BY unconfirmed.
- The Ready filter and exports use the same backend selection and require source-checked complete text plus eligible private-purpose rights. Unknown terms, explicit holds and pre-4.0 ND are not silently approved.
- Ready downloads contain reviewed main versions only, not unchecked alternate witness texts. Original evidence remains available through ordinary browsing and individual poem details.
- Rights remain source/scope projections; preserve every original record, witness, licence notice and authentication/authorization boundary.
- Show plain licence explanations first, source evidence expandable, raw technical records under a further expandable disclosure. Preserve citations and all source notices in exports.

## Impact decisions

Application-local presentation and rights projection. No migration, storage import, public deployment, access-scope transition or model/provider integration. Existing account/access/Content adoption planning remains untouched. No shared UI/scaffold promotion: these labels and rules are domain-specific. Agent context and ADR: unchanged; existing protected read/export contracts retained. Generator impact: regenerate the owning TypeScript contract generator after the additive API projection/query update. Documentation: this owning BMAD oneshot record and user guide. No competing delivery lifecycle or duplicate ADR introduced.

## Evidence

Acceptance tests will first demonstrate the missing research projection/filter and simple reader controls, then implementation will satisfy them. Preserve unrelated dirty-tree work.


## Using the reader

The reader opens with Ready for team research selected. Search or choose a dialect. Turn Ready off to browse all collected texts, including drafts. More filters opens the same drawer on desktop and mobile; Close/Back discards un-applied changes, Apply preserves the chosen filters.

Poem text is shown immediately. Private-training terms and text quality have separate labels. Usage and source details opens the project conditions and source links. Licence and evidence, Other source versions and Technical record/history progressively expose the full preserved evidence.

Download poems is the primary download. Other downloads contains JSON and the original text export. Ready downloads contain only eligible, complete source-checked main versions, with project purpose, source attribution and conditions. A source check is not expert language adjudication. Ordinary browsing still exposes the original witnesses and reference notices.

No stored copyright record was rewritten. The private-purpose assessment is a read-only source/scope projection; primary CC grants differ from an article licence for quoted works. ND 4.0 private noncommercial use is not automatically held; older ND, independent poem rights holds, unknown licences and unresolved contradictory notices remain review cases. The known Wastara PDF NC-SA 4.0 statement is the working basis, with the broader catalogue BY grant unconfirmed. No public output, dataset/model release, provider-general-model training or changed-purpose permission is inferred.

## Verification

- Red: `python3 -m pytest apps/pts/tests/test_research_use.py -q` — 11 expected failures: missing private-purpose projection, unchecked/unknown-rights rows admitted, no bounded ready export.
- Red: Node 24 with Playwright `--grep simple` — desktop and mobile failed because the simple private-purpose reader was absent.
- Green: `PYTHONPATH=/tmp/pts-test-driver-3.2.9 python3 -m pytest apps/pts/tests/test_research_use.py apps/pts/tests/test_collection.py apps/pts/tests/test_api.py apps/pts/tests/test_contracts.py apps/pts/tests/test_archive.py -q` — 30 passed. Covers CC/ND version distinctions, explicit holds, container licences, Wastara working terms, text quality, main-only export, unchanged originals, authorization and generated contracts.
- `python3 -m apps.pts.tools.generate_contracts` — regenerated through owning generator. Contract drift test passed. No generated file hand-edited.
- Node 24 `npm run build --prefix apps/pts/web` — passed TypeScript and Vite; existing large-bundle warning remains.
- Full desktop/mobile browser suite — 50 passed. Final Sources presentation refinement — affected Sources suite 6 passed. Covers filters/draft Apply/Close/Back, search, links, citations, downloads, notices, revocation, sign-out, session refresh, account replacement, password recovery, launcher and private-file serving denial.
- Initial regression failures were explained: new API fields required asserting original source arrays separately; simplified count wording replaced the old count string; hidden witness text needed a distinct semantic CSS class; ready checkbox needed a role-specific locator. Requirements changed deliberately; protection assertions remain.

## Review / deployment

Application and shared scope/access planning was preserved. No authentication, account/organization adoption, Content ownership or storage boundary changed. No migrations or corpus import were run. No local PtS API process was running at verification time; no service was restarted and no public deployment performed.

Deploy the updated API before activating the updated reader, since the new reader defaults to the additive `availability=research` query. The previous reader remains supported by the updated API. Use the existing platform release procedure; this task does not activate a hosted release.

Rights evidence used for the private scope:
https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en (2(a)(1), private adapted use)
https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en
https://creativecommons.org/faq/#artificial-intelligence-and-cc-licenses

Scaffold/shared UI/agent context/ADR impact: no changes, application-specific projection and presentation. Documentation and owning contract generator updated in this delivery. Existing corpus checksum/preservation tests pass.
