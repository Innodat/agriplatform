# PtS Studio — design direction

Status: a reviewable design study, not a deployed application. Open the
[interactive concept](../data/interim/pts-studio-design-v1/index.html) to compare
**Evidence first** and **Review first**, switch between the four Psalms, and try
language/prompt composition. All prototype inclusions are explicitly simulated;
they do not approve research or call a provider.

## Recommendation

Use an evidence-first reading desk: a compact observation queue, a large source
page and a focused claim/review panel. Offer a review-first arrangement for the
editing stage. Keep source review, language/prompt preparation, and draft comparison
as three separate views of the same Psalm project.

The current problem is semantic fragmentation, not just visual styling. The new
[file review workflow](../data/interim/guide-review-items-v2/index.html) is the
working baseline: 85 proposed items from 379 fragments across the four supplied
image guides, with connected footnotes and editable category defaults. The other
21 guides still need comparable curation. No human approval has been inferred.

## Patterns considered

| Reference | Relevant pattern | PtS adaptation |
| --- | --- | --- |
| [Hypothesis annotation basics](https://web.hypothes.is/help/annotation-basics/) | Notes attached to selected source text, accessible beside the document; tags and search help navigation. | Keep the source and its interpretation together. The queue is organised by Psalm/verse, not by extracted paragraph. |
| [Label Studio labeling guide](https://labelstud.io/guide/labeling) | Task-oriented annotation with predefined choices and correction of suggestions. | Prepopulate categories and proposed claims; let the reviewer correct them. Avoid a blank form for every fragment. |
| [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/#fragment-selector) | A body can target a specific part of a source; selectors represent image regions and text spans. | Store verse and footnote regions as multiple targets for one observation, alongside source checksums. A source highlight is not itself an approved interpretation. |

These are design references. Adopting their interaction patterns does not require
adopting those products or a new annotation platform. The recommendation below is
an inference from those patterns and the observed Psalm-guide layout problems.

## Two layouts to compare

**Evidence first — recommended for interpretation.** Give the PDF/image most of
the available width. Selecting an observation reveals its concise claim and shows
the verse and footnote regions together. This suits Hebrew layout, colour patterns
and checking alternative readings. Allow the reviewer to enlarge or collapse the
claim editor without losing their source position.

**Review first — useful for editing.** Give the claim and linked evidence text more
space while keeping the source beside it. This suits wording revisions and moving
through already-inspected observations. It is the layout used by the working file
reviewer. Do not require users to reopen a PDF in another window just to check a note.

Both arrangements use a quiet cream/green palette, restrained serif titles and
legible sans-serif controls. Source colours retain their original meanings; UI
status colours must not masquerade as guide annotation colours. Labels accompany
status dots. Keyboard focus and a stacked narrow-screen layout are required.

## The observation is the review unit

Each observation has a stable identity and revision, Psalm applicability, verse
references with numbering convention, title, editable category, proposed claim,
alternatives, source targets, preparation provenance and explicit review decisions.
A source target includes its PDF page and image revision, verse/footnote label and,
when captured, a region or text selector. One observation can cite multiple pages.

A heading, isolated marker or colour legend is context. A lexical observation and
an independent stanza claim can be separate decisions even if they concern the
same verse. Footnotes can support more than one observation when that relationship
is explicit. All source fragments remain accounted for in a coverage audit.

Suggested primary categories include word meaning, imagery, ambiguity, grammar,
parallelism, repetition, sound, wordplay, speaker/addressee, discourse, emphasis,
structure, refrain, inclusio, chiasm, genre, cultural context and theological terms.
Use one primary default per observation, editable with a custom value where needed.
A classification is never an approval or a claim of scholarly certainty.

## Source and review view

The queue shows verse, concise title and review status, with search and filters.
The focused card shows a proposed claim, category and type, related footnotes,
competing readings and reviewer notes. Source controls switch among supporting
pages, zoom into verse/footnote regions and open the original image.

Approval applies to the exact claim/evidence revision. Editing a decided claim
returns the edited revision to pending; preserve prior signed decisions in history.
Keep rejection, disagreement and context-only decisions distinct. A note explaining
rejection/disagreement is required; approval does not require repetitive boilerplate.
Avoid global approve-all. Later, allow carefully selected bulk decisions only with
a clear list of included revisions and the same audit trail.

The current file workflow supports Save work, Load work and Export decisions.
In the Studio, autosaved drafts should show save state and authorship. Concurrent
edits require conflict detection, not last-write-wins replacement of reviews.

## Language and prompt view

Keep source observations independent of target language. A language brief records
language, audience, register, output purpose, translation constraints and translator
instructions. The design study includes Afrikaans, English, French, Portuguese and
Swahili to demonstrate selection; it does not claim language-specific validation.
The prompt's instruction language and its target output language are different
settings; translating every source note is not a prerequisite for target selection.

The production evidence picker offers only approved, applicable, current revisions
from Appendix B/C. It lists why an observation is unavailable (pending, disputed,
wrong Psalm, changed evidence, or outside scope). The exact selected claims, source
references, Hebrew representation, language brief, system instructions, provider,
model and settings are frozen into a new prompt/run revision before generation.

Show the assembled prompt, not an opaque Generate button. Allow a translator to
edit their instructions, while changes to evidence claims return through source
review. Preserve the current engine's requirement for an eligible approved PDF
principle in condition D. Do not silently include the excluded page-17 checklist.

## Drafts and collaboration

Compare actual drafts by verse, with linked decision notes, losses and uncertainties.
Keep translator edits and evaluation separate from model output. A review or draft
comment identifies its author and target revision. The assistant and browser must
use the same structured records/API; neither should depend on replaying UI clicks.

The prototype's draft screen is an honest empty state. It does not invent a model
run, reviewer score, real-time collaborator or approval history.

## Delivery boundary

The current delivery fixes file review and supplies a design study. A next Studio
slice would integrate these records into Scribeswell's React interface and a thin
API over the poetry engine. Retain JSON exchange and immutable exports. No parallel
annotation database, vector search, separate generic workflow, shared-platform
components or accepted ADR changes are justified by this prototype.

Before expanding the UI, try one real review session on Psalm 23: inspect note 12,
edit a category/claim, save/reload work, approve a reviewed item, and inspect its
export. Then check Psalm 1's Flower Garden and the numbering differences in Psalms
42–43. The next milestone is useful reviewed evidence and a traceable prompt, not
merely a larger catalogue of pending records.
