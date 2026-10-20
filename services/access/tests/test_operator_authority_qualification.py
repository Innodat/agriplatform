"""Head5 provenance and rollback-only reference publication, without DB execution."""
import json
import shutil
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_identity_baseline as qualification
from test_organization_qualification import organization_recorder
from test_projection_qualification import digest


def test_authority_head_and_previous_history(monkeypatch):
    b=qualification.baseline
    monkeypatch.setattr(b,'verify_owned_history',lambda c:'identity_0005')
    monkeypatch.setattr(b,'verify_legacy_history',lambda c:None)
    kinds=[];monkeypatch.setattr(b,'verify_catalog',lambda c,k:kinds.append(k))
    b.verify_owned_postcondition(object(),require_head=True)
    assert kinds==['authority']
    monkeypatch.setattr(b,'verify_owned_history',lambda c:'identity_0004')
    b.verify_owned_postcondition(object())
    with pytest.raises(b.BaselineError,match='identity_unknown_history'):
        b.verify_owned_postcondition(object(),require_head=True)


def authority_recorder(tmp_path,monkeypatch,mutation=None):
    runner,statements=organization_recorder(tmp_path,monkeypatch,mutation)
    (tmp_path/'identity_baseline.py').write_text('AUTHORITY_REFERENCE_SHA256 = None\n')
    (tmp_path/'organization-reference.json').write_text('{}')
    (tmp_path/'versions/0005_operator_authority.py').write_text('AUTHORITY_SCHEMA_SQL = "captured authority"\n')
    runner.private={'owner_urls':{'authority_reference':'synthetic'}}
    monkeypatch.setattr(qualification.baseline,'trusted_organization_reference',lambda:{})
    monkeypatch.setattr(qualification.baseline,'verify_authority_roles',lambda *a,**k:None)
    monkeypatch.setattr(qualification.baseline,'authority_catalog_snapshot',lambda *a:{})
    original=(tmp_path/'identity_baseline.py').read_bytes()
    monkeypatch.setattr(qualification.baseline,'__file__',str(tmp_path/'identity_baseline.py'))
    monkeypatch.setattr(qualification.baseline,'IMPORTED_SOURCE_SHA256',digest(original))
    return runner,statements,original


@pytest.mark.parametrize('mutation',[None,'identity_baseline.py','source-pins.json','reference.json',
    'actor-reference.json','projection-reference.json','organization-reference.json','versions/0001_baseline.py',
    'versions/0002_actor_registry.py','versions/0003_current_account_actor.py',
    'versions/0004_current_account_organization.py','versions/0005_operator_authority.py'])
def test_authority_recorder_captures_sources_and_never_pins(tmp_path,monkeypatch,mutation):
    runner,statements,original=authority_recorder(tmp_path,monkeypatch,mutation)
    if mutation:
        with pytest.raises(AssertionError,match='authority_reference_source_changed'):runner.record_authority_reference()
        assert not (tmp_path/'authority-reference.json').exists()
    else:
        runner.record_authority_reference()
        assert (tmp_path/'identity_baseline.py').read_bytes()==original
        assert runner.records[-1]['pin_update_required'] is True
        with pytest.raises(AssertionError,match='authority_reference_already_exists'):runner.record_authority_reference()
    assert statements==['captured baseline','captured actor','captured projection','captured organization','captured authority']


def test_authority_reference_retains_all_prior_evidence(tmp_path,monkeypatch):
    b=qualification.baseline
    for name in ['source-pins.json','reference.json','actor-reference.json','projection-reference.json','organization-reference.json',
                 'versions/0002_actor_registry.py','versions/0003_current_account_actor.py','versions/0004_current_account_organization.py','versions/0005_operator_authority.py']:
        p=tmp_path/name;p.parent.mkdir(exist_ok=True);shutil.copyfile(qualification.OWNER/name,p)
    content=json.dumps({'source_pins':json.loads((tmp_path/'source-pins.json').read_bytes()),'migration_sha256':digest((tmp_path/'versions/0005_operator_authority.py').read_bytes()),'authority':{}}).encode()
    (tmp_path/'authority-reference.json').write_bytes(content)
    monkeypatch.setattr(b,'HERE',tmp_path);monkeypatch.setattr(b,'AUTHORITY_REFERENCE_SHA256',digest(content))
    assert b.trusted_authority_reference()=={}
    (tmp_path/'organization-reference.json').write_bytes(b'changed')
    with pytest.raises(b.BaselineError,match='identity_reference_unavailable'):b.trusted_authority_reference()


@pytest.mark.parametrize('problem',[None,'owner-login','operator-no-login','inherit','superuser','admin','operator-membership','missing','staged-dependency','effective-write','effective-read','external-definer','sequence'])
def test_authority_role_preparation_refuses_unsafe_state(problem):
    b=qualification.baseline
    class Result:
        def __init__(self,rows=(),scalar=False):self.rows=rows;self.scalar=scalar
        def all(self):return self.rows
        def scalar_one(self):return self.scalar
    class Connection:
        def execute(self,sql,params=None):
            sql=str(sql)
            for prefix,role,login in [('authority',b.AUTHORITY_OWNER,False),('operator',b.OPERATOR,True)]:
                if sql==b.AUTHORITY_ROLE_QUERIES[prefix+'_role']:
                    if problem=='missing':return Result()
                    flags=[role,False,False,False,False,login,False,False]
                    if problem=='owner-login' and prefix=='authority':flags[5]=True
                    if problem=='operator-no-login' and prefix=='operator':flags[5]=False
                    if problem=='inherit':flags[2]=True
                    if problem=='superuser':flags[1]=True
                    return Result([tuple(flags)])
                if sql==b.AUTHORITY_ROLE_QUERIES[prefix+'_memberships']:
                    rows=[(b.AUTHORITY_OWNER,'identity_migrator',problem=='admin','false','true')] if prefix=='authority' else []
                    if problem=='operator-membership' and prefix=='operator':rows=[('unexpected',b.OPERATOR,False,'false','true')]
                    return Result(rows)
                if sql==b.AUTHORITY_ROLE_QUERIES[prefix+'_dependencies']:
                    return Result([('unlisted',)] if problem=='staged-dependency' else [])
            if 'has_function_privilege' in sql:return Result(scalar=problem=='external-definer')
            if 'has_sequence_privilege' in sql:return Result(scalar=problem=='sequence')
            if 'has_any_column_privilege' in sql:
                return Result(scalar=problem==('effective-read' if "'SELECT'" in sql else 'effective-write'))
            raise AssertionError('unmodelled_role_query')
    if problem:
        with pytest.raises(b.BaselineError,match='identity_authority_role_'):b.verify_authority_roles(Connection(),staged=True)
    else:b.verify_authority_roles(Connection(),staged=True)


def test_qualifier_failure_reports_only_frame_metadata(capsys):
    import qualify_operator_authority as authority
    secret='sensitive-sql-and-parameter-value'
    try:
        raise AssertionError(secret)
    except AssertionError as error:
        authority.report_failure(error)
    output=capsys.readouterr().err
    assert 'authority_qualification_failed:AssertionError:test_operator_authority_qualification.py:' in output
    assert output.rstrip().endswith(':test_qualifier_failure_reports_only_frame_metadata')
    assert secret not in output


@pytest.mark.parametrize('identity',['source','path'])
def test_authority_recorder_rejects_stale_import_before_execution(tmp_path,monkeypatch,identity):
    runner,statements,_=authority_recorder(tmp_path,monkeypatch)
    if identity=='source':monkeypatch.setattr(qualification.baseline,'IMPORTED_SOURCE_SHA256','0'*64)
    else:monkeypatch.setattr(qualification.baseline,'__file__',str(tmp_path/'another-helper.py'))
    with pytest.raises(AssertionError,match='authority_reference_stale_imported_helper'):runner.record_authority_reference()
    assert statements==[]
    assert not (tmp_path/'authority-reference.json').exists()


def test_authority_reference_publication_is_private_with_permissive_umask(tmp_path,monkeypatch):
    import os
    import stat
    runner,_,_=authority_recorder(tmp_path,monkeypatch)
    previous=os.umask(0)
    try:runner.record_authority_reference()
    finally:os.umask(previous)
    assert stat.S_IMODE((tmp_path/'authority-reference.json').stat().st_mode)==0o600


@pytest.mark.parametrize('defect',[None,'missing-group','missing-case','extra-case','wrong-login','wrong-target','wrong-port','query','fragment'])
def test_all_operator_targets_validate_before_writes(tmp_path,defect):
    import qualify_operator_authority as authority
    private={group:{case:'postgresql://'+login+':synthetic@127.0.0.1:1234/'+case for case in authority.REQUIRED_CASES}
             for group,login in [('operator_urls','identity_operator'),('owner_urls','identity_migrator'),('databases','postgres'),('runtime_urls','access_runtime')]}
    if defect=='missing-group':private.pop('operator_urls')
    elif defect=='missing-case':private['operator_urls'].pop('failure')
    elif defect=='extra-case':private['operator_urls']['other']='postgresql://identity_operator@127.0.0.1:1234/other'
    elif defect:
        url=private['operator_urls']['failure']
        private['operator_urls']['failure']={'wrong-login':url.replace('identity_operator','other'),'wrong-target':url.replace('/failure','/clean'),
            'wrong-port':url.replace(':1234/',':5678/'),'query':url+'?options=bad','fragment':url+'#bad'}[defect]
    runner=authority.AuthorityQualification(tmp_path,private)
    writes=[];runner.prior_evidence=lambda *a:writes.append('entered-qualification')
    if defect:
        with pytest.raises(AssertionError,match='authority_operator_'):runner.upgrades_and_failures()
        assert writes==[]
    else:runner.validate_operator_urls()
