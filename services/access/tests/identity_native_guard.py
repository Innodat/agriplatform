"""Read-only guard for the one approved disposable Leave Identity rehearsal."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'platform/deployment'))
import dev
import native_cli
RUN='88a737dd-ad7b-429a-a83c-5d103716d659'
PORT=55582
DATABASE_PREFIX='idb_88a737ddad7b_'


def guard():
    source=ROOT/'platform/deployment/environments/leave-local.json'
    raw=dev.read(source);target=dev.decode(raw);native_cli.validate_target(target)
    if target['target_id']!='leave-local' or target['ports']['database']!=PORT or target['workspace_root']!=str(ROOT):
        raise ValueError('native_target_invalid')
    path=native_cli.run_path(target,RUN);native_cli.check_run(path,target,raw,RUN)
    project=dev.project_identity(target,RUN);network=native_cli.network(target,RUN,False,path)
    rows=dev.decode(native_cli.docker(['container','inspect','supabase_db_'+project],path))
    if (len(rows)!=1 or rows[0]['State']['Running'] is not True
        or rows[0]['NetworkSettings']['Ports']['5432/tcp']!=[{'HostIp':'127.0.0.1','HostPort':str(PORT)}]
        or rows[0]['NetworkSettings']['Networks'][project+'-network']['NetworkID']!=network):
        raise ValueError('native_target_invalid')
    if dev.read(source)!=raw:raise ValueError('native_target_changed')
    return target,path
