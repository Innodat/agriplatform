# Note read response boundary

Status: bounded Notes correction implemented and independently reviewed. Final
48 repeated focused checks and owning build pass on unchanged166-file source
SHA1b10e1a3fcd202a38f2c803949b5a4d7e9fdcffe155a732c82bada7736fe07a4.
Broader affected run:743passed/2expected native skips/1existing mobile public-scroll
failure,16.4m. Its cause remains unverified; no clean broader-suite or final live
integration qualification is claimed.

The owning HTTP adapter now rejects unreadable note documents before outline/editor
attachment, using existing response_invalid and consumer recovery paths. The fixed
current grammar protects paragraph/list/inline shapes, scalar/collection budgets,
current format1/2 passage references, existing safe external URLs and unsupported
nonempty connections/highlights. It is a consumer renderability guard, not complete
wire-schema validation or authorization. Metadata attribution remains server-owned;
existing context guards still own account/current resource/intent decisions.

The editor reuses its unchanged extracted URL predicate. No direct DOM fallback,
partial-note sanitization, fabricated content or new recovery owner was added.
Malformed responses never replace a dirty lane. Success-response note/page identity,
revision and cursor shapes are checked before attachment. HTTP error codes/timeouts,
current authority, cancellation and original operations retain their existing paths.

## Chronology

Exact browser invocation prefix from repository root:
`SCRIBESWELL_TEST_PYTHON=/usr/bin/python3 npm run test:browser --workspace=apps/scribeswell/web --`

| Log under evidence/note-response-boundary | Arguments / result |
| --- | --- |
| 01-acceptance-red-and-characterization.log | `workspace-restoration.spec.cjs personal-notes.spec.cjs --workers=4 --fully-parallel --grep 'note response boundary\|formatting\|external link\|mixed Hebrew\|passage atoms'`:6 genuine failures/8 characterization passes,23.3s, before runtime edits. |
| 02-url-editor-characterization.log | `personal-notes.spec.cjs --workers=3 --fully-parallel --grep 'rich paragraphs\|editor toolbar actions\|invalid DNS link'`:6 passed,11.6s, before URL extraction. |
| 03-boundary-green.log | `workspace-restoration.spec.cjs personal-notes.spec.cjs --workers=4 --fully-parallel --grep 'note response boundary\|rich paragraphs\|editor toolbar actions\|invalid DNS link\|outline return opens complete'`:14 passed,27.1s. |
| 04-build.log | `npm run build --workspace=apps/scribeswell/web`:passed12.82s,existing bundle warning, before final guard-order correction. |
| 05-extended-boundary.log | `workspace-restoration.spec.cjs --workers=4 --fully-parallel --grep 'note response boundary'`:10 passed,13.7s, before malformed-marks refinement. |
| 06-mark-shape-red.log | `workspace-restoration.spec.cjs --workers=1 --project=desktop --grep 'rejects unreadable direct reads'`:one genuine failure; malformed JSON marks object was coerced before primitive validation and escaped the typed error. |
| 07-boundary-final.log | `workspace-restoration.spec.cjs --workers=4 --fully-parallel --grep 'note response boundary'`:10 passed,13.2s, after evaluation-order correction; page-envelope coverage added afterward. |

The new server-valid compatibility case validates representative format1/2 values
through actual Python NoteValue before passing them through both browser read adapters.
It proves mixed Hebrew/supplementary scalars, marks, lists, external URLs and canonical
passage links remain readable. Negative cases exercise actual intercepted HTTP values,
including malformed documents, inline/list/reference structures, revisions and page
containers. Actual ordinary/restored outline cases prove error/recovery without a page
exception. A dirty restored-note case preserves text and the original unknown-save
request across failed outline reads and successful Retry.

## Boundaries and impacts

No backend/SQL/migration, Access/Identity implementation, owner-service/live signup,
physical-device/session, provider configuration, KDG55481/55482 or release operation
ran. Browser component evidence is separate from final integration. The existing
restoration L1-E1 defer is the source of this correction; its old entry is retained.
Application-specific implementation stays in Scribeswell. No shared UI/scaffold,
agent context, accepted ADR or generated contract change is needed.

## Independent review and correction

Configured oneshot blind review completed; six individual verdicts appear in the
implementation spec. Five direct corrections were accepted, one claim that pending
status was already inaccurate was refuted. Raw findings/provenance are retained.
Budget checks now terminate during traversal, nested chapter/range reference models
count toward the same2048-node bound, and IDs are canonical nonzero lowercase UUIDs.
A real editor-opening failure/retry proves another shared dirty note stays intact.

`09-review-counterexamples-red.log`: genuine malformed-page ID failure; its budget
case failed at OS argv E2BIG before testing behavior. The fixture uses stdin now.
`10-reference-budget-red.log`: genuine browser acceptance of reference-nodes2049
while actual server DTO validation rejects it. `11-review-patches.log`:16passed20.5s;
`12-build-review-patches.log`:build passed10.05s. Added range-point budget coverage
and an early marks-array cardinality guard, then `13-review-final-focused.log`:
16passed22.0s; `14-build-final.log`:build passed9.33s,existing bundle warning.
The final focused command is the prefix above plus
`workspace-restoration.spec.cjs --workers=4 --fully-parallel --grep 'note response boundary'`.
The marks-length/early-traversal guards are audit-directed; no dedicated pre-fix
behavior red is claimed for them.

The first affected regression stopped normally before source corrections:
184passed/4interrupted/1expected native skip/553notrun,4.7m,exit130. Its166-file
before/after manifests match SHAdebdfedd3abd4cbf59fed722d4f8eeb291a8ae0d57f9f4574e84910ffb916f33.
An initial exact process-name search found no matching CLI and sent no signal;
the subsequent owning-runner descendant match sent normal SIGINT only to its
Playwright CLI. Final corrected regression02 is running, not yet qualified.
Exact command and source manifests accompany each parent run. No whole-browser
run is claimed for this correction: the two affected Notes/restoration suites
are the chosen regression scope; unrelated public reader/lexicon/account-entry
suites retain their prior checkpoint evidence.

## Final evidence and unresolved broader observation

`parent-affected-regression-02/parent-full-run.log`: exact recorded command runs
both Notes/restoration files with4workers/fully-parallel;746registered,
743passed/2expected native skips/1failure,16.4m,exit1. Failure is the existing mobile
last-public-scroll test: its first native-anchor assertion remained at verse3.
The raw failure context is retained byte-for-byte beside the log, SHA256
a4f90441c6b06be01b534e9d2919060b9052d1dceb5ae2ebf5dc83bd6d915bb8.
No new Notes boundary case failed. This anonymous test does not execute the changed
Notes read/URL guards; the underlying cause is not established.

`15-unchanged-scroll-diagnostic.log` retains12mobile repeats with the original
gesture/assertions and selected safe geometry diagnostics: all12passed21.0s,
loaded fonts/device readiness and actual scrollTop350. These passing observations
do not explain the original failure. Diagnostics were removed; original test
bytes were restored from the delivery baseline, without changing expectations.

`parent-final-targeted/parent-full-run.log` records exact final command: owning
browser prefix plus `--workers=4 --fully-parallel personal-notes.spec.cjs workspace-restoration.spec.cjs --repeat-each=2 --grep 'note response boundary|last public scroll checkpoint|rich paragraphs|editor toolbar actions|invalid DNS link'`:
48passed1.2m,exit0. Both parent runs have identical166-file before/after/current
manifest SHA1b10e1a3fcd202a38f2c803949b5a4d7e9fdcffe155a732c82bada7736fe07a4.
Final build is14-build-final.log,9.33s,existing bundle warning; runtime is unchanged.
Authored source/docs whitespace check passes; byte-exact raw logs are not normalized.

The original malformed-note defer L1-E1 is addressed. All6 independent-review
findings have individual verdicts: five direct fixes and one false pending-status
claim. An additional medium-if-confirmed public-scroll investigation remains
unverified and deferred, with broader suite qualification open. Capture bootstrap,
painted geometry, gesture delivery and current entry during an actual failure to
settle it. No failing expectation was weakened, and passing repeats do not erase
failed/interrupted chronology. Final native/owner/session/device/signup/release
acceptance remains separately gated.
