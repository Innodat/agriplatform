"""Review closure for explicit private qualifier binding and aggregate ordering."""
import json
from types import SimpleNamespace
from copy import deepcopy
import pytest
import qualify_account_actor_ensure as q


@pytest.mark.parametrize('defect',[None,'extra','run','database','scheme','host','port','path','login','query','fragment'])
def test_cli_owner_fixture_is_protected_closed_and_exact(tmp_path,defect):
    tmp_path.chmod(0o700)
    target=SimpleNamespace(run_id='a1234567-1234-1234-1234-123456789abc',database='idop_synthetic',port=55482)
    value=dict(run_id=target.run_id,database=target.database,owner_url='postgresql://identity_migrator:synthetic@127.0.0.1:55482/idop_synthetic')
    if defect=='extra':value['extra']=True
    elif defect=='run':value['run_id']='other'
    elif defect=='database':value['database']='other'
    elif defect:
        changes=dict(scheme=('postgresql:','https:'),host=('127.0.0.1','example.invalid'),port=('55482','55483'),path=('/idop_synthetic','/other'),login=('identity_migrator','postgres'),query=('idop_synthetic','idop_synthetic?option=x'),fragment=('idop_synthetic','idop_synthetic#x'))
        value['owner_url']=value['owner_url'].replace(*changes[defect])
    path=tmp_path/'owner.json';path.write_text(json.dumps(value));path.chmod(0o600)
    if defect:
        with pytest.raises(ValueError):q.load_cli_owner_fixture(path,target)
    else:assert q.load_cli_owner_fixture(path,target)==value


def test_all_reuses_existing_acceptance_stages_in_dependency_order(monkeypatch):
    runner=object.__new__(q.AccountQualification);seen=[]
    stages=['run','boundaries','review_boundaries','alternate_executor','physical_lifecycle','recovery_and_migration_failure','retained_commands','closure','cli','populated_repeat','verify_retained']
    for name in stages:monkeypatch.setattr(runner,name,lambda name=name:seen.append(name))
    monkeypatch.setattr(runner,'passed',lambda name:seen.append(name))
    runner.all()
    assert seen==stages+['ensure-all-acceptance-stages']


@pytest.mark.parametrize('login',['identity_operator','access_runtime'])
def test_invocation_accepts_only_explicit_validated_operator_or_alternate_url(monkeypatch,login):
    runner=object.__new__(q.AccountQualification)
    runner.private=dict(operator_urls=dict(clean='postgresql://identity_operator:synthetic@127.0.0.1:55482/local'),runtime_urls=dict(clean='postgresql://access_runtime:synthetic@127.0.0.1:55482/local'))
    seen=[]
    class Result:
        def one(self):return (login,login)
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,*args):return Result()
        def commit(self):pass
    class Engine:
        def connect(self):return Connection()
        def dispose(self):pass
    monkeypatch.setattr(q,'engine',lambda url:seen.append(url) or Engine())
    monkeypatch.setattr(q.operator,'execute',lambda *args:'executed')
    value={}
    url=runner.private['operator_urls' if login=='identity_operator' else 'runtime_urls']['clean']
    assert runner.invoke(value,url=url)=='executed' and seen==[url]
    with pytest.raises(AssertionError,match='qualification_invocation_url_invalid'):
        runner.invoke(value,url='postgresql://postgres:synthetic@example.invalid/foreign')
    assert seen==[url]
