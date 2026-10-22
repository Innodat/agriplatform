"""Bounded synthetic Access11 proof; storage integrity grants no effective access."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from dataclasses import asdict
from hashlib import sha256
import json,os,re,subprocess,sys,time
from pathlib import Path
from uuid import uuid4
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_application_register as base
import qualify_organization_application_storage as storage
import qualify_organization_application_configure as configure
import qualify_grant_lifecycle_storage as lifecycle
from sqlalchemy import text,create_engine
ROOT,ACCESS,ACTOR=base.ROOT,base.ACCESS,base.ACTOR
baseline=base.baseline
CASES=frozenset(('clean','upgrade','drift','failure','locks'))
base.CASES=CASES
load_fixture=base.load_fixture
ORG1,ORG2=storage.ORG1,storage.ORG2
PERMISSIONS=lifecycle.PERMISSIONS
INSERT=lifecycle.EXPLICIT_INSERT.replace('permission,scope_kind','permission,membership_id,scope_kind').replace(':permission,:scope_kind',':permission,:membership_id,:scope_kind')


def source_snapshot(proof):
    paths=set(base.source_paths(proof))|set(Path(__file__).parent.glob('qualify_*.py'))
    paths|={Path(__file__).with_name('test_grant_registry_bridge.py'),ACCESS/'GRANT-REGISTRY-BRIDGE.md',proof/'runtime-credential.json',proof/'root_qualification_driver.py',proof/'auth-helper-definitions.json'}
    historical=proof.parent/'org-storage-reviewed-20261021'
    paths|={proof.parent/'access-registry-reviewed-20261021/credentials.json',historical/'credentials.json',historical/'run.json'}
    # Bootstrap consumes the retained native run's config, never its secret values in logs.
    run=json.loads((historical/'run.json').read_text())
    paths|={ROOT/'platform/deployment/.local/kdg'/run['run_id']/'supabase/config.toml'}
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def qualification_logs(proof):
    patterns=[re.escape(case)+r'-(?:(?:head|access_[0-9]{4})-[0-9]+|identity19-repeat)\.log' for case in CASES]
    patterns += [r'identity-drift-[a-z]+\.json',r'injected-postcondition\.log',r'(?:locks|failure)-migration-refusal\.json']
    return {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(proof.iterdir()) if any(re.fullmatch(pattern,p.name) for pattern in patterns)}


def verify_qualification_logs(proof,expected):
    assert type(expected) is dict and expected,'qualification_logs_missing'
    assert qualification_logs(proof)==expected,'qualification_log_custody_mismatch'


def values(permission='kdg_capture.read.own',complete=True):
    return lifecycle.parameters()|lifecycle.provenance()|dict(permission=permission,membership_id=7 if complete else None,created_actor_id=ACTOR if complete else None,updated_actor_id=ACTOR if complete else None,updated_at='2002-01-01Z' if complete else None)


def permission_document(permission='kdg_capture.read.own',scope='organization'):
    value=base.document();value['command']='permission.register'
    value['payload'].update(permission=permission,scope_kind=scope)
    return value


def canonical_trigger_rows(rows):
    """Ignore only rebuilt PostgreSQL RI name suffixes in diagnostic snapshots."""
    result=[]
    for original in rows:
        row=list(original)
        match=re.fullmatch(r'RI_ConstraintTrigger_([ac])_[0-9]+',row[1])
        if row[3] is True and match:
            canonical='RI_ConstraintTrigger_'+match.group(1)
            # Replace the declaration's matching identifier only, preserving the
            # complete event/function/arguments/deferral definition and all fields.
            definition,count=re.subn(r'\ACREATE CONSTRAINT TRIGGER "'+re.escape(row[1])+r'" ',
                                     'CREATE CONSTRAINT TRIGGER "'+canonical+'" ',row[4],count=1)
            if count:
                row[1],row[4]=canonical,definition
        result.append(row)
    return sorted(result,key=lambda row:json.dumps(row,sort_keys=True))


class Qualification(storage.Qualification):
    admin=storage.Qualification.admin
    def snapshot(self,case):
        value=super().snapshot(case)
        value['catalog_triggers']=canonical_trigger_rows(value['catalog_triggers'])
        return value
    refused=storage.Qualification.refused
    def explicit_insert(self,case,values):
        e=self.db(case)
        try:
            with e.begin() as c:
                c.execute(text("SELECT set_config('app.org_id',:org,true)"),dict(org=values['org']))
                c.exec_driver_sql("SET LOCAL app.actor_id='opaque legacy creator'")
                c.execute(text(INSERT),values)
        finally:e.dispose()
    owner_insert=lifecycle.Qualification.owner_insert
    grant_privileges=lifecycle.Qualification.grant_privileges
    identity_drift_refusal=lifecycle.Qualification.identity_drift_refusal
    def seed(self,case):
        base.Qualification.seed(self,case)
        for command,scope,org in (('permission.register','platform','NULL'),('entry_permission.register','platform','NULL'),('application.set_enabled','platform','NULL'),('organization_application.configure','organization',"'"+ORG1+"'")):
            self.execute_sql(case,f"INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,org_id,enabled,created_by,updated_by) VALUES(gen_random_uuid(),'access_operator','{command}','{scope}',{org},true,'{ACTOR}','{ACTOR}')")
    def prepare_cases(self):
        for case in CASES:
            self.migrate(case,'access_0010' if case in ('upgrade','failure','locks') else 'head')
            self.seed(case)
            self.execute_sql(case,f"INSERT INTO identity.org(id,name,slug) VALUES('{ORG1}','Synthetic organization','synthetic-bridge')",'owner_urls')
        self.record('clean11-and-exact10-restricted-owner-fixtures-with-Identity19-service-actor')
    def functional(self):
        case='clean';self.command(case,base.document())
        self.command(case,permission_document())
        self.command(case,permission_document('account.only','account'))
        for org in (ORG1,ORG2):
            for permission in PERMISSIONS:self.owner_insert(case,lifecycle.parameters(org)|dict(permission=permission),context=org)
        rows=self.snapshot(case)['grants']
        assert len(rows)==6 and all(row[-1] is None and row[6] is None for row in rows)
        for org in (ORG1,ORG2):
            self.execute_sql(case,f"SET LOCAL app.org_id='{org}'; UPDATE access.grants SET membership_id=7,created_actor_id='{ACTOR}',updated_actor_id='{ACTOR}',updated_at='2002-01-01Z' WHERE permission IN ('pts.poetry.read','pts.poetry.export','pts.poetry.documents')")
            self.execute_sql(case,f"SET LOCAL app.org_id='{org}'; UPDATE access.grants SET membership_id=NULL,created_actor_id=NULL,updated_actor_id=NULL,updated_at=NULL WHERE permission IN ('pts.poetry.read','pts.poetry.export','pts.poetry.documents')")
        assert self.snapshot(case)['grants']==rows
        self.explicit_insert(case,values());self.explicit_insert(case,values()|dict(org=ORG2))
        self.explicit_insert(case,values(complete=False)|dict(revoked_at='2001-01-01Z'))
        assert all(row[-1]==row[3] for row in self.snapshot(case)['grants'] if row[3] not in PERMISSIONS)
        prefix=f"SET LOCAL app.actor_id='legacy';INSERT INTO access.grants(org_id,id,user_id,permission) VALUES('{ORG1}','rollback-first','{ORG2}','pts.poetry.read');"
        for permission in ('unknown.permission','account.only'):
            for revoked in (None,'2001-01-01Z'):
                self.refused(case,INSERT,'23503',values(permission)|dict(revoked_at=revoked),constraint='grants_registry_permission_scope_fkey',prefix=prefix)
        for field in ('membership_id','created_actor_id','updated_actor_id','updated_at'):
            self.refused(case,INSERT,'23514',values()|{field:None},constraint='grants_nonlegacy_active_fields',prefix=prefix)
        self.refused(case,"UPDATE access.grants SET revoked_at=NULL WHERE permission='kdg_capture.read.own' AND membership_id IS NULL",'23514',constraint='grants_nonlegacy_active_fields',prefix=prefix)
        for field in ('membership_id','created_actor_id','updated_actor_id','updated_at'):
            revoked=values()|{field:None,'revoked_at':'2001-01-01Z'}
            self.explicit_insert(case,revoked)
            row=next(row for row in self.snapshot(case)['grants'] if row[1]==revoked['id'])
            assert row[6:]==[revoked['membership_id'],'organization',1,'2001-01-01 00:00:00+00:00',revoked['created_actor_id'],revoked['updated_actor_id'],None if field=='updated_at' else '2002-01-01 00:00:00+00:00','kdg_capture.read.own']
            self.refused(case,'UPDATE access.grants SET revoked_at=NULL WHERE id=:id','23514',dict(id=revoked['id']),constraint='grants_nonlegacy_active_fields',prefix=prefix)
        transition=values(PERMISSIONS[0],complete=False)
        self.explicit_insert(case,transition)
        self.refused(case,"UPDATE access.grants SET permission='kdg_capture.read.own' WHERE id=:id",'23514',dict(id=transition['id']),constraint='grants_nonlegacy_active_fields',prefix=prefix)
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET permission='kdg_capture.read.own',membership_id=7,created_actor_id='{ACTOR}',updated_actor_id='{ACTOR}',updated_at='2002-01-01Z' WHERE id='{transition['id']}'")
        row=next(row for row in self.snapshot(case)['grants'] if row[1]==transition['id'])
        assert row[3]==row[-1]=='kdg_capture.read.own'
        self.refused(case,"UPDATE access.grants SET permission='unknown.permission' WHERE id=:id",'23503',dict(id=transition['id']),constraint='grants_registry_permission_scope_fkey',prefix=prefix)
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET permission='pts.poetry.export',membership_id=NULL,created_actor_id=NULL,updated_actor_id=NULL,updated_at=NULL WHERE id='{transition['id']}'")
        row=next(row for row in self.snapshot(case)['grants'] if row[1]==transition['id'])
        assert row[3]=='pts.poetry.export' and row[6] is None and row[10:]==[None,None,None,None]
        self.refused(case,"UPDATE access.grants SET registry_permission='pts.poetry.read'",'428C9',prefix=prefix)
        for field,value,constraint in [('membership_id',0,'grants_membership_id_positive'),('revision',0,'grants_revision_positive'),('created_actor_id',storage.NIL,'grants_created_actor_id_non_nil'),('updated_actor_id',storage.NIL,'grants_updated_actor_id_non_nil'),('updated_at','infinity','grants_updated_at_finite'),('revoked_at','-infinity','grants_revoked_at_finite')]:
            self.refused(case,INSERT,'23514',values()|{field:value},constraint=constraint,prefix=prefix)
        self.refused(case,"INSERT INTO access.grants(org_id,id,user_id,permission) VALUES ('"+ORG1+"','multi-good','"+ORG2+"','pts.poetry.read'),('"+ORG1+"','multi-bad','"+ORG2+"','unknown.permission')",'23514',constraint='grants_nonlegacy_active_fields',prefix="SET LOCAL app.actor_id='legacy'")
        # Both rows pass active-field CHECKs; the dependent second write reaches the FK.
        cte="""WITH first_write AS (
          INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at)
          VALUES(CAST(:org AS uuid),:id,CAST(:user AS uuid),'kdg_capture.read.own',7,CAST(:actor AS uuid),CAST(:actor AS uuid),'2002-01-01Z') RETURNING org_id,user_id)
          INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at)
          SELECT org_id,:bad_id,user_id,'unknown.permission',7,CAST(:actor AS uuid),CAST(:actor AS uuid),'2002-01-01Z' FROM first_write"""
        self.refused(case,cte,'23503',values()|dict(actor=ACTOR,bad_id='dependent-unknown'),constraint='grants_registry_permission_scope_fkey',prefix=prefix)
        before=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==before
        self.record('permission-update-recomputation-each-revoked-missing-field-org2-nonlegacy-runtime-dependent-cte-fk-rollback')
        self.record('legacy-null-preservation-registered-org-active-revoked-fk-required-fields-generated-override-alternate-multirow-whole-transaction-rollback')
    def upgrade(self):
        case='upgrade';self.command(case,base.document())
        p=permission_document();entry=base.document();entry['command']='entry_permission.register';entry['payload']['permission']='kdg_capture.read.own'
        enabled=base.document();enabled['command']='application.set_enabled';enabled['payload']=dict(app_id='synthetic_app',enabled=True,expected_revision='1')
        docs=[base.document(),p,entry,enabled,configure.document()]
        receipts=[self.command(case,v) for v in docs]
        for org in (ORG1,ORG2):
            for permission in PERMISSIONS:
                self.owner_insert(case,lifecycle.parameters(org)|dict(permission=permission),context=org)
        # Exercise exact old owner SQL, opaque IDs/text and original historical time.
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET created_at='1990-01-01Z',membership_id=7,created_actor_id='{ACTOR}',updated_actor_id='{ACTOR}',updated_at='2002-01-01Z'")
        before=self.snapshot(case);self.identity_repeat(case)
        self.migrate(case);after=self.snapshot(case)
        assert after['alembic_version']==[['access_0011']]
        assert [row[:-1] for row in after['grants']]==before['grants'] and all(row[-1] is None for row in after['grants'])
        for name in configure.TABLES:
            if name!='grants':assert after[name]==before[name],name
        for value,receipt in zip(docs,receipts):
            assert self.command(case,value)==receipt
            target=dict(command=value['command'],app_id=value['payload']['app_id'])
            if 'permission' in value['payload']:target['permission']=value['payload']['permission']
            if value['command']=='organization_application.configure':target['org_id']=ORG1
            e=self.db(case,'access_operator_urls')
            try:
                with e.connect() as c:assert base.adapter.outcome(c,value['operation_id'],**target)==receipt
            finally:e.dispose()
        self.owner_insert(case);state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        self.record('populated10-upgrade11-original-values-five-unchanged-client-receipts-replay-lookup-old-owner-sql-repeat')
    def privileges(self):
        # Existing behavior helper's fixed case is mapped locally; no fixture framework.
        self.private={group:dict(urls,guards=urls['clean']) for group,urls in self.private.items()}
        try:self.grant_privileges()
        finally:self.private={group:{case:url for case,url in urls.items() if case!='guards'} for group,urls in self.private.items()}
    def identity_repeat(self,case):
        before=self.snapshot(case)
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',IDENTITY_MIGRATION_DATABASE_URL=self.private['owner_urls'][case].replace('postgresql:','postgresql+psycopg:'))
        result=subprocess.run([sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'identity-alembic.ini'),'upgrade','head'],cwd=ROOT,env=env,capture_output=True,timeout=40)
        path=self.proof/(case+'-identity19-repeat.log');path.write_bytes(result.stdout+result.stderr);path.chmod(0o600)
        assert result.returncode==0,'identity19_metadata_repeat_failed'
        assert self.snapshot(case)==before
    def drift(self):
        case='drift';before=self.snapshot(case);e=self.db(case)
        alterations=['ALTER TABLE access.grants DROP CONSTRAINT grants_nonlegacy_active_fields','ALTER TABLE access.grants DROP CONSTRAINT grants_registry_permission_scope_fkey','ALTER TABLE access.grants ALTER COLUMN registry_permission DROP EXPRESSION','ALTER TABLE access.grants NO FORCE ROW LEVEL SECURITY','GRANT UPDATE ON access.grants TO access_command_owner',"UPDATE access.alembic_version SET version_num='access_unknown'",'ALTER TABLE access.grants ALTER COLUMN revision SET DEFAULT 2']
        try:
            for sql in alterations:
                with e.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(sql)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('bridge_drift_accepted')
                    finally:transaction.rollback()
                assert self.snapshot(case)==before
        finally:e.dispose()
        admin=self.admin(case)
        try:
            for relation in ('grants','permissions'):
                with admin.connect() as c:
                    transaction=c.begin()
                    try:
                        trigger=c.exec_driver_sql("SELECT t.tgname FROM pg_trigger t JOIN pg_constraint k ON k.oid=t.tgconstraint WHERE t.tgrelid='access."+relation+"'::regclass AND t.tgisinternal AND k.conrelid='access.grants'::regclass AND k.confrelid='access.permissions'::regclass AND k.conname='grants_registry_permission_scope_fkey' ORDER BY t.tgname LIMIT 1").scalar_one()
                        c.exec_driver_sql('ALTER TABLE access.'+relation+' DISABLE TRIGGER "'+trigger+'"')
                        try:baseline.verify_catalog(c,'access_0011')
                        except baseline.BaselineError:pass
                        else:raise AssertionError('disabled_fk_trigger_accepted')
                    finally:transaction.rollback()
                assert self.snapshot(case)==before
        finally:admin.dispose()
        altered="CASE WHEN permission = ANY (ARRAY['pts.poetry.read','pts.poetry.export']) THEN NULL::text ELSE permission END"
        restore="CASE WHEN permission = ANY (ARRAY['pts.poetry.read','pts.poetry.export','pts.poetry.documents']) THEN NULL::text ELSE permission END"
        alter_sql='ALTER TABLE access.grants ALTER COLUMN registry_permission SET EXPRESSION AS ('+altered+')'
        restore_sql='ALTER TABLE access.grants ALTER COLUMN registry_permission SET EXPRESSION AS ('+restore+')'
        # The marker still says STORED; both verifiers must inspect the expression.
        expression_engine=self.db(case)
        try:
            with expression_engine.connect() as c:
                transaction=c.begin()
                try:
                    c.exec_driver_sql(alter_sql)
                    assert c.exec_driver_sql("SELECT attgenerated FROM pg_attribute WHERE attrelid='access.grants'::regclass AND attname='registry_permission'").scalar_one()=='s'
                    try:baseline.preflight(c)
                    except baseline.BaselineError:pass
                    else:raise AssertionError('altered_stored_expression_accepted')
                finally:transaction.rollback()
        finally:expression_engine.dispose()
        assert self.snapshot(case)==before
        self.identity_drift_refusal(case,'expression',alter_sql,restore_sql)
        self.identity_drift_refusal(case,'generated','ALTER TABLE access.grants RENAME COLUMN registry_permission TO fixture_registry_permission','ALTER TABLE access.grants RENAME COLUMN fixture_registry_permission TO registry_permission')
        self.identity_drift_refusal(case,'acl','GRANT UPDATE ON access.grants TO access_command_owner','REVOKE UPDATE ON access.grants FROM access_command_owner')
        for case in CASES:self.identity_repeat(case)
        self.record('exact-catalog-history-generated-expression-fk-trigger-acl-drift-refusal-Identity19-metadata-only10-and11')
    def migration_refusal(self,case):
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private['access_owner_urls'][case])
        code="""import sys,json
sys.path.insert(0,"""+repr(str(ACCESS/'migrations'))+""")
from alembic.config import Config
from alembic import command
import access_baseline as b
try:command.upgrade(Config("""+repr(str(ACCESS/'alembic.ini'))+"""),'head')
except Exception as error:
 result=dict(code=None,sqlstate=None,error_class='MigrationFailure')
 seen=set();pending=[error]
 while pending:
  item=pending.pop()
  if id(item) in seen:continue
  seen.add(id(item))
  if isinstance(item,b.BaselineError) and item.args in (('access_migration_busy',),('access_migration_failed_requires_reconciliation',)):result['code']=item.args[0]
  state=getattr(item,'sqlstate',None)
  if state=='55P03':result['sqlstate']=state
  for name in ('__context__','__cause__','orig'):
   nested=getattr(item,name,None)
   if isinstance(nested,BaseException):pending.append(nested)
 print(json.dumps(result))
 raise SystemExit(1) from None
raise SystemExit(2)
"""
        child=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        assert child.returncode==1 and not child.stderr,'migration_refusal_child_failed'
        selected=json.loads(child.stdout)
        expected=dict(code='access_migration_busy' if case=='failure' else 'access_migration_failed_requires_reconciliation',sqlstate=None if case=='failure' else '55P03',error_class='MigrationFailure')
        assert selected==expected,'migration_lock_reason_mismatch'
        path=self.proof/(case+'-migration-refusal.json');path.write_text(json.dumps(selected)+'\n');path.chmod(0o600)
    def failure_and_locks(self):
        for case,sql in (('locks','LOCK TABLE access.grants IN ACCESS SHARE MODE'),('failure',baseline.LOCK_SQL)):
            before=self.snapshot(case);e=self.db(case)
            try:
                with e.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(sql);started=time.monotonic();self.migration_refusal(case)
                        elapsed=time.monotonic()-started;assert elapsed<15
                        if case=='locks':assert elapsed>=2.5
                    finally:transaction.rollback()
            finally:e.dispose()
            assert self.snapshot(case)==before
        case='failure';before=self.snapshot(case)
        env=dict(PATH='/usr/bin:/bin',LANG='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private['access_owner_urls'][case])
        code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;b.verify_postcondition=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'head')"
        result=subprocess.run([sys.executable,'-I','-B','-c',code],cwd=ROOT,env=env,capture_output=True,timeout=40)
        path=self.proof/'injected-postcondition.log';path.write_bytes(result.stdout+result.stderr);path.chmod(0o600)
        assert result.returncode!=0 and b'access_test_postcondition_failure' in path.read_bytes()
        assert self.snapshot(case)==before
        for case in ('failure','locks'):self.migrate(case)
        self.record('bounded-advisory-and-relation-lock-failure-postcondition-rollback-explicit-forward-retry')
    def retained(self):
        for case in CASES:
            e=self.db(case)
            try:
                with e.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
                    assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[('access_0011',)],'retained_head_not_eleven'
            finally:e.dispose()
        self.record('separate-read-only-exact11-retained-verification')


def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all',action='store_true');group.add_argument('--verify-retained',action='store_true');args=parser.parse_args()
    raw=Path(os.environ['ACCESS_QUALIFICATION_DIR']);assert '..' not in raw.parts
    proof=Path(os.path.abspath(raw));private,run=load_fixture(proof)
    captured=source_snapshot(proof);witness=json.loads((proof/'bootstrap-source-custody.json').read_text())
    assert witness['status']=='passed' and witness['before']==witness['after']==captured
    assert set(witness['generated_inputs'])=={'credentials.json','run.json'}
    for name,digest in witness['generated_inputs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    assert witness['logs'] and all(Path(name).name==name and name.startswith('bootstrap') and name.endswith('.log') for name in witness['logs'])
    for name,digest in witness['logs'].items():assert sha256((proof/name).read_bytes()).hexdigest()==digest
    if not args.all:
        result=json.loads((proof/'results.json').read_text());assert result['status']=='passed' and result['source']==captured
        verify_qualification_logs(proof,result['logs'])
        assert sha256((proof/'retained-state.json').read_bytes()).hexdigest()==result['retained_state_sha256'],'retained_state_custody_mismatch'
    q=Qualification(proof,private)
    if args.all:
        (proof/'all-started').open('x').close()
        for method in (q.prepare_cases,q.functional,q.upgrade,q.privileges,q.drift,q.failure_and_locks,q.retained):method()
        (proof/'retained-state.json').write_text(json.dumps({case:q.snapshot(case) for case in CASES},indent=2)+'\n')
    else:
        assert json.loads((proof/'retained-state.json').read_text())=={case:q.snapshot(case) for case in CASES}
        q.retained()
    assert captured==source_snapshot(proof),'qualification_source_changed'
    path=proof/('results.json' if args.all else 'retained-results.json')
    path.write_text(json.dumps(dict(status='passed',steps=q.results,source=captured,logs=qualification_logs(proof),retained_state_sha256=sha256((proof/'retained-state.json').read_bytes()).hexdigest()),indent=2)+'\n')
    print(json.dumps(dict(ok=True,steps=q.results)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        storage.report_failure(error)
        raise SystemExit(1) from None
