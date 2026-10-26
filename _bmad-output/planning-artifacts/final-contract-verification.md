# Final planning contract verification

**Approval closure — 2026-10-26:** Explicit user approval is recorded. CE complete and
SP planning-readiness PASS; official tracking validation valid=true, problems=[].
[Closing evidence](leave-planning-completion.md#executed-closing-checks) supersedes
the earlier pending-approval concern below. No implementation started; new session next.

**Date:** 2026-10-26. **Result:** PASS for the document checks below.
Formal implementation readiness remains CONCERNS for final candidate approval.

Commands actually executed successfully:

| Command | Result |
| --- | --- |
| `python3 /tmp/check-leave-final-contracts.py` | PASS: 310 nodes, 1,564 edges, 66 acyclic layers; all 1,757 registered criterion hashes match current story text. All story/source bodies from Proposed epic list onward are byte-identical to the before-status snapshot, including E5 originals. |
| Same contract check | PASS: all 1,219 exact source-unit hashes match current physical source text; all 115/837 earlier independent judgments and hashes are unchanged. Existing owning contracts retain their full original bytes as prefixes; targeted old/new/new-contract hashes match the registers. |
| Same contract check | PASS: exact 435/2=217.5, two halves=435, remainder=217.5; Advanced closure example=300 minutes; selected nominal-DST example=180 minutes and half=90. These check the documented arithmetic, not a runtime calculator. |
| `python3 /tmp/leave-final-verification.py` | PASS: twenty local links in the final package/new contracts resolve; graph physical story-line pointers refreshed; final-review handoff and pending implementation boundary consistent. |
| `git diff --check --` scoped to the affected planning documents, tracker/handoff and owning contracts | PASS, exit0, no output. |
| `uv run _bmad/scripts/resolve_customization.py --skill .agents/skills/bmad-sprint-planning --project-root . --key workflow` | PASS after using the approved uv execution lane; no prepend/append/persistent overrides or completion action. The readiness-only reference was read and assessed; no tracking generation. |

The temporary scripts are inspection aids, not installed application tests or another
delivery workflow. Their saved-register/hash/prefix comparisons test preservation and
navigation; the manual delta judgments are in final-contract-reconciliation.md. A valid
hash/acyclic graph alone does not establish semantic coverage. The earlier complete
source/criterion judgments remain the evidence for that separate finding.

The checker handles both numbered and unnumbered Given criteria and counts the saved
actual delivery criterion references. Historical amendment prose is preserved verbatim,
not silently promoted to an extra delivery node or used to erase an existing criterion.
No accepted ADR changed. No application/provider/browser/release test is claimed. No
code implementation, migration, import, email, grant/provider change, deployment or
commit was performed. Unrelated working-tree changes were left alone.
