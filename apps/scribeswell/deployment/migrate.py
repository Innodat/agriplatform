"""Bounded Scribeswell migration process and safe create-only release evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
APP = Path(__file__).resolve().parents[1]
ROOT = APP.parents[1]
BUDGET_SECONDS = 180

def validate_url(environ):
    sys.path.insert(0,str(ROOT / 'platform/deployment'))
    from target_contract import database_url
    return database_url(environ['SCRIBESWELL_MIGRATION_DATABASE_URL'],environ['SUPABASE_URL'],'scribeswell_migrator')

def worker():
    # Internal IPC only. No raw exception or Alembic logging crosses this process.
    config=None
    try:
        request=json.loads(sys.stdin.read(16385))
        sys.path.insert(0,str(APP / 'backend'))
        from database import validate_url as local_url
        url=local_url(request['url'],'scribeswell_migrator')
        os.environ['SCRIBESWELL_MIGRATION_DATABASE_URL']=url
        from alembic import command
        from alembic.config import Config
        config=Config(str(APP / 'alembic.ini'))
        command.upgrade(config,'head')
        result={'before':config.attributes['scribeswell_before'],'after':config.attributes['scribeswell_after']}
        sys.stdout.write(json.dumps(result))
    except BaseException:
        result={'code':'scribeswell_migration_failed'}
        if config is not None and 'scribeswell_before' in config.attributes:
            before=config.attributes['scribeswell_before']
            if before is None or before in ('scribeswell_0001','scribeswell_0002'):
                result['before']=before
        sys.stdout.write(json.dumps(result))
        raise SystemExit(1) from None

def main(target=Path('/evidence/migrations.json'), *, environ=None, run=subprocess.Popen, timeout=BUDGET_SECONDS):
    environ=dict(os.environ if environ is None else environ)
    started=time.monotonic()
    report={'owners':{'scribeswell':{'status':'not_attempted'}},'complete':False}
    entry=report['owners']['scribeswell']
    # Refuse existing evidence before any validation or database work.
    try:
        evidence=Path(target).open('x',encoding='utf-8')
    except Exception:
        raise SystemExit(1) from None
    def save():
        evidence.seek(0)
        evidence.write(json.dumps(report,sort_keys=True)+'\n')
        evidence.truncate()
        evidence.flush()
        os.fsync(evidence.fileno())
    child=None
    try:
        save()
        url=validate_url(environ)
        if not 0 < timeout <= BUDGET_SECONDS:
            raise ValueError
        clean={key:value for key,value in environ.items() if not key.startswith('PG') and key!='SCRIBESWELL_MIGRATION_DATABASE_URL'}
        entry['status']='running';save()
        child=run([sys.executable,str(Path(__file__).resolve()),'--worker'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=clean,text=True)
        try:
            output,_=child.communicate(json.dumps({'url':url}),timeout=max(.001,timeout-(time.monotonic()-started)-min(5,timeout/10)))
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate(timeout=5)
            entry.update(status='unknown',outcome_requires_reconciliation=True)
            raise RuntimeError from None
        if len(output)>4096:
            raise RuntimeError
        result=json.loads(output)
        if child.returncode:
            if (isinstance(result,dict) and set(result) <= {'code','before'}
                    and result.get('code')=='scribeswell_migration_failed' and 'before' in result
                    and (result['before'] is None or result['before'] in ('scribeswell_0001','scribeswell_0002'))):
                entry['before']=result['before']
            raise RuntimeError
        if set(result)!={'before','after'} or result['before'] not in (None,'scribeswell_0001','scribeswell_0002') or result['after']!='scribeswell_0002':
            raise RuntimeError
        entry.update(status='succeeded',**result)
        report['complete']=True
        save()
    except BaseException:
        report['complete']=False
        if child is not None and child.poll() is None:
            child.kill()
            try:child.communicate(timeout=5)
            except Exception:pass
        if entry['status']!='unknown':
            entry.update(status='failed',outcome_requires_reconciliation=child is not None)
        report['code']='scribeswell_migration_failed'
        save()
        raise SystemExit(1) from None
    finally:
        evidence.close()
    return report

if __name__=='__main__':
    if sys.argv[1:]==['--worker']:
        worker()
    elif not sys.argv[1:]:
        main()
    else:
        raise SystemExit(1)
