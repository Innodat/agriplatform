# Third-party source inventory (checked 2026-09-07)

| Source | Dataset terms | Software terms | Attribution / use |
| --- | --- | --- | --- |
| [MorphHB](https://github.com/openscriptures/morphhb/blob/master/LICENSE.md) | CC-BY-4.0; underlying WLC public domain | Check code separately if copied | Attribute Open Scriptures Hebrew Bible and its repository; identify transformations. Commercial use and redistribution permitted under the attribution terms. |
| [ETCBC BHSA](https://github.com/ETCBC/bhsa#license) | CC-BY-NC-4.0 | Repository LICENSE is MIT for software; it does not override dataset terms | Attribute ETCBC, VU Amsterdam; cite https://doi.org/10.17026/dans-z6y-skyh. Commercial applications require consent; upstream directs enquiries to German Bible Society. |
| Supplied Psalm PDFs | Unknown per document | N/A | Local research files only. Record title/author/page/hash; extracted principles require human review. Do not publish extracted full text or assume training rights. |
| Existing `scripts/hebrew.json` | Export provenance/version not recorded | N/A | Used to restore the existing DB. Engine uses pinned original MorphHB instead. Do not infer a verified upstream revision for the export. |

Pinned MorphHB and BHSA source files are intended to be tracked in Git with their
source manifests and notices. Extracted PDF full text stays in ignored local directories. No automatic
corpus download occurs in the translation pipeline. The fetch command records a
pinned upstream revision and hashes; it is for the stated local research use.
Permission for commercial reuse of BHSA or redistribution of the supplied PDFs is
not inferred. Original documents, imported facts and analytical proposals stay
separate. This is an operational source inventory, not a legal opinion.
