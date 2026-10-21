"""Actual synthetic Access staging matrix on fresh privately prepared native cases.

ACCESS_QUALIFICATION_DIR selects a private fixture using the existing Identity native
framework. Bootstrap is explicit separate preparation, never discovered or executed.
--all is single-use; --verify-retained performs only repeatable read-only inspection.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import urlsplit

from qualify_identity_baseline import ROOT, fixture as identity_fixture, engine, text, validate_fixture_urls
from sqlalchemy.exc import DBAPIError

ACCESS = ROOT/'services/access'
sys.path.insert(0, str(ACCESS/'migrations'))
import access_baseline as baseline


def validate_access_urls(private, run, target):
    # Keep identity_migrator URLs intact: the shared fixture validates them itself.
    validate_fixture_urls(private, run, target)
    assert set(private['access_owner_urls']) == set(private['databases'])
    for case,url in private['access_owner_urls'].items():
        a,b = urlsplit(url),urlsplit(private['databases'][case])
        assert a.scheme=='postgresql' and a.username=='access_migrator'
        assert a.hostname in ('127.0.0.1','localhost') and a.hostname==b.hostname
        assert a.port==target['ports']['database'] and a.path==b.path
        assert not a.query and not a.fragment


def fixture():
    os.environ['IDENTITY_QUALIFICATION_DIR'] = os.environ['ACCESS_QUALIFICATION_DIR']
    proof,private = identity_fixture()
    run=json.loads((proof/'run.json').read_text())
    target=json.loads(Path(run['target']).read_text())
    validate_access_urls(private,run,target)
    for p in (proof/'credentials.json',proof/'run.json'):
        assert p.stat().st_uid==os.getuid() and p.stat().st_mode & 0o077 == 0
    return proof,private


def require_database_error(operation, sqlstate, constraint=None):
    try:
        operation()
    except DBAPIError as error:
        assert error.orig.sqlstate == sqlstate, 'unexpected database refusal'
        if constraint is not None:
            assert error.orig.diag.constraint_name == constraint, 'unexpected constraint refusal'
    else:
        raise AssertionError('expected database refusal')


def verify_preparation(proof):
    witness = json.loads((proof/'bootstrap-source-custody.json').read_text())
    current = {str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(proof)}
    assert witness['status']=='passed' and witness['before']==witness['after']==current, 'bootstrap execution custody required'
    assert witness['steps']==['bootstrap.py','bootstrap_identity18.py']
    for name,digest in witness['logs'].items():
        assert name in ('bootstrap.log','bootstrap_identity18.log')
        assert sha256((proof/name).read_bytes()).hexdigest()==digest
    assert set(witness['logs'])=={'bootstrap.log','bootstrap_identity18.log'}


class Qualification:
    def __init__(self,proof,private):
        self.proof,self.private=proof,private
        result=proof/'access-membership-results.json'
        self.records=json.loads(result.read_text())['steps'] if result.exists() else []

    def db(self,case,role='access_owner_urls'):
        return engine(self.private[role][case])

    def execute(self,case,sql,role='access_owner_urls'):
        db=self.db(case,role)
        try:
            with db.begin() as c:
                c.exec_driver_sql("SET LOCAL statement_timeout='5s'; SET LOCAL lock_timeout='2s'")
                c.exec_driver_sql(sql)
        finally:db.dispose()

    def snapshot(self,case):
        db=self.db(case,'databases')
        try:
            with db.begin() as c:
                result={}
                for key,query in {
                    'relations':"SELECT c.relname,c.relkind,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,c.relacl::text,c.reloptions::text,c.relpersistence FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname",
                    'inheritance':"SELECT cn.nspname,child.relname,pn.nspname,parent.relname,i.inhseqno FROM pg_inherits i JOIN pg_class child ON child.oid=i.inhrelid JOIN pg_namespace cn ON cn.oid=child.relnamespace JOIN pg_class parent ON parent.oid=i.inhparent JOIN pg_namespace pn ON pn.oid=parent.relnamespace WHERE cn.nspname='access' OR pn.nspname='access' ORDER BY 1,2,3,4,5",
                    'columns':"SELECT c.relname,a.attname,a.attnum,format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity,a.attgenerated,pg_get_expr(d.adbin,d.adrelid),a.attacl::text FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE n.nspname='access' AND a.attnum>0 ORDER BY c.relname,a.attnum",
                    'constraints':"SELECT c.relname,k.conname,pg_get_constraintdef(k.oid),k.convalidated,k.condeferrable FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,k.conname",
                    'policies':"SELECT tablename,policyname,permissive,roles::text,cmd,qual,with_check FROM pg_policies WHERE schemaname='access' ORDER BY tablename,policyname",
                    'indexes':"SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='access' ORDER BY tablename,indexname",
                    'triggers':"SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access' ORDER BY c.relname,t.tgname",
                    'schema':"SELECT pg_get_userbyid(nspowner),nspacl::text FROM pg_namespace WHERE nspname='access'",
                    'defaults':"SELECT pg_get_userbyid(d.defaclrole),coalesce(n.nspname,''),d.defaclobjtype,d.defaclacl::text FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='access' OR d.defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator') ORDER BY 1,2,3",
                }.items(): result[key]=[list(r) for r in c.exec_driver_sql(query)]
                for name in ('grants','alembic_version'):
                    if c.execute(text("SELECT to_regclass(:name)"),{'name':'access.'+name}).scalar_one():
                        result[name]=[list(r) for r in c.exec_driver_sql('SELECT * FROM access.'+name+' ORDER BY 1,2' if name=='grants' else 'SELECT * FROM access.alembic_version ORDER BY 1')]
                return json.loads(json.dumps(result,default=str))
        finally:db.dispose()

    def record(self,label,**data):
        self.records.append(dict(label=label,**data));self.persist();print(label,'PASS',flush=True)

    def persist(self):
        (self.proof/'access-membership-results.json').write_text(json.dumps({'steps':self.records},indent=2)+'\n')

    def command(self,label,case,expected=None,action=('upgrade','head'),role='access_owner_urls',injected=False):
        env=dict(PATH='/usr/bin:/bin',LC_ALL='C.UTF-8',ACCESS_MIGRATION_DATABASE_URL=self.private[role][case].replace('postgresql://','postgresql+psycopg://',1))
        cmd=[sys.executable,'-I','-B','-m','alembic','-c',str(ACCESS/'alembic.ini'),*action]
        if injected:
            code="import sys;sys.path.insert(0,"+repr(str(ACCESS/'migrations'))+");import access_baseline as b;from alembic.config import Config;from alembic import command;defect=lambda c:(_ for _ in ()).throw(b.BaselineError('access_test_postcondition_failure'));b.verify_postcondition=defect;command.upgrade(Config("+repr(str(ACCESS/'alembic.ini'))+"),'head')"
            cmd=[sys.executable,'-I','-B','-c',code]
        started=time.monotonic();r=subprocess.run(cmd,env=env,cwd=ROOT,capture_output=True,text=True,timeout=75)
        log=r.stdout+r.stderr
        path=self.proof/(label+'.log');assert not path.exists();path.write_text(log);path.chmod(0o600)
        assert (r.returncode!=0 and expected in log) if expected else r.returncode==0,label
        # A DBAPI error string must not escape the controlled owner route.
        assert 'sqlalchemy.exc.' not in log and self.private['role_passwords']['access_migrator'] not in log
        self.record(label,case=case,exit_code=r.returncode,expected_failure=expected,elapsed_seconds=round(time.monotonic()-started,3),log_sha256=sha256(log.encode()).hexdigest())

    def initial(self,case,populated=False):
        self.command('exact1-'+case,case,action=('upgrade','access_0001'))
        if populated:
            self.execute(case,"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='legacy:System/not-a-uuid'; INSERT INTO access.grants(org_id,id,user_id,permission) VALUES ('11111111-1111-4111-8111-111111111111','opaque/grant:legacy','22222222-2222-4222-8222-222222222222','pts.poetry.read')")

    def assert_refused(self,label,case,expected,**kwargs):
        before=self.snapshot(case);self.command(label,case,expected,**kwargs);assert self.snapshot(case)==before,label+' changed state'

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
        self.record('opaque-ids-and-legacy-attribution-preserved')

    def boundaries(self):
        self.initial('boundary',True);self.command('boundary-upgrade','boundary')
        for value in ('NULL','1','9223372036854775807'):
            self.execute('boundary',"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; UPDATE access.grants SET membership_id="+value)
        for value in ('0','-1','-9223372036854775808','9223372036854775808'):
            before=self.snapshot('boundary')
            require_database_error(lambda:self.execute('boundary',"SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; UPDATE access.grants SET membership_id="+value),
                                   '22003' if value=='9223372036854775808' else '23514',
                                   None if value=='9223372036854775808' else 'grants_membership_id_positive')
            assert before==self.snapshot('boundary')
        before=self.snapshot('boundary')
        self.command('nonnull-membership-repeat','boundary')
        assert self.snapshot('boundary')==before
        self.record('nullable-positive-bigint-boundaries-atomic')

    def refusals(self):
        self.assert_refused('missing-bootstrap','missing','access_schema_owner_mismatch')
        self.assert_refused('wrong-owner-login','owner','access_migration_login_required',role='databases')
        for case,mutation,error in [
            ('unknown',"UPDATE access.alembic_version SET version_num='future_unknown'",'access_unknown_history'),
            ('malformed','ALTER TABLE access.alembic_version ALTER COLUMN version_num TYPE text','access_unknown_history'),
            ('multiple',"INSERT INTO access.alembic_version VALUES ('access_0002')",'access_unknown_history'),
            ('drift','ALTER TABLE access.grants ADD COLUMN surprise text','access_catalog_mismatch'),
            ('acl','GRANT UPDATE ON access.grants TO access_runtime','access_catalog_mismatch'),
            ('default','ALTER DEFAULT PRIVILEGES IN SCHEMA access GRANT SELECT ON TABLES TO access_runtime','access_default_privileges_mismatch'),
            ('policy','DROP POLICY org_scope ON access.grants','access_catalog_mismatch'),
            ('trigger',"CREATE FUNCTION access.fixture_trigger() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END $$; CREATE TRIGGER fixture BEFORE UPDATE ON access.grants FOR EACH ROW EXECUTE FUNCTION access.fixture_trigger()",'access_catalog_mismatch'),
        ]:
            self.initial(case,True);self.execute(case,mutation);self.assert_refused(case+'-refusal',case,error)
        for case,table,mutation in [
            ('unlogged_grants','grants','ALTER TABLE access.grants SET UNLOGGED'),
            ('unlogged_ledger','alembic_version','ALTER TABLE access.alembic_version SET UNLOGGED'),
            ('parent_grants','grants','CREATE TABLE fixture.child () INHERITS (access.grants)'),
            ('child_grants','grants','CREATE TABLE fixture.parent (LIKE access.grants INCLUDING CONSTRAINTS); ALTER TABLE access.grants INHERIT fixture.parent'),
            ('parent_ledger','alembic_version','CREATE TABLE fixture.child () INHERITS (access.alembic_version)'),
            ('child_ledger','alembic_version','CREATE TABLE fixture.parent (LIKE access.alembic_version INCLUDING CONSTRAINTS); ALTER TABLE access.alembic_version INHERIT fixture.parent'),
        ]:
            self.initial(case,True);self.execute(case,mutation)
            self.assert_refused(case+'-refusal',case,'access_unknown_history' if table=='alembic_version' else 'access_catalog_mismatch')
        self.initial('definer',True)
        self.execute('definer',"CREATE FUNCTION identity.fixture_cross_owner() RETURNS integer LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog AS $$ SELECT 1 $$; REVOKE ALL ON FUNCTION identity.fixture_cross_owner() FROM PUBLIC; GRANT USAGE ON SCHEMA identity TO access_migrator; GRANT EXECUTE ON FUNCTION identity.fixture_cross_owner() TO access_migrator",role='owner_urls')
        self.assert_refused('identity-definer-execute-refusal','definer','access_migration_role_excess_authority')
        self.execute('owner','GRANT CREATE ON DATABASE '+urlsplit(self.private['databases']['owner']).path[1:]+' TO access_migrator',role='databases')
        self.assert_refused('excess-database-authority','owner','access_migration_role_excess_authority')
        self.execute('owner','REVOKE CREATE ON DATABASE '+urlsplit(self.private['databases']['owner']).path[1:]+' FROM access_migrator',role='databases')
        for action in [('stamp','head'),('downgrade','base'),('upgrade','head','--sql')]:
            label='prohibit-'+action[0]+('-offline' if '--sql' in action else '')
            self.assert_refused(label,'owner','access_offline_migrations_prohibited' if '--sql' in action else 'access_use_verified_upgrade_route',action=action)

    def recovery(self):
        self.initial('failure',True)
        self.assert_refused('injected-postcondition-rollback','failure','access_test_postcondition_failure',injected=True)
        self.command('explicit-recovery','failure')
        for case,sql,error in [('concurrent',baseline.LOCK_SQL,'access_migration_busy'),('lock','LOCK TABLE access.grants IN ACCESS EXCLUSIVE MODE','access_migration_failed_requires_reconciliation')]:
            self.initial(case,True);before=self.snapshot(case);db=self.db(case)
            try:
                with db.begin() as c:
                    c.exec_driver_sql(sql)
                    self.command('bounded-'+case,case,error)
                assert self.snapshot(case)==before
            finally:db.dispose()
            self.command('recovery-'+case,case)

    def permissions(self):
        before=self.snapshot('boundary')
        context="SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='legacy:System/not-a-uuid'; SET LOCAL app.account_id='22222222-2222-4222-8222-222222222222'; "
        for statement in ["INSERT INTO access.grants(org_id,id,user_id,permission) VALUES ('11111111-1111-4111-8111-111111111111','forbidden','33333333-3333-4333-8333-333333333333','pts.poetry.read')",'UPDATE access.grants SET membership_id=1','DELETE FROM access.grants','SET ROLE access_migrator','ALTER TABLE access.grants ADD COLUMN forbidden text','SELECT * FROM access.alembic_version']:
            require_database_error(lambda:self.execute('boundary',context+statement,role='runtime_urls'),'42501')
        assert self.snapshot('boundary')==before
        db=self.db('boundary','runtime_urls')
        try:
            with db.begin() as c:
                assert c.exec_driver_sql('SELECT * FROM access.grants').all()==[]
                c.exec_driver_sql("SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'")
                assert c.exec_driver_sql('SELECT membership_id FROM access.grants').scalar_one()==9223372036854775807
        finally:db.dispose()
        self.record('actual-runtime-read-only-rls-private-ledger')

    def integration(self):
        # Explicit root preparation supplies a real Identity18 case before this stage.
        db=engine(self.private['owner_urls']['integration'])
        sys.path.insert(0,str(ACCESS/'identity-migrations'));import identity_baseline
        def snapshot():
            with db.begin() as c:
                identity_baseline.verify_owned_postcondition(c,require_head=True)
                result=identity_baseline.catalog_snapshot(c)
                result['data']={}
                for table in c.exec_driver_sql("SELECT tablename FROM pg_tables WHERE schemaname='identity' ORDER BY tablename").scalars():
                    # Identifiers originate from the inspected synthetic owner catalog.
                    result['data'][table]=[list(r) for r in c.exec_driver_sql('SELECT * FROM identity."'+table.replace('"','""')+'" ORDER BY 1')]
                return json.dumps(result,default=str,sort_keys=True)
        try:
            before=snapshot();self.command('identity18-access-upgrade','integration');assert snapshot()==before
            context="SET LOCAL app.org_id='11111111-1111-4111-8111-111111111111'; SET LOCAL app.actor_id='legacy:System/not-a-uuid'; SET LOCAL app.account_id='22222222-2222-4222-8222-222222222222'; "
            for statement in ['SELECT * FROM identity.org_member','ALTER TABLE identity.org_member ADD COLUMN forbidden text','DELETE FROM identity.org_member','SET ROLE identity_migrator']:
                require_database_error(lambda:self.execute('integration',context+statement),'42501')
            assert snapshot()==before
            self.record('real-identity18-catalog-history-data-preserved',sha256=sha256(before.encode()).hexdigest())
        finally:db.dispose()

    def retained(self, require_aggregate=True):
        if require_aggregate:
            records=json.loads((self.proof/'access-membership-results.json').read_text())['steps']
            completed=[r for r in records if r['label']=='executed-source-custody' and r.get('invocation')==['--all']]
            assert completed,'completed aggregate source witness required'
            recorded=json.loads((self.proof/completed[-1]['witness']).read_text())
            current={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths(self.proof)}
            assert recorded['status']=='passed' and recorded['before']==recorded['after']==current
            for receipt in records:
                if 'log_sha256' in receipt:
                    assert sha256((self.proof/(receipt['label']+'.log')).read_bytes()).hexdigest()==receipt['log_sha256']
            expected=json.loads((self.proof/'access-retained-state.json').read_text())
            assert expected=={case:self.snapshot(case) for case in expected}
        for case in ('clean','previous','boundary','failure','concurrent','lock','integration'):
            db=self.db(case)
            try:
                with db.begin() as c:baseline.preflight(c);baseline.verify_postcondition(c)
            finally:db.dispose()
        self.record('retained-exact-head-inspection')


def source_paths(proof):
    # Capture every repository-owned executed source in this aggregate, including
    # the separately prepared Identity18 source/reference closure and native guards.
    import dev
    return sorted(set([*[ROOT/name for name in dev.SOURCES],
        *list((ROOT/'platform/deployment').glob('*.py')),
        *list((ROOT/'platform/deployment').glob('*.json')),
        *list((ROOT/'platform/deployment/schema').glob('*.json')),
        *list((ROOT/'platform/deployment/environments').glob('*.json')),
        *list((ACCESS/'tools').glob('*.sql')),
        ACCESS/'identity-migrations/pyproject.toml', ACCESS/'identity-migrations/uv.lock',
        *list((ACCESS/'migrations').glob('*.py')),*list((ACCESS/'migrations/versions').glob('*.py')),
        ACCESS/'alembic.ini',ACCESS/'identity-alembic.ini',*list((ACCESS/'identity-migrations').glob('*.py')),
        *list((ACCESS/'identity-migrations').glob('*.json')),*list((ACCESS/'identity-migrations/versions').glob('*.py')),
        *[ROOT/name for name in ('platform/deployment/dev.py','platform/deployment/native_cli.py')],
        ACCESS/'tests/qualify_identity_baseline.py',Path(__file__),*list(proof.glob('bootstrap*.py')),proof/'auth-helper-definitions.json',
        *[ROOT/name for name in json.loads((ACCESS/'identity-migrations/source-pins.json').read_text())]]))


def main():
    if not __debug__:
        raise RuntimeError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    for flag in ('all','verify-retained','clean-previous','boundaries','refusals','recovery','permissions','integration'):group.add_argument('--'+flag,action='store_true')
    args=parser.parse_args();proof,private=fixture();verify_preparation(proof);q=Qualification(proof,private)
    paths=source_paths(proof);captured={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths}
    witness=proof/('access-source-'+str(time.time_ns())+'.json');witness.write_text(json.dumps(dict(before=captured,status='started'),indent=2)+'\n')
    if args.all:
        marker=proof/'access-all-started';marker.open('x').close()
        for method in (q.clean_previous,q.boundaries,q.refusals,q.recovery,q.permissions,q.integration):method()
        q.retained(require_aggregate=False)
        states={case:q.snapshot(case) for case in private['databases'] if case not in ('native','red')}
        (proof/'access-retained-state.json').write_text(json.dumps(states,indent=2)+'\n')
    else:
        method=next(k for k,v in vars(args).items() if v)
        getattr(q,'retained' if method=='verify_retained' else method)()
    assert captured=={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},'qualification_source_changed'
    witness.write_text(json.dumps(dict(before=captured,after=captured,status='passed'),indent=2)+'\n')
    q.record('executed-source-custody',files=len(captured),witness=witness.name,invocation=sys.argv[1:])


if __name__=='__main__':
    try:main()
    except Exception:
        print(json.dumps(dict(ok=False,code='access_qualification_failed_requires_inspection')))
        raise SystemExit(1) from None
