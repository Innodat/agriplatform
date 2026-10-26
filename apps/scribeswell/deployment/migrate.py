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
sys.path.insert(0,str(APP / 'migrations'))
sys.path.insert(0,str(APP / 'deployment'))
from release_profile import from_environ, selection, evidence as profile_evidence, strict_json, valid_result, OPTION_KEYS

def validate_url(environ):
    sys.path.insert(0,str(ROOT / 'platform/deployment'))
    from target_contract import database_url
    return database_url(environ['SCRIBESWELL_MIGRATION_DATABASE_URL'],environ['SUPABASE_URL'],'scribeswell_migrator')

def worker():
    # Internal IPC only. No raw exception or Alembic logging crosses this process.
    config=None
    try:
        request=strict_json(sys.stdin.read(16385),16384)
        if type(request) is not dict or set(request)!={'url','validation'}:
            raise ValueError
        expected=selection(request['validation'])
        sys.path.insert(0,str(APP / 'backend'))
        from database import validate_url as local_url
        url=local_url(request['url'],'scribeswell_migrator')
        os.environ['SCRIBESWELL_MIGRATION_DATABASE_URL']=url
        from alembic import command
        from alembic.config import Config
        config=Config(str(APP / 'alembic.ini'))
        config.attributes['scribeswell_validation_profile']=expected['profile']
        if expected['custody'] is not None:
            config.attributes['scribeswell_prepared_actor']=expected['custody']
        command.upgrade(config,'head' if expected['profile']=='publication-v1' else 'scribeswell_0003')
        if config.attributes.get('scribeswell_validated_profile')!=expected['profile']:
            raise ValueError
        result={'before':config.attributes['scribeswell_before'],'after':config.attributes['scribeswell_after'],
                'validation':profile_evidence(expected)}
        if not valid_result(result,expected):
            raise ValueError
        sys.stdout.write(json.dumps(result))
    except BaseException:
        result={'code':'scribeswell_migration_failed'}
        if config is not None and 'scribeswell_before' in config.attributes:
            before=config.attributes['scribeswell_before']
            if before is None or before in ('scribeswell_0001','scribeswell_0002','scribeswell_0003','scribeswell_0004'):
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
        from studies_migrate import selected
        private_selected=selected(environ)
        if private_selected and Path(target).with_name('studies-migrations.json').exists():raise ValueError
        expected=from_environ(environ)
        entry['requested_validation']=profile_evidence(expected)
        url=validate_url(environ)
        if not 0 < timeout <= BUDGET_SECONDS:
            raise ValueError
        clean={key:value for key,value in environ.items() if not key.startswith('PG') and key not in OPTION_KEYS|{'SCRIBESWELL_MIGRATION_DATABASE_URL','SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL'}}
        entry['status']='running';save()
        child=run([sys.executable,str(Path(__file__).resolve()),'--worker'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=clean,text=True)
        try:
            output,_=child.communicate(json.dumps({'url':url,'validation':expected}),timeout=max(.001,timeout-(time.monotonic()-started)-min(5,timeout/10)))
        except subprocess.TimeoutExpired:
            child.kill()
            child.communicate(timeout=5)
            entry.update(status='unknown',outcome_requires_reconciliation=True)
            raise RuntimeError from None
        if len(output)>4096:
            raise RuntimeError
        result=strict_json(output,4096)
        if child.returncode:
            if (isinstance(result,dict) and set(result) <= {'code','before'}
                    and result.get('code')=='scribeswell_migration_failed' and 'before' in result
                    and (result['before'] is None or result['before'] in ('scribeswell_0001','scribeswell_0002','scribeswell_0003','scribeswell_0004'))):
                entry['before']=result['before']
            raise RuntimeError
        if not valid_result(result,expected):
            raise RuntimeError
        entry.update(status='succeeded',**result)
        from studies_migrate import selected
        if selected(environ):
            # Corpus precedes private history. The same supervised process budget applies.
            child=run([sys.executable,str(APP/'deployment/studies_migrate.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=clean,text=True)
            try:
                private_output,_=child.communicate(json.dumps({'url':environ['SCRIBESWELL_STUDIES_MIGRATION_DATABASE_URL']}),timeout=max(.001,timeout-(time.monotonic()-started)-min(5,timeout/10)))
            except subprocess.TimeoutExpired:
                child.kill();child.communicate(timeout=5)
                entry.update(status='unknown',outcome_requires_reconciliation=True)
                raise RuntimeError from None
            expected_private={'complete':True,'owner':'scribeswell_studies','after':'scribeswell_studies_0001','recovery':'forward-only'}
            if child.returncode or len(private_output)>4096 or strict_json(private_output,4096)!=expected_private:raise RuntimeError
            with Path(target).with_name('studies-migrations.json').open('x',encoding='utf8') as private_evidence:
                private_evidence.write(json.dumps(expected_private)+'\n');private_evidence.flush();os.fsync(private_evidence.fileno())
        report['complete']=True
        save()
    except BaseException:
        report['complete']=False
        entry.pop('validation',None)
        entry.pop('after',None)
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
