Conduct a review of CONTENT.
Look for what's missing, not only what's wrong.
Compute your finding floor N from the diff file's size: N = min(floor(sqrt(kB) + 1), 10), where kB is the file's size in kilobytes. State the arithmetic in one line, then find at least N issues to fix or improve.
Output a Markdown list of findings only — no severity, priority, or ranking.
If the content is empty, stop and say so.
If you have zero findings, re-check and keep thinking; do not stop with an empty list.

CONTENT: the unified diff at 
<unified_diff>
diff --git a/apps/kdg-capture/docs/next-session.md b/apps/kdg-capture/docs/next-session.md
index b1c9a1e..b36a4c7 100644
--- a/apps/kdg-capture/docs/next-session.md
+++ b/apps/kdg-capture/docs/next-session.md
@@ -1,6 +1,20 @@
 # Resume shared ENV delivery after KDG planning PASS
 
-## Current ID-B increment — typed command retry identity, 2026-10-21
+## Current ID-B increment — staged membership actor attribution, 2026-10-21
+
+Revision15 adds nullable durable actor references, local RESTRICT FKs and guarded
+owner-only changes; populated creation actor is immutable. Legacy attribution/times,
+full uniqueness, active index and seeds stay. No automatic real adoption or membership
+command activation. See [Build and evidence](../../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md).
+Actual matrix PASS27.931s;921 affected tests and both composers PASS. Review is pending:
+fresh reviewer launch is blocked by host thread capacity. Resume the in-review Build
+and complete all three review layers before dependent work. After review, next is scoped
+retirement command evidence/outcomes, authorization and protected writer transition;
+account_actor.ensure has a separate live Auth/profile verification requirement.
+Preserve all failed frames/receipts/data/resources and concurrent work; no real-target,
+production/provider/access/deploy/pilot, reset/prune, Leave/editor or push.
+
+## Previous ID-B increment — typed command retry identity, 2026-10-21
 
 The existing owner helper now canonicalizes all four already-parsed command variants
 and prepares scope/executor/command/operation-bound outcome lock keys. Actor registration
diff --git a/apps/kdg-capture/docs/shared-prerequisites.md b/apps/kdg-capture/docs/shared-prerequisites.md
index 43e0bdf..1977658 100644
--- a/apps/kdg-capture/docs/shared-prerequisites.md
+++ b/apps/kdg-capture/docs/shared-prerequisites.md
@@ -276,3 +276,15 @@ Reviewed actual matrix PASS46.265s;846 affected tests/both composers PASS, three
 complete, no deferrals. Historical duplicates/rejoin remain unavailable on canonical14;
 owner commands/seeds/compatibility must be coordinated before full-constraint removal.
 Access/WRITE/server KDG and real-target activation remain gated.
+
+
+## ID-B membership actor-attribution staging — 2026-10-21
+
+Revision15 prepares the existing membership table with nullable durable actor references,
+RESTRICT FKs and guarded owner-only changes; populated creation actor is immutable.
+Legacy attribution/timestamps, uniqueness, seeds and existing runtime contracts stay.
+Unknown historical references remain null pending verified adoption, without inferred
+System actors. Changed owner backfill advances revision. This does not activate
+retirement/rejoin, Access/WRITE or server KDG; scoped owner commands/audit/outcomes and
+protected writers remain next. See
+[Build/evidence](../../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md).
diff --git a/platform/docs/architecture/contracts/identity-migration-ownership-inventory.md b/platform/docs/architecture/contracts/identity-migration-ownership-inventory.md
index 6ca3cf0..ed23f66 100644
--- a/platform/docs/architecture/contracts/identity-migration-ownership-inventory.md
+++ b/platform/docs/architecture/contracts/identity-migration-ownership-inventory.md
@@ -344,3 +344,14 @@ full unique constraint/index and all data/writers stay. Final replacement/rejoin
 coordinated owner-command/seed changes and release-recovery disposition; canonical14
 still forbids historical duplicates. [Evidence](../../../../services/access/ACTIVE_MEMBERSHIP_INDEX_EVIDENCE.md)
 records source-bound canonical versus isolated-index proof and remaining gates.
+
+
+## Bounded ID-B actor-attribution expansion — 2026-10-21
+
+Revision15 stages nullable membership created_actor_id/updated_actor_id references to
+the durable actor registry, RESTRICT FKs and owner-only field changes with immutable
+populated creation actor. Legacy attribution/timestamps remain; no inferred/automatic
+backfill, identity classification, owner command, seed transition or production adoption
+is claimed. Owner-verified updates retain evidence and advance the existing revision.
+See [Build/evidence](../../../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md)
+and [owner runbook](../../../../services/access/IDENTITY-MIGRATIONS.md#staged-membership-actor-attribution--revision15).
diff --git a/services/access/IDENTITY-MIGRATIONS.md b/services/access/IDENTITY-MIGRATIONS.md
index 6d32b81..36d423a 100644
--- a/services/access/IDENTITY-MIGRATIONS.md
+++ b/services/access/IDENTITY-MIGRATIONS.md
@@ -1536,3 +1536,34 @@ The complete active-index matrix is single-use after its committed concurrency f
 Preserve the winner and precommit/result witnesses; use fresh synthetic cases for another
 proof. An initial zero-members refusal is intentional rather than authority to reset,
 delete, adopt or replay a prior winner. Failed/uncertain runs retain all diagnostics/data.
+
+
+## Staged membership actor attribution — revision15
+
+Revision15 adds nullable created_actor_id/updated_actor_id actor FKs with RESTRICT to
+org_member. A new invoker trigger denies setting/changing them through ordinary writers,
+including legacy table-wide writers; only identity_migrator may populate them in this
+stage. Once nonnull, creation actor cannot be cleared/replaced even by that owner.
+Existing table grants still cover new columns, so enforcement is the tested trigger,
+not a claim that column privileges alone protect these fields. Its function inherits
+no PUBLIC or default-grantee EXECUTE; no new command-owner privilege is granted.
+
+No automatic backfill occurs. Legacy created_by/updated_by/timestamps remain intact;
+unknown authors are not assigned to System and UUID equality is not mapping evidence.
+Real adoption requires explicit verified account/service classifications, exact row/
+revision preconditions, disposition of unknown references and retained mapping evidence.
+Owner backfill is a controlled migration operation, not an API/startup task. Changed
+actor fields advance the existing revision once per update; equal values do not.
+This increment executes only rollback-only synthetic adoption with verified fixture
+actors. Production/real-target adoption and membership commands remain unapproved gates.
+
+The independent existing reference recorder uses
+`--record-membership-actor-attribution-reference` with private case
+membership_actor_attribution_reference. Root prepares the established fixture protocol,
+runs `tests/qualify_membership_actor_attribution.py --characterize` against canonical14,
+then the full source-bound matrix. Preserve historical references and every failed frame;
+no reset, automatic downgrade, Docker removal or new generic qualification system.
+[Build/evidence](../../_bmad-output/implementation-artifacts/spec-id-b-membership-actor-attribution.md)
+records exact commands/results and limits. Full uniqueness and existing seed behavior
+remain. Retirement still needs scoped immutable evidence/outcomes, authorization,
+server attribution/time, protected writers and typed scoped CLI recovery.
diff --git a/services/access/identity-migrations/identity_baseline.py b/services/access/identity-migrations/identity_baseline.py
index 91b16c6..27870c3 100644
--- a/services/access/identity-migrations/identity_baseline.py
+++ b/services/access/identity-migrations/identity_baseline.py
@@ -22,6 +22,8 @@ TARGET_REVISION = 'identity_0007'
 PROFILE_REVISION = 'identity_0008'
 LEGACY_ROLES_REVISION = 'identity_0009'
 TOKEN_HOOK_REVISION = 'identity_0010'
+MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION = 'identity_0015'
+MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 = '2204a3ca4323bf9693aacc5f4202d2aab1516ac395e71516df2d8f702298a715'
 ACTIVE_MEMBERSHIP_INDEX_REVISION = 'identity_0014'
 ACTIVE_MEMBERSHIP_INDEX_REFERENCE_SHA256 = 'b710b943ecb95e4b7cbce9eb77debad8f1ad181c40a2532ff87cd85be317033b'
 MEMBERSHIP_RETIREMENT_REVISION = 'identity_0013'
@@ -88,6 +90,8 @@ def compare_catalog(actual, expected):
         raise BaselineError('identity_catalog_mismatch:' + ','.join(changed))
 
 def trusted_reference(kind):
+    if kind == 'membership_actor_attribution':
+        return trusted_membership_actor_attribution_reference()
     if kind == 'active_membership_index':
         return trusted_active_membership_index_reference()
     if kind == 'membership_retirement':
@@ -189,6 +193,14 @@ def catalog_fingerprints(snapshot):
 
 
 def verify_catalog(connection, kind):
+    if kind == 'membership_actor_attribution':
+        verify_projection_role(connection)
+        verify_authority_roles(connection)
+        verify_command_role(connection)
+        verify_target_roles(connection)
+        verify_profile_privileges(connection)
+        compare_catalog(catalog_fingerprints(target_catalog_snapshot(connection)), trusted_membership_actor_attribution_reference())
+        return
     if kind == 'active_membership_index':
         verify_projection_role(connection)
         verify_authority_roles(connection)
@@ -348,15 +360,15 @@ def verify_legacy_history(connection, clean=False):
 
 def verify_owned_postcondition(connection, require_head=False):
     revision = verify_owned_history(connection)
-    if require_head and revision != ACTIVE_MEMBERSHIP_INDEX_REVISION:
+    if require_head and revision != MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION:
         raise BaselineError('identity_unknown_history')
     verify_legacy_history(connection)
-    verify_catalog(connection, {REVISION: 'owned', ACTOR_REVISION: 'actor', PROJECTION_REVISION: 'projection', ORGANIZATION_REVISION: 'organization', AUTHORITY_REVISION: 'authority', COMMAND_REVISION: 'command', TARGET_REVISION: 'target', PROFILE_REVISION: 'profile', LEGACY_ROLES_REVISION: 'legacy_roles', TOKEN_HOOK_REVISION: 'token_hook', MEMBERSHIP_BINDING_REVISION: 'membership_binding', MEMBERSHIP_RETENTION_REVISION: 'membership_retention', MEMBERSHIP_RETIREMENT_REVISION: 'membership_retirement', ACTIVE_MEMBERSHIP_INDEX_REVISION: 'active_membership_index'}[revision])
+    verify_catalog(connection, {REVISION: 'owned', ACTOR_REVISION: 'actor', PROJECTION_REVISION: 'projection', ORGANIZATION_REVISION: 'organization', AUTHORITY_REVISION: 'authority', COMMAND_REVISION: 'command', TARGET_REVISION: 'target', PROFILE_REVISION: 'profile', LEGACY_ROLES_REVISION: 'legacy_roles', TOKEN_HOOK_REVISION: 'token_hook', MEMBERSHIP_BINDING_REVISION: 'membership_binding', MEMBERSHIP_RETENTION_REVISION: 'membership_retention', MEMBERSHIP_RETIREMENT_REVISION: 'membership_retirement', ACTIVE_MEMBERSHIP_INDEX_REVISION: 'active_membership_index', MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION: 'membership_actor_attribution'}[revision])
 
 
 def verify_owned_history(connection):
     revisions = list(connection.execute(text('SELECT version_num FROM identity.alembic_version')).scalars())
-    if revisions not in ([REVISION], [ACTOR_REVISION], [PROJECTION_REVISION], [ORGANIZATION_REVISION], [AUTHORITY_REVISION], [COMMAND_REVISION], [TARGET_REVISION], [PROFILE_REVISION], [LEGACY_ROLES_REVISION], [TOKEN_HOOK_REVISION], [MEMBERSHIP_BINDING_REVISION], [MEMBERSHIP_RETENTION_REVISION], [MEMBERSHIP_RETIREMENT_REVISION], [ACTIVE_MEMBERSHIP_INDEX_REVISION]):
+    if revisions not in ([REVISION], [ACTOR_REVISION], [PROJECTION_REVISION], [ORGANIZATION_REVISION], [AUTHORITY_REVISION], [COMMAND_REVISION], [TARGET_REVISION], [PROFILE_REVISION], [LEGACY_ROLES_REVISION], [TOKEN_HOOK_REVISION], [MEMBERSHIP_BINDING_REVISION], [MEMBERSHIP_RETENTION_REVISION], [MEMBERSHIP_RETIREMENT_REVISION], [ACTIVE_MEMBERSHIP_INDEX_REVISION], [MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION]):
         raise BaselineError('identity_unknown_history')
     columns = connection.execute(text("SELECT column_name,data_type,character_maximum_length,is_nullable,column_default FROM information_schema.columns WHERE table_schema='identity' AND table_name='alembic_version' ORDER BY ordinal_position")).all()
     if [tuple(row) for row in columns] != [('version_num','character varying',32,'NO',None)]:
@@ -842,3 +854,19 @@ def trusted_active_membership_index_reference():
         or reference['migration_sha256']!=sha256((HERE/'versions/0014_active_membership_index.py').read_bytes()).hexdigest()):
         raise BaselineError('identity_reference_unavailable')
     return reference['active_membership_index']
+
+
+def trusted_membership_actor_attribution_reference():
+    """Independent helper-only fixture, retaining the full historical trust chain."""
+    trusted_active_membership_index_reference()
+    path=HERE/'membership-actor-attribution-reference.json'
+    if MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 is None or not path.exists():
+        raise BaselineError('identity_reference_unavailable')
+    content=path.read_bytes()
+    if sha256(content).hexdigest()!=MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256:
+        raise BaselineError('identity_reference_unavailable')
+    reference=json.loads(content)
+    if (reference['source_pins']!=json.loads((HERE/'source-pins.json').read_text())
+        or reference['migration_sha256']!=sha256((HERE/'versions/0015_membership_actor_attribution.py').read_bytes()).hexdigest()):
+        raise BaselineError('identity_reference_unavailable')
+    return reference['membership_actor_attribution']
diff --git a/services/access/identity-migrations/membership-actor-attribution-reference.json b/services/access/identity-migrations/membership-actor-attribution-reference.json
new file mode 100644
index 0000000..5d09f65
--- /dev/null
+++ b/services/access/identity-migrations/membership-actor-attribution-reference.json
@@ -0,0 +1,283 @@
+{
+  "_generated": "GENERATED by tests/qualify_identity_baseline.py --record-membership-actor-attribution-reference; change owning fixture/code, never hand-edit",
+  "membership_actor_attribution": {
+    "access_command_owner_target_dependencies": {
+      "rows": 2,
+      "sha256": "5f9d4db692ee8ad4321fad67baf196cc5c2e3f4679488d25f3627040fa2d5290"
+    },
+    "access_command_owner_target_memberships": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "access_command_owner_target_role": {
+      "rows": 1,
+      "sha256": "4f485b1a526e56f65f921c86fd7b55443deff71743cdf3b98dda8a0feee6d487"
+    },
+    "access_setup_target_reader_target_dependencies": {
+      "rows": 2,
+      "sha256": "5f9d4db692ee8ad4321fad67baf196cc5c2e3f4679488d25f3627040fa2d5290"
+    },
+    "access_setup_target_reader_target_memberships": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "access_setup_target_reader_target_role": {
+      "rows": 1,
+      "sha256": "b030aca1256b6d52c378ea4a4f4d2fa3e1ec32e6d4568269adef52b7ab7ac835"
+    },
+    "access_target_reader_target_dependencies": {
+      "rows": 3,
+      "sha256": "13527b38e516c0ab947cda4ac1755e5df2b9bc1944dbad62d7c13bed3e5cd7bd"
+    },
+    "access_target_reader_target_memberships": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "access_target_reader_target_role": {
+      "rows": 1,
+      "sha256": "077cf5d919556a83b16d4e273ec929c60355917b48a0a37371fccdd820b09ee2"
+    },
+    "authority_dependencies": {
+      "rows": 15,
+      "sha256": "5cc09a7548d2d74d7f70284f2d899a05ca184fc067fd5e85029ecad47b472882"
+    },
+    "authority_effective_columns": {
+      "rows": 944,
+      "sha256": "60ae68bdfeb68f76ab8a5c6fd1bdcc0f6991704937fd6ffd95cb440918c7884c"
+    },
+    "authority_effective_functions": {
+      "rows": 50,
+      "sha256": "634edbc9e4cef818fc0a92de99b21548647a17810f18495e2ef4c9ba7be38660"
+    },
+    "authority_effective_schemas": {
+      "rows": 4,
+      "sha256": "b1c64338c5309830ea1c30fed9299288a2ab39feda8596cf0c7db1dc76277d44"
+    },
+    "authority_effective_sequences": {
+      "rows": 18,
+      "sha256": "9a689940ee5acfed8b28b11773be7ef04704c87adf176d27c09a87ed91ae9a3f"
+    },
+    "authority_effective_tables": {
+      "rows": 168,
+      "sha256": "9946ddceab64e53d11d375bee0cab7337acfe40ad72113977dd4265094f11102"
+    },
+    "authority_memberships": {
+      "rows": 1,
+      "sha256": "aa5516814e024ed0e1bcb859391358f9f26e499118920e6c21e751f07c1ca4b6"
+    },
+    "authority_role": {
+      "rows": 1,
+      "sha256": "4ea45766c182d9eceb85f0d01b21edf3f3df65d2d1e1800eea5f483052395a5b"
+    },
+    "columns": {
+      "rows": 118,
+      "sha256": "0197bebb6a290cd284fe52775a51848d128fc96fe51ce0dd66471d74e0dc2175"
+    },
+    "command_dependencies": {
+      "rows": 14,
+      "sha256": "d000244767ffe56bac80872fe6833be6d5a43f8ca614d344117a4ac7f5c06f47"
+    },
+    "command_effective_columns": {
+      "rows": 472,
+      "sha256": "932310b70ff2469b15a72b1c8e4e73e6731983c179ff80962941d66eddb62b62"
+    },
+    "command_effective_functions": {
+      "rows": 25,
+      "sha256": "c10843e97c39e2d77f3b336540f1712a5b14cdbed9714455de05b1e746c29d0b"
+    },
+    "command_effective_schemas": {
+      "rows": 2,
+      "sha256": "063477e8c1c1a9766e331d04f9e3d8a05963b6b052abd898eaee1953b83433c9"
+    },
+    "command_effective_sequences": {
+      "rows": 9,
+      "sha256": "dfa797a9a0ff3dee2449c1913e59ae2f9f0b58ec875e463e9009d6ea5c118972"
+    },
+    "command_effective_tables": {
+      "rows": 84,
+      "sha256": "37831cbad7ec7840ab82f3d22cbd9ab96042fc329ed550ecc7a5da53e96d05b4"
+    },
+    "command_memberships": {
+      "rows": 1,
+      "sha256": "fd41016be965c704c0061cb7f11fc260cf439c4a120894d65daf128db6e03e9e"
+    },
+    "command_role": {
+      "rows": 1,
+      "sha256": "d0eaff8d252869eacf45e8c844bed6787a7d31b7cf15221c69429dd8d5c873f1"
+    },
+    "constraints": {
+      "rows": 99,
+      "sha256": "629e204606ba6ef4f567e68427be0527f474a70690d9a504fa173bf5bf448dee"
+    },
+    "default_privileges": {
+      "rows": 1,
+      "sha256": "2a3ef87e3dad4e6693b3400be9b49ee020cabad58257ec0c1774f4d5b4ec9ed3"
+    },
+    "effective_columns": {
+      "rows": 2832,
+      "sha256": "df4c68836b42efe5a07b891bdd0dbf843e2f1fd4dded72e0a2e17f6fa04e1243"
+    },
+    "effective_functions": {
+      "rows": 150,
+      "sha256": "f47b651eaff2a0c9c30f260dab5545bda67ae3fd137a9285f5cdc01ec25c76fa"
+    },
+    "effective_schemas": {
+      "rows": 12,
+      "sha256": "f136cffb060cff1ae0abc131e0078bc3d90817df1009acabdd2df3be298bf1ca"
+    },
+    "effective_sequences": {
+      "rows": 54,
+      "sha256": "2da85df381a92f9aa48309713eb7fb2f08b61299accc5c06d79cd30d97b8b0a6"
+    },
+    "effective_tables": {
+      "rows": 504,
+      "sha256": "335e36cad814b379e6d85c9b7a2beee62e3412067797c41e85cdb1c6e950fc95"
+    },
+    "enums": {
+      "rows": 38,
+      "sha256": "efb94af72df341a4bc235f743696a2ab62054cc622f6a3a453e524b39c128072"
+    },
+    "functions": {
+      "rows": 25,
+      "sha256": "847b6d85c7d2c90223a682e44809d7e39fe22a13868229600d6a0484dfdf11dd"
+    },
+    "identity_target_projection_owner_target_dependencies": {
+      "rows": 19,
+      "sha256": "5aad55f9aa3487a80adffae4e9158d4043519c24528b78435d28e3152998dfa5"
+    },
+    "identity_target_projection_owner_target_memberships": {
+      "rows": 1,
+      "sha256": "3b58c7002cf703639b5cf52a1ba4859e6fb9a37cb780d74bf4b4728a76710ccf"
+    },
+    "identity_target_projection_owner_target_role": {
+      "rows": 1,
+      "sha256": "d9eda7ebdc664014e54c2560f3e08785759b8b42ac474eebd0b82275071e927e"
+    },
+    "indexes": {
+      "rows": 25,
+      "sha256": "2d16c8c3076aaee6423d9b44a48971319ad8a9db9d5ca0a1683fe943e12adc01"
+    },
+    "operator_dependencies": {
+      "rows": 4,
+      "sha256": "204340830ff7cdc926f601fa73b2f6bebf4ac3da542708166d98d643526582dd"
+    },
+    "operator_memberships": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "operator_role": {
+      "rows": 1,
+      "sha256": "4212baa7cb3a17da089cacc988564e475013c05862b32794660185058855313b"
+    },
+    "permission_seeds": {
+      "rows": 46,
+      "sha256": "ce477ea2120eec1b38dee2ea238e2e8e26af498dcfa96a75d4aa36285df6b4ba"
+    },
+    "policies": {
+      "rows": 24,
+      "sha256": "009c8a6382ca04faf58ccfe9f0a0be56f8d9e144bc109f4c6cba78e292edb6f6"
+    },
+    "projection_auth_effective_columns": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "projection_auth_effective_tables": {
+      "rows": 0,
+      "sha256": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
+    },
+    "projection_auth_schema_privileges": {
+      "rows": 4,
+      "sha256": "dd02d5042de78ba4f408df3cdb3aefd00ff41b5e25aea52df6998b2db312ff78"
+    },
+    "projection_dependencies": {
+      "rows": 19,
+      "sha256": "3d6cd750d6c1ec52287adbd14db6c2a226b0e313823e7751cf1d5904834731c1"
+    },
+    "projection_effective_columns": {
+      "rows": 472,
+      "sha256": "6671c0575005676e3f8588c99e7c311252e62ab21bc02f0cae5dd700978ef39c"
+    },
+    "projection_effective_functions": {
+      "rows": 25,
+      "sha256": "c25807b02101000ed0efe24eb105bd0c59c54075bab8c9ee7e9637d819bf069c"
+    },
+    "projection_effective_schemas": {
+      "rows": 2,
+      "sha256": "3327528c865e9ff102536c7ef8f18d393b1ac5bc52054970fe5d391e44cd54a1"
+    },
+    "projection_effective_sequences": {
+      "rows": 9,
+      "sha256": "6faaac5625b22a62f7b1edf3c4c93ce0ae03deb020f530f09abfc608123fff27"
+    },
+    "projection_effective_tables": {
+      "rows": 84,
+      "sha256": "31c27a927caae4c3aed716f3c38b97fd7ecf500128cc15b9629240483b62c301"
+    },
+    "projection_memberships": {
+      "rows": 1,
+      "sha256": "a4429904fc3c61f2e04c0b1f304324ae4376b3b51f2937d23be352d8b8d6954f"
+    },
+    "projection_role": {
+      "rows": 1,
+      "sha256": "b3ceddc8a420506cb102bc3f90a78130bb482cfb97cee369de0822871b4e1294"
+    },
+    "relations": {
+      "rows": 40,
+      "sha256": "290983e942c231792c34c73183bfa78ab459082df63875129c97abfa4fd12686"
+    },
+    "role_memberships": {
+      "rows": 5,
+      "sha256": "c0ef36ec027665dc56170c20561aefa12de58ecaff0ff4b8c3232ae6f0ee00cd"
+    },
+    "roles": {
+      "rows": 6,
+      "sha256": "318e5d6782d233327a4282feb8d3de40e7f3701b27550e23f8dcefc4ad3d5ea5"
+    },
+    "schema": {
+      "rows": 1,
+      "sha256": "6fbf7ab08dc2da71a1086f369ab1c717900e505d1cb05039168174d8faad7731"
+    },
+    "sequences": {
+      "rows": 3,
+      "sha256": "17a2be8cd5b5bdd71377a96b212b38db0c5e89359d93258f1abb3a6aec2ec02a"
+    },
+    "target_effective_columns": {
+      "rows": 1888,
+      "sha256": "46428e45f30a907c76bc9709ff5ccc750808916c5995a6eab2d2f8b23fbefa2e"
+    },
+    "target_effective_functions": {
+      "rows": 100,
+      "sha256": "9d76043faab15f02d828119b5d7e9756ce403ab263e78b9aa4dc72dff88a7ce3"
+    },
+    "target_effective_schemas": {
+      "rows": 8,
+      "sha256": "e5c344fd1846c27963970409e137b3a490d3439ab20cc298af9bf8169d0bd535"
+    },
+    "target_effective_sequences": {
+      "rows": 36,
+      "sha256": "383fcd8544da05553c35ef3eae1217ac145eecc4f311220374ad32221d57f1e4"
+    },
+    "target_effective_tables": {
+      "rows": 336,
+      "sha256": "631a0e982afd115ec70b664532492d55b3388572268eb8399f5552bb9594be9e"
+    },
+    "triggers": {
+      "rows": 21,
+      "sha256": "3c18774b2a257d37f6887f0a64769eea56f356af3169756596a0615c4ac47d92"
+    },
+    "types": {
+      "rows": 28,
+      "sha256": "fe3f3d4042f035a79ecee7f2893a1989103d77a9854f3f5c1d5ee6ac9d29df08"
+    }
+  },
+  "migration_sha256": "70be70971e7f06475e2fe365dfaed9c8e8e5d96d11edc0375e4b114696126742",
+  "source_pins": {
+    "platform/supabase/migrations/20250815110000_platform_create_identity_schema.sql": "cad9d5f3e5be38efdcf39ab338c06ecc693758f965234b0e5782c00480a61992",
+    "platform/supabase/migrations/20250815150000_platform_auth-hook.sql": "3286922124a974349691fe88ede59a595409df86a94654b713bb82a68cbf828d",
+    "platform/supabase/migrations/20250815160000_platform_create_audit_log_tbl.sql": "32cc49339c0ec9029261528c71e65246fd430498c7b693f31794489235c67b35",
+    "platform/supabase/migrations/20250815170000_platform_create_audit_triggers.sql": "853882974e29bba54c40de0ccb47d17362fd33e2ce2c4b940353388f364c1e01",
+    "platform/supabase/migrations/20250815180000_platform_add_get_user_roles_function.sql": "d3683ac1cba6b78ba4cad7086a2f6868a44aa116b3c3f76de77572a3d1066ace",
+    "platform/supabase/migrations/20250815210000_platform_multitenancy_orgs.sql": "f7a1f2bf26f5f72807d1451de441f53291562b4c41e3ae75e03957c11b0c8d20",
+    "services/access/tools/identity_bridge.sql": "e4063529f1dd589a7269bdcff3ec5695ed599ab1e1df6ecfc3f9042765fa90fc"
+  }
+}
diff --git a/services/access/identity-migrations/versions/0015_membership_actor_attribution.py b/services/access/identity-migrations/versions/0015_membership_actor_attribution.py
new file mode 100644
index 0000000..9bf4b26
--- /dev/null
+++ b/services/access/identity-migrations/versions/0015_membership_actor_attribution.py
@@ -0,0 +1,57 @@
+"""Stage protected durable membership actor references; no inferred adoption."""
+from alembic import op
+
+revision = 'identity_0015'
+down_revision = 'identity_0014'
+branch_labels = None
+depends_on = None
+
+MEMBERSHIP_ACTOR_ATTRIBUTION_SQL = r"""
+ALTER TABLE identity.org_member
+ ADD COLUMN created_actor_id uuid CONSTRAINT org_member_created_actor_fk REFERENCES identity.actor(id) ON DELETE RESTRICT,
+ ADD COLUMN updated_actor_id uuid CONSTRAINT org_member_updated_actor_fk REFERENCES identity.actor(id) ON DELETE RESTRICT;
+
+CREATE FUNCTION identity.guard_org_member_actor_attribution()
+RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, pg_temp
+AS $actor_guard$
+BEGIN
+ IF TG_OP='UPDATE' AND OLD.created_actor_id IS NOT NULL
+    AND NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id THEN
+  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_creation_actor_immutable',
+    CONSTRAINT='org_member_creation_actor_immutable';
+ END IF;
+ IF current_user <> 'identity_migrator' AND
+   ((TG_OP='INSERT' AND (NEW.created_actor_id IS NOT NULL OR NEW.updated_actor_id IS NOT NULL))
+    OR (TG_OP='UPDATE' AND (NEW.created_actor_id IS DISTINCT FROM OLD.created_actor_id
+                          OR NEW.updated_actor_id IS DISTINCT FROM OLD.updated_actor_id))) THEN
+  RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_membership_actor_owner_required',
+    CONSTRAINT='org_member_actor_owner_required';
+ END IF;
+ RETURN NEW;
+END;
+$actor_guard$;
+CREATE TRIGGER org_member_actor_attribution_guard BEFORE INSERT OR UPDATE ON identity.org_member
+ FOR EACH ROW EXECUTE FUNCTION identity.guard_org_member_actor_attribution();
+
+-- Strip any inherited function grants, including unlisted default grantees.
+DO $acl$
+DECLARE a record; grantee text;
+BEGIN
+ REVOKE ALL ON FUNCTION identity.guard_org_member_actor_attribution() FROM PUBLIC;
+ FOR a IN SELECT DISTINCT x.grantee FROM pg_proc p,
+  LATERAL aclexplode(p.proacl) x
+  WHERE p.oid='identity.guard_org_member_actor_attribution()'::regprocedure AND x.grantee<>p.proowner LOOP
+  grantee:=CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END;
+  EXECUTE format('REVOKE ALL ON FUNCTION identity.guard_org_member_actor_attribution() FROM %s',grantee);
+ END LOOP;
+END;
+$acl$;
+"""
+
+
+def upgrade():
+    op.get_bind().exec_driver_sql(MEMBERSHIP_ACTOR_ATTRIBUTION_SQL, execution_options={'no_parameters': True})
+
+
+def downgrade():
+    raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
diff --git a/services/access/tests/qualify_identity_baseline.py b/services/access/tests/qualify_identity_baseline.py
index f0f15dd..a76bd60 100644
--- a/services/access/tests/qualify_identity_baseline.py
+++ b/services/access/tests/qualify_identity_baseline.py
@@ -1183,6 +1183,102 @@ class Qualification:
         self.records.append({'label':'trusted-active-membership-index-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'active_membership_index_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
         self.persist();print('trusted-active-membership-index-reference PASS',sha(content),flush=True)
 
+    def record_membership_actor_attribution_reference(self):
+        """Independent rollback-only fixture, verifying every historical catalog through13."""
+        if not __debug__:
+            raise RuntimeError('membership_actor_attribution_reference_optimized_python_prohibited')
+        destination=OWNER/'membership-actor-attribution-reference.json'
+        assert not destination.exists(), 'membership_actor_attribution_reference_already_exists'
+        module=OWNER/'identity_baseline.py'
+        captured = {module: module.read_bytes(), OWNER/'source-pins.json': (OWNER/'source-pins.json').read_bytes()}
+        assert (Path(baseline.__file__).resolve()==module.resolve()
+                and sha(captured[module])==baseline.IMPORTED_SOURCE_SHA256), 'membership_actor_attribution_reference_stale_imported_helper'
+        assert b'MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 = None' in captured[module]
+        for name in ['reference.json','actor-reference.json','projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json','membership-retention-reference.json','membership-retirement-reference.json','active-membership-index-reference.json']:
+            path=OWNER/name; captured[path]=path.read_bytes()
+        baseline.trusted_active_membership_index_reference()
+        revisions=[]
+        for name in ['0001_baseline.py','0002_actor_registry.py','0003_current_account_actor.py','0004_current_account_organization.py','0005_operator_authority.py','0006_actor_command.py','0007_organization_targets.py','0008_profile_fields.py','0009_legacy_roles.py','0010_token_hook.py','0011_membership_binding.py','0012_membership_retention.py','0013_membership_retirement.py','0014_active_membership_index.py','0015_membership_actor_attribution.py']:
+            path = OWNER/'versions'/name
+            captured[path] = path.read_bytes()
+            # Execute the exact captured source that the fixture digest binds.
+            spec=importlib.util.spec_from_file_location('projection_source_'+name[:4],path)
+            revision=importlib.util.module_from_spec(spec)
+            exec(compile(captured[path], str(path), 'exec'), revision.__dict__)
+            revisions.append(revision)
+        db=engine(self.private['owner_urls']['membership_actor_attribution_reference'])
+        try:
+            with db.connect() as connection:
+                transaction=connection.begin()
+                try:
+                    connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
+                    assert baseline.preflight(connection,'clean')=='clean'
+                    baseline.verify_projection_role(connection,staged=True)
+                    baseline.verify_authority_roles(connection,staged=True)
+                    baseline.verify_command_role(connection,staged=True)
+                    baseline.verify_target_roles(connection,staged=True)
+                    for source in baseline.source_sql():connection.exec_driver_sql(source)
+                    connection.exec_driver_sql(revisions[0].LEGACY_INTEGRATION_SQL)
+                    baseline.verify_catalog(connection,'owned')
+                    connection.execute(text(revisions[1].ACTOR_SCHEMA_SQL))
+                    baseline.verify_catalog(connection,'actor')
+                    connection.execute(text(revisions[2].PROJECTION_SCHEMA_SQL))
+                    baseline.verify_catalog(connection,'projection')
+                    connection.execute(text(revisions[3].ORGANIZATION_SCHEMA_SQL))
+                    baseline.verify_projection_role(connection)
+                    baseline.verify_catalog(connection,'organization')
+                    connection.execute(text(revisions[4].AUTHORITY_SCHEMA_SQL))
+                    baseline.verify_catalog(connection,'authority')
+                    connection.exec_driver_sql(revisions[5].COMMAND_SCHEMA_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_command_role(connection)
+                    baseline.verify_catalog(connection,'command')
+                    connection.exec_driver_sql(revisions[6].TARGET_SCHEMA_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_target_roles(connection)
+                    baseline.verify_catalog(connection,'target')
+                    connection.exec_driver_sql(revisions[7].PROFILE_FIELDS_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_profile_privileges(connection)
+                    baseline.verify_catalog(connection,'profile')
+                    connection.exec_driver_sql(revisions[8].LEGACY_ROLES_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'legacy_roles')
+                    connection.exec_driver_sql(revisions[9].TOKEN_HOOK_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'token_hook')
+                    connection.exec_driver_sql(revisions[10].MEMBERSHIP_BINDING_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'membership_binding')
+                    connection.exec_driver_sql(revisions[11].MEMBERSHIP_RETENTION_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'membership_retention')
+                    connection.exec_driver_sql(revisions[12].MEMBERSHIP_RETIREMENT_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'membership_retirement')
+                    connection.exec_driver_sql(revisions[13].ACTIVE_MEMBERSHIP_INDEX_SQL, execution_options={'no_parameters': True})
+                    baseline.verify_catalog(connection,'active_membership_index')
+                    connection.exec_driver_sql(revisions[14].MEMBERSHIP_ACTOR_ATTRIBUTION_SQL, execution_options={'no_parameters': True})
+                    fingerprints=baseline.catalog_fingerprints(baseline.target_catalog_snapshot(connection))
+                finally:
+                    transaction.rollback()
+            with db.connect() as connection:
+                connection.execute(text("SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"))
+                assert baseline.preflight(connection,'clean')=='clean'
+                baseline.verify_projection_role(connection,staged=True)
+                baseline.verify_authority_roles(connection,staged=True)
+                baseline.verify_command_role(connection,staged=True)
+                baseline.verify_target_roles(connection,staged=True)
+        finally:db.dispose()
+        reference={'_generated':'GENERATED by tests/qualify_identity_baseline.py --record-membership-actor-attribution-reference; change owning fixture/code, never hand-edit',
+                   'source_pins':json.loads(captured[OWNER/'source-pins.json']),
+                   'migration_sha256':sha(captured[OWNER/'versions/0015_membership_actor_attribution.py']),
+                   'membership_actor_attribution':fingerprints}
+        content=(json.dumps(reference,sort_keys=True,indent=2)+'\n').encode()
+        temporary=OWNER/'.membership-actor-attribution-reference-recording';created=False
+        try:
+            descriptor=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
+            with os.fdopen(descriptor,'wb') as output:
+                created=True;output.write(content);output.flush();os.fsync(output.fileno())
+            assert all(path.read_bytes() == data for path,data in captured.items()), 'membership_actor_attribution_reference_source_changed'
+            os.link(temporary,destination)
+        finally:
+            if created:temporary.unlink(missing_ok=True)
+        self.records.append({'label':'trusted-membership-actor-attribution-reference','status':'passed','sha256':sha(content),'migration_sha256':reference['migration_sha256'],'known_source_case':'membership_actor_attribution_reference','rolled_back':True,'helper_sha256':sha(captured[module]),'source_sha256':{str(path.relative_to(OWNER)):sha(data) for path,data in captured.items()},'pin_update_required':True})
+        self.persist();print('trusted-membership-actor-attribution-reference PASS',sha(content),flush=True)
+
     def sql(self, case, statement, values=None, role='owner_urls'):
         db = engine(self.private[role][case])
         try:
@@ -1523,6 +1619,8 @@ class Qualification:
         self.persist()
 
 def main():
+    if sys.argv[1:] == ['--record-membership-actor-attribution-reference'] and not __debug__:
+        raise RuntimeError('membership_actor_attribution_reference_optimized_python_prohibited')
     if sys.argv[1:] == ['--record-active-membership-index-reference'] and not __debug__:
         raise RuntimeError('active_membership_index_reference_optimized_python_prohibited')
     if sys.argv[1:] == ['--record-membership-retirement-reference'] and not __debug__:
@@ -1541,6 +1639,9 @@ def main():
         raise RuntimeError('target_reference_optimized_python_prohibited')
     proof, private = fixture()
     q = Qualification(proof, private)
+    if sys.argv[1:] == ['--record-membership-actor-attribution-reference']:
+        q.record_membership_actor_attribution_reference()
+        return
     if sys.argv[1:] == ['--record-active-membership-index-reference']:
         q.record_active_membership_index_reference()
         return
diff --git a/services/access/tests/qualify_membership_actor_attribution.py b/services/access/tests/qualify_membership_actor_attribution.py
new file mode 100644
index 0000000..5b465c2
--- /dev/null
+++ b/services/access/tests/qualify_membership_actor_attribution.py
@@ -0,0 +1,299 @@
+"""Actual staged actor-reference proof through existing Identity fixture tooling."""
+from contextlib import contextmanager
+from pathlib import Path
+import json
+import sys
+import signal
+import time
+
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import qualify_active_membership_index as previous
+from qualify_identity_baseline import baseline, engine, fixture, text
+
+PREVIOUS_COMMIT='f885abf5b782af09d845af4eefcd9c170faa7bab'
+PREVIOUS_FILES=previous.PREVIOUS_FILES | {'versions/0014_active_membership_index.py','active-membership-index-reference.json'}
+REQUIRED_CASES=(previous.REQUIRED_CASES-{'active_membership_index_reference'})|{'membership_actor_attribution_reference'}
+FIELDS=('created_actor_id','updated_actor_id')
+
+
+class MembershipActorAttributionQualification(previous.ActiveMembershipIndexQualification):
+    required_cases=REQUIRED_CASES
+
+    def characterize(self):
+        case='characterization';self.fixture_rows(case)
+        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
+        catalog=self.snapshot(case)
+        baseline.compare_catalog(baseline.catalog_fingerprints(catalog),baseline.trusted_active_membership_index_reference())
+        before=self.data_state(case)
+        db=engine(self.private['owner_urls'][case])
+        try:
+            with db.connect() as c:
+                try:c.execute(text('SELECT created_actor_id,updated_actor_id FROM identity.org_member'))
+                except Exception as error:assert error.orig.sqlstate=='42703'
+                else:raise AssertionError('expected_missing_membership_actor_columns')
+                finally:c.rollback()
+        finally:db.dispose()
+        assert self.data_state(case)==before
+        self.witness('membership-actor-attribution-head14-characterization',{
+            'binding':self.characterization_binding(),'catalog':catalog,'head':'identity_0014',
+            'missing_columns':list(FIELDS),'unchanged_data':True})
+        self.passed('membership-actor-attribution-head14-characterization',expected_sqlstate='42703')
+
+    def compatibility(self):
+        paths=sorted(self.proof.glob('membership-actor-attribution-head14-characterization-*.json'),key=lambda p:p.stat().st_mtime_ns)
+        assert paths
+        witness=json.loads(paths[-1].read_text())
+        assert witness['binding']==self.characterization_binding() and witness['head']=='identity_0014'
+        assert witness['unchanged_data'] and witness['missing_columns']==list(FIELDS)
+        old=witness['catalog'];current=self.snapshot('clean')
+        baseline.compare_catalog(baseline.catalog_fingerprints(old),baseline.trusted_active_membership_index_reference())
+        baseline.compare_catalog(baseline.catalog_fingerprints(current),baseline.trusted_membership_actor_attribution_reference())
+        self.verify_catalog_delta(old,current)
+        assert self.sql('clean',"SELECT pg_get_userbyid(proowner),prosecdef,provolatile,proconfig::text FROM pg_proc WHERE oid='identity.guard_org_member_actor_attribution()'::regprocedure")==[('identity_migrator',False,'v','{\"search_path=pg_catalog, pg_temp\"}')]
+        for name in FIELDS:
+            assert self.sql('clean',"SELECT is_nullable,column_default FROM information_schema.columns WHERE table_schema='identity' AND table_name='org_member' AND column_name=:name",{'name':name})==[('YES',None)]
+        constraints=self.sql('clean',"SELECT conname,pg_get_constraintdef(oid,true),convalidated FROM pg_constraint WHERE conrelid='identity.org_member'::regclass AND conname IN ('org_member_created_actor_fk','org_member_updated_actor_fk') ORDER BY conname")
+        assert constraints==[(f'org_member_{prefix}_actor_fk',f'FOREIGN KEY ({prefix}_actor_id) REFERENCES identity.actor(id) ON DELETE RESTRICT',True) for prefix in ['created','updated']]
+        self.passed('membership-actor-attribution-exact-additive-delta',legacy_catalog_preserved=True)
+
+    @staticmethod
+    def verify_catalog_delta(old,current):
+        structural={'columns','constraints','functions','triggers'}
+        prefixes=('', 'authority_', 'command_', 'projection_', 'target_')
+        effective={prefix+'effective_'+kind for prefix in prefixes for kind in ('columns','functions')}
+        changed={key for key in old if old[key]!=current[key]}
+        assert old.keys()==current.keys() and changed==structural|effective
+        for category in changed:
+            assert all(row in current[category] for row in old[category]), category
+        # New catalogue observation rows do not imply new grants. Column rights
+        # inherit the unchanged table rights, not unrelated explicit column ACLs.
+        for prefix in prefixes:
+            category=prefix+'effective_columns'
+            expected=[[role,table,field,permission,allowed]
+                for role,table,permission,allowed in old[prefix+'effective_tables']
+                if table=='org_member' and permission in ('INSERT','REFERENCES','SELECT','UPDATE')
+                for field in FIELDS]
+            assert sorted(current[category])==sorted(old[category]+expected)
+            category=prefix+'effective_functions'
+            roles={row[0] for row in old[category]}
+            expected=[[role,'identity','guard_org_member_actor_attribution','',role=='identity_migrator'] for role in roles]
+            assert sorted(current[category])==sorted(old[category]+expected)
+        assert len(current['columns'])==len(old['columns'])+2
+        assert len(current['constraints'])==len(old['constraints'])+2
+        assert len(current['functions'])==len(old['functions'])+1
+        assert len(current['triggers'])==len(old['triggers'])+1
+
+    def attribution_writes(self):
+        case='clean';v=dict(self.inputs[case]);self.fixture_rows(case)
+        v.update(actor='c1234567-1234-1234-1234-123456789abc',other_actor='d1234567-1234-1234-1234-123456789abc')
+        before=self.data_state(case);catalog=self.snapshot(case)
+        with self.fixture_execution(case):
+            db=engine(self.private['runtime_urls'][case])
+            try:
+                with db.connect() as c:
+                    for field in FIELDS:
+                        with self.execution(c,v):
+                            for statement in [
+                                f'UPDATE identity.org_member SET {field}=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint)',
+                                f'INSERT INTO identity.org_member(org_id,user_id,{field}) VALUES(CAST(:spare_org AS uuid),CAST(:spare AS uuid),CAST(:actor AS uuid))',
+                                f'INSERT INTO identity.org_member(org_id,user_id,{field}) VALUES(CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid)) ON CONFLICT(org_id,user_id) DO UPDATE SET {field}=EXCLUDED.{field}',
+                                f'UPDATE identity.org_member SET is_owner=NOT is_owner,{field}=CASE WHEN id=CAST(:member AS bigint) THEN CAST(:actor AS uuid) ELSE NULL END WHERE org_id=CAST(:org AS uuid)',
+                            ]:
+                                self.reject(c,statement,v,'23514','identity_membership_actor_owner_required','org_member_actor_owner_required')
+                    self.seed_compatibility(c,v)
+            finally:db.dispose()
+        # Explicit synthetic adoption only, under the actual owner. All rows restored.
+        db=self.admin(case)
+        try:
+            with db.connect() as c:
+                tx=c.begin()
+                try:
+                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
+                    c.execute(text('SET LOCAL ROLE identity_migrator'))
+                    assert c.execute(text('SELECT current_user')).scalar_one()=='identity_migrator'
+                    for key in ['actor','other_actor']:
+                        c.execute(text("INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by) VALUES(CAST(:id AS uuid),'service',:key,'Synthetic verified actor',CAST(:id AS uuid),CAST(:id AS uuid))"),{'id':v[key],'key':'synthetic:'+key})
+                    original=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:member AS bigint)'),v).scalar_one()
+                    for field in FIELDS:
+                        for invalid in ['00000000-0000-0000-0000-000000000000','e1234567-1234-1234-1234-123456789abc']:
+                            self.reject(c,f'UPDATE identity.org_member SET {field}=CAST(:invalid AS uuid) WHERE id=CAST(:member AS bigint)',dict(v,invalid=invalid),'23503',None,None)
+                    changed=c.execute(text('UPDATE identity.org_member SET created_actor_id=CAST(:actor AS uuid),updated_actor_id=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
+                    assert changed==dict(original,created_actor_id=v['actor'],updated_actor_id=v['actor'],revision=original['revision']+1)
+                    for replacement in ['NULL','CAST(:other_actor AS uuid)']:
+                        self.reject(c,'UPDATE identity.org_member SET created_actor_id='+replacement+' WHERE id=CAST(:member AS bigint)',v,'23514','identity_membership_creation_actor_immutable','org_member_creation_actor_immutable')
+                    noop=c.execute(text('UPDATE identity.org_member SET created_actor_id=created_actor_id,updated_actor_id=updated_actor_id,revision=999 WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
+                    assert noop==changed
+                    updated=c.execute(text('UPDATE identity.org_member SET updated_actor_id=CAST(:other_actor AS uuid) WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
+                    assert updated==dict(changed,updated_actor_id=v['other_actor'],revision=changed['revision']+1)
+                    c.execute(text('SET LOCAL ROLE service_role'))
+                    for field in FIELDS:
+                        for replacement in ['NULL','CAST(:other_actor AS uuid)']:
+                            # Repeating the existing value remains a supported no-op.
+                            if field=='updated_actor_id' and replacement!='NULL':continue
+                            message='identity_membership_creation_actor_immutable' if field=='created_actor_id' else 'identity_membership_actor_owner_required'
+                            constraint='org_member_creation_actor_immutable' if field=='created_actor_id' else 'org_member_actor_owner_required'
+                            self.reject(c,f'UPDATE identity.org_member SET {field}={replacement} WHERE id=CAST(:member AS bigint)',v,'23514',message,constraint)
+                    preserved=c.execute(text('UPDATE identity.org_member SET is_owner=NOT is_owner,created_actor_id=created_actor_id,updated_actor_id=updated_actor_id WHERE id=CAST(:member AS bigint) RETURNING to_jsonb(org_member)'),v).scalar_one()
+                    assert preserved==dict(updated,is_owner=not updated['is_owner'],revision=updated['revision']+1)
+                    c.execute(text(self.seed_statement()),v)
+                    seeded=c.execute(text('SELECT to_jsonb(m) FROM identity.org_member m WHERE id=CAST(:member AS bigint)'),v).scalar_one()
+                    assert seeded['created_actor_id']==v['actor'] and seeded['updated_actor_id']==v['other_actor']
+                    c.execute(text('RESET ROLE'))
+                    c.execute(text('SET LOCAL ROLE identity_migrator'))
+                    # Rollback-only owner preparation exercises exhaustion without changing production guard code.
+                    c.execute(text('ALTER TABLE identity.org_member DISABLE TRIGGER org_member_revision_guard'))
+                    c.execute(text('UPDATE identity.org_member SET revision=9223372036854775807 WHERE id=CAST(:member AS bigint)'),v)
+                    c.execute(text('ALTER TABLE identity.org_member ENABLE TRIGGER org_member_revision_guard'))
+                    self.reject(c,'UPDATE identity.org_member SET updated_actor_id=CAST(:actor AS uuid) WHERE id=CAST(:member AS bigint)',v,'23514','identity_membership_revision_exhausted','org_member_revision_positive')
+                finally:tx.rollback()
+        finally:db.dispose()
+        assert self.data_state(case)==before and self.snapshot(case)==catalog
+        self.passed('membership-actor-attribution-writes',owner_prepared_adoption=True,actual_restricted_login_null_columns=True,adopted_fields_set_role_service_role=True,legacy_fields_times_preserved=True,rollback_only=True)
+
+    def preserved_upgrade(self,case,legacy=False):
+        before=self.data_state(case,membership_without_revision=legacy)
+        members=self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m ORDER BY id')
+        external=self.external_state(case) if case!='clean' else None
+        self.command('membership-actor-attribution-'+case,case,mode='adopt' if legacy else 'clean')
+        after=self.data_state(case,membership_without_revision=legacy)
+        assert all(after[key]==value for key,value in before.items() if key not in {'identity.alembic_version','org_member'})
+        new=self.sql(case,'SELECT to_jsonb(m) FROM identity.org_member m ORDER BY id')
+        assert len(new)==len(members)
+        for (old,), (row,) in zip(members,new):
+            assert row['created_actor_id'] is None and row['updated_actor_id'] is None
+            normalized={k:v for k,v in row.items() if k not in FIELDS and not (legacy and k=='revision')}
+            assert normalized==old
+        assert external is None or self.external_state(case)==external
+
+    @contextmanager
+    def failure_fixture(self,case):
+        state_sql="""SELECT 'function',p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.proname='synthetic_membership_actor_attribution_failure'
+            UNION ALL SELECT 'event_trigger',evtname FROM pg_event_trigger WHERE evtname='synthetic_membership_actor_attribution_failure'
+            UNION ALL SELECT 'sequence',c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname='synthetic_membership_actor_attribution_failure_marker' ORDER BY 1,2"""
+        before=self.admin_sql(case,state_sql);assert before==[],'membership_actor_attribution_failure_fixture_already_exists'
+        marker_sql='SELECT last_value,is_called FROM public.synthetic_membership_actor_attribution_failure_marker'
+        create="""CREATE SEQUENCE public.synthetic_membership_actor_attribution_failure_marker START WITH 1;
+            REVOKE ALL ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker FROM PUBLIC,anon,authenticated,service_role,access_runtime;
+            GRANT USAGE ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker TO identity_migrator;
+            CREATE FUNCTION public.synthetic_membership_actor_attribution_failure() RETURNS event_trigger LANGUAGE plpgsql AS $$ BEGIN
+            IF to_regprocedure('identity.guard_org_member_actor_attribution()') IS NOT NULL THEN
+                PERFORM pg_catalog.nextval('public.synthetic_membership_actor_attribution_failure_marker'::regclass);
+                RAISE EXCEPTION USING ERRCODE='P0001',MESSAGE='synthetic_membership_actor_attribution_failure';
+            END IF; END $$;
+            CREATE EVENT TRIGGER synthetic_membership_actor_attribution_failure ON ddl_command_end WHEN TAG IN ('CREATE TRIGGER') EXECUTE FUNCTION public.synthetic_membership_actor_attribution_failure();"""
+        cleanup='DROP EVENT TRIGGER IF EXISTS synthetic_membership_actor_attribution_failure; DROP FUNCTION IF EXISTS public.synthetic_membership_actor_attribution_failure(); DROP SEQUENCE IF EXISTS public.synthetic_membership_actor_attribution_failure_marker'
+        self.witness('membership-actor-attribution-event-restoration-required',{'case':case,'before':before,'create':create,'cleanup':cleanup})
+        verified=False
+        def verify_fired():
+            nonlocal verified
+            marker=self.admin_sql(case,marker_sql)
+            assert marker==[(1,True)],'membership_actor_attribution_failure_fixture_not_fired'
+            if not verified:
+                self.witness('membership-actor-attribution-event-fired',{'case':case,'marker_before':[1,False],'marker_after':list(marker[0]),'new_guard_observed':True})
+                verified=True
+        with self.restoration_signals():
+            try:
+                self.admin_sql(case,create)
+                assert self.admin_sql(case,marker_sql)==[(1,False)],'membership_actor_attribution_failure_marker_initially_called'
+                yield verify_fired
+                verify_fired()
+            finally:
+                for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,signal.SIG_IGN)
+                self.admin_sql(case,cleanup)
+                assert self.admin_sql(case,state_sql)==before,'membership_actor_attribution_failure_fixture_not_restored'
+                self.witness('membership-actor-attribution-event-restored',{'case':case,'exact_objects':True})
+
+
+    def blocked_index_ddl(self):
+        case='failure';before,catalog=self.data_state(case),self.snapshot(case)
+        assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
+        db=engine(self.private['owner_urls'][case])
+        try:
+            with db.connect() as holder:
+                tx=holder.begin()
+                try:
+                    holder.execute(text("SET LOCAL statement_timeout='15s'; SET LOCAL lock_timeout='2s'"))
+                    holder.execute(text('LOCK TABLE identity.org_member IN ROW EXCLUSIVE MODE'))
+                    started=time.monotonic()
+                    self.command('membership-actor-attribution-blocked-ddl-refused',case,expected='identity_migration_failed_requires_reconciliation')
+                    elapsed=time.monotonic()-started
+                    assert 4<=elapsed<30,'membership_actor_attribution_blocked_ddl_bound'
+                    assert self.data_state(case)==before and self.snapshot(case)==catalog
+                    assert self.sql(case,'SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
+                finally:tx.rollback()
+        finally:db.dispose()
+        assert self.data_state(case)==before and self.snapshot(case)==catalog
+        self.witness('membership-actor-attribution-blocked-ddl-restored',{'case':case,'elapsed_seconds':round(elapsed,3),
+            'lock_mode':'ROW EXCLUSIVE','migration_lock_timeout_seconds':5,'old_catalog_history_data_preserved':True})
+        self.passed('membership-actor-attribution-blocked-ddl',bounded_refusal=True,owner_lock_released=True)
+
+    def function_drift_refusal(self):
+        case='unknown';before,catalog=self.data_state(case),self.snapshot(case)
+        db=engine(self.private['owner_urls'][case])
+        try:
+            with db.connect() as c:
+                tx=c.begin()
+                try:
+                    c.execute(text("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'"))
+                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
+                    rows=self.state(c)
+                    definition=next(row[4] for row in catalog['functions'] if row[:3]==['identity','guard_org_member_revision',''])
+                    c.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n    -- synthetic source drift\n',1),execution_options={'no_parameters':True})
+                    changed=baseline.target_catalog_snapshot(c)
+                    assert {key for key in catalog if catalog[key]!=changed[key]}=={'functions'}
+                    try:baseline.preflight(c,'clean')
+                    except baseline.BaselineError as error:assert str(error)=='identity_catalog_mismatch:functions'
+                    else:raise AssertionError('membership_actor_attribution_function_drift_accepted')
+                    assert baseline.target_catalog_snapshot(c)==changed and self.state(c)==rows
+                    assert c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one()=='identity_0014'
+                finally:tx.rollback()
+        finally:db.dispose()
+        assert self.data_state(case)==before and self.snapshot(case)==catalog
+        self.passed('membership-actor-attribution-function-drift-refused',rollback_only=True,no_normalization=True)
+
+    def upgrades_and_failures(self):
+        self.validate_targets();self.prior_evidence(PREVIOUS_COMMIT,PREVIOUS_FILES,'identity_0014')
+        self.preserved_upgrade('clean');self.compatibility();self.attribution_writes();self.writes()
+        self.command('membership-actor-attribution-repeat','clean')
+        self.legacy('legacy');self.original_ledger('legacy')
+        for case in ['legacy','previous']:
+            self.row_fixtures(case);self.preserved_upgrade(case,legacy=case=='legacy')
+        self.blocked_index_ddl()
+        with self.failure_fixture('failure') as fired:
+            before,catalog=self.data_state('failure'),self.snapshot('failure')
+            self.command('membership-actor-attribution-ddl-rollback','failure',expected='identity_migration_failed_requires_reconciliation')
+            fired();assert self.data_state('failure')==before and self.snapshot('failure')==catalog
+            assert self.sql('failure','SELECT version_num FROM identity.alembic_version')==[('identity_0014',)]
+        self.command('membership-actor-attribution-after-rollback','failure')
+        self.command('membership-actor-attribution-unsafe-clean','unsafe')
+        with self.acl_fixture('unsafe','GRANT INSERT ON identity.users TO authenticated','REVOKE INSERT ON identity.users FROM authenticated','GRANT INSERT (id, username) ON identity.users TO authenticated'):
+            before,catalog=self.data_state('unsafe'),self.snapshot('unsafe')
+            self.command('membership-actor-attribution-drift-refused','unsafe',expected='identity_profile_column_privileges_mismatch')
+            assert self.data_state('unsafe')==before and self.snapshot('unsafe')==catalog
+        self.command('membership-actor-attribution-drift-reconciled','unsafe')
+        self.function_drift_refusal()
+        db=engine(self.private['owner_urls']['unknown']);before,catalog=self.data_state('unknown'),self.snapshot('unknown')
+        try:
+            with db.connect() as c:
+                tx=c.begin()
+                try:
+                    c.execute(text("UPDATE identity.alembic_version SET version_num='identity_unknown'"))
+                    try:baseline.preflight(c,'clean')
+                    except baseline.BaselineError as error:assert str(error)=='identity_unknown_history'
+                    else:raise AssertionError('unknown_history_accepted')
+                finally:tx.rollback()
+        finally:db.dispose()
+        assert self.data_state('unknown')==before and self.snapshot('unknown')==catalog
+        self.passed('membership-actor-attribution-migration-matrix',clean_adopt_exact14_repeat=True,rollback_recovery=True,drift_unknown_refused=True)
+
+
+def main():
+    if not __debug__:raise RuntimeError('membership_actor_attribution_qualification_optimized_python_prohibited')
+    proof,private=fixture();q=MembershipActorAttributionQualification(proof,private)
+    if sys.argv[1:]==['--characterize']:q.validate_targets();q.characterize()
+    elif not sys.argv[1:]:q.upgrades_and_failures()
+    else:raise RuntimeError('qualification_arguments_invalid')
+    q.persist()
+
+
+if __name__=='__main__':main()
diff --git a/services/access/tests/test_membership_actor_attribution.py b/services/access/tests/test_membership_actor_attribution.py
new file mode 100644
index 0000000..870bbd0
--- /dev/null
+++ b/services/access/tests/test_membership_actor_attribution.py
@@ -0,0 +1,247 @@
+"""Staged membership actor reference custody and release checks."""
+import importlib.util
+from pathlib import Path
+import sys
+import pytest
+sys.path.insert(0,str(Path(__file__).resolve().parent))
+import qualify_identity_baseline as qualification
+
+
+def test_new_head_preserves_previous_index_catalog(monkeypatch):
+    b=qualification.baseline
+    assert b.MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION=='identity_0015'
+    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
+    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_ACTOR_ATTRIBUTION_REVISION)
+    seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
+    b.verify_owned_postcondition(object(),require_head=True)
+    assert seen==['membership_actor_attribution']
+    monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACTIVE_MEMBERSHIP_INDEX_REVISION)
+    b.verify_owned_postcondition(object())
+    assert seen[-1]=='active_membership_index'
+    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)
+
+
+@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json','actor-reference.json',
+    'projection-reference.json','organization-reference.json','authority-reference.json','command-reference.json',
+    'target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json',
+    'membership-retention-reference.json','membership-retirement-reference.json','active-membership-index-reference.json',
+    'versions/0001_baseline.py','versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
+    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py','versions/0006_actor_command.py',
+    'versions/0007_organization_targets.py','versions/0008_profile_fields.py','versions/0009_legacy_roles.py',
+    'versions/0010_token_hook.py','versions/0011_membership_binding.py','versions/0012_membership_retention.py',
+    'versions/0013_membership_retirement.py','versions/0014_active_membership_index.py','versions/0015_membership_actor_attribution.py'])
+def test_recorder_captures_every_source_and_checks_every_prior_catalog(tmp_path,monkeypatch,mutation):
+    from test_actor_command_qualification import recorder
+    from test_projection_qualification import digest
+    import stat
+    runner,statements=recorder(tmp_path,monkeypatch,mutation)
+    (tmp_path/'identity_baseline.py').write_text('MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256 = None\n')
+    for name in ['command-reference.json','target-reference.json','profile-reference.json','legacy-role-reference.json','token-hook-reference.json','membership-binding-reference.json','membership-retention-reference.json','membership-retirement-reference.json','active-membership-index-reference.json']:(tmp_path/name).write_text('{}')
+    for number,name,symbol in [(7,'organization_targets','TARGET_SCHEMA_SQL'),(8,'profile_fields','PROFILE_FIELDS_SQL'),(9,'legacy_roles','LEGACY_ROLES_SQL'),(10,'token_hook','TOKEN_HOOK_SQL'),(11,'membership_binding','MEMBERSHIP_BINDING_SQL'),(12,'membership_retention','MEMBERSHIP_RETENTION_SQL'),(13,'membership_retirement','MEMBERSHIP_RETIREMENT_SQL'),(14,'active_membership_index','ACTIVE_MEMBERSHIP_INDEX_SQL'),(15,'membership_actor_attribution','MEMBERSHIP_ACTOR_ATTRIBUTION_SQL')]:
+        (tmp_path/f'versions/{number:04d}_{name}.py').write_text(f'{symbol} = "captured {name}"\n')
+    runner.private={'owner_urls':{'membership_actor_attribution_reference':'synthetic'}}
+    b=qualification.baseline
+    monkeypatch.setattr(b,'trusted_active_membership_index_reference',lambda:{})
+    monkeypatch.setattr(b,'verify_target_roles',lambda *a,**k:None)
+    monkeypatch.setattr(b,'verify_profile_privileges',lambda *a,**k:None)
+    monkeypatch.setattr(b,'target_catalog_snapshot',lambda *a:{})
+    monkeypatch.setattr(b,'IMPORTED_SOURCE_SHA256',digest((tmp_path/'identity_baseline.py').read_bytes()))
+    helper=(tmp_path/'identity_baseline.py').read_bytes();catalogs=[]
+    monkeypatch.setattr(b,'verify_catalog',lambda c,kind:catalogs.append(kind))
+    deadline="SET LOCAL statement_timeout='60s'; SET LOCAL lock_timeout='5s'"
+    preflights=[]
+    def preflight(*args):
+        assert statements[-1]==deadline
+        preflights.append(len(statements));return 'clean'
+    monkeypatch.setattr(b,'preflight',preflight)
+    if mutation:
+        with pytest.raises(AssertionError,match='membership_actor_attribution_reference_source_changed'):runner.record_membership_actor_attribution_reference()
+        assert not (tmp_path/'membership-actor-attribution-reference.json').exists()
+    else:
+        runner.record_membership_actor_attribution_reference()
+        assert (tmp_path/'identity_baseline.py').read_bytes()==helper
+        assert runner.records[-1]['pin_update_required'] is True
+        assert stat.S_IMODE((tmp_path/'membership-actor-attribution-reference.json').stat().st_mode)==0o600
+        with pytest.raises(AssertionError,match='already_exists'):runner.record_membership_actor_attribution_reference()
+    assert len(preflights)==2
+    assert catalogs==['owned','actor','projection','organization','authority','command','target','profile','legacy_roles','token_hook','membership_binding','membership_retention','membership_retirement','active_membership_index']
+    assert statements==[deadline,'captured baseline','captured actor','captured projection','captured organization','captured authority','captured command',
+        'captured organization_targets','captured profile_fields','captured legacy_roles','captured token_hook','captured membership_binding','captured membership_retention','captured membership_retirement','captured active_membership_index','captured membership_actor_attribution',deadline]
+
+
+@pytest.mark.parametrize('defect',[None,'migration','missing_reference','modified_reference','source_pins'])
+def test_trusted_reference_keeps_historical_chain_and_refuses_drift(tmp_path,monkeypatch,defect):
+    import json
+    from test_projection_qualification import digest
+    b=qualification.baseline;calls=[]
+    monkeypatch.setattr(b,'trusted_active_membership_index_reference',lambda:calls.append('index'))
+    monkeypatch.setattr(b,'HERE',tmp_path)
+    (tmp_path/'versions').mkdir();migration=tmp_path/'versions/0015_membership_actor_attribution.py';migration.write_bytes(b'source')
+    (tmp_path/'source-pins.json').write_text('{}')
+    content=json.dumps({'source_pins':{},'migration_sha256':digest(b'source'),'membership_actor_attribution':{}}).encode()
+    path=tmp_path/'membership-actor-attribution-reference.json';path.write_bytes(content)
+    monkeypatch.setattr(b,'MEMBERSHIP_ACTOR_ATTRIBUTION_REFERENCE_SHA256',digest(content))
+    if defect=='migration':migration.write_bytes(b'drift')
+    elif defect=='missing_reference':path.unlink()
+    elif defect=='modified_reference':path.write_bytes(content+b' ')
+    elif defect=='source_pins':(tmp_path/'source-pins.json').write_text('{"changed":"pin"}')
+    if defect:
+        with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_membership_actor_attribution_reference()
+    else:assert b.trusted_membership_actor_attribution_reference()=={}
+    assert calls==['index']
+
+
+@pytest.mark.parametrize('module,args',[('qualify_identity_baseline',['--record-membership-actor-attribution-reference']),('qualify_membership_actor_attribution',[])])
+def test_optimized_execution_refused_before_fixture(module,args):
+    import subprocess
+    source="""import importlib,sys
+sys.path.insert(0,sys.argv[1])
+module=importlib.import_module(sys.argv[2])
+module.fixture=lambda: (_ for _ in ()).throw(RuntimeError('fixture_reached'))
+sys.argv=[module.__file__]+sys.argv[3:]
+try:module.main()
+except RuntimeError as error:
+    if str(error) not in {'membership_actor_attribution_reference_optimized_python_prohibited','membership_actor_attribution_qualification_optimized_python_prohibited'}:raise RuntimeError('wrong_guard')
+else:raise RuntimeError('missing_guard')
+"""
+    result=subprocess.run([sys.executable,'-I','-B','-O','-c',source,str(Path(__file__).resolve().parent),module,*args],capture_output=True,text=True,timeout=10)
+    assert result.returncode==0 and result.stdout==result.stderr==''
+
+
+def failure_fixture_mock(tmp_path,*,create_failure=False,cleanup_fails=False,initially_called=False):
+    import qualify_membership_actor_attribution as retirement
+    import json
+    runner=retirement.MembershipActorAttributionQualification(tmp_path,{})
+    state={'created':False,'called':initially_called};commands=[]
+    def sql(case,statement,values=None):
+        commands.append(statement)
+        if statement.startswith('SELECT last_value,is_called'):
+            assert state['created']
+            return [(1,state['called'])]
+        if statement.startswith('SELECT '):
+            return [('event_trigger','synthetic_membership_actor_attribution_failure'),
+                ('function','synthetic_membership_actor_attribution_failure'),
+                ('sequence','synthetic_membership_actor_attribution_failure_marker')] if state['created'] else []
+        if statement.startswith('CREATE SEQUENCE'):
+            paths=list(tmp_path.glob('membership-actor-attribution-event-restoration-required-*.json'))
+            assert len(paths)==1 and json.loads(paths[0].read_text())['before']==[]
+            assert "WHEN TAG IN ('CREATE TRIGGER')" in statement
+            assert statement.index("to_regprocedure('identity.guard_org_member_actor_attribution()')")<statement.index('pg_catalog.nextval(')<statement.index("RAISE EXCEPTION USING ERRCODE='P0001'")
+            assert 'GRANT USAGE ON SEQUENCE public.synthetic_membership_actor_attribution_failure_marker TO identity_migrator;' in statement
+            assert statement.count('GRANT ')==1
+            state['created']=True
+            if create_failure:raise RuntimeError('synthetic_create_after_commit')
+        if statement.startswith('DROP EVENT TRIGGER'):
+            assert 'DROP FUNCTION IF EXISTS public.synthetic_membership_actor_attribution_failure()' in statement
+            assert 'DROP SEQUENCE IF EXISTS public.synthetic_membership_actor_attribution_failure_marker' in statement
+            if cleanup_fails:raise RuntimeError('synthetic_cleanup_failed')
+            state['created']=False
+        return []
+    runner.admin_sql=sql
+    return runner,state,commands
+
+
+@pytest.mark.parametrize('failure',['create_after_commit','body'])
+def test_after_create_index_failure_fixture_restores_exact_objects(tmp_path,failure):
+    import stat
+    runner,state,commands=failure_fixture_mock(tmp_path,create_failure=failure=='create_after_commit')
+    with pytest.raises(RuntimeError,match='synthetic_'):
+        with runner.failure_fixture('failure'):raise RuntimeError('synthetic_body')
+    assert state['created'] is False
+    paths=list(tmp_path.glob('membership-actor-attribution-event-restored-*.json'))
+    assert len(paths)==1 and stat.S_IMODE(paths[0].stat().st_mode)==0o600
+
+
+@pytest.mark.parametrize('signame',['SIGINT','SIGTERM'])
+@pytest.mark.parametrize('cleanup_fails',[False,True])
+def test_failure_fixture_signal_and_failed_cleanup_keep_witness(tmp_path,monkeypatch,signame,cleanup_fails):
+    import qualify_membership_actor_attribution as retirement
+    signal=retirement.signal
+    originals={signal.SIGINT:object(),signal.SIGTERM:object()};handlers=dict(originals)
+    monkeypatch.setattr(signal,'getsignal',lambda sig:handlers[sig])
+    monkeypatch.setattr(signal,'signal',lambda sig,handler:handlers.__setitem__(sig,handler))
+    runner,state,commands=failure_fixture_mock(tmp_path,cleanup_fails=cleanup_fails)
+    expected='synthetic_cleanup_failed' if cleanup_fails else 'profile_fixture_interrupted'
+    with pytest.raises(RuntimeError,match=expected):
+        with runner.failure_fixture('failure'):handlers[getattr(signal,signame)](getattr(signal,signame),None)
+    assert handlers==originals
+    assert len(list(tmp_path.glob('membership-actor-attribution-event-restoration-required-*.json')))==1
+    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==(0 if cleanup_fails else 1)
+    assert state['created'] is cleanup_fails
+
+
+@pytest.mark.parametrize('kind',['event_trigger','function','sequence'])
+def test_failure_fixture_refuses_preexisting_object_without_mutation(tmp_path,kind):
+    import qualify_membership_actor_attribution as retirement
+    runner=retirement.MembershipActorAttributionQualification(tmp_path,{})
+    commands=[]
+    def sql(case,statement,values=None):commands.append(statement);return [(kind,'synthetic_membership_actor_attribution_failure')]
+    runner.admin_sql=sql
+    with pytest.raises(AssertionError,match='already_exists'):
+        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
+    assert len(commands)==1 and commands[0].startswith('SELECT ')
+    assert not list(tmp_path.glob('membership-actor-attribution-event-*.json'))
+
+
+@pytest.mark.parametrize('fired',[False,True])
+def test_failure_marker_proves_injected_event_before_rollback_claim_and_restores(tmp_path,fired):
+    import json
+    runner,state,commands=failure_fixture_mock(tmp_path)
+    def execute():
+        with runner.failure_fixture('failure') as verify_fired:
+            assert state['called'] is False
+            state['called']=fired
+            verify_fired()
+    if fired:
+        execute()
+        witnesses=list(tmp_path.glob('membership-actor-attribution-event-fired-*.json'))
+        assert len(witnesses)==1
+        assert json.loads(witnesses[0].read_text())=={'case':'failure','marker_before':[1,False],'marker_after':[1,True],'new_guard_observed':True}
+    else:
+        with pytest.raises(AssertionError,match='failure_fixture_not_fired'):execute()
+        assert not list(tmp_path.glob('membership-actor-attribution-event-fired-*.json'))
+    assert state['created'] is False
+    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==1
+
+
+def test_failure_marker_cannot_start_called(tmp_path):
+    runner,state,commands=failure_fixture_mock(tmp_path,initially_called=True)
+    with pytest.raises(AssertionError,match='failure_marker_initially_called'):
+        with runner.failure_fixture('failure'):raise AssertionError('body_reached')
+    assert state['created'] is False
+    assert len(list(tmp_path.glob('membership-actor-attribution-event-restored-*.json')))==1
+
+
+
+
+
+
+@pytest.mark.parametrize('defect', [None, 'missing_false_column', 'extra_column_grant',
+    'new_function_public', 'old_privilege_change', 'unrelated_category_change'])
+def test_catalog_delta_accounts_for_exact_effective_observations(defect):
+    from copy import deepcopy
+    from qualify_membership_actor_attribution import MembershipActorAttributionQualification as Q, FIELDS
+    old={'columns':[], 'constraints':[], 'functions':[], 'triggers':[], 'indexes':['unchanged']}
+    prefixes=('', 'authority_', 'command_', 'projection_', 'target_')
+    for prefix in prefixes:
+        old[prefix+'effective_tables']=[['identity_migrator','org_member','SELECT',True],
+                                      ['restricted','org_member','SELECT',False]]
+        old[prefix+'effective_columns']=[['restricted','org_member','id','SELECT',False]]
+        old[prefix+'effective_functions']=[['identity_migrator','identity','prior','',True],
+                                         ['restricted','identity','prior','',False]]
+    current=deepcopy(old)
+    for category,count in [('columns',2),('constraints',2),('functions',1),('triggers',1)]:
+        current[category]=[[str(i)] for i in range(count)]
+    for prefix in prefixes:
+        current[prefix+'effective_columns'] += [[role,'org_member',field,'SELECT',allowed]
+            for role,allowed in [('identity_migrator',True),('restricted',False)] for field in FIELDS]
+        current[prefix+'effective_functions'] += [[role,'identity','guard_org_member_actor_attribution','',allowed]
+            for role,allowed in [('identity_migrator',True),('restricted',False)]]
+    if defect=='missing_false_column':current['effective_columns'].pop()
+    if defect=='extra_column_grant':current['effective_columns'][-1][-1]=True
+    if defect=='new_function_public':current['effective_functions'][-1][-1]=True
+    if defect=='old_privilege_change':current['effective_columns'][0][-1]=True
+    if defect=='unrelated_category_change':current['indexes'].append('unexpected')
+    if defect:
+        with pytest.raises(AssertionError):Q.verify_catalog_delta(old,current)
+    else:Q.verify_catalog_delta(old,current)
diff --git a/services/access/tests/test_active_membership_index.py b/services/access/tests/test_active_membership_index.py
index 9d5a791..e690a4c 100644
--- a/services/access/tests/test_active_membership_index.py
+++ b/services/access/tests/test_active_membership_index.py
@@ -22,7 +22,9 @@ def test_active_index_required_head_preserves_historical13(monkeypatch):
     monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
     monkeypatch.setattr(b,'verify_owned_history',lambda c:b.ACTIVE_MEMBERSHIP_INDEX_REVISION)
     seen=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:seen.append(k))
-    b.verify_owned_postcondition(object(),require_head=True)
+    # Revision14 remains verifiable history; revision15 is now the required head.
+    b.verify_owned_postcondition(object())
+    with pytest.raises(b.BaselineError,match='identity_unknown_history'):b.verify_owned_postcondition(object(),require_head=True)
     assert seen==['active_membership_index']
     monkeypatch.setattr(b,'verify_owned_history',lambda c:b.MEMBERSHIP_RETIREMENT_REVISION)
     b.verify_owned_postcondition(object())
</unified_diff>
. Read that file — it is the content under review.

Do not invoke any skill, and do not spawn subagents of your own — you are the reviewer. Return your findings as text in your final message; do not route them through any findings-reporting tool the host may offer.
