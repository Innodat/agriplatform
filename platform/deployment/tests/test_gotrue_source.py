"""Repeatable selected publisher conformance; explicit pinned tool artifact required.

Set KDG_PROFILE_TOOLCHAIN_RUN_ID to an existing toolchain owner receipt UUID.
No downloads, Docker access or runtime qualification occurs in this test.
See fixtures/supabase-gotrue-source/README.md for fresh-checkout preparation.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import toolchain
import create_profile
from create_profile_fixtures import boundary_fixture, target_fixture


class GotruePublisherConformance(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('KDG_PROFILE_TOOLCHAIN_RUN_ID'),
                         'requires explicit qualified Node artifact; see GoTrue source README')
    def test_selected_publisher_environment_container_and_argv(self):
        run_id = os.environ['KDG_PROFILE_TOOLCHAIN_RUN_ID']
        self.assertEqual(str(uuid.UUID(run_id)), run_id)
        root = ROOT
        payload = root / 'platform/deployment/.local/kdg-toolchains' / run_id / 'payload'
        receipt_path = payload.parent / 'receipt.json'
        receipt_raw = receipt_path.read_bytes()
        receipt = json.loads(receipt_raw)
        self.assertIs(receipt.get('toolchain_ready'), True)
        node = payload / 'node/bin/node'
        h = lambda raw: hashlib.sha256(raw).hexdigest()
        self.assertEqual(h(node.read_bytes()), '5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657')
        self.assertTrue(toolchain.payload_fingerprint(payload) == receipt['payload'],
                        'tool artifact differs from owner receipt')
        source=root/'platform/deployment/fixtures/supabase-gotrue-source'
        manifest_raw=(source/'sources.json').read_bytes();assert h(manifest_raw)=='42db3a50316b5aa434860f5d9dd87d682f20defd54751b85a0f8bc363283384c'
        manifest=json.loads(manifest_raw);raws={f.name:f.read_bytes() for f in source.iterdir() if f.name in ('gotrue.service.ts', 'go-duration.ts', 'password-requirements.ts', 'internal-db-connection.ts', 'docker-ids.ts', 'slim-images.ts')}
        for name,raw in raws.items(): assert h(raw)==manifest[name]['sha256']
        inputs_raw=(source/'selected-input.json').read_bytes();authority_raw=(source/'public-environment.json').read_bytes()
        assert h(authority_raw)=='29a7f4067b053c16525c5e8025eb0cb00b6e1fc42c4403ad51aeb9c8b7e7ef46'
        assert h(inputs_raw)=='0192b3c338ca65aaec3de13770583338855d2199c02be8b1eb4fd88e7eafea4c'
        authority=json.loads(authority_raw);inputs=json.loads(inputs_raw)
        old=root/'platform/deployment/fixtures/supabase-kong-source';old_raw=(old/'sources.json').read_bytes()
        assert h(old_raw)=='054cb89c47d19e55b46eeb5d0c9b4b81d04316ede0facb437c4628ff09b08da1'
        old_manifest=json.loads(old_raw);extra={name:(old/name).read_bytes() for name in ('Defaults.ts','docker-create-args.ts','container-lifecycle.ts')}
        for name,raw in extra.items(): assert h(raw)==next(v['sha256'] for k,v in old_manifest.items() if k.rsplit('/',1)[-1]==name)
        fixture=boundary_fixture();target=target_fixture();fixture['network']['Id']='b'*64
        fixture.update(origins=target['origins'],callback_urls=target['callback_urls'])
        reference=next(v for k,v in fixture['selection_plan'].items() if '/supabase/gotrue:' in k)
        def strip_imports(text):return re.sub(r'^import\b[\s\S]*?;\s*\n','',text,flags=re.M)
        slim=raws['slim-images.ts'].decode()
        selected_slim=re.search(r'const SLIM_IMAGE_PREFIX = [^;]+;',slim)[0]+'\n'
        for name in ('isSlimImageRef','usesSlimImageRuntime'):
            selected_slim+=re.search(r'export function '+name+r'\([^\n]+\{\n[\s\S]*?^\}',slim,re.M)[0]+'\n'
        prefix=('import { formatGoDuration,parseGoDuration } from "./go-duration.ts";\n'
                'import { DEFAULT_SIGNING_KEY } from "./Defaults.ts";\n'
                'import { passwordRequirementsToChar } from "./password-requirements.ts";\n'
                'import { startInternalDbUrl,startInternalDbPassword } from "./internal-db-connection.ts";\n'
                'import { serviceContainerName } from "./docker-ids.ts";\n'
                'import { usesSlimImageRuntime } from "./slim-selected.ts";\n')
        wrapper={'slim':False,'image':reference,'projectId':fixture['project'],'networkId':'b'*64,
                 'dbUrl':'postgresql://postgres:postgres@127.0.0.1:55482/postgres'}
        with tempfile.TemporaryDirectory(prefix='gotrue-public-proof-') as directory:
            work=Path(directory)
            for name,raw in {**raws,**extra}.items():(work/name).write_bytes(raw)
            (work/'builder.ts').write_text(prefix+strip_imports(raws['gotrue.service.ts'].decode()))
            (work/'slim-selected.ts').write_text(selected_slim)
            (work/'args.ts').write_text(strip_imports(extra['docker-create-args.ts'].decode()))
            # Linux extra-host and lifecycle labels are supplied context, not executed lifecycle proof.
            main=('import {buildGotrueEnv,buildGotrueContainerSpec} from "./builder.ts";\n'
                  'import {buildStartContainerCreateArgs} from "./args.ts";\n'
                  'const input='+json.dumps(inputs)+';\nconst context='+json.dumps(wrapper)+';\n'
                  'const {dbHost,dbPassword,...env}=input;\n'
                  'const spec=buildGotrueContainerSpec({...context,env});\n'
                  'spec.extraHosts=["host.docker.internal:host-gateway"];\n'
                  'spec.labels={"com.supabase.cli.project":context.projectId,"com.docker.compose.project":context.projectId,'
                  '"com.supabase.cli.workdir":"/private"};\n'
                  'console.log(JSON.stringify({environment:buildGotrueEnv(input),spec,args:buildStartContainerCreateArgs(spec)}));\n')
            (work/'main.ts').write_text(main)
            result=subprocess.run([str(node),str(work/'main.ts')],env={'PATH':'/usr/bin:/bin','NODE_NO_WARNINGS':'1'},capture_output=True,timeout=10)
            assert result.returncode==0,'pinned pure GoTrue profile proof failed'
            value=json.loads(result.stdout)
        assert value['environment']==authority['environment'],'publisher environment differs from public fixture'
        assert value['environment']==create_profile.gotrue_service_environment(fixture),'runtime environment differs from publisher'
        assert value['args']==create_profile.gotrue_service_request(fixture),'runtime argv differs from publisher'
        assert value['spec']['binds']==[] and value['spec'].get('ports',[])==[]
        assert 'entrypoint' not in value['spec'] and 'cmd' not in value['spec']
        assert all((source/name).read_bytes()==raw for name,raw in raws.items())
        assert all((old/name).read_bytes()==raw for name,raw in extra.items())
        assert (source/'sources.json').read_bytes()==manifest_raw and (old/'sources.json').read_bytes()==old_raw
        assert (source/'selected-input.json').read_bytes()==inputs_raw and (source/'public-environment.json').read_bytes()==authority_raw
        assert receipt_path.read_bytes()==receipt_raw and h(node.read_bytes())=='5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657'
