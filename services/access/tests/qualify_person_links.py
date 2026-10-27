"""Native person/link proof against an explicitly root-prepared disposable fixture.

No credential discovery, infrastructure creation, Auth mutation or reference recording.
The fixture is private and contains only synthetic retained/recreated cohorts. Root owns
migration/release transitions and calls this module after independently rehearsing them.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import threading
import traceback
from uuid import UUID,uuid4
from sqlalchemy import create_engine,text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

APPROVED_RUN='88a737dd-ad7b-429a-a83c-5d103716d659'
APPROVED_PORT=55582
OWNER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(OWNER))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import identity_operator as operator
from identity_native_guard import guard,DATABASE_PREFIX


def load_fixture(path,run_id,port):
    """Closed caller-selected fixture with exact target/login binding, never discovery."""
    if run_id!=APPROVED_RUN or type(port) is not int or port!=APPROVED_PORT:
        raise ValueError('qualification_target_not_approved')
    path=Path(path).absolute()
    if path.is_symlink() or path.parent.is_symlink():raise ValueError('qualification_fixture_invalid')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or info.st_uid!=os.getuid() or info.st_size>65536:
            raise ValueError('qualification_fixture_invalid')
        with os.fdopen(os.dup(fd),'rb') as file:value=json.load(file)
    finally:os.close(fd)
    required={'run_id','port','database','owner_url','operator_url','runtime_url','cohorts','cli_target'}
    if type(value) is not dict or set(value)!=required or value['run_id']!=str(UUID(run_id)) or value['port']!=port:
        raise ValueError('qualification_fixture_invalid')
    if type(value['database']) is not str or not value['database'].startswith(DATABASE_PREFIX):raise ValueError('qualification_database_invalid')
    for key,login in [('owner_url','identity_migrator'),('operator_url','identity_operator'),('runtime_url','access_runtime')]:
        url=make_url(value[key])
        if (url.drivername,url.username,url.host,url.port,url.database,bool(url.query))!=('postgresql',login,'127.0.0.1',port,value['database'],False):
            raise ValueError('qualification_target_invalid')
    cohorts=value['cohorts']
    if type(cohorts) is not dict or set(cohorts)!={'retained','second','recreated','inactive','unlinked','missing_actor','foreign_target'}:
        raise ValueError('qualification_cohort_invalid')
    for name,cohort in cohorts.items():
        if type(cohort) is not dict or set(cohort)!={'account_id','actor_id'}:raise ValueError('qualification_cohort_invalid')
        for field,item in cohort.items():
            if name=='missing_actor' and field=='actor_id' and item is None:continue
            if type(item) is not str or not UUID(item).int or str(UUID(item))!=item:raise ValueError('qualification_cohort_invalid')
    if len({c['account_id'] for c in cohorts.values()})!=7 or len({c['actor_id'] for c in cohorts.values() if c['actor_id'] is not None})!=6:
        raise ValueError('qualification_cohort_invalid')
    import re
    cli=Path(value['cli_target'])
    expected=OWNER.parents[1]/'platform/deployment/.local/leave'/APPROVED_RUN
    match=re.fullmatch(r'identity-operator-([0-9a-f]{8})\.json',cli.name)
    if not cli.is_absolute() or cli.parent!=expected or match is None or value['database']!=DATABASE_PREFIX+match.group(1):raise ValueError('qualification_cli_target_invalid')
    return value


def require_permission_denial(connection,statement):
    """A SQL/constraint/transport failure never proves a privilege boundary."""
    try:
        connection.execute(text(statement))
    except Exception as error:
        connection.rollback()
        if getattr(getattr(error,'orig',error),'sqlstate',None)!='42501':
            raise
    else:
        raise AssertionError('qualification_runtime_boundary_failed')


class Qualification:
    def __init__(self,fixture,journal=None):
        self.fixture=fixture;self.checks=[];self.receipts=[];self.journal=journal;self._guarded=False;self.expected_person={}
    def record(self,**value):
        if self.journal is not None:self.journal(value)
    def engine(self,key):
        url=make_url(self.fixture[key])
        roles={'owner_url':'identity_migrator','operator_url':'identity_operator','runtime_url':'access_runtime','legacy_probe_url':'identity_legacy_probe_runtime'}
        if (key not in roles or url.drivername!='postgresql' or url.username!=roles[key] or url.host!='127.0.0.1'
            or url.port!=APPROVED_PORT or url.database!=self.fixture['database'] or not url.database.startswith(DATABASE_PREFIX) or url.query):
            raise ValueError('qualification_target_invalid')
        if not self._guarded:
            guard();self._guarded=True
        return create_engine(url.set(drivername='postgresql+psycopg'),poolclass=NullPool,
            hide_parameters=True,connect_args=dict(connect_timeout=3,options='-c statement_timeout=5000 -c lock_timeout=2000'))
    def sql(self,statement,params=None,key='owner_url'):
        db=self.engine(key)
        try:
            with db.begin() as connection:return connection.execute(text(statement),params or {}).all() if statement.lstrip().upper().startswith('SELECT') else connection.execute(text(statement),params or {})
        finally:db.dispose()
    def invoke(self,value,lookup=False,key='operator_url'):
        reference=dict(stage='outcome' if lookup else 'execute',command=value['command'],operation_id=value['operation_id'],
            target={name:value['payload'][name] for name in ('account_id','person_id','actor_id') if name in value['payload']},
            credential_kind=key)
        self.record(status='attempting',**reference)
        db=self.engine(key)
        try:
            with db.connect() as connection:
                expected=make_url(self.fixture[key]).username
                assert tuple(connection.execute(text('SELECT session_user,current_user')).one())==(expected,expected)
                connection.rollback()
                if lookup:receipt=operator.outcome(connection,value['operation_id'],command=value['command'],person_id=value['payload']['person_id'],
                    **(dict(account_id=value['payload']['account_id']) if value['command']=='account.link_person' else {}))
                else:receipt=operator.execute(connection,json.dumps(value,separators=(',',':')).encode())
                self.record(status='committed' if receipt is not None else 'unresolved',**reference)
                return receipt
        except Exception as error:
            self.record(status='failed',diagnostic=safe_diagnostic(error),**reference)
            raise
        finally:db.dispose()
    def value(self,person,cohort=None):
        return dict(schema_version=1,operation_id=str(uuid4()),command='person.create' if cohort is None else 'account.link_person',
            scope=dict(kind='platform'),payload=dict(person_id=person,expected_absent=True,**(cohort or {})),
            reason_code='synthetic_fixture',evidence_ref='synthetic:person-proof')
    def denied(self,value,key='operator_url',code=None,lookup=False):
        try:self.invoke(value,lookup,key)
        except operator.OperatorError as error:
            if code is not None:assert error.code==code,error.code
            return error.code
        raise AssertionError('qualification_expected_denial')
    def state(self):
        self.record(stage='state-counts',status='attempting')
        # Compact IDs/evidence only; no profile, documents or credentials in output.
        return {table:self.sql('SELECT count(*) FROM identity.'+table)[0][0] for table in ('person','account_person','actor','account_actor','org_member','operation_outcome','business_event')}
    def run(self):
        self.setup_projections()
        before=self.state();person=str(uuid4());create=self.value(person)
        receipt=self.invoke(create);assert receipt.result.disposition=='created'
        assert self.invoke(create)==receipt and self.invoke(create,True)==receipt
        unchanged=deepcopy(create);unchanged['operation_id']=str(uuid4())
        assert self.invoke(unchanged).result.disposition=='unchanged'
        changed=deepcopy(create);changed['payload']['person_id']=str(uuid4())
        self.denied(changed,code='operation_conflict')
        wrong=deepcopy(create);wrong['payload']['person_id']=str(uuid4())
        assert self.invoke(wrong,True) is None
        self.checks.append('person-create-independent-exact-retry-changed-retry-and-targeted-outcome')
        cohorts=self.fixture['cohorts'];links=[]
        for name in ('retained','second','recreated'):
            value=self.value(person,cohorts[name]);receipt=self.invoke(value)
            assert receipt.result.target.actor_id==cohorts[name]['actor_id'] and receipt.result.disposition=='created'
            assert self.invoke(value)==receipt and self.invoke(value,True)==receipt
            unchanged=deepcopy(value);unchanged['operation_id']=str(uuid4());unchanged['payload'].pop('expected_absent');unchanged['payload']['expected_revision']='1'
            assert self.invoke(unchanged).result.disposition=='unchanged'
            stale=deepcopy(unchanged);stale['operation_id']=str(uuid4());stale['payload']['expected_revision']='2'
            self.denied(stale,code='operation_conflict')
            changed=deepcopy(value);changed['payload']['person_id']=str(uuid4())
            self.denied(changed,code='operation_conflict')
            changed['operation_id']=str(uuid4());self.denied(changed,code='operation_conflict')
            actor=deepcopy(value);actor['operation_id']=str(uuid4());actor['payload']['actor_id']=cohorts['inactive']['actor_id']
            self.denied(actor,code='operation_conflict')
            links.append(value);self.expected_person[cohorts[name]['account_id']]=person;self.receipts.append(asdict(receipt))
        self.checks.append('same-person-separate-account-actors-retained-history-and-no-conflicting-relink')
        inactive=self.value(person,cohorts['inactive']);self.denied(inactive,code='operation_conflict')
        runtime=self.value(str(uuid4()));self.denied(runtime,key='runtime_url',code='access_denied')
        self.denied(links[0],key='runtime_url',code='access_denied',lookup=True)
        self.checks.append('inactive-account-and-runtime-command-and-outcome-denied')
        race=self.value(str(uuid4()))
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:self.invoke(race),range(2)))
        assert results[0]==results[1]
        self.event_evidence(race,results[0])
        self.checks.append('concurrent-identical-command-one-outcome-event')
        after=self.state()
        assert all(after[k]==before[k] for k in ('actor','account_actor','org_member'))
        assert after['person']==before['person']+2 and after['account_person']==before['account_person']+3
        self.checks.append('no-actor-member-or-other-owner-effects')
        self.link_contention(person,race['payload']['person_id'])
        foreign=self.value(person,cohorts['foreign_target']);unchanged=self.state()
        self.denied(foreign,code='access_denied');self.denied(foreign,lookup=True,code='access_denied')
        assert self.state()==unchanged
        self.checks.append('exact-target-authority-denies-foreign-execute-and-outcome-without-effects')
        self.cli_recovery(links[0],create)
        self.boundaries()
        return dict(status='passed',run_id=self.fixture['run_id'],database=self.fixture['database'],checks=self.checks,
            receipts=self.receipts,source_sha256={str(path.relative_to(OWNER)):sha256(path.read_bytes()).hexdigest() for path in
             [Path(__file__),OWNER/'identity_operator.py',OWNER/'identity_operator_input.py',OWNER/'operator_cli.py',OWNER/'identity-migrations/versions/0022_person_links.py']})
    def projection(self,account):
        db=self.engine('runtime_url')
        try:
            with db.begin() as connection:
                connection.execute(text("SELECT set_config('app.context_kind','user',true),set_config('app.account_id',:account,true)"),dict(account=account))
                return connection.execute(text('SELECT account_id::text,actor_id::text,person_id::text,revision FROM identity.current_account_person()')).all()
        finally:db.dispose()
    def setup_projections(self):
        for name in ('unlinked','missing_actor','foreign_target'):
            cohort=self.fixture['cohorts'][name]
            assert_projection(self.projection(cohort['account_id']),cohort['account_id'],cohort['actor_id'],None,None)
        assert self.projection(self.fixture['cohorts']['inactive']['account_id'])==[]
        self.checks.append('known-missing-person-missing-actor-and-inactive-account-distinguished')
    def event_evidence(self,value,receipt):
        rows=self.sql("SELECT o.id::text,o.command_type,o.operation_id::text,o.result,e.event_id::text,e.outcome_id::text,e.target,e.event_type FROM identity.operation_outcome o LEFT JOIN identity.business_event e ON e.outcome_id=o.id WHERE o.operation_id=CAST(:operation AS uuid) AND o.command_type=:command",dict(operation=value['operation_id'],command=value['command']))
        assert_event_evidence(rows,value,receipt)
    def link_contention(self,first_person,second_person):
        cohort=self.fixture['cohorts']['unlinked'];commands=[self.value(person,cohort) for person in (first_person,second_person)]
        start=threading.Barrier(2)
        def attempt(command):
            start.wait(timeout=5)
            try:return self.invoke(command)
            except operator.OperatorError as error:return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,commands))
        winners=[i for i,result in enumerate(results) if not isinstance(result,str)]
        assert len(winners)==1
        winner=winners[0];loser=1-winner;assert results[loser]=='operation_conflict'
        receipt=results[winner];assert receipt.result.disposition=='created'
        self.event_evidence(commands[winner],receipt)
        assert self.invoke(commands[loser],lookup=True) is None
        assert self.sql('SELECT count(*) FROM identity.operation_outcome WHERE operation_id=CAST(:operation AS uuid)',dict(operation=commands[loser]['operation_id']))==[(0,)]
        self.expected_person[cohort['account_id']]=commands[winner]['payload']['person_id']
        assert_projection(self.projection(cohort['account_id']),cohort['account_id'],cohort['actor_id'],self.expected_person[cohort['account_id']],1)
        self.checks.append('competing-person-links-one-mapping-one-linked-event-no-loser-outcome')
    def cli_recovery(self,link,create):
        import operator_cli
        target=operator_cli.load_target(self.fixture['cli_target'])
        assert target.database==self.fixture['database'] and target.port==APPROVED_PORT and target.run_id==APPROVED_RUN
        directory=Path(self.fixture['cli_target']).parent/'secrets'
        for command in (create,link):
            path=directory/('person-command-'+command['operation_id']+'.json')
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'w') as stream:json.dump(command,stream)
            common=[sys.executable,'-I','-B',str(OWNER/'operator_cli.py')]
            execute=common+['execute','--owner','identity','--target',self.fixture['cli_target'],'--command-file',str(path)]
            outcome=common+['outcome','--owner','identity','--target',self.fixture['cli_target'],'--command',command['command'],'--operation-id',command['operation_id'],'--person-id',command['payload']['person_id']]
            if command['command']=='account.link_person':outcome+=['--account-id',command['payload']['account_id']]
            values=[]
            for action,argv in [('execute',execute),('outcome',outcome)]:
                self.record(stage='cli-'+action,status='attempting',command=command['command'],operation_id=command['operation_id'])
                result=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=20,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'})
                assert result.returncode==0 and not result.stderr
                expected={name:command['payload'][name] for name in ('account_id','person_id','actor_id') if name in command['payload']}
                values.append(operator_cli.validate_response(result.stdout,command['operation_id'],command['command'],expected))
            assert values[0]==values[1]
        self.checks.append('actual-cli-isolated-worker-execute-and-original-outcome-both-person-commands')
    def boundaries(self):
        statements=['SELECT * FROM identity.person','SELECT * FROM identity.account_person','SELECT * FROM identity.operation_outcome',
            'SELECT * FROM identity.business_event','SELECT * FROM identity.alembic_version','CREATE TABLE identity.forbidden_person_probe(id integer)',
            'INSERT INTO identity.person(id,created_by,updated_by) VALUES (gen_random_uuid(),gen_random_uuid(),gen_random_uuid())']
        for index,statement in enumerate(statements):
            self.record(stage='runtime-denial',probe=index,status='attempting')
            db=self.engine('runtime_url')
            try:
                with db.connect() as connection:
                    require_permission_denial(connection,statement)
            finally:db.dispose()
        for name in ('retained','second','recreated','unlinked'):
            self.record(stage='own-person-projection',cohort=name,status='attempting')
            cohort=self.fixture['cohorts'][name]
            assert_projection(self.projection(cohort['account_id']),cohort['account_id'],cohort['actor_id'],self.expected_person[cohort['account_id']],1)
        self.checks.append('restricted-runtime-no-raw-rows-ledger-or-ddl-and-own-person-projection')


def assert_projection(rows,account,actor,person,revision):
    assert len(rows)==1 and tuple(rows[0])==(account,actor,person,revision),'qualification_person_projection_invalid'
    assert revision is None or type(rows[0][3]) is int,'qualification_person_projection_invalid'


def assert_event_evidence(rows,value,receipt):
    assert len(rows)==1,'qualification_command_event_linkage_invalid'
    outcome_id,command,operation,result,event_id,event_outcome,target,event_type=rows[0]
    expected=asdict(receipt.result);expected.pop('command')
    assert (command==value['command'] and operation==value['operation_id'] and result==expected
        and event_id==receipt.result.event_id and event_outcome==outcome_id and target==expected['target']
        and event_type==('identity.person_created' if command=='person.create' else 'identity.account_person_linked')),'qualification_command_event_linkage_invalid'


def safe_diagnostic(error):
    """Selected source locations/codes only; never exception text, SQL or parameters."""
    frames=traceback.extract_tb(error.__traceback__)
    locations=[dict(file=Path(frame.filename).name,line=frame.lineno) for frame in frames
        if Path(frame.filename).resolve().is_relative_to(OWNER)]
    result=dict(locations=locations)
    if isinstance(error,operator.OperatorError):result['code']=error.code
    state=getattr(getattr(error,'orig',error),'sqlstate',None)
    if isinstance(state,str) and len(state)==5 and state.isascii() and state.isalnum():result['sqlstate']=state
    return result


class Journal:
    """Private durable attempt references, written before calling a mutating command."""
    def __init__(self,path):
        self.lock=threading.Lock()
        self.fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    def __call__(self,value):
        encoded=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()
        with self.lock:
            with os.fdopen(os.dup(self.fd),'ab') as stream:
                stream.write(encoded);stream.flush();os.fsync(stream.fileno())
    def close(self):os.close(self.fd)


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);parser.add_argument('--run-id',required=True)
    parser.add_argument('--port',required=True,type=int);parser.add_argument('--output',required=True);args=parser.parse_args(argv)
    journal=None
    try:
        if not __debug__:raise ValueError('qualification_optimized_python_prohibited')
        fixture=load_fixture(args.fixture,args.run_id,args.port)
        output=Path(args.output)
        if output.exists():raise ValueError('qualification_output_exists')
        journal=Journal(str(output)+'.attempts.jsonl')
        result=Qualification(fixture,journal).run()
        with output.open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True,default=str);stream.write('\n')
        output.chmod(0o600)
    except Exception as error:
        diagnostic=safe_diagnostic(error)
        if journal is not None:journal(dict(stage='qualification',status='failed',diagnostic=diagnostic))
        print(json.dumps(dict(status='failed',code='person_qualification_failed_requires_reconciliation',diagnostic=diagnostic)))
        return 2
    finally:
        if journal is not None:journal.close()
    print(json.dumps(dict(status='passed',checks=len(result['checks']))));return 0

if __name__=='__main__':raise SystemExit(main())
