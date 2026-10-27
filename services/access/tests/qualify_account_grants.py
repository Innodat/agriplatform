"""Native controlled-account proof on one explicit root-prepared Leave fixture.

Never creates databases, roles, Auth users, authority, references or application setup.
The root supplies a fresh isolated fixture and retains earlier frames on failure.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import threading
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'services/access'))
sys.path.insert(0,str(Path(__file__).parent))
import psycopg
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool
from access_operator import execute,outcome,canonical_command
from access_operator_input import parse_command
from identity_operator import OperatorError
from identity_native_guard import guard,RUN

REQUIRED={'database','port','run_id','container','network','operator_url','runtime_url','migrator_url','identity_migrator_url','account_id','other_account_id','executor_actor_id','permission','org_permission','org_id','membership_id','target_file'}
OPTIONAL={'inactive_account_id','replacement_account_id','same_person_account_id'}

def load(path):
    path=Path(path)
    if path.is_symlink() or path.parent.is_symlink() or stat.S_IMODE(path.stat().st_mode)!=0o600 or path.stat().st_uid!=os.getuid():raise ValueError('fixture_invalid')
    value=json.loads(path.read_bytes())
    if type(value) is not dict or not REQUIRED<=set(value) or set(value)-REQUIRED-OPTIONAL:raise ValueError('fixture_invalid')
    if value['run_id']!=RUN or value['port']!=55582 or re.fullmatch('aca_88a737ddad7b_[0-9a-f]{8}',value['database']) is None:raise ValueError('fixture_invalid')
    for key,role in [('operator_url','access_operator'),('runtime_url','access_runtime'),('migrator_url','access_migrator'),('identity_migrator_url','identity_migrator')]:
        url=make_url(value[key])
        if (url.drivername,url.host,url.port,url.database,url.username,bool(url.query))!=('postgresql','127.0.0.1',55582,value['database'],role,False):raise ValueError('fixture_invalid')
    return value

def engine(url):return create_engine(make_url(url).set(drivername='postgresql+psycopg'),poolclass=NullPool,hide_parameters=True,connect_args=dict(connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000'))

def write_all(fd,data):
    remaining=memoryview(data)
    while remaining:
        written=os.write(fd,remaining)
        if written<=0:raise OSError('evidence_write_incomplete')
        remaining=remaining[written:]
    os.fsync(fd)


class Proof:
    def __init__(self,f,output):
        self.f=f;self.output=Path(output);self.checks=[];self.operation_ids=[];self.committed={};self.refused=set();self.journal_lock=threading.Lock()
        self.fd=os.open(str(output)+'.attempts.jsonl',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    def record(self,value):
        data=memoryview((json.dumps(value,sort_keys=True)+'\n').encode())
        with self.journal_lock:
            write_all(self.fd,data)
    def stage(self,name):self.checks.append(name);self.record(dict(stage=name,status='passed'))
    def command(self,name='account_grant.assign',account=None,**payload):
        operation=str(uuid4());self.operation_ids.append(operation)
        return dict(schema_version=1,operation_id=operation,command=name,scope=dict(kind='platform'),payload=dict(account_id=account or self.f['account_id'],permission=self.f['permission'],**payload),reason_code='synthetic_fixture')
    def run_command(self,doc,expected=None):
        self.record(dict(operation_id=doc['operation_id'],command=doc['command'],status='attempting',expected=expected or 'committed'))
        e=engine(self.f['operator_url'])
        try:
            with e.connect() as c:
                assert c.execute(text('SELECT session_user,current_user')).one()==('access_operator','access_operator');c.rollback()
                try:r=execute(c,json.dumps(doc).encode())
                except OperatorError as error:
                    assert error.code==expected,'unexpected_operator_refusal_'+error.code
                    self.refused.add(doc['operation_id'])
                    self.record(dict(operation_id=doc['operation_id'],status='refused',code=error.code));return None
            assert expected is None,'unexpected_operator_success'
            self.accept(doc,asdict(r.result))
            return r
        finally:e.dispose()
    def accept(self,doc,result):
        result=dict(result);result.pop('command',None)
        target=result['target'];payload=doc['payload']
        assert set(target)=={'grant_id','account_id','permission'}
        assert target['account_id']==payload['account_id'] and target['permission']==payload['permission']
        if 'grant_id' in payload:assert target['grant_id']==payload['grant_id']
        expected=dict(command=doc['command'],result=result)
        if doc['operation_id'] in self.committed:assert self.committed[doc['operation_id']]==expected
        self.committed[doc['operation_id']]=expected
        self.record(dict(operation_id=doc['operation_id'],status='committed',disposition=result['disposition'],revision=result['revision']))
    def concurrent_revoke(self,race):
        pids={};pid_lock=threading.Lock()
        def attempt(doc):
            self.record(dict(operation_id=doc['operation_id'],command=doc['command'],status='attempting',stage='concurrent-revoke'))
            e=engine(self.f['operator_url'])
            try:
                with e.connect() as c:
                    pid=c.execute(text('SELECT pg_backend_pid()')).scalar_one();c.rollback()
                    with pid_lock:pids[doc['operation_id']]=pid
                    try:return execute(c,json.dumps(doc).encode())
                    except OperatorError as error:return error.code
            finally:e.dispose()
        holder=psycopg.connect(self.f['migrator_url'],connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000')
        try:
            holder.execute('SELECT pg_advisory_xact_lock(access.command_lock(%s))',('access:account-grant:v1:'+self.f['account_id']+':'+self.f['permission'],))
            with ThreadPoolExecutor(max_workers=2) as pool:
                tasks=[pool.submit(attempt,doc) for doc in race]
                try:
                    deadline=time.monotonic()+1.5
                    while True:
                        with pid_lock:waiting_pids=list(pids.values())
                        waiting=holder.execute("SELECT DISTINCT pid FROM pg_locks WHERE locktype='advisory' AND NOT granted AND pid=ANY(%s)",(waiting_pids,)).fetchall() if len(waiting_pids)==2 else []
                        if len(waiting)==2:break
                        assert time.monotonic()<deadline,'concurrent_attempts_not_both_waiting'
                        time.sleep(.02)
                    self.record(dict(stage='concurrent-revoke',status='both-waiting',operations=[doc['operation_id'] for doc in race]))
                finally:holder.rollback()
                results=[task.result(timeout=15) for task in tasks]
        finally:holder.rollback();holder.close()
        for doc,result in zip(race,results):
            if isinstance(result,str):
                self.refused.add(doc['operation_id']);self.record(dict(operation_id=doc['operation_id'],status='refused',code=result))
            else:self.accept(doc,asdict(result.result))
        return results
    def expired_assignment(self,doc,grant):
        before=self.owner('SELECT revision,revoked_at FROM access.account_grants WHERE id=%s',(grant,))
        self.record(dict(stage='deferred-observation-expiry',operation_id=doc['operation_id'],status='attempting'))
        c=psycopg.connect(self.f['operator_url'],connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000')
        try:
            assert c.execute('SELECT session_user,current_user').fetchone()==('access_operator','access_operator')
            payload=doc['payload']
            row=c.execute('SELECT * FROM access.change_account_grant(%s,%s,%s,%s,%s,false,%s,%s,NULL,%s)',(doc['operation_id'],doc['command'],payload['account_id'],payload['permission'],payload['grant_id'],payload['expected_revision'],doc['reason_code'],canonical_command(parse_command(json.dumps(doc).encode())))).fetchone()
            assert row and row[0]['disposition']=='changed' and row[0]['event_id'] is not None
            self.record(dict(stage='deferred-observation-expiry',operation_id=doc['operation_id'],status='returned-before-commit'))
            time.sleep(5.1)
            try:c.commit()
            except psycopg.Error as error:
                assert error.sqlstate=='AC004','unexpected_deferred_expiry_state'
                self.refused.add(doc['operation_id']);self.record(dict(stage='deferred-observation-expiry',operation_id=doc['operation_id'],status='commit-refused',sqlstate=error.sqlstate))
            else:raise AssertionError('expired_observation_commit_succeeded')
        finally:c.rollback();c.close()
        assert self.owner('SELECT revision,revoked_at FROM access.account_grants WHERE id=%s',(grant,))==before
        assert self.owner('SELECT count(*) FROM access.operation_outcome WHERE operation_id=%s',(doc['operation_id'],))==[(0,)]
        assert self.owner('SELECT count(*) FROM access.business_event WHERE operation_id=%s',(doc['operation_id'],))==[(0,)]
        self.stage('post-return-observation-expiry-rolls-back-grant-outcome-and-event')
        return self.run_command(doc)
    def deactivated_retry(self,doc,receipt):
        account=doc['payload']['account_id']
        c=psycopg.connect(self.f['identity_migrator_url'],connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000')
        original=None;changed=False
        try:
            actor=c.execute('SELECT actor_id::text FROM identity.account_actor WHERE account_id=%s',(account,)).fetchone()
            assert actor is not None
            def context():
                c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true),set_config('app.actor_id',%s,true),set_config('app.org_id','',true),set_config('request.jwt.claims',%s,true),set_config('request.jwt.claim.sub',%s,true),set_config('request.jwt.claim.role','authenticated',true)",(account,actor[0],json.dumps(dict(sub=account,role='authenticated')),account))
            context();row=c.execute('SELECT deleted_at FROM identity.users WHERE id=%s',(account,)).fetchone();assert row is not None;original=row[0]
            assert original is None
            assert c.execute('UPDATE identity.users SET deleted_at=statement_timestamp() WHERE id=%s',(account,)).rowcount==1
            c.commit();changed=True
            self.record(dict(stage='deactivated-exact-assignment-retry',operation_id=doc['operation_id'],status='profile-deactivated'))
            assert self.run_command(doc)==receipt
            self.run_command(dict(doc,reason_code='setup_correction'),'operation_conflict')
            self.stage('committed-exact-assignment-retry-survives-deactivation')
        finally:
            c.rollback()
            if changed:
                context()
                assert c.execute('UPDATE identity.users SET deleted_at=%s WHERE id=%s',(original,account)).rowcount==1
                c.commit()
                self.record(dict(stage='deactivated-exact-assignment-retry',status='profile-restored'))
            c.close()
    def verify_cardinality(self):
        all_operations=set(self.operation_ids)|set(self.committed)|self.refused
        rows=self.owner('SELECT id::text,operation_id::text,command_type,result,executor_actor_id::text,scope_kind,scope_id FROM access.operation_outcome WHERE operation_id=ANY(%s::uuid[])',(list(all_operations),))
        assert len(rows)==len(self.committed) and {row[1] for row in rows}==set(self.committed),'exact_committed_outcome_set_mismatch'
        outcome_ids={}
        for oid,operation,command,result,executor,scope,scope_id in rows:
            expected=self.committed[operation]
            assert (command,result,executor,scope,scope_id)==(expected['command'],expected['result'],self.f['executor_actor_id'],'platform',None)
            outcome_ids[operation]=oid
        events=self.owner('SELECT event_id::text,operation_id::text,outcome_id::text,event_type,target,executor_actor_id::text,scope_kind,scope_id,event_version FROM access.business_event WHERE operation_id=ANY(%s::uuid[])',(list(all_operations),))
        expected_events={expected['result']['event_id']:operation for operation,expected in self.committed.items() if expected['result']['event_id'] is not None}
        assert len(events)==len(expected_events) and {row[0] for row in events}==set(expected_events),'exact_committed_event_set_mismatch'
        for event,operation,oid,kind,target,executor,scope,scope_id,version in events:
            expected=self.committed[operation]
            assert expected_events[event]==operation and oid==outcome_ids[operation]
            assert (target,executor,scope,scope_id,version)==(expected['result']['target'],self.f['executor_actor_id'],'platform',None,1)
            assert kind==('access.account_grant_assigned' if expected['command']=='account_grant.assign' else 'access.account_grant_revoked')
        assert not ({row[1] for row in rows}&(self.refused-set(self.committed)))
    def owner(self,query,parameters=()):
        with psycopg.connect(self.f['migrator_url'],connect_timeout=3) as c:return c.execute(query,parameters).fetchall()
    def denial(self,url,query,parameters=()):
        with psycopg.connect(url,connect_timeout=3) as c:
            try:c.execute(query,parameters)
            except psycopg.Error as error:
                assert error.sqlstate in ('42501','23514','AC002'),'unexpected_native_denial_state';return
            raise AssertionError('native_denial_missing')
    def run(self):
        first=self.command(expected_absent=True);created=self.run_command(first)
        assert created.result.disposition=='created' and created.result.revision=='1'
        grant=created.result.target.grant_id
        assert self.run_command(first)==created
        self.run_command({**first,'reason_code':'setup_correction'},'operation_conflict')
        self.run_command(self.command(expected_absent=True),'operation_conflict')
        unchanged=self.run_command(self.command(grant_id=grant,expected_revision='1'))
        assert unchanged.result.disposition=='unchanged' and unchanged.result.event_id is None
        reused=dict(first,command='account_grant.revoke',payload=dict(account_id=self.f['account_id'],permission=self.f['permission'],grant_id=grant,expected_revision='1'))
        self.run_command(reused,'operation_conflict')
        self.stage('create-exact-retry-input-and-cross-command-conflict-absence-and-unchanged')
        self.run_command(self.command(grant_id=str(uuid4()),expected_revision='1'),'operation_conflict')
        self.run_command(self.command(grant_id=grant,expected_revision='2'),'operation_conflict')
        # Real concurrent revisions: one revoke changes, the other is stale.
        race=[self.command('account_grant.revoke',grant_id=grant,expected_revision='1') for _ in range(2)]
        results=self.concurrent_revoke(race)
        assert sum(not isinstance(r,str) for r in results)==1 and 'operation_conflict' in results
        changed=next(r for r in results if not isinstance(r,str));assert changed.result.revision=='2'
        winner=next(doc for doc,r in zip(race,results) if not isinstance(r,str))
        assert self.run_command(winner)==changed
        e=engine(self.f['operator_url'])
        try:
            with e.connect() as c:
                try:outcome(c,winner['operation_id'],command='account_grant.revoke',account_id=self.f['account_id'],permission=self.f['permission'],grant_id=str(uuid4()))
                except OperatorError as error:assert error.code=='access_denied'
                else:raise AssertionError('wrong_grant_receipt_disclosed')
                assert outcome(c,winner['operation_id'],command='account_grant.revoke',account_id=self.f['account_id'],permission=self.f['permission'],grant_id=grant)==changed
        finally:e.dispose()
        self.stage('concurrent-exact-revision-single-revoke-retry-and-authorized-wrong-grant-denial')
        regrant=self.expired_assignment(self.command(grant_id=grant,expected_revision='2'),grant)
        assert regrant.result.disposition=='changed' and regrant.result.revision=='3' and regrant.result.target.grant_id==grant
        assert self.run_command(winner)==changed
        self.run_command(self.command('account_grant.revoke',grant_id=grant,expected_revision='2'),'operation_conflict')
        self.deactivated_retry(first,created)
        self.stage('retained-id-regrant-and-delayed-revoke-protection')
        # Selected other account must not be exposed by receipt lookup, including
        # a reused connection whose previous call installed transaction context.
        e=engine(self.f['operator_url'])
        try:
            with e.connect() as c:
                assert outcome(c,first['operation_id'],command=first['command'],account_id=self.f['account_id'],permission=self.f['permission'])==created
                try:outcome(c,first['operation_id'],command=first['command'],account_id=self.f['other_account_id'],permission=self.f['permission'])
                except OperatorError as error:assert error.code=='access_denied'
                else:raise AssertionError('foreign_outcome_disclosed')
                assert c.execute(text("SELECT nullif(current_setting('app.target_account_id',true),'') IS NULL")).scalar_one();c.rollback()
        finally:e.dispose()
        self.stage('scoped-outcome-and-connection-reuse-context-reset')
        self.denial(self.f['runtime_url'],'CREATE TABLE access.account_grant_forbidden(id integer)')
        with psycopg.connect(self.f['runtime_url'],connect_timeout=3) as c:
            assert c.execute('SELECT session_user,current_user').fetchone()==('access_runtime','access_runtime')
            assert c.execute('SELECT id FROM access.account_grants').fetchall()==[];c.commit()
            c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true)",(self.f['account_id'],))
            assert c.execute('SELECT id::text,account_id::text FROM access.account_grants').fetchall()==[(grant,self.f['account_id'])];c.commit()
            assert c.execute('SELECT id FROM access.account_grants').fetchall()==[];c.rollback()
            c.execute("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',%s,true)",(self.f['other_account_id'],))
            assert c.execute('SELECT id FROM access.account_grants').fetchall()==[];c.rollback()
            assert c.execute('SELECT id FROM access.account_grants').fetchall()==[]
        self.denial(self.f['runtime_url'],'UPDATE access.account_grants SET revoked_at=statement_timestamp()')
        self.stage('forced-rls-own-account-read-commit-rollback-and-pooled-context-reset')
        self.denial(self.f['runtime_url'],'SELECT * FROM access.account_grant_outcome(%s,%s,%s,%s,NULL)',(first['operation_id'],first['command'],self.f['account_id'],self.f['permission']))
        self.denial(self.f['operator_url'],'SELECT * FROM identity.account_grant_target(%s)',(self.f['account_id'],))
        self.denial(self.f['operator_url'],'UPDATE access.account_grants SET revoked_at=statement_timestamp() WHERE id=%s',(grant,))
        self.stage('actual-original-runtime-and-operator-direct-permission-denials')
        mismatch=self.command(expected_absent=True);mismatch['payload']['permission']=self.f['org_permission']
        self.run_command(mismatch,'access_denied')
        foreign=self.command(account=self.f['other_account_id'],expected_absent=True)
        self.run_command(foreign,'access_denied')
        self.stage('organization-scope-mismatch-and-exact-target-authority')
        for key in ('same_person_account_id','replacement_account_id'):
            if key in self.f:
                # Explicit exact authority for these accounts is fixture-owned.
                other=self.run_command(self.command(account=self.f[key],expected_absent=True))
                assert other.result.target.account_id==self.f[key] and other.result.target.grant_id!=grant
                self.stage(key+'-independent-grant')
        if 'inactive_account_id' in self.f:
            self.run_command(self.command(account=self.f['inactive_account_id'],expected_absent=True),'operation_verification_unavailable')
            self.stage('inactive-account-assignment-refused')
        # CLI executes the next exact state transition in the isolated child.
        cli=self.command('account_grant.revoke',grant_id=grant,expected_revision='3')
        command_path=self.output.with_suffix('.command.json');write_all(self.command_fd,(json.dumps(cli)+'\n').encode())
        os.close(self.command_fd);self.command_fd=None
        child=subprocess.run([sys.executable,'-I','-B',str(ROOT/'services/access/operator_cli.py'),'execute','--owner','access','--target',self.f['target_file'],'--command-file',str(command_path)],capture_output=True,timeout=20,env={'PATH':'/usr/bin:/bin'})
        assert child.returncode==0,'isolated_cli_failed'
        response=json.loads(child.stdout);assert response['operation_id']==cli['operation_id'] and response['result']['revision']=='4'
        self.accept(cli,response['result'])
        recovered=subprocess.run([sys.executable,'-I','-B',str(ROOT/'services/access/operator_cli.py'),'outcome','--owner','access','--target',self.f['target_file'],'--operation-id',cli['operation_id'],'--command','account_grant.revoke','--account-id',self.f['account_id'],'--permission',self.f['permission'],'--grant-id',grant],capture_output=True,timeout=20,env={'PATH':'/usr/bin:/bin'})
        assert recovered.returncode==0 and json.loads(recovered.stdout)==response,'isolated_cli_recovery_failed'
        self.stage('isolated-cli-exact-transition-and-same-operation-outcome-recovery')
        self.verify_cardinality()
        assert self.owner('SELECT revision,revoked_at IS NOT NULL,created_by::text,updated_by::text FROM access.account_grants WHERE id=%s',(grant,))==[(4,True,self.f['executor_actor_id'],self.f['executor_actor_id'])]
        self.stage('exact-outcome-event-cardinality-and-server-provenance')
        return self.checks

def main():
    if not __debug__:raise ValueError('access_qualification_optimized_python_prohibited')
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    proof=None;command_fd=None
    try:
        with os.fdopen(fd,'w') as file:
            file.write('{"status":"incomplete"}\n');file.flush();os.fsync(file.fileno())
            command_fd=os.open(Path(args.output).with_suffix('.command.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            proof=Proof(None,args.output);proof.command_fd=command_fd
            target,run=guard();f=load(args.fixture)
            import dev,native_cli
            project=dev.project_identity(target,RUN);network=native_cli.network(target,RUN,False,run)
            if f['container']!='supabase_db_'+project or f['network']!=network:raise ValueError('fixture_target_invalid')
            proof.f=f
            checks=proof.run()
            result=dict(status='passed',checks=checks,fixture_sha256=sha256(Path(args.fixture).read_bytes()).hexdigest(),sources={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in (ROOT/'services/access/access_operator.py',ROOT/'services/access/access_operator_input.py',Path(__file__))})
            file.seek(0);json.dump(result,file,indent=2);file.write('\n');file.truncate();file.flush();os.fsync(file.fileno())
    finally:
        if proof is not None:
            os.close(proof.fd)
            if proof.command_fd is not None:os.close(proof.command_fd)
        elif command_fd is not None:os.close(command_fd)
if __name__=='__main__':main()
