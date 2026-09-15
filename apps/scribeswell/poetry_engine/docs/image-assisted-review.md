# File-based, image-assisted approval

Open [the current review index](../data/interim/guide-review-items-v2/index.html).

| Guide | Old fragments | Proposed review items |
| --- | ---: | ---: |
| Psalm 1 | 116 | 22 |
| Psalm 23 | 71 | 20 |
| Psalm 133 | 70 | 15 |
| Psalms 42–43 | 122 | 28 |
| Total | 379 | 85 |

These four guides were inspected using all 15 supplied images. Each image is
checksum-pinned and mapped to the PDF page(s) it contains; some show two pages.
Only Appendix B/C is used. Psalms 42–43 has no Appendix C in the supplied PDF.
The other guides have not yet received this visual curation.

Every item has an assistant-proposed title, verse reference, category, record type,
concise claim and linked evidence. All start pending. Categories are editable;
custom values are accepted. Competing readings are prefilled where identified.
The wording attributes interpretations to the guide and preserves uncertainty.

Footnote continuations are joined, and source images show their verse anchors.
For example, Psalm 23 note 12 belongs to the marked-word-order observation in 23:4.
Psalm 23 note 2 is printed as 22 in the source; the UI records both rather than
silently renumbering the source. Psalm 1's numbered Flower Garden commentary is
split into supporting notes, not one enormous decision. The source legend and
verse diagrams are supporting context, not claims to approve on their own.

All 379 original fragments are accounted for as support or context. The full
footnote text, raw source fragments and image paths stay in ignored local packets.
The checked-in specifications contain concise proposed summaries and source
selectors, not human approvals. No source image was edited.

## Review and resume

1. Choose an observation and inspect its linked footnotes and source image.
2. Correct the proposed claim, category, type or alternative readings as needed.
3. Enter your reviewer identifier and explicitly choose a decision. Approve & next
   records the selected item only. Rejection/disagreement needs a reason; approval
   does not need boilerplate notes.
4. Use **Save work** to download all edits, including pending items. **Load work**
   restores that file only against the same packet. Keep the downloaded work file.
5. Use **Export decisions** when ready to export your explicit decisions.

Editing a decided item resets it to pending. Nothing is submitted automatically.
This local file workflow does not provide server autosave or concurrent editing.
The extracted supporting text can still contain spacing/character errors: the
provided images are available for checking them.

```bash
uv run psalm-engine prepare-guide-items --packets data/interim/guide-review-bc-v1 --resources resources --output data/interim/guide-review-items-next
uv run psalm-engine export-guide-review --packet data/interim/guide-review-items-v2/psalms-23.json --decisions /path/to/psalms-23.decisions.json --psalm 23 --output data/interim/psalm-23-reviewed-items-v1
```

The first command regenerates proposals from the stored specifications; it does
not call a provider or automatically infer new analyses for the other guides.
The second verifies the packet, item/evidence fingerprints, PDF and image checksums,
source scope and explicit reviewer. It exports concise claims, PDF provenance and
a decision audit. Every supporting footnote/page is cited; raw source text is not
copied into prompt claims. Context-only decisions export an audit with empty claim
files. Psalm 42-only claims do not enter a Psalm 43 export, and conversely.

Old fragment decisions cannot silently apply to these new item IDs and hashes.
The old page-17 checklist approval remains outside the Appendix B/C scope.

## Studio design

After trying the working reviewer, open the [PtS Studio design study](pts-studio-design.md)
and its [interactive concept](../data/interim/pts-studio-design-v1/index.html).
The concept compares two layouts and demonstrates language/prompt selection using
clearly marked simulations. It does not approve research or generate translations.
