---
title: 'Recover safely from malformed note read responses'
type: 'bugfix'
created: '2026-10-26'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
baseline_commit: '5d3bbbfd10ed3af447d787f7939810a67f3001c9'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** A successful Notes read can carry a malformed document through the typed browser adapter into the study outline, where preview rendering throws. The same unchecked values can reach an editor lane. This is the concrete deferred defect from workspace-restoration review L1-E1.

**Approach:** Reject unreadable note values at the existing application HTTP read boundary before attaching them to outlines or editor lanes. Reuse current response-invalid/Retry handling; retain authorized current selections and unsent writing. Cover ordinary note pages, direct note reads and restored outlines. Keep valid format1/format2 writing, lists, external and passage links unchanged. This is browser consumer protection, not a new server wire format, permission source or general schema engine. No Access/Identity implementation, native SQL/migrations, live services, KDG ports, Leave/factory, provider change, push or release activation. Existing dirty/concurrent work remains preserved.

</frozen-after-approval>

## Implementation Notes

- Read-only investigation chose a small oneshot correction: shared renderability guard for current note documents, extraction of unchanged editor URL checking, and api.note/api.notes response attachment checks. No intent gap or irreversible action; dirty main-tree continuation and technical choices are already delegated. No story/sprint key or Leave planning artifact applies.
- ATDD observed6 genuine desktop/mobile failures before runtime edits: direct malformed value accepted; ordinary/restored outlines crashed instead of showing recovery. Eight existing formatting/passage-atom cases passed. Separate6 rich/editor/DNS-link characterizations passed before extracting safeUrl.
- note-value.ts protects current rendering grammar, bounded lists/inlines/scalars and empty unsupported connections/highlights; it is not a duplicate complete server DTO validator. URL behavior is moved unchanged and reused by NoteEditor. personal-notes.ts rejects malformed note/page shapes before existing context owners attach them; no error copy, authority or retry protocol changes.
- First14 affected checks pass; expanded10 boundary/golden/dirty-lane checks pass. A concrete JSON marks object caused coercion before primitive validation; observed dedicated failing case, reordered guard, final10 checks pass13.2s. Build passed before that one-line correction; final owning build and affected Notes/restoration regression follow frozen source.
- Scaffold/shared-UI: application-specific response protection, no promotion/generator or shared runtime changes. Agent context and ADRs: unchanged. Documentation: owning evidence and canonical memlog/status; no server schema, migrations, release activation or live integration.


## Review Triage Log

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 budget check after whole block | low | Fixed grammar and4MB response bound limit allocation, but a malformed list traverses avoidable nodes before rejection. Direct patch checks budgets while visiting nodes/text, before proceeding to later descendants. |
| B2 nested passage nodes omitted | medium | Server document_budget counts PassageLink plus reference/target and range endpoints; current consumer counts only the link. Direct patch includes validated nested models so its numeric bound matches the authoritative budget; add server-backed exact-limit cases. |
| B3 note IDs only nonempty | medium | Notes pages can attach an ID containing query/path separators; callers interpolate it when opening the note. Direct patch validates existing canonical nonzero lowercase UUID identifiers at this boundary; dedicated malformed-page red first. |
| B4 direct editor failure lacks UI proof | medium | Existing UI cases corrupt page reads, not a direct note read when another dirty note remains live. Add ordinary editor-opening failure/correction with retained shared dirty lane/original operation. No new runtime navigation behavior. |
| B5 boundary tests absent | medium | Current positives prove formats/Unicode but not exact aggregate/collection boundaries. Add exact/+1 and Python DTO-backed document/node/reference/character cases; no schema or public API extension. |
| B6 running review/regression docs | false | Records accurately say review/regression are pending during review; no completed delivery is claimed. Final commands/results/dispositions are already the required completion step. |

All five retained findings have direct small patches and concrete reachable inputs;
no frozen intent, scope or owner change. First affected regression stopped normally
before edits to avoid spending a complete run on known-incomplete source. Preserve
its final partial counts and unchanged source proof; no broad passing claim.

- Review corrections: per-node/character early exits, nested passage-reference model counts and canonical nonzero UUIDs; malformed IDs and reference2049 budget had genuine pre-fix reds. Large golden fixture initially exceeded OS argv bounds; retained E2BIG failure and changed only transport to stdin before observing budget red. Server-backed exact/+1 cases cover256blocks/inlines,128listitems,16paragraphs/item,64external texts,2048aggregate/reference/range nodes and50000supplementary characters. Marks-length fence is audit-directed, not separately red-first.
- Direct editor-opening failure/retry retains a different shared dirty note lane and exact unknown-save request. Final16 focused checks pass22.0s; final production build passes9.33s (existing bundle warning). Frozen-source affected regression02 is running; no final passing claim yet. Initial742-case attempt was normally stopped before corrections:184passed/4interrupted/1skip/553notrun4.7m, unchanged166-source proof. No test expectation was weakened.


### Final verification and additional audit finding

- Public-scroll observation — maybe-false (underlying product defect, medium if confirmed), defer. Existing mobile anonymous scroll assertion failed once while all Notes boundary cases passed; no changed read/URL guard executes in that scenario. Twelve diagnostic repeats passed, not proof of original cause. Removed diagnostics and retained exact original gesture/assertions; final48 repeated focused cases passed on the identical166-source manifest. Full wider qualification remains open; raw failure context and investigation are retained, not dismissed.
- Completed affected run02:743passed/2expected native skips/1mobile public-scroll failure16.4m,exit1. This is not a clean affected-suite qualification. Final targeted command includes boundary, original scroll and rich-editor/link cases with repeat-each2:48passed1.2m,exit0. Before/after/current166-source SHA1b10e1a3fcd202a38f2c803949b5a4d7e9fdcffe155a732c82bada7736fe07a4 matches both runs. Build14 passed9.33s; authored whitespace check passes.
- Bounded Notes correction is done: all five independent-review patches verified, one false review claim rejected; additional unverified public-scroll investigation deferred. This status does not close broader suite or actual-owner/native/device/session/signup/release gates. No original expected result was weakened; no production or native integration ran.
