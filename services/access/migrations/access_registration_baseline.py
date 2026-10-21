"""Fixed Access0004 catalog assertions; no adoption or target-derived approval."""
import importlib.util
from hashlib import sha256
from pathlib import Path
import re
from access_baseline import rows,require_equal,acl,owner_acl,OWNER,verify_operator_roles,BaselineError

TABLES=('operator_principals','operator_authorities','operation_outcome','business_event')
INDEXES=('operator_principals_pkey','operator_authorities_pkey',
 'operator_authorities_database_login_command_scope_kind_org__key',
 'operation_outcome_pkey','operation_outcome_executor_actor_id_operation_id_key',
 'business_event_pkey','business_event_outcome_id_key')
FUNCTIONS=('command_lock','current_operator_authority','guard_operator_authority','guard_command_evidence',
 'require_command_event','require_application_registration','register_application','application_registration_outcome')

def _sql():
    path=Path(__file__).parent/'versions/0004_application_register.py'
    if sha256(path.read_bytes()).hexdigest() != '14d6e70b8142936700eb96d5e44cc6580be8c2e9bb06a00db841b529bf824807':
        raise BaselineError('access_original_source_mismatch')
    spec=importlib.util.spec_from_file_location('_access_registration_ddl',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.SQL


def verify_registration(connection):
    verify_operator_roles(connection)
    from access_registration_catalog import TABLE_CATALOG,FUNCTION_CATALOG
    sql=_sql()
    for name in TABLES:
        oid=f"(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' AND c.relname='{name}')"
        require_equal(rows(connection,f"SELECT pg_get_userbyid(relowner),relkind,relrowsecurity,relforcerowsecurity,reloptions,relispartition,relreplident,relpersistence FROM pg_class WHERE oid={oid}"),[(OWNER,'r',False,False,None,False,'d','p')])
        expected=TABLE_CATALOG[name]
        require_equal(rows(connection,f"SELECT attname,format_type(atttypid,atttypmod),attnotnull,attidentity,attgenerated,pg_get_expr(d.adbin,d.adrelid),attcollation::regcollation::text FROM pg_attribute a LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE attrelid={oid} AND attnum>0 AND NOT attisdropped ORDER BY attnum"),expected['columns'])
        require_equal(rows(connection,f"SELECT conname,contype,pg_get_constraintdef(oid),convalidated,condeferrable,condeferred FROM pg_constraint WHERE conrelid={oid} ORDER BY conname"),expected['constraints'])
        for query in (f"SELECT 1 FROM pg_inherits WHERE inhrelid={oid} OR inhparent={oid}",f"SELECT 1 FROM pg_policy WHERE polrelid={oid}",f"SELECT 1 FROM pg_rewrite WHERE ev_class={oid}",f"SELECT 1 FROM pg_attribute WHERE attrelid={oid} AND attisdropped"):
            require_equal(rows(connection,query),[])
        privileges=['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']+(['MAINTAIN'] if connection.dialect.server_version_info>=(17,) else [])
        grantee='access_operator_authority_owner' if name.startswith('operator_') else 'access_command_owner'
        grants=[] if name.startswith('operator_') else ['SELECT','INSERT']
        require_equal(acl(connection,oid,'r'),owner_acl(privileges)+[(OWNER,grantee,p,False) for p in grants])
        column_grants=[]
        if name.startswith('operator_'):
            selected=('database_login','executor_actor_id','enabled') if name=='operator_principals' else ('id','database_login','command','scope_kind','org_id','application_id','target_account_id','enabled')
            column_grants=[(col,OWNER,grantee,'SELECT',False) for col in selected]
        require_equal(acl(connection,oid,'r',column=True),column_grants)
        require_equal(rows(connection,f"SELECT tgname,tgenabled,pg_get_triggerdef(oid) FROM pg_trigger WHERE tgrelid={oid} AND NOT tgisinternal ORDER BY tgname"),expected['triggers'])
        require_equal(rows(connection,f"SELECT k.conname,t.tgenabled,p.proname FROM pg_trigger t JOIN pg_constraint k ON k.oid=t.tgconstraint JOIN pg_proc p ON p.oid=t.tgfoid WHERE t.tgrelid={oid} AND t.tgisinternal ORDER BY k.conname,p.proname"),expected['foreign_triggers'])
        require_equal(rows(connection,f"SELECT pg_get_indexdef(indexrelid),indisvalid,indisready,indislive FROM pg_index WHERE indrelid={oid} ORDER BY indexrelid::regclass::text"),expected['indexes'])
    for name in FUNCTIONS:
        declarations=list(re.finditer(r'CREATE (?:OR REPLACE )?FUNCTION access\.'+name+r'\((.*?)\).*?AS \$f\$(.*?)\$f\$;',sql,re.S))
        declaration=declarations[-1];signature,body=declaration.groups()
        owner=('access_operator_authority_owner' if name=='current_operator_authority' else 'access_command_owner' if name in ('require_command_event','require_application_registration','register_application','application_registration_outcome') else OWNER)
        language='sql' if name in ('command_lock','current_operator_authority') else 'plpgsql'
        volatility='i' if name=='command_lock' else 's' if name=='current_operator_authority' else 'v'
        require_equal(rows(connection,f"SELECT pg_get_userbyid(proowner),l.lanname,prosecdef,provolatile,proconfig,prosrc,proleakproof,proisstrict,proparallel FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace JOIN pg_language l ON l.oid=p.prolang WHERE n.nspname='access' AND p.proname='{name}'"),[(owner,language,name in ('current_operator_authority','require_command_event','require_application_registration','register_application','application_registration_outcome'),volatility,['search_path=pg_catalog, pg_temp'],body,False,False,'u')])
        require_equal(rows(connection,f"SELECT pg_get_function_identity_arguments(p.oid),pg_get_function_result(p.oid),prokind,proretset,pronargdefaults,procost,prorows,prosupport::text FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='{name}'"),FUNCTION_CATALOG[name])
        raw_arguments={
            'command_lock':(None,None,['value']),
            'current_operator_authority':(None,None,['p_app']),
            'register_application':([2950,25,25,25,17,3802,23,23,1184],['i']*5+['t']*4,
                ['p_operation','p_app','p_reason','p_evidence','p_canonical','result','command_version','result_version','committed_at']),
            'application_registration_outcome':([2950,25,3802,23,23,1184],['i']*2+['t']*4,
                ['p_operation','p_app','result','command_version','result_version','committed_at']),
        }.get(name,(None,None,None))
        require_equal(rows(connection,f"SELECT probin,proallargtypes,proargmodes,proargnames FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='{name}'"),[(None,*raw_arguments)])
        grants=[(owner,owner,'EXECUTE',False)]
        if name in ('command_lock','current_operator_authority'):grants.append((owner,'access_command_owner','EXECUTE',False))
        if name in ('register_application','application_registration_outcome'):grants=[(owner,'access_operator','EXECUTE',False),(owner,owner,'EXECUTE',False)]
        require_equal(acl(connection,f"(SELECT p.oid FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' AND p.proname='{name}')",'f'),grants)
