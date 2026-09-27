# HebrewLexicon source audit — 2026-09-27

Source: https://github.com/openscriptures/HebrewLexicon
Revision: `21c9add13bc727d3a951361778e97e3ff7afd1ce`
Original XML, README and checksum manifest: `apps/scribeswell/data/hebrew-lexicon/`.

Read-only inspection of the pinned XML and existing `scripts/hebrew.json` found:

| Measure | Count |
| --- | ---: |
| Augmented identifier mappings | 9,299 |
| Lexical entries | 10,221 |
| Strong dictionary entries | 8,674 |
| BDB entries | 11,845 |
| Entries with explicit root attributes | 2,459 |
| Distinct root spellings | 1,840 |
| Imported word tokens | 306,785 |
| Imported distinct raw lemma strings | 21,070 |
| Imported noun/verb tokens | 220,605 |
| Noun/verb tokens mapping through AugIndex | 220,597 |
| Noun/verb tokens resolving to an explicit root | 179,976 (81.58%) |

These are source-coverage figures, not linguistic accuracy claims. Noun/verb eligibility was checked against OSHB morphology segments after the leading language indicator; proper nouns are included. Root resolution follows an entry's explicit `etym@root`, or a `type="sub"` parent link, with cycle protection. Root identity is the lexical entry ID, not the consonantal spelling. There are 2,458 `main` root attributes and one `single` root attribute.

AugIndex identifiers are compact (`1254a`), while the imported source preserves spaced suffixes (`1254 a`) and attached prefix markers (`c/l/4723 c`). No imported tuple contains multiple numeric lemma components. 5,977 tokens have no numeric lemma; these must not acquire a fabricated lexical mapping. Original values must remain unchanged.

Useful verification example: Genesis 14's מלך (Strong 4428) and Genesis 10:10's ממלכה (4467) share lexical root identity `haj`. Nehemiah 5:7's 4427b has the same consonantal root spelling but root identity `hah`; it must remain distinct. Hebrew/Aramaic entries also retain distinct identities.

BDB includes 3,952 reference elements, but not every reference is a clean collected OSIS location. Examples include malformed strings, aliases, verse-part suffixes, ranges, and Matthew/Luke references outside this collection. Preserve source text and only activate navigation for supported references; do not invent a target.

Attribution: Open Scriptures Hebrew Bible Project, CC BY 4.0. The original README notes that BDB is a work in progress and TWOT identifiers are references rather than transcribed TWOT content. Retain these notices in the integration.
