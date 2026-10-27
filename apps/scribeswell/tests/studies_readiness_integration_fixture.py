"""App-owned qualification of the published exact-owner default startup contract.

The owner archive and its retained qualification are read-only inputs. Each new
fixture prepares its own executor-bound artifact; no retained artifact is reused.
All original browser, independent SQL, privacy and local-mail oracles are inherited.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from hashlib import sha256
from importlib.machinery import all_suffixes
import json
from pathlib import Path
import sys

import studies_owner_fixture as owner
from studies_signup_fixture import SignupQualification


def app_sources():
    # Keep the live app/helper/deployment inputs, while qualifying only the
    # explicitly selected owner source tree rather than concurrent owner work.
    sources={path:digest for path,digest in owner.source_inventory().items()
        if not path.is_relative_to(owner.ROOT/'services/access')}
    for name in ('tests/studies_readiness_integration_fixture.py',
                 'tests/test_studies_readiness_integration.py',
                 'tools/py/qualify_studies_readiness_integration.py'):
        path=owner.APP/name;sources[path]=sha256(path.read_bytes()).hexdigest()
    return sources


def owner_module_sources(access):
    # Re-enumerate packages as well as top-level modules, including sourceless
    # bytecode and extension modules that Python can select from this directory.
    suffixes=tuple(all_suffixes())
    return {path:sha256(path.read_bytes()).hexdigest() for path in access.rglob('*')
        if path.is_file() and path.name.endswith(suffixes)}


@contextmanager
def selected_owner(root):
    previous=owner.ACCESS
    try:
        owner.ACCESS=root/'services/access'
        yield
    finally:owner.ACCESS=previous


class ReadinessIntegrationQualification(SignupQualification):
    qualification_scope=('Exact Identity0026/Access0019 default startup and real local '
        'browser/signup/mail/SQL integration; no production, external SMTP, release/recovery or device claim')

    def __init__(self,run_id,cli,proof,*,source_root,qualification):
        self.source_root=Path(source_root).resolve(strict=True)
        self.owner_access=self.source_root/'services/access'
        self.qualification=Path(qualification).resolve(strict=True)
        # Base construction records the historical app inventory. The independent
        # inventory below additionally freezes the driver and selected owner inputs.
        super().__init__(run_id,cli,proof)
        self.app_sources=app_sources()
        record=json.loads(self.qualification.read_bytes())
        self.owner_sources={self.source_root/name:digest for name,digest in record['sources'].items()}
        # Operator commands and fixture preparation also execute owner helpers
        # beyond the published default-runtime module inventory.
        self.owner_module_sources=owner_module_sources(self.owner_access)
        self.owner_sources.update(self.owner_module_sources)
        for pattern in ('*.ini','tools/*.sql'):
            self.owner_sources.update({path:sha256(path.read_bytes()).hexdigest()
                for path in self.owner_access.glob(pattern)})
        self.proof_sources={self.qualification:sha256(self.qualification.read_bytes()).hexdigest()}
        self.proof_sources.update({self.qualification.parent/name:sha256((self.qualification.parent/name).read_bytes()).hexdigest()
            for name in record['proof_sha256']})
        self.cli_sha256=sha256(self.cli.read_bytes()).hexdigest()
        self.verify_sources()
        owner.private(self.proof/'integration-sources.json',self.inventory())

    def inventory(self):
        return {'app':{str(path.relative_to(owner.ROOT)):digest for path,digest in sorted(self.app_sources.items())},
            'owner':{str(path.relative_to(self.source_root)):digest for path,digest in sorted(self.owner_sources.items())},
            'qualification':{path.name:digest for path,digest in sorted(self.proof_sources.items())},
            'supabase_sha256':self.cli_sha256,'source_root':str(self.source_root),
            'qualification_path':str(self.qualification)}

    def validate_owner_qualification(self):
        code=('import json,sys;from pathlib import Path;import studies_readiness as r;'
            'p=Path(sys.argv[1]);r.validate_qualification(json.loads(p.read_bytes()),p.parent);'
            'print("owner_qualification_validated")')
        self.command('owner-qualification-validation',[sys.executable,'-B','-c',code,self.qualification],
            cwd=self.owner_access,timeout=30)

    def prepare_owners(self):
        self.validate_owner_qualification()
        with selected_owner(self.source_root):super().prepare_owners()

    def operator(self,*args,**kwargs):
        with selected_owner(self.source_root):return super().operator(*args,**kwargs)

    def prepare_readiness(self):
        self.verify_sources()
        self.readiness_path=self.proof/'readiness-private.json'
        env={**self.environment,**{name.upper()+'_MIGRATION_DATABASE_URL':
            self.urls[name+'_migrator'].set(drivername='postgresql+psycopg').render_as_string(hide_password=False)
            for name in ('identity','access')}}
        self.command('owner-prepare',[sys.executable,'-B',self.owner_access/'studies_readiness.py',
            '--qualification',self.qualification,'--release-id','synthetic-app-'+self.run_id,
            '--output',self.readiness_path],env=env,cwd=self.owner_access,timeout=45)
        self.readiness_raw=self.readiness_path.read_text()
        artifact=json.loads(self.readiness_raw)
        assert artifact['service_actor_id']==self.actor
        assert artifact['qualification_sha256']==self.proof_sources[self.qualification]
        assert self.readiness_path.stat().st_mode&0o777==0o600
        self.runtime_environment={**self.environment,'SCRIBESWELL_SERVICE_KEY':self.service_key,
            'STUDIES_READINESS_JSON':self.readiness_raw,'SUPABASE_URL':self.status['api_url'],
            'SUPABASE_ANON_KEY':self.status['anon_key'],
            **{name:self.urls[role].render_as_string(hide_password=False) for name,role in (
                ('STUDIES_ACCESS_DATABASE_URL','access_studies_runtime'),
                ('STUDIES_IDENTITY_DATABASE_URL','identity_studies_reader_runtime'),
                ('STUDIES_IDENTITY_SETUP_DATABASE_URL','identity_studies_setup_runtime'))}}
        owner.private(self.proof/'prepared-readiness.json',{'schema_version':artifact['schema_version'],
            'identity_revision':artifact['identity_revision'],'access_revision':artifact['access_revision'],
            'service_actor_id':self.actor,'artifact_sha256':sha256(self.readiness_raw.encode()).hexdigest(),
            'qualification_sha256':artifact['qualification_sha256'],'fresh_owner_prepare':True,
            'default_module':'main:app','runtime_sources':artifact['runtime_sources']})

    def startup_refusals(self):
        artifact=json.loads(self.readiness_raw)
        variants=[('missing-artifact',{'STUDIES_READINESS_JSON':None}),
            ('malformed-artifact',{'STUDIES_READINESS_JSON':'{}'})]
        for name in ('STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL'):
            variants.append(('missing-'+name,{name:None}))
        for label,change in [('old-version',{'schema_version':1}),
            ('later-head',{'identity_revision':'identity_0027'}),('stale-sources',{'runtime_sources':{}}),
            ('wrong-pair',{'identity_revision':'identity_0025','access_revision':'access_0018'})]:
            variants.append((label,{'STUDIES_READINESS_JSON':json.dumps(artifact|change)}))
        variants.append(('wrong-role',{'STUDIES_ACCESS_DATABASE_URL':self.urls['access_migrator'].render_as_string(hide_password=False)}))
        # Check the unmodified module in separate processes, without emitting
        # configuration values or provider/SQL errors into diagnostic output.
        code=('import importlib,sys\ntry:importlib.import_module("main")\n'
            'except RuntimeError as e:\n'
            ' if str(e)=="studies_configuration_invalid":sys.exit(0)\n'
            ' raise\nelse:sys.exit(3)')
        for label,changes in variants:
            env={k:v for k,v in (self.runtime_environment|changes).items() if v is not None}
            self.command('startup-refusal-'+label,[sys.executable,'-B','-c',code],env=env,cwd=self.owner_access,timeout=15)
        owner.private(self.proof/'startup-refusals.json',{'cases':[label for label,_ in variants],
            'unmodified_module_import':True,'all_refused':True})

    def start_apps(self):
        self.prepare_readiness();self.startup_refusals()
        access=self.spawn('access-http',[sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1',
            '--port',str(owner.TARGET_CONFIG['ports']['access_http']),'--no-access-log','--log-level','error'],
            self.runtime_environment,self.owner_access)
        owner.wait_http(owner.OWNER_URL+'/health',access)
        env={**self.environment,'SCRIBESWELL_DATABASE_URL':self.urls['scribeswell_runtime'].render_as_string(hide_password=False),
            'SCRIBESWELL_STUDIES_ENABLED':'true','SCRIBESWELL_STUDIES_DATABASE_URL':self.urls['scribeswell_studies_runtime'].render_as_string(hide_password=False),
            'SCRIBESWELL_STUDIES_ACCESS_URL':owner.OWNER_URL,'SCRIBESWELL_STUDIES_SERVICE_KEY':self.service_key,
            'SUPABASE_URL':self.status['api_url'],'SUPABASE_SECRET_KEY':'','SUPABASE_SERVICE_ROLE_KEY':''}
        app=self.spawn('scribeswell-http',[sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1',
            '--port',str(owner.TARGET_CONFIG['ports']['api']),'--no-access-log','--log-level','error'],env,owner.APP/'backend')
        owner.wait_http(owner.API_URL+'/health',app)
        env={**self.environment,'VITE_STUDIES_ENABLED':'true','VITE_APP_BASE':'/','VITE_PLATFORM_ORIGIN':'',
            'VITE_SUPABASE_URL':self.status['api_url'],'VITE_SUPABASE_ANON_KEY':self.status['anon_key'],
            'VITE_API_BASE_URL':owner.API_URL,'VITE_APP_DIRECTORY_URL':owner.OWNER_URL}
        web=self.spawn('vite',['npm','run','dev','--','--host','localhost','--port',str(owner.TARGET_CONFIG['ports']['web']),
            '--strictPort'],env,owner.APP/'web')
        owner.wait_http(owner.WEB_URL,web)

    def verify_sources(self):
        if app_sources()!=self.app_sources:raise RuntimeError('qualification_app_sources_changed')
        if owner_module_sources(self.owner_access)!=self.owner_module_sources:
            raise RuntimeError('qualification_owner_sources_changed')
        for path,digest in (self.owner_sources|self.proof_sources).items():
            if sha256(path.read_bytes()).hexdigest()!=digest:raise RuntimeError('qualification_owner_sources_changed')
        if sha256(self.cli.read_bytes()).hexdigest()!=self.cli_sha256:raise RuntimeError('qualification_cli_changed')

    def extra_qualification(self):
        super().extra_qualification()
        self.verify_sources()
        owner.private(self.proof/'integration-final-inspection.json',{'sources':self.inventory(),
            'all_inherited_browser_sql_signup_oracles_completed':True,
            'confirmation_did_not_grant_access':True,'fresh_default_startup':True})


def qualify():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    for name in ('supabase','proof','source-root','qualification'):
        parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args()
    ReadinessIntegrationQualification(args.run_id,args.supabase,args.proof,
        source_root=args.source_root,qualification=args.qualification).execute()
