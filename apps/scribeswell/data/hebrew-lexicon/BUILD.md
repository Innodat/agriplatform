# HebrewLexicon reference artifact

`manifest.json` pins Open Scriptures HebrewLexicon revision `21c9add13bc727d3a951361778e97e3ff7afd1ce`, exact source URLs, byte lengths and SHA-256 checksums. `readme.md` and `NOTICE.md` preserve source attribution and CC BY 4.0 notices. BDB remains incomplete. This application transforms the XML into safe structured text; it does not provide contextual translations or audio.

From the repository root, build the checked-in snapshot:

```sh
python3 apps/scribeswell/tools/py/build_lexicon.py
```

To reacquire the exact pinned source bytes and rebuild (network required):

```sh
python3 apps/scribeswell/tools/py/build_lexicon.py --acquire
```

The builder validates all four XML checksums, rejects DTD/entity declarations and oversized input, and emits deterministic `lexicon.json`. Never hand-edit the generated JSON. It retains inline separators, safe language/direction nodes, ordered nested senses and parsed scripture references; rendering never inserts source HTML. The builder validates reference chapter/verse bounds against the canonical corpus and importer book metadata. References only become interactive when their OSIS book is present in the loaded Bible collection; navigation additionally waits for the requested verse to be present in the preview response. Malformed, unsupported and out-of-range references remain plain text, including the source’s Ezra 13:17 citation.

The artifact has 9,299 augmented identities, 5,897 with resolved recorded roots. AugIndex compact suffixes normalize to the import's spaced form (`1254a` → `1254 a`), preserving homonyms. Root resolution uses an explicit root attribute or a chain of single `sub` parent IDs; missing/ambiguous/cyclic paths yield no root. Root groups use lexical entry IDs, not Hebrew spelling. Only noun/verb morphology expands chapter highlights to roots. Other words and unresolved roots match the exact content lemma. Strong's definitions use the numeric base and may cover several augmented senses; the inspector labels this limitation. See [source coverage audit](../../docs/verification/lexicon-source-audit.md).

The FastAPI silo owns this immutable reference artifact. No database/login/hosting service was added. Supabase remains authoritative for occurrences: exact raw lemma variants identify imported words, fetched in stable bounded database pages; verse metadata joins use batches of 400 IDs, and the final response is bounded to 100 words (default 25). Counts explicitly separate words and verses. Common lemmas require several reads before paging; live measurements were ~0.15–2.54 seconds for 53–10,979 words, including the most frequent imported identity (853). A future indexed database read contract can optimize this without changing the public lookup semantics. Reference source text never substitutes for database occurrence counts.

Deployment includes this directory and the canonical `scripts/hebrew.json` used for raw lemma variant discovery. No migration or production write is required. Missing artifact data returns an unavailable dictionary state while chapter text, lemma fallback highlights and morphology remain available. Existing application authentication and protected-content routing are unchanged.
