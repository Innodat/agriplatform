"""Single-use synthetic SQL→HTTP organization check, using existing owner fixtures."""
if not __debug__:
    raise RuntimeError('organization_check_optimized_python_prohibited')
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from hashlib import sha256
from unittest.mock import patch
from uuid import UUID, uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_check_reader_bridge as prior
import qualify_permission_register as permission
ROOT, ACCESS, ACTOR = prior.ROOT, prior.ACCESS, prior.ACTOR
base, storage, assign, revoke = prior.base, prior.storage, prior.assign, prior.revoke
base.CASES = frozenset(('reference', 'bridge'))
sys.path.insert(0, str(ACCESS))
import main as runtime
# Independent contract oracle; never derive expected resources from runtime sets.
RESOURCE_KINDS = {
    'kdg_capture.capture.create.assigned': 'own_account',
    'kdg_capture.capture.create.all': 'own_account',
    'kdg_capture.capture.read.own': 'own_account',
    'kdg_capture.capture.edit.own': 'own_account',
    'kdg_capture.capture.read.all': 'organization',
    'kdg_capture.capture.edit.all': 'organization',
    'kdg_capture.questionnaire.manage': 'organization',
    'kdg_capture.child.manage': 'organization',
    'kdg_capture.assignment.manage': 'organization',
}
PERMISSIONS = frozenset(RESOURCE_KINDS)
APP = 'kdg_capture'
READ = 'kdg_capture.capture.read.own'
ORG = assign.ORG1


def sources(proof):
    captured = prior.source_snapshot(proof)
    paths = {Path(__file__), ACCESS/'tests/test_organization_check.py', ACCESS/'ORGANIZATION-CHECK.md',
             ACCESS/'pyproject.toml', ACCESS/'uv.lock', ACCESS/'openapi.json', ACCESS/'export_openapi.py'}
    for directory in ('identity-migrations', 'migrations'):
        paths.update(p for p in (proof/directory).rglob('*') if p.is_file())
    paths.add(proof/'historical_identity20_driver.py')
    paths.update(proof.parent/name for name in ('access-registry-reviewed-20261021/credentials.json','org-storage-reviewed-20261021/credentials.json','org-storage-reviewed-20261021/run.json'))
    root_runtime=ROOT/'platform/deployment/.local/access-organization-check-20261022/runtime'
    paths.update(root_runtime/name for name in ('pyproject.toml','uv.lock'))
    paths.add(root_runtime.parent/'owner-environment.json')
    return captured | {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def logs(proof):
    return {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(proof.glob('*.log'))}


class Qualification(prior.Qualification):
    def migration(self, label, target='head', expected=None, injected=False, case='bridge'):
        environment={'PATH':'/usr/bin:/bin','LC_ALL':'C.UTF-8',
                     'ACCESS_MIGRATION_DATABASE_URL':self.private['access_owner_urls'][case]}
        if injected:
            code="""import sys
sys.path.insert(0,DIRECTORY)
import access_baseline as b
from alembic.config import Config
from alembic import command
original=b.verify_catalog
def verify(c,revision):
 original(c,revision)
 if revision=='access_0015':raise b.BaselineError('access_test_postcondition_failure')
b.verify_catalog=verify
command.upgrade(Config(INI),'head')
""".replace('DIRECTORY',repr(str(ACCESS/'migrations'))).replace('INI',repr(str(ACCESS/'alembic.ini')))
            command=[sys.executable,'-I','-B','-c',code]
        else:
            command=[sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'alembic.ini'),'upgrade',target]
        result=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,timeout=45)
        path=self.proof/('organization-'+label+'.log')
        with path.open('xb') as output:output.write(result.stdout+result.stderr)
        path.chmod(0o600)
        if expected is None:assert result.returncode==0,'migration_failed:'+label
        else:
            assert result.returncode!=0,'migration_did_not_refuse:'+label
            lines=(result.stdout+result.stderr).rstrip().splitlines()
            assert lines and re.fullmatch(rb'(?:[A-Za-z_][A-Za-z0-9_.]*\.)?BaselineError: '+expected.encode()+rb'(?:[:][a-z_,]+)?',lines[-1]),'migration_refusal_mismatch:'+label
    def check_owners(self, case='bridge'):
        db=self.db(case)
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                base.baseline.verify_catalog(c,'access_0015')
        finally:db.dispose()
        db=self.db(case,'owner_urls')
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                prior.baseline.verify_owned_postcondition(c,require_head=True)
        finally:db.dispose()
    def raw_catalog(self):
        # Observe invalid metadata without approving it. Include every function
        # field and RLS policy so drift refusal cannot normalize unseen fields.
        result=super().raw_catalog()
        db=self.db('bridge')
        try:
            with db.connect() as c:
                c.exec_driver_sql('SET TRANSACTION READ ONLY')
                result['access_complete_functions']=[row[0] for row in c.exec_driver_sql("SELECT to_jsonb(p) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' ORDER BY p.proname,p.oid")]
                result['access_complete_policies']=[row[0] for row in c.exec_driver_sql("SELECT to_jsonb(p) FROM pg_policy p JOIN pg_class t ON t.oid=p.polrelid JOIN pg_namespace n ON n.oid=t.relnamespace WHERE n.nspname='access' ORDER BY t.relname,p.polname")]
        finally:db.dispose()
        return result
    def prepare(self, case='bridge', wrong_registration=False):
        # One legacy unmapped grant is retained through12→14 to prove actor setup
        # precedence without disabling any current attribution/command guard.
        self.migration(case+'-baseline12','access_0012',case=case)
        self.seed(case);self.prepare_identity(case)
        self.command(case,base.document(APP))
        if wrong_registration:
            self.command(case,base.document('synthetic_other_app'))
        for value in sorted(PERMISSIONS):
            app='synthetic_other_app' if wrong_registration and value=='kdg_capture.capture.read.all' else APP
            self.command(case,permission.document(value,app,'organization'))
        if wrong_registration:
            self.command(case,prior.entry.document('kdg_capture.capture.read.all','synthetic_other_app'))
            self.command(case,prior.enable.document(True,app='synthetic_other_app'))
            self.command(case,prior.configure.document(True,app='synthetic_other_app'))
        self.command(case,prior.entry.document(READ,APP))
        self.command(case,prior.enable.document(True,app=APP))
        self.command(case,prior.configure.document(True,app=APP))
        t=self.targets[case]
        db=self.db(case)
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.org_id',:org,true),set_config('app.actor_id',:actor,true)"),dict(org=ORG,actor=ACTOR))
                c.execute(text("""INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_by,created_actor_id,updated_actor_id,updated_at)
                 VALUES(CAST(:org AS uuid),'synthetic-retained-unmapped',CAST(:account AS uuid),:permission,CAST(:member AS bigint),CAST(:actor AS text),CAST(:actor AS uuid),CAST(:actor AS uuid),statement_timestamp())"""),
                 dict(org=ORG,account=t['unmapped'],member=t['unmapped_member'],permission=READ,actor=ACTOR))
        finally:db.dispose()
        self.migration(case+'-baseline14','access_0014',case=case)
        assign.Qualification.authority(self,case)
        revoke.Qualification.authority(self,case)
        self.assignments={}
        for value in sorted(PERMISSIONS):
            document=assign.document(t['account'],t['member'],permission=value)
            self.assignments[value]=(document,self.command(case,document))
        self.record('supported-Identity-ensure-join-nine-KDG-capabilities-enabled-current14-and-retained-unmapped-grant')
    def prepare_reader(self):
        # Existing exact prepared global edge can be retained on a fresh frame;
        # never rerun a single-use preparation script or repair extra memberships.
        db=self.admin('bridge')
        try:
            with db.connect() as c:
                edges=c.exec_driver_sql("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid='access_check_reader'::regrole OR member='access_check_reader'::regrole").all()
            if not edges:
                with db.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
                    c.exec_driver_sql((ACCESS/'tools/prepare_access_check_reader_execution.sql').read_text())
            else:assert [tuple(r) for r in edges]==[('access_check_reader','access_migrator',False,False,True)],'unknown_reader_membership'
        finally:db.dispose()
        db=self.db('bridge')
        try:
            with db.connect() as c:
                from access_organization_check_catalog import verify_reader_role
                verify_reader_role(c,installed=False)
        finally:db.dispose()
        self.record('exact-prepared-SET-only-reader-edge-no-runtime-membership')
    def response(self, account=None, value=READ, expected=200, code=None, case='bridge', **changes):
        target=self.targets[case]; account=account or target['account']
        def authenticate(token):
            if token!='Bearer synthetic-local-qualification':raise HTTPException(401,{'code':'authentication_required'})
            return UUID(account)
        db=self.auxiliary_db(case,'access_runtime')
        try:
            with patch.dict(os.environ,{'KDG_SERVICE_KEY':'synthetic-local-kdg-check-key','KDG_ORG_ID':ORG},clear=False):
                app=runtime.create_app(db=db,authenticate=authenticate)
            with TestClient(app) as client:
                body={'permission':value,'authorization_scope':{'kind':'organization','org_id':ORG}}
                body.update(changes.pop('body',{}))
                headers={'Authorization':'Bearer synthetic-local-qualification','X-Service-Key':'synthetic-local-kdg-check-key'}
                headers.update(changes.pop('headers',{}))
                response=client.post('/v2/check',json=body,headers=headers,**changes)
            assert response.status_code==expected,'HTTP_status_mismatch:'+str(expected)
            assert 'no-store' in response.headers.get('cache-control',''),'HTTP_cache_not_private'
            value=response.json()
            if code is not None:assert value=={'detail':{'code':code}},'HTTP_error_mismatch'
            if expected==200:
                assert set(value)=={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at','membership_id','resource_scope'}
                assert value['account_id']==account and value['permission']==body['permission'] and value['authorization_scope']==body['authorization_scope']
                assert value['actor_id']==target['actor' if account==target['account'] else 'other_actor'] and value['membership_id']==str(target['member' if account==target['account'] else 'other_member'])
                assert UUID(value['decision_id']).int and value['checked_at'].endswith(('Z','+00:00'))
                resource={'kind':'own_account','account_id':account} if RESOURCE_KINDS[body['permission']]=='own_account' else {'kind':'organization','org_id':ORG}
                assert value['resource_scope']==resource,'resource_scope_wrong'
            return value
        finally:db.dispose()
    def upgrade(self):
        before=self.snapshot('bridge'); catalog=self.raw_catalog()
        self.migration('postcondition-rollback',expected='access_test_postcondition_failure',injected=True)
        assert self.snapshot('bridge')==before and self.raw_catalog()==catalog,'rollback_changed_state'
        self.migration('controlled14-to15')
        self.check_owners()
        after=self.snapshot('bridge')
        for key,value in before.items():
            if not key.startswith('catalog_') and key!='alembic_version':assert after[key]==value,'upgrade_changed_business:'+key
        assert before['alembic_version']==[['access_0014']] and after['alembic_version']==[['access_0015']]
        before=after;catalog=self.raw_catalog()
        self.migration('repeat15')
        assert self.snapshot('bridge')==before and self.raw_catalog()==catalog,'repeat_changed_state'
        self.record('controlled14-to15-complete-business-preservation-postcondition-rollback-repeat')
    def drift(self):
        for label,change,restore,code in (
            ('unsafe-role','ALTER ROLE access_check_reader LOGIN','ALTER ROLE access_check_reader NOLOGIN','access_check_reader_role_unsafe'),
            ('column-drift','GRANT UPDATE (user_id) ON access.grants TO access_check_reader','REVOKE UPDATE (user_id) ON access.grants FROM access_check_reader','access_check_reader_privileges_unsafe'),
            ('policy-drift','ALTER POLICY check_reader_account_scope ON access.grants USING (true)',"ALTER POLICY check_reader_account_scope ON access.grants USING (org_id::text=current_setting('app.org_id',true) AND user_id::text=current_setting('app.account_id',true))",'access_catalog_mismatch'),
            ('routine-drift','ALTER FUNCTION access.check_organization_permission(text) VOLATILE','ALTER FUNCTION access.check_organization_permission(text) STABLE','access_catalog_mismatch'),
        ):
            before=self.snapshot('bridge');catalog=self.raw_catalog()
            self.admin_sql(change)
            try:
                mutated=self.snapshot('bridge');mutated_catalog=self.raw_catalog()
                self.migration(label,expected=code)
                db=self.db('bridge','owner_urls')
                try:
                    with db.connect() as c:
                        c.exec_driver_sql('SET TRANSACTION READ ONLY')
                        try:prior.baseline.verify_owned_postcondition(c,require_head=True)
                        except prior.baseline.BaselineError as error:
                            assert str(error)=='identity_target_role_unsafe','identity_drift_refusal_mismatch'
                        else:raise AssertionError('identity_drift_not_refused')
                finally:db.dispose()
                assert self.snapshot('bridge')==mutated and self.raw_catalog()==mutated_catalog,'drift_refusal_changed_state'
            finally:self.admin_sql(restore)
            assert self.snapshot('bridge')==before and self.raw_catalog()==catalog,'drift_restore_changed_state'
        self.migration('explicit-forward-retry15');self.check_owners()
        self.record('unsafe-role-column-policy-and-routine-drift-both-owners-refused-without-normalization-explicit-forward-retry')
    def reads(self):
        before=self.snapshot('bridge');catalog=self.raw_catalog()
        for permission in sorted(PERMISSIONS):self.response(value=permission)
        first=self.response();second=self.response();assert first['decision_id']!=second['decision_id']
        self.response(account=self.targets['bridge']['other'],expected=403,code='access_denied')
        self.response(account=self.targets['bridge']['unmapped'],expected=409,code='identity.actor_setup_required')
        self.response(account=self.targets['bridge']['unmapped'],value='kdg_capture.capture.read.all',expected=403,code='access_denied')
        self.response(expected=403,code='service_access_denied',headers={'X-Service-Key':'invalid'})
        self.response(expected=401,code='authentication_required',headers={'Authorization':'Bearer invalid'})
        self.response(expected=403,code='service_access_denied',body={'authorization_scope':{'kind':'organization','org_id':assign.ORG2}})
        self.response(expected=422,code='validation_failed',body={'account_id':self.targets['bridge']['other']})
        assert self.snapshot('bridge')==before and self.raw_catalog()==catalog,'HTTP_reads_mutated_state'
        self.record('actual-runtime-SQL-HTTP-nine-resources-actor-precedence-binding-policy-denials-no-writes')
    def role_denials(self):
        before=self.snapshot('bridge');db=self.admin('bridge')
        try:
            for role,statements in {
                'access_runtime':('SELECT * FROM access.grants','SELECT * FROM access.applications','SET ROLE access_check_reader'),
                'access_check_reader':('SELECT * FROM identity.users','SELECT * FROM identity.alembic_version','SELECT * FROM access.alembic_version','SELECT * FROM access.grants','SELECT * FROM identity.current_account_actor()','SET ROLE access_migrator'),
            }.items():
                for statement in statements:
                    with db.connect() as c:
                        tx=c.begin()
                        try:
                            c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION '+role)
                            self.context(c)
                            savepoint=c.begin_nested()
                            try:c.exec_driver_sql(statement)
                            except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501','unexpected_role_error'
                            else:raise AssertionError('role_authority_expanded')
                            finally:savepoint.rollback()
                        finally:tx.rollback()
            with db.begin() as c:
                c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION access_check_reader');self.context(c)
                accounts=c.exec_driver_sql('SELECT user_id::text FROM access.grants').scalars().all()
                assert accounts and set(accounts)=={self.targets['bridge']['account']},'reader_account_RLS_expanded'
            for changes in ({'account_id':None},{'org_id':'malformed'},{'context_kind':'setup'},{'account_id':self.targets['bridge']['other']}):
                with db.begin() as c:
                    c.exec_driver_sql('SET LOCAL SESSION AUTHORIZATION access_runtime');self.context(c,**changes)
                    assert not c.execute(text('SELECT * FROM access.check_organization_permission(:permission)'),dict(permission=READ)).all()
        finally:db.dispose()
        assert self.snapshot('bridge')==before
        db=self.admin('bridge')
        try:
            with db.connect() as c:
                tx=c.begin()
                try:
                    if c.dialect.server_version_info >= (17,):
                        c.exec_driver_sql('GRANT MAINTAIN ON access.applications TO PUBLIC')
                        from access_organization_check_catalog import verify_reader_role
                        try:verify_reader_role(c,installed=True)
                        except base.baseline.BaselineError as error:assert str(error)=='access_check_reader_privileges_unsafe'
                        else:raise AssertionError('PUBLIC_maintain_not_refused')
                finally:tx.rollback()
        finally:db.dispose()
        assert self.snapshot('bridge')==before
        self.record('actual-reader-runtime-private-table-ledger-role-escalation-context-and-PUBLIC-maintenance-isolation')
    def lifecycle(self):
        self.command('bridge',prior.enable.document(False,'2',APP));self.response(expected=403,code='access_denied')
        self.command('bridge',prior.enable.document(True,'3',APP));self.response()
        self.command('bridge',prior.configure.document(False,'1',app=APP));self.response(expected=403,code='access_denied')
        self.command('bridge',prior.configure.document(True,'2',app=APP));self.response()
        target=self.targets['bridge'];receipt=self.assignments[READ][1]
        self.command('bridge',revoke.document(target['account'],target['member'],receipt.result.target.grant_id,permission=READ))
        self.response(expected=403,code='access_denied')
        self.command('bridge',prior.enable.document(False,'4',APP));self.command('bridge',prior.enable.document(True,'5',APP))
        self.response(expected=403,code='access_denied')
        self.command('bridge',assign.document(target['account'],target['member'],'2',permission=READ));self.response()
        old_member=str(target['member'])
        self.invoke('bridge','membership.retire',dict(account_id=target['account'],membership_id=old_member,expected_revision='1'),ORG)
        self.response(expected=403,code='access_denied')
        result=self.invoke('bridge','membership.join',dict(account_id=target['account'],expected_previous_membership_id=old_member,is_owner=False),ORG)
        new_member=str(result.result.target.membership_id);assert new_member!=old_member
        self.response(expected=403,code='access_denied')
        self.command('bridge',assign.document(target['account'],new_member,'3',permission=READ))
        target['member']=new_member;self.response()
        self.record('protected-disable-reenable-revoke-no-resurrection-retire-rejoin-explicit-renewal')
    def preparation_refusals(self):
        # Exercise the exact preparation DO body inside rollback-only fixtures.
        # Omit only its outer transaction statements so no fixture can commit.
        sql=(ACCESS/'tools/prepare_access_check_reader_execution.sql').read_text()
        body='DO $reader_execution$'+sql.split('DO $reader_execution$',1)[1].rsplit('COMMIT;',1)[0]
        db=self.admin('reference')
        graph="SELECT to_jsonb(m) FROM pg_auth_members m WHERE roleid IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_check_reader','access_migrator')) OR member IN (SELECT oid FROM pg_roles WHERE rolname IN ('access_check_reader','access_migrator')) ORDER BY roleid,member,grantor"
        try:
            with db.connect() as c:
                initial=c.exec_driver_sql(graph).all();c.rollback()
                for label,mutation in (
                    ('valid',None),
                    ('unsafe-flags','ALTER ROLE access_migrator CREATEDB'),
                    ('unsafe-incoming','GRANT access_migrator TO access_runtime'),
                ):
                    tx=c.begin()
                    try:
                        c.exec_driver_sql('REVOKE access_check_reader FROM access_migrator')
                        if mutation:c.exec_driver_sql(mutation)
                        before=c.exec_driver_sql(graph).all()
                        savepoint=c.begin_nested()
                        try:c.exec_driver_sql(body,execution_options={'no_parameters':True})
                        except Exception as error:
                            assert mutation and getattr(getattr(error,'orig',None),'diag',None).message_primary=='access_check_reader_migrator_unsafe','preparation_refusal_mismatch:'+label
                            savepoint.rollback()
                            assert c.exec_driver_sql(graph).all()==before,'preparation_refusal_changed_graph'
                        else:
                            assert not mutation,'preparation_accepted_unsafe_recipient'
                            savepoint.commit()
                            edges=c.exec_driver_sql("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,inherit_option,set_option FROM pg_auth_members WHERE roleid='access_check_reader'::regrole OR member='access_check_reader'::regrole").all()
                            assert [tuple(r) for r in edges]==[('access_check_reader','access_migrator',False,False,True)]
                    finally:tx.rollback()
                    assert c.exec_driver_sql(graph).all()==initial,'preparation_fixture_not_restored'
                    c.rollback()
        finally:db.dispose()
        self.record('rollback-only-exact-preparation-safe-recipient-unsafe-flags-and-assumption-path-refusals')
    def reference_boundaries(self):
        case='reference'
        self.prepare(case,wrong_registration=True)
        self.preparation_refusals()
        self.migration('reference-controlled14-to15',case=case)
        self.check_owners(case)
        self.response(case=case)
        # This permission belongs to another enabled app. It must never authorize
        # KDG, including while KDG itself is disabled.
        self.command(case,prior.enable.document(False,'2',APP))
        self.response(case=case,value='kdg_capture.capture.read.all',expected=403,code='access_denied')
        self.command(case,prior.enable.document(True,'3',APP))
        self.response(case=case,value='kdg_capture.capture.read.all',expected=403,code='access_denied')
        target=self.targets[case]
        self.command(case,assign.document(target['other'],target['other_member'],permission=READ))
        # Synthetic owner fixture retirement; retain its actual history/state.
        db=self.db(case,'owner_urls')
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),dict(actor=ACTOR,org=ORG))
                c.execute(text('UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)'),dict(id=target['account']))
        finally:db.dispose()
        before=self.snapshot(case)
        self.response(case=case,expected=403,code='access_denied')
        assert self.snapshot(case)==before,'deleted_profile_check_mutated_state'
        # Obtain the already-established second actor, without creating identity.
        db=self.db(case,'owner_urls')
        try:
            with db.connect() as c:
                target['other_actor']=str(c.execute(text('SELECT actor_id FROM identity.account_actor WHERE account_id=CAST(:id AS uuid)'),dict(id=target['other'])).scalar_one())
        finally:db.dispose()
        self.response(case=case,account=target['other'])
        db=self.db(case,'owner_urls')
        try:
            with db.begin() as c:
                c.execute(text("SELECT set_config('app.actor_id',:actor,true),set_config('app.org_id',:org,true)"),dict(actor=ACTOR,org=ORG))
                c.execute(text('UPDATE identity.org SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)'),dict(id=ORG))
        finally:db.dispose()
        before=self.snapshot(case)
        self.response(case=case,account=target['other'],expected=403,code='access_denied')
        assert self.snapshot(case)==before,'deleted_organization_check_mutated_state'
        self.check_owners(case)
        self.record('KDG-app-binding-wrong-registration-current-profile-and-organization-HTTP-denials')
    def all(self):
        marker=self.proof/'organization-check-source.json';assert not marker.exists(),'qualification_already_started'
        captured=sources(self.proof)
        with marker.open('x') as output:json.dump(captured,output,sort_keys=True,indent=2)
        marker.chmod(0o600)
        self.reference_boundaries();self.prepare();self.prepare_reader();self.upgrade();self.drift();self.reads();self.role_denials();self.lifecycle()
        assert sources(self.proof)==captured,'qualification_source_changed'
        retained=dict(reference_state=self.snapshot('reference'),sources=captured,logs=logs(self.proof),state=self.snapshot('bridge'),catalog=self.raw_catalog(),stages=self.results)
        path=self.proof/'organization-check-retained.json'
        with path.open('x') as output:json.dump(retained,output,sort_keys=True,indent=2)
        path.chmod(0o600);self.verify_retained()
    def verify_retained(self):
        retained=json.loads((self.proof/'organization-check-retained.json').read_text())
        assert sources(self.proof)==retained['sources'] and logs(self.proof)==retained['logs'],'retained_source_log_changed'
        self.check_owners();self.check_owners('reference')
        assert self.snapshot('reference')==retained['reference_state'],'retained_reference_changed'
        assert self.snapshot('bridge')==retained['state'] and self.raw_catalog()==retained['catalog'],'retained_database_changed'
        self.record('independent-read-only-retained-owner-source-log-state-inspection')


def main():
    assert sys.argv[1:] in (['--all'],['--verify-retained']),'qualification_action_invalid'
    proof=Path(os.environ['IDENTITY_QUALIFICATION_DIR']).resolve()
    private,_=base.load_fixture(proof)
    qualification=Qualification(proof,private)
    qualification.all() if sys.argv[1:] == ['--all'] else qualification.verify_retained()


def run():
    try:main()
    except Exception as error:
        print('organization_check_qualification_failed:'+type(error).__name__,file=sys.stderr)
        raise SystemExit(1) from None


if __name__=='__main__':run()
