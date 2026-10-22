"""Harness safeguards; the actual-login matrix runs separately in the native fixture."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

PATH=Path(__file__).with_name('qualify_identity_pregrant_target.py')

def qualifier():
    spec=importlib.util.spec_from_file_location('pregrant_qualification',PATH)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_clean_only_current_sources_and_complete_matrix():
    q=qualifier()
    assert q.CASES=={'clean'}
    matrix=q.read_cases('11111111-1111-4111-8111-111111111111',7,('expected',))
    labels={case['label'] for case in matrix}
    assert {'setup-empty','uuid-spelling','wrong-org','wrong-account','wrong-member','null-target','nil-target','null-member','zero-member','negative-member','missing-member','invalid-uuid','invalid-bigint','overflow-bigint','valid-user-separate-caller','user-missing-account','setup-with-account','missing-context'}<=labels
    for field in ('org','actor'):
        for kind in ('missing','empty','malformed','nil'):
            assert field+'-'+kind in labels
    assert all('expected' in case or 'sqlstate' in case for case in matrix)


def test_optimized_python_refuses_before_import_or_io():
    result=subprocess.run([sys.executable,'-I','-B','-O',str(PATH),'--all'],capture_output=True)
    assert result.returncode!=0
    assert b'pregrant_qualification_optimized_python_prohibited' in result.stderr


def test_credential_rejects_extra_or_empty_without_engine(tmp_path):
    q=qualifier()
    for value in ({'password':''},{'password':'secret','url':'untrusted'},[]):
        (tmp_path/'runtime-credential.json').write_text(json.dumps(value))
        (tmp_path/'runtime-credential.json').chmod(0o600)
        with pytest.raises(AssertionError):q.credential(tmp_path,'runtime-credential.json')


def test_log_custody_detects_edit_addition_and_deletion(tmp_path):
    q=qualifier();log=tmp_path/'clean-head-1.log';log.write_text('safe')
    captured=q.qualification_logs(tmp_path)
    q.verify_qualification_logs(tmp_path,captured)
    log.write_text('changed')
    with pytest.raises(AssertionError):q.verify_qualification_logs(tmp_path,captured)
    log.write_text('safe');extra=tmp_path/'unexpected.log';extra.write_text('new')
    with pytest.raises(AssertionError):q.verify_qualification_logs(tmp_path,captured)
    extra.unlink();log.unlink()
    with pytest.raises(AssertionError):q.verify_qualification_logs(tmp_path,captured)


def test_repeated_all_refuses_before_fixture_or_database_io(tmp_path,monkeypatch):
    q=qualifier();(tmp_path/'all-started').touch()
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualifier','--all'])
    monkeypatch.setattr(q,'load_fixture',lambda proof:pytest.fail('fixture opened'))
    with pytest.raises(FileExistsError):q.main()


def test_source_and_log_mismatch_refuse_before_database_io(tmp_path,monkeypatch):
    q=qualifier()
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualifier','--verify-retained'])
    monkeypatch.setattr(q,'load_fixture',lambda proof:({},{}))
    monkeypatch.setattr(q,'source_snapshot',lambda proof:{'source':'current'})
    monkeypatch.setattr(q,'Qualification',lambda *args:pytest.fail('database qualifier created'))
    witness=dict(status='passed',before={'source':'old'},after={'source':'old'},logs={})
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(witness))
    with pytest.raises(AssertionError):q.main()
    witness.update(before={'source':'current'},after={'source':'current'},logs={'bootstrap.log':'wrong'})
    (tmp_path/'bootstrap.log').write_text('changed')
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(witness))
    with pytest.raises(AssertionError):q.main()


def test_fixture_reference_restore_preserves_selected_fields_allows_fixture_audit():
    from copy import deepcopy
    q=qualifier()
    original={'identity':{'users':[dict(id='target',deleted_at=None,updated_at='2026-10-22T10:00:00+00:00',username='kept')],'audit_log':[]}}
    deleted=deepcopy(original)
    deleted['identity']['users'][0].update(deleted_at='2026-10-22T10:01:00+00:00',updated_at='2026-10-22T10:01:00+00:00')
    deleted['identity']['audit_log'].append({'action':'UPDATE','fixture':'target'})
    q.verify_fixture_reference(original,deleted,'users','target',deleted=True)
    restored=deepcopy(deleted);restored['identity']['users'][0].update(deleted_at=None,updated_at='2026-10-22T10:02:00+00:00')
    restored['identity']['audit_log'].append({'action':'UPDATE','fixture':'target'})
    q.verify_fixture_reference(original,restored,'users','target',deleted=False)
    for mutate in [lambda state:state['identity']['users'][0].update(username='changed'),lambda state:state['identity']['users'].pop(0),lambda state:state['identity']['users'].append(deepcopy(state['identity']['users'][0])),lambda state:state['identity']['users'][0].update(deleted_at='2026-10-22T10:01:00+00:00'),lambda state:state['identity']['users'][0].update(updated_at='infinity'),lambda state:state['identity']['users'][0].update(updated_at='2026-10-22T09:00:00+00:00')]:
        invalid=deepcopy(restored);mutate(invalid)
        with pytest.raises((AssertionError,ValueError)):q.verify_fixture_reference(original,invalid,'users','target',deleted=False)


@pytest.mark.parametrize('name',['runtime-credential.json','identity-operator-credential.json'])
def test_auxiliary_credential_rejects_actual_unsafe_mode_and_symlink(tmp_path,name):
    q=qualifier();path=tmp_path/name;path.write_text(json.dumps({'password':'synthetic'}));path.chmod(0o600)
    assert q.credential(tmp_path,name)=='synthetic'
    path.chmod(0o644)
    with pytest.raises(q.base.dev.Refusal):q.credential(tmp_path,name)
    path.chmod(0o600);target=tmp_path/'protected.json';path.rename(target);path.symlink_to(target)
    with pytest.raises((OSError,q.base.dev.Refusal)):q.credential(tmp_path,name)


def custody_main(q,tmp_path,monkeypatch):
    monkeypatch.setenv('ACCESS_QUALIFICATION_DIR',str(tmp_path))
    monkeypatch.setattr(sys,'argv',['qualifier','--all'])
    monkeypatch.setattr(q,'load_fixture',lambda proof:({},{}))
    monkeypatch.setattr(q,'source_snapshot',lambda proof:{'source':'current'})
    (tmp_path/'bootstrap.log').write_text('original')
    for name in ('credentials.json','run.json'):(tmp_path/name).write_text('{}')
    witness=dict(status='passed',before={'source':'current'},after={'source':'current'},logs={'bootstrap.log':q.digest(tmp_path/'bootstrap.log')},generated_inputs={name:q.digest(tmp_path/name) for name in ('credentials.json','run.json')})
    (tmp_path/'bootstrap-source-custody.json').write_text(json.dumps(witness))


def test_extra_bootstrap_log_refuses_before_database_io(tmp_path,monkeypatch):
    q=qualifier();custody_main(q,tmp_path,monkeypatch)
    (tmp_path/'bootstrap-extra.log').write_text('unbound')
    monkeypatch.setattr(q,'Qualification',lambda *args:pytest.fail('database qualifier created'))
    with pytest.raises(AssertionError,match='bootstrap_log_inventory_mismatch'):q.main()


def test_original_bootstrap_log_mutation_during_execution_refuses_acceptance(tmp_path,monkeypatch):
    q=qualifier();custody_main(q,tmp_path,monkeypatch)
    class FakeQualification:
        def __init__(self,*args):self.receipts=[];self.results=[]
        def prepare_cases(self):(tmp_path/'bootstrap.log').write_text('changed during database work')
        def retained(self):pass
        soft_deletions=privileges=read_matrix=lifecycle=advance_revision=retained
        def snapshot(self):return {}
    monkeypatch.setattr(q,'Qualification',FakeQualification)
    with pytest.raises(AssertionError,match='bootstrap_log_custody_mismatch'):q.main()
    assert not (tmp_path/'results.json').exists()


def test_local_reset_checks_every_setting_and_original_roles():
    q=qualifier();instance=q.Qualification(Path('/unused'),{})
    class Result:
        def __init__(self,row):self.row=row
        def one(self):return self.row
    class Connection:
        def __init__(self,row):self.row=row
        def begin(self):return self
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def exec_driver_sql(self,sql):return Result(self.row)
    clean=['access_migrator','access_migrator',123,None,'',None,'']
    assert instance.assert_local_reset(Connection(clean))==123
    for index in (0,1,3,4,5,6):
        leaked=clean.copy();leaked[index]='leaked'
        with pytest.raises(AssertionError):instance.assert_local_reset(Connection(leaked))


def test_revision_two_fixture_changes_only_timestamp_and_revision():
    q=qualifier();instance=q.Qualification(Path('/unused'),{})
    instance.target='target';instance.member=7;instance.actor='actor'
    original=dict(id=7,revision=1,deleted_at=None,updated_at='2026-10-22T10:00:00+00:00',is_owner=False)
    current=dict(original,revision=2,updated_at='2026-10-22T10:01:00+00:00')
    def sql(statement,values):
        assert values=={'id':7}
        if statement.startswith('UPDATE'):
            assert statement=='UPDATE identity.org_member SET updated_at=statement_timestamp() WHERE id=:id'
            return None
        return [(dict(current if updated[0] else original),)]
    updated=[False]
    def execute(statement,values):
        if statement.startswith('UPDATE'):updated[0]=True
        return sql(statement,values)
    instance.parameter_sql=execute
    instance.advance_revision()
    assert instance.expected==[('target',7,2,'actor',q.DISPLAY)]
    assert instance.results==['owner-fixture-timestamp-update-active-revision2-no-membership-authority-change']
    updated[0]=False;current['is_owner']=True
    with pytest.raises(AssertionError,match='revision_fixture_changed_other_membership_fields'):instance.advance_revision()
