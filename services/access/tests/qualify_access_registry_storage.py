"""Actual synthetic Access staging matrix on fresh privately prepared native cases.

ACCESS_QUALIFICATION_DIR selects a private fixture using the existing Identity native
framework. Bootstrap is explicit separate preparation, never discovered or executed.
--all is single-use; --verify-retained performs only repeatable read-only inspection.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from qualify_access_membership_binding import (
    ROOT, ACCESS, baseline, fixture, text, require_database_error,
)
import qualify_access_membership_binding as membership

def verify_preparation(proof):
    witness = json.loads((proof/'bootstrap-source-custody.json').read_text())
    current = {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(proof)}
    assert witness['status']=='passed' and witness['before']==witness['after']==current, 'bootstrap execution custody required'
    assert witness['steps']==['bootstrap.py','bootstrap_identity18.py']
    assert set(witness['logs'])=={'bootstrap.log','bootstrap_identity18.log'}
    for name,digest in witness['logs'].items():
        assert sha256((proof/name).read_bytes()).hexdigest()==digest

class Qualification(membership.Qualification):
    def __init__(self,proof,private):
        self.proof,self.private=proof,private
        result=proof/'access-registry-results.json'
        self.records=json.loads(result.read_text())['steps'] if result.exists() else []

    def snapshot(self,case):
        db=self.db(case,'databases')
        try:
            with db.begin() as c:
                c.exec_driver_sql('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
                c.exec_driver_sql("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'; SET LOCAL idle_in_transaction_session_timeout='10s'")
                if c.dialect.server_version_info >= (17,):
                    c.exec_driver_sql("SET LOCAL transaction_timeout='30s'")
                result={}
                for key,query in {
                    'relations':"SELECT c.relname,c.relkind,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,c.relacl::text,c.reloptions::text,c.relpersistence FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname",
                    'inheritance':"SELECT cn.nspname,child.relname,pn.nspname,parent.relname,i.inhseqno FROM pg_inherits i JOIN pg_class child ON child.oid=i.inhrelid JOIN pg_namespace cn ON cn.oid=child.relnamespace JOIN pg_class parent ON parent.oid=i.inhparent JOIN pg_namespace pn ON pn.oid=parent.relnamespace WHERE cn.nspname='access' OR pn.nspname='access' ORDER BY 1,2,3,4,5",
                    'columns':"SELECT c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid),a.attacl::text FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE n.nspname='access' AND a.attnum>0 ORDER BY c.relname,a.attnum",
                    'constraints':"SELECT c.relname,k.conname,pg_get_constraintdef(k.oid),k.convalidated,k.condeferrable FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,k.conname",
                    'policies':"SELECT tablename,policyname,permissive,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname='access' ORDER BY tablename,policyname",
                    'indexes':"SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='access' ORDER BY tablename,indexname",
                    'triggers':"SELECT c.relname,t.tgname,t.tgenabled,t.tgisinternal,t.tgtype,(SELECT conname FROM pg_constraint WHERE oid=t.tgconstraint),pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,t.tgname",
                    'routines':"SELECT p.proname,pg_get_functiondef(p.oid),p.proacl::text,pg_get_userbyid(p.proowner) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='access' ORDER BY 1",
                    'schema':"SELECT pg_get_userbyid(nspowner),nspacl::text FROM pg_namespace WHERE nspname='access'",
                    'defaults':"SELECT pg_get_userbyid(d.defaclrole),coalesce(n.nspname,''),d.defaclobjtype,d.defaclacl::text FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='access' OR d.defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator') ORDER BY 1,2,3",
                }.items(): result[key]=[list(r) for r in c.exec_driver_sql(query)]
                for name in ('grants','alembic_version','applications','permissions','entry_permissions'):
                    if c.execute(text("SELECT to_regclass(:name)"),{'name':'access.'+name}).scalar_one():
                        result[name]=[list(r) for r in c.exec_driver_sql('SELECT * FROM access.'+name+' ORDER BY 1,2' if name!='alembic_version' else 'SELECT * FROM access.alembic_version ORDER BY 1')]
                return json.loads(json.dumps(result,default=str))
        finally:db.dispose()

    def persist(self):
        (self.proof/'access-registry-results.json').write_text(json.dumps({'steps':self.records},indent=2)+'\n')

    def clean_previous(self):
        db=self.db('clean')
        try:
            with db.begin() as c:
                assert baseline.preflight(c) is None, 'clean case must be exactly empty before upgrade'
        finally:db.dispose()
        self.command('clean-upgrade', 'clean')
        self.initial('previous',True);before=self.snapshot('previous')['grants']
        self.command('populated-upgrade','previous');after=self.snapshot('previous')['grants']
        assert [r[:-1] for r in after]==before and all(r[-1] is None for r in after)
        original=self.snapshot('previous');self.command('populated-repeat','previous');assert self.snapshot('previous')==original
        self.initial('exact2',True);self.command('exact2-stage','exact2',action=('upgrade','access_0002'))
        self.execute('exact2',"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; UPDATE access.grants SET membership_id=42")
        old=self.snapshot('exact2')['grants'];self.command('exact2-upgrade','exact2');assert self.snapshot('exact2')['grants']==old
        for case in ('clean','previous','exact2'):
            snap=self.snapshot(case);assert all(not snap[name] for name in baseline.REGISTRY_TABLES)
        self.record('exact1-exact2-grants-preserved-empty-registry')

    def boundaries(self):
        self.initial('boundary',True);self.command('boundary-upgrade','boundary')
        context="SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; "
        for value in ('NULL','1','9223372036854775807'):
            self.execute('boundary',context+'UPDATE access.grants SET membership_id='+value)
        membership_before=self.snapshot('boundary')
        for value in ('0','-1','-9223372036854775808','9223372036854775808'):
            overflow=value=='9223372036854775808'
            require_database_error(lambda:self.execute('boundary',context+'UPDATE access.grants SET membership_id='+value),
                                   '22003' if overflow else '23514',None if overflow else 'grants_membership_id_positive')
            assert self.snapshot('boundary')==membership_before
        self.record('nullable-positive-bigint-boundaries-preserved')
        actor="'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'";now="'2026-10-21T12:00:00Z'"
        self.execute('boundary',f"INSERT INTO access.applications(app_id,created_by,updated_by,created_at,updated_at) VALUES ('test_app',{actor},{actor},{now},{now}),('other_app',{actor},{actor},{now},{now})")
        self.execute('boundary',f"INSERT INTO access.permissions VALUES ('literal.*','test_app','account',{actor},{now}),('literal.organization','test_app','organization',{actor},{now})")
        self.execute('boundary',f"INSERT INTO access.entry_permissions VALUES ('test_app','literal.*',{actor},{now})")
        before=self.snapshot('boundary')
        assert all(row[1:3]==[False,1] for row in before['applications'])
        def reject(sql,state,constraint=None):
            require_database_error(lambda:self.execute('boundary',sql),state,constraint)
            assert self.snapshot('boundary')==before
        for bad in ("''","'a'","'A_bad'","'bad-app'","'éé'","repeat('a',65)"):
            reject(f"INSERT INTO access.applications VALUES ({bad},false,1,{actor},{actor},{now},{now})",'23514','applications_app_id_valid')
        for bad in ("''","repeat('a',201)","'é'"):
            reject(f"INSERT INTO access.permissions VALUES ({bad},'test_app','account',{actor},{now})",'23514','permissions_permission_valid')
        reject(f"INSERT INTO access.permissions VALUES ('new','test_app','wrong',{actor},{now})",'23514','permissions_scope_kind_valid')
        reject(f"INSERT INTO access.permissions VALUES ('new','missing_app','account',{actor},{now})",'23503','permissions_app_id_fkey')
        reject(f"INSERT INTO access.permissions VALUES ('literal.*','other_app','organization',{actor},{now})",'23505','permissions_pkey')
        reject(f"INSERT INTO access.entry_permissions VALUES ('other_app','literal.*',{actor},{now})",'23503','entry_permissions_app_id_permission_fkey')
        reject(f"INSERT INTO access.entry_permissions VALUES ('test_app','missing',{actor},{now})",'23503','entry_permissions_app_id_permission_fkey')
        reject(f"INSERT INTO access.entry_permissions VALUES ('test_app','literal.*',{actor},{now})",'23505','entry_permissions_pkey')
        reject(f"INSERT INTO access.applications VALUES ('test_app',false,1,{actor},{actor},{now},{now})",'23505','applications_pkey')
        nil="'00000000-0000-0000-0000-000000000000'"
        for table in baseline.REGISTRY_TABLES:
            valid=dict(app_id="'new_app'",enabled='false',revision='1',created_by=actor,updated_by=actor,created_at=now,updated_at=now,permission="'literal.organization'",scope_kind="'account'")
            cols={'applications':['app_id','enabled','revision','created_by','updated_by','created_at','updated_at'],'permissions':['permission','app_id','scope_kind','created_by','created_at'],'entry_permissions':['app_id','permission','created_by','created_at']}[table]
            if table!='applications':valid['app_id']="'test_app'"
            if table=='permissions':valid['permission']="'new_permission'"
            for col in [c for c in cols if c.endswith('_by') or c.endswith('_at') or c=='revision']:
                for bad in (['0','-1'] if col=='revision' else [nil] if col.endswith('_by') else ["'infinity'","'-infinity'"]):
                    values=dict(valid);values[col]=bad
                    suffix='positive' if col=='revision' else 'non_nil' if col.endswith('_by') else 'finite'
                    reject('INSERT INTO access.'+table+'('+','.join(cols)+') VALUES ('+','.join(values[c] for c in cols)+')','23514',table+'_'+col+'_'+suffix)
                values=dict(valid);values[col]='NULL'
                reject('INSERT INTO access.'+table+'('+','.join(cols)+') VALUES ('+','.join(values[c] for c in cols)+')','23502')
        # Literal ASCII controls, DEL and both length endpoints are accepted, with no prefix rule.
        self.execute('boundary',f"INSERT INTO access.permissions VALUES (chr(1)||chr(127),'test_app','account',{actor},{now}),(repeat('x',200),'test_app','organization',{actor},{now}),('x','test_app','account',{actor},{now})")
        self.execute('boundary',f"INSERT INTO access.applications VALUES ('a1',false,9223372036854775807,{actor},{actor},{now},{now}),(repeat('a',64),false,1,{actor},{actor},{now},{now})")
        before=self.snapshot('boundary')
        reject(f"INSERT INTO access.applications VALUES ('overflow',false,9223372036854775808,{actor},{actor},{now},{now})",'22003')
        for table,key in [('applications','app_id'),('permissions','permission'),('entry_permissions','permission')]:
            for statement in ('UPDATE access.'+table+' SET '+key+'='+key,'UPDATE access.'+table+' SET '+key+'='+key+' WHERE false','DELETE FROM access.'+table,'DELETE FROM access.'+table+' WHERE false','TRUNCATE access.'+table+' CASCADE'):
                reject(statement,'55000')
            reject(f"INSERT INTO access.applications VALUES ('atomic_app',false,1,{actor},{actor},{now},{now}); UPDATE access."+table+' SET '+key+'='+key,'55000')
        for table,key in [('applications','app_id'),('permissions','app_id'),('entry_permissions','app_id')]:
            reject('UPDATE access.'+table+" SET "+key+"='changed_app'",'55000')
            reject('UPDATE access.'+table+' SET created_at=created_at+interval \'1 second\'','55000')
        reject(f"WITH inserted AS (INSERT INTO access.applications VALUES ('cte_app',false,1,{actor},{actor},{now},{now}) RETURNING app_id) UPDATE access.applications SET enabled=true WHERE app_id IN (SELECT app_id FROM inserted)",'55000')
        for table,cols,key,existing,new in [
            ('applications',['app_id','enabled','revision','created_by','updated_by','created_at','updated_at'],['app_id'],
             f"('test_app',false,1,{actor},{actor},{now},{now})",f"('upsert_app',false,1,{actor},{actor},{now},{now})"),
            ('permissions',['permission','app_id','scope_kind','created_by','created_at'],['permission'],
             f"('literal.*','test_app','account',{actor},{now})",f"('upsert_permission','test_app','account',{actor},{now})"),
            ('entry_permissions',['app_id','permission','created_by','created_at'],['app_id','permission'],
             f"('test_app','literal.*',{actor},{now})",f"('test_app','literal.organization',{actor},{now})"),
        ]:
            for values in (existing,existing+','+new):
                for change in ('',"+interval '1 second'"):
                    reject('INSERT INTO access.'+table+' VALUES '+values+' ON CONFLICT ('+','.join(key)+') DO UPDATE SET created_at=EXCLUDED.created_at'+change,'55000')
                    typed_values=values.replace(actor,actor+'::uuid').replace(now,now+'::timestamptz')
                    condition=' AND '.join('target.'+col+'=incoming.'+col for col in key)
                    reject('MERGE INTO access.'+table+' AS target USING (VALUES '+typed_values+') AS incoming('+','.join(cols)+') ON '+condition+' WHEN MATCHED THEN UPDATE SET created_at=target.created_at'+change+' WHEN NOT MATCHED THEN INSERT ('+','.join(cols)+') VALUES ('+','.join('incoming.'+col for col in cols)+')','55000')
        for table in ('applications','permissions'):
            reject('TRUNCATE access.'+table,'0A000')
        reject('TRUNCATE access.applications,access.permissions,access.entry_permissions','55000')
        reject(f"INSERT INTO access.applications VALUES ('multirow_app',false,1,{actor},{actor},{now},{now}),('invalid-app',false,1,{actor},{actor},{now},{now})",'23514','applications_app_id_valid')
        self.command('populated-registry-repeat','boundary');assert self.snapshot('boundary')==before
        self.record('registry-boundaries-attribution-literal-ascii-relationships-and-immutable-rollback')

    def registry_refusals(self):
        for case,sql in [
            ('registry_object','CREATE TABLE access.unexpected(id integer)'),
            ('registry_constraint','ALTER TABLE access.permissions DROP CONSTRAINT permissions_app_id_permission_key CASCADE'),
            ('registry_function',"CREATE OR REPLACE FUNCTION access.registry_storage_immutable() RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $$ BEGIN RETURN NULL; END $$"),
            ('registry_security','ALTER FUNCTION access.registry_storage_immutable() SECURITY DEFINER'),
            ('registry_search_path','ALTER FUNCTION access.registry_storage_immutable() RESET search_path'),
            ('registry_trigger','ALTER TABLE access.permissions DISABLE TRIGGER registry_storage_immutable'),
            ('registry_default','ALTER TABLE access.applications ALTER COLUMN enabled SET DEFAULT true'),
            ('registry_acl','GRANT SELECT ON access.permissions TO access_runtime'),
        ]:
            self.command(case+'-upgrade',case);self.execute(case,sql)
            self.assert_refused(case+'-refusal',case,'access_catalog_mismatch')

        case='registry_fk_trigger'
        self.command(case+'-upgrade',case)
        # Only the isolated synthetic true-admin fixture can disable system FK triggers.
        import psycopg
        from psycopg import sql
        with psycopg.connect(self.private['databases'][case],user='supabase_admin',connect_timeout=5) as c:
            c.execute("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'")
            assert c.execute("SELECT current_user,rolsuper FROM pg_roles WHERE rolname=current_user").fetchone()==('supabase_admin',True)
            trigger=c.execute("SELECT tgname FROM pg_trigger WHERE tgrelid='access.entry_permissions'::regclass AND tgisinternal ORDER BY tgname LIMIT 1").fetchone()[0]
            c.execute(sql.SQL('ALTER TABLE access.entry_permissions DISABLE TRIGGER {}').format(sql.Identifier(trigger)))
        self.assert_refused(case+'-refusal',case,'access_catalog_mismatch')
        self.assert_refused('sql-ascii-refusal','sql_ascii','access_utf8_encoding_required')

    def permissions(self):
        before=self.snapshot('boundary')
        context="SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='legacy:System/not-a-uuid'; SET LOCAL app.account_id='22222222-2222-4222-8222-222222222222'; "
        for statement in [*[sql for table in baseline.REGISTRY_TABLES for sql in ('SELECT * FROM access.'+table,'INSERT INTO access.'+table+' DEFAULT VALUES','UPDATE access.'+table+' SET created_at=created_at','DELETE FROM access.'+table,'TRUNCATE access.'+table,'ALTER TABLE access.'+table+' ADD COLUMN forbidden text')],'SELECT access.registry_storage_immutable()',"INSERT INTO access.grants(org_id,id,user_id,permission) VALUES ('11111111-1111-4111-8111-111111111111','forbidden','33333333-3333-4333-8333-333333333333','pts.poetry.read')",'UPDATE access.grants SET membership_id=1','DELETE FROM access.grants','SET ROLE access_migrator','ALTER TABLE access.grants ADD COLUMN forbidden text','SELECT * FROM access.alembic_version']:
            require_database_error(lambda:self.execute('boundary',context+statement,role='runtime_urls'),'42501')
        assert self.snapshot('boundary')==before
        db=self.db('boundary','runtime_urls')
        try:
            with db.begin() as c:
                assert c.exec_driver_sql('SELECT * FROM access.grants').all()==[]
                c.exec_driver_sql("SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'")
                assert c.exec_driver_sql('SELECT membership_id FROM access.grants').scalar_one()==9223372036854775807
        finally:db.dispose()
        for role in ('anon','authenticated','service_role'):
            for table in baseline.REGISTRY_TABLES:
                for statement in ('SELECT * FROM access.'+table,'INSERT INTO access.'+table+' DEFAULT VALUES','UPDATE access.'+table+' SET created_at=created_at','DELETE FROM access.'+table,'TRUNCATE access.'+table):
                    require_database_error(lambda:self.execute('boundary','SET LOCAL ROLE '+role+'; '+statement,role='databases'),'42501')
            for statement in ('SELECT access.registry_storage_immutable()','CREATE TABLE access.forbidden(id integer)'):
                require_database_error(lambda:self.execute('boundary','SET LOCAL ROLE '+role+'; '+statement,role='databases'),'42501')
        db=self.db('boundary','databases')
        try:
            with db.begin() as c:
                for role in ('anon','authenticated','service_role'):
                    assert not c.execute(text("SELECT pg_has_role(:role,'access_migrator','MEMBER')"),{'role':role}).scalar_one()
                    assert not c.execute(text("SELECT has_function_privilege(:role,'access.registry_storage_immutable()','EXECUTE')"),{'role':role}).scalar_one()
        finally:db.dispose()
        assert self.snapshot('boundary')==before
        self.record('actual-runtime-browser-read-write-ddl-execute-and-owner-assumption-denied')

    def retained(self, require_aggregate=True):
        if require_aggregate:
            records=json.loads((self.proof/'access-registry-results.json').read_text())['steps']
            completed=[r for r in records if r['label']=='executed-source-custody' and r.get('invocation')==['--all']]
            assert completed,'completed aggregate source witness required'
            recorded=json.loads((self.proof/completed[-1]['witness']).read_text())
            current={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(self.proof)}
            assert recorded['status']=='passed' and recorded['before']==recorded['after']==current
            for receipt in records:
                if 'log_sha256' in receipt:
                    assert sha256((self.proof/(receipt['label']+'.log')).read_bytes()).hexdigest()==receipt['log_sha256']
            expected=json.loads((self.proof/'access-registry-retained-state.json').read_text())
            require_retained_inventory(expected,self.private)
            assert expected=={case:self.snapshot(case) for case in retained_cases(self.private)}
        for case in ('clean','previous','exact2','boundary','failure','concurrent','lock','integration'):
            db=self.db(case)
            try:
                with db.begin() as c:baseline.preflight(c);baseline.verify_postcondition(c)
            finally:db.dispose()
        self.record('retained-exact-head-inspection')

def source_paths(proof):
    return sorted(set([*membership.source_paths(proof),Path(__file__)]))

def retained_cases(private):
    return set(private['databases']) - {'native','red'}


def require_retained_inventory(saved,private):
    assert isinstance(saved,dict) and set(saved)==retained_cases(private), 'retained_case_inventory_mismatch'


def source_snapshot(proof):
    return {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(proof)}


def verify_source_completion(proof,captured):
    assert source_snapshot(proof)==captured, 'qualification_source_changed'


def main():
    if not __debug__:
        raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    for flag in ('all','verify-retained','clean-previous','boundaries','refusals','registry-refusals','recovery','permissions','integration'):group.add_argument('--'+flag,action='store_true')
    args=parser.parse_args();proof,private=fixture();verify_preparation(proof);q=Qualification(proof,private)
    captured=source_snapshot(proof)
    witness=proof/('access-registry-source-'+str(time.time_ns())+'.json');witness.write_text(json.dumps(dict(before=captured,status='started'),indent=2)+'\n')
    if args.all:
        marker=proof/'access-registry-all-started';marker.open('x').close()
        for method in (q.clean_previous,q.boundaries,q.refusals,q.registry_refusals,q.recovery,q.permissions,q.integration):method()
        q.retained(require_aggregate=False)
        states={case:q.snapshot(case) for case in retained_cases(private)}
        (proof/'access-registry-retained-state.json').write_text(json.dumps(states,indent=2)+'\n')
    else:
        method=next(k for k,v in vars(args).items() if v)
        getattr(q,'retained' if method=='verify_retained' else method)()
    verify_source_completion(proof,captured)
    witness.write_text(json.dumps(dict(before=captured,after=captured,status='passed'),indent=2)+'\n')
    q.record('executed-source-custody',files=len(captured),witness=witness.name,invocation=sys.argv[1:])

if __name__=='__main__':
    try:main()
    except Exception:
        print(json.dumps(dict(ok=False,code='access_qualification_failed_requires_inspection')))
        raise SystemExit(1) from None
