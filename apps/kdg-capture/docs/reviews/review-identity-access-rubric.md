# Identity/Access execution substrate rubric review

2026-10-14. Independent bmad-architecture reviewer-gate rubric walker.

**Verdict: one medium planning clarification required before final closure.** The
selected tables/lifecycle/role boundaries are coherent, but initial organization
grant assignment needs an explicit pre-grant target-verification path and caller
privilege. This does not require restarting product discovery or implementing code.

## Scope

Reviewed the Identity/Access execution substrate against the shared KDG addendum,
canonical Access/person/account distinctions and retained actor/membership lifecycle.
The sole owner's acknowledgement remains settled. This review does not claim live
database inspection, migration rehearsal or restricted-role execution. The documented
PUBLIC get_user_roles correction is source/adoption evidence, not an inferred live ACL.

## Rubric assessment

| Dimension | Assessment |
| --- | --- |
| Durable actor separation | PASS. Auth profile and durable actor are distinct; account-kind mapping prevents service actor misuse; legacy verified IDs are preserved; unknown attribution blocks activation instead of invented backfill. No synthetic accounts or permission derived from actor existence. |
| Membership lifecycle | PASS. Active uniqueness plus immutable retained IDs prevents silent rejoin resurrection. Retirement is one-way; delayed commands bind exact old membership/revision; joins require predecessor history and allocate new membership. Roles/grants are not copied. |
| Access physical scope | PASS. Permission scope is capability-local. Organization grants retain opaque legacy identifiers; account grants do not require an organization. Admission is distinct from grant. Missing/unmatched membership/actor rows do not become effective during adoption. |
| Current checks and target isolation | PASS for ordinary reads and post-grant assignment verification. Actor absence is handled after admission/authority; target list eligibility is filtered before keyset page limits; target-specific pool/NOLOGIN owners cannot expand normal user check powers. |
| Operator trust | PASS for protected executor and command policy. session_user mapping is protected from operator editing; exact command/org/app/target authority is checked inside the local transaction. One initial grant-verification privilege/path remains under-specified (I1). |
| Constraint and routine safety | PASS at planning altitude. Local structural/FK/immutable guards, forced RLS, fixed definer routines, restricted search_path, explicit revocation/grant and pooled-context proof are selected. Actual roles/ACLs remain delivery acceptance. |
| Source adoption | PASS. Target equivalence, legacy writer characterization and documented privilege differences are migration inputs. Cascade/unique/index changes require coordinated compatibility or maintenance rather than assumed safe additive cutover. Existing Auth-backed legacy rows are retained. |
| Scope discipline | PASS. The substrate allocates ID-A/ID-B/ACCESS-A/B work and does not introduce People/Leave product behavior, a second Identity service, synthetic employment or KDG direct Identity-table access. |
| Planning versus delivery | PASS. Schema/command/privilege selection is distinct from installed migrations, ACLs, target runs and effective authority. WRITE outcome/evidence/secret details remain expressly delegated. |

## I1 — Specify pre-grant membership verification for Access owner commands

**Severity:** Medium. **Disposition:** Clear bounded contract fix before closing this
planning prerequisite.

`grant.assign` requires exact current target membership, including initial grants.
The KDG Access assignment-target wrappers require an existing effective create grant;
they cannot verify a target before that grant is assigned. Current-account projections
also do not resolve an arbitrary operator-selected account. The privilege matrix
describes Access command-owner local DML but does not explicitly give it the narrow
Identity target-membership projection authority needed to validate that initial target.

Specify a trusted pre-grant membership verification path: an owner-authorized exact
org/account/expected-membership Identity projection, restricted to an explicit Access
command-owner caller and the operator command's verified scope/target. It must not
depend on an existing KDG grant, reuse user impersonation, broaden ordinary runtime
target discovery or permit raw Identity table reads. Preserve local expected-state
guards and the selected short-transaction/cross-owner observation ordering. Include
a fixture for an active member with no KDG grant acquiring its first grant and
retired/replaced membership refusing it.

## Material accepted limits

The plan deliberately retains legacy Auth/profile/org deletion constraints; it does
not promise account deletion works during transition. Production get_user_roles ACL
history remains a source preservation assertion to compare against the actual target.
Unknown legacy grants/actors/writers require explicit adoption disposition. These
are coherent safeguards, not permission to inspect or modify production in planning.

The remaining WRITE record/evidence shapes and secret wiring remain separate gates.
No additional product requirements or universal permissions are needed for this review.

## Resolution recheck — 2026-10-14

**Final resolution verdict: PASS for this planning substrate. I1 is closed.**

The updated privilege matrix explicitly names access_command_owner as a NOLOGIN
definer with EXECUTE on the exact Identity target-account/member projection and
no raw Identity table authority. The pre-grant section now requires verified actual
operator command/org/app/target policy, protected owner-command context and the exact
account/member check before grant write locks. Identity verifies current org/profile/
actor/member without a KDG grant predicate. An eligible member can acquire its first
grant without using the post-grant assignment endpoint or bearer impersonation.
New/delayed execution rechecks and records its exact target/member evidence; a raced
retirement cannot silently substitute a replacement membership.

Associated closure fixes make user and setup target contexts/logins distinct, add
the immutable explicit entry-permission registration command, and preserve extra
owner-join authority rather than trusting a payload boolean. These remain coherent
with the selected narrow command scope. No installed role, effective grant, migration
or live target query is inferred from this recheck. WRITE and actual restricted-role/
clean-adopt/recovery evidence remain separately scoped work.
