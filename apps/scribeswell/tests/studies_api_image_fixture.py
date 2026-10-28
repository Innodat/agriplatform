"""Create-only default Scribeswell API image qualification on the real owner fixture.

The app requirements are intentionally unchanged and unpinned. Recorded installed
bytes qualify one built image, not a reproducible or frozen dependency baseline.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import time

import studies_frozen_runtime_fixture as frozen
import studies_owner_fixture as owner

APP_ROLE_KEYS={'SCRIBESWELL_DATABASE_URL':'scribeswell_runtime',
    'SCRIBESWELL_STUDIES_DATABASE_URL':'scribeswell_studies_runtime'}
PACKAGING=('deployment/Dockerfile','deployment/Dockerfile.dockerignore','deployment/manifest.json')
DRIVERS=('tests/studies_api_image_fixture.py','tests/test_studies_api_image.py',
    'tools/py/qualify_studies_api_image.py')


def packaged_sources():
    """Enumerate every shipped COPY input, with the shipped context exclusions."""
    paths=set()
    for line in (owner.APP/'deployment/Dockerfile').read_text().splitlines():
        if not line.startswith('COPY '):continue
        parts=line.split()
        if len(parts)!=3 or parts[1].startswith('--'):raise RuntimeError('qualification_copy_syntax_changed')
        source=owner.ROOT/parts[1]
        if source.is_symlink():raise RuntimeError('qualification_packaging_symlink_refused')
        candidates=source.rglob('*') if source.is_dir() else (source,)
        for path in candidates:
            relative=path.relative_to(owner.ROOT)
            if any(part.startswith('.env') or part in ('__pycache__','.pytest_cache','tests','.local') for part in relative.parts) or path.suffix=='.pyc':continue
            if path.is_symlink():raise RuntimeError('qualification_packaging_symlink_refused')
            if path.is_file():paths.add(path)
    return {p:frozen.digest(p) for p in sorted(paths)}


def image_sources(inputs):
    result={}
    for path,value in inputs.items():
        relative=str(path.relative_to(owner.ROOT))
        result['/tmp/requirements.txt' if relative=='apps/scribeswell/backend/requirements.txt' else '/app/'+relative]=value
    # The backend COPY also includes requirements.txt.
    result['/app/apps/scribeswell/backend/requirements.txt']=inputs[owner.APP/'backend/requirements.txt']
    return result


def app_container_arguments(name,image,network,environment,port=None):
    args=frozen.container_arguments(name,image,network,environment,port)
    args[args.index('--user')+1]='10001:10001'
    return args


PROBE='''import os,json,platform,hashlib,importlib.metadata,importlib.util
from pathlib import Path
assert os.getuid()==10001
assert importlib.util.find_spec('pytest') is None
assert not any('MIGRATION' in key for key in os.environ)
assert not any(os.environ.get(key) for key in ('SUPABASE_SECRET_KEY','SUPABASE_SERVICE_ROLE_KEY'))
import psycopg
sql_tls={}
for key,role in (('SCRIBESWELL_DATABASE_URL','scribeswell_runtime'),('SCRIBESWELL_STUDIES_DATABASE_URL','scribeswell_studies_runtime')):
 with psycopg.connect(os.environ[key].replace('postgresql+psycopg://','postgresql://',1),connect_timeout=3,autocommit=True,options='-c statement_timeout=3000 -c default_transaction_read_only=on') as connection:
  row=connection.execute('SELECT current_user,s.ssl,s.version,s.cipher FROM pg_stat_ssl s WHERE s.pid=pg_backend_pid()').fetchone()
 assert row[0]==role and row[1] is True
 sql_tls[role]={'ssl':row[1],'version':row[2],'cipher':row[3]}
def inventory(root):
 result={}
 for p in sorted(root.rglob('*')):
  name=str(p)
  result[name]={'link':os.readlink(p)} if p.is_symlink() else {'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} if p.is_file() else {'directory':True}
 return result
try:Path('/app/qualification-forbidden').write_text('forbidden')
except OSError as error:assert error.errno==30
else:raise RuntimeError('qualification_root_writable')
print(json.dumps({'python_version':platform.python_version(),'uid':os.getuid(),'pytest_absent':True,'read_only':True,'migration_authority_absent':True,'provider_service_authority_absent':True,'sql_tls':sql_tls,'files':inventory(Path('/app')),'requirements_sha256':hashlib.sha256(Path('/app/apps/scribeswell/backend/requirements.txt').read_bytes()).hexdigest(),'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'dependency_files':inventory(Path('/usr/local/lib/python3.12/site-packages'))}))'''


class ApiImageQualification(frozen.FrozenRuntimeQualification):
    qualification_scope=('Exact Scribeswell default API image and frozen Identity0026/Access0019 Access image '
        'on a fresh synthetic browser/signup/local-mail/SQL fixture; unpinned app dependencies observed only; '
        'no production activation, environment release/recovery, external SMTP, sharing or device claim')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.api_inputs=packaged_sources()
        self.api_driver_inputs={owner.APP/name:frozen.digest(owner.APP/name) for name in (*PACKAGING,*DRIVERS)}
        owner.private(self.proof/'api-initial-inputs.json',self.api_inventory())

    def api_inventory(self):
        return {'packaged':{str(p.relative_to(owner.ROOT)):d for p,d in self.api_inputs.items()},
            'drivers':{str(p.relative_to(owner.ROOT)):d for p,d in self.api_driver_inputs.items()}}

    def verify_sources(self):
        super().verify_sources()
        if not hasattr(self,'api_inputs'):return
        if packaged_sources()!=self.api_inputs:raise RuntimeError('qualification_api_inputs_changed')
        if any(frozen.digest(p)!=d for p,d in self.api_driver_inputs.items()):
            raise RuntimeError('qualification_api_driver_changed')
        if hasattr(self,'api_context'):
            actual={str(p.relative_to(self.api_context)):frozen.digest(p) for p in self.api_context.rglob('*') if p.is_file()}
            expected={str(p.relative_to(owner.ROOT)):d for p,d in (self.api_inputs|self.api_driver_inputs).items() if p in self.api_inputs or p in [owner.APP/n for n in PACKAGING]}
            if actual!=expected:raise RuntimeError('qualification_api_context_changed')

    def package_image(self):
        super().package_image()
        self.api_context=self.context/'scribeswell-api';self.api_context.mkdir(mode=0o700)
        for source in self.api_inputs|{owner.APP/n:self.api_driver_inputs[owner.APP/n] for n in PACKAGING}:
            destination=self.api_context/source.relative_to(owner.ROOT)
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
        self.verify_sources()
        self.api_tag='scribeswell-api-qualified:'+self.run_id
        self.docker('api-image-build',['build','--pull=false','-t',self.api_tag,'-f',
            self.api_context/'apps/scribeswell/deployment/Dockerfile',self.api_context],timeout=300)
        self.api_image=json.loads(self.docker('api-image-id',['image','inspect','--format','{{json .Id}}',self.api_tag]))
        fields='{"Id":{{json .Id}},"RepoDigests":{{json .RepoDigests}},"RootFS":{{json .RootFS}},"Cmd":{{json .Config.Cmd}},"User":{{json (index .Config "User")}}}'
        self.api_image_metadata=json.loads(self.docker('api-image-metadata',['image','inspect','--format',fields,self.api_image]))
        self.api_base_metadata=json.loads(self.docker('api-base-metadata',['image','inspect','--format',fields,'python:3.12-slim-bookworm']))
        base_layers=self.api_base_metadata['RootFS']['Layers']
        if self.api_image_metadata['RootFS']['Layers'][:len(base_layers)]!=base_layers:
            raise RuntimeError('qualification_api_base_changed')
        owner.private(self.proof/'api-image-package.json',{'image':self.api_image_metadata,'base':self.api_base_metadata,
            'inputs':self.api_inventory(),'dependency_baseline_frozen':False})

    def prepare_owners(self):
        super().prepare_owners()
        self.prepare_tls()

    def prepare_tls(self):
        # native_cli checked custody of this newly created run before status capture.
        project=owner.dev.project_identity(owner.TARGET_CONFIG,self.run_id)
        name='supabase_db_'+project
        identifier=json.loads(self.docker('fixture-db-id',['inspect','--format','{{json .Id}}',name]))
        with self.connect() as connection:enabled=connection.execute('SHOW ssl').fetchone()[0]=='on'
        if not enabled:
            cert=self.proof/'fixture-tls.crt';key=self.proof/'fixture-tls.key'
            self.command('fixture-tls-create',['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1',
                '-subj','/CN='+name,'-keyout',key,'-out',cert],timeout=30)
            key.chmod(0o600);cert.chmod(0o600)
            for source,target in ((cert,'/tmp/scribeswell-qualification.crt'),(key,'/tmp/scribeswell-qualification.key')):
                self.docker('fixture-tls-copy',['cp',source,identifier+':'+target])
            self.docker('fixture-tls-owner',['exec','--user','root',identifier,'chown','postgres:postgres',
                '/tmp/scribeswell-qualification.crt','/tmp/scribeswell-qualification.key'])
            self.docker('fixture-tls-mode',['exec','--user','root',identifier,'chmod','600',
                '/tmp/scribeswell-qualification.crt','/tmp/scribeswell-qualification.key'])
            with self.connect() as connection:
                connection.execute("ALTER SYSTEM SET ssl_cert_file='/tmp/scribeswell-qualification.crt'")
                connection.execute("ALTER SYSTEM SET ssl_key_file='/tmp/scribeswell-qualification.key'")
                connection.execute("ALTER SYSTEM SET ssl='on'")
                connection.execute('SELECT pg_reload_conf()')
            time.sleep(.3)
        results={}
        for role in APP_ROLE_KEYS.values():
            self.urls[role]=self.urls[role].update_query_dict({'sslmode':'require'})
            with self.connect(role) as connection:
                row=connection.execute('SELECT current_user,s.ssl,s.version,s.cipher FROM pg_stat_ssl s WHERE s.pid=pg_backend_pid()').fetchone()
            if row[0]!=role or row[1] is not True:raise RuntimeError('qualification_app_tls_unproven')
            results[role]={'ssl':row[1],'version':row[2],'cipher':row[3]}
        owner.private(self.proof/'api-fixture-tls.json',{'database_container':identifier,'tls_preexisting':enabled,'roles':results})

    def api_environment(self,environment):
        from sqlalchemy.engine import make_url
        project=owner.dev.project_identity(owner.TARGET_CONFIG,self.run_id)
        values={k:v for k,v in environment.items() if k in (*APP_ROLE_KEYS,'SCRIBESWELL_STUDIES_ENABLED',
            'SCRIBESWELL_STUDIES_ACCESS_URL','SCRIBESWELL_STUDIES_SERVICE_KEY','APP_ENV','CORS_ORIGINS',
            'SUPABASE_SECRET_KEY','SUPABASE_SERVICE_ROLE_KEY')}
        values['SUPABASE_URL']='http://supabase_kong_'+project+':8000'
        # Docker DNS resolves the retained container name, not its hexadecimal ID.
        values['SCRIBESWELL_STUDIES_ACCESS_URL']='http://'+self.access_container+':8000'
        for key in APP_ROLE_KEYS:
            if key in values:values[key]=make_url(values[key]).set(host='supabase_db_'+project,port=5432).update_query_dict({'sslmode':'require'}).render_as_string(hide_password=False)
        return values

    def launch_api(self,label,environment,port=None):
        name='scribeswell-api-'+self.run_id+'-'+label
        path=self.proof/('api-'+label+'-private.env');frozen.write_environment(path,self.api_environment(environment))
        network=owner.native_cli.network(owner.TARGET_CONFIG,self.run_id,False,self.run)
        args=app_container_arguments(name,self.api_image,network,path,port)
        args[1:1]=['--label','agri.scribeswell.frozen-run='+self.run_id]
        self.containers[name]=None
        identifier=self.docker('api-'+label+'-start',args).strip()
        if len(identifier)!=64 or any(c not in '0123456789abcdef' for c in identifier):raise RuntimeError('qualification_container_id_invalid')
        self.containers[name]=identifier
        return name

    def api_refusals(self,environment):
        variants=[('migration-role',{'SCRIBESWELL_DATABASE_URL':self.urls['identity_migrator'].render_as_string(hide_password=False)},'Invalid database configuration'),
            ('private-migration-role',{'SCRIBESWELL_STUDIES_DATABASE_URL':self.urls['identity_migrator'].render_as_string(hide_password=False)},'Invalid database configuration'),
            ('provider-key',{'SUPABASE_SERVICE_ROLE_KEY':'synthetic-forbidden-authority'},'Remove obsolete runtime service-key authority'),
            ('provider-secret-key',{'SUPABASE_SECRET_KEY':'synthetic-forbidden-authority'},'Remove obsolete runtime service-key authority'),
            ('production',{'APP_ENV':'production'},'Studies production activation awaits migration and integration qualification')]
        for label,changes,marker in variants:
            name=self.launch_api('refusal-'+label,environment|changes)
            deadline=time.monotonic()+20
            while self.container_state(name)['State']['Running']:
                if time.monotonic()>deadline:raise RuntimeError('qualification_api_refusal_timeout')
                time.sleep(.1)
            state=self.container_state(name)['State']
            output=self.docker('api-'+label+'-logs',['logs',self.containers[name]])
            if state['ExitCode']==0 or state['OOMKilled'] or marker not in output:raise RuntimeError('qualification_api_refusal_reason_invalid:'+label)
            self.stop_one(name)
        owner.private(self.proof/'api-startup-refusals.json',{'cases':[r[0] for r in variants],'all_refused':True,'default_command':True})

    def spawn(self,label,args,env,cwd):
        if label!='scribeswell-http':return super().spawn(label,args,env,cwd)
        self.api_refusals(env)
        self.api_container=self.launch_api('http',env,owner.TARGET_CONFIG['ports']['api'])
        return frozen.ContainerProcess(self,self.api_container)

    def probe_api(self):
        identifier=self.containers[self.api_container]
        value=json.loads(self.docker('api-runtime-probe',['exec',identifier,'python','-B','-c',PROBE]))
        expected=image_sources(self.api_inputs)
        actual={name:record['sha256'] for name,record in value['files'].items() if 'sha256' in record}
        if actual!={n:d for n,d in expected.items() if n.startswith('/app/')} or value['requirements_sha256']!=expected['/tmp/requirements.txt']:
            raise RuntimeError('qualification_api_image_files_invalid')
        directories=set()
        for name in actual:
            path=Path(name).parent
            while str(path)!='/app':directories.add(str(path));path=path.parent
        if {name for name,row in value['files'].items() if row=={'directory':True}}!=directories or any('link' in row for row in value['files'].values()):
            raise RuntimeError('qualification_api_image_membership_invalid')
        fields='{"Image":{{json .Image}},"Cmd":{{json .Config.Cmd}},"User":{{json (index .Config "User")}},"ReadonlyRootfs":{{json .HostConfig.ReadonlyRootfs}},"CapDrop":{{json .HostConfig.CapDrop}},"SecurityOpt":{{json .HostConfig.SecurityOpt}},"PidsLimit":{{json .HostConfig.PidsLimit}},"Memory":{{json .HostConfig.Memory}},"NanoCpus":{{json .HostConfig.NanoCpus}},"NetworkMode":{{json .HostConfig.NetworkMode}},"PortBindings":{{json .HostConfig.PortBindings}},"Tmpfs":{{json .HostConfig.Tmpfs}},"Mounts":{{json .Mounts}},"Privileged":{{json .HostConfig.Privileged}}}'
        restrictions=json.loads(self.docker('api-runtime-restrictions',['inspect','--format',fields,identifier]))
        if not (restrictions['Image']==self.api_image and restrictions['Cmd']==self.api_image_metadata['Cmd']
            and self.api_image_metadata['User']=='10001:10001' and restrictions['User']=='10001:10001'
            and restrictions['ReadonlyRootfs'] and restrictions['CapDrop']==['ALL']
            and restrictions['SecurityOpt']==['no-new-privileges'] and restrictions['PidsLimit']==64
            and restrictions['Memory']==256*1024*1024 and restrictions['NanoCpus']==1000000000
            and restrictions['NetworkMode']==owner.native_cli.network(owner.TARGET_CONFIG,self.run_id,False,self.run)
            and restrictions['PortBindings']=={'8000/tcp':[{'HostIp':'127.0.0.1','HostPort':str(owner.TARGET_CONFIG['ports']['api'])}]}
            and restrictions['Tmpfs']=={'/tmp':'rw,noexec,nosuid,size=16m'} and not restrictions['Mounts']
            and restrictions['Privileged'] is False):raise RuntimeError('qualification_api_hardening_invalid')
        with self.connect() as connection:
            rows=connection.execute('SELECT a.usename,s.ssl,s.version,s.cipher FROM pg_stat_activity a JOIN pg_stat_ssl s ON s.pid=a.pid WHERE a.usename=ANY(%s)',(list(APP_ROLE_KEYS.values()),)).fetchall()
        tls={role:[{'ssl':ssl,'version':version,'cipher':cipher} for user,ssl,version,cipher in rows if user==role] for role in APP_ROLE_KEYS.values()}
        if set(value['sql_tls'])!=set(APP_ROLE_KEYS.values()) or any(row['ssl'] is not True for row in value['sql_tls'].values()):
            raise RuntimeError('qualification_api_runtime_tls_unproven')
        if any(row['ssl'] is not True for sessions in tls.values() for row in sessions):
            raise RuntimeError('qualification_api_resident_tls_invalid')
        owner.private(self.proof/'api-runtime-probe.json',value|{'container_id':identifier,'restrictions':restrictions,'resident_sessions_tls':tls,'dependency_baseline_frozen':False})

    def extra_qualification(self):
        self.probe_api()
        super().extra_qualification()
        self.probe_api_final()

    def probe_api_final(self):
        # A second independent observation proves immutable installed bytes during
        # the inherited signup/expiry path, without a dependency freeze claim.
        before=json.loads((self.proof/'api-runtime-probe.json').read_bytes())
        after=json.loads(self.docker('api-final-runtime-probe',['exec',self.containers[self.api_container],'python','-B','-c',PROBE]))
        if any(before[key]!=after[key] for key in ('files','requirements_sha256','dependencies','dependency_files')):raise RuntimeError('qualification_api_runtime_drift')
        owner.private(self.proof/'api-final-inspection.json',{'inputs':self.api_inventory(),'image_id':self.api_image,'installed_dependency_files_unchanged':True,'all_inherited_oracles_completed':True})


def qualify():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    for name in ('supabase','proof','source-root','qualification','context','python','uv','cache'):parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args()
    ApiImageQualification(args.run_id,args.supabase,args.proof,source_root=args.source_root,
        qualification=args.qualification,context=args.context,python=args.python,uv=args.uv,cache=args.cache).execute()
