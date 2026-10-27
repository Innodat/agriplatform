"""Independent person identity and permanent verified account/person links."""
from alembic import op

revision='identity_0022'
down_revision='identity_0021'
branch_labels=None
depends_on=None

SQL=r'''
ALTER TABLE identity.operator_authorities DROP CONSTRAINT operator_authorities_check;
ALTER TABLE identity.operator_authorities ADD CONSTRAINT operator_authorities_check CHECK
 ((scope_kind='platform' AND org_id IS NULL AND command IN ('actor.register_system','account_actor.ensure','person.create','account.link_person'))
 OR (scope_kind='organization' AND org_id IS NOT NULL AND command IN ('membership.join','membership.retire','membership.join_owner')));
ALTER TABLE identity.operator_authorities DROP CONSTRAINT operator_authorities_check1;
ALTER TABLE identity.operator_authorities ADD CONSTRAINT operator_authorities_check1 CHECK
 (command NOT IN ('actor.register_system','person.create') OR target_account_id IS NULL);
CREATE FUNCTION identity.person_executor(p_command text,p_account uuid) RETURNS uuid
LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT executor_actor_id FROM identity.current_operator_authority(p_command,'platform',NULL,p_account)
 WHERE p_command IN ('person.create','account.link_person')
$f$;
CREATE TABLE identity.person(
 id uuid PRIMARY KEY CHECK(id<>'00000000-0000-0000-0000-000000000000'),
 revision bigint NOT NULL DEFAULT 1 CHECK(revision=1),
 created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT statement_timestamp());
ALTER TABLE identity.account_actor ADD CONSTRAINT account_actor_person_reference UNIQUE(account_id,actor_id);
CREATE TABLE identity.account_person(
 account_id uuid PRIMARY KEY REFERENCES identity.account_actor(account_id) ON DELETE RESTRICT,
 person_id uuid NOT NULL REFERENCES identity.person(id) ON DELETE RESTRICT,
 actor_id uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 revision bigint NOT NULL DEFAULT 1 CHECK(revision=1),
 FOREIGN KEY(account_id,actor_id) REFERENCES identity.account_actor(account_id,actor_id) ON DELETE RESTRICT,
 evidence_ref text NOT NULL CHECK(evidence_ref COLLATE "C" ~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' AND position('://' in evidence_ref)=0),
 created_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 updated_by uuid NOT NULL REFERENCES identity.actor(id) ON DELETE RESTRICT,
 created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
 updated_at timestamptz NOT NULL DEFAULT statement_timestamp());
CREATE FUNCTION identity.guard_person_identity() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;
BEGIN
 IF TG_OP<>'INSERT' THEN RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_person_history_retained'; END IF;
 IF TG_TABLE_NAME='person' THEN executor:=identity.person_executor('person.create',NULL);
 ELSE
  executor:=identity.person_executor('account.link_person',NEW.account_id);
  IF NOT EXISTS(SELECT 1 FROM identity.account_actor m WHERE m.account_id=NEW.account_id AND m.actor_id=NEW.actor_id AND m.actor_kind='account') THEN
   RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_person_actor_mismatch'; END IF;
 END IF;
 IF current_user<>'identity_command_owner' OR executor IS NULL THEN
  RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_person_owner_required'; END IF;
 NEW.revision:=1;NEW.created_by:=executor;NEW.updated_by:=executor;
 NEW.created_at:=statement_timestamp();NEW.updated_at:=NEW.created_at;RETURN NEW;
END $f$;
CREATE TRIGGER person_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.person FOR EACH ROW EXECUTE FUNCTION identity.guard_person_identity();
CREATE TRIGGER person_retention BEFORE TRUNCATE ON identity.person FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_person_identity();
CREATE TRIGGER account_person_guard BEFORE INSERT OR UPDATE OR DELETE ON identity.account_person FOR EACH ROW EXECUTE FUNCTION identity.guard_person_identity();
CREATE TRIGGER account_person_retention BEFORE TRUNCATE ON identity.account_person FOR EACH STATEMENT EXECUTE FUNCTION identity.guard_person_identity();
ALTER TABLE identity.person ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.person FORCE ROW LEVEL SECURITY;
ALTER TABLE identity.account_person ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.account_person FORCE ROW LEVEL SECURITY;
CREATE POLICY migration_inspection ON identity.person FOR SELECT TO identity_migrator USING(true);
CREATE POLICY migration_inspection ON identity.account_person FOR SELECT TO identity_migrator USING(true);
CREATE POLICY person_commands ON identity.person TO identity_command_owner
 USING(identity.person_executor('person.create',NULL) IS NOT NULL OR identity.person_link_creation_executor() IS NOT NULL)
 WITH CHECK(identity.person_executor('person.create',NULL) IS NOT NULL);
CREATE POLICY person_links ON identity.account_person TO identity_command_owner
 USING(identity.person_executor('account.link_person',account_id) IS NOT NULL)
 WITH CHECK(identity.person_executor('account.link_person',account_id) IS NOT NULL);
CREATE POLICY person_projection ON identity.account_person FOR SELECT TO identity_account_projection_owner
 USING(current_setting('app.context_kind',true)='user' AND account_id::text=lower(current_setting('app.account_id',true)));
GRANT SELECT,INSERT ON identity.person,identity.account_person TO identity_command_owner;
GRANT SELECT(account_id,person_id,actor_id,revision) ON identity.account_person TO identity_account_projection_owner;
CREATE FUNCTION identity.person_account_profile(p_account uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT EXISTS(SELECT 1 FROM identity.users u WHERE u.id=p_account AND u.deleted_at IS NULL AND u.is_system IS NOT TRUE
 AND u.actor_key IS NULL AND identity.person_executor('account.link_person',p_account) IS NOT NULL)
$f$;
CREATE POLICY person_link_verification ON identity.users FOR SELECT TO identity_account_verification_owner
 USING(identity.person_executor('account.link_person',id) IS NOT NULL);
CREATE FUNCTION identity.current_account_person() RETURNS TABLE(account_id uuid,actor_id uuid,person_id uuid,revision bigint)
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
 SELECT a.account_id,a.actor_id,m.person_id,m.revision FROM identity.current_account_actor() a
 LEFT JOIN identity.account_person m ON m.account_id=a.account_id AND m.actor_id=a.actor_id
$f$;
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_command_type_check;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_command_type_check CHECK(command_type IN
 ('actor.register_system','account_actor.ensure','membership.retire','membership.join','person.create','account.link_person'));
ALTER TABLE identity.operation_outcome DROP CONSTRAINT operation_outcome_check1;
ALTER TABLE identity.operation_outcome ADD CONSTRAINT operation_outcome_check1 CHECK(initiator_actor_id IS NULL AND
 ((command_type IN ('actor.register_system','account_actor.ensure','person.create','account.link_person') AND scope_kind='platform')
 OR (command_type IN ('membership.retire','membership.join') AND scope_kind='organization')));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_event_type_check;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_event_type_check CHECK(event_type IN
 ('identity.actor_registered','identity.account_actor_ensured','identity.membership_retired','identity.membership_joined','identity.person_created','identity.account_person_linked'));
ALTER TABLE identity.business_event DROP CONSTRAINT business_event_check1;
ALTER TABLE identity.business_event ADD CONSTRAINT business_event_check1 CHECK(initiator_actor_id IS NULL AND
 ((event_type IN ('identity.actor_registered','identity.account_actor_ensured','identity.person_created','identity.account_person_linked') AND scope_kind='platform')
 OR (event_type IN ('identity.membership_retired','identity.membership_joined') AND scope_kind='organization')));
CREATE POLICY person_outcomes ON identity.operation_outcome TO identity_command_owner
 USING(command_type IN ('person.create','account.link_person') AND scope_kind='platform'
 AND executor_actor_id=identity.person_executor(command_type,(result->'target'->>'account_id')::uuid))
 WITH CHECK(command_type IN ('person.create','account.link_person') AND scope_kind='platform'
 AND executor_actor_id=identity.person_executor(command_type,(result->'target'->>'account_id')::uuid));
CREATE POLICY person_events ON identity.business_event TO identity_command_owner
 USING(event_type IN ('identity.person_created','identity.account_person_linked') AND scope_kind='platform'
 AND executor_actor_id=identity.person_executor(CASE event_type WHEN 'identity.person_created' THEN 'person.create' ELSE 'account.link_person' END,(target->>'account_id')::uuid))
 WITH CHECK(event_type IN ('identity.person_created','identity.account_person_linked') AND scope_kind='platform'
 AND executor_actor_id=identity.person_executor(CASE event_type WHEN 'identity.person_created' THEN 'person.create' ELSE 'account.link_person' END,(target->>'account_id')::uuid));
'''
# Called only after exact person command authority has been established. It discloses
# no person catalogue, merely permits validating an explicit target under that authority.
CREATION_EXECUTOR=r'''
CREATE FUNCTION identity.person_link_creation_executor() RETURNS uuid LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $f$
 SELECT p.executor_actor_id FROM identity.operator_principals p JOIN identity.operator_authorities a USING(database_login)
 WHERE p.database_login=session_user AND p.enabled AND a.enabled AND a.command='account.link_person'
 AND a.scope_kind='platform' AND a.application_id IS NULL ORDER BY a.id LIMIT 1
$f$;
'''

EVIDENCE_BRANCH=r'''
 IF TG_OP='INSERT' AND (coalesce(to_jsonb(NEW)->>'command_type','') IN ('person.create','account.link_person')
 OR coalesce(to_jsonb(NEW)->>'event_type','') IN ('identity.person_created','identity.account_person_linked')) THEN
  IF TG_TABLE_NAME='operation_outcome' THEN
   IF current_user<>'identity_command_owner' OR NEW.executor_actor_id IS DISTINCT FROM
    identity.person_executor(NEW.command_type,(NEW.result->'target'->>'account_id')::uuid) THEN
    RAISE EXCEPTION USING ERRCODE='42501',MESSAGE='identity_person_owner_required'; END IF;
   IF NEW.command_version<>1 OR NEW.result_version<>1 OR NEW.scope_kind<>'platform' OR NEW.scope_id IS NOT NULL
    OR NEW.result->>'revision' IS DISTINCT FROM '1' OR NEW.result->>'disposition' IS NULL
    OR NEW.result->>'disposition' NOT IN ('created','unchanged')
    OR (NEW.result->>'disposition'='created') IS DISTINCT FROM (NEW.result->>'event_id' IS NOT NULL)
    OR (NEW.result->>'event_id')::uuid='00000000-0000-0000-0000-000000000000'::uuid
    OR NEW.result IS DISTINCT FROM jsonb_build_object('target',NEW.result->'target','disposition',NEW.result->>'disposition','revision','1','event_id',NEW.result->'event_id')
    OR (NEW.command_type='person.create' AND NOT EXISTS(SELECT 1 FROM identity.person p WHERE p.id=(NEW.result->'target'->>'person_id')::uuid
      AND NEW.result->'target'=jsonb_build_object('person_id',p.id)))
    OR (NEW.command_type='account.link_person' AND NOT EXISTS(SELECT 1 FROM identity.account_person m
      WHERE m.account_id=(NEW.result->'target'->>'account_id')::uuid AND NEW.result->'target'=jsonb_build_object('account_id',m.account_id,'person_id',m.person_id,'actor_id',m.actor_id))) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_person_result_invalid'; END IF;
   NEW.committed_at:=statement_timestamp();
  ELSE
   SELECT * INTO o FROM identity.operation_outcome WHERE id=NEW.outcome_id;
   IF current_user<>'identity_command_owner' OR o.id IS NULL OR o.command_type NOT IN ('person.create','account.link_person')
    OR NEW.executor_actor_id IS DISTINCT FROM identity.person_executor(o.command_type,(NEW.target->>'account_id')::uuid)
    OR NEW.event_type IS DISTINCT FROM (CASE o.command_type WHEN 'person.create' THEN 'identity.person_created' ELSE 'identity.account_person_linked' END)
    OR NEW.event_version<>1 OR NEW.scope_kind IS DISTINCT FROM o.scope_kind OR NEW.scope_id IS DISTINCT FROM o.scope_id
    OR NEW.executor_actor_id IS DISTINCT FROM o.executor_actor_id OR NEW.initiator_actor_id IS DISTINCT FROM o.initiator_actor_id
    OR NEW.event_id IS DISTINCT FROM (o.result->>'event_id')::uuid OR o.result->>'disposition'<>'created'
    OR NEW.target IS DISTINCT FROM o.result->'target'
    OR NEW.target_key IS DISTINCT FROM (CASE o.command_type WHEN 'person.create' THEN NEW.target->>'person_id' ELSE NEW.target->>'account_id' END)
    OR NEW.transition IS DISTINCT FROM jsonb_build_object('before',NULL,'after',jsonb_build_object('revision','1'))
    OR (o.command_type='account.link_person' AND (NEW.evidence_ref IS NULL OR NOT EXISTS(SELECT 1 FROM identity.account_person m
      WHERE m.account_id=(NEW.target->>'account_id')::uuid AND m.evidence_ref=NEW.evidence_ref))) THEN
    RAISE EXCEPTION USING ERRCODE='23514',MESSAGE='identity_person_event_invalid'; END IF;
   NEW.created_at:=o.committed_at;
  END IF;RETURN NEW;
 END IF;
'''

# One fixed SQL function per command; shared source construction keeps their lock,
# replay and compact evidence logic identical without adding a runtime engine.
def command_sql(link):
    name='account.link_person' if link else 'person.create'
    function='link_person' if link else 'create_person'
    params='p_account uuid,p_person uuid,p_actor uuid,p_revision bigint,' if link else 'p_person uuid,'
    target="jsonb_build_object('account_id',p_account,'person_id',p_person,'actor_id',p_actor)" if link else "jsonb_build_object('person_id',p_person)"
    payload=("',\"payload\":{\"account_id\":'||to_json(p_account::text)::text||',\"actor_id\":'||to_json(p_actor::text)::text||CASE WHEN p_revision IS NULL THEN ',\"expected_absent\":true' ELSE ',\"expected_revision\":'||to_json(p_revision::text)::text END||',\"person_id\":'||to_json(p_person::text)::text||'}'" if link else "',\"payload\":{\"expected_absent\":true,\"person_id\":'||to_json(p_person::text)::text||'}'")
    validation="""
 IF p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000'::uuid
 OR p_actor IS NULL OR p_actor='00000000-0000-0000-0000-000000000000'::uuid
 OR (p_revision IS NOT NULL AND p_revision<=0) OR p_evidence IS NULL THEN
 RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
""" if link else ''
    observe="""
 observed:=clock_timestamp();
 IF NOT identity.verify_person_account(p_account) THEN
 RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_account_ineligible'; END IF;
""" if link else ''
    state="""
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:account-actor:v1:'||p_account::text));
 IF clock_timestamp()-observed>interval '5 seconds' THEN
 RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 IF NOT identity.person_account_profile(p_account) OR NOT EXISTS(SELECT 1 FROM identity.account_actor a
 WHERE a.account_id=p_account AND a.actor_id=p_actor AND a.actor_kind='account')
 OR NOT EXISTS(SELECT 1 FROM identity.person p WHERE p.id=p_person) THEN
 RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_mapping_conflict'; END IF;
 SELECT * INTO mapping FROM identity.account_person m WHERE m.account_id=p_account;
 IF FOUND THEN
  IF mapping.person_id<>p_person OR mapping.actor_id<>p_actor OR (p_revision IS NOT NULL AND p_revision<>mapping.revision) THEN
  RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_mapping_conflict'; END IF;
  disposition:='unchanged';
 ELSE
  IF p_revision IS NOT NULL THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_expected_state_conflict'; END IF;
  INSERT INTO identity.account_person(account_id,person_id,actor_id,evidence_ref,created_by,updated_by)
  VALUES(p_account,p_person,p_actor,p_evidence,executor,executor);
  disposition:='created';event_id:=gen_random_uuid();
 END IF;
""" if link else """
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:person-id:v1:'||p_person::text));
 IF EXISTS(SELECT 1 FROM identity.person p WHERE p.id=p_person) THEN disposition:='unchanged';
 ELSE
 INSERT INTO identity.person(id,created_by,updated_by) VALUES(p_person,executor,executor);
 disposition:='created';event_id:=gen_random_uuid();END IF;
"""
    account='p_account' if link else 'NULL'
    event='identity.account_person_linked' if link else 'identity.person_created'
    key='p_account' if link else 'p_person'
    return r'''
CREATE FUNCTION identity.FUNCTION(p_operation uuid,PARAMSp_reason text,p_evidence text,p_canonical bytea)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;canonical text;lock_document text;saved identity.operation_outcome;mapping identity.account_person;
 outcome_id uuid;event_id uuid;response jsonb;disposition text;observed timestamptz;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_operation IS NULL
 OR p_operation='00000000-0000-0000-0000-000000000000'::uuid OR p_person IS NULL
 OR p_person='00000000-0000-0000-0000-000000000000'::uuid OR p_reason IS NULL
 OR p_reason NOT IN ('initial_setup','synthetic_fixture','identity_adoption','access_change','setup_correction')
 OR (p_evidence IS NOT NULL AND (p_evidence COLLATE "C" !~ '^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}$' OR position('://' in p_evidence)>0)) THEN
 RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
VALIDATION
 canonical:='{"command":"COMMAND","evidence_ref":'||coalesce(to_json(p_evidence)::text,'null')||',"operation_id":'||to_json(p_operation::text)::text||
 PAYLOAD||',"reason_code":'||to_json(p_reason)::text||',"schema_version":1,"scope":{"kind":"platform"}}';
 IF p_canonical IS DISTINCT FROM convert_to(canonical,'UTF8') THEN
 RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid'; END IF;
 executor:=identity.person_executor('COMMAND',ACCOUNT);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied'; END IF;
OBSERVE
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":"COMMAND","lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy';END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.person_executor('COMMAND',ACCOUNT) THEN
 RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied';END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type='COMMAND' AND o.operation_id=p_operation;
 IF FOUND THEN
 IF saved.command_version<>1 OR saved.result_version<>1 OR saved.fingerprint_version<>1
 OR saved.fingerprint_algorithm<>'sha256' OR saved.fingerprint_key_id IS NOT NULL THEN
 RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable'; END IF;
 IF saved.fingerprint<>sha256(p_canonical) THEN RAISE EXCEPTION USING ERRCODE='IC003',MESSAGE='identity_operation_conflict'; END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;RETURN;END IF;
STATE
 outcome_id:=gen_random_uuid();response:=jsonb_build_object('target',TARGET,'disposition',disposition,'revision','1','event_id',event_id);
 INSERT INTO identity.operation_outcome(id,scope_kind,scope_id,executor_actor_id,command_type,operation_id,command_version,
 fingerprint_version,fingerprint_algorithm,fingerprint_key_id,fingerprint,result_version,result,initiator_actor_id)
 VALUES(outcome_id,'platform',NULL,executor,'COMMAND',p_operation,1,1,'sha256',NULL,sha256(p_canonical),1,response,NULL) RETURNING * INTO saved;
 IF event_id IS NOT NULL THEN
 INSERT INTO identity.business_event(event_id,event_type,event_version,scope_kind,scope_id,executor_actor_id,initiator_actor_id,
 outcome_id,target_key,target,transition,reason_code,evidence_ref)
 VALUES(event_id,'EVENT',1,'platform',NULL,executor,NULL,outcome_id,KEY::text,TARGET,
 jsonb_build_object('before',NULL,'after',jsonb_build_object('revision','1')),p_reason,p_evidence);END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
'''.replace('FUNCTION(',function+'(',1).replace('PARAMS',params).replace('COMMAND',name).replace('ACCOUNT',account).replace('VALIDATION',validation).replace('OBSERVE',observe).replace('PAYLOAD',payload).replace('STATE',state).replace('TARGET',target).replace('EVENT',event).replace('KEY::',key+'::')

OUTCOME=r'''
CREATE FUNCTION identity.person_command_outcome(p_command text,p_operation uuid,p_person uuid,p_account uuid)
RETURNS TABLE(result jsonb,command_version integer,result_version integer,committed_at timestamptz)
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $f$
DECLARE executor uuid;saved identity.operation_outcome;lock_document text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' OR p_command IS NULL OR p_command NOT IN ('person.create','account.link_person')
 OR p_operation IS NULL OR p_operation='00000000-0000-0000-0000-000000000000' OR p_person IS NULL
 OR p_person='00000000-0000-0000-0000-000000000000'
 OR (p_command='person.create' AND p_account IS NOT NULL)
 OR (p_command='account.link_person' AND (p_account IS NULL OR p_account='00000000-0000-0000-0000-000000000000')) THEN
 RAISE EXCEPTION USING ERRCODE='IC005',MESSAGE='identity_command_invalid';END IF;
 executor:=identity.person_executor(p_command,p_account);
 IF executor IS NULL THEN RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied';END IF;
 lock_document:='{"caller_id":'||to_json(executor::text)::text||',"caller_kind":"actor","command_type":'||to_json(p_command)::text||',"lock_version":1,"operation_id":'||
 to_json(p_operation::text)::text||',"owner_schema":"identity","scope_id":null,"scope_kind":"platform"}';
 BEGIN PERFORM pg_advisory_xact_lock(identity.command_lock(lock_document));
 EXCEPTION WHEN lock_not_available THEN RAISE EXCEPTION USING ERRCODE='IC001',MESSAGE='identity_operation_busy';END;
 PERFORM pg_advisory_xact_lock(identity.command_lock('identity:operator-authority:v1:'||session_user::text));
 IF executor IS DISTINCT FROM identity.person_executor(p_command,p_account) THEN
 RAISE EXCEPTION USING ERRCODE='IC002',MESSAGE='identity_command_denied';END IF;
 SELECT * INTO saved FROM identity.operation_outcome o WHERE o.scope_kind='platform' AND o.scope_id IS NULL
 AND o.executor_actor_id=executor AND o.command_type=p_command AND o.operation_id=p_operation
 AND o.result->'target'->>'person_id'=p_person::text
 AND (p_command='person.create' OR o.result->'target'->>'account_id'=p_account::text);
 IF NOT FOUND THEN RETURN;END IF;
 IF saved.command_version<>1 OR saved.result_version<>1 OR saved.fingerprint_version<>1
 OR saved.fingerprint_algorithm<>'sha256' OR saved.fingerprint_key_id IS NOT NULL THEN
 RAISE EXCEPTION USING ERRCODE='IC004',MESSAGE='identity_verification_unavailable';END IF;
 RETURN QUERY SELECT saved.result,saved.command_version,saved.result_version,saved.committed_at;
END $f$;
'''

def upgrade():
    from identity_baseline import verify_catalog
    from studies_migration_support import strip_acl,transfer_functions
    connection=op.get_bind()
    verify_catalog(connection,'studies_setup')
    # Extend the authenticated allowlist in place, retaining all original role/target checks.
    connection.exec_driver_sql('GRANT CREATE ON SCHEMA identity TO identity_operator_authority_owner')
    connection.exec_driver_sql('SET LOCAL ROLE identity_operator_authority_owner')
    definition=connection.exec_driver_sql("SELECT pg_get_functiondef('identity.current_operator_authority(text,text,uuid,uuid)'::regprocedure)").scalar_one()
    definition=definition.replace("$1 = 'actor.register_system'","$1 IN ('actor.register_system','person.create')").replace("$1 = 'account_actor.ensure'","$1 IN ('account_actor.ensure','account.link_person')")
    connection.exec_driver_sql(definition,execution_options={'no_parameters':True})
    connection.exec_driver_sql('RESET ROLE')
    connection.exec_driver_sql('REVOKE CREATE ON SCHEMA identity FROM identity_operator_authority_owner')
    connection.exec_driver_sql(CREATION_EXECUTOR,execution_options={'no_parameters':True})
    connection.exec_driver_sql(SQL,execution_options={'no_parameters':True})
    # The verified predecessor pins the guard. Insert one bounded family branch;
    # immutable UPDATE/DELETE/TRUNCATE handling and other commands remain intact.
    definition=connection.exec_driver_sql("SELECT pg_get_functiondef('identity.guard_command_evidence()'::regprocedure)").scalar_one()
    connection.exec_driver_sql(definition.replace('BEGIN\n','BEGIN\n'+EVIDENCE_BRANCH,1),execution_options={'no_parameters':True})
    definition=connection.exec_driver_sql("SELECT pg_get_functiondef('identity.verify_account_actor_account(uuid)'::regprocedure)").scalar_one()
    definition=definition.replace('verify_account_actor_account','verify_person_account').replace('identity.account_actor_executor(p_account)',"identity.person_executor('account.link_person',p_account)").replace('identity.account_actor_profile(p_account)','identity.person_account_profile(p_account)')
    connection.exec_driver_sql(definition,execution_options={'no_parameters':True})
    connection.exec_driver_sql(command_sql(False)+command_sql(True)+OUTCOME,execution_options={'no_parameters':True})
    routines=('person_executor','person_link_creation_executor','guard_person_identity','person_account_profile','verify_person_account','current_account_person','create_person','link_person','person_command_outcome')
    strip_acl(connection,'identity',routines)
    # Remove inherited broad table defaults before granting the fixed owner seams.
    for table in ('person','account_person'):
        rows=connection.exec_driver_sql("SELECT DISTINCT CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(a.grantee)) END FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a WHERE c.oid='identity."+table+"'::regclass AND a.grantee<>c.relowner").scalars().all()
        for role in rows:connection.exec_driver_sql('REVOKE ALL ON identity.'+table+' FROM '+role)
    connection.exec_driver_sql('''
GRANT SELECT,INSERT ON identity.person,identity.account_person TO identity_command_owner;
GRANT SELECT(account_id,person_id,actor_id,revision) ON identity.account_person TO identity_account_projection_owner;
GRANT EXECUTE ON FUNCTION identity.person_executor(text,uuid) TO identity_command_owner,identity_account_verification_owner;
GRANT EXECUTE ON FUNCTION identity.person_link_creation_executor() TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.person_account_profile(uuid),identity.verify_person_account(uuid) TO identity_command_owner;
GRANT EXECUTE ON FUNCTION identity.current_account_person() TO access_runtime;
GRANT EXECUTE ON FUNCTION identity.create_person(uuid,uuid,text,text,bytea),identity.link_person(uuid,uuid,uuid,uuid,bigint,text,text,bytea),identity.person_command_outcome(text,uuid,uuid,uuid) TO identity_operator;
''')
    transfer_functions(connection,'identity','identity_operator_authority_owner',('person_link_creation_executor()',))
    transfer_functions(connection,'identity','identity_account_verification_owner',('person_account_profile(uuid)','verify_person_account(uuid)'))
    transfer_functions(connection,'identity','identity_account_projection_owner',('current_account_person()',))
    transfer_functions(connection,'identity','identity_command_owner',('person_executor(text,uuid)','create_person(uuid,uuid,text,text,bytea)','link_person(uuid,uuid,uuid,uuid,bigint,text,text,bytea)','person_command_outcome(text,uuid,uuid,uuid)'))

def downgrade():raise RuntimeError('Destructive rollback is not supported; use the recovery runbook')
