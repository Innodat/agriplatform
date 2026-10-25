"""One new disposable native fixture. Not a provisioner or release readiness gate.

Only this module's newly allocated run is eligible for writes/normal stop. Owner
migrations and Auth run against the same real provider database, with no clones.
"""
from __future__ import annotations
if not __debug__:raise RuntimeError('qualification_optimized_python_prohibited')
import argparse
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import time
from uuid import UUID,uuid4

ROOT=Path(__file__).resolve().parents[3]
APP=ROOT/'apps/scribeswell'
ACCESS=ROOT/'services/access'
TARGET=ROOT/'platform/deployment/environments/kdg-local.json'
PORTS=(5188,8188,8189,55480,55481,55482,55483,15484,8443)
RESERVATIONS=ROOT/'platform/deployment/.local/scribeswell-owner-reservations'

def private(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as out:json.dump(value,out,ensure_ascii=False,indent=2,default=str)

def check_ports():
    for port in PORTS:
        with socket.socket() as listener:
            try:listener.bind(('127.0.0.1',port))
            except OSError:raise RuntimeError('qualification_port_occupied:'+str(port)) from None

def wait_http(url,process):
    import httpx
    limit=time.monotonic()+30
    while time.monotonic()<limit:
        if process.poll() is not None:raise RuntimeError('qualification_process_exited')
        try:
            if httpx.get(url,timeout=1).status_code<500:return
        except httpx.HTTPError:pass
        time.sleep(.2)
    raise RuntimeError('qualification_start_timeout')

def source_inventory():
    from hashlib import sha256
    paths={Path(__file__),TARGET}
    for base in (ACCESS,APP):paths.update(base.glob('*.ini'))
    paths.update(ACCESS.glob('*.py'))
    for base in (ACCESS/'identity-migrations',ACCESS/'migrations',ACCESS/'tools',APP/'backend',APP/'studies-migrations',APP/'studies-database-tools',APP/'tools/sql',APP/'supabase/migrations',APP/'web/src'):
        paths.update(p for p in base.rglob('*') if p.is_file() and p.suffix in ('.py','.sql','.json','.ts','.tsx','.ini'))
    paths.update((APP/'data/reference-catalogue').glob('*.json'))
    paths.update((APP/'scripts').glob('hebrew.json'));paths.update((APP/'tools/py').glob('build_reference_catalogue.py'))
    paths.update((APP/'web/tests').glob('studies-owner*.cjs'))
    paths.update((APP/'tools/py').glob('qualify_studies_owner_integration.py'))
    paths.update((APP/'web').glob('*config.*'))
    paths.update((APP/'web').glob('package*.json'))
    paths.update((ROOT/'platform/deployment').glob('*.py'))
    paths.update((ROOT/'platform/deployment/schema').glob('*.json'))
    target=json.loads(TARGET.read_text())
    paths.update(ROOT/target[name] for name in ('fixture_ref','release_registry_ref'))
    paths.update(ROOT/name for name in json.loads((ACCESS/'identity-migrations/source-pins.json').read_text()))
    paths.update(ROOT.glob('package*.json'))
    return {p:sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}

PROTECTED_TABLES=(
    'identity.users','identity.actor','identity.account_actor','identity.org_member',
    'identity.operation_outcome','identity.business_event',
    'identity.studies_setup_outcome','identity.studies_setup_event',
    'access.studies_account_grant','access.studies_enrollment_outcome','access.studies_assignment_event',
    'scribeswell_studies.studies','scribeswell_studies.notes','scribeswell_studies.receipts',
    'scribeswell_studies.passage_lists','scribeswell_studies.passage_entries',
)

def protected_state(connection):
    from psycopg import sql
    tables=connection.execute("SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname=ANY(%s) AND c.relkind IN ('r','p') ORDER BY 1,2",(['identity','access','scribeswell_studies'],)).fetchall()
    return {schema+'.'+table:[row[0] for row in connection.execute(sql.SQL('SELECT to_jsonb(t) FROM {} t ORDER BY to_jsonb(t)::text').format(sql.Identifier(schema,table))).fetchall()] for schema,table in tables}

def unchanged_state(before,after):
    if before!=after:raise AssertionError('Denied operation changed protected business state')

def assert_non_target_notes_unchanged(before,after,note_id):
    assert [row for row in before if row['id']!=note_id]==[row for row in after if row['id']!=note_id],'Note link changed another note'

def empty_protected_state(state):
    if any(state[name] for name in PROTECTED_TABLES if name not in ('identity.users','identity.actor')):
        raise AssertionError('Protected effects exist before explicit enrollment')

def executing_group_members(group):
    # Linux fixture-only observation. Zombies cannot execute and must not prevent
    # confirmation when the container's init has not yet reaped an orphan.
    members=[]
    try:
        for path in Path('/proc').iterdir():
            if not path.name.isdecimal():continue
            try:fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            except FileNotFoundError:continue
            if int(fields[2])==group and fields[0] not in ('Z','X'):members.append(int(path.name))
    except (OSError,ValueError,IndexError):raise OSError('qualification_process_observation_unavailable') from None
    return members

def assert_study_erasure(before,after,expected):
    study=expected['study'];empty={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
    # Preserve independent owner/application/identity rows and every old receipt.
    changed={'scribeswell_studies.studies','scribeswell_studies.notes','scribeswell_studies.passage_lists','scribeswell_studies.passage_entries','scribeswell_studies.receipts'}
    for table in before:
        if table not in changed:assert before[table]==after[table]
    for table in ('scribeswell_studies.studies','scribeswell_studies.notes'):
        key='id' if table.endswith('.studies') else 'study_id'
        assert [row for row in before[table] if row[key]!=study]==[row for row in after[table] if row[key]!=study]
        old={row['id']:row for row in before[table] if row[key]==study};new={row['id']:row for row in after[table] if row[key]==study}
        assert old.keys()==new.keys()
        for id,row in old.items():
            current=new[id]
            if not row['active']:assert current==row;continue
            assert not current['active'] and current['revision']==row['revision']+1
            assert current['created_at']==row['created_at'] and current['created_by']==row['created_by']==current['updated_by'] and current['updated_at']>row['updated_at']
            if table.endswith('.studies'):assert current['title']=='Deleted study' and current['revision']==int(expected['revision'])
            else:assert current['value']==empty
    for table in ('scribeswell_studies.passage_lists','scribeswell_studies.passage_entries'):
        assert after[table]==[row for row in before[table] if row['study_id']!=study]
    old=before['scribeswell_studies.receipts'];new=after['scribeswell_studies.receipts']
    assert all(row in new for row in old)
    added=[row for row in new if row not in old]
    assert len(added)==1 and added[0]['command']=='study.delete' and added[0]['operation_id']==expected['operation']
    assert added[0]['outcome']=={'operation_id':expected['operation'],'command':'study.delete','study_id':study,'note_id':None,'revision':expected['revision']}


class Qualification:
    def __init__(self,run_id,cli,proof):
        if str(UUID(run_id))!=run_id or UUID(run_id).int==0:raise ValueError('canonical_new_run_required')
        self.run_id=run_id;self.cli=Path(cli).resolve();self.proof=Path(proof).absolute()
        self.run=ROOT/'platform/deployment/.local/kdg'/run_id
        if self.run.exists():raise FileExistsError('existing_run_refused')
        self.proof.mkdir(mode=0o700,parents=True,exist_ok=False)
        self.events=[];self.processes=[];self.owned=False
        RESERVATIONS.mkdir(mode=0o700,parents=True,exist_ok=True)
        self.reservation=RESERVATIONS/(run_id+'.json')
        private(self.reservation,{'run_id':run_id,'proof':str(self.proof)})
        self.sources=source_inventory()
        self.protected_snapshots={}
        private(self.proof/'sources.json',{str(p.relative_to(ROOT)):digest for p,digest in self.sources.items()})
        self.environment={key:os.environ[key] for key in ('PATH','HOME') if key in os.environ}
        self.environment.update({'LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1'})

    def command(self,label,args,env=None,cwd=ROOT,timeout=120,on_started=None):
        path=self.proof/(label+'.log')
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as output:
            started=time.monotonic()
            process=subprocess.Popen([str(a) for a in args],env=env or self.environment,cwd=cwd,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                if on_started:on_started(process)
                code=process.wait(timeout=max(.001,timeout-(time.monotonic()-started)))
            except BaseException:
                self.stop_process(process)
                self.events.append({'stage':label,'outcome':'interrupted-or-timed-out'})
                raise
            # Reap any remaining owned launcher descendants before the next stage.
            self.stop_process(process)
        self.events.append({'stage':label,'command':[str(a) for a in args],'exit_code':code})
        if code:raise RuntimeError('qualification_stage_failed:'+label)

    def wrapper(self,action):
        self.command('wrapper-'+action,[sys.executable,ROOT/'platform/deployment/dev.py',action,'--target',TARGET,'--run-id',self.run_id,'--supabase',self.cli],timeout=240)

    def capture_status(self):
        sys.path.insert(0,str(ROOT/'platform/deployment'))
        import dev,native_cli
        raw=dev.read(TARGET);target=dev.decode(raw)
        native_cli.check_run(self.run,target,raw,self.run_id)
        network=native_cli.network(target,self.run_id,False,self.run)
        fd=os.open(self.proof/'status-private.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as output:
            process=subprocess.Popen([str(self.cli),'--workdir',str(self.run),'--network-id',network,'status','-o','json'],env=native_cli.environment(self.run),cwd=self.run,stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.DEVNULL,start_new_session=True)
            try:code=process.wait(timeout=30)
            finally:self.stop_process(process)
            if code:raise RuntimeError('qualification_status_capture_failed')
        self.status={k.lower():v for k,v in json.loads((self.proof/'status-private.json').read_text()).items()}
        from sqlalchemy.engine import make_url
        self.admin=make_url(self.status['db_url']).set(username='supabase_admin')
        if self.admin.host not in ('127.0.0.1','localhost') or self.admin.port!=55482 or self.admin.database!='postgres':raise ValueError('unexpected_native_database')
        self.urls={}

    def connect(self,role=None):
        import psycopg
        url=self.admin if role is None else self.urls[role]
        return psycopg.connect(url.render_as_string(hide_password=False),connect_timeout=3,autocommit=True,options='-c statement_timeout=20000 -c lock_timeout=3000 -c idle_in_transaction_session_timeout=20000')

    def prepare_owners(self):
        from psycopg import sql
        # Fresh cluster-only role setup; ordinary helpers own the additional roles.
        roles=('identity_migrator','access_migrator','access_runtime','scribeswell_runtime')
        with self.connect() as c:
            if c.execute("SELECT 1 FROM pg_namespace WHERE nspname IN ('identity','access','scribeswell','scribeswell_studies')").fetchone():raise RuntimeError('nonempty_owner_fixture_refused')
            c.execute('REVOKE TEMPORARY,CREATE ON DATABASE postgres FROM PUBLIC')
            # The native image exposes extension diagnostics to PUBLIC. Empty
            # owner-role qualification requires no inherited table reads. Confine
            # these fixture ACL changes to this fresh disposable database.
            public_reads=c.execute("SELECT n.nspname,c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname !~ '^pg_' AND n.nspname<>'information_schema' AND c.relkind IN ('r','p','v','m','f') AND EXISTS(SELECT 1 FROM aclexplode(c.relacl) a WHERE a.grantee=0 AND a.privilege_type='SELECT')").fetchall()
            private(self.proof/'fixture-public-read-preparation.json',{'tables':public_reads})
            for schema,table in public_reads:c.execute(sql.SQL('REVOKE SELECT ON {}.{} FROM PUBLIC').format(sql.Identifier(schema),sql.Identifier(table)))
            for role in roles:
                password=secrets.token_urlsafe(32)
                c.execute(sql.SQL('CREATE ROLE {} LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
                self.urls[role]=self.admin.set(username=role,password=password)
            # Reproduce the owner-verified native bootstrap graph, not inherited
            # owner authority: postgres holds the exact ADMIN-only Identity edge.
            c.execute('GRANT identity_migrator TO postgres WITH ADMIN TRUE, INHERIT FALSE, SET FALSE')
            c.execute('GRANT access_migrator TO postgres WITH ADMIN TRUE, INHERIT FALSE, SET FALSE')
            c.execute('SET SESSION AUTHORIZATION postgres;GRANT access_migrator TO postgres WITH ADMIN FALSE, INHERIT FALSE, SET TRUE;RESET SESSION AUTHORIZATION')
            c.execute('CREATE SCHEMA identity AUTHORIZATION identity_migrator;CREATE SCHEMA access AUTHORIZATION access_migrator')
            c.execute('SET ROLE access_migrator;GRANT USAGE ON SCHEMA access TO access_runtime;RESET ROLE')
            c.execute('GRANT USAGE ON SCHEMA auth TO identity_migrator WITH GRANT OPTION;GRANT USAGE ON SCHEMA extensions TO identity_migrator;GRANT SELECT(id),REFERENCES(id),TRIGGER ON auth.users TO identity_migrator;GRANT CREATE,USAGE ON SCHEMA public TO identity_migrator')
            for helper in ('prepare_identity_projection_role.sql','prepare_identity_operator_roles.sql','prepare_identity_command_role.sql','prepare_identity_target_roles.sql','prepare_identity_account_verification_role.sql','prepare_identity_account_verification_auth.sql','prepare_access_operator_roles.sql','prepare_access_check_reader.sql','prepare_studies_runtime_roles.sql','prepare_studies_auth_evidence.sql'):
                c.execute((ACCESS/'tools'/helper).read_text())
            # Access reader preparation predates Studies and requires its exact
            # two existing owner edges. Stage the later Access edge afterwards.
            c.execute('REVOKE access_studies_owner FROM access_migrator')
            c.execute((APP/'tools/sql/prepare_personal_notes_roles.sql').read_text())
            for role in ('identity_studies_reader_runtime','identity_studies_setup_runtime','access_studies_runtime','access_operator','scribeswell_studies_migrator','scribeswell_studies_runtime'):
                password=secrets.token_urlsafe(32)
                c.execute(sql.SQL('ALTER ROLE {} PASSWORD {}').format(sql.Identifier(role),sql.Literal(password)))
                self.urls[role]=self.admin.set(username=role,password=password)
        with self.connect() as c:
            memberships=c.execute("SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,to_jsonb(m)->>'inherit_option',to_jsonb(m)->>'set_option' FROM pg_auth_members m WHERE pg_get_userbyid(member) IN ('identity_migrator','access_runtime','authenticated','anon','service_role','supabase_auth_admin') OR pg_get_userbyid(roleid)='identity_migrator' ORDER BY 1,2").fetchall()
            private(self.proof/'prepared-role-memberships.json',memberships)
        # Separate owner processes avoid name collisions and preserve real Alembic guards.
        for owner,config in (('identity','identity-alembic.ini'),):
            self.migrate(owner,ACCESS/config)
        with self.connect() as c:
            c.execute((ACCESS/'tools/prepare_access_check_reader_execution.sql').read_text())
            c.execute('GRANT access_studies_owner TO access_migrator WITH ADMIN FALSE, INHERIT FALSE, SET TRUE')
        self.migrate('access',ACCESS/'alembic.ini')
        self.migrate('scribeswell_studies',APP/'studies-alembic.ini')
        self.prepare_principals()
        self.prepare_corpus()
        self.create_accounts()
        private(self.proof/'credentials-private.json',{role:url.render_as_string(hide_password=False) for role,url in self.urls.items()})
        self.observe('before-enrollment',initial=True)

    def migrate(self,owner,config):
        env={**self.environment,owner.upper()+'_MIGRATION_DATABASE_URL':self.urls[owner+'_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)}
        self.command('migrate-'+owner,[sys.executable,'-I','-B','-m','alembic','-c',config,'upgrade','head'],env=env)

    def prepare_principals(self):
        self.actor=str(uuid4());self.service_key=secrets.token_urlsafe(32)
        with self.connect('identity_migrator') as c:
            c.execute("INSERT INTO identity.actor(id,kind,display_name,actor_key,created_by,updated_by) VALUES(%s,'service','Synthetic integration executor',%s,%s,%s)",(self.actor,'owner-integration.'+self.run_id,self.actor,self.actor))
            c.execute("INSERT INTO identity.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('identity_studies_setup_runtime',%s,true,%s,%s,%s)",(self.actor,self.actor,self.actor,str(uuid4())))
        with self.connect('access_migrator') as c:
            c.execute("INSERT INTO access.studies_runtime_principal(database_login,executor_actor_id,enabled,created_by,updated_by,operation_id) VALUES('access_studies_runtime',%s,true,%s,%s,%s)",(self.actor,self.actor,self.actor,str(uuid4())))
            c.execute("INSERT INTO access.operator_principals(database_login,executor_actor_id,enabled,created_by,updated_by) VALUES('access_operator',%s,true,%s,%s)",(self.actor,self.actor,self.actor))
            for command in ('application.register','permission.register','application.set_enabled'):
                c.execute("INSERT INTO access.operator_authorities(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by) VALUES(%s,'access_operator',%s,'platform','scribeswell',true,%s,%s)",(str(uuid4()),command,self.actor,self.actor))
        for command,payload in (('application.register',{'app_id':'scribeswell','expected_absent':True}),('permission.register',{'app_id':'scribeswell','permission':'scribeswell.studies.use','scope_kind':'account','expected_absent':True}),('application.set_enabled',{'app_id':'scribeswell','enabled':True,'expected_revision':'1'})):
            self.operator(command,payload)

    def operator(self,command,payload):
        # Run the existing protected command in its own module namespace.
        envelope={'schema_version':1,'operation_id':str(uuid4()),'command':command,'scope':{'kind':'platform'},'payload':payload,'reason_code':'synthetic_fixture','evidence_ref':'synthetic:'+self.run_id}
        path=self.proof/('operator-'+str(uuid4())+'.json');private(path,envelope)
        code="import os,sys;from sqlalchemy import create_engine;from access_operator import execute;e=create_engine(os.environ['FIXTURE_OPERATOR_URL'],hide_parameters=True);c=e.connect();execute(c,open(sys.argv[1],'rb').read());c.close();e.dispose()"
        self.command(path.stem,[sys.executable,'-c',code,path],env={**self.environment,'FIXTURE_OPERATOR_URL':self.urls['access_operator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)},cwd=ACCESS)

    def prepare_corpus(self):
        with self.connect() as c:
            c.execute((APP/'supabase/migrations/20260614000000_scribeswell_create_schema.sql').read_text())
            c.execute("INSERT INTO scribeswell.book VALUES(1,'Gen','Genesis','בראשית','old','torah',1);INSERT INTO scribeswell.chapter(id,book_id,chapter_num) VALUES(1,1,1);INSERT INTO scribeswell.verse(id,chapter_id,verse_num,book_id,chapter_num) VALUES(1,1,1,1,1);INSERT INTO scribeswell.word(id,verse_id,position,surface_he,display_he) VALUES(1,1,1,'בְּרֵאשִׁית','בְּרֵאשִׁית')")
            c.execute('GRANT USAGE ON SCHEMA scribeswell TO scribeswell_runtime;GRANT SELECT ON ALL TABLES IN SCHEMA scribeswell TO scribeswell_runtime')
            for table in ('book','chapter','verse','word','morpheme'):
                c.execute('CREATE POLICY integration_read ON scribeswell.'+table+' FOR SELECT TO scribeswell_runtime USING(true)')

    def create_accounts(self):
        import httpx
        self.accounts=[]
        api=self.status['api_url'];service=self.status['service_role_key']
        headers={'apikey':service,'Authorization':'Bearer '+service}
        with httpx.Client(timeout=5) as client:
            for _ in range(2):
                email='studies-'+uuid4().hex+'@example.invalid'
                response=client.post(api+'/auth/v1/admin/users',headers=headers,json={'email':email,'email_confirm':True})
                if response.status_code!=200:raise RuntimeError('provider_account_creation_failed')
                account=response.json()['id']
                response=client.post(api+'/auth/v1/admin/generate_link',headers=headers,params={'redirect_to':'http://localhost:5188/'},json={'type':'magiclink','email':email})
                if response.status_code!=200:raise RuntimeError('provider_magic_link_failed')
                body=response.json();properties=body.get('properties',body)
                self.accounts.append({'account_id':account,'link':properties['action_link']})
        private(self.proof/'browser-private.json',{'accounts':self.accounts,'service_key_sentinel':self.service_key,'provider_service_sentinel':self.status['service_role_key'],'proof':str(self.proof)})

    def snapshot(self,label,previous=None):
        from hashlib import sha256
        with self.connect() as c:
            c.execute('BEGIN READ ONLY');state=protected_state(c);c.execute('ROLLBACK')
        if previous is not None:unchanged_state(self.protected_snapshots[previous],state)
        self.protected_snapshots[label]=state
        private(self.proof/(label+'.json'),{'protected_counts':{name:len(rows) for name,rows in state.items()},'protected_sha256':sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'unchanged_from':previous,'independent_sql':True})
        return state

    def observe(self,label,initial=False):
        state=self.snapshot(label)
        accounts={account['account_id'] for account in self.accounts}
        assert {row['id'] for row in state['identity.users']}==accounts
        assert not state['identity.org_member']
        if initial:
            empty_protected_state(state)
            assert {row['id'] for row in state['identity.actor']}=={self.actor}
            return
        expected=json.loads((self.proof/'browser-result.json').read_text())
        bindings={row['account_id']:row['actor_id'] for row in state['identity.account_actor']}
        assert set(bindings)==accounts and len(state['identity.account_actor'])==2
        assert bindings==expected['account_actors']
        actors={row['id']:row for row in state['identity.actor']}
        assert set(actors)=={self.actor,*bindings.values()} and actors[self.actor]['kind']=='service'
        for actor in bindings.values():assert actors[actor]['kind']=='account'
        owner=self.accounts[0]['account_id'];studies=state['scribeswell_studies.studies'];notes=state['scribeswell_studies.notes']
        assert len(studies)==2 and {row['id'] for row in studies}=={expected['study'],expected['retry_study']}
        assert len(notes)==2 and {row['id'] for row in notes}=={expected['note'],expected['retained_note']}
        target=next(row for row in notes if row['id']==expected['note'])
        assert target['study_id']==expected['study'] and target['value']==expected['value'] and not target['active']
        retained=next(row for row in notes if row['id']==expected['retained_note'])
        if 'study_delete_operation' in expected:
            assert not retained['active'] and retained['value']=={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
            deleted_study=next(row for row in studies if row['id']==expected['study'])
            assert not deleted_study['active'] and deleted_study['title']=='Deleted study' and deleted_study['revision']==3
            assert next(row for row in studies if row['id']==expected['retry_study'])['active']
        else:assert retained['active']
        for row in studies+notes:
            assert row['account_id']==owner and row['created_by']==row['updated_by']==bindings[owner]
            assert row['created_at'] and row['updated_at']>=row['created_at'] and row['revision']>0
        receipts=state['scribeswell_studies.receipts']
        assert sorted(row['command'] for row in receipts)==sorted(['note.create','note.replace','study.create','study.create']+(['study.rename'] if 'rename_operation' in expected else [])+['study.passages.replace']*len(expected.get('passage_operations',[]))+(['note.replace'] if 'note_link_operation' in expected else [])+(['note.delete','note.create'] if 'note_delete_operation' in expected else [])+(['study.delete'] if 'study_delete_operation' in expected else []))
        if 'rename_operation' in expected:
            renamed=next(row for row in studies if row['id']==expected['study'])
            assert (renamed['title'],renamed['revision'])==(('Deleted study',3) if 'study_delete_operation' in expected else (expected['rename_title'],2))
            assert {row['operation_id'] for row in receipts if row['command']=='study.rename'}=={expected['rename_operation']}
        if 'passage_operations' in expected:
            assert {row['operation_id'] for row in receipts if row['command']=='study.passages.replace'}==set(expected['passage_operations'])
            headers=state['scribeswell_studies.passage_lists'];entries=state['scribeswell_studies.passage_entries']
            if 'study_delete_operation' in expected:assert headers==[] and entries==[]
            else:
                assert len(headers)==1 and headers[0]['revision']==4 and headers[0]['study_id']==expected['study']
                assert len(entries)==1 and entries[0]['id']==expected['passage_item']['id'] and entries[0]['book_id']=='Matt'
            for row in headers+entries:assert row['account_id']==owner and row['created_by']==bindings[owner] and row['created_at']
        assert {row['operation_id'] for row in receipts if row['command']=='study.create'}=={expected['operation'],expected['ui_operation']}
        for row in receipts:assert row['account_id']==owner and row['created_by']==bindings[owner] and row['created_at']
        for table in ('access.studies_account_grant','access.studies_assignment_event','identity.studies_setup_event'):
            rows=state[table];assert len(rows)==2 and {row['account_id'] for row in rows}==accounts
            for row in rows:assert row['actor_id']==bindings[row['account_id']]
        expected_operations={expected['enrollment'],expected['ui_enrollment'],expected['other_enrollment']}
        for table in ('access.studies_enrollment_outcome','identity.studies_setup_outcome'):
            operations=expected_operations if table.startswith('access.') else {expected['ui_enrollment'],expected['other_enrollment']}
            rows=state[table];assert len(rows)==len(operations) and {row['operation_id'] for row in rows}==operations
            for row in rows:assert row['actor_id']==bindings[row['account_id']]

    def verify_sources(self):
        if source_inventory()!=self.sources:raise RuntimeError('qualification_sources_changed')

    def spawn(self,label,args,env,cwd):
        fd=os.open(self.proof/(label+'.log'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as out:
            started=time.monotonic()
            process=subprocess.Popen([str(a) for a in args],cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
        self.processes.append(process);return process

    def start_apps(self):
        owner_code="import os;from main import create_app;os.environ['SCRIBESWELL_SERVICE_KEY']=os.environ['FIXTURE_SERVICE_KEY'];from studies_identity import AsyncDatabase;app=create_app(object(),studies_db=AsyncDatabase(os.environ['FIXTURE_ACCESS_URL']),studies_identity_db=AsyncDatabase(os.environ['FIXTURE_IDENTITY_URL']),studies_setup_db=AsyncDatabase(os.environ['FIXTURE_SETUP_URL']));import uvicorn;uvicorn.run(app,host='127.0.0.1',port=8189,access_log=False,log_level='error')"
        env={**self.environment,'FIXTURE_SERVICE_KEY':self.service_key,'SUPABASE_URL':self.status['api_url'],'SUPABASE_ANON_KEY':self.status['anon_key'],'FIXTURE_ACCESS_URL':self.urls['access_studies_runtime'].render_as_string(hide_password=False),'FIXTURE_IDENTITY_URL':self.urls['identity_studies_reader_runtime'].render_as_string(hide_password=False),'FIXTURE_SETUP_URL':self.urls['identity_studies_setup_runtime'].render_as_string(hide_password=False)}
        owner=self.spawn('access-http',[sys.executable,'-c',owner_code],env,ACCESS)
        wait_http('http://127.0.0.1:8189/health',owner)
        env={**self.environment,'SCRIBESWELL_DATABASE_URL':self.urls['scribeswell_runtime'].render_as_string(hide_password=False),'SCRIBESWELL_STUDIES_ENABLED':'true','SCRIBESWELL_STUDIES_DATABASE_URL':self.urls['scribeswell_studies_runtime'].render_as_string(hide_password=False),'SCRIBESWELL_STUDIES_ACCESS_URL':'http://127.0.0.1:8189','SCRIBESWELL_STUDIES_SERVICE_KEY':self.service_key,'SUPABASE_URL':self.status['api_url'],'SUPABASE_SECRET_KEY':'','SUPABASE_SERVICE_ROLE_KEY':''}
        app=self.spawn('scribeswell-http',[sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port','8188','--no-access-log','--log-level','error'],env,APP/'backend')
        wait_http('http://127.0.0.1:8188/health',app)
        env={**self.environment,'VITE_STUDIES_ENABLED':'true','VITE_APP_BASE':'/','VITE_PLATFORM_ORIGIN':'','VITE_SUPABASE_URL':self.status['api_url'],'VITE_SUPABASE_ANON_KEY':self.status['anon_key'],'VITE_API_BASE_URL':'http://127.0.0.1:8188','VITE_APP_DIRECTORY_URL':'http://127.0.0.1:8189'}
        web=self.spawn('vite',['npm','run','dev','--','--host','localhost','--port','5188','--strictPort'],env,APP/'web')
        wait_http('http://localhost:5188',web)

    def browser(self):
        def checkpoints(process):
            for name in ('pre-enrollment','rename-before','rename-after','passages-before','passages-after','note-links-before','note-links-after','search-before','search-after','foreign-before','foreign-after','deletion-before','deletion-after','study-deletion-before','study-deletion-after'):
                limit=time.monotonic()+60
                while not (self.proof/(name+'-check.json')).exists():
                    if process.poll() is not None or time.monotonic()>=limit:raise RuntimeError('qualification_checkpoint_missing:'+name)
                    time.sleep(.05)
                if name=='pre-enrollment':self.observe('after-protected-check',initial=True)
                elif name=='rename-before':self.snapshot('before-rename')
                elif name=='rename-after':
                    before=self.protected_snapshots['before-rename'];after=self.snapshot('after-rename')
                    expected=json.loads((self.proof/'rename-result.json').read_text())
                    assert before['scribeswell_studies.notes']==after['scribeswell_studies.notes'],'Rename changed acknowledged note rows'
                    old=next(row for row in before['scribeswell_studies.studies'] if row['id']==expected['study'])
                    new=next(row for row in after['scribeswell_studies.studies'] if row['id']==expected['study'])
                    assert old['revision']==1 and new['revision']==2 and new['title']==expected['title']
                    assert new['updated_by']==old['created_by'] and new['updated_at']>old['updated_at']
                    for key in old:
                        if key not in ('title','revision','updated_by','updated_at'):assert new[key]==old[key]
                    previous=before['scribeswell_studies.receipts'];current=after['scribeswell_studies.receipts']
                    assert len(current)==len(previous)+1 and all(row in current for row in previous)
                    receipts=[row for row in current if row['command']=='study.rename']
                    assert len(receipts)==1 and receipts[0]['operation_id']==expected['operation'] and receipts[0]['created_by']==new['updated_by']
                    assert receipts[0]['outcome']['revision']=='2' and receipts[0]['outcome']['note_id'] is None
                elif name=='passages-before':self.snapshot('before-passages')
                elif name=='passages-after':
                    before=self.protected_snapshots['before-passages'];after=self.snapshot('after-passages')
                    expected=json.loads((self.proof/'passages-result.json').read_text())
                    assert before['scribeswell_studies.notes']==after['scribeswell_studies.notes'],'Collection mutated note rows'
                    assert before['scribeswell_studies.studies']==after['scribeswell_studies.studies'],'Collection mutated title rows'
                    headers=after['scribeswell_studies.passage_lists'];entries=after['scribeswell_studies.passage_entries']
                    assert len(headers)==1 and headers[0]['revision']==4 and headers[0]['study_id']==expected['study']
                    assert len(entries)==1 and entries[0]['book_id']=='Matt' and entries[0]['id']==expected['item']['id'] and entries[0]['position']==1
                    assert all(entries[0][key]==expected['item']['reference'][key] for key in ('catalogue_id','catalogue_version','versification_id','book_id'))
                    assert entries[0]['kind']=='verse_range' and (entries[0]['start_chapter'],entries[0]['start_verse'],entries[0]['end_chapter'],entries[0]['end_verse'])==(26,63,26,64)
                    assert entries[0]['created_by']==headers[0]['created_by']==headers[0]['updated_by']
                    assert headers[0]['updated_at']>=headers[0]['created_at'] and entries[0]['created_at']
                    receipts=[row for row in after['scribeswell_studies.receipts'] if row['command']=='study.passages.replace']
                    assert {row['operation_id'] for row in receipts}==set(expected['operations']) and len(receipts)==3
                    assert all(row['created_by']==headers[0]['updated_by'] and row['outcome']['note_id'] is None for row in receipts)
                elif name=='note-links-before':self.snapshot('before-note-links')
                elif name=='note-links-after':
                    before=self.protected_snapshots['before-note-links'];after=self.snapshot('after-note-links')
                    expected=json.loads((self.proof/'note-links-result.json').read_text())
                    for table in ('scribeswell_studies.studies','scribeswell_studies.passage_lists','scribeswell_studies.passage_entries'):
                        assert before[table]==after[table],'Note link changed independent resource'
                    assert_non_target_notes_unchanged(before['scribeswell_studies.notes'],after['scribeswell_studies.notes'],expected['note'])
                    old=next(row for row in before['scribeswell_studies.notes'] if row['id']==expected['note'])
                    new=next(row for row in after['scribeswell_studies.notes'] if row['id']==expected['note'])
                    assert new['value']==expected['value'] and new['value']['document']['version']==2
                    assert new['revision']==old['revision']+1 and new['updated_at']>old['updated_at']
                    assert new['created_at']==old['created_at'] and new['created_by']==old['created_by']==new['updated_by']
                    previous=before['scribeswell_studies.receipts'];current=after['scribeswell_studies.receipts']
                    added=[row for row in current if row not in previous]
                    assert len(current)==len(previous)+1 and len(added)==1
                    assert added[0]['command']=='note.replace' and added[0]['operation_id']==expected['operation']
                elif name=='search-before':self.snapshot('before-library-search')
                elif name=='search-after':self.snapshot('after-library-search',previous='before-library-search')
                elif name=='deletion-before':self.snapshot('before-note-deletion')
                elif name=='deletion-after':
                    before=self.protected_snapshots['before-note-deletion'];after=self.snapshot('after-note-deletion')
                    expected=json.loads((self.proof/'deletion-result.json').read_text())
                    for table in ('scribeswell_studies.studies','scribeswell_studies.passage_lists','scribeswell_studies.passage_entries'):
                        assert before[table]==after[table],'Deletion changed independent resources'
                    assert_non_target_notes_unchanged(before['scribeswell_studies.notes'],after['scribeswell_studies.notes'],expected['note'])
                    old=next(row for row in before['scribeswell_studies.notes'] if row['id']==expected['note'])
                    new=next(row for row in after['scribeswell_studies.notes'] if row['id']==expected['note'])
                    assert not new['active'] and new['value']=={'document':{'version':1,'blocks':[]},'connections':[],'highlights':[]}
                    assert new['revision']==old['revision']+1==int(expected['revision']) and new['updated_at']>old['updated_at']
                    assert new['created_at']==old['created_at'] and new['created_by']==old['created_by']==new['updated_by']
                    added=[row for row in after['scribeswell_studies.receipts'] if row not in before['scribeswell_studies.receipts']]
                    assert len(added)==1 and added[0]['command']=='note.delete' and added[0]['operation_id']==expected['operation']
                    assert set(added[0]['outcome'])=={'operation_id','command','study_id','note_id','revision'}
                elif name=='study-deletion-before':self.snapshot('before-study-deletion')
                elif name=='study-deletion-after':
                    before=self.protected_snapshots['before-study-deletion'];after=self.snapshot('after-study-deletion')
                    expected=json.loads((self.proof/'study-deletion-result.json').read_text());assert_study_erasure(before,after,expected)
                elif name=='foreign-before':self.snapshot('before-foreign-denial')
                else:self.snapshot('after-foreign-denial',previous='before-foreign-denial')
                private(self.proof/(name+'-observed.json'),{'independent_sql':True})
        env={**self.environment,'SCRIBESWELL_OWNER_FIXTURE':str(self.proof/'browser-private.json')}
        self.command('browser',['node',ROOT/'node_modules/@playwright/test/cli.js','test','--config',APP/'web/playwright.owner-integration.config.cjs'],env=env,cwd=APP/'web',timeout=120,on_started=checkpoints)

    def stop_process(self,process):
        forced=False
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        limit=time.monotonic()+3
        while time.monotonic()<limit:
            process.poll()
            if not executing_group_members(process.pid):break
            time.sleep(.05)
        else:
            try:os.killpg(process.pid,signal.SIGKILL);forced=True
            except ProcessLookupError:pass
        process.wait(timeout=5)
        limit=time.monotonic()+1
        while executing_group_members(process.pid):
            if time.monotonic()>=limit:raise OSError('qualification_descendant_termination_unconfirmed')
            time.sleep(.01)
        self.events.append({'stage':'process-stopped','pid':process.pid,'forced':forced,'termination_confirmed':True})

    def execute(self):
        try:
            import importlib.util
            for dependency in ('psycopg','sqlalchemy','alembic','httpx','rfc8785'):
                if importlib.util.find_spec(dependency) is None:raise RuntimeError('qualification_dependency_missing:'+dependency)
            check_ports();self.wrapper('prepare');self.owned=True
            self.wrapper('up');self.wrapper('verify');self.capture_status()
            self.prepare_owners();self.start_apps();self.browser();self.observe('after-browser')
            self.operator('application.set_enabled',{'app_id':'scribeswell','enabled':False,'expected_revision':'2'})
            self.snapshot('before-disabled-denial')
            self.command('browser-denied',['node',ROOT/'node_modules/@playwright/test/cli.js','test','--config',APP/'web/playwright.owner-integration.config.cjs','--grep','disabled'],env={**self.environment,'SCRIBESWELL_OWNER_FIXTURE':str(self.proof/'browser-private.json'),'SCRIBESWELL_OWNER_DENIED':'true'},cwd=APP/'web',timeout=90)
            self.snapshot('after-disabled-denial',previous='before-disabled-denial')
            self.observe('after-denial')
            self.verify_sources()
            self.events.append({'stage':'passed'})
        except BaseException as error:
            import traceback
            private(self.proof/'failure.json',{'type':type(error).__name__,'code':str(error) if type(error) is RuntimeError and str(error).startswith('qualification_') else None,'sqlstate':getattr(error,'sqlstate',None),'frames':[{'file':f.filename,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]})
            self.events.append({'stage':'failed'});raise
        finally:
            cleanup_failed=False
            for process in reversed(self.processes):
                try:self.stop_process(process)
                except (OSError,subprocess.TimeoutExpired):
                    cleanup_failed=True
                    self.events.append({'stage':'process-stop-failed','pid':process.pid})
            if self.owned:
                try:self.wrapper('stop')
                except Exception:self.events.append({'stage':'stop-failed'});cleanup_failed=True
            private(self.proof/'result.json',{'run_id':self.run_id,'events':self.events,'scope':'HTTP/domain integration only; no default readiness, signup, release or device claim'})
            if cleanup_failed:raise RuntimeError('qualification_exact_run_stop_failed')

def qualify():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True);parser.add_argument('--supabase',required=True,type=Path);parser.add_argument('--proof',required=True,type=Path)
    args=parser.parse_args()
    Qualification(args.run_id,args.supabase,args.proof).execute()
