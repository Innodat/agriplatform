# P3 source-editor reachability refutation

No runtime patch was made. StudiesContext editorLanes excludes abandoned lanes;
NoteEditor mounts BoundNoteEditor only from that list. Ordinary Switch anyway
therefore unmounts the source editor while the destination GET waits. There is no
interactive source editor to receive new typing/composition during that wait.

A same-task synthetic event characterization was started before parent clarified
that P3 came from source tracing rather than observed interaction. It was stopped,
removed, and is not reachability evidence. Its partial failed/interrupted log is
retained as review-abandoned-red.log, not a valid ATDD red.

The replacement normal-UI R8 holds the destination note GET, explicitly clicks
Switch anyway, verifies zero source editor/textbox DOM nodes, reconciles through
Recover note save while preserving the exact original source operation/payload,
then releases GET and observes destination selection without a second prompt.
R8 plus unchanged D3 pass4desktop/mobile cases,6.1s, in
review-abandoned-render-guard.log. No synthetic DOM input or runtime hook is used.

Parent310application/44affected/18review results remain prior-state evidence;
all runtime source is unchanged from those checks. P3 is false: its trace missed
the existing render guard. Parent owns canonical triage and checkpoint.
