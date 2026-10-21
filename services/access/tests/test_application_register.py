"""Access registration adapter and transport boundaries."""
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test_operator_target import prepared

OP = 'a1234567-1234-1234-1234-123456789abc'

def document(command='application.register'):
    payload = {'app_id':'synthetic_app','expected_absent':True}
    if command != 'application.register':
        payload['permission'] = 'synthetic.read'
    if command == 'permission.register':
        payload['scope_kind'] = 'account'
    return dict(schema_version=1,operation_id=OP,command=command,scope={'kind':'platform'},
        payload=payload,reason_code='synthetic_fixture',evidence_ref='synthetic:register')


def test_adapter_canonical_and_lock_namespace():
    import access_operator as a
    from access_operator_input import parse_command
    value = document(); command = parse_command(json.dumps(value).encode())
    assert json.loads(a.canonical_command(command)) == value
    actor = 'b1234567-1234-1234-1234-123456789abc'
    assert a.command_outcome_lock_key(actor,command) != __import__('identity_operator').outcome_lock_key(actor,OP)


def test_receipt_is_typed_and_closed():
    import access_operator as a
    row = ({'target':{'app_id':'synthetic_app'},'disposition':'created','revision':'1','event_id':OP},1,1,datetime.now(timezone.utc))
    receipt = a._receipt(row,OP)
    assert receipt.result.target.app_id == 'synthetic_app' and receipt.result.revision == '1'
    for bad in [dict(revision=1),dict(revision='0'),dict(event_id=None),dict(target={'app_id':'PRIVATE'}),dict(disposition='changed')]:
        with pytest.raises(a.OperatorError):a._receipt(({**row[0],**bad},*row[1:]),OP)
    assert a._receipt(None,OP) is None


def test_non_executable_access_commands_reject_before_connection():
    import access_operator as a
    for command in ('permission.register','entry_permission.register'):
        with pytest.raises(a.OperatorError) as failure:a.execute(object(),json.dumps(document(command)).encode())
        assert failure.value.code == 'command_unsupported'


def test_lookup_requires_explicit_app_before_connection():
    import access_operator as a
    for app in (None,'INVALID','x','a'*65):
        with pytest.raises(a.OperatorError) as failure:a.outcome(object(),OP,app_id=app)
        assert failure.value.code == 'command_invalid'


def test_cli_access_closed_dispatch(tmp_path,monkeypatch,capsys):
    import operator_cli as c
    from types import SimpleNamespace
    value = document();path = tmp_path/'command.json';path.write_text(json.dumps(value))
    seen=[]
    monkeypatch.setattr(c,'load_target',lambda path,**kw:SimpleNamespace(path=Path('/synthetic/access-operator.json')))
    monkeypatch.setattr(c,'dispatch',lambda request:seen.append(request) or json.dumps(dict(operation_id=OP,status='unresolved')).encode())
    assert c.main(['execute','--owner','access','--target','synthetic','--command-file',str(path)]) == 2
    assert json.loads(capsys.readouterr().out)['status'] == 'unresolved'
    assert seen[-1][-1] == 'access'
    assert c.main(['outcome','--owner','access','--target','synthetic','--command','application.register','--operation-id',OP,'--app-id','synthetic_app']) == 2
    assert seen[-1][2] == dict(command='application.register',app_id='synthetic_app')
    capsys.readouterr()
    before=len(seen)
    path.write_text(json.dumps(document('permission.register')))
    assert c.main(['execute','--owner','access','--target','synthetic','--command-file',str(path)]) == 2
    assert json.loads(capsys.readouterr().out)['code'] == 'command_unsupported'
    assert len(seen) == before


def test_revision4_is_known_and_roles_are_required():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_baseline as b
    assert b.validate_revision(['access_0004']) == 'access_0004'
    assert callable(b.verify_operator_roles)


@pytest.mark.parametrize('drift',('literal_case','grouping'))
def test_exact_registration_constraints_reject_drift(monkeypatch,drift):
    import access_registration_baseline as r
    from access_registration_catalog import TABLE_CATALOG
    import access_baseline as b
    monkeypatch.setattr(r,'verify_operator_roles',lambda _:None)
    monkeypatch.setattr(r,'TABLES',('operator_authorities',))
    def query(connection,sql):
        name='operator_authorities'
        if 'FROM pg_class WHERE oid=' in sql:return [(b.OWNER,'r',False,False,None,False,'d','p')]
        if 'FROM pg_attribute a LEFT JOIN' in sql:return TABLE_CATALOG[name]['columns']
        if 'FROM pg_constraint' in sql:
            rows=list(TABLE_CATALOG[name]['constraints'])
            index=next(i for i,row in enumerate(rows) if 'application.register' in row[2])
            row=list(rows[index]);row[2]=row[2].replace('application.register','APPLICATION.REGISTER') if drift=='literal_case' else row[2]+' OR true'
            rows[index]=tuple(row);return rows
        pytest.fail('drift was accepted before further inspection')
    monkeypatch.setattr(r,'rows',query)
    with pytest.raises(b.BaselineError,match='access_catalog_mismatch'):r.verify_registration(object())


def test_access_target_is_separately_bound(prepared):
    t,env,run_id,run,secret=prepared
    access=secret.with_name('access.env');access.write_bytes(b'ACCESS_OPERATOR_PASSWORD=access-private\n');access.chmod(0o600)
    descriptor=t.prepare_target(env,run_id,owner='access')
    loaded=t.load_target(descriptor,owner='access')
    assert loaded.database=='acop_'+run_id.replace('-','') and loaded.owner_id=='access'
    assert loaded.password=='access-private'
    with pytest.raises(t.TargetError):t.load_target(descriptor)
    with pytest.raises(t.TargetError):t.load_target(t.prepare_target(env,run_id),owner='access')


def test_identity_accepts_only_exact_access_role_extension(monkeypatch):
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('identity_access_extension',path)
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    class Connection:
        def execute(self,*args):return self
        def all(self):return [('access_command_owner','access_migrator',False,'false','true'),('access_command_owner','access_operator',False,'false','true')]
    with pytest.raises(b.BaselineError,match='identity_target_role_unsafe'):
        b.verified_access_command_extension(Connection())


@pytest.mark.parametrize('namespace',('','A1234567','1234567','123456789','../../bad'))
def test_access_namespace_is_bounded_and_owner_bound(prepared,namespace):
    t,env,run_id,run,secret=prepared
    with pytest.raises(t.TargetError):t.prepare_target(env,run_id,owner='access',namespace=namespace)
    with pytest.raises(t.TargetError):t.prepare_target(env,run_id,namespace='abcd1234')


def test_access_namespace_reconstructs_database_and_rejects_forgery(prepared):
    import json
    t,env,run_id,run,secret=prepared
    access=secret.with_name('access.env');access.write_bytes(b'ACCESS_OPERATOR_PASSWORD=access-private\n');access.chmod(0o600)
    path=t.prepare_target(env,run_id,owner='access',namespace='abcd1234')
    assert t.load_target(path,owner='access').database=='acop_'+run_id.replace('-','')+'_abcd1234'
    with pytest.raises(t.TargetError):t.load_target(path)
    value=json.loads(path.read_bytes());value['database']=value['database'].replace('abcd1234','abcd5678');path.write_text(json.dumps(value))
    with pytest.raises(t.TargetError):t.load_target(path,owner='access')


def test_identity_dependency_filter_keeps_foreign_access_schema():
    import importlib.util
    path=Path(__file__).resolve().parents[1]/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('identity_access_dependencies',path)
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    foreign=['current_database','pg_namespace','a','schema access_evil']
    assert b._identity_target_dependencies([foreign,['current_database','pg_namespace','a','schema access']])==[foreign]


@pytest.mark.parametrize('mutation',('host','port','login','database','query','namespace','inventory','group'))
def test_native_fixture_refuses_foreign_target_before_connection(mutation):
    import copy
    import qualify_application_register as q
    run_id='99b7231c-0a5b-4bdb-98e8-3329564c526a';namespace='abcd1234'
    proof=q.ROOT/'platform/deployment/.local/identity-baseline/unit-fixture'
    prefix='acreg_'+run_id.replace('-','')[:12]+'_'+namespace+'_'
    run=dict(run_id=run_id,operator_namespace=namespace,proof=str(proof),database_namespace=prefix,
        target=str(q.ROOT/'platform/deployment/environments/kdg-local.json'))
    private={group:{case:'postgresql://'+login+':private@127.0.0.1:55482/'+('acop_'+run_id.replace('-','')+'_'+namespace if case=='cli' else prefix+case) for case in q.CASES} for group,login in q.GROUP_LOGINS.items()}
    target={'ports':{'database':55482}}
    q.validate_fixture(private,run,target,proof)
    if mutation=='host':private['access_operator_urls']['boundary']=private['access_operator_urls']['boundary'].replace('127.0.0.1','example.com')
    if mutation=='port':private['access_operator_urls']['boundary']=private['access_operator_urls']['boundary'].replace(':55482/',':5432/')
    if mutation=='login':private['access_operator_urls']['boundary']=private['access_operator_urls']['boundary'].replace('access_operator:','postgres:')
    if mutation=='database':private['access_operator_urls']['boundary']=private['access_operator_urls']['boundary'].replace(prefix,'foreign_')
    if mutation=='query':private['access_operator_urls']['boundary']+='?options=foreign'
    if mutation=='namespace':run['database_namespace']='foreign_'
    if mutation=='inventory':private['databases'].pop('clean')
    if mutation=='group':private['extra']={}
    with pytest.raises(AssertionError):q.validate_fixture(private,run,target,proof)


@pytest.mark.parametrize('action',('execute','lookup'))
@pytest.mark.parametrize('refusal',('busy','isolation','option_autocommit','driver_autocommit'))
def test_access_runner_preserves_caller_work_without_sql(action,refusal):
    import access_operator as a
    from types import SimpleNamespace
    class Connection:
        calls=[]
        connection=SimpleNamespace(driver_connection=SimpleNamespace(autocommit=refusal=='driver_autocommit'))
        def in_transaction(self):return refusal=='busy'
        def get_isolation_level(self):return 'SERIALIZABLE' if refusal=='isolation' else 'READ COMMITTED'
        def get_execution_options(self):return {'isolation_level':'AUTOCOMMIT'} if refusal=='option_autocommit' else {}
        def begin(self):pytest.fail('began over caller-owned or unsupported connection')
        def execute(self,*args):pytest.fail('issued SQL')
        def commit(self):pytest.fail('committed caller work')
        def rollback(self):pytest.fail('rolled back caller work')
    c=Connection()
    with pytest.raises(a.OperatorError) as failure:
        a.execute(c,json.dumps(document()).encode()) if action=='execute' else a.outcome(c,OP,app_id='synthetic_app')
    assert failure.value.code==('connection_busy' if refusal=='busy' else 'isolation_unsupported')
    assert c.in_transaction()==(refusal=='busy') and not c.calls


@pytest.mark.parametrize('commit_return',(9.75,10.25))
def test_access_delayed_commit_rearms_budget_and_returns_uncertain_when_late(monkeypatch,commit_return):
    import access_operator as a
    from types import SimpleNamespace
    now=[0.0];monkeypatch.setattr(a.time,'monotonic',lambda:now[0])
    class Connection:
        calls=[];committed=False;rolled_back=False
        def in_transaction(self):return False
        def get_isolation_level(self):return 'READ COMMITTED'
        def begin(self):return self
        def __enter__(self):return self
        def __exit__(self,kind,*args):
            self.rolled_back=kind is not None
            if kind is None:self.committed=True;now[0]=commit_return
        def execute(self,sql,params):
            self.calls.append((str(sql),params));return self
        def one_or_none(self):
            now[0]=9.5
            return ({'target':{'app_id':'synthetic_app'},'disposition':'created','revision':'1','event_id':OP},1,1,datetime.now(timezone.utc))
    c=Connection()
    if commit_return>10:
        with pytest.raises(a.OperatorError) as failure:a.execute(c,json.dumps(document()).encode())
        assert failure.value.code=='operation_unavailable' and failure.value.operation_id==OP
    else:assert a.execute(c,json.dumps(document()).encode()).status=='committed'
    assert c.committed and not c.rolled_back
    assert 'set_config' in c.calls[-1][0] and c.calls[-1][1]=={'statement':'500ms'}


@pytest.mark.parametrize('role',('access_operator','access_operator_authority_owner','access_command_owner'))
@pytest.mark.parametrize('kind',('schema','table','column','sequence','function'))
def test_restricted_roles_reject_effective_foreign_authority(monkeypatch,role,kind):
    import access_baseline as b
    from types import SimpleNamespace
    def query(connection,sql):
        if 'FROM pg_proc p JOIN' in sql:
            return [('foreign_fixture','privileged','','foreign_owner','unapproved',None)] if kind=='function' else []
        if 'FROM pg_namespace WHERE' in sql:return [('foreign_fixture',True,False)] if kind=='schema' else []
        if 'LEFT JOIN pg_depend' in sql:
            return [('foreign_fixture','secret','r','foreign_owner',['SELECT'] if kind=='table' else [],None,kind=='column')] if kind in ('table','column') else []
        if "c.relkind='S'" in sql:return [(1,)] if kind=='sequence' else []
        pytest.fail('unrecognized privilege query')
    monkeypatch.setattr(b,'rows',query)
    with pytest.raises(b.BaselineError,match='access_operator_roles_invalid'):
        b.verify_operator_foreign_privileges(SimpleNamespace(dialect=SimpleNamespace(server_version_info=(17,))),role)


@pytest.mark.parametrize('role',('access_operator','access_operator_authority_owner','access_command_owner'))
def test_restricted_foreign_guard_preserves_exact_native_public_baseline(monkeypatch,role):
    import access_baseline as b
    from types import SimpleNamespace
    owner,hashes,grants=b._FOREIGN_FUNCTIONS[('public','get_user_roles','')]
    def query(connection,sql):
        if 'FROM pg_proc p JOIN' in sql:return [('public','get_user_roles','',owner,sorted(hashes)[0],grants)]
        if 'FROM pg_namespace WHERE' in sql:return [('public',True,False),('extensions',False,False)]
        if 'LEFT JOIN pg_depend' in sql:return [('extensions',n,'v','supabase_admin',['SELECT'],'pg_stat_statements',False) for n in ('pg_stat_statements','pg_stat_statements_info')]
        if "c.relkind='S'" in sql:return []
        pytest.fail('unrecognized privilege query')
    monkeypatch.setattr(b,'rows',query)
    b.verify_operator_foreign_privileges(SimpleNamespace(dialect=SimpleNamespace(server_version_info=(17,))),role)


@pytest.mark.parametrize('field',('probin','proallargtypes','proargmodes','proargnames'))
def test_fixed_function_verifier_refuses_raw_metadata_drift(monkeypatch,field):
    import access_registration_baseline as r
    from access_registration_catalog import FUNCTION_CATALOG
    monkeypatch.setattr(r,'verify_operator_roles',lambda _:None)
    monkeypatch.setattr(r,'TABLES',())
    monkeypatch.setattr(r,'FUNCTIONS',('command_lock',))
    body=__import__('re').search(r'CREATE FUNCTION access.command_lock\(.*?AS \$f\$(.*?)\$f\$;',r._sql(),__import__('re').S).group(1)
    def query(connection,sql):
        if 'SELECT pg_get_userbyid(proowner)' in sql:return [('access_migrator','sql',False,'i',['search_path=pg_catalog, pg_temp'],body,False,False,'u')]
        if 'SELECT pg_get_function_identity_arguments' in sql:return FUNCTION_CATALOG['command_lock']
        if 'SELECT probin,proallargtypes' in sql:
            row=[None,None,None,['value']];row[('probin','proallargtypes','proargmodes','proargnames').index(field)]='unapproved'
            return [tuple(row)]
        pytest.fail('raw metadata drift was accepted')
    monkeypatch.setattr(r,'rows',query)
    with pytest.raises(r.BaselineError,match='access_catalog_mismatch'):r.verify_registration(object())


def test_native_malformed_sql_matrix_covers_closed_sql_boundary():
    import qualify_application_register as q
    import access_operator as a
    parameters=dict(operation=OP,app='synthetic_app',reason='synthetic_fixture',evidence='synthetic:register',
        canonical=a.canonical_command(a.parse_command(json.dumps(document()).encode())))
    cases=q.malformed_sql_cases()
    assert len(cases)==len({label for label,_ in cases})==18
    assert {'invalid_utf8','duplicate_key','oversize','argument_envelope_mismatch'}<={label for label,_ in cases}
    for label,changes in cases:
        altered={**parameters,**(changes(parameters) if callable(changes) else changes)}
        assert altered!=parameters,label
