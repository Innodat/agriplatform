# Final owner-contract reconciliation

**Adopted 2026-10-26:** Explicit user approval resolves the final candidate-review gate.
The approved choices are recorded in platform ADR-0064 and Leave ADR-0171. Earlier
pending-approval wording is historical; source/criterion bodies and dependencies unchanged.
Implementation is held for a new Codex session at the user's request.

**Date:** 2026-10-26. **Status:** Planning candidate complete for one consolidated review.
This is a targeted delta to the completed coverage pass, not a new product specification.

## The three remaining planning inputs

| Input | Selected candidate | Existing implementation owners |
| --- | --- | --- |
| Invitation and staged access | Exact account or once-bound recipient target; signed-in session plus fresh mailbox challenge; seven-day invitation, rotating resend/old-link rejection, thirty-day prepared approval and honest atomic stage outcomes | 2.6 owns invitation/mail adapter and membership acceptance; 2.9 owns prepared assignments/activation. Existing Identity/Access foundations supply account/operation/membership contracts. No E3 notification dependency. |
| Membership continuity | Preserve one active owner and one explicit protected Organization Administrator; no ordinary self-removal. Same services/access owner-local organization guard serializes every relevant membership/role writer. Owner flag grants no permission. | 2.10 retirement and guard; 2.2 assignment/revoke and 2.9 activation participate; 2.3–2.5 preserve protected built-ins. Existing restricted bootstrap/adoption recovery only. |
| Work/calendar arithmetic | Unique dated full/reduction/clock closure; clock closures require Advanced detail. Nominal civil-clock DST quota; exact half-minute amounts across consumers. Explicit initial UTC anchor and predecessor-zone transition boundaries eliminate circular current-time timezone selection. | 2.18 calendar, 2.19 profile, 2.20–2.24 effective selection, 3.7 duration, 3.18 accounting; actual E5–E8 consumers prove their integration. |

Authoritative candidate contracts:
- [Invitation and prepared access](../../platform/docs/architecture/contracts/organization-invitation-and-prepared-access.md)
- [Organization administration continuity](../../platform/docs/architecture/contracts/organization-administrator-continuity.md)
- [Work/calendar and exact minutes](../../apps/leave/docs/architecture/contracts/work-calendar-and-minute-precision.md)

## Targeted source and criterion judgments

2.6/AC01–08 already require recipient verification, explicit bounded expiry/resend,
concurrent acceptance/rejoin, original recovery and real provider proof. The selected
protocol supplies those missing inputs without an account/person merge. Fresh mailbox
verification is evidence for this one intended admission; the once-bound exact account
is the enduring target. Prepared Access approval is independently checked; onboarding
never creates automatic grants or employment. Known account invitations cannot be accepted
by another account, even with mailbox control. P-0057/0058 remain authoritative.

2.10/AC01–08 explicitly reserve last-owner/admin and self-removal policy before readiness.
The selected candidate fills that reservation. Inspection of the E1 ownership table
confirms both membership and grants belong to services/access, so continuity can be a
short owner-local transaction. It needs no People/Leave database access or external wait
under locks. Alternate operator writers must participate; browser-only checking fails.
No custom app-role name or is_owner flag creates authority. Provider-wide account loss
remains controlled recovery, not a guarantee of permanent external login availability.

2.18/AC01–07, 2.19/AC01–08 and 3.7/AC01–07 already require exact holiday/timezone/duration
rules. Nominal DST quota is an explicit candidate choice, not an inference that a net
schedule contains shift instants. Clock-only holiday information cannot be applied to
unknown net-only intervals. Unique dated closure records prevent duplicate-label double
subtraction. Exact 50% of 435 working minutes is 217.5. L-0103's whole-minute floor applies
to usable entitlement, not this duration. Earlier integer-only technical mappings in E3,
E6 and E7 are explicitly superseded by the exact MinuteAmount binding; counters/IDs stay
integers. The extra fixed-point fixture belongs to each real consumer, not a new ledger.
The earlier timezone applicability gap is now bound without restoring setup as an E1
lightweight-save prerequisite under L-0122.

## Size and dependency result

No story or Given block was added or removed by this delta. The existing 310 leaves /
1,564 edges /66 layers remain. 2.6 remains one invitation lifecycle with a narrow approved
mail adapter and existing authentication/membership primitives. 2.9 remains one prepared
assignment lifecycle using completed invitation/role owners. 2.10 adds a single local
continuity guard to existing retirement/assignment commands; it does not introduce a
distributed protocol. 2.18/2.19/3.7 remain separate calendar/profile/pure-duration outcomes.
Cross-consumer precision adapters are scoped to their actual consuming stories. No E5
story is reopened and no earlier foundation waits for future request tables.

All five impact decisions are in each owning contract. Existing scaffold/UI patterns are
proved/promoted with first consumers; agent rules remain sufficient; actual owner docs,
schema/client/permission evidence update with delivery. Accepted ADRs remain immutable.
The three technical choices require the single consolidated approval, not partial reviews.

## Hash and preservation evidence

The early register retains all 837 individual judgments and criterion hashes. Its 59
existing owning-contract bindings changed only because narrow candidate annexes were
appended; each records old/new hashes and scope. The reverse register has one such
existing authority binding plus explicit new bindings to affected owners. Both JSON
registers include exact hashes of the three new contracts and targeted manual judgments.
Old owning-contract bytes are exact prefixes of the new files. No source-unit body or
accepted ADR changed; the graph and all 1,757 criterion hashes remain unchanged in this
final delta, including the 230 E5 originals. This is document evidence, not a runtime PASS.
