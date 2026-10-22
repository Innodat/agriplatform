"""Current-head consuming proof of the existing Identity point dependency only."""
if not __debug__:
    raise RuntimeError('pregrant_qualification_optimized_python_prohibited')
import argparse
from dataclasses import asdict
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
from uuid import uuid4
from sqlalchemy import create_engine,text
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_application_register as base
import qualify_organization_application_storage as storage
ROOT,ACCESS,ACTOR=base.ROOT,base.ACCESS,base.ACTOR
CASES=frozenset({'clean'})
base.CASES=CASES
load_fixture=base.load_fixture
ORG='11111111-1111-4111-8111-111111111111'
OTHER='22222222-2222-4222-8222-222222222222'
NIL='00000000-0000-0000-0000-000000000000'
DISPLAY='Synthetic pre-grant é 🙂'
CALL='SELECT account_id::text,membership_id,membership_revision,actor_id::text,display_name FROM identity.organization_account_target(CAST(:target AS uuid),CAST(:member AS bigint))'
LIST='SELECT * FROM identity.organization_account_candidates(NULL::uuid)'
identity_spec=importlib.util.spec_from_file_location('pregrant_identity_baseline',ACCESS/'identity-migrations/identity_baseline.py')
identity=importlib.util.module_from_spec(identity_spec);identity_spec.loader.exec_module(identity)
import identity_operator


def digest(path):
    assert not path.is_symlink(),'source_symlink_refused'
    return sha256(path.read_bytes()).hexdigest()


def credential(proof,name):
    with base.dev.directory(proof) as directory:
        base.dev.check_private(directory)
        value=base.dev.decode(base.dev.read_at(directory,name,protected=True))
    assert type(value) is dict and set(value)=={'password'}
    assert type(value['password']) is str and value['password']
    return value['password']


def source_snapshot(proof):
    paths=set(base.source_paths(proof))|set(Path(__file__).parent.glob('qualify_*.py'))
    paths|={proof/'root_qualification_driver.py',Path(__file__).resolve(),Path(__file__).with_name('test_identity_pregrant_target.py'),ACCESS/'IDENTITY-PREGRANT-TARGET.md',proof/'runtime-credential.json',proof/'identity-operator-credential.json'}
    historical=proof.parent/'org-storage-reviewed-20261021'
    paths|={proof.parent/'access-registry-reviewed-20261021/credentials.json',historical/'credentials.json',historical/'run.json',proof.parent/'account-ensure-j9ial0p1/credentials.json'}
    run=json.loads((historical/'run.json').read_text())
    paths|={ROOT/'platform/deployment/.local/kdg'/run['run_id']/'supabase/config.toml'}
    paths|=set((ACCESS/'tools').glob('*.sql'))
    return {str(path.relative_to(ROOT)):digest(path) for path in sorted(paths)}


def qualification_logs(proof):
    return {path.name:digest(path) for path in sorted(proof.glob('*.log'))}


def verify_qualification_logs(proof,expected):
    assert type(expected) is dict and expected,'qualification_logs_missing'
    assert qualification_logs(proof)==expected,'qualification_log_custody_mismatch'


def verify_bootstrap_logs(proof,expected,*,initial=False):
    assert type(expected) is dict and expected,'bootstrap_logs_missing'
    assert all(Path(name).name==name and name.startswith('bootstrap') and name.endswith('.log') for name in expected),'bootstrap_log_inventory_mismatch'
    paths=proof.glob('*.log' if initial else 'bootstrap*.log')
    assert {path.name for path in paths}==set(expected),'bootstrap_log_inventory_mismatch'
    for name,value in expected.items():
        assert digest(proof/name)==value,'bootstrap_log_custody_mismatch'


def verify_fixture_reference(before,after,table,key,*,deleted):
    """Bound deliberate fixture effects; read probes retain their exact snapshots."""
    original=[row for row in before['identity'][table] if row['id']==key]
    current=[row for row in after['identity'][table] if row['id']==key]
    assert len(original)==len(current)==1,'fixture_reference_missing_or_duplicated'
    original,current=original[0],current[0]
    assert original['deleted_at'] is None
    if deleted:
        assert current['deleted_at'] is not None,'fixture_reference_not_deleted'
        assert datetime.fromisoformat(current['deleted_at']).utcoffset() is not None
    else:assert current['deleted_at'] is None,'fixture_reference_not_restored'
    row=deepcopy(current)
    row['deleted_at']=original['deleted_at']
    # Existing update triggers may advance this selected fixture row's timestamp.
    # Fixture writes also append existing audit evidence. Compare this reference;
    # the surrounding read probes independently require exact global snapshots.
    if 'updated_at' in original:
        assert 'updated_at' in current
        if current['updated_at'] is not None:
            stamp=datetime.fromisoformat(current['updated_at'])
            assert stamp.utcoffset() is not None
            if original['updated_at'] is not None:assert stamp>=datetime.fromisoformat(original['updated_at'])
        else:assert original['updated_at'] is None
        row['updated_at']=original['updated_at']
    assert row==original,'fixture_reference_changed_unrelated_fields'


def read_cases(target,member,expected):
    cases=[dict(label='setup-empty',expected=expected),dict(label='uuid-spelling',target=target.upper(),expected=expected),dict(label='valid-user-separate-caller',context=dict(kind='user',account=OTHER),expected=expected),dict(label='wrong-org',context=dict(org=OTHER),expected=[]),dict(label='wrong-account',target=OTHER,expected=[]),dict(label='wrong-member',member=member+1,expected=[])]
    for label,value in [('null-target',None),('nil-target',NIL)]:cases.append(dict(label=label,target=value,expected=[]))
    for label,value in [('null-member',None),('zero-member',0),('negative-member',-1),('missing-member',9223372036854775807)]:cases.append(dict(label=label,member=value,expected=[]))
    for field in ('org','actor'):
        for kind,value in [('missing',None),('empty',''),('malformed','malformed'),('nil',NIL)]:cases.append(dict(label=field+'-'+kind,context={field:value},expected=[]))
    for label,context in [('missing-context',dict(kind=None)),('empty-context',dict(kind='')),('malformed-context',dict(kind='malformed')),('nil-context',dict(kind=NIL)),('user-missing-account',dict(kind='user',account=None)),('user-empty-account',dict(kind='user')),('user-malformed-account',dict(kind='user',account='malformed')),('user-nil-account',dict(kind='user',account=NIL)),('setup-with-account',dict(account=OTHER)),('setup-malformed-account',dict(account='malformed')),('setup-nil-account',dict(account=NIL))]:cases.append(dict(label=label,context=context,expected=[]))
    for label,changes,state in [('invalid-uuid',dict(target='malformed'),'22P02'),('invalid-bigint',dict(member='malformed'),'22P02'),('overflow-bigint',dict(member='9223372036854775808'),'22003')]:cases.append(dict(label=label,sqlstate=state,**changes))
    return cases


class Qualification(storage.Qualification):
    admin=storage.Qualification.admin
    access_snapshot=storage.Qualification.snapshot

    def parameter_sql(self,sql,values=None,role='owner_urls'):
        db=self.db('clean',role)
        try:
            with db.begin() as c:return c.execute(text(sql),values or {}).all() if sql.lstrip().startswith('SELECT') else c.execute(text(sql),values or {})
        finally:db.dispose()

    def snapshot(self,case='clean'):
        value={'access':self.access_snapshot(case)}
        db=self.admin(case)
        try:
            with db.begin() as c:
                c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                assert c.exec_driver_sql('SELECT current_user').scalar_one()=='supabase_admin'
                assert c.exec_driver_sql('SELECT rolbypassrls OR rolsuper FROM pg_roles WHERE rolname=current_user').scalar_one()
                tables=c.exec_driver_sql("SELECT tablename FROM pg_tables WHERE schemaname='identity' ORDER BY tablename").scalars().all()
                value['identity']={name:c.exec_driver_sql('SELECT to_jsonb(t) FROM identity."'+name+'" t ORDER BY to_jsonb(t)::text').scalars().all() for name in tables}
                value['identity_sequences']=c.exec_driver_sql("SELECT sequencename,last_value FROM pg_sequences WHERE schemaname='identity' ORDER BY sequencename").all()
                value['identity_catalog']=identity.account_actor_catalog_snapshot(c)
        finally:db.dispose()
        return json.loads(json.dumps(value,default=str))

    def auxiliary_db(self,role):
        name={'identity_operator':'identity-operator-credential.json','access_runtime':'runtime-credential.json'}[role]
        source=self.db('clean');url=source.url.set(username=role,password=credential(self.proof,name));source.dispose()
        return create_engine(url,hide_parameters=True,connect_args=base.CONNECTION_ARGS)

    def invoke(self,command,payload,org=None):
        value=dict(schema_version=1,operation_id=str(uuid4()),command=command,scope=dict(kind='platform') if org is None else dict(kind='organization',org_id=org),payload=payload,reason_code='synthetic_fixture',evidence_ref='synthetic:pregrant/target')
        db=self.auxiliary_db('identity_operator')
        try:
            with db.connect() as c:
                assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('identity_operator','identity_operator');c.commit()
                receipt=identity_operator.execute(c,json.dumps(value).encode())
                self.receipts.append(json.loads(json.dumps(asdict(receipt),default=str)))
                return receipt
        finally:db.dispose()

    def prepare_cases(self):
        self.migrate('clean');self.receipts=[]
        self.parameter_sql("INSERT INTO identity.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('identity_operator',:actor,true,:actor,:actor)",dict(actor=ACTOR))
        for org in (ORG,OTHER):
            self.parameter_sql("INSERT INTO identity.org(id,name,slug) VALUES(:id,'Synthetic pre-grant organization',:slug)",dict(id=org,slug='synthetic-pregrant-'+org))
        for command,org in [('account_actor.ensure',None),('membership.join',ORG),('membership.join',OTHER),('membership.retire',ORG)]:
            self.parameter_sql("INSERT INTO identity.operator_authorities(id,database_login,command,scope_kind,org_id,enabled,created_by,updated_by) VALUES(:id,'identity_operator',:command,:scope,CAST(:org AS uuid),true,:actor,:actor)",dict(id=str(uuid4()),command=command,scope='platform' if org is None else 'organization',org=org,actor=ACTOR))
        self.target,self.actor,self.unmapped=str(uuid4()),str(uuid4()),str(uuid4())
        for account in (self.target,self.unmapped):
            self.parameter_sql('INSERT INTO auth.users(id,email) VALUES(:id,:email)',dict(id=account,email='synthetic-'+account+'@example.invalid'),role='databases')
        self.invoke('account_actor.ensure',dict(account_id=self.target,actor_id=self.actor,display_name=DISPLAY,expected_absent=True))
        def join(account,org):return self.invoke('membership.join',dict(account_id=account,expected_previous_membership_id=None,is_owner=False),org)
        self.member=int(join(self.target,ORG).result.target.membership_id)
        self.other_member=int(join(self.target,OTHER).result.target.membership_id)
        self.unmapped_member=int(join(self.unmapped,ORG).result.target.membership_id)
        self.expected=[(self.target,self.member,1,self.actor,DISPLAY)]
        state=self.snapshot()
        assert state['access']['grants']==[] and state['access']['organization_applications']==[]
        assert self.parameter_sql('SELECT count(*) FROM identity.account_actor WHERE account_id=CAST(:id AS uuid)',dict(id=self.unmapped))==[(0,)]
        self.record('supported-actual-identity-operator-ensure-join-unmapped-no-grants-or-admission')

    def context(self,c,org=ORG,actor=ACTOR,kind='setup',account=''):
        for name,value in [('org_id',org),('actor_id',actor),('context_kind',kind),('account_id',account)]:
            if value is not None:c.execute(text('SELECT set_config(:name,:value,true)'),dict(name='app.'+name,value=value))

    def begin_read(self,c,role=True):
        c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ ONLY')
        assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('access_migrator','access_migrator')
        if role:c.exec_driver_sql('SET LOCAL ROLE access_command_owner')
        assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==('access_migrator','access_command_owner' if role else 'access_migrator')
        assert c.exec_driver_sql('SHOW transaction_read_only').scalar_one()=='on'
        assert c.exec_driver_sql('SHOW transaction_isolation').scalar_one()=='read committed'

    def point(self,c,target=None,member=None):
        return c.execute(text(CALL),dict(target=target,member=member)).all()

    def assert_local_reset(self,c,login='access_migrator'):
        with c.begin():
            c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ ONLY')
            row=c.exec_driver_sql("SELECT session_user,current_user,pg_backend_pid(),current_setting('app.org_id',true),current_setting('app.actor_id',true),current_setting('app.context_kind',true),current_setting('app.account_id',true)").one()
            assert tuple(row[:2])==(login,login),'local_role_leaked'
            assert all(value in (None,'') for value in row[3:]),'local_context_setting_leaked'
            return row[2]

    def probe(self,c,target,member,expected,context=None,sqlstate=None):
        before=self.snapshot()
        try:
            with c.begin():
                self.begin_read(c);self.context(c,**(context or {}))
                actual=self.point(c,target,member)
                assert sqlstate is None,'typed_invalid_input_accepted'
                assert actual==expected,'pregrant_point_result_mismatch'
        except Exception as error:
            assert sqlstate is not None and getattr(getattr(error,'orig',None),'sqlstate',None)==sqlstate,'unexpected_point_refusal'
        self.assert_local_reset(c)
        assert self.snapshot()==before,'read_matrix_changed_persistent_state'

    def read_matrix(self):
        db=self.db('clean')
        try:
            with db.connect() as c:
                # Truly absent account on this fresh backend, before LOCAL setters.
                before=self.snapshot()
                with c.begin():
                    self.begin_read(c)
                    assert c.exec_driver_sql("SELECT current_setting('app.account_id',true)").scalar_one() is None
                    assert self.point(c,self.target,self.member)==[],'missing_context_accepted'
                    self.context(c,account=None)
                    assert self.point(c,self.target,self.member)==self.expected
                pid=self.assert_local_reset(c)
                assert self.snapshot()==before
                for item in read_cases(self.target,self.member,self.expected):
                    self.probe(c,item.get('target',self.target),item.get('member',self.member),item.get('expected',[]),item.get('context'),item.get('sqlstate'))
                self.probe(c,self.target,self.other_member,[])
                self.probe(c,self.unmapped,self.unmapped_member,[])
                before=self.snapshot()
                with c.begin():
                    self.begin_read(c)
                    assert self.point(c,self.target,self.member)==[],'local_context_leaked'
                assert self.assert_local_reset(c)==pid
                assert self.snapshot()==before
            # Return the connection to the pool, then borrow and inspect the same backend.
            with db.connect() as c:
                assert self.assert_local_reset(c)==pid,'pool_backend_not_reborrowed'
                before=self.snapshot()
                with c.begin():
                    self.begin_read(c)
                    assert self.point(c,self.target,self.member)==[],'pooled_context_leaked'
                assert self.assert_local_reset(c)==pid
                assert self.snapshot()==before
        finally:db.dispose()
        self.record('exact-five-values-setup-absent-empty-user-compatible-input-context-matrix-pooled-local-reset-no-effects')

    def soft_deletions(self):
        db=self.db('clean')
        try:
            with db.connect() as c:
                for table,key in [('users',self.target),('org',ORG)]:
                    original=self.snapshot()
                    self.parameter_sql('UPDATE identity.'+table+' SET deleted_at=statement_timestamp() WHERE id=CAST(:id AS uuid)',dict(id=key))
                    verify_fixture_reference(original,self.snapshot(),table,key,deleted=True)
                    self.probe(c,self.target,self.member,[])
                    self.parameter_sql('UPDATE identity.'+table+' SET deleted_at=NULL WHERE id=CAST(:id AS uuid)',dict(id=key))
                    verify_fixture_reference(original,self.snapshot(),table,key,deleted=False)
                    self.probe(c,self.target,self.member,self.expected)
        finally:db.dispose()
        self.record('soft-deleted-profile-org-no-row-explicit-fixture-restoration-current-recheck')

    def advance_revision(self):
        # Deliberate owner fixture write, distinct from the read no-effects proof.
        query='SELECT to_jsonb(m) FROM identity.org_member m WHERE id=:id'
        original=self.parameter_sql(query,dict(id=self.member))[0][0]
        assert original['revision']==1 and original['deleted_at'] is None
        self.parameter_sql('UPDATE identity.org_member SET updated_at=statement_timestamp() WHERE id=:id',dict(id=self.member))
        current=self.parameter_sql(query,dict(id=self.member))[0][0]
        assert current['revision']==2 and current['updated_at']!=original['updated_at']
        normalized=dict(current,revision=original['revision'],updated_at=original['updated_at'])
        assert normalized==original,'revision_fixture_changed_other_membership_fields'
        self.expected=[(self.target,self.member,2,self.actor,DISPLAY)]
        self.record('owner-fixture-timestamp-update-active-revision2-no-membership-authority-change')

    def lifecycle(self):
        retained=self.parameter_sql('SELECT to_jsonb(m) FROM identity.account_actor m WHERE account_id=CAST(:id AS uuid)',dict(id=self.target))
        self.invoke('membership.retire',dict(account_id=self.target,membership_id=str(self.member),expected_revision='2'),ORG)
        db=self.db('clean')
        try:
            with db.connect() as c:self.probe(c,self.target,self.member,[])
            replacement=self.invoke('membership.join',dict(account_id=self.target,expected_previous_membership_id=str(self.member),is_owner=False),ORG)
            new=int(replacement.result.target.membership_id)
            assert new!=self.member and replacement.result.revision=='1'
            with db.connect() as c:
                self.probe(c,self.target,self.member,[])
                self.probe(c,self.target,new,[(self.target,new,1,self.actor,DISPLAY)])
            assert self.parameter_sql('SELECT to_jsonb(m) FROM identity.account_actor m WHERE account_id=CAST(:id AS uuid)',dict(id=self.target))==retained
            assert self.parameter_sql('SELECT revision,deleted_at IS NOT NULL FROM identity.org_member WHERE id=:id',dict(id=self.member))==[(3,True)]
        finally:db.dispose()
        self.record('supported-retire-explicit-rejoin-new-id-revision1-old-id-never-substitutes-mapping-history-retained')

    def privileges(self):
        before=self.snapshot();db=self.db('clean')
        try:
            with db.connect() as c:
                for sql in [LIST,'SELECT * FROM identity.org','SELECT * FROM identity.users','SELECT * FROM identity.org_member','SELECT * FROM identity.account_actor','SELECT * FROM identity.actor']:
                    try:
                        with c.begin():self.begin_read(c);self.context(c);c.exec_driver_sql(sql).all()
                    except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                    else:raise AssertionError('command_owner_raw_or_list_allowed')
                    self.assert_local_reset(c)
        finally:db.dispose()
        for role in ('access_runtime','access_operator'):
            db=self.auxiliary_db(role) if role=='access_runtime' else self.db('clean','access_operator_urls')
            try:
                with db.connect() as c:
                    for sql in (CALL,LIST):
                        try:
                            with c.begin():
                                c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ ONLY')
                                assert tuple(c.exec_driver_sql('SELECT session_user,current_user').one())==(role,role)
                                self.context(c);c.execute(text(sql),dict(target=self.target,member=self.member)).all()
                        except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                        else:raise AssertionError('restricted_login_point_or_list_allowed')
                        self.assert_local_reset(c,login=role)
            finally:db.dispose()
        assert self.snapshot()==before,'privilege_checks_changed_state'
        self.record('actual-command-owner-point-only-list-raw-denied-actual-runtime-operator-point-list-denied-no-acl-change')

    def retained(self):
        before=self.snapshot()
        for role in ('owner_urls','access_owner_urls'):
            db=self.db('clean',role)
            try:
                with db.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ ONLY')
                    if role=='owner_urls':
                        identity.verify_owned_postcondition(c,require_head=True)
                        assert c.exec_driver_sql('SELECT version_num FROM identity.alembic_version').all()==[('identity_0019',)]
                    else:
                        base.baseline.preflight(c);base.baseline.verify_postcondition(c)
                        assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[('access_0010',)]
            finally:db.dispose()
        assert self.snapshot()==before
        assert before['access']['grants']==[] and before['access']['organization_applications']==[]
        self.record('read-only-exact-Identity19-Access10-catalog-state-no-grant-activation')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw))
    # Claim before fixture/DB I/O, and never restart an incomplete aggregate.
    if args.all:(proof/'all-started').open('x').close()
    private,run=load_fixture(proof)
    captured=source_snapshot(proof);witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==captured,'bootstrap_source_custody_mismatch'
    verify_bootstrap_logs(proof,witness['logs'],initial=args.all)
    assert set(witness['generated_inputs'])=={'credentials.json','run.json'},'generated_input_inventory_mismatch'
    for name,expected in witness['generated_inputs'].items():
        assert digest(proof/name)==expected,'generated_input_custody_mismatch'
    if not args.all:
        results=json.loads((proof/'results.json').read_text())
        assert results['status']=='passed' and results['source']==captured
        verify_qualification_logs(proof,results['logs'])
        assert digest(proof/'pregrant-receipts.json')==results['receipts']
        assert digest(proof/'retained-state.json')==results['retained_state']
    q=Qualification(proof,private)
    if args.all:
        for method in (q.prepare_cases,q.retained,q.soft_deletions,q.privileges,q.advance_revision,q.read_matrix,q.lifecycle,q.retained):method()
        (proof/'pregrant-receipts.json').write_text(json.dumps(q.receipts,indent=2)+'\n')
        (proof/'retained-state.json').write_text(json.dumps(q.snapshot(),indent=2)+'\n')
    else:
        before=json.loads((proof/'retained-state.json').read_text());assert q.snapshot()==before
        q.retained();assert q.snapshot()==before
    verify_bootstrap_logs(proof,witness['logs'])
    assert captured==source_snapshot(proof),'qualification_source_changed'
    result=dict(status='passed',steps=q.results,source=captured,logs=qualification_logs(proof),receipts=digest(proof/'pregrant-receipts.json'),retained_state=digest(proof/'retained-state.json'))
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
