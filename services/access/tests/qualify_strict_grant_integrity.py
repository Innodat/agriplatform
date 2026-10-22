"""Single-use synthetic Access12 proof; no effective access or PtS cutover."""
if not __debug__:
    raise RuntimeError('access_qualification_optimized_python_prohibited')
import argparse
from hashlib import sha256
import json,os,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_grant_registry_bridge as bridge
from sqlalchemy import text
ROOT,ACCESS,ACTOR=bridge.ROOT,bridge.ACCESS,bridge.ACTOR
base,storage,lifecycle,configure=bridge.base,bridge.storage,bridge.lifecycle,bridge.configure
baseline=bridge.baseline
CASES=frozenset(('clean','upgrade','refusal','drift','failure','locks'))
base.CASES=CASES
load_fixture=bridge.load_fixture
bridge_source_snapshot=bridge.source_snapshot
ORG1,ORG2=bridge.ORG1,bridge.ORG2
INSERT=bridge.INSERT
FK='grants_permission_scope_fkey'
CHECK='grants_active_fields'
SECOND_PERMISSION='synthetic.organization.second'
values=bridge.values
permission_document=bridge.permission_document
canonical_trigger_rows=bridge.canonical_trigger_rows
def qualification_logs(proof):
    patterns=[re.escape(case)+r'-(?:(?:head|access_[0-9]{4})-[0-9]+|identity19-repeat)\.log' for case in CASES]
    patterns += [r'identity-drift-[a-z]+\.json',r'injected-postcondition\.log',r'(?:locks|failure)-migration-refusal\.json',r'refusal-fixture-transitions\.json']
    return {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(proof.iterdir()) if any(re.fullmatch(pattern,p.name) for pattern in patterns)}


def verify_qualification_logs(proof,expected):
    assert type(expected) is dict and expected,'qualification_logs_missing'
    assert qualification_logs(proof)==expected,'qualification_log_custody_mismatch'


def source_snapshot(proof):
    return bridge_source_snapshot(proof)|{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__).with_name('test_strict_grant_integrity.py'),ACCESS/'STRICT-GRANT-INTEGRITY.md')}


class Qualification(bridge.Qualification):
    migrate=storage.Qualification.migrate
    def prepare_cases(self):
        for case in CASES:
            self.migrate(case,'access_0011' if case in ('upgrade','refusal','failure','locks') else 'head')
            self.seed(case)
            self.execute_sql(case,f"INSERT INTO identity.org(id,name,slug) VALUES('{ORG1}','Synthetic organization','synthetic-strict')",'owner_urls')
        self.record('clean12-exact11-six-private-cases-Identity19-service-actor')
    def owner_insert(self,case,parameters=None,context=ORG1):
        supplied=parameters or {}
        self.explicit_insert(case,values()|supplied|dict(org=context,permission='kdg_capture.read.own'))
    def functional(self):
        case='clean';self.command(case,base.document())
        self.command(case,permission_document())
        self.command(case,permission_document(SECOND_PERMISSION))
        self.command(case,permission_document('account.only','account'))
        for org in (ORG1,ORG2):self.explicit_insert(case,values()|dict(org=org))
        prefix=f"SET LOCAL app.actor_id='legacy';INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at) VALUES('{ORG1}','rollback-first','{ORG2}','kdg_capture.read.own',7,'{ACTOR}','{ACTOR}','2002-01-01Z');"
        for permission in ('unknown.permission','account.only',*lifecycle.PERMISSIONS):
            for revoked in (None,'2001-01-01Z'):
                self.refused(case,INSERT,'23503',values(permission)|dict(revoked_at=revoked),constraint=FK,prefix=prefix)
                target=values();self.explicit_insert(case,target)
                self.refused(case,'UPDATE access.grants SET permission=:permission,revoked_at=:revoked WHERE id=:id','23503',dict(permission=permission,revoked=revoked,id=target['id']),constraint=FK,prefix=prefix)
        for field in ('membership_id','created_actor_id','updated_actor_id','updated_at'):
            for permission in ('kdg_capture.read.own',*lifecycle.PERMISSIONS):
                self.refused(case,INSERT,'23514',values(permission)|{field:None},constraint=CHECK,prefix=prefix)
            revoked=values()|{field:None,'revoked_at':'2001-01-01Z'}
            self.explicit_insert(case,revoked)
            row=next(row for row in self.snapshot(case)['grants'] if row[1]==revoked['id'])
            assert len(row)==13 and row[6:]==[revoked['membership_id'],'organization',1,'2001-01-01 00:00:00+00:00',revoked['created_actor_id'],revoked['updated_actor_id'],None if field=='updated_at' else '2002-01-01 00:00:00+00:00']
            self.refused(case,'UPDATE access.grants SET revoked_at=NULL WHERE id=:id','23514',dict(id=revoked['id']),constraint=CHECK,prefix=prefix)
            active=values();self.explicit_insert(case,active)
            self.refused(case,'UPDATE access.grants SET '+field+'=NULL WHERE id=:id','23514',dict(id=active['id']),constraint=CHECK,prefix=prefix)
        transition=values();self.explicit_insert(case,transition)
        before_row=next(row for row in self.snapshot(case)['grants'] if row[1]==transition['id'])
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET permission='{SECOND_PERMISSION}' WHERE id='{transition['id']}'")
        after_row=next(row for row in self.snapshot(case)['grants'] if row[1]==transition['id'])
        assert after_row==before_row[:3]+[SECOND_PERMISSION]+before_row[4:]
        revival=values()|dict(revoked_at='2001-01-01Z');self.explicit_insert(case,revival)
        before_row=next(row for row in self.snapshot(case)['grants'] if row[1]==revival['id'])
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET revoked_at=NULL WHERE id='{revival['id']}'")
        after_row=next(row for row in self.snapshot(case)['grants'] if row[1]==revival['id'])
        assert after_row==before_row[:9]+[None]+before_row[10:]
        for field,index in (('membership_id',6),('created_actor_id',10),('updated_actor_id',11),('updated_at',12)):
            revoked=values()|dict(revoked_at='2001-01-01Z');self.explicit_insert(case,revoked)
            before_row=next(row for row in self.snapshot(case)['grants'] if row[1]==revoked['id'])
            self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET {field}=NULL WHERE id='{revoked['id']}'")
            after_row=next(row for row in self.snapshot(case)['grants'] if row[1]==revoked['id'])
            assert after_row==before_row[:index]+[None]+before_row[index+1:]
        self.record('registered-org-permission-update-preserves-other-values-complete-revival-and-each-revoked-provenance-removal')
        partial=values(complete=False)|dict(revoked_at='2001-01-01Z');self.explicit_insert(case,partial)
        for field,value,constraint in [('membership_id',0,'grants_membership_id_positive'),('revision',0,'grants_revision_positive'),('created_actor_id',storage.NIL,'grants_created_actor_id_non_nil'),('updated_actor_id',storage.NIL,'grants_updated_actor_id_non_nil'),('updated_at','infinity','grants_updated_at_finite'),('revoked_at','-infinity','grants_revoked_at_finite')]:
            self.refused(case,INSERT,'23514',values()|{field:value},constraint=constraint,prefix=prefix)
        self.refused(case,INSERT,'23514',values()|dict(scope_kind='account'),constraint='grants_scope_kind_organization',prefix=prefix)
        cte="""WITH first_write AS (
          INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at)
          VALUES(CAST(:org AS uuid),:id,CAST(:user AS uuid),'kdg_capture.read.own',7,CAST(:actor AS uuid),CAST(:actor AS uuid),'2002-01-01Z') RETURNING org_id,user_id)
          INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at)
          SELECT org_id,:bad_id,user_id,'unknown.permission',7,CAST(:actor AS uuid),CAST(:actor AS uuid),'2002-01-01Z' FROM first_write"""
        self.refused(case,cte,'23503',values()|dict(actor=ACTOR,bad_id='dependent-unknown'),constraint=FK,prefix=prefix)
        multi=f"INSERT INTO access.grants(org_id,id,user_id,permission,membership_id,created_actor_id,updated_actor_id,updated_at) VALUES('{ORG1}','multi-good','{ORG2}','kdg_capture.read.own',7,'{ACTOR}','{ACTOR}','2002-01-01Z'),('{ORG1}','multi-bad','{ORG2}','unknown.permission',7,'{ACTOR}','{ACTOR}','2002-01-01Z')"
        self.refused(case,multi,'23503',constraint=FK,prefix="SET LOCAL app.actor_id='legacy'")
        before=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==before
        self.record('direct-named-fk-all-three-PtS-unknown-account-insert-update-active-revoked-global-fields-revival-structural-checks-dependent-multirow-full-rollback')
    def upgrade(self):
        case='upgrade';p=permission_document();entry=base.document();entry['command']='entry_permission.register';entry['payload']['permission']='kdg_capture.read.own'
        enabled=base.document();enabled['command']='application.set_enabled';enabled['payload']=dict(app_id='synthetic_app',enabled=True,expected_revision='1')
        docs=[base.document(),p,entry,enabled,configure.document()]
        receipts=[self.command(case,v) for v in docs]
        self.command(case,permission_document(SECOND_PERMISSION))
        for org in (ORG1,ORG2):
            for permission in ('kdg_capture.read.own',SECOND_PERMISSION):
                self.explicit_insert(case,values(permission)|dict(org=org))
                self.explicit_insert(case,values(permission,complete=False)|dict(org=org,revoked_at='2001-01-01Z',revision=9223372036854775807))
        for org in (ORG1,ORG2):
            self.execute_sql(case,f"SET LOCAL app.org_id='{org}'; UPDATE access.grants SET created_at='1990-01-01Z',created_by='opaque historical creator'")
        before=self.snapshot(case);self.identity_repeat(case);self.migrate(case);after=self.snapshot(case)
        assert after['alembic_version']==[['access_0012']]
        assert after['grants']==[row[:-1] for row in before['grants']]
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
        state=self.snapshot(case);self.migrate(case);assert self.snapshot(case)==state
        self.record('compatible-populated11-upgrade12-original-columns-values-opaque-ids-partial-history-five-receipts-replay-lookup-repeat')
    def refusal(self):
        case='refusal';self.command(case,base.document())
        for permission in lifecycle.PERMISSIONS:
            for revoked in (None,'2001-01-01Z'):
                self.explicit_insert(case,values(permission,complete=False)|dict(revoked_at=revoked))
                before=self.snapshot(case);self.migrate(case,success=False)
                assert self.snapshot(case)==before and before['alembic_version']==[['access_0011']]
        self.identity_repeat(case)
        self.record('incompatible-populated11-aggregate-three-unregistered-PtS-active-revoked-controlled-refusal-retains-exact-data-catalog-history')
        transitions=[dict(stage='aggregate-unregistered-refusal-preserved',snapshot=self.snapshot(case))]
        # Preserve the aggregate evidence above, then deliberately make this owned
        # fixture registry-compatible. These are synthetic test transitions only.
        for permission in lifecycle.PERMISSIONS:self.command(case,permission_document(permission))
        self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET revoked_at='2001-01-01Z'")
        self.record('deliberate-owned-fixture-transition-explicitly-register-three-synthetic-PtS-permissions-and-revoke-retained-rows-for-isolated-CHECK-probes')
        transitions.append(dict(stage='explicit-synthetic-registration-and-revocation',snapshot=self.snapshot(case)))
        target=self.snapshot(case)['grants'][0][1]
        for field,index in (('membership_id',6),('created_actor_id',10),('updated_actor_id',11),('updated_at',12)):
            self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET revoked_at=NULL,membership_id=7,created_actor_id='{ACTOR}',updated_actor_id='{ACTOR}',updated_at='2002-01-01Z' WHERE id='{target}'; UPDATE access.grants SET {field}=NULL WHERE id='{target}'")
            before=self.snapshot(case)
            assert before['alembic_version']==[['access_0011']]
            registered={row[0] for row in before['permissions'] if row[2]=='organization'}
            assert all(row[3] in registered for row in before['grants'])
            active=[row for row in before['grants'] if row[9] is None]
            assert len(active)==1 and active[0][1]==target
            assert [i for i in (6,10,11,12) if active[0][i] is None]==[index]
            self.migrate(case,success=False)
            after=self.snapshot(case);assert after==before
            transitions.append(dict(stage='isolated-missing-'+field,before=before,after=after))
            self.record('isolated-populated11-registered-legacy-active-missing-'+field+'-controlled-upgrade-refusal-exact-snapshot-preserved')
            self.execute_sql(case,f"SET LOCAL app.org_id='{ORG1}'; UPDATE access.grants SET revoked_at='2001-01-01Z',membership_id=NULL,created_actor_id=NULL,updated_actor_id=NULL,updated_at=NULL WHERE id='{target}'")
        transitions.append(dict(stage='restored-revoked-unknown-provenance',snapshot=self.snapshot(case)))
        path=self.proof/'refusal-fixture-transitions.json'
        path.write_text(json.dumps(transitions,indent=2)+'\n');path.chmod(0o600)
        self.record('deliberate-owned-fixture-transition-restores-revoked-unknown-provenance-after-each-isolated-CHECK-probe')

    def drift(self):
        case='drift';before=self.snapshot(case);e=self.db(case)
        alterations=['ALTER TABLE access.grants DROP CONSTRAINT '+CHECK,'ALTER TABLE access.grants DROP CONSTRAINT '+FK,'ALTER TABLE access.grants NO FORCE ROW LEVEL SECURITY','GRANT UPDATE ON access.grants TO access_command_owner',"UPDATE access.alembic_version SET version_num='access_unknown'",'ALTER TABLE access.grants ALTER COLUMN revision SET DEFAULT 2','ALTER TABLE access.grants ADD COLUMN unexpected text','ALTER TABLE access.grants ADD COLUMN unexpected text; ALTER TABLE access.grants DROP COLUMN unexpected']
        try:
            for sql in alterations:
                with e.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql(sql)
                        try:baseline.preflight(c)
                        except baseline.BaselineError:pass
                        else:raise AssertionError('strict_drift_accepted')
                    finally:transaction.rollback()
                assert self.snapshot(case)==before
        finally:e.dispose()
        admin=self.admin(case)
        try:
            with admin.connect() as c:
                inventory=[tuple(row) for row in c.exec_driver_sql("SELECT c.relname,t.tgname,p.proname,t.tgenabled FROM pg_trigger t JOIN pg_constraint k ON k.oid=t.tgconstraint JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid WHERE t.tgisinternal AND k.conrelid='access.grants'::regclass AND k.confrelid='access.permissions'::regclass AND k.conname='"+FK+"' ORDER BY c.relname,p.proname")]
            assert [(rel,function,enabled) for rel,trigger,function,enabled in inventory]==[
                ('grants','RI_FKey_check_ins','O'),('grants','RI_FKey_check_upd','O'),
                ('permissions','RI_FKey_noaction_upd','O'),('permissions','RI_FKey_restrict_del','O')]
            for relation,trigger,function,enabled in inventory:
                with admin.connect() as c:
                    transaction=c.begin()
                    try:
                        c.exec_driver_sql('ALTER TABLE access.'+relation+' DISABLE TRIGGER "'+trigger+'"')
                        try:baseline.verify_catalog(c,'access_0012')
                        except baseline.BaselineError:pass
                        else:raise AssertionError('disabled_fk_trigger_accepted')
                    finally:transaction.rollback()
                assert self.snapshot(case)==before
            # Read-only metadata verifier must reject even a forged tombstone.
            with admin.connect() as c:
                transaction=c.begin()
                try:
                    c.exec_driver_sql("UPDATE pg_attribute SET attname='unexpected_dropped_slot' WHERE attrelid='access.grants'::regclass AND attnum=14")
                    try:baseline.verify_catalog(c,'access_0012')
                    except baseline.BaselineError:pass
                    else:raise AssertionError('tombstone_drift_accepted')
                finally:transaction.rollback()
            assert self.snapshot(case)==before
        finally:admin.dispose()
        self.identity_drift_refusal(case,'direct',f'ALTER TABLE access.grants RENAME CONSTRAINT {FK} TO fixture_direct_fk',f'ALTER TABLE access.grants RENAME CONSTRAINT fixture_direct_fk TO {FK}')
        self.identity_drift_refusal(case,'acl','GRANT UPDATE ON access.grants TO access_command_owner','REVOKE UPDATE ON access.grants FROM access_command_owner')
        for case in CASES:self.identity_repeat(case)
        self.record('exact-catalog-history-ACL-extra-dropped-slot-forged-tombstone-both-FK-ends-Identity19-metadata11-and12-refusal')
    def retained(self):
        for case in CASES:
            e=self.db(case)
            try:
                with e.begin() as c:
                    c.exec_driver_sql('SET TRANSACTION READ ONLY');baseline.preflight(c);baseline.verify_postcondition(c)
                    expected='access_0011' if case=='refusal' else 'access_0012'
                    assert c.exec_driver_sql('SELECT version_num FROM access.alembic_version').all()==[(expected,)],'retained_revision_mismatch'
            finally:e.dispose()
        self.record('separate-read-only-exact12-and-intentional-refused11-retained-verification')


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
        for method in (q.prepare_cases,q.functional,q.upgrade,q.refusal,q.privileges,q.drift,q.failure_and_locks,q.retained):method()
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
