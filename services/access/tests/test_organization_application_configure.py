"""Protected organization configuration dispatch and compact receipts."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_organization_application_input import document
from test_application_register import OP

def test_configure_dispatch_lookup_and_canonical_scope(monkeypatch):
    import access_operator as a
    from access_operator_input import parse_command
    seen=[]
    monkeypatch.setattr(a,'_run',lambda *args:seen.append(args))
    body=document()
    a.execute(object(),json.dumps(body).encode())
    assert 'access.configure_organization_application' in seen[-1][2]
    assert seen[-1][3]['org']==body['scope']['org_id'].lower()
    assert seen[-1][3]['absent'] is True and seen[-1][3]['revision'] is None
    a.outcome(object(),OP,command=body['command'],app_id='fixture_app',org_id=body['scope']['org_id'])
    assert 'access.organization_application_configuration_outcome' in seen[-1][2]
    command=parse_command(json.dumps(body).encode())
    assert json.loads(a.canonical_command(command))['scope']['org_id']==body['scope']['org_id'].lower()
    first=a.command_outcome_lock_key(OP,command)
    body['scope']['org_id']='12345678-1234-1234-1234-123456789abc'
    assert first!=a.command_outcome_lock_key(OP,parse_command(json.dumps(body).encode()))
    for kwargs in ({'org_id':None},{'permission':'p'},{'org_id':OP,'command':'application.register'}):
        with pytest.raises(a.OperatorError):a.outcome(object(),OP,**(dict(command='organization_application.configure',app_id='fixture_app',org_id=OP)|kwargs))

def test_configure_receipt_closed_contract():
    import access_operator as a
    base={'target':{'org_id':OP,'app_id':'fixture_app'},'disposition':'created','revision':'1','event_id':OP}
    tail=(1,1,datetime.now(timezone.utc))
    assert type(a._receipt((base,*tail),OP,'organization_application.configure').result) is a.ConfigureOrganizationApplicationResult
    assert a._receipt(({**base,'disposition':'changed','revision':'2'},*tail),OP,'organization_application.configure')
    assert a._receipt(({**base,'disposition':'unchanged','event_id':None},*tail),OP,'organization_application.configure')
    for changes in ({'revision':'2'},{'event_id':None},{'revision':1},{'target':{'app_id':'fixture_app'}},{'target':{'org_id':'bad','app_id':'fixture_app'}}):
        with pytest.raises(a.OperatorError):a._receipt(({**base,**changes},*tail),OP,'organization_application.configure')


def test_historical8_and_exact9_catalogs_stay_distinct():
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'migrations'))
    import access_baseline as baseline
    from access_registration_catalog import enablement_catalog,configure_catalog
    for revision in ('access_0008','access_0009'):
        assert baseline.validate_revision([revision])==revision
    assert 'organization_application.configure' not in repr(enablement_catalog())
    assert 'organization_application.configure' in repr(configure_catalog())


def test_identity_selects_nine_from_metadata_only(monkeypatch):
    import importlib.util
    import access_baseline as baseline
    path=Path(__file__).resolve().parents[1]/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('_configure_identity_baseline',path)
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def __init__(self,sql):self.sql=str(sql)
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):return 'discover_applications' not in self.sql and 'check_account_capability' not in self.sql and 'change_account_grant' not in self.sql and 'check_organization_permission' not in self.sql and 'enroll_studies_account' not in self.sql and 'revoke_organization_grant' not in self.sql and 'assign_organization_grant' not in self.sql and 'pg_attribute' not in self.sql and 'grants_permission_scope_fkey' not in self.sql
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result(sql)
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r))
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    monkeypatch.setattr(baseline,'rows',lambda *args:[])
    monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==['access_0009']
    assert all('FROM access.' not in sql for sql in calls)


def test_cli_receipt_target_binding_and_closed_worker(monkeypatch):
    import access_operator as a
    import operator_cli as cli
    base={'target':{'org_id':OP,'app_id':'fixture_app'},'disposition':'created','revision':'1','event_id':OP}
    tail=(1,1,datetime.now(timezone.utc))
    from dataclasses import asdict
    receipt=a._receipt((base,*tail),OP,'organization_application.configure')
    wire=asdict(receipt);wire['committed_at']=receipt.committed_at.isoformat()
    assert cli.validate_response(json.dumps(wire).encode(),OP,'organization_application.configure',base['target'])==wire
    for target in ({'org_id':'12345678-1234-1234-1234-123456789abc','app_id':'fixture_app'},{'org_id':OP,'app_id':'other_app'}):
        with pytest.raises(ValueError):cli.validate_response(json.dumps(wire).encode(),OP,'organization_application.configure',target)
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:pytest.fail('invalid worker touched target'))
    for context in ({'command':'organization_application.configure','app_id':'fixture_app'},
                    {'command':'organization_application.configure','org_id':'bad','app_id':'fixture_app'},
                    {'command':'application.register','org_id':OP,'app_id':'fixture_app'}):
        with pytest.raises(ValueError):cli.access_worker(['outcome','unused',context,OP,'access'])


def test_cli_org_lookup_requires_exact_flag_before_target(monkeypatch,capsys):
    import operator_cli as cli
    monkeypatch.setattr(cli,'load_target',lambda *args,**kwargs:pytest.fail('invalid CLI touched target'))
    common=['outcome','--owner','access','--target','unused','--operation-id',OP,'--app-id','fixture_app']
    for args in ([*common,'--command','organization_application.configure'],
                 [*common,'--command','application.register','--org-id',OP],
                 [*common,'--command','organization_application.configure','--org-id','bad']):
        assert cli.main(args)==2
        output=capsys.readouterr()
        assert json.loads(output.out)=={'code':'command_invalid'} and output.err==''


def test_standalone_qualification_custody_includes_consumed_helpers_and_previous_package(tmp_path,monkeypatch):
    import qualify_organization_application_configure as q
    from hashlib import sha256
    previous=tmp_path/'previous-root/services/access/access_operator.py'
    previous.parent.mkdir(parents=True);previous.write_text('# retained previous8 adapter\n')
    manifest={'baseline_commit':'fd8248f43a3355b9494e031128d2ffdafd0a8fb0',
              'sources':{'services/access/access_operator.py':sha256(previous.read_bytes()).hexdigest()}}
    (tmp_path/'previous-source.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(q,'ROOT',Path('/'))
    monkeypatch.setattr(q.base,'source_paths',lambda proof:[])
    captured=q.source_snapshot(tmp_path)
    for module in (q.storage,q.storage.prior,q.storage.prior.prior,q.storage.prior.prior.prior):
        path=Path(module.__file__).resolve()
        assert captured[str(path.relative_to('/'))]==sha256(path.read_bytes()).hexdigest()
    assert str(previous.relative_to('/')) in captured
    previous.write_text('# changed historical source\n')
    with pytest.raises(AssertionError,match='previous_source_mismatch'):q.source_snapshot(tmp_path)


def test_previous8_fixture_documents_cover_four_independent_command_receipts():
    import qualify_organization_application_configure as q
    values=q.Qualification(None,{}).previous8_documents('previous8_fixture')
    assert [v['command'] for v in values]==['application.register','permission.register','entry_permission.register','application.set_enabled']
    assert len({v['operation_id'] for v in values})==4
    assert all(q.base.parse_command(json.dumps(value).encode()) for value in values)
    assert values[1]['payload']['permission']==values[2]['payload']['permission']
    assert values[3]['payload']['expected_revision']=='1'


def test_wait_observer_clears_snapshot_and_requires_both_actual_waiters(monkeypatch):
    import qualify_organization_application_configure as q
    from types import SimpleNamespace
    calls=[];waiting=iter((0,2))
    class Holder:
        def exec_driver_sql(self,sql):
            calls.append(sql)
            return SimpleNamespace(scalar_one=lambda:17 if 'pg_backend_pid' in sql else None)
        def execute(self,statement,parameters):
            assert parameters==dict(blocker=17,any_lock=True)
            assert 'pg_blocking_pids(a.pid)' in str(statement)
            return SimpleNamespace(scalar_one=lambda:next(waiting))
    monkeypatch.setattr(q.time,'sleep',lambda seconds:None)
    future=SimpleNamespace(done=lambda:False)
    q.Qualification(None,{}).wait_for_retry_lock(Holder(),[future,future],advisory=False,count=2)
    assert calls.count('SELECT pg_stat_clear_snapshot()')==2


def test_malformed_qualification_matrix_changes_arguments_or_wire_and_checks_state(monkeypatch):
    import qualify_organization_application_configure as q
    instance=q.Qualification(None,{})
    calls=[];snapshots=[];references=[]
    original_bound=q.bound
    def capture_bound(value):
        result=original_bound(value);references.append(result);return result
    monkeypatch.setattr(q,'bound',capture_bound)
    monkeypatch.setattr(instance,'command',lambda *args:None)
    monkeypatch.setattr(instance,'snapshot',lambda *args:snapshots.append(True) or {})
    monkeypatch.setattr(instance,'refused',lambda *args,**kwargs:calls.append((args,kwargs)))
    instance.guards()
    reference=references[0]
    malformed=[(args,kwargs) for args,kwargs in calls if args[1]==q.EXECUTE]
    assert len(malformed)==len(q.base.malformed_sql_cases())+10 and len(snapshots)==2
    for args,kwargs in malformed:
        assert args[2]=='AC005'
        assert kwargs.get('prefix') or kwargs['parameters']!=reference
    assert {kwargs.get('prefix') for args,kwargs in malformed if kwargs.get('prefix')}=={
        'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ','SET TRANSACTION ISOLATION LEVEL SERIALIZABLE'}
