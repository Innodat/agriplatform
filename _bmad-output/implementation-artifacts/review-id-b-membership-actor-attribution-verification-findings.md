# Verification-gap review received from user

Received 2026-10-21. External independent review of the verification handoff.

### Replacing an adopted update actor lacks a denial check

- Changed surface: services/access/identity-migrations/versions/0015_membership_actor_attribution.py:23 restricts changes to membership actor references to identity_migrator.
- Impacted consumer or site: Ordinary service_role updates to memberships with populated updated_actor_id, exercised at services/access/tests/qualify_membership_actor_attribution.py:128.
- Existing test evidence: Regression gap: attribution_writes checks null-to-actor rejection at line 97 and populated-to-null rejection at line 135. After owner adoption sets updated_actor_id to other_actor, line 132 skips the nonnull replacement case. Repository-wide searches for updated_actor_id, attribution_writes, and qualification imports found no additional behavioral test covering an ordinary writer replacing one valid actor with another. The inherited retirement tests also lack this transition.
- Missing verification: Assert that service_role replacing populated updated_actor_id with a different existing actor raises identity_membership_actor_owner_required and preserves membership, revision, role and audit state.
- Demonstration: Replacing the update-actor comparison with a nullness comparison would still reject null-to-actor and actor-to-null transitions while allowing actor-to-different-actor changes. The behavioral checks read would pass; source-bound catalog fingerprints record the implementation rather than independently establish this transition’s authorization rule.
- Consequence: An ordinary writer could overwrite adopted last-change attribution without the checked behavioral verification detecting it.
- Disposition: patch — extend MembershipActorAttributionQualification.attribution_writes to attempt updated_actor_id=:actor after switching to service_role, when the stored value is other_actor, and use the existing reject helper to verify denial and unchanged state.
