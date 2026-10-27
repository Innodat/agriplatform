"""Explicit private fixture qualification; no fixture provisioning or reference publication."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
from threading import Barrier
from urllib.parse import urlsplit
from uuid import UUID
import httpx
import psycopg
from psycopg.conninfo import conninfo_to_dict
sys.path.insert(0,str(Path(__file__).resolve().parent))
from identity_native_guard import guard,RUN,ROOT
OWNER=ROOT/'services/access'
COVERAGE=frozenset(('account-zero-membership','mixed-scope','no-cross-scope-union',
 'no-person-union','deny-before-setup','wrong-caller','revocation','rejoin',
 'reenable','people-context','concurrent-ordering','reused-context','restricted-runtime',
 'provider-unavailable','actor-setup','person-setup'))
ROLES=frozenset(('access_runtime','access_operator','identity_operator','identity_preferences_runtime'))
SERVICE_ENV={name:name.upper()+'_SERVICE_KEY' for name in ('leave','pts','reference','people','kdg','scribeswell','content','directory')}
COMMON={'account_id','actor_id','permission','authorization_scope','decision_id','checked_at'}
CONTEXT={'account_id','actor_id','org_id','membership_id','person_id','observation_id','checked_at'}


def private_bytes(path):
    """Open once without following links; validate the same descriptor we read."""
    try:
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        with os.fdopen(fd,'rb') as source:
            metadata=os.fstat(source.fileno())
            if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode)!=0o600 or metadata.st_uid!=os.getuid():raise ValueError('fixture_private_file_required')
            raw=source.read(16*1024*1024+1)
            current=os.stat(path,follow_symlinks=False)
            if len(raw)>16*1024*1024 or (metadata.st_dev,metadata.st_ino)!=(current.st_dev,current.st_ino):raise ValueError('fixture_private_file_required')
            return raw
    except OSError:raise ValueError('fixture_private_file_required') from None


def parse_fixture(raw):
    def closed(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('fixture_duplicate_key')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=closed,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('fixture_constant')))


def private_json(path):return parse_fixture(private_bytes(path))


def database_url(url,database,role=None):
    parsed=conninfo_to_dict(url.replace('postgresql+psycopg://','postgresql://',1))
    if (parsed.get('dbname')!=database or parsed.get('host')!='127.0.0.1' or parsed.get('port')!='55582'
        or parsed.get('user') not in ROLES or (role and parsed.get('user')!=role)
        or set(parsed)-{'dbname','host','port','user','password','sslmode','connect_timeout'}):raise ValueError('fixture_database_binding_invalid')
    return url.replace('postgresql+psycopg://','postgresql://',1)


def loopback_url(value,port=None):
    parsed=urlsplit(value)
    if (parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or not parsed.port
        or (port and parsed.port!=port) or parsed.username or parsed.password or parsed.query
        or parsed.fragment or parsed.path not in ('','/')):raise ValueError('fixture_http_binding_invalid')
    return value.rstrip('/')


def process_binding(fixture,proc=Path('/proc')):
    """Verify the live Linux process and socket before forwarding any credentials."""
    pid=fixture['api_process_id']
    if type(pid) is not int or pid<=0:raise ValueError('fixture_process_invalid')
    directory=proc/str(pid)
    try:
        identity=(directory/'stat').read_bytes()
        command=[part.decode() for part in (directory/'cmdline').read_bytes().split(b'\0') if part]
        cwd=(directory/'cwd').resolve(strict=True)
        fields=[part.split(b'=',1) for part in (directory/'environ').read_bytes().split(b'\0') if part]
        if any(len(part)!=2 for part in fields):raise ValueError('fixture_process_invalid')
        environment={key.decode():value.decode() for key,value in fields}
        if len(environment)!=len(fields):raise ValueError('fixture_process_invalid')
        # Only the actual owner main:app loaded by uvicorn is accepted.
        python_arguments=command[1:]
        while python_arguments and python_arguments[0] in ('-I','-B','-u'):
            python_arguments=python_arguments[1:]
        if len(python_arguments)>=3 and python_arguments[:2]==['-m','uvicorn']:arguments=python_arguments[2:]
        elif command and Path(command[0]).name=='uvicorn':arguments=command[1:]
        else:raise ValueError('fixture_process_invalid')
        if not arguments or arguments[0]!='main:app':raise ValueError('fixture_process_invalid')
        options=arguments[1:]
        if options.count('--no-access-log')>1:raise ValueError('fixture_process_invalid')
        options=[option for option in options if option!='--no-access-log']
        if len(options)%2 or any(option not in ('--host','--port','--app-dir','--log-level') for option in options[::2]):raise ValueError('fixture_process_invalid')
        settings=dict(zip(options[::2],options[1::2]))
        if len(settings)!=len(options)//2:raise ValueError('fixture_process_invalid')
        selected=Path(settings.get('--app-dir',str(cwd))).resolve(strict=True)
        if selected!=OWNER.resolve() or cwd not in (OWNER.resolve(),ROOT.resolve()):raise ValueError('fixture_process_invalid')
        port=urlsplit(fixture['api_url']).port
        if settings.get('--host')!='127.0.0.1' or settings.get('--port')!=str(port):raise ValueError('fixture_process_invalid')
        if conninfo_to_dict(environment.get('CAPABILITY_ACCESS_DATABASE_URL','').replace('postgresql+psycopg://','postgresql://',1))!=conninfo_to_dict(fixture['runtime_database_url'].replace('postgresql+psycopg://','postgresql://',1)):raise ValueError('fixture_process_binding_invalid')
        if environment.get('SUPABASE_URL','').rstrip('/')!=fixture['provider_url'].rstrip('/'):raise ValueError('fixture_process_binding_invalid')
        for caller,name in SERVICE_ENV.items():
            configured=environment.get(name,'');expected=fixture['service_keys'].get(caller,'')
            if configured!=expected:raise ValueError('fixture_process_binding_invalid')
        if any(name in environment for name in ('PYTHONPATH','PYTHONHOME')):raise ValueError('fixture_process_invalid')
        inodes=set()
        for link in (directory/'fd').iterdir():
            try:target=os.readlink(link)
            except FileNotFoundError:continue
            match=re.fullmatch(r'socket:\[([0-9]+)\]',target)
            if match:inodes.add(match.group(1))
        local='0100007F:'+format(port,'04X')
        listeners=[line.split() for line in (directory/'net/tcp').read_text().splitlines()[1:]]
        if not any(len(row)>9 and row[1]==local and row[3]=='0A' and row[9] in inodes for row in listeners):raise ValueError('fixture_process_listener_invalid')
        if (directory/'stat').read_bytes().split(b') ',1)[1].split()[19]!=identity.split(b') ',1)[1].split()[19]:raise ValueError('fixture_process_changed')
    except (OSError,UnicodeError,IndexError,psycopg.Error):raise ValueError('fixture_process_invalid') from None


def source_manifest():
    # Reuse the actual package's complete runtime source list, including its
    # unchanged Studies, identity preference and readiness dependencies.
    path=OWNER/'deployment/verify_runtime.py'
    spec=importlib.util.spec_from_file_location('_capability_runtime_manifest',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    paths={OWNER/name for name in module.SOURCES}|{path,OWNER/'pyproject.toml',OWNER/'uv.lock',Path(__file__),OWNER/'identity-migrations/versions/0025_capability_reader.py',OWNER/'migrations/versions/0018_current_capabilities.py'}
    return {str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',value) or not UUID(value).int:raise ValueError('http_identifier_invalid')


def membership(value):
    if not isinstance(value,str) or not re.fullmatch(r'[1-9][0-9]{0,18}',value) or int(value)>9223372036854775807:raise ValueError('http_membership_invalid')


def binding_fields(request):
    if request['path'].endswith('organization-context'):return CONTEXT-{'observation_id','checked_at'}
    fields=COMMON-{'decision_id','checked_at'}
    if request['body']['authorization_scope']['kind']=='organization':
        fields|={'membership_id','resource_scope'}
        if request['caller']=='leave':fields.add('person_id')
    return fields


def validate_http_case(case,fixture):
    request=case.get('request',case);expected=case.get('expected',request.get('expected'))
    if (not isinstance(expected,dict) or type(expected.get('status')) is not int
        or expected['status'] not in (200,401,403,409,422,503)
        or request.get('caller') not in fixture['service_keys'] or request.get('token') not in fixture['tokens']
        or request.get('path') not in ('/v2/check','/v2/identity/organization-context')
        or not isinstance(request.get('body'),dict)):raise ValueError('fixture_http_invalid')
    if expected['status']!=200:
        if not isinstance(expected.get('error_id'),str) or not re.fullmatch(r'[a-z][a-z0-9_.]{0,100}',expected['error_id']):raise ValueError('fixture_error_oracle_required')
        if expected.get('error_envelope','canonical') not in ('canonical','legacy'):raise ValueError('fixture_error_oracle_required')
    else:
        fields=expected.get('fields')
        if not isinstance(fields,dict) or not binding_fields(request)<=fields.keys():raise ValueError('fixture_binding_oracle_required')
        # The fixture's binding oracle must itself satisfy the declared variant.
        probe={**fields,'checked_at':'2026-10-27T00:00:00Z'}
        probe['observation_id' if request['path'].endswith('organization-context') else 'decision_id']='11111111-1111-4111-8111-111111111111'
        validate_success(probe,request)


def validate_sql_case(case,fixture):
    database_url(case['database_url'],fixture['database'])
    statements=case.get('statements',[case])
    if not isinstance(statements,list) or not statements:raise ValueError('fixture_sql_invalid')
    for statement in statements:
        if (not isinstance(statement,dict) or not isinstance(statement.get('statement'),str)
            or not statement['statement'] or len(set(statement)&{'expected_rows','expected_sqlstate'})!=1
            or ('expected_rows' in statement and not isinstance(statement['expected_rows'],list))
            or ('expected_sqlstate' in statement and not re.fullmatch(r'[A-Z0-9]{5}',statement['expected_sqlstate']))):raise ValueError('fixture_sql_invalid')


def validate_case(case,fixture,concurrent=False):
    choices=set(case)&{'request','sql','concurrent'}
    if len(choices)!=1:raise ValueError('fixture_step_ambiguous')
    if 'sql' in case:validate_sql_case(case['sql'],fixture)
    elif 'request' in case:validate_http_case(case,fixture)
    else:
        cases=case['concurrent']
        if concurrent or not isinstance(cases,list) or not 2<=len(cases)<=16:raise ValueError('fixture_concurrent_invalid')
        for item in cases:validate_case(item,fixture,True)


def load(fixture,target,run):
    import dev,native_cli
    required={'schema_version','run_id','database','container','network','provider_url','api_url','api_process_id','runtime_database_url','service_keys','tokens','steps'}
    if set(fixture)!=required or fixture['schema_version']!=1 or fixture['run_id']!=RUN:raise ValueError('fixture_shape_invalid')
    if not re.fullmatch(r'acb_88a737ddad7b_[0-9a-f]{8}',fixture['database']):raise ValueError('fixture_database_binding_invalid')
    project=dev.project_identity(target,RUN);network=native_cli.network(target,RUN,False,run)
    if fixture['container']!='supabase_db_'+project or fixture['network']!=network:raise ValueError('fixture_target_invalid')
    loopback_url(fixture['provider_url'],55581);loopback_url(fixture['api_url'])
    database_url(fixture['runtime_database_url'],fixture['database'],'access_runtime')
    if not isinstance(fixture['steps'],list) or not fixture['steps']:raise ValueError('fixture_steps_invalid')
    names=set();covered=set()
    for step in fixture['steps']:
        if not isinstance(step,dict) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}',step.get('name','')) or step['name'] in names:raise ValueError('fixture_step_invalid')
        names.add(step['name']);covered.update(step.get('coverage',[]));validate_case(step,fixture)
    if not COVERAGE<=covered:raise ValueError('fixture_coverage_incomplete')
    process_binding(fixture)
    return fixture


def validate_success(value,request):
    context=request['path'].endswith('organization-context')
    expected_shape=set(CONTEXT if context else COMMON)
    if not context and request['body']['authorization_scope']['kind']=='organization':
        expected_shape|={'membership_id','resource_scope'}
        if request['caller']=='leave':expected_shape.add('person_id')
    if not isinstance(value,dict) or set(value)!=expected_shape:raise ValueError('http_response_shape_invalid')
    for field in ('account_id','actor_id','observation_id' if context else 'decision_id'):identifier(value[field])
    checked=value['checked_at']
    if not isinstance(checked,str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)',checked):raise ValueError('http_time_invalid')
    parsed=datetime.fromisoformat(checked.replace('Z','+00:00'))
    if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):raise ValueError('http_time_invalid')
    if context:
        identifier(value['org_id']);membership(value['membership_id'])
        if value['org_id']!=request['body']['org_id']:raise ValueError('http_scope_mismatch')
        if value['person_id'] is not None:identifier(value['person_id'])
    else:
        scope=value['authorization_scope'];wanted=request['body']['authorization_scope']
        if value['permission']!=request['body']['permission'] or scope!=wanted:raise ValueError('http_scope_mismatch')
        if scope.get('kind')=='account':
            if set(scope)!={'kind'}:raise ValueError('http_scope_mismatch')
        elif scope.get('kind')=='organization':
            if set(scope)!={'kind','org_id'}:raise ValueError('http_scope_mismatch')
            identifier(scope['org_id']);membership(value['membership_id'])
            if request['caller']=='leave':
                identifier(value['person_id'])
                if value['resource_scope']!={'kind':'own','person_id':value['person_id']}:raise ValueError('http_resource_mismatch')
            elif value['resource_scope']!=scope:raise ValueError('http_resource_mismatch')
        else:raise ValueError('http_scope_mismatch')


def validate_response(response,case):
    request=case['request'];expected=case.get('expected',request.get('expected'))
    if response.status_code!=expected['status']:raise ValueError('http_status_mismatch')
    if 'no-store' not in response.headers.get('cache-control',''):raise ValueError('http_cache_policy_mismatch')
    value=response.json()
    if response.status_code!=200:
        if expected.get('error_envelope','canonical')=='legacy':
            if value!={'detail':{'code':expected['error_id']}}:raise ValueError('http_error_mismatch')
        elif (not isinstance(value,dict) or set(value)!={'error_id','error','details'} or value['error_id']!=expected['error_id']
              or not isinstance(value['error'],str) or value['details']!={}):raise ValueError('http_error_mismatch')
    else:
        validate_success(value,request)
        for key,item in expected['fields'].items():
            if value.get(key)!=item:raise ValueError('http_binding_mismatch')
    if any(key in value for key in expected.get('absent',[])):raise ValueError('http_absent_field_disclosed')


def normalize(rows):return json.loads(json.dumps([list(row) for row in rows],default=str))

class Qualification:
    def __init__(self,fixture,journal):self.fixture=fixture;self.journal=journal;self.checks=[]
    def record(self,value):
        self.journal.write(json.dumps(value,sort_keys=True)+'\n');self.journal.flush();os.fsync(self.journal.fileno())
    def request(self,case):
        request=case['request'];key=self.fixture['service_keys'][request['caller']];token=self.fixture['tokens'][request['token']]
        with httpx.Client(timeout=8,follow_redirects=False,trust_env=False) as client:
            response=client.post(self.fixture['api_url']+request['path'],json=request['body'],headers={'X-Service-Key':key,'Authorization':'Bearer '+token})
        validate_response(response,case)
    def sql(self,case):
        url=database_url(case['database_url'],self.fixture['database']);statements=case.get('statements',[case])
        with psycopg.connect(url,connect_timeout=2,autocommit=True) as connection:
            if connection.execute('SELECT current_database()').fetchone()[0]!=self.fixture['database']:raise ValueError('actual_database_binding_invalid')
            for statement in statements:
                try:
                    with connection.transaction():
                        connection.execute("SET LOCAL statement_timeout='3000'; SET LOCAL lock_timeout='1000'")
                        cursor=connection.execute(statement['statement'],statement.get('parameters'))
                        result=normalize(cursor.fetchall()) if cursor.description else []
                        if statement.get('expected_sqlstate'):raise ValueError('sql_did_not_refuse')
                        if result!=statement['expected_rows']:raise ValueError('sql_result_mismatch')
                except psycopg.Error as error:
                    if not statement.get('expected_sqlstate') or error.sqlstate!=statement['expected_sqlstate']:raise ValueError('sql_refusal_mismatch') from None
    def execute(self,case):
        if 'sql' in case:return self.sql(case['sql'])
        return self.request(case)
    def run(self):
        self.sql({'database_url':self.fixture['runtime_database_url'],'statement':'SELECT current_user,current_database()','expected_rows':[['access_runtime',self.fixture['database']]]})
        for step in self.fixture['steps']:
            self.record({'step':step['name'],'state':'attempted','coverage':step.get('coverage',[])})
            if 'concurrent' not in step:self.execute(step)
            else:
                cases=step['concurrent'];barrier=Barrier(len(cases))
                # Record each nested attempt before any worker can reach the barrier.
                for index in range(len(cases)):self.record({'step':step['name'],'case':index,'state':'attempted'})
                def launch(case):barrier.wait(timeout=5);return self.execute(case)
                with ThreadPoolExecutor(max_workers=len(cases)) as executor:list(executor.map(launch,cases))
            self.checks.append(step['name']);self.record({'step':step['name'],'state':'passed'})
        return self.checks


def main():
    if not __debug__:raise ValueError('capability_optimized_python_prohibited')
    parser=argparse.ArgumentParser();parser.add_argument('--fixture',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output);journal=output.with_suffix('.journal.jsonl')
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as destination:
        destination.write('{"status":"incomplete"}\n');destination.flush();os.fsync(destination.fileno())
        journal_fd=os.open(journal,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(journal_fd,'w') as events:
            events.write('{"state":"reserved"}\n');events.flush();os.fsync(events.fileno())
            raw=private_bytes(args.fixture);fixture=parse_fixture(raw);before=source_manifest()
            target,run=guard();fixture=load(fixture,target,run)
            checks=Qualification(fixture,events).run()
            if private_bytes(args.fixture)!=raw:raise ValueError('fixture_changed')
            if source_manifest()!=before:raise ValueError('runtime_source_changed')
            process_binding(fixture)
            result={'status':'passed','checks':checks,'fixture_sha256':sha256(raw).hexdigest(),'journal_sha256':sha256(journal.read_bytes()).hexdigest(),'sources':before}
            destination.seek(0);json.dump(result,destination,indent=2);destination.write('\n');destination.truncate();destination.flush();os.fsync(destination.fileno())
if __name__=='__main__':
    try:main()
    except Exception:
        print('capability_qualification_failed',file=sys.stderr);sys.exit(1)
