from pathlib import Path
import subprocess,os,json,time,hashlib
base=Path(__file__).resolve().parent
out=Path('apps/scribeswell/docs/evidence/isolated-owner-fixture-20261027/parent-final');out.mkdir(parents=True,exist_ok=False)
paths=['platform/deployment/native_cli.py','platform/deployment/tests/test_native_cli.py','platform/deployment/environments/scribeswell-local.json','platform/deployment/schema/scribeswell-development-target-v1.json','apps/scribeswell/tests/studies_owner_fixture.py','apps/scribeswell/tests/test_studies_owner_integration.py','apps/scribeswell/web/playwright.owner-integration.config.cjs','apps/scribeswell/web/tests/studies-owner.integration.cjs','apps/scribeswell/web/tests/studies-owner-reporter.cjs','apps/scribeswell/web/tests/studies-owner-reporter.oracle.cjs']
before={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
cmd=[str(base/'python/bin/python'),'-m','pytest','-q','platform/deployment/tests/test_native_cli.py','apps/scribeswell/tests/test_studies_owner_integration.py'];env={**os.environ,'PYTHONPATH':str(Path('platform/deployment').resolve()),'PYTHONDONTWRITEBYTECODE':'1'};started=time.monotonic()
with (out/'pytest.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
after={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
result={'command':cmd,'environment':{'PYTHONPATH':env['PYTHONPATH'],'PYTHONDONTWRITEBYTECODE':'1'},'exit_code':r.returncode,'seconds':round(time.monotonic()-started,2),'sources_unchanged':before==after,'before':before,'after':after};(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('before','after')}));print((out/'pytest.log').read_text()[-1200:]);raise SystemExit(r.returncode)
