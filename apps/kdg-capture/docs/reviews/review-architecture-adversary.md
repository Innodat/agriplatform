# Adversarial divergence review — KDG Capture

Date: 2026-10-12. Scope: offline queue, ownership, history, sessions and privacy across architecture/PRD/EXPERIENCE/discovery. No implementation or shared-contract edits performed.

## Verdict

The proposal avoids the obvious unsafe shortcuts: no offline bearer authority at the server, no replacement-account submission, no silent last-write-wins, no generic API response cache. It needs explicit sequencing rules for conflict descendants and an authoritative local access renewal definition before those stories are build-ready.

## Findings

- **high — A resolved conflict can be undone by its queued descendants (AD-5/6).** Reproduce: offline edit A queues against server r1; later edit B queues behind A; A conflicts with administrator r2; user reviews A and chooses server or replacement C. The rule supersedes the conflicted command but does not say what happens to B. Automatically giving B the resolved revision would immediately overwrite the reviewed state with an unreviewed older proposal. *Fix:* include every descendant local edit in resolution, or explicitly quarantine/supersede the descendant chain after preserving it. Never merely rebase descendants to the new revision. Resolution must atomically establish the new queue/head and retained evidence.
- **high — Partial online authorization may extend stronger cached local rights (AD-7).** Successful history read must not refresh a formerly authorized administration/create capability or stale assignment observation. *Fix:* bind renewal to the observed capability/assignment set and explicit validity; specify complete setup renewal versus partial refresh and denial effects. The seven-day duration is agreed; this finding concerns its renewal semantics.
- **medium — History refresh may erase pending edits (AD-4/5/8).** A server download during reconnect must not replace the authoritative local unsynced snapshot or conflict base. *Fix:* separate baseline from pending overlay and apply revision-aware reconciliation before UI/status updates.
- **medium — Multiple browser contexts may race local queue processing (AD-5).** Two reconnect handlers can choose different successors unless queue claims and local acknowledgement compare operation/head/session generation atomically. *Fix:* declare local claim ownership/recovery and stale-response handling beyond account-generation checks; test two tabs and interrupted drainer recovery.

## Privacy and session assessment

Account/org partitioning is appropriately distinguished from protection against device access or same-origin malicious JavaScript. Dedicated origin and shell-only caches reduce accidental disclosure; do not market locked IndexedDB as encrypted data. Business history remains protected content, not operational logging. Role-loss behavior safely blocks affected content and retains pending data, but pilot approval still needs device suitability/history retention/download bounds as already recorded. No extra authentication service, employee directory, export recovery shortcut or platform permission bypass is warranted.

## Gate disposition

Resolve the deterministic queue/download/renewal seams in the application architecture/contract before affected story readiness. Keep owner acknowledgement, saving classification, assignment policy, retention and actual package/provider validation as explicit unresolved gates. These findings do not require finished application code or all Leave planning to pass now.
