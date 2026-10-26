# Workspace tabs — architecture seam review

Reviewed 2026-10-22 against the draft architecture spine, reader-interaction,
SPEC, UX, acceptance and canonical reference/save portions of data-and-saving.
Scope: independently implemented consumers of the approved tabs/four-pane direction.
No runtime or implementation-readiness verdict is implied.

**Verdict: tighten the draft in two navigation seams before consuming code.**
The main ownership choices are consistent: temporary public reading tabs, per-tab
study/current-note associations, one resource-keyed note lane, one tool surface,
explicit pane targeting and no private history snapshots. D-1–D-5 remain open.

## Findings

### 1. Medium — New URL shape cannot represent canonical range references

Evidence: reader-interaction.md lines 104–114 declares the multi-pane URL shape
`{book,chapter,verse?}`. data-and-saving.md's Canonical references section includes
ordered verse ranges with start and end, while ST-05 requires preserving both
endpoints. The history snapshot separately uses an unspecified canonical `ref`.

Independent units: a pane/picker controller retains the canonical range to satisfy
ST-05 and D-2; a URL encoder/decoder implements the closed D-4 URL object literally
and retains only its first verse. Each can follow its local contract and AD-12's
public-only constraint, yet sharing/reloading that layout loses the endpoint or
rejects the controller's reference object. This also leaves URL and history
validators using different reference shapes despite the stated single boundary.

Tighten D-4 to embed the same D-2 canonical reference object in both pane URL and
history entries, or explicitly define the lossless transport mapping. Distinguish
the selected reference range from a separate scroll/seek anchor. Add an ST-31
round-trip case for chapter, single-verse and verse-range references in several
panes, including reference-only text. This is a technical clarification, not a new
feature choice.

### 2. Medium — Capacity-blocked history restoration invalidates its own recovery

Evidence: reader-interaction.md lines 125–140 makes tab closure a pushed deliberate
navigation, but a blocked closed-tab replay tells the user to close a tab then Retry
and invalidates the pending restore on newer navigation.

Independent units: the tab controller correctly pushes one entry when a tab is
closed; the history controller correctly invalidates pending restoration on that
new navigation. The user follows the prescribed Close a tab / Retry path and there
is then no valid pending restoration to retry. A second implementation could exempt
the closure, producing different browser stack and stale-replay behavior.

Define one owner command for resolving a capacity-blocked replay: validate the
pending browser-entry identity, close an explicitly chosen tab with any applicable
note guard, and apply the pending snapshot without an intermediate push. Any
unrelated navigation cancels it. Alternatively choose another explicit coherent
recovery, but do not leave ordinary closure both invalidating and enabling Retry.
Specify the address-bar/layout mismatch while blocked and add a sequence test for
Back at capacity → close chosen tab → recover, plus Forward/new navigation while
the guard or pending restore is open.

### 3. Low — Aggregate replacement and shared-lane retention need one exit predicate

Evidence: reader-interaction.md lines 44 and 198 require an exit guard when changing
the edited note/study. Lines 87–93 instead use the last-live-editing-context rule for
tab closure; ST-33 says distinct notes retain independent lanes. It is not explicit
whether selecting note B in tab A drops A's reference to note A while tab B still
retains note A, or whether it is a global exit from note A.

Two implementations can retain the same resource lane yet differ on whether this
selection prompts, and on whether Switch anyway may discard a buffer still used
by another tab. The adopted no-loss invariant rules out actual data loss but does
not define the transition/refcount boundary clearly enough for independent UI and
save-coordinator work.

Apply the same last-reference predicate to note/study replacement and tab closure.
Define whether a hidden editor reference counts independently of current-note
association, and revalidate live references/account/lane generation before an
asynchronous exit decision releases anything. A shared lane must not be discarded
by a stale dialog after another tab attaches or edits it. Add the two-tab same-note
→ change one tab's current note case to ST-33/ST-34.

### 4. Low — New acceptance rows fall outside the Markdown table

acceptance.md has a blank line between ST-27 and ST-32. CommonMark/GFM ends the
table there, leaving ST-32–34 as pipe-delimited prose. Remove that blank line so
the new stable cases remain part of the requirement-to-test table.

## Boundaries that held

- AD-12 and the companions consistently supersede the old two-pane/per-pane-history
  proposal while preserving sequential chapter arrows.
- No tab creates a study/note copy, grants authority or stores private data in public
  URL/history snapshots. Account-generation invalidation covers all private lanes.
- Capacity handling forbids silently replacing an arbitrary reader pane or tab.
- Source loss/private-response independence, owner-local saves and notification
  ownership are unchanged by the new workspace layout.
- Proposed limits, URL details and layout geometry are expressly gated for D-4
  qualification; no new runtime stack, physical-device result or readiness is claimed.

All findings can be resolved within the approved direction. No additional user
permission or product-scope decision is needed for the proposed clarifications.

## Resolution recheck — 2026-10-22

Rechecked only the changed reader-interaction.md and acceptance.md passages after
the author applied fixes. **Verdict: all four findings resolved for this draft.**

1. URL panes now carry the same canonical `ref` as D-2/history, explicitly retaining
   inclusive range endpoints and keeping scroll anchors distinct.
2. Capacity recovery is now one explicit chosen-tab-close-and-restore command with
   no intermediate push. Save guards, pending-entry identity and editing generations
   are revalidated; unrelated navigation invalidates recovery. The contradictory
   ordinary-close/Retry dependency is removed.
3. A common last-live-context departure predicate now covers note/study replacement
   and tab closure, including asynchronous confirmation revalidation. Another live
   context leaves immediately and cannot have its buffer discarded by a stale action.
4. ST-32–34 now remain contiguous with the acceptance table.

No new product decision is required. This is a contract-coherence result, not browser
history, save-race or device execution evidence. D-4 still requires its stated
executable snapshot/closure qualification; all other readiness gates remain open.
