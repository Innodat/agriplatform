"""Negative oracles for the native qualifier; these do not claim native execution."""
import ast
import asyncio
import copy
from pathlib import Path
import sys

import pytest
from sqlalchemy.engine import make_url

sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_studies_current as qualification
from studies_identity import StudiesFailure


@pytest.mark.parametrize('expected',[(403,'access_denied'),(403,'identity.verification_required'),(503,'identity.setup_unavailable')])
def test_denial_oracle_requires_exact_contract_class(expected):
    async def raises(outcome):raise StudiesFailure(*outcome)
    assert asyncio.run(qualification.require_studies_failure(lambda:raises(expected),expected,'synthetic'))=={
        'case':'synthetic','status':expected[0],'error_id':expected[1]}
    for wrong in ((503,'dependency_unavailable'),(403,'access_denied'),(503,'identity.setup_unavailable')):
        if wrong==expected:continue
        with pytest.raises(AssertionError,match='unexpected_studies_refusal'):
            asyncio.run(qualification.require_studies_failure(lambda:raises(wrong),expected,'synthetic'))
    async def succeeds():return None
    with pytest.raises(AssertionError,match='studies_refusal_missing'):
        asyncio.run(qualification.require_studies_failure(succeeds,expected,'synthetic'))


def fixture(tmp_path):
    value=qualification.CurrentQualification.__new__(qualification.CurrentQualification)
    value.proof=tmp_path;value.environment={};value.events=[];value.cli_results=[]
    value.urls={'identity_migrator':make_url('postgresql://identity_migrator@localhost/synthetic')}
    value.stop_process=lambda process:None
    return value


@pytest.mark.parametrize('reached,verified',[(False,False),(True,False),(True,True)])
def test_injected_failure_requires_verified_postcondition_marker(monkeypatch,tmp_path,reached,verified):
    subject=fixture(tmp_path);observed=[]
    def launch(arguments,**kwargs):
        body=next(node.args[0].value for node in ast.walk(ast.parse(arguments[4]))
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='exec')
        def original(*args,**kwargs):
            observed.append('postcondition')
            if not verified:raise RuntimeError('sensitive error must not become a marker')
        namespace={'original':original};exec(body,namespace)
        class Process:
            def wait(self,timeout):
                if reached:
                    try:namespace['replacement'](object())
                    except RuntimeError:pass
                return 1
        return Process()
    monkeypatch.setattr(qualification.subprocess,'Popen',launch)
    if reached and verified:
        subject.migration_case('identity','synthetic-failure',fail=True,expected=1)
        marker=tmp_path/'synthetic-failure-postcondition.json'
        assert observed==['postcondition'] and marker.stat().st_mode&0o777==0o600
        assert marker.read_bytes()==b'{"postcondition_verified":true}\n'
        assert 'postcondition_marker_sha256' in subject.cli_results[0]
    else:
        with pytest.raises(AssertionError,match='injected_postcondition_not_observed'):
            subject.migration_case('identity','synthetic-failure',fail=True,expected=1)
        assert not (tmp_path/'synthetic-failure-postcondition.json').exists()
        assert not subject.cli_results


@pytest.mark.parametrize('changed',[False,True])
def test_failed_migration_compares_row_values_before_retry(monkeypatch,tmp_path,changed):
    import studies_owner_fixture
    subject=fixture(tmp_path);subject.populated=True;subject.prior_account='synthetic-account'
    subject.protected_snapshots={};subject.prepare_principals=lambda:None
    subject.ledger=lambda owner:'access_0018'
    state={'identity.users':[{'id':subject.prior_account,'username':'retained-value'}],
        'access.alembic_version':[{'version_num':'access_0018'}]}
    stages=[]
    def migration_case(owner,label,**kwargs):
        stages.append(label)
        if kwargs.get('fail') and changed:state['identity.users'][0]['username']='unexpected-changed-value'
    subject.migration_case=migration_case
    class Connection:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def execute(self,*args):return self
        def fetchone(self):return (subject.prior_account,)
    subject.connect=lambda:Connection()
    monkeypatch.setattr(studies_owner_fixture,'protected_state',lambda connection:copy.deepcopy(state))
    if changed:
        with pytest.raises(AssertionError,match='changed protected business state'):
            subject.migrate('access',None)
        assert stages==['access-prior','cli-access-failure']
        assert not (tmp_path/'after-access-failed-migration.json').exists()
    else:
        subject.migrate('access',None)
        assert stages==['access-prior','cli-access-failure','cli-access-upgrade','cli-access-repeat']
        assert (tmp_path/'after-access-failed-migration.json').exists()
