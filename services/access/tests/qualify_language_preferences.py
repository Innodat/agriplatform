"""Explicit disposable Leave language API/PostgreSQL proof, never live discovery."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import sys
from unittest.mock import patch
from uuid import uuid4
import httpx
import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'services/access'))
from main import create_app
from studies_identity import AsyncDatabase
from fastapi.testclient import TestClient
RUN='88a737dd-ad7b-429a-a83c-5d103716d659'

def load(path):
    path=Path(path)
    if path.is_symlink() or path.parent.is_symlink() or stat.S_IMODE(path.stat().st_mode)!=0o600 or path.stat().st_uid!=os.getuid():raise ValueError('fixture_invalid')
    value=json.loads(path.read_bytes())
    if type(value) is not dict or set(value)!={'run_id','database','runtime_url','owner_url','auth_url','anon_key','service_key','accounts'} or value['run_id']!=RUN:raise ValueError('fixture_invalid')
    if value['auth_url']!='http://127.0.0.1:55581':raise ValueError('fixture_invalid')
    if type(value['database']) is not str or not value['database'].startswith('idb_88a737ddad7b_'):raise ValueError('fixture_invalid')
    for key,role in [('runtime_url','identity_preferences_runtime'),('owner_url','identity_migrator')]:
        url=make_url(value[key])
        if (url.drivername,url.host,url.port,url.database,url.username,bool(url.query))!=('postgresql','127.0.0.1',55582,value['database'],role,False):raise ValueError('fixture_invalid')
    if type(value['accounts']) is not dict or set(value['accounts'])!={'a','b'}:raise ValueError('fixture_invalid')
    for account in value['accounts'].values():
        if type(account) is not dict or set(account)!={'id','email','password'}:raise ValueError('fixture_invalid')
    return value

sys.path.insert(0,str(Path(__file__).resolve().parent))
from identity_native_guard import guard

def connect(url):return psycopg.connect(url,connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000')

class Proof:
    def __init__(self,fixture,output):
        self.f=fixture;self.output=Path(output);self.checks=[]
        journal=self.output.with_suffix(self.output.suffix+'.attempts.jsonl')
        self.fd=os.open(journal,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    def record(self,value):
        remaining=memoryview((json.dumps(value,sort_keys=True)+'\n').encode())
        while remaining:
            written=os.write(self.fd,remaining)
            if written<=0:raise OSError('qualification_journal_incomplete')
            remaining=remaining[written:]
        os.fsync(self.fd)
    def stage(self,label):self.checks.append(label);self.record({'stage':label,'status':'passed'})
    def count(self):
        with connect(self.f['owner_url']) as c:
            return dict(zip(('preferences','outcomes','actors','people','members'),c.execute('SELECT (SELECT count(*) FROM identity.account_language_preference),(SELECT count(*) FROM identity.language_preference_outcome),(SELECT count(*) FROM identity.actor),(SELECT count(*) FROM identity.person),(SELECT count(*) FROM identity.org_member)').fetchone()))
    def request(self,client,method,headers,body=None,expected=200):
        self.record({'method':method,'operation_id':body.get('operation_id') if body else None,'expected':expected,'status':'attempting'})
        r=client.request(method,'/v2/me/preferences/language',headers=headers,json=body) if body is not None else client.request(method,'/v2/me/preferences/language',headers=headers)
        assert r.status_code==expected,'preference_http_status_'+str(r.status_code)
        assert r.headers['cache-control']=='private, no-store'
        self.record({'method':method,'status':'completed','http_status':r.status_code,'operation_id':body.get('operation_id') if body else None})
        return r.json()
    def run(self):
        tokens={}
        for label,account in self.f['accounts'].items():
            r=httpx.post(self.f['auth_url']+'/auth/v1/token?grant_type=password',headers={'apikey':self.f['anon_key']},json={'email':account['email'],'password':account['password']},timeout=5)
            assert r.status_code==200 and r.json()['user']['id']==account['id']
            tokens[label]=r.json()['access_token']
        initial=self.count();assert initial['preferences']==0 and initial['outcomes']==0 and initial['people']==0 and initial['members']==0
        env={'SUPABASE_URL':self.f['auth_url'],'SUPABASE_ANON_KEY':self.f['anon_key'],'IDENTITY_PREFERENCES_SERVICE_KEY':self.f['service_key']}
        with patch.dict(os.environ,env):
            with TestClient(create_app(db=object(),preferences_db=AsyncDatabase(self.f['runtime_url']))) as client:
                headers={name:{'Authorization':'Bearer '+token,'X-Service-Key':self.f['service_key']} for name,token in tokens.items()}
                a,b=headers['a'],headers['b']
                assert self.request(client,'GET',a)=={'preferred_locale':'en','revision':'0'}
                assert self.request(client,'GET',b)=={'preferred_locale':'en','revision':'0'}
                self.stage('actual-local-auth-and-known-preference-absence')
                body={'operation_id':str(uuid4()),'expected_revision':'0','preferred_locale':'pt'}
                assert self.request(client,'PUT',a,body)=={'preferred_locale':'pt','revision':'1'}
                assert self.request(client,'PUT',a,body)=={'preferred_locale':'pt','revision':'1'}
                assert self.request(client,'PUT',a,{**body,'preferred_locale':'en'},409)=={'detail':{'code':'identity.preference_operation_conflict'}}
                assert self.request(client,'PUT',a,{**body,'operation_id':str(uuid4())},409)=={'detail':{'code':'identity.preference_revision_conflict'}}
                assert self.request(client,'GET',b)=={'preferred_locale':'en','revision':'0'}
                for org in (str(uuid4()),str(uuid4())):
                    assert self.request(client,'GET',{**a,'X-Org-Id':org})=={'preferred_locale':'pt','revision':'1'}
                self.request(client,'PUT',a,{**body,'account_id':self.f['accounts']['b']['id']},422)
                self.stage('desired-portuguese-retry-conflict-account-isolation-and-org-independence')
                race=[{'operation_id':str(uuid4()),'expected_revision':'1','preferred_locale':'pt'} for _ in range(2)]
                for item in race:self.record({'stage':'race','status':'attempting','operation_id':item['operation_id']})
                with ThreadPoolExecutor(max_workers=2) as pool:
                    responses=list(pool.map(lambda item:client.put('/v2/me/preferences/language',headers=a,json=item),race))
                assert sorted(r.status_code for r in responses)==[200,409]
                assert next(r for r in responses if r.status_code==409).json()=={'detail':{'code':'identity.preference_revision_conflict'}}
                assert self.request(client,'GET',a)=={'preferred_locale':'pt','revision':'2'}
                self.stage('concurrent-same-revision-one-write')
                self.failure(client,a)
                assert self.request(client,'GET',a)=={'preferred_locale':'pt','revision':'2'}
                change={'operation_id':str(uuid4()),'expected_revision':'2','preferred_locale':'en'}
                assert self.request(client,'PUT',a,change)=={'preferred_locale':'en','revision':'3'}
                assert self.request(client,'GET',a)=={'preferred_locale':'en','revision':'3'}
                self.stage('successful-persisted-portuguese-to-english-transition')
                # Original outcome remains resolvable after later successful changes.
                assert self.request(client,'PUT',a,body)=={'preferred_locale':'pt','revision':'1'}
                assert self.request(client,'GET',a)=={'preferred_locale':'en','revision':'3'}
                self.request(client,'GET',{'Authorization':'Bearer invalid','X-Service-Key':self.f['service_key']},expected=401)
                self.request(client,'GET',{'Authorization':a['Authorization'],'X-Service-Key':'wrong'},expected=403)
                self.stage('lost-response-original-outcome-and-current-authentication')
        self.boundaries()
        after=self.count();assert after['preferences']==1 and after['outcomes']==3
        assert all(after[name]==initial[name] for name in ('actors','people','members'))
        self.stage('no-implicit-person-actor-employment-membership-or-grants')
        return {'status':'passed','run_id':RUN,'database':self.f['database'],'checks':self.checks,'source_sha256':{str((ROOT/name).relative_to(ROOT)):sha256((ROOT/name).read_bytes()).hexdigest() for name in ('services/access/main.py','services/access/identity_preferences.py','services/access/identity-migrations/versions/0023_language_preferences.py','services/access/tests/qualify_language_preferences.py')}}
    def failure(self,client,headers):
        trigger='test_language_failure_'+uuid4().hex[:8]
        before=self.count();body={'operation_id':str(uuid4()),'expected_revision':'2','preferred_locale':'en'}
        self.record({'stage':'outcome-failure','operation_id':body['operation_id'],'status':'preparing-trigger','trigger':trigger})
        with connect(self.f['owner_url']) as c:
            c.execute(sql.SQL("CREATE FUNCTION identity.{}() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION USING ERRCODE='IP999',MESSAGE='synthetic_outcome_failure'; END $$").format(sql.Identifier(trigger)))
            c.execute(sql.SQL('CREATE TRIGGER {} BEFORE INSERT ON identity.language_preference_outcome FOR EACH STATEMENT EXECUTE FUNCTION identity.{}()').format(sql.Identifier(trigger),sql.Identifier(trigger)))
        try:
            value=self.request(client,'PUT',headers,body,503)
            assert value=={'detail':{'code':'identity.preference_unavailable'}}
            assert self.count()==before
        finally:
            with connect(self.f['owner_url']) as c:
                c.execute(sql.SQL('DROP TRIGGER {} ON identity.language_preference_outcome').format(sql.Identifier(trigger)))
                c.execute(sql.SQL('DROP FUNCTION identity.{}()').format(sql.Identifier(trigger)))
            self.record({'stage':'outcome-failure','status':'trigger-restored','trigger':trigger})
        self.stage('required-outcome-failure-rolls-back-preference-write')
    def boundaries(self):
        for statement in ('SELECT * FROM identity.account_language_preference','SELECT * FROM identity.language_preference_outcome','SELECT * FROM identity.alembic_version','CREATE TABLE identity.forbidden_language_probe(id integer)'):
            with connect(self.f['runtime_url']) as c:
                try:c.execute(statement)
                except psycopg.Error as error:
                    assert error.sqlstate=='42501';c.rollback()
                else:raise AssertionError('preference_runtime_permission_denial_missing')
        with connect(self.f['runtime_url']) as c:
            c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true),set_config('request.jwt.claims',%s,true)",(self.f['accounts']['b']['id'],json.dumps({'sub':self.f['accounts']['a']['id'],'role':'admin'})))
            assert c.execute('SELECT preferred_locale,revision FROM identity.read_account_language()').fetchone()==('en',0)
        self.stage('restricted-runtime-denials-and-forged-jwt-cannot-switch-account')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    proof=None;output=None
    try:
        if not __debug__:raise ValueError('optimized_python_prohibited')
        output=os.fdopen(os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')
        fixture=load(args.fixture);guard();proof=Proof(fixture,args.output);value=proof.run()
        json.dump(value,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
        Path(args.output).chmod(0o600)
        print(json.dumps({'status':'passed','checks':len(value['checks'])}));return 0
    except Exception as error:
        import traceback
        if proof is not None:proof.record({'status':'failed','class':type(error).__name__,'locations':[(Path(f.filename).name,f.lineno) for f in traceback.extract_tb(error.__traceback__) if str(ROOT/'services/access') in f.filename]})
        print(json.dumps({'status':'failed','code':'language_qualification_requires_reconciliation','class':type(error).__name__}));return 2
    finally:
        if proof is not None:os.close(proof.fd)
        if output is not None:output.close()

if __name__=='__main__':raise SystemExit(main())
