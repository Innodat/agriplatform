"""Offline numeric-code template intent; never SMTP or Auth runtime evidence.

Run with KDG_PROFILE_TOOLCHAIN_RUN_ID selecting an existing qualified Node artifact
to include the publisher builder comparison. Also set KDG_EMAIL_CODE_REQUIRE_PUBLISHER=1
for qualification: missing selection fails rather than skips. Ordinary discovery may skip.
No tool installation, Docker or network.
"""
from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import toolchain

FIXTURE = ROOT / 'platform/deployment/fixtures/email-code-v1'


def candidate():
    return tomllib.loads((FIXTURE / 'config.toml').read_text())


class NumericEmailCodeContract(unittest.TestCase):
    def test_existing_account_candidate_names_a_code_only_template(self):
        self.assertTrue((FIXTURE / 'config.toml').is_file(), 'numeric-code config candidate missing')
        value = candidate()
        self.assertEqual(set(value), {'auth'})
        auth = value['auth']
        self.assertEqual(set(auth), {'enable_signup', 'enable_anonymous_sign_ins', 'enable_manual_linking', 'email'})
        for key in ['enable_signup', 'enable_anonymous_sign_ins', 'enable_manual_linking']:
            self.assertIs(auth[key], False)
        email = auth['email']
        self.assertEqual(set(email), {'enable_signup', 'otp_length', 'otp_expiry', 'max_frequency', 'template'})
        # CLI maps this misleadingly named flag to GOTRUE_EXTERNAL_EMAIL_ENABLED.
        self.assertIs(email['enable_signup'], True)
        self.assertEqual(type(email['otp_length']), int)
        self.assertEqual(email['otp_length'], 6)
        self.assertEqual(email['otp_expiry'], 3600)
        self.assertEqual(email['max_frequency'], '60s')
        self.assertEqual(email['template'], {'magic_link': {
            'subject': 'Your sign-in code',
            'content_path': './supabase/templates/sign-in.html',
        }})

    def test_template_contains_one_visible_token_and_no_link_or_external_resource(self):
        self.assertTrue((FIXTURE / 'sign-in.html').is_file(), 'numeric-code template missing')
        raw = (FIXTURE / 'sign-in.html').read_text()
        self.assert_code_template(raw)

    def test_title_only_code_is_rejected(self):
        raw = (FIXTURE / 'sign-in.html').read_text().replace('{{ .Token }}', '').replace('<title>', '<title>{{ .Token }}')
        with self.assertRaises(AssertionError):
            self.assert_code_template(raw)

    def assert_code_template(self, raw):
        self.assertLess(len(raw.encode()), 4096)
        self.assertEqual(re.findall(r'{{[\s\S]*?}}', raw), ['{{ .Token }}'])
        self.assertNotIn('{{', raw.replace('{{ .Token }}', ''))
        self.assertNotIn('}}', raw.replace('{{ .Token }}', ''))
        self.assertNotRegex(raw, r'(?i)https?:|javascript:|data:|confirmationurl|tokenhash|redirectto')
        testcase = self

        class Content(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.body_text = []
                self.counts = {}
                self.stack = []

            def handle_starttag(self, tag, attrs):
                testcase.assertIn(tag, {'html', 'head', 'title', 'body', 'h1', 'p', 'strong'})
                testcase.assertEqual(attrs, [('lang', 'en')] if tag == 'html' else [])
                self.counts[tag] = self.counts.get(tag, 0) + 1
                if tag == 'html': testcase.assertEqual(self.stack, [])
                elif tag in {'head', 'body'}: testcase.assertEqual(self.stack, ['html'])
                elif tag == 'title': testcase.assertEqual(self.stack, ['html', 'head'])
                else: testcase.assertIn('body', self.stack)
                self.stack.append(tag)

            def handle_endtag(self, tag):
                testcase.assertTrue(self.stack)
                testcase.assertEqual(self.stack.pop(), tag)

            def handle_data(self, data):
                self.text.append(data)
                if 'body' in self.stack: self.body_text.append(data)

            def handle_comment(self, _data):
                testcase.fail('template comments must not conceal directives')

        content = Content()
        content.feed(raw)
        content.close()
        self.assertFalse(content.stack)
        for tag in ['html', 'head', 'title', 'body']:
            self.assertEqual(content.counts.get(tag), 1)
        text = ''.join(content.body_text)
        self.assertIn('{{ .Token }}', text)
        self.assertIn('six-digit code', text)
        self.assertIn('Return to the app', text)
        self.assertNotIn('3600', text)  # Do not promise delivery time or a remaining lifetime.

    def test_default_native_configuration_stays_unactivated(self):
        target = json.loads((ROOT / 'platform/deployment/environments/kdg-local.json').read_text())
        value = tomllib.loads(dev.configuration(target, '00000000-0000-4000-8000-000000000001').decode())
        self.assertIs(value['local_smtp']['enabled'], False)
        self.assertNotIn('smtp', value['auth']['email'])
        self.assertNotIn('template', value['auth']['email'])
        self.assertIs(value['auth']['email']['enable_signup'], False)
        self.assertIs(value['auth']['enable_signup'], False)

    @unittest.skipUnless(os.environ.get('KDG_PROFILE_TOOLCHAIN_RUN_ID') or os.environ.get('KDG_EMAIL_CODE_REQUIRE_PUBLISHER') == '1',
                         'publisher proof requires explicit qualified Node artifact')
    def test_pinned_publisher_maps_candidate_to_matching_gotrue_and_kong_paths(self):
        run_id = os.environ.get('KDG_PROFILE_TOOLCHAIN_RUN_ID')
        self.assertTrue(run_id, 'publisher qualification requires KDG_PROFILE_TOOLCHAIN_RUN_ID')
        self.assertEqual(str(uuid.UUID(run_id)), run_id)
        payload = ROOT / 'platform/deployment/.local/kdg-toolchains' / run_id / 'payload'
        receipt_raw = (payload.parent / 'receipt.json').read_bytes()
        receipt = json.loads(receipt_raw)
        self.assertIs(receipt.get('toolchain_ready'), True)
        node = payload / 'node/bin/node'
        h = lambda raw: hashlib.sha256(raw).hexdigest()
        self.assertEqual(h(node.read_bytes()), '5a7b8a3cf5ccb57d297519754fd73238f64cf560afd0ef19a2f9bf7384cbb657')
        self.assertEqual(toolchain.payload_fingerprint(payload), receipt['payload'])
        gotrue = ROOT / 'platform/deployment/fixtures/supabase-gotrue-source'
        kong = ROOT / 'platform/deployment/fixtures/supabase-kong-source'
        manifest_raw = (gotrue / 'sources.json').read_bytes()
        kong_manifest_raw = (kong / 'sources.json').read_bytes()
        self.assertEqual(h(manifest_raw), '42db3a50316b5aa434860f5d9dd87d682f20defd54751b85a0f8bc363283384c')
        self.assertEqual(h(kong_manifest_raw), '054cb89c47d19e55b46eeb5d0c9b4b81d04316ede0facb437c4628ff09b08da1')
        manifest, kong_manifest = json.loads(manifest_raw), json.loads(kong_manifest_raw)
        names = ['gotrue.service.ts', 'go-duration.ts', 'password-requirements.ts', 'internal-db-connection.ts', 'docker-ids.ts']
        raws = {name: (gotrue / name).read_bytes() for name in names}
        for name, raw in raws.items():
            self.assertEqual(h(raw), manifest[name]['sha256'])
        defaults, kong_raw = (kong / 'Defaults.ts').read_bytes(), (kong / 'kong.service.ts').read_bytes()
        for name, raw in [('Defaults.ts', defaults), ('kong.service.ts', kong_raw)]:
            self.assertEqual(h(raw), next(v['sha256'] for k, v in kong_manifest.items() if k.rsplit('/', 1)[-1] == name))
        inputs_raw = (gotrue / 'selected-input.json').read_bytes()
        self.assertEqual(h(inputs_raw), '0192b3c338ca65aaec3de13770583338855d2199c02be8b1eb4fd88e7eafea4c')
        inputs = json.loads(inputs_raw)
        auth = candidate()['auth']
        inputs.update(enableSignup=auth['enable_signup'], enableAnonymousSignIns=auth['enable_anonymous_sign_ins'], enableManualLinking=auth['enable_manual_linking'])
        # Supply resolved scalar input; this is not the CLI config parser or file reader.
        inputs['email'].update(auth['email'])
        strip = lambda value: re.sub(r'^import\b[\s\S]*?;\s*\n', '', value, flags=re.M)
        prefix = ('import {formatGoDuration,parseGoDuration} from "./go-duration.ts";\n'
                  'import {DEFAULT_SIGNING_KEY} from "./Defaults.ts";\n'
                  'import {passwordRequirementsToChar} from "./password-requirements.ts";\n'
                  'import {startInternalDbPassword,startInternalDbUrl} from "./internal-db-connection.ts";\n'
                  'import {serviceContainerName} from "./docker-ids.ts";\n')
        before = {p: p.read_bytes() for p in [FIXTURE / 'config.toml', FIXTURE / 'sign-in.html', gotrue / 'selected-input.json', gotrue / 'public-environment.json']}
        with tempfile.TemporaryDirectory(prefix='email-code-contract-') as directory:
            work = Path(directory)
            for name, raw in raws.items():
                (work / name).write_bytes(raw)
            (work / 'Defaults.ts').write_bytes(defaults)
            (work / 'gotrue.ts').write_text(prefix + strip(raws['gotrue.service.ts'].decode()))
            (work / 'kong.ts').write_text(strip(kong_raw.decode()))
            (work / 'main.ts').write_text(
                'import {buildGotrueEnv} from "./gotrue.ts";\n'
                'import {buildKongEmailTemplateBind} from "./kong.ts";\n'
                'import path from "node:path";\n'
                'const input=' + json.dumps(inputs) + ';\n'
                'const env=buildGotrueEnv(input);\n'
                'const keys=["GOTRUE_MAILER_TEMPLATES_MAGIC_LINK","GOTRUE_MAILER_SUBJECTS_MAGIC_LINK",'
                '"GOTRUE_MAILER_OTP_LENGTH","GOTRUE_MAILER_OTP_EXP","GOTRUE_SMTP_MAX_FREQUENCY",'
                '"GOTRUE_DISABLE_SIGNUP","GOTRUE_EXTERNAL_EMAIL_ENABLED","GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED","GOTRUE_SECURITY_MANUAL_LINKING_ENABLED"];\n'
                'console.log(JSON.stringify({selected:Object.fromEntries(keys.map(k=>[k,env[k]])),'
                'smtpConfigured:"GOTRUE_SMTP_HOST" in env,'
                'bind:buildKongEmailTemplateBind({id:"magic_link",resolvedPath:"/synthetic/project/supabase/templates/sign-in.html"},{path,posixPath:path.posix})}));\n')
            result = subprocess.run([str(node), str(work / 'main.ts')], env={'PATH': '/usr/bin:/bin', 'NODE_NO_WARNINGS': '1'}, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, 'pinned publisher builder execution failed')
            value = json.loads(result.stdout)
        self.assertEqual(value, {
            'selected': {
                'GOTRUE_MAILER_TEMPLATES_MAGIC_LINK': 'http://' + inputs['kongContainerName'] + ':8088/email/magic_link.html',
                'GOTRUE_MAILER_SUBJECTS_MAGIC_LINK': 'Your sign-in code',
                'GOTRUE_MAILER_OTP_LENGTH': '6', 'GOTRUE_MAILER_OTP_EXP': '3600',
                'GOTRUE_SMTP_MAX_FREQUENCY': '1m0s', 'GOTRUE_DISABLE_SIGNUP': 'true',
                'GOTRUE_EXTERNAL_EMAIL_ENABLED': 'true',
                'GOTRUE_EXTERNAL_ANONYMOUS_USERS_ENABLED': 'false',
                'GOTRUE_SECURITY_MANUAL_LINKING_ENABLED': 'false',
            },
            'smtpConfigured': False,
            'bind': '/synthetic/project/supabase/templates/sign-in.html:/home/kong/templates/email/magic_link.html:rw,z',
        })
        for path, raw in before.items():
            self.assertEqual(path.read_bytes(), raw)
        self.assertEqual((payload.parent / 'receipt.json').read_bytes(), receipt_raw)


if __name__ == '__main__':
    unittest.main()
