"""Protected organization grant command schema and exact historical verification."""
import importlib.util
from pathlib import Path
import sys
import pytest
ACCESS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ACCESS/'migrations'))
import access_baseline as baseline


@pytest.fixture(autouse=True)
def preserve_qualification_case_inventory():
    # Qualifiers deliberately select their own native case set at import. Unit
    # inspection must not leave that selection in another qualifier's fixtures.
    import qualify_application_register as base_qualification
    previous=base_qualification.CASES
    yield
    base_qualification.CASES=previous


def migration():
    spec=importlib.util.spec_from_file_location('_grant_assign_ddl',ACCESS/'migrations/versions/0013_grant_assign.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_assignment_extends_twelve_without_losing_history():
    assert baseline.HEAD=='access_0013'
    for i in range(1,14):assert baseline.validate_revision([f'access_{i:04}'])==f'access_{i:04}'
    for invalid in ([],['access_0014'],['access_0012','access_0013']):
        with pytest.raises(baseline.BaselineError):baseline.validate_revision(invalid)
    from access_registration_catalog import configure_catalog,grant_assignment_catalog
    assert 'grant.assign' not in repr(configure_catalog())
    assert 'grant.assign' in repr(grant_assignment_catalog())


def test_assignment_ddl_exact_identity_observation_precedes_locks():
    module=migration();sql=module.SQL
    assert (module.revision,module.down_revision)==('access_0013','access_0012')
    start=sql.index('CREATE FUNCTION access.assign_organization_grant(')
    command=sql[start:sql.index('CREATE FUNCTION access.organization_grant_assignment_outcome(',start)]
    assert command.index('grant_assignment_authority(p_org,p_app,p_account)')<command.index('identity.organization_account_target(p_account,p_member)')<command.index('pg_advisory_xact_lock')
    for fragment in ('verified_membership_revision','verified_account_actor_id','target_observed_at',"interval '5 seconds'",'p_member','access_required_grant_change_missing','grants_active_fields'):
        assert fragment in sql
    for forbidden in ('CREATE ROLE','ALTER ROLE','GRANT ALL','FROM identity.org_member','UPDATE identity.','DELETE FROM access.grants'):
        assert forbidden not in sql
    with pytest.raises(RuntimeError,match='Destructive rollback'):module.downgrade()


def test_target_dependency_allowlist_is_column_exact():
    path=ACCESS/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('_grant_dependency_identity',path)
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    allowed=[(None,None,None,'column '+column+' of table access.grants') for column in ('membership_id','revoked_at')]
    forbidden=(None,None,None,'column permission of table access.grants')
    assert identity._identity_target_dependencies([*allowed,forbidden])==[forbidden]


def test_exact_assignment_function_list_preserves_historical_nine():
    from access_registration_baseline import CONFIGURE_FUNCTIONS,GRANT_ASSIGNMENT_FUNCTIONS,_sql
    from access_registration_catalog import grant_assignment_catalog
    assert not any('grant' in name for name in CONFIGURE_FUNCTIONS)
    assert len(GRANT_ASSIGNMENT_FUNCTIONS)==len(set(GRANT_ASSIGNMENT_FUNCTIONS))
    assert set(grant_assignment_catalog()[1])==set(GRANT_ASSIGNMENT_FUNCTIONS)
    assert 'CREATE FUNCTION access.assign_organization_grant(' not in _sql('access_0010')
    assert 'CREATE FUNCTION access.assign_organization_grant(' in _sql('access_0013')


def test_identity_selects_thirteen_from_schema_resolved_routine_metadata(monkeypatch):
    path=ACCESS/'identity-migrations/identity_baseline.py'
    spec=importlib.util.spec_from_file_location('_grant_metadata_identity',path)
    identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def __init__(self,sql):self.sql=str(sql)
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):return True
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result(sql)
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None)
    monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r))
    monkeypatch.setattr(baseline,'require_equal',lambda *args:None)
    monkeypatch.setattr(baseline,'rows',lambda *args:[])
    monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==['access_0013']
    query=next(sql for sql in calls if 'assign_organization_grant' in sql)
    assert "n.nspname='access'" in query and 'p.pronamespace' in query
    assert all('FROM access.' not in sql and 'FROM identity.' not in sql for sql in calls)


def test_qualifier_closed_case_inventory_and_log_custody(tmp_path):
    sys.path.insert(0,str(ACCESS/'tests'))
    import qualify_grant_assign as q
    assert q.CASES=={'assign','authority','retry','guards','concurrency','upgrade','rollback','drift','cli'}
    owned=tmp_path/'assign-head-123.log';owned.write_text('controlled migration')
    (tmp_path/'root-stdout.log').write_text('independent status')
    captured=q.qualification_logs(tmp_path)
    assert set(captured)=={owned.name}
    q.verify_qualification_logs(tmp_path,captured)
    (tmp_path/'root-stdout.log').write_text('independent status changed')
    q.verify_qualification_logs(tmp_path,captured)
    owned.write_text('modified')
    with pytest.raises(AssertionError,match='qualification_log_custody_mismatch'):q.verify_qualification_logs(tmp_path,captured)


def test_qualifier_refuses_optimized_python_before_fixture_access(tmp_path):
    import subprocess
    child=subprocess.run([sys.executable,'-I','-B','-O',str(ACCESS/'tests/qualify_grant_assign.py'),'--all'],env={'PATH':'/usr/bin:/bin','ACCESS_QUALIFICATION_DIR':str(tmp_path/'missing')},capture_output=True,timeout=10)
    assert child.returncode!=0 and b'access_qualification_optimized_python_prohibited' in child.stderr
    assert not (tmp_path/'missing').exists()


def test_qualifier_retained_state_custody_checked_before_database(tmp_path,monkeypatch):
    import json
    from hashlib import sha256
    import qualify_grant_assign as q
    for name in ('credentials.json','run.json','bootstrap-fixed.log','assign-head-123.log'):(tmp_path/name).write_bytes(b'fixed')
    retained=tmp_path/'retained-state.json';retained.write_bytes(b'original')
    digest=sha256(retained.read_bytes()).hexdigest();retained.write_bytes(b'edited')
    witness=dict(status='passed',before={},after={},generated_inputs={name:sha256((tmp_path/name).read_bytes()).hexdigest() for name in ('credentials.json','run.json')},logs={'bootstrap-fixed.log':sha256(b'fixed').hexdigest()})
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(witness))
    (tmp_path/'results.json').write_text(json.dumps(dict(status='passed',source={},logs=q.qualification_logs(tmp_path),retained_state_sha256=digest)))
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path));monkeypatch.setattr(sys,'argv',['qualifier','--verify-retained'])
    monkeypatch.setattr(q,'load_fixture',lambda p:({},{}));monkeypatch.setattr(q,'source_snapshot',lambda p:{})
    monkeypatch.setattr(q,'Qualification',lambda *args:pytest.fail('database opened before state custody validation'))
    with pytest.raises(AssertionError,match='retained_state_custody_mismatch'):q.main()


def test_native_authority_matrix_retains_mapping_identities(monkeypatch):
    import qualify_grant_assign as q
    instance=q.Qualification(None,{})
    instance.targets={'authority':dict(account=q.ORG1,member='1',other=q.ORG2,other_member='2',unmapped=q.configure.MISSING,unmapped_member='3')}
    from types import SimpleNamespace
    writes=[];refusals=[];executions=[];recoveries=[];receipt=SimpleNamespace(result=SimpleNamespace(disposition='created'))
    monkeypatch.setattr(instance,'execute_sql',lambda case,sql,*args:writes.append((sql,{})))
    monkeypatch.setattr(instance,'parameter_sql',lambda case,sql,parameters=None,**kwargs:writes.append((sql,parameters or {})))
    monkeypatch.setattr(instance,'unchanged_refusal',lambda *args:None)
    monkeypatch.setattr(instance,'refused',lambda *args,**kwargs:refusals.append((args,kwargs)))
    monkeypatch.setattr(instance,'command',lambda *args:executions.append(list(writes)) or receipt)
    monkeypatch.setattr(instance,'lookup',lambda *args:recoveries.append(list(writes)) or receipt)
    monkeypatch.setattr(instance,'blocked_identity_projection',lambda *args:None)
    monkeypatch.setattr(instance,'inactive_identity_targets',lambda *args:None)
    monkeypatch.setattr(instance,'denied',lambda *args:None)
    instance.authority_and_identity()
    updates=[sql for sql,parameters in writes if sql.startswith('UPDATE access.operator_authorities')]
    assert updates and all(' SET enabled=' in sql for sql in updates)
    inserted=[parameters for sql,parameters in writes if sql.startswith('INSERT INTO access.operator_authorities')]
    assert len(inserted)==3 and len({p['id'] for p in inserted})==3
    assert [(p['app'],p['account']) for p in inserted]==[('other_app',None),('synthetic_app',q.ORG2),('synthetic_app',q.ORG1)]
    assert 'application_id IS NULL AND target_account_id IS NULL' in updates[-1]
    assert len(executions)==3 and len(recoveries)==2
    for observed in (executions[0],executions[1],recoveries[0]):
        broad_updates=[sql for sql,parameters in observed if sql.startswith('UPDATE access.operator_authorities') and 'application_id IS NULL AND target_account_id IS NULL' in sql]
        assert broad_updates[-1].startswith('UPDATE access.operator_authorities SET enabled=false')
        assert len([parameters for sql,parameters in observed if sql.startswith('INSERT INTO access.operator_authorities')])==3
    nil_args,nil_kwargs=refusals[-1]
    assert nil_args[1].startswith('INSERT INTO access.operator_authorities')
    assert nil_kwargs['constraint']=='operator_authorities_target_account_id_check'


def test_deferred_outcome_checks_observation_deadline_for_unchanged_too():
    from access_registration_baseline import _sql
    import re
    pattern=r'CREATE (?:OR REPLACE )?FUNCTION access\.require_command_event\(\).*?AS \$f\$(.*?)\$f\$;'
    historical=re.findall(pattern,_sql('access_0010'),re.S)[-1]
    current=re.findall(pattern,_sql('access_0013'),re.S)[-1]
    assert 'target_observed_at' not in historical
    deadline=current.index("IF NEW.command_type='grant.assign'")
    event_check=current.index("IF NEW.result->>'disposition' IN ('created','changed')")
    assert deadline<event_check
    for fragment in ('NEW.target_observed_at IS NULL','NOT isfinite(NEW.target_observed_at)',"NEW.target_observed_at>clock_timestamp()","clock_timestamp()-NEW.target_observed_at>=interval '5 seconds'","ERRCODE='AC004'","MESSAGE='access_verification_unavailable'"):
        assert fragment in current
    assert historical.strip() in current.replace(current[deadline:event_check],'').strip()
    assert 'identity.' not in current


def test_native_commit_deadline_covers_created_and_unchanged_and_checks_rollback(monkeypatch):
    import qualify_grant_assign as q
    from types import SimpleNamespace
    instance=q.Qualification(None,{})
    instance.targets={'guards':dict(account=q.ORG1,member='1',other=q.ORG2,other_member='2')}
    calls=[];states=[];attempt=[0]
    class ExpiredCommit(Exception):
        orig=SimpleNamespace(sqlstate='AC004')
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):attempt[0]+=1;raise ExpiredCommit()
        def exec_driver_sql(self,sql):
            calls.append(sql)
            return SimpleNamespace(scalar_one=lambda:'5s')
        def execute(self,sql,parameters):
            return SimpleNamespace(one=lambda:({'disposition':'created' if parameters['absent'] else 'unchanged'},1,1,None))
    class Engine:
        def begin(self):return Connection()
        def dispose(self):pass
    monkeypatch.setattr(instance,'db',lambda *args:Engine())
    monkeypatch.setattr(instance,'snapshot',lambda *args:states.append(True) or {})
    instance.deferred_observation_commit()
    assert attempt[0]==2 and len(states)==4
    assert calls.count('SELECT pg_sleep(2.6)')==4
    assert calls.count('SHOW statement_timeout')==2


def test_blocked_projection_probe_reads_snapshots_only_outside_lock(monkeypatch):
    import qualify_grant_assign as q
    instance=q.Qualification(None,{})
    locked=[False];snapshots=[];waits=[];observed=[]
    authorized=object();unauthorized=object()
    class Transaction:
        def rollback(self):locked[0]=False
    class Holder:
        def __enter__(self):return self
        def __exit__(self,*args):assert not locked[0]
        def begin(self):return Transaction()
        def exec_driver_sql(self,sql):
            assert sql=='LOCK TABLE identity.org_member IN ACCESS EXCLUSIVE MODE'
            locked[0]=True
    class Engine:
        def connect(self):return Holder()
        def dispose(self):pass
    def snapshot(case):
        assert not locked[0],'snapshot attempted while Identity relation locked'
        snapshots.append(case);return {}
    def command(case,value):
        assert locked[0]
        observed.append(value)
        raise q.adapter.OperatorError('access_denied' if value is unauthorized else 'operation_verification_unavailable')
    monkeypatch.setattr(instance,'db',lambda case,role:Engine())
    monkeypatch.setattr(instance,'snapshot',snapshot)
    monkeypatch.setattr(instance,'command',command)
    monkeypatch.setattr(instance,'wait_for_retry_lock',lambda holder,future,**kwargs:waits.append(kwargs))
    instance.blocked_identity_projection('authority',authorized,unauthorized)
    assert snapshots==['authority','authority'] and observed==[unauthorized,authorized]
    assert waits==[dict(advisory=False)] and not locked[0]
