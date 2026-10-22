"""Source-bound Access10 staging using the existing private four-group owner fixture."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from hashlib import sha256
import json,os,re,subprocess,sys,time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_organization_application_configure as prior
from sqlalchemy import text
ROOT,ACCESS,ACTOR=prior.ROOT,prior.ACCESS,prior.ACTOR
base,storage,baseline=prior.base,prior.storage,prior.baseline
CASES=prior.CASES
base.CASES=CASES
load_fixture=base.load_fixture
ORG1,ORG2=prior.ORG1,prior.ORG2
NIL=storage.NIL
PERMISSIONS=('pts.poetry.read','pts.poetry.export','pts.poetry.documents')
NEW=('scope_kind','revision','revoked_at','created_actor_id','updated_actor_id','updated_at')
INSERT="INSERT INTO access.grants(org_id,id,user_id,permission) VALUES(CAST(:org AS uuid),:id,CAST(:user AS uuid),:permission)"


PREVIOUS_INVENTORY_SHA256='b276f6292c88e901d5850ba56bd9f93205560848f9840981e719eff03845f787'


def previous_inventory(proof):
    previous=json.loads((proof/'previous-source.json').read_text())
    assert previous['baseline_commit']=='7a565562c7b5086f2f7b432358f0048c45a47efc'
    inventory=json.dumps(previous['sources'],sort_keys=True,separators=(',',':')).encode()
    assert sha256(inventory).hexdigest()==PREVIOUS_INVENTORY_SHA256,'previous_inventory_mismatch'
    root=proof/'previous-root'
    for name,digest in previous['sources'].items():
        path=root/name
        assert path.resolve().is_relative_to(root.resolve())
        assert sha256(path.read_bytes()).hexdigest()==digest,'previous_source_mismatch'
    return previous


def qualification_logs(proof):
    # Only outputs owned by this aggregate; root stdout/inspection stays independent.
    patterns=[re.escape(case)+r'-(?:(?:head|access_[0-9]{4})-[0-9]+|identity19-repeat)\.log' for case in CASES]
    patterns += [r'previous9-[a-z-]+\.log',r'identity-drift-[a-z]+\.json',r'injected-postcondition\.log',r'cli-execute\.json']
    return {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(proof.iterdir())
            if any(re.fullmatch(pattern,p.name) for pattern in patterns)}


def verify_qualification_logs(proof,expected):
    assert type(expected) is dict and expected,'qualification_logs_missing'
    assert qualification_logs(proof)==expected,'qualification_log_custody_mismatch'


def previous_receipts(result,values):
    # Reject arbitrary child output. Reuse the current compact wire validator and
    # bind every result target to its already-approved synthetic command.
    assert result.returncode==0 and not result.stderr,'actual_previous9_adapter_failed'
    body=json.loads(result.stdout)
    assert type(body) is dict and set(body)=={'ok','receipts'} and body['ok'] is True
    receipts=body['receipts'];assert type(receipts) is list and len(receipts)==len(values)
    approved=[]
    for value,receipt in zip(values,receipts):
        assert set(receipt)=={'operation_id','result','command_version','result_version','committed_at','status'}
        assert receipt['operation_id']==value['operation_id'] and receipt['status']=='committed'
        wire=dict(receipt['result']);assert wire.pop('command')==value['command']
        target=dict(app_id=value['payload']['app_id'])
        if value['command'] in ('permission.register','entry_permission.register'):target['permission']=value['payload']['permission']
        if value['command']=='organization_application.configure':target['org_id']=value['scope']['org_id']
        assert wire['target']==target
        parsed=base.adapter._receipt((wire,receipt['command_version'],receipt['result_version'],datetime.fromisoformat(receipt['committed_at'])),value['operation_id'],value['command'])
        approved.append(json.loads(json.dumps(asdict(parsed),default=str)))
    return approved


def safe_child_failure(result):
    safe=dict(error_class='ChildFailure',sqlstate=None,returncode=result.returncode)
    try:
        body=json.loads(result.stdout)
        if type(body) is dict and set(body)=={'ok','error_class','sqlstate'} and body['ok'] is False:
            if body['error_class'] in ('AssertionError','OperationalError','IntegrityError','DBAPIError','OperatorError','ChildFailure'):safe['error_class']=body['error_class']
            state=body['sqlstate']
            if type(state) is str and re.fullmatch('[A-Z0-9]{5}',state):safe['sqlstate']=state
    except (ValueError,TypeError):pass
    return safe


def source_snapshot(proof):
    # Bind every consumed helper, not only the direct import. No old proof is edited.
    modules=(prior,storage,storage.prior,storage.prior.prior,storage.prior.prior.prior)
    paths=base.source_paths(proof)+[proof/'runtime-credential.json',Path(__file__),*(Path(m.__file__).resolve() for m in modules)]
    captured={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    manifest=proof/'previous-source.json';previous=previous_inventory(proof)
    previous_root=proof/'previous-root'
    for name,digest in previous['sources'].items():
        path=previous_root/name
        assert path.resolve().is_relative_to(previous_root.resolve())
        assert sha256(path.read_bytes()).hexdigest()==digest,'previous_source_mismatch'
        captured[str(path.relative_to(ROOT))]=digest
    captured[str(manifest.relative_to(ROOT))]=sha256(manifest.read_bytes()).hexdigest()
    return captured


EXPLICIT_INSERT=INSERT.replace('permission) VALUES','permission,'+','.join(NEW)+') VALUES').replace(':permission)',':permission,'+','.join(':'+name for name in NEW)+')')


def provenance():
    return dict(scope_kind='organization',revision=1,revoked_at=None,created_actor_id=None,updated_actor_id=None,updated_at=None)


def parameters(org=ORG1):
    return dict(org=org,id='opaque:'+uuid4().hex,user=str(uuid4()),permission=PERMISSIONS[0])


class Qualification(prior.Qualification):
    def migrate(self,case,head='access_0010',success=True):
        # This historical proof retains its original target when current head advances.
        return super().migrate(case,'access_0010' if head=='head' else head,success)
    def prepare_cases(self):
        for case in CASES:
            self.migrate(case,'access_0009' if case in ('upgrade','rollback') else 'head')
            self.seed(case);self.command(case,base.document())
            for org in (ORG1,ORG2):self.org_sql(case,f"INSERT INTO identity.org(id,name,slug) VALUES('{org}','Synthetic storage organization','synthetic-{org}')")
            if case!='rollback':self.authority(case)
        self.record('fresh10-and-exact9-controlled-owner-fixtures-with-Identity19-no-grant-activation')
    def owner_insert(self,case,values=None,extra='',context=ORG1):
        engine=self.db(case)
        try:
            with engine.begin() as c:
                if context is not None:c.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=context))
                c.exec_driver_sql("SET LOCAL app.actor_id='opaque legacy creator'")
                c.execute(text(INSERT+extra),values or parameters())
        finally:engine.dispose()
    def grant_functional(self):
        case='configure'
        before=self.snapshot(case)
        for org in (ORG1,ORG2):
            for permission in PERMISSIONS:
                self.owner_insert(case,parameters(org)|dict(permission=permission),context=org)
        rows=self.snapshot(case)['grants']
        assert len(rows)==6 and all(row[7:]==['organization',1,None,None,None,None] for row in rows)
        assert all(row[5]=='opaque legacy creator' and row[6] is None for row in rows)
        engine=self.db(case)
        try:
            with engine.begin() as c:
                c.exec_driver_sql(f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET membership_id=7,revision=9223372036854775807,revoked_at='2001-01-01Z',created_actor_id='{ACTOR}',updated_actor_id='{ACTOR}',updated_at='2002-01-01Z'")
        finally:engine.dispose()
        after=self.snapshot(case)
        assert sum(row[8]==9223372036854775807 for row in after['grants'])==3
        for key in prior.TABLES:
            if key!='grants':assert after[key]==before[key],key
        self.migrate(case);assert self.snapshot(case)==after
        for revision in (1,9223372036854775807):
            values=parameters()|provenance()|dict(revision=revision,revoked_at='2003-01-01Z',created_actor_id=ACTOR,updated_actor_id=ACTOR,updated_at='2004-01-01Z')
            self.explicit_insert(case,values)
            row=next(row for row in self.snapshot(case)['grants'] if row[1]==values['id'])
            assert row[7:9]==['organization',revision] and row[10:12]==[ACTOR,ACTOR] and row[9] and row[12]
        self.explicit_insert(case,parameters()|provenance())
        self.record('valid-explicit-insert-scope-revision1-max-null-and-finite-provenance')
        self.record('all-three-legacy-permissions-opaque-creators-defaults-null-and-positive-membership-revision1-max-finite-optional-provenance-owner-update-repeat')
    def explicit_insert(self,case,values):
        engine=self.db(case)
        try:
            with engine.begin() as c:
                c.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=values['org']))
                c.exec_driver_sql("SET LOCAL app.actor_id='opaque legacy creator'")
                c.execute(text(EXPLICIT_INSERT),values)
        finally:engine.dispose()
    def grant_constraints(self):
        case='guards';self.owner_insert(case)
        invalid=[('revision',0,'23514','grants_revision_positive'),('revision',-1,'23514','grants_revision_positive'),('revision',None,'23502',None),('scope_kind','account','23514','grants_scope_kind_organization'),('scope_kind',None,'23502',None)]
        invalid += [(col,NIL,'23514','grants_'+col+'_non_nil') for col in ('created_actor_id','updated_actor_id')]
        invalid += [(col,value,'23514','grants_'+col+'_finite') for col in ('revoked_at','updated_at') for value in ('infinity','-infinity')]
        prefix=f"SET LOCAL app.actor_id='legacy';INSERT INTO access.grants(org_id,id,user_id,permission) VALUES('{ORG1}','rollback-first','{ORG2}','pts.poetry.read');"
        for col,value,state,constraint in invalid:
            # A successful earlier write must also disappear on structural refusal.
            self.refused(case,'UPDATE access.grants SET '+col+'=:value',state,parameters=dict(value=value),constraint=constraint,prefix=prefix)
            self.refused(case,EXPLICIT_INSERT,state,parameters=parameters()|provenance()|{col:value},constraint=constraint,prefix=prefix)
        self.record('named-scope-revision-actor-time-constraints-and-not-null-denials-whole-transaction-rollback')
    def grant_privileges(self):
        case='guards';self.owner_insert(case,parameters(ORG2),context=ORG2)
        before=self.snapshot(case)
        # Root copies the already-existing restricted runtime credential privately;
        # the four-group fixture and global roles/secrets remain unchanged.
        with base.dev.directory(self.proof) as directory:
            base.dev.check_private(directory)
            credential=base.dev.decode(base.dev.read_at(directory,'runtime-credential.json',protected=True))
        assert type(credential) is dict and set(credential)=={'password'}
        assert type(credential['password']) is str and credential['password']
        source=self.db(case)
        runtime=source.url.set(username='access_runtime',password=credential['password']);source.dispose()
        from sqlalchemy import create_engine
        engine=create_engine(runtime,hide_parameters=True,connect_args=base.CONNECTION_ARGS)
        try:
            with engine.connect() as c:
                for org in (None,ORG2,ORG1):
                    with c.begin():
                        if org:c.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=org))
                        actual=json.loads(json.dumps([list(row) for row in c.exec_driver_sql('SELECT * FROM access.grants ORDER BY org_id,id')],default=str))
                        assert actual==[row for row in before['grants'] if row[0]==org]
                        if org:assert actual,'runtime_org_fixture_empty'
                with c.begin():assert not c.exec_driver_sql('SELECT * FROM access.grants').all()
            for sql in ('INSERT INTO access.grants(org_id,id,user_id,permission) SELECT org_id,id,user_id,permission FROM access.grants WHERE false','UPDATE access.grants SET revision=revision WHERE false','DELETE FROM access.grants WHERE false','TRUNCATE access.grants'):
                try:
                    with engine.begin() as c:c.exec_driver_sql(sql)
                except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                else:raise AssertionError('runtime_grant_write_accepted')
        finally:engine.dispose()
        for sql in ('INSERT INTO access.grants(org_id,id,user_id,permission) SELECT org_id,id,user_id,permission FROM access.grants WHERE false','SELECT * FROM access.grants','UPDATE access.grants SET revision=revision WHERE false','DELETE FROM access.grants WHERE false','TRUNCATE access.grants'):
            self.refused(case,sql,'42501',role='access_operator_urls')
        admin=self.admin(case)
        try:
            for role in ('access_command_owner','access_operator_authority_owner'):
                for sql in ('INSERT INTO access.grants(org_id,id,user_id,permission) SELECT org_id,id,user_id,permission FROM access.grants WHERE false','UPDATE access.grants SET revision=revision WHERE false','DELETE FROM access.grants WHERE false','TRUNCATE access.grants'):
                    try:
                        with admin.begin() as c:c.exec_driver_sql('SET LOCAL ROLE '+role);c.exec_driver_sql(sql)
                    except Exception as error:assert getattr(getattr(error,'orig',None),'sqlstate',None)=='42501'
                    else:raise AssertionError('definer_grant_write_accepted')
        finally:admin.dispose()
        assert self.snapshot(case)==before
        self.record('actual-runtime-org-and-missing-context-rls-local-context-reset-select-only-operator-definer-raw-write-refusal')
    def previous9(self,case,values,label):
        code="""import sys,json,os
try:
 from dataclasses import asdict
 sys.path.insert(0,os.environ['PREVIOUS_OWNER'])
 import access_operator as a
 from sqlalchemy import create_engine
 engine=create_engine(os.environ['QUALIFICATION_URL'].replace('postgresql:','postgresql+psycopg:'),hide_parameters=True)
 try:
  with engine.connect() as c:
   receipts=[]
   for value in json.loads(os.environ['QUALIFICATION_COMMANDS']):
    receipt=a.execute(c,json.dumps(value).encode())
    assert a.execute(c,json.dumps(value).encode())==receipt
    target=dict(command=value['command'],app_id=value['payload']['app_id'])
    if value['command'] in ('permission.register','entry_permission.register'):target['permission']=value['payload']['permission']
    if value['command']=='organization_application.configure':target['org_id']=value['scope']['org_id']
    assert a.outcome(c,value['operation_id'],**target)==receipt
    receipts.append(asdict(receipt))
   print(json.dumps(dict(ok=True,receipts=receipts),default=str))
 finally:engine.dispose()
except Exception as error:
 import re
 name=type(error).__name__
 if name not in ('AssertionError','OperationalError','IntegrityError','DBAPIError','OperatorError'):name='ChildFailure'
 state=getattr(getattr(error,'orig',None),'sqlstate',None)
 if type(state) is not str or not re.fullmatch('[A-Z0-9]{5}',state):state=None
 print(json.dumps(dict(ok=False,error_class=name,sqlstate=state)))
 raise SystemExit(1) from None
"""
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',PREVIOUS_OWNER=str(self.proof/'previous-root/services/access'),QUALIFICATION_URL=self.private['access_operator_urls'][case],QUALIFICATION_COMMANDS=json.dumps(values))
        path=self.proof/('previous9-'+label+'.log')
        try:
            result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=30)
        except subprocess.TimeoutExpired:
            path.write_text(json.dumps(dict(error_class='ChildTimeout',sqlstate=None,returncode=None))+'\n')
            raise AssertionError('actual_previous9_adapter_timeout') from None
        try:receipts=previous_receipts(result,values)
        except Exception:
            path.write_text(json.dumps(safe_child_failure(result))+'\n')
            raise AssertionError('actual_previous9_adapter_failed') from None
        path.write_text(json.dumps(receipts,sort_keys=True)+'\n')
        return receipts
    def upgrade_previous(self):
        case='upgrade';assert self.snapshot(case)['alembic_version']==[['access_0009']]
        values=self.previous8_documents('previous9_before')+[prior.document(app='previous9_before')]
        receipts=self.previous9(case,values,'before-upgrade')
        for org in (ORG1,ORG2):
            for i,permission in enumerate(PERMISSIONS):
                p=parameters(org)|dict(permission=permission)
                self.owner_insert(case,p,context=org)
                engine=self.db(case)
                try:
                    with engine.begin() as c:
                        c.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=org))
                        c.execute(text("UPDATE access.grants SET created_at='1990-01-01Z',membership_id=:membership WHERE id=:id"),dict(membership=None if i==0 else i,id=p['id']))
                finally:engine.dispose()
        before=self.snapshot(case)
        assert sorted((row[6] for row in before['grants']),key=repr)==[1,1,2,2,None,None]
        self.migrate(case);after=self.snapshot(case)
        assert after['alembic_version']==[['access_0010']]
        for name in prior.TABLES:
            if name=='grants':
                assert [row[:7] for row in after[name]]==before[name]
                assert all(row[7:]==['organization',1,None,None,None,None] for row in after[name])
            else:assert after[name]==before[name],name
        assert self.previous9(case,values,'retained-after-upgrade')==receipts
        assert self.snapshot(case)==after
        fresh=self.previous8_documents('previous9_after')+[prior.document(app='previous9_after')]
        assert len(self.previous9(case,fresh,'new-after-upgrade'))==5
        state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        self.record('populated-exact9-upgrade10-original-projection-historical-creation-time-five-old-command-receipts-new-replay-lookup-repeat-preserved')
    def rollback_recovery(self):
        case='rollback';self.owner_insert(case)
        before=self.snapshot(case)
        assert before['alembic_version']==[['access_0009']]
        engine=self.db(case)
        try:
            with engine.connect() as c:
                tx=c.begin()
                try:
                    c.exec_driver_sql('LOCK TABLE access.grants IN ACCESS SHARE MODE')
                    started=time.monotonic();self.migrate(case,success=False)
                    elapsed=time.monotonic()-started
                    assert 2.5<=elapsed<15,'grant_relation_lock_timeout_not_observed'
                finally:tx.rollback()
        finally:engine.dispose()
        assert self.snapshot(case)==before
        self.record('exact9-held-grants-relation-lock-bounded-alter-timeout-unchanged-data-catalog-history')
        # Existing advisory/injected-failure proof ends in explicit forward retry.
        super().rollback_recovery()
        assert self.snapshot(case)['alembic_version']==[['access_0010']]
    def identity_drift_refusal(self,case,label,alter,restore):
        original=self.snapshot(case)
        self.execute_sql(case,alter)  # Commit deliberate fixture drift before the child.
        try:
            drifted=self.snapshot(case)
            env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',IDENTITY_MIGRATION_DATABASE_URL=self.private['owner_urls'][case].replace('postgresql:','postgresql+psycopg:'))
            code="""import sys,json
sys.path.insert(0,"""+repr(str(ACCESS/'identity-migrations'))+""")
import identity_baseline as b
from alembic import command
from alembic.config import Config
try:command.upgrade(Config("""+repr(str(ACCESS/'identity-alembic.ini'))+"""),'head')
except b.BaselineError as error:
 print(json.dumps(dict(refused=str(error)=='identity_target_role_unsafe')))
 raise SystemExit(1) from None
"""
            result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
            # Persist only fixed selected evidence; stderr and tracebacks are discarded.
            refused=result.returncode==1 and result.stdout.strip()==b'{"refused": true}'
            (self.proof/('identity-drift-'+label+'.json')).write_text(json.dumps(dict(refused=refused,returncode=result.returncode))+'\n')
            assert refused,'restricted_identity19_drift_refusal_missing'
            assert self.snapshot(case)==drifted,'identity_refusal_changed_drifted_state'
        finally:self.execute_sql(case,restore)
        assert self.snapshot(case)==original,'fixture_drift_restore_changed_state'
    def catalog_and_identity(self):
        case='drift';before=self.snapshot(case);engine=self.db(case)
        alterations=[
            'ALTER TABLE access.grants DROP CONSTRAINT grants_revision_positive',
            'ALTER TABLE access.grants ALTER COLUMN scope_kind DROP NOT NULL',
            'ALTER TABLE access.grants ALTER COLUMN revision SET DEFAULT 2',
            'ALTER TABLE access.grants NO FORCE ROW LEVEL SECURITY',
            'GRANT UPDATE ON access.grants TO access_command_owner',
            'GRANT SELECT ON access.grants TO access_operator',
            "UPDATE access.alembic_version SET version_num='access_unknown'",
        ]
        try:
            for sql in alterations:
                with engine.connect() as c:
                    tx=c.begin()
                    try:
                        c.exec_driver_sql(sql)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('grant_storage_catalog_drift_accepted')
                    finally:tx.rollback()
                assert self.snapshot(case)==before
        finally:engine.dispose()
        for label,alter,restore in (
            ('column','ALTER TABLE access.grants RENAME COLUMN revision TO fixture_revision','ALTER TABLE access.grants RENAME COLUMN fixture_revision TO revision'),
            ('constraint','ALTER TABLE access.grants DROP CONSTRAINT grants_revision_positive','ALTER TABLE access.grants ADD CONSTRAINT grants_revision_positive CHECK (revision > 0)'),
            ('acl','GRANT UPDATE ON access.grants TO access_command_owner','REVOKE UPDATE ON access.grants FROM access_command_owner'),
        ):self.identity_drift_refusal(case,label,alter,restore)
        self.record('committed-column-marker-constraint-acl-drift-restricted-Identity19-refuses-preserves-exact-drifted-state-explicit-fixture-restore')
        # Reuse exact9 command/catalog and genuine restricted Identity19 repeat.
        super().catalog_and_identity()
        self.record('exact10-grant-column-constraint-default-rls-acl-history-drift-refusal-without-normalization')
    def retained(self):
        for case in CASES:
            engine=self.db(case)
            try:
                with engine.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
                    assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[('access_0010',)],'retained_head_not_ten'
            finally:engine.dispose()
        self.record('separate-read-only-exact10-retained-inspection')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    captured=source_snapshot(proof);witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.grant_functional,q.grant_constraints,q.grant_privileges,q.functional,q.authority_and_identity,q.retry_and_recovery,q.guards,q.deferred_evidence_and_overflow,q.forged_evidence_and_merge,q.concurrency,q.freshness_and_revocation,q.late_wait_expiry,q.context_and_login_boundaries,q.upgrade_previous,q.rollback_recovery,q.catalog_and_identity,q.cli,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in CASES},indent=2)+'\n')
    else:
        results=json.loads((proof/'results.json').read_text())
        assert results['status']=='passed' and results['source']==captured
        verify_qualification_logs(proof,results['logs'])
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in CASES}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    (proof/('results.json' if args.all else 'retained-results.json')).write_text(json.dumps(dict(status='passed',steps=q.results,source=captured,logs=qualification_logs(proof)),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
