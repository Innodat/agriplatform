# Own-note highlights v1

Scribeswell owns this opt-in aggregate extension. Production activation, native SQL,
restricted-role, owner-service, release and real-device qualification remain gated.

Legacy values retain exactly document/connections/highlights with empty arrays.
The additive aggregate is `{format_version:3,document,connections,highlights}`;
document versions 1 and 2 retain their existing exact grammar. Connections are
`{id,reference}`. Highlights are `{id,colour,anchor}` with canonical nonnil UUIDs,
unique IDs per array and freely chosen uppercase `#RRGGBB` colours. Version 3 is
sticky even after removal; stored document2 cannot be replaced by document1.

An anchor is `{version:1,source_id,source_revision,catalogue_version,
versification_id,tokenization_version,segments}`. Each segment is
`{reference,start_position,end_position,observed_word_ids,verse_token_digest}`.
References are canonical supported single verses; segments form one continuous
single-book range in catalogue order. Interior segment boundaries include complete
verses. IDs are exact positive decimal PostgreSQL bigint strings, never converted
from browser numbers. All segments share the anchor's labels. Limits are64 marks,
128 connections,128 total segments,4096 selected IDs,262144 UTF-8 command bytes and
32768 JSON nodes; existing document limits and depth16 remain. Reject, never truncate.

Public verse responses add `anchor_evidence`, discriminated on ready/unavailable.
Ready evidence binds the canonical reference, source labels/revision, exact full-verse
digest and full ordered decimal-string IDs to actual words in one bounded read-only
repeatable snapshot. Optional publication lookup failures are isolated by savepoint;
text stays public and available. Unsupported/missing/stale proof is unavailable.

Fresh source observation finishes before private write locks. New or changed anchor
identity requires exact current revision, labels, digest, positions and selected IDs.
Unchanged anchors are compared structurally with trusted current/base-revision metadata;
colour/removal/writing do not require corpus availability. Replays reconcile before
requiring proof. Whole aggregate admission, note revision and immutable validated
reference/anchor metadata commit together. Metadata retains no historical note bodies.
`highlight_proof_unavailable` is503; `highlight_proof_invalid` is409. Both preserve
recoverable input and reject the whole aggregate. Existing Access, operation, ownership,
revision, lifecycle, deletion and document-format contracts remain binding.

The visible current own note is the sole mark destination across its passages/tabs.
Selection actions are Highlight, Add note and Add to study. Highlight names its note
and offers Change; absent destination requires explicit own-note selection/creation.
Add note creates a connected observation in Notes; Add to study collects containing
verses. No action quotes selected text. Ordinary inspection does not change the note.
Marks use freely selected colours, deterministic overlap by highlight ID, and remain
visible beneath lexical selection. Recolour/remove preserve writing. Changed evidence
suppresses precise paint and offers explicit reselect repair; unavailable proof never
implies deletion. Read classification does not mutate saved revisions or historical IDs.

Selection belongs to one account/tab/pane/navigation/source and destination; stale
origins cannot act. Desktop drag and Shift-click select continuous phrases. Touch
retains native selection/copy and uses reachable bottom actions/palette. Notes and
reader return preserve passage/position. Cross-pane selection is refused.

Search/outline use deduplicated connections, document links and segment references;
collected passages are independent. Scaffold/shared UI/agent-context/ADR impact: none;
this is app-specific and promotes no unproven shared pattern. Accepted ADRs are unchanged.
