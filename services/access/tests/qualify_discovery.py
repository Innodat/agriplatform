"""Guarded native discovery proof using independently authored private fixture oracles."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sys
import time
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parent))
import qualify_capabilities as existing
from identity_native_guard import guard,RUN,ROOT
OWNER=ROOT/'services/access'
private_bytes=existing.private_bytes
parse_fixture=existing.parse_fixture
database_url=existing.database_url
process_binding=existing.process_binding
COVERAGE=frozenset(('account-zero-membership','mixed-scope','shared-person-accounts',
 'entry-not-admin','sparse-pagination','over-100','revocation','rejoin','disabled-account',
 'caller-isolation','spoofed-input','context-isolation','restricted-runtime',
 'public-execute-denied','temp-shadowing','provider-unavailable','catalogue-overflow'))

def source_manifest():
    result=existing.source_manifest()
    paths=[Path(__file__),OWNER/'openapi.json',OWNER/'contracts/adapter.ts',
        OWNER/'identity-migrations/versions/0026_discovery.py',OWNER/'identity-migrations/identity_discovery_catalog.py',
        OWNER/'identity-migrations/identity_baseline.py',OWNER/'identity-migrations/discovery-reference.json',
        OWNER/'migrations/versions/0019_discovery.py',OWNER/'migrations/access_discovery_catalog.py',
        OWNER/'migrations/access_baseline.py',OWNER/'migrations/discovery-reference.json']
    for path in paths:
        if path.is_file():result[str(path.relative_to(ROOT))]=sha256(path.read_bytes()).hexdigest()
    return result

def validate_success(value,request):
    if not isinstance(value,dict):raise ValueError('http_response_shape_invalid')
    if request['path']=='/v2/organizations':
        if set(value)!={'organizations','next_cursor'} or not isinstance(value['organizations'],list) or len(value['organizations'])>100:raise ValueError('http_response_shape_invalid')
        previous=''
        for row in value['organizations']:
            if not isinstance(row,dict) or set(row)!={'org_id','name','membership_id'} or not isinstance(row['name'],str):raise ValueError('http_response_shape_invalid')
            existing.identifier(row['org_id']);existing.membership(row['membership_id'])
            if row['org_id'].lower()<=previous:raise ValueError('http_order_invalid')
            previous=row['org_id'].lower()
        cursor=value['next_cursor']
        if cursor is not None:
            import base64
            if not isinstance(cursor,str) or not re.fullmatch(r'[A-Za-z0-9_-]{48}',cursor) or not previous:raise ValueError('http_cursor_invalid')
            if base64.b64decode(cursor,altchars=b'-_',validate=True).decode('ascii')!=previous:raise ValueError('http_cursor_invalid')
    else:
        if set(value)!={'applications','checked_at'} or not isinstance(value['applications'],list) or len(value['applications'])>128:raise ValueError('http_response_shape_invalid')
        checked=value['checked_at']
        if not isinstance(checked,str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|\+00:00)',checked):raise ValueError('http_time_invalid')
        parsed=datetime.fromisoformat(checked.replace('Z','+00:00'))
        if parsed.utcoffset()!=timezone.utc.utcoffset(parsed):raise ValueError('http_time_invalid')
        previous=''
        for row in value['applications']:
            if not isinstance(row,dict) or set(row)!={'app_id','eligible_scope_kinds'}:raise ValueError('http_response_shape_invalid')
            app=row['app_id']
            if not isinstance(app,str) or not re.fullmatch(r'[a-z][a-z0-9_]{1,63}',app) or app<=previous:raise ValueError('http_order_invalid')
            if row['eligible_scope_kinds'] not in (['account'],['organization'],['account','organization']):raise ValueError('http_scope_invalid')
            previous=app

def validate_http_case(case,fixture):
    request=case['request'];expected=case.get('expected')
    if (not isinstance(expected,dict) or type(expected.get('status')) is not int
        or expected['status'] not in (200,401,403,422,500,503)
        or request.get('caller') not in fixture['service_keys'] or request.get('token') not in fixture['tokens']
        or request.get('path') not in ('/v2/organizations','/v2/applications')
        or set(request)-{'caller','token','path','query'}
        or not isinstance(request.get('query',''),str) or len(request.get('query',''))>4096
        or any(ord(c)<32 or ord(c)>126 or c=='#' for c in request.get('query',''))):raise ValueError('fixture_http_invalid')
    if expected['status']!=200:
        if not isinstance(expected.get('error_id'),str) or not re.fullmatch(r'[a-z][a-z0-9_.]{0,100}',expected['error_id']):raise ValueError('fixture_error_oracle_required')
    else:
        fields=expected.get('fields');required={'applications'} if request['path']=='/v2/applications' else {'organizations','next_cursor'}
        if not isinstance(fields,dict) or set(fields)!=required:raise ValueError('fixture_binding_oracle_required')
        validate_success({**fields,**({'checked_at':'2026-10-27T00:00:00Z'} if request['path']=='/v2/applications' else {})},request)

def validate_case(case,fixture,concurrent=False):
    choices=set(case)&{'request','sql','concurrent'}
    if len(choices)!=1:raise ValueError('fixture_step_ambiguous')
    if 'sql' in case:existing.validate_sql_case(case['sql'],fixture)
    elif 'request' in case:validate_http_case(case,fixture)
    else:
        cases=case['concurrent']
        if concurrent or not isinstance(cases,list) or not 2<=len(cases)<=16:raise ValueError('fixture_concurrent_invalid')
        for item in cases:validate_case(item,fixture,True)

def load(fixture,target,run):
    import dev,native_cli
    required={'schema_version','run_id','database','container','network','provider_url','api_url','api_process_id','runtime_database_url','service_keys','tokens','steps'}
    if set(fixture)!=required or fixture['schema_version']!=1 or fixture['run_id']!=RUN:raise ValueError('fixture_shape_invalid')
    if not re.fullmatch(r'dsc_88a737ddad7b_[0-9a-f]{8}',fixture['database']):raise ValueError('fixture_database_binding_invalid')
    project=dev.project_identity(target,RUN);network=native_cli.network(target,RUN,False,run)
    if fixture['container']!='supabase_db_'+project or fixture['network']!=network:raise ValueError('fixture_target_invalid')
    existing.loopback_url(fixture['provider_url'],55581);existing.loopback_url(fixture['api_url'])
    database_url(fixture['runtime_database_url'],fixture['database'],'access_runtime')
    if not isinstance(fixture['steps'],list) or not fixture['steps']:raise ValueError('fixture_steps_invalid')
    names=set();covered=set()
    for step in fixture['steps']:
        if not isinstance(step,dict) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}',step.get('name','')) or step['name'] in names:raise ValueError('fixture_step_invalid')
        names.add(step['name']);covered.update(step.get('coverage',[]));validate_case(step,fixture)
    if not COVERAGE<=covered:raise ValueError('fixture_coverage_incomplete')
    process_binding(fixture)
    return fixture

def validate_response(response,case):
    expected=case['expected']
    if response.status_code!=expected['status']:raise ValueError('http_status_mismatch')
    if response.headers.get('cache-control')!='private, no-store':raise ValueError('http_cache_policy_mismatch')
    value=response.json()
    if response.status_code!=200:
        if not isinstance(value,dict) or set(value)!={'error_id','error','details'} or value['error_id']!=expected['error_id'] or not isinstance(value['error'],str) or value['details']!={}:raise ValueError('http_error_mismatch')
    else:
        validate_success(value,case['request'])
        for key,wanted in expected['fields'].items():
            if value.get(key)!=wanted:raise ValueError('http_binding_mismatch')

class Qualification(existing.Qualification):
    def request(self,case):
        request=case['request'];key=self.fixture['service_keys'][request['caller']];token=self.fixture['tokens'][request['token']]
        url=self.fixture['api_url']+request['path']+('?' + request['query'] if request.get('query') else '')
        headers={'X-Service-Key':key}
        if token:headers['Authorization']='Bearer '+token
        started=time.monotonic()
        with httpx.Client(timeout=4,follow_redirects=False,trust_env=False) as client:
            response=client.get(url,headers=headers)
        if time.monotonic()-started>3.75:raise ValueError('discovery_budget_exceeded')
        validate_response(response,case)

def main():
    if not __debug__:raise ValueError('discovery_optimized_python_prohibited')
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
        print('discovery_qualification_failed',file=sys.stderr);sys.exit(1)
