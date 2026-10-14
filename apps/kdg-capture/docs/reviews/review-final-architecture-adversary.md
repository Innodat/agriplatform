# Final architecture adversarial review

Reviewed 2026-10-14: ARCHITECTURE-SPINE.md and full contracts.md, including engineering closure, against platform ADR-0012/0019/0025/0028/0031 and current operation/error/security contracts. Planning only; no core/shared files changed or runtime checks performed.

## Verdict

Engineering closure addresses the significant earlier divergence risks. No critical/high finding remains. One medium operation-recovery wire ambiguity and two low consistency clarifications should be corrected before affected DTOs are finalized; acknowledged owner gates remain gates, not evidence of working shared APIs.

## Findings

- **medium — Outcome route lacks its command discriminator** (contracts.md:139, 352–355, 403–405, 645–648). The storage key deliberately includes command_type, so create and edit may legally reuse the same UUID under distinct command contracts. `GET /operations/{id}` exposes only the UUID, yet lookup is supposed to distinguish create/edit and apply their scopes. A compliant backend could select the first matching command; another could return unresolved/ambiguous, and the frontend cannot request the intended key. This can incorrectly settle a pending action against another receipt. **Fix:** define a required validated command_type discriminator on the outcome lookup, or bind lookup to a command-specific route. Validate the returned command_type/version and operation identity against the pending action; add same-account/same-UUID/different-command recovery coverage. Do not introduce a global operation service or change tenant/caller authority.
- **low — Conflict identifier spelling diverges** (contracts.md:156–158 versus :661). The API table declares `kdg_capture.capture_revision_conflict`; closure says `capture_revision_conflict`. Two independently implemented adapters could emit/recognize different stable IDs, contrary to ADR-0031. **Fix:** use the fully qualified identifier consistently or explicitly mark shorthand as prose only; keep the shared error envelope authoritative.
- **low — Earlier removal rule is broader than approved inactivity exception** (contracts.md:42–44 versus :527–536 and :628–634). “A queued command submitted after removal is refused” can be read as covering ordinary child deactivation, although the later amendment accepts verified prior-provisioned inactive-child captures under current authority. **Fix:** narrow the early statement to current permission/membership/assignment removal and link ordinary child inactivity to the explicit exception. This is document reconciliation, not a product redesign.

## Adversarial constructions that are prevented

- Reusing an operation with changed content: strict accepted field sets, JCS envelope including target and executor, versioned fingerprint, atomic receipt and unique caller/org/command key prevent silent payload mutation (ADR-0012). Algorithm/key lifecycle is explicitly gated; no encryption claim is made.
- No-op or lost response becoming a second edit: no-op retains revision without false audit; uncertainty retains original IDs and uses authorized lookup/retry. Trusted actor/time and immutable original owner remain separate from untrusted device captured_at (ADR-0025).
- Foreign/stale eligibility bypassing current access: opaque app-owned reference binds account/org/membership/child/creation context; current admission/create/assignment is rechecked. It deliberately proves prior provisioning rather than a phone Save timestamp. The seven-day local window and reference retention do not grant server authority (ADR-0019).
- Membership rejoin resurrecting old assignment: approved instance-renewal rule prevents it; exact shared instance representation/target evidence remains a declared owner gate. Do not demand a invented KDG representation or treat current legacy schema as sufficient.
- Server refresh erasing local work: immutable pagination order, filter/account/mode-bound cursors, monotonic baseline merge and retained pending overlays are explicit. Scan absence is not deletion evidence; only own phone records persist.
- Update stranding pending work: independent schema/command versions, conditional claims/acknowledgements, non-destructive versionchange transactions, update-first settlement and supported old producer/queue fixtures satisfy the intended ADR-0028 compatibility boundary. Unsupported work is retained; no per-release adapter is mandated.

## Remaining gates are appropriately honest

Shared Access union/caller/registry schemas, verified membership-instance/target evidence, operator binding, exact package pins and fingerprint sensitivity/lifecycle still require their owning delivery decisions. Their explicit pending status is not a new review defect or a reason to require finished runtime proof during planning. Readiness must reflect them before the affected Build stories.
