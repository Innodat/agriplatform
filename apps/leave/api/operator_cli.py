"""Explicit guarded disposable target; protected DB login/authority, no actor flags."""
import argparse,asyncio,json,os,stat,sys
from pathlib import Path
import psycopg
from sqlalchemy.engine import make_url
from leave_operator import parse_command,execute,outcome,OperationError
from contracts import json_object
ROOT=next((p for p in Path(__file__).resolve().parents if (p/'platform/deployment/native_cli.py').is_file() and (p/'platform/builder-cli').is_dir()),Path(__file__).resolve().parents[3])

def load_target(value):
    try:
        path=Path(os.path.abspath(value))
        if '..' in Path(value).parts:raise ValueError()
        for part in [path,*path.parents]:
            if part.is_symlink():raise ValueError()
        info=path.stat();parent=path.parent.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600 or parent.st_uid!=os.getuid() or stat.S_IMODE(parent.st_mode)!=0o700 or info.st_nlink!=1 or info.st_size>8192:raise ValueError()
        target=json_object(path.read_bytes())
        if set(target)!={'schema_version','owner','environment_kind','run_id','database','database_url','environment_target_ref','target_sha256'} or type(target['schema_version']) is not int or target['schema_version']!=1 or target['owner']!='leave' or target['environment_kind'] not in ('local_disposable','ci_disposable'):raise ValueError()
        import re
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,62}',target['database']):raise ValueError()
        from uuid import UUID
        run_id=str(UUID(target['run_id']))
        if run_id!=target['run_id'] or not UUID(run_id).int:raise ValueError()
        url=make_url(target['database_url'])
        if url.drivername!='postgresql+psycopg' or url.username!='leave_operator' or url.host!='127.0.0.1' or url.database!=target['database'] or not url.password or url.query:raise ValueError()
        # Generic deployment tooling only, never another owner's runtime code.
        sys.path.insert(0,str(ROOT/'platform/deployment'))
        import dev,native_cli
        ref=target['environment_target_ref']
        if type(ref) is not str or '..' in Path(ref).parts or not ref.startswith('platform/deployment/environments/') or not ref.endswith('.json'):raise ValueError()
        source=ROOT/ref;raw=dev.read(source);environment=dev.decode(raw);native_cli.validate_target(environment)
        if dev.digest(raw)!=target['target_sha256'] or environment['workspace_root']!=str(ROOT) or environment['environment_kind']!=target['environment_kind'] or url.port!=environment['ports']['database']:raise ValueError()
        run=native_cli.run_path(environment,run_id);native_cli.check_run(run,environment,raw,run_id)
        network=native_cli.network(environment,run_id,False,run)
        project=dev.project_identity(environment,run_id)
        rows=dev.decode(native_cli.docker(['container','inspect','supabase_db_'+project],run))
        if len(rows)!=1 or rows[0]['State']['Running'] is not True or rows[0]['NetworkSettings']['Ports']['5432/tcp']!=[{'HostIp':'127.0.0.1','HostPort':str(url.port)}] or rows[0]['NetworkSettings']['Networks'][project+'-network']['NetworkID']!=network or dev.read(source)!=raw:raise ValueError()
        return target
    except Exception:raise OperationError('leave_operator_target_invalid') from None

async def run(args):
    target=load_target(args.target)
    url=make_url(target['database_url']).set(drivername='postgresql').render_as_string(hide_password=False)
    async with asyncio.timeout(12):
        async with await psycopg.AsyncConnection.connect(url,connect_timeout=3,autocommit=True) as connection:
            cursor=await connection.execute("SELECT session_user,current_user,current_database(),r.rolsuper,r.rolcreatedb,r.rolcreaterole,r.rolreplication,r.rolbypassrls,r.rolinherit,EXISTS(SELECT 1 FROM pg_auth_members m WHERE m.member=r.oid) FROM pg_roles r WHERE r.rolname=session_user")
            if tuple(await cursor.fetchone())!=('leave_operator','leave_operator',target['database'],False,False,False,False,False,False,False):raise OperationError('access_denied')
            if args.action=='execute':
                if not args.command_file or any(v is not None for v in (args.command,args.operation_id,args.org_id,args.type_id)):raise OperationError('command_invalid')
                path=Path(args.command_file)
                if path.is_symlink() or path.stat().st_size>65536:raise OperationError('command_invalid')
                raw=path.read_bytes();parse_command(raw)
                return await execute(connection,raw)
            if args.command_file or not all((args.command,args.operation_id,args.org_id,args.type_id)):raise OperationError('command_invalid')
            return await outcome(connection,args.command,args.operation_id,args.org_id,args.type_id)

class SafeParser(argparse.ArgumentParser):
    def error(self,message):raise OperationError('command_invalid')

def main():
    result={'code':'command_invalid'}
    try:
        parser=SafeParser(allow_abbrev=False)
        parser.add_argument('action',choices=['execute','outcome']);parser.add_argument('--target',required=True)
        for flag in ('command-file','command','operation-id','org-id','type-id'):parser.add_argument('--'+flag)
        flags=[v for v in sys.argv[1:] if v.startswith('--')]
        if len(set(flags))!=len(flags) or any('=' in v for v in flags):raise OperationError('command_invalid')
        args=parser.parse_args();result=asyncio.run(run(args));status=0 if result.get('status')=='committed' else 2
    except OperationError as e:result={'code':e.code};status=2
    except Exception:result={'code':'operation_unavailable'};status=2
    print(json.dumps(result,separators=(',',':'),sort_keys=True));return status
if __name__=='__main__':raise SystemExit(main())
