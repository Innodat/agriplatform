"""Access14 retains exact13 while adding independent protected removal."""
import importlib.util
from pathlib import Path
import sys,re
import pytest
ACCESS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ACCESS/'migrations'))
import access_baseline as baseline
from access_registration_baseline import _sql,GRANT_ASSIGNMENT_FUNCTIONS,GRANT_REVOCATION_FUNCTIONS
from access_registration_catalog import grant_assignment_catalog,grant_revocation_catalog


def test_fourteen_is_additive_and_historical_thirteen_fixed():
    assert baseline.HEAD=='access_0014'
    for i in range(1,15):assert baseline.validate_revision([f'access_{i:04}'])==f'access_{i:04}'
    for bad in ([],['access_0015'],['access_0013','access_0014']):
        with pytest.raises(baseline.BaselineError):baseline.validate_revision(bad)
    assert set(grant_assignment_catalog()[1])==set(GRANT_ASSIGNMENT_FUNCTIONS)
    assert set(grant_revocation_catalog()[1])==set(GRANT_REVOCATION_FUNCTIONS)
    assert 'grant.revoke' not in repr(grant_assignment_catalog())
    assert 'grant.revoke' in repr(grant_revocation_catalog())
    assert 'revoke_organization_grant' not in _sql('access_0013')


def test_revoke_exact_selectors_no_identity_observation_and_retry_namespaces():
    sql=_sql('access_0014');command=re.search(r'CREATE FUNCTION access.revoke_organization_grant\(.*?\$f\$;',sql,re.S)[0]
    for fragment in ('p_grant text','bound_grant.id IS DISTINCT FROM p_grant','bound_grant.membership_id IS DISTINCT FROM p_member',"bound_grant.revision::text IS DISTINCT FROM p_revision",'grant_revocation_authority','access:organization-grant:v1:', '"command_type":"grant.revoke"',"sha256(p_canonical)","'access.organization_grant_revoked'",'octet_length(p_canonical)>65556'):
        assert fragment in command
    for forbidden in ('identity.','target_observed_at','verified_member_revision','p_absent','interval'):
        assert forbidden not in command
    noop=command.index("IF bound_grant.revoked_at IS NOT NULL")
    overflow=command.index('IF bound_grant.revision=9223372036854775807')
    assert noop<overflow
    # Assignment source and its observation/deferred default stay byte-identical.
    old=_sql('access_0013')
    assert re.findall(r'CREATE (?:OR REPLACE )?FUNCTION access.require_command_event\(.*?\$f\$;',sql,re.S)==re.findall(r'CREATE (?:OR REPLACE )?FUNCTION access.require_command_event\(.*?\$f\$;',old,re.S)


def test_identity_selects_fourteen_using_schema_metadata(monkeypatch):
    spec=importlib.util.spec_from_file_location('_revoke_identity',ACCESS/'identity-migrations/identity_baseline.py');identity=importlib.util.module_from_spec(spec);spec.loader.exec_module(identity)
    calls=[];selected=[]
    class Result:
        def all(self):return [('access_command_owner','access_migrator',False,'false','true')]
        def scalar_one(self):return True
    class Connection:
        def execute(self,sql):calls.append(str(sql));return Result()
    monkeypatch.setattr(baseline,'verify_operator_roles',lambda c:None);monkeypatch.setattr(baseline,'verify_catalog',lambda c,r:selected.append(r));monkeypatch.setattr(baseline,'require_equal',lambda *args:None);monkeypatch.setattr(baseline,'rows',lambda *args:[]);monkeypatch.setattr(baseline,'acl',lambda *args:[])
    assert identity.verified_access_command_extension(Connection())==(True,True)
    assert selected==['access_0014']
    assert any("n.nspname='access'" in q and 'revoke_organization_grant' in q for q in calls)
    assert all('FROM access.' not in q and 'FROM identity.' not in q for q in calls)


def test_result_bound_changes_only_revoke_after_immutable_thirteen():
    old=grant_assignment_catalog()[0];new=grant_revocation_catalog()[0]
    old_result=next(c[2] for c in old['operation_outcome']['constraints'] if c[0]=='operation_outcome_result_check')
    current=next(c[2] for c in new['operation_outcome']['constraints'] if c[0]=='operation_outcome_result_check')
    assert '8192' in old_result and 'grant.revoke' not in old_result and '65556' not in old_result
    assert "(command_type = 'grant.revoke'::text) AND (octet_length((result)::text) <= 65556)" in current
    assert "(command_type <> 'grant.revoke'::text) AND (octet_length((result)::text) <= 8192)" in current
    assert "ADD CONSTRAINT operation_outcome_result_check" in _sql('access_0014')


def test_cli_child_diagnostics_never_echo_untrusted_output(capsys):
    from types import SimpleNamespace
    import qualify_grant_revoke as q
    assert not q.cli_child_ok(SimpleNamespace(returncode=2,stdout=b'{"code":"operation_unavailable","secret":"DO_NOT_ECHO"}',stderr=b'PRIVATE_TRACE'),'execute')
    out=capsys.readouterr();assert 'DO_NOT_ECHO' not in out.out and 'PRIVATE_TRACE' not in out.out
    import json
    assert json.loads(out.out)==dict(stage='execute',returncode=2,code='operation_unavailable',stderr_bytes=13)
    assert q.cli_child_ok(SimpleNamespace(returncode=0,stdout=b'PRIVATE_RECEIPT',stderr=b''),'execute')
    assert capsys.readouterr().out==''


def test_direct_sql_selector_ceiling_applies_to_execute_and_lookup_only_in_fourteen():
    sql=_sql('access_0014')
    for name in ('revoke_organization_grant','organization_grant_revocation_outcome'):
        body=re.search(r'CREATE FUNCTION access\.'+name+r'\(.*?\$f\$;',sql,re.S)[0]
        assert 'p_grant IS NULL OR octet_length(p_grant)>65536' in body
        assert body.index('octet_length(p_grant)>65536')<body.index('FROM access.permissions')
    assert 'octet_length(p_grant)>65536' not in _sql('access_0013')
