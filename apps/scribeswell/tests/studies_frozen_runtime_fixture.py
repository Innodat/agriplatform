"""Single-use app consumer qualification of the reviewed frozen Access image.

Preparation executes from the complete immutable owner archive. Only the new
build context receives a bundle; runtime uses the unchanged Dockerfile command.
Private environment files and logs remain in the exclusive fixture proof.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import time

import studies_owner_fixture as owner
import studies_readiness_integration_fixture as integration
from studies_readiness_integration_fixture import ReadinessIntegrationQualification

RUNTIME_MODULES=('main.py','organization_check.py','studies_access.py','studies_identity.py',
    'studies_contract.py','studies_readiness.py','identity_preferences.py','caller_policy.py',
    'capability_contract.py','capability_check.py','identity_context.py','discovery.py',
    'discovery_contract.py','discovery_query.py')
INPUTS=('pyproject.toml','uv.lock',*RUNTIME_MODULES,'deployment/verify_runtime.py',
    'deployment/package_runtime.py','deployment/Dockerfile','deployment/Dockerfile.dockerignore')


def digest(path):return sha256(path.read_bytes()).hexdigest()


def app_sources():
    result=integration.app_sources()
    for name in ('tests/studies_frozen_runtime_fixture.py','tests/test_studies_frozen_runtime.py',
                 'tools/py/qualify_studies_frozen_runtime.py'):
        path=owner.APP/name;result[path]=digest(path)
    return result


def runtime_inventory(root):
    return {str(path.relative_to(root)):value for path,value in integration.owner_module_sources(root).items()}


def require_runtime_sources(root,expected):
    if set(expected)!=set(RUNTIME_MODULES) or runtime_inventory(root)!=expected:
        raise RuntimeError('qualification_runtime_membership_invalid')


def write_environment(path,environment):
    if any(not isinstance(k,str) or not k.replace('_','').isalnum() or not isinstance(v,str)
           or any(c in v for c in ('\n','\r','\0')) for k,v in environment.items()):
        raise ValueError('qualification_environment_invalid')
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as output:
        for key,value in sorted(environment.items()):output.write(key+'='+value+'\n')


def write_runtime_environment(path,environment):
    # Owner preparation's genuine compact JSON includes its terminal newline.
    # Docker --env NAME inherits that exact process value; env files cannot.
    values=dict(environment)
    inherited={}
    if 'STUDIES_READINESS_JSON' in values:
        inherited['STUDIES_READINESS_JSON']=values.pop('STUDIES_READINESS_JSON')
    write_environment(path,values)
    return inherited


def container_arguments(name,image,network,environment,port=None):
    args=['run','--detach','--name',name,'--network',network,'--read-only','--user','65532:65532',
        '--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
        '--pids-limit','64','--memory','256m','--cpus','1','--env-file',str(environment)]
    if port is not None:args+=['--publish','127.0.0.1:'+str(port)+':8000']
    return args+[image]


class ContainerProcess:
    """Health polling observes the actual container, without a long-lived client."""
    def __init__(self,qualification,name):self.qualification=qualification;self.name=name
    def poll(self):
        state=self.qualification.container_state(self.name)['State']
        return None if state['Running'] else state['ExitCode']


class FrozenRuntimeQualification(ReadinessIntegrationQualification):
    qualification_scope=('Exact archived Identity0026/Access0019 frozen Access Python3.15 default image '
        'with inherited real local browser/signup/mail/SQL integration; no production activation, '
        'whole-app production image, external SMTP, environment release/recovery or device claim')

    def __init__(self,run_id,cli,proof,*,source_root,qualification,context,python,uv,cache):
        self.context=Path(context).absolute()
        if self.context.exists() or self.context.is_symlink():raise FileExistsError('qualification_context_exists')
        self.python=Path(python).resolve(strict=True);self.uv=Path(uv).resolve(strict=True)
        self.cache=Path(cache).resolve(strict=True)
        if not self.python.is_file() or not self.uv.is_file() or not self.cache.is_dir():
            raise ValueError('qualification_toolchain_invalid')
        self.containers={};self.container_stops=[];self.docker_sequence=0
        super().__init__(run_id,cli,proof,source_root=source_root,qualification=qualification)
        self.frozen_sources=app_sources()
        self.package_inputs={name:digest(self.owner_access/name) for name in INPUTS}
        self.tool_sources={self.python:digest(self.python),self.uv:digest(self.uv)}
        self.live_bundle=owner.ACCESS/'runtime-bundle'
        self.live_bundle_files=self.bundle_inventory(self.live_bundle)
        owner.private(self.proof/'frozen-inputs.json',self.frozen_inventory())

    @staticmethod
    def bundle_inventory(root):
        # Include links and directory membership without following links outside
        # the retained bundle. File contents are always independently hashed.
        return {str(path.relative_to(root)):({'link':os.readlink(path)} if path.is_symlink()
            else {'sha256':digest(path)} if path.is_file() else {'directory':True})
            for path in sorted(root.rglob('*'))} if root.exists() else None

    def frozen_inventory(self):
        return {'app':{str(p.relative_to(owner.ROOT)):d for p,d in self.frozen_sources.items()},
            'package_inputs':self.package_inputs,'tools':{str(p):d for p,d in self.tool_sources.items()},
            'live_bundle':self.live_bundle_files,'live_bundle_path':str(self.live_bundle)}

    def verify_sources(self):
        super().verify_sources()
        if not hasattr(self,'frozen_sources'):return
        if app_sources()!=self.frozen_sources:raise RuntimeError('qualification_frozen_driver_changed')
        if self.package_inputs!={n:digest(self.owner_access/n) for n in INPUTS}:
            raise RuntimeError('qualification_package_inputs_changed')
        if any(digest(p)!=d for p,d in self.tool_sources.items()):raise RuntimeError('qualification_toolchain_changed')
        if self.bundle_inventory(self.live_bundle)!=self.live_bundle_files:
            raise RuntimeError('qualification_original_bundle_changed')
        if hasattr(self,'bundle_manifest_sha256'):
            verifier=runpy.run_path(str(self.owner_access/'deployment/verify_runtime.py'))
            verifier['verify'](self.packaged_owner,self.packaged_owner/'runtime-bundle')
            if digest(self.packaged_owner/'runtime-bundle/provenance.json')!=self.bundle_manifest_sha256:
                raise RuntimeError('qualification_bundle_changed')
            require_runtime_sources(self.packaged_owner/'runtime-bundle/owner-code',self.runtime_sources)

    def docker(self,label,args,*,timeout=60,expected=0,environment=None):
        # stdout/stderr are retained privately. Inspect calls select only safe
        # fields; never dump Config.Env, request values or vendor diagnostics.
        self.docker_sequence+=1
        path=self.proof/(f'docker-{self.docker_sequence:03d}-'+label+'.log')
        started=time.monotonic()
        try:
            result=subprocess.run(['docker',*map(str,args)],cwd=owner.ROOT,
                env={'PATH':'/usr/bin:/bin','DOCKER_HOST':'unix:///var/run/docker.sock',**(environment or {})},
                stdin=subprocess.DEVNULL,capture_output=True,timeout=timeout)
        except subprocess.TimeoutExpired as error:
            data=(error.stdout or b'')+(error.stderr or b'')
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as out:out.write(data)
            self.events.append({'stage':label,'outcome':'timed-out','log_sha256':sha256(data).hexdigest()})
            raise RuntimeError('qualification_docker_timeout:'+label) from None
        data=result.stdout+result.stderr
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as out:out.write(data)
        self.events.append({'stage':label,'exit_code':result.returncode,
            'seconds':round(time.monotonic()-started,3),'log':path.name,'log_sha256':sha256(data).hexdigest()})
        if (result.returncode!=0) if expected else (result.returncode==0):
            return (data if expected or args[0]=='logs' else result.stdout).decode()
        raise RuntimeError('qualification_docker_failed:'+label)

    def package_image(self):
        self.verify_sources();self.validate_owner_qualification()
        self.context.mkdir(parents=True,mode=0o700,exist_ok=False)
        self.packaged_owner=self.context/'services/access';self.packaged_owner.mkdir(parents=True)
        for name in INPUTS:
            destination=self.packaged_owner/name;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(self.owner_access/name,destination)
        self.command('offline-package',[sys.executable,'-B',self.owner_access/'deployment/package_runtime.py',
            '--python',self.python,'--uv',self.uv,'--cache',self.cache,
            '--output',self.packaged_owner/'runtime-bundle'],timeout=240)
        manifest_path=self.packaged_owner/'runtime-bundle/provenance.json'
        manifest=json.loads(manifest_path.read_bytes())
        if manifest['inputs']!=self.package_inputs:raise RuntimeError('qualification_bundle_inputs_invalid')
        self.runtime_sources={name:self.package_inputs[name] for name in RUNTIME_MODULES}
        require_runtime_sources(self.packaged_owner/'runtime-bundle/owner-code',self.runtime_sources)
        self.bundle_manifest_sha256=digest(manifest_path)
        self.image_tag='scribeswell-frozen-access:'+self.run_id
        self.docker('image-build',['build','--network','none','--pull=false','-t',self.image_tag,
            '-f',self.packaged_owner/'deployment/Dockerfile',self.context],timeout=240)
        self.image_id=json.loads(self.docker('image-id',['image','inspect','--format','{{json .Id}}',self.image_tag]))
        self.packaging_refusals()
        owner.private(self.proof/'image-package.json',{'image':self.image_tag,'image_id':self.image_id,
            'context':str(self.context),'manifest_sha256':self.bundle_manifest_sha256,
            'inputs':manifest['inputs'],'python_version':manifest['python_version'],'uv_version':manifest['uv_version']})
        self.verify_sources()

    def packaging_refusals(self):
        negative=self.context/'negative';target=negative/'services/access';target.mkdir(parents=True)
        for name in INPUTS:
            destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(self.packaged_owner/name,destination)
        shutil.copytree(self.packaged_owner/'runtime-bundle',target/'runtime-bundle',symlinks=True,copy_function=os.link)
        args=['build','--target','verified','--network','none','--pull=false','-f',target/'deployment/Dockerfile',negative]
        def refused(label):
            output=self.docker(label,args,timeout=180,expected=1)
            if 'access_runtime_verification_failed' not in output:
                raise RuntimeError('qualification_docker_refusal_reason_invalid:'+label)
        lock=target/'uv.lock';original=lock.read_bytes();lock.write_bytes(original+b'\n# stale fixture input\n')
        refused('stale-lock-refused');lock.write_bytes(original)
        extra=target/'runtime-bundle/owner-code/foreign.py';extra.write_text('unexpected = True\n')
        refused('extra-module-refused');extra.unlink()
        # Unlink before writing: the original immutable payload is hard-linked.
        main=target/'runtime-bundle/owner-code/main.py';data=main.read_bytes();main.unlink();main.write_bytes(data+b'\n# altered fixture payload\n')
        verifier=runpy.run_path(str(self.owner_access/'deployment/verify_runtime.py'))
        manifest=target/'runtime-bundle/provenance.json';value=json.loads(manifest.read_bytes());manifest.unlink()
        value['files']=verifier['inventory'](target/'runtime-bundle');manifest.write_text(json.dumps(value))
        refused('altered-reinventoried-source-refused')
        owner.private(self.proof/'packaging-refusals.json',{'stale_lock':True,'extra_importable_module':True,
            'altered_source_with_recomputed_inventory':True,'actual_docker_build_refusals':True})

    def prepare_owners(self):
        self.package_image()
        # The archive qualification validation already ran before packaging.
        with integration.selected_owner(self.source_root):
            super(ReadinessIntegrationQualification,self).prepare_owners()

    def container_environment(self,environment):
        project=owner.dev.project_identity(owner.TARGET_CONFIG,self.run_id)
        result={k:v for k,v in environment.items() if k in ('SCRIBESWELL_SERVICE_KEY',
            'STUDIES_READINESS_JSON','SUPABASE_ANON_KEY','STUDIES_ACCESS_DATABASE_URL',
            'STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL')}
        result['SUPABASE_URL']='http://supabase_kong_'+project+':8000'
        from sqlalchemy.engine import make_url
        for key in ('STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL'):
            if key in result:
                result[key]=make_url(result[key]).set(host='supabase_db_'+project,port=5432).render_as_string(hide_password=False)
        return result

    def launch_container(self,label,environment,port=None):
        name='scribeswell-frozen-'+self.run_id+'-'+label
        envpath=self.proof/(label+'-private.env')
        inherited=write_runtime_environment(envpath,self.container_environment(environment))
        network=owner.native_cli.network(owner.TARGET_CONFIG,self.run_id,False,self.run)
        args=container_arguments(name,self.image_id,network,envpath,port)
        args[1:1]=['--label','agri.scribeswell.frozen-run='+self.run_id]
        if inherited:args[1:1]=['--env','STUDIES_READINESS_JSON']
        self.containers[name]=None
        raw=self.docker(label+'-start',args,environment=inherited)
        identifier=raw.strip()
        if len(identifier)!=64 or any(c not in '0123456789abcdef' for c in identifier):
            raise RuntimeError('qualification_container_id_invalid')
        self.containers[name]=identifier
        return name

    def container_state(self,name):
        reference=self.containers[name] or name
        fmt='{"Id":{{json .Id}},"State":{"Running":{{json .State.Running}},"ExitCode":{{json .State.ExitCode}},"OOMKilled":{{json .State.OOMKilled}}},"Run":{{json (index .Config.Labels "agri.scribeswell.frozen-run")}}}'
        row=json.loads(self.docker('container-state',['inspect','--format',fmt,reference]))
        if self.containers[name] is None:
            if row.get('Run')!=self.run_id:raise RuntimeError('qualification_foreign_container_refused')
            self.containers[name]=row['Id']
        elif row['Id']!=self.containers[name]:raise RuntimeError('qualification_container_id_changed')
        return row

    def startup_refusals(self):
        artifact=json.loads(self.readiness_raw)
        variants=[('missing-artifact',{'STUDIES_READINESS_JSON':None}),('malformed-artifact',{'STUDIES_READINESS_JSON':'{}'})]
        for name in ('STUDIES_ACCESS_DATABASE_URL','STUDIES_IDENTITY_DATABASE_URL','STUDIES_IDENTITY_SETUP_DATABASE_URL'):
            variants.append(('missing-'+name.lower(),{name:None}))
        for label,change in [('old-version',{'schema_version':1}),('later-head',{'identity_revision':'identity_0027'}),
            ('stale-sources',{'runtime_sources':{}}),('wrong-pair',{'identity_revision':'identity_0025','access_revision':'access_0018'})]:
            variants.append((label,{'STUDIES_READINESS_JSON':json.dumps(artifact|change)}))
        variants.append(('wrong-role',{'STUDIES_ACCESS_DATABASE_URL':self.urls['access_migrator'].render_as_string(hide_password=False)}))
        for label,changes in variants:
            env={k:v for k,v in (self.runtime_environment|changes).items() if v is not None}
            name=self.launch_container('refusal-'+label,env)
            deadline=time.monotonic()+15
            while self.container_state(name)['State']['Running']:
                if time.monotonic()>=deadline:raise RuntimeError('qualification_startup_refusal_timeout')
                time.sleep(.1)
            state=self.container_state(name)['State']
            if state['ExitCode']==0 or state['OOMKilled']:raise RuntimeError('qualification_startup_refusal_invalid')
            output=self.docker(label+'-logs',['logs',self.containers[name]])
            if 'RuntimeError: studies_configuration_invalid' not in output:
                raise RuntimeError('qualification_startup_refusal_reason_invalid')
            self.stop_one(name)
        owner.private(self.proof/'startup-refusals.json',{'cases':[label for label,_ in variants],
            'unchanged_default_image_command':True,'all_refused':True})

    def spawn(self,label,args,env,cwd):
        if label!='access-http':return super().spawn(label,args,env,cwd)
        artifact=json.loads(self.readiness_raw)
        if artifact['runtime_sources']!=self.runtime_sources:
            raise RuntimeError('qualification_artifact_image_sources_mismatch')
        name=self.launch_container('access',env,owner.TARGET_CONFIG['ports']['access_http'])
        self.access_container=name
        return ContainerProcess(self,name)

    def probe_image(self):
        code='''import os,sys,json,platform,hashlib,importlib.util,importlib.metadata
from pathlib import Path
from importlib.machinery import all_suffixes
assert platform.python_version()=='3.15.0' and os.getuid()==65532
assert importlib.util.find_spec('pytest') is None
assert not any('MIGRATION' in k for k in os.environ)
root=Path('/srv');suffixes=tuple(all_suffixes())
sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p.name.endswith(suffixes)}
try:Path('/srv/forbidden-proof').write_text('forbidden')
except OSError as error:assert error.errno==30
else:raise RuntimeError('root_writable')
dependencies={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=['/opt/site-packages'])}
files={str(p.relative_to('/opt/site-packages')):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/opt/site-packages').rglob('*') if p.is_file()}
print(json.dumps({'python_version':platform.python_version(),'executable':sys.executable,'uid':os.getuid(),'pytest_absent':True,'migration_credentials_absent':True,'read_only':True,'sources':sources,'dependencies':dependencies,'dependency_files':files}))'''
        identifier=self.containers[self.access_container]
        value=json.loads(self.docker('independent-runtime-probe',['exec',identifier,'/opt/python/bin/python3.15','-B','-c',code]))
        if value['sources']!=self.runtime_sources:raise RuntimeError('qualification_image_sources_invalid')
        manifest=json.loads((self.packaged_owner/'runtime-bundle/provenance.json').read_bytes())
        dependencies={n.removeprefix('site-packages/'):d['sha256'] for n,d in manifest['files'].items()
            if n.startswith('site-packages/') and 'sha256' in d}
        if dependencies!=value['dependency_files']:raise RuntimeError('qualification_dependency_provenance_invalid')
        fmt='{"Image":{{json .Image}},"Cmd":{{json .Config.Cmd}},"User":{{json .Config.User}},"ReadonlyRootfs":{{json .HostConfig.ReadonlyRootfs}},"CapDrop":{{json .HostConfig.CapDrop}},"SecurityOpt":{{json .HostConfig.SecurityOpt}},"PidsLimit":{{json .HostConfig.PidsLimit}},"Memory":{{json .HostConfig.Memory}},"NanoCpus":{{json .HostConfig.NanoCpus}},"NetworkMode":{{json .HostConfig.NetworkMode}}}'
        config=json.loads(self.docker('independent-runtime-restrictions',['inspect','--format',fmt,identifier]))
        image_cmd=json.loads(self.docker('default-image-command',['image','inspect','--format','{{json .Config.Cmd}}',self.image_id]))
        if not (config['Image']==self.image_id and config['Cmd']==image_cmd and 'main:app' in image_cmd
            and config['User']=='65532:65532' and config['ReadonlyRootfs'] and config['CapDrop']==['ALL']
            and config['SecurityOpt']==['no-new-privileges'] and config['PidsLimit']==64
            and config['Memory']==256*1024*1024 and config['NanoCpus']==1000000000):
            raise RuntimeError('qualification_runtime_restrictions_invalid')
        owner.private(self.proof/'runtime-probe.json',value|{'container_id':identifier,'restrictions':config})

    def extra_qualification(self):
        self.probe_image()
        super().extra_qualification()
        self.verify_sources()
        owner.private(self.proof/'frozen-final-inspection.json',{'inputs':self.frozen_inventory(),
            'manifest_sha256':self.bundle_manifest_sha256,'image_id':self.image_id,
            'all_inherited_oracles_completed':True,'exact_runtime_sources':self.runtime_sources})

    def stop_one(self,name):
        identifier=self.containers[name]
        if identifier is None:identifier=self.container_state(name)['Id']
        failure=None
        try:self.docker('container-stop',['stop','--time','20',identifier],timeout=30)
        except Exception as error:failure=error
        row=self.container_state(name)
        if row['State']['Running']:
            self.docker('container-kill',['kill',identifier],timeout=10)
            row=self.container_state(name)
        if row['State']['Running']:raise OSError('qualification_container_stop_unconfirmed')
        record={'container_id':identifier,'termination_confirmed':True,
            'exit_code':row['State']['ExitCode'],'oom_killed':row['State']['OOMKilled'],
            'forced':row['State']['ExitCode']==137,'stop_command_failed':failure is not None}
        self.container_stops.append(record)
        del self.containers[name]
        try:self.docker('container-final-logs',['logs',identifier])
        except Exception:record['log_retrieval_failed']=True
        if failure:raise OSError('qualification_container_stop_command_failed') from None

    def stop_containers(self):
        failed=False
        for name in list(self.containers):
            try:self.stop_one(name)
            except Exception:
                failed=True;self.container_stops.append({'name':name,'termination_confirmed':False})
        owner.private(self.proof/'container-shutdown.json',{'containers':self.container_stops,
            'all_termination_confirmed':not failed,'forced':any(r.get('forced') for r in self.container_stops)})
        if failed:raise OSError('qualification_container_stop_unconfirmed')

    def wrapper(self,action):
        if action!='stop':return super().wrapper(action)
        try:self.stop_containers()
        finally:super().wrapper(action)


def qualify():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id',required=True)
    for name in ('supabase','proof','source-root','qualification','context','python','uv','cache'):
        parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args()
    FrozenRuntimeQualification(args.run_id,args.supabase,args.proof,source_root=args.source_root,
        qualification=args.qualification,context=args.context,python=args.python,uv=args.uv,cache=args.cache).execute()
