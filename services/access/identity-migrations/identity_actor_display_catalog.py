"""Identity28 source-bound evidence and concrete restricted-reader protections."""
from hashlib import sha256
import json
from pathlib import Path
from sqlalchemy import text

HERE=Path(__file__).parent
REFERENCE_SHA256='cd93272373dd056e9d661a309ffe545b44c17ec23710d1fd23f795e5b1bd82fb'
ROLE='identity_actor_display_runtime'

def verify_runtime(connection, staged=False):
    from identity_baseline import BaselineError
    flags=connection.execute(text('SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname=:role'),{'role':ROLE}).one_or_none()
    if flags is None or tuple(flags)!=(True,False,False,False,False,False,False):
        raise BaselineError('identity_actor_display_role_unsafe')
    if connection.execute(text("SELECT EXISTS(SELECT 1 FROM pg_auth_members WHERE roleid=to_regrole(:role) OR member=to_regrole(:role)) OR has_database_privilege(:role,current_database(),'CREATE') OR NOT has_database_privilege(:role,current_database(),'CONNECT')"),{'role':ROLE}).scalar_one():
        raise BaselineError('identity_actor_display_role_unsafe')
    if connection.execute(text("""SELECT EXISTS(
     SELECT 1 FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname<>'information_schema' AND has_schema_privilege(:role,oid,'CREATE')
     UNION ALL SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND
       ((c.relkind IN ('r','p','v','m','f') AND (has_table_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER,MAINTAIN') OR has_any_column_privilege(:role,c.oid,'SELECT,INSERT,UPDATE,REFERENCES')))
        OR (c.relkind='S' AND CASE WHEN c.relkind='S' THEN has_sequence_privilege(:role,c.oid,'SELECT,USAGE,UPDATE') ELSE false END))
    )"""),{'role':ROLE}).scalar_one():
        raise BaselineError('identity_actor_display_privileges_unsafe')
    if not staged:
        if connection.execute(text("""SELECT EXISTS(SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
          WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND
           (n.nspname='identity' OR p.prosecdef) AND has_function_privilege(:role,p.oid,'EXECUTE')
           AND p.oid NOT IN ('identity.actor_displays(uuid[])'::regprocedure,
             'identity.current_org_id()'::regprocedure,'identity.current_member_id()'::regprocedure))
          OR NOT has_function_privilege(:role,'identity.actor_displays(uuid[])','EXECUTE')
          OR has_function_privilege(:role,'identity.actor_displays(uuid[])','EXECUTE WITH GRANT OPTION')"""),{'role':ROLE}).scalar_one():
            raise BaselineError('identity_actor_display_privileges_unsafe')

def reference_document(connection):
    from identity_people_setup_catalog import reference_document as previous
    from identity_baseline import catalog_fingerprints
    # Reuse the owner's existing historical observation convention. This adds no
    # global catalogue policy or alternate migration ledger implementation.
    catalog=previous(connection)['catalog']
    queries={
      'runtime_role':"SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,rolinherit FROM pg_roles WHERE rolname=:role",
      'runtime_memberships':"SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid=to_regrole(:role) OR member=to_regrole(:role)",
      'runtime_schemas':"SELECT nspname,p,has_schema_privilege(:role,oid,p) FROM pg_namespace CROSS JOIN unnest(ARRAY['USAGE','CREATE']) p WHERE nspname IN ('identity','access','auth','public')",
      'runtime_functions':"SELECT n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),has_function_privilege(:role,p.oid,'EXECUTE'),has_function_privilege(:role,p.oid,'EXECUTE WITH GRANT OPTION') FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE p.oid IN ('identity.actor_displays(uuid[])'::regprocedure,'identity.log_audit()'::regprocedure,'identity.set_audit_fields()'::regprocedure,'identity.handle_new_user()'::regprocedure)",
    }
    catalog.update(catalog_fingerprints({key:sorted([list(row) for row in connection.execute(text(query),{'role':ROLE})],key=lambda row:json.dumps(row,sort_keys=True)) for key,query in queries.items()}))
    return {'migration_sha256':sha256((HERE/'versions/0028_actor_displays.py').read_bytes()).hexdigest(),
      'predecessor_reference_sha256':sha256((HERE/'people-setup-reference.json').read_bytes()).hexdigest(),'catalog':catalog}

def verify_actor_display_catalog(connection):
    from identity_baseline import BaselineError,compare_catalog
    from identity_people_setup_catalog import REFERENCE_SHA256 as previous
    from identity_account_grant_catalog import trusted_predecessors
    from studies_migration_support import verify_roles
    from identity_discovery_catalog import verify_role
    trusted_predecessors();verify_roles(connection,'identity');verify_role(connection)
    verify_role(connection,'access_discovery_owner','access_migrator');verify_runtime(connection)
    predecessor=HERE/'people-setup-reference.json';path=HERE/'actor-display-reference.json'
    if sha256(predecessor.read_bytes()).hexdigest()!=previous or json.loads(predecessor.read_bytes())['migration_sha256']!=sha256((HERE/'versions/0027_people_setup_references.py').read_bytes()).hexdigest():
        raise BaselineError('identity_actor_display_predecessor_unavailable')
    if REFERENCE_SHA256 is None or not path.is_file() or sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:
        raise BaselineError('identity_actor_display_reference_unavailable')
    expected=json.loads(path.read_bytes());actual=reference_document(connection)
    if any(expected.get(k)!=actual[k] for k in ('migration_sha256','predecessor_reference_sha256')):
        raise BaselineError('identity_actor_display_reference_unavailable')
    compare_catalog(actual['catalog'],expected['catalog'])
