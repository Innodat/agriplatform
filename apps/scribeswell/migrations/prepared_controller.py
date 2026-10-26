"""Closed prepared-controller v1 checks. Local custody is not Identity verification."""
import json
from baseline import APP, REVISION, BaselineError, _checked_authority_ledger
from catalogue import snapshot

OPERATOR = 'scribeswell_corpus_operator'
ENTRIES = ('execute_corpus_command', 'lookup_corpus_command_outcome')
TABLES = ('corpus_operator_principal', 'corpus_operator_authority', 'corpus_fence_control',
          'corpus_epoch', 'corpus_attempt', 'corpus_command_outcome', 'corpus_write_binding')


def deny(code):
    raise BaselineError('scribeswell_prepared_' + code)


def custody(value):
    from release_profile import validate_custody
    try:
        return validate_custody(value)
    except ValueError:
        deny('custody_invalid')


def acl(connection, value):
    return sorted(tuple(row) for row in connection.exec_driver_sql("""SELECT pg_get_userbyid(grantor),
        CASE WHEN grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(grantee) END,
        privilege_type,is_grantable FROM aclexplode(%s::aclitem[])""",(value,)).fetchall())


def catalogue(connection, expected):
    actual = snapshot(connection,head=True)
    # Only these exact cells may change; compare every ACL entry including grantor.
    pairs = [(actual['schema'][0], expected['schema'][0], 2, 'USAGE')]
    for name in ENTRIES:
        observed = [row for row in actual['functions'] if row[0] == name]
        pinned = [row for row in expected['functions'] if row[0] == name]
        if len(observed) != 1 or len(pinned) != 1:
            deny('catalogue_mismatch')
        pairs.append((observed[0],pinned[0],6,'EXECUTE'))
    for observed,pinned,index,privilege in pairs:
        required = acl(connection,pinned[index]) + [('scribeswell_migrator',OPERATOR,privilege,False)]
        if acl(connection,observed[index]) != sorted(required):
            deny('catalogue_mismatch')
        observed[index] = pinned[index]
    if actual != expected:
        deny('catalogue_mismatch')


def operator(connection, *, publication=False):
    role = connection.exec_driver_sql("SELECT rolcanlogin,rolsuper,rolbypassrls,rolcreatedb,rolcreaterole,rolreplication,rolinherit FROM pg_roles WHERE rolname=%s",(OPERATOR,)).first()
    if role is None or tuple(role) != (True,False,False,False,False,False,False):
        deny('operator_authority')
    if connection.exec_driver_sql("""SELECT 1 FROM pg_auth_members m JOIN pg_roles r
        ON r.oid=m.member OR r.oid=m.roleid WHERE r.rolname=%s""",(OPERATOR,)).first():
        deny('operator_authority')
    # Only the existing timeout settings are safe in this qualified profile.
    if connection.exec_driver_sql("""SELECT 1 FROM pg_db_role_setting s WHERE (s.setrole=(SELECT oid FROM pg_roles WHERE rolname=%s)
        OR (s.setrole=0 AND s.setdatabase=(SELECT oid FROM pg_database WHERE datname=current_database())))
        AND EXISTS (SELECT FROM unnest(s.setconfig) x WHERE split_part(x,'=',1) NOT IN
        ('statement_timeout','lock_timeout','idle_in_transaction_session_timeout'))""",(OPERATOR,)).first():
        deny('operator_authority')
    query = """WITH actor AS (SELECT oid FROM pg_roles WHERE rolname=%s),
    profile AS (SELECT %s::boolean AS publication),
    allowed_routines AS (
      SELECT unnest(ARRAY['scribeswell.execute_corpus_command(jsonb)'::regprocedure::oid,
        'scribeswell.lookup_corpus_command_outcome(jsonb)'::regprocedure::oid]) AS oid
      UNION ALL SELECT to_regprocedure(name)::oid FROM profile,
        unnest(ARRAY['scribeswell.execute_corpus_publication(jsonb)',
                     'scribeswell.lookup_corpus_publication_outcome(jsonb)']) name WHERE publication),
    allowed_reads AS (SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace,profile
      WHERE publication AND n.nspname='scribeswell' AND c.relname IN
       ('book','chapter','verse','word','corpus_fence_control','corpus_epoch','corpus_attempt',
        'corpus_operator_principal','corpus_operator_authority')),
    business AS (SELECT * FROM pg_namespace WHERE nspname NOT IN ('pg_catalog','information_schema') AND left(nspname,3)<>'pg_')
    SELECT 1 FROM pg_shdepend d,actor WHERE d.refclassid='pg_authid'::regclass AND d.refobjid=actor.oid
       AND (d.deptype='o' OR (d.deptype='a' AND NOT (
         d.dbid=(SELECT oid FROM pg_database WHERE datname=current_database()) AND
         ((d.classid='pg_class'::regclass AND d.objid IN (SELECT oid FROM allowed_reads)) OR
          (d.classid='pg_namespace'::regclass AND d.objid='scribeswell'::regnamespace) OR
          (d.classid='pg_proc'::regclass AND d.objid IN (SELECT oid FROM allowed_routines))))))
    UNION ALL SELECT 1 FROM pg_namespace n,actor WHERE n.nspowner=actor.oid
    UNION ALL SELECT 1 FROM pg_class c,actor WHERE c.relowner=actor.oid
    UNION ALL SELECT 1 FROM pg_proc p,actor WHERE p.proowner=actor.oid
    UNION ALL SELECT 1 FROM pg_type t,actor WHERE t.typowner=actor.oid
    UNION ALL SELECT 1 FROM pg_database d,actor WHERE d.datdba=actor.oid OR has_database_privilege(actor.oid,d.oid,'CREATE')
    UNION ALL SELECT 1 FROM pg_foreign_data_wrapper w,actor WHERE has_foreign_data_wrapper_privilege(actor.oid,w.oid,'USAGE')
    UNION ALL SELECT 1 FROM pg_foreign_server s,actor WHERE has_server_privilege(actor.oid,s.oid,'USAGE')
    UNION ALL SELECT 1 FROM pg_tablespace t,actor WHERE has_tablespace_privilege(actor.oid,t.oid,'CREATE')
    UNION ALL SELECT 1 FROM pg_parameter_acl p LEFT JOIN pg_settings s ON s.name=p.parname,actor
       WHERE has_parameter_privilege(actor.oid,p.parname,'ALTER SYSTEM') OR
       (s.context IS DISTINCT FROM 'user' AND has_parameter_privilege(actor.oid,p.parname,'SET'))
    UNION ALL SELECT 1 FROM business n,actor WHERE has_schema_privilege(actor.oid,n.oid,'CREATE')
    UNION ALL SELECT 1 FROM pg_namespace n,LATERAL aclexplode(n.nspacl) a,actor WHERE a.grantee=actor.oid AND NOT (n.nspname='scribeswell' AND a.privilege_type='USAGE' AND a.grantor=n.nspowner AND NOT a.is_grantable)
    UNION ALL SELECT 1 FROM pg_class c,LATERAL aclexplode(c.relacl) a,actor WHERE a.grantee=actor.oid AND NOT (c.oid IN (SELECT oid FROM allowed_reads)
       AND a.privilege_type='SELECT' AND a.grantor=c.relowner AND NOT a.is_grantable)
    UNION ALL SELECT 1 FROM pg_attribute col,LATERAL aclexplode(col.attacl) a,actor WHERE a.grantee=actor.oid
    UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace,LATERAL aclexplode(p.proacl) a,actor
       WHERE a.grantee=actor.oid AND NOT (n.nspname='scribeswell' AND p.oid IN (SELECT oid FROM allowed_routines) AND a.privilege_type='EXECUTE' AND a.grantor=p.proowner AND NOT a.is_grantable)
    UNION ALL SELECT 1 FROM pg_default_acl d,LATERAL aclexplode(d.defaclacl) a,actor WHERE a.grantee=actor.oid OR d.defaclrole=actor.oid
    UNION ALL SELECT 1 FROM pg_default_acl d,LATERAL aclexplode(d.defaclacl) a,actor
       WHERE a.grantee=0 AND d.defaclobjtype IN ('r','S') AND
       (d.defaclnamespace=0 OR has_schema_privilege(actor.oid,d.defaclnamespace,'USAGE'))
    UNION ALL SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
       JOIN pg_init_privs i ON i.classoid='pg_catalog.pg_proc'::regclass AND i.objoid=p.oid
       AND i.objsubid=0 AND i.privtype='i',actor
       WHERE n.nspname='pg_catalog' AND has_function_privilege(actor.oid,p.oid,'EXECUTE')
       AND NOT EXISTS (SELECT 1 FROM aclexplode(i.initprivs) a WHERE a.privilege_type='EXECUTE'
          AND CASE WHEN a.grantee=0 THEN true ELSE pg_has_role(actor.oid,a.grantee,'USAGE') END)
    UNION ALL SELECT 1 FROM pg_class c JOIN business n ON n.oid=c.relnamespace,actor
       WHERE c.relkind IN ('r','p','v','m','f','S') AND has_schema_privilege(actor.oid,n.oid,'USAGE') AND
       CASE WHEN c.relkind='S' THEN has_sequence_privilege(actor.oid,c.oid,'USAGE,SELECT,UPDATE')
       ELSE has_table_privilege(actor.oid,c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER,MAINTAIN')
        OR has_any_column_privilege(actor.oid,c.oid,'INSERT,UPDATE,REFERENCES')
        OR ((has_table_privilege(actor.oid,c.oid,'SELECT') OR has_any_column_privilege(actor.oid,c.oid,'SELECT'))
           AND c.oid NOT IN (SELECT oid FROM allowed_reads)) END
    UNION ALL SELECT 1 FROM pg_proc p JOIN business n ON n.oid=p.pronamespace,actor
       WHERE p.prosecdef AND has_schema_privilege(actor.oid,n.oid,'USAGE') AND has_function_privilege(actor.oid,p.oid,'EXECUTE')
       AND NOT (n.nspname='scribeswell' AND p.oid IN (SELECT oid FROM allowed_routines))
    """
    forbidden=connection.exec_driver_sql(query,(OPERATOR,publication)).first()
    if forbidden:
        deny('operator_authority')


def custody_state(connection, expected):
    principal = connection.exec_driver_sql("""SELECT database_login,executor_actor_id::text,actor_kind,actor_key,preparation_evidence_ref,
        revision>0 AND created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid
        AND updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid AND isfinite(created_at) AND isfinite(updated_at)
        FROM scribeswell.corpus_operator_principal LIMIT 2""").fetchall()
    required = [(OPERATOR,expected['executor_actor_id'],expected['actor_kind'],expected['actor_key'],expected['preparation_evidence_ref'],True)]
    if [tuple(row) for row in principal] != required:
        deny('custody_mismatch')
    authority = connection.exec_driver_sql("""SELECT database_login,source_id,command,
        revision>0 AND created_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid
        AND updated_by_actor_id<>'00000000-0000-0000-0000-000000000000'::uuid AND isfinite(created_at) AND isfinite(updated_at)
        FROM scribeswell.corpus_operator_authority ORDER BY command LIMIT 4""").fetchall()
    if [tuple(row) for row in authority] != [(OPERATOR,expected['source_id'],'corpus.'+command,True) for command in ('begin','recover','seal')]:
        deny('custody_mismatch')


def local_state(connection, expected):
    custody_state(connection, expected)
    if connection.exec_driver_sql('SELECT singleton,enforcement FROM scribeswell.corpus_fence_control').fetchall() != [(True,False)]:
        deny('dormant_state_required')
    for table in TABLES[3:]:
        if connection.exec_driver_sql('SELECT 1 FROM scribeswell.'+table+' LIMIT 1').first():
            deny('dormant_state_required')


def checked_prepared(connection, expected_actor, *, controller_history=False):
    expected = custody(expected_actor)
    if not connection.in_transaction() or connection.connection.dbapi_connection.autocommit or connection.get_isolation_level() != 'READ COMMITTED' or connection.exec_driver_sql('SHOW transaction_read_only').scalar() != 'off':
        deny('transaction_required')
    # Explicit temp placement prevents implicit pg_temp precedence over catalogues.
    connection.exec_driver_sql('SET LOCAL search_path=pg_catalog,pg_temp')
    # These are ceilings, not permission to widen a caller's shorter deadline.
    for name,ceiling in (('statement_timeout',5000),('lock_timeout',2000)):
        current = int(connection.exec_driver_sql('SELECT setting FROM pg_catalog.pg_settings WHERE name=%s',(name,)).scalar())
        bounded = min(current,ceiling) if current else ceiling
        connection.exec_driver_sql('SELECT pg_catalog.set_config(%s,%s,true)',(name,str(bounded)+'ms'))
    # Pins/reference loading precedes table locks; no source audit belongs here.
    pinned = json.loads((APP / 'migrations/reference-controller.json').read_text())
    state = _checked_authority_ledger(connection)
    if state != REVISION:
        deny('revision_required')
    if controller_history:
        connection.exec_driver_sql('SELECT pg_catalog.pg_advisory_xact_lock(31003,1)')
    for table in TABLES:
        connection.exec_driver_sql('LOCK TABLE scribeswell.'+table+' IN SHARE MODE')
    catalogue(connection,pinned)
    operator(connection)
    return state, expected


def _preflight_prepared(connection, expected_actor):
    state, expected = checked_prepared(connection, expected_actor)
    local_state(connection, expected)
    return state


def preflight_prepared(connection, expected_actor):
    try:
        return _preflight_prepared(connection,expected_actor)
    except BaselineError:
        raise
    except Exception:
        raise BaselineError('scribeswell_prepared_validation_failed') from None
