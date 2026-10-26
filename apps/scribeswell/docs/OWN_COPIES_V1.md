# Independent own copies v1

This app-owned opt-in implements independent private copying and conflict recovery.
It changes no shared scaffold, UI package, agent context or accepted ADR. Native SQL,
owner integration, production activation and release qualification remain gated.

`POST /api/studies/{study_id}/notes/{note_id}/duplicate` is `note.duplicate`,
with `{operation_id,expected_revision}`. Destination is the same own study.
`POST .../conflict-copy` is `note.conflict_copy`, with
`{operation_id,base_revision,value}`: the complete frozen local branch, never an
automatic merge. `POST /api/studies/{study_id}/copy` is `study.copy`, with
`{operation_id,expected_revision}`. The exact title is retained; duplicate titles
are valid. All commands return the standard operation acknowledgement naming the
new destination and support the existing original-command operation lookup.

Current account Access completes before private transactions. Receipt reconciliation
precedes source validation; acknowledged retries validate the independent destination.
The active own source parent is locked before its children. All child writers use
that parent lock, yielding one coherent snapshot, including every active own note
and ordered passage entry. The whole copy is refused above 128 notes, 200 passages
or 2097152 canonical UTF-8 aggregate bytes (title, notes with visibility/value,
and passage references). `copy_limit_exceeded` is a safe 409; no partial success.
Unsupported source visibility/kinds fail with `note_format_unsupported` (409).
New notes, connections, highlights and passage entries receive fresh UUIDs; exact
content, anchor source identities and colours survive without corpus reobservation.

Conflict branches preserve their original base revision. Immutable server metadata
validates unchanged highlight ID/anchor pairs; new/repaired anchors need fresh actual
public observation before private locks. Missing rich base metadata returns
`note_base_unavailable` (409), retaining input. Legacy branches without historical
anchors need no invented history. Current source ownership/lifecycle always rechecks;
metadata cannot revive a deleted source. Proof failures retire their attempt; unknown
outcomes retain the exact frozen operation/payload. All destination values, revision
metadata, provenance and receipts commit or roll back together.

Immutable provenance has destination composite owner/study/note keys, relation,
immediate source account/study/note IDs, bounded original-origin IDs and server actor
and UTC creation attribution. Study provenance has no note IDs. Source IDs are opaque:
no source foreign key, cached title/body/email or chain. A copy of a copy retains
original-origin credit. Labels resolve only through current authorized app reads;
otherwise presentation says Original unavailable. Source deletion cannot delete a
copy. Only supported `study` note visibility is copied; no response creation or
sharing capability is introduced.

Review latest reads a separate full current aggregate; local writing remains intact.
Use latest explicitly replaces the shared lane. Save mine freezes the branch/base
and opens its acknowledged new note only while the original account/tab/navigation
and input generation remain current. Changed origins use Open created recovery.
Duplicate confirms pending source saves; study copy confirms every pending note lane
and refuses unresolved/invalid/conflicting input. No consequential copy runs
automatically following reauthentication. Reader positions remain independent.

The browser transport accepts at most `50*262144+65536` response characters,
covering a declared maximum note page plus bounded attribution/envelope. Existing
50-row, per-value262144-byte, document and aggregate guards still reject invalid
responses. A larger list allowance does not expand the2MiB whole-copy limit.
