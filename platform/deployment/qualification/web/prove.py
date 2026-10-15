#!/usr/bin/env python3
"""Disposable root-workspace proof; never installs into the checkout."""
import argparse
import base64
import binascii
import glob
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import shlex
import signal
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
RUN_ID = '0cc4bc48-505e-41c1-8876-25b2d49b5694'
TOOLS = ROOT / f'platform/deployment/.local/kdg-toolchains/{RUN_ID}/payload'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_lock(lock, workspaces):
    """Only registry-integrity artifacts, declared workspaces and pinned bundles."""
    packages = lock.get('packages')
    if lock.get('lockfileVersion') != 3 or not isinstance(packages, dict) or '' not in packages:
        raise ValueError('expected npm v3 lock with root packages entry')
    bundle_owners = {'npm': '12.2.0', '@tailwindcss/oxide-wasm32-wasi': '4.3.3'}
    for path, entry in packages.items():
        if not isinstance(entry, dict) or path.startswith('/') or '..' in path.split('/') or '\\' in path:
            raise ValueError(f'invalid lock entry: {path}')
        if path == '' or path in workspaces.values():
            if any(key in entry for key in ['resolved', 'integrity', 'link', 'inBundle']):
                raise ValueError(f'nonlocal workspace entry: {path}')
            continue
        if entry.get('link'):
            if not any(path == f'node_modules/{name}' and entry.get('resolved') == owner
                       for name, owner in workspaces.items()):
                raise ValueError(f'unknown workspace link: {path}')
            continue
        if 'node_modules/' not in path or not isinstance(entry.get('version'), str):
            raise ValueError(f'unknown package entry: {path}')
        if entry.get('inBundle'):
            valid_owner = False
            for name, version in bundle_owners.items():
                owner = f'node_modules/{name}'
                if path.startswith(owner + '/node_modules/') and packages.get(owner, {}).get('version') == version:
                    valid_owner = True
            if not valid_owner:
                raise ValueError(f'unknown or unpinned bundled entry: {path}')
            if 'resolved' not in entry and 'integrity' not in entry:
                continue  # Bytes covered by the pinned registry bundle owner's integrity.
        source = entry.get('resolved')
        if not isinstance(source, str):
            raise ValueError(f'missing registry artifact: {path}')
        url = urlsplit(source)
        if (url.scheme != 'https' or url.netloc != 'registry.npmjs.org' or
                not url.path.endswith('.tgz') or url.query or url.fragment):
            raise ValueError(f'foreign artifact source: {path}')
        integrity = entry.get('integrity')
        if not isinstance(integrity, str) or not integrity.startswith('sha512-'):
            raise ValueError(f'missing sha512 artifact integrity: {path}')
        try:
            decoded = base64.b64decode(integrity[7:], validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError(f'invalid artifact integrity: {path}') from exc
        if len(decoded) != 64:
            raise ValueError(f'invalid artifact integrity length: {path}')


def execute(command, *, cwd, env, timeout=600, grace=2):
    """Run one Linux command group; bound both execution and descendant cleanup."""
    process = subprocess.Popen(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, start_new_session=True)
    def cleanup():
        def signal_group(value):
            try:
                os.killpg(process.pid, value)
            except ProcessLookupError:
                pass
        signal_group(signal.SIGTERM)
        try:
            output, _ = process.communicate(timeout=grace)
        except subprocess.TimeoutExpired:
            output = None
        signal_group(signal.SIGKILL)
        if output is None:
            try:
                output, _ = process.communicate(timeout=grace)
            except subprocess.TimeoutExpired as exc:
                output = exc.stdout or b''
                if isinstance(output, bytes):
                    output = output.decode('utf-8', errors='replace')
                if process.stdout:
                    process.stdout.close()
                try:
                    process.wait(timeout=grace)
                except subprocess.TimeoutExpired:
                    output += '\nFAILED: group cleanup could not confirm leader exit\n'
                output += '\nFAILED: stdout remained open after bounded group cleanup\n'
        return output

    try:
        output, _ = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(command, process.returncode, output)
    except subprocess.TimeoutExpired:
        output = cleanup()
        return subprocess.CompletedProcess(command, 124, output +
            '\nFAILED: bounded command timeout; process-group TERM/KILL sent\n')
    except KeyboardInterrupt:
        cleanup()
        raise


def verify_tools():
    """Delegate immutable payload/preparation verification to its existing owner CLI."""
    receipt = TOOLS.parent / 'receipt.json'
    inventory = ROOT / f'platform/deployment/.local/kdg/{RUN_ID}/inventory.json'
    for path in [receipt, inventory]:
        if not path.is_file() or any(item.is_symlink() for item in [path, *path.parents]):
            raise ValueError('existing toolchain receipt and preparation are required; no installation')
    receipt_hash = digest(receipt)
    with tempfile.TemporaryDirectory(prefix='env-web-preflight-') as private:
        folder = Path(private)
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'CI': '1'}
        for kind in ['user', 'global']:
            path = folder / kind
            path.write_text('')
            path.chmod(0o600)
            env[f'NPM_CONFIG_{kind.upper()}CONFIG'] = str(path)
        env['NPM_CONFIG_CACHE'] = str(folder / 'cache')
        command = [sys.executable, '-B', str(ROOT / 'platform/deployment/toolchain.py'),
                   'qualify', '--target', 'platform/deployment/environments/kdg-local.json',
                   '--run-id', RUN_ID]
        owner = execute(command, cwd=ROOT, env=env, timeout=180)
        if owner.returncode != 0:
            raise ValueError('existing owner toolchain verification refused: ' + owner.stdout)
        result = json.loads(owner.stdout)
        if result.get('ok') is not True or result.get('code') != 'toolchain_qualified' or result.get('runtime_ready') is not False:
            raise ValueError('owner toolchain verification did not confirm qualification')
        if digest(receipt) != receipt_hash:
            raise ValueError('toolchain receipt changed during repeat verification')
        owner_command = command
        for command, version in [([str(TOOLS / 'node/bin/node'), '--version'], 'v26.11.1'),
                                 ([str(TOOLS / 'node/bin/node'), str(TOOLS / 'npm/bin/npm-cli.js'), '--version'], '12.2.0')]:
            checked = execute(command, cwd=folder, env=env, timeout=30)
            if checked.returncode != 0 or checked.stdout.strip() != version:
                raise ValueError('selected version preflight refused or timed out')
        return {'receipt_sha256': receipt_hash, 'owner_command': [str(x) for x in owner_command],
                'owner_result': result, 'owner_log': owner.stdout}


def browser_identity(copy, cache, env, node, owner):
    """Record the explicit executable used by smoke and installed metadata identity."""
    if cache is None:
        return {'status': 'unqualified', 'reason': 'no-explicit-browser-path'}
    code = """const {createRequire}=require('node:module'); const path=require('node:path');
const r=createRequire(path.resolve('package.json')); const test=r('@playwright/test');
const testPackage=r.resolve('@playwright/test/package.json');
const pw=createRequire(testPackage).resolve('playwright/package.json');
const core=createRequire(pw).resolve('playwright-core/package.json');
function bounded(promise,ms) { let timer; return Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('browser identity close timeout')),ms)})]).finally(()=>clearTimeout(timer)); }
(async()=>{ let server; try {
  server=await test.chromium.launchServer({headless:true,timeout:15000});
  console.log(JSON.stringify({executable:server.process().spawnfile,metadata:path.join(path.dirname(core),'browsers.json'),package:core,test_package:testPackage}));
} finally { if(server) { try { await bounded(server.close(),3000); } catch(error) { await bounded(server.kill(),3000); throw error; } } }
})().catch(error=>{console.error(error.message);process.exitCode=1});"""
    result = execute([str(node), '-e', code], cwd=copy / owner, env=env, timeout=30)
    if result.returncode != 0:
        return {'status': 'unqualified', 'reason': 'browser-identity-query-failed', 'exit_code': result.returncode}
    try:
        identities = json.loads(result.stdout)
    except ValueError:
        return {'status': 'unqualified', 'reason': 'invalid-browser-identity'}
    if not isinstance(identities, dict) or set(identities) != {'executable', 'metadata', 'package', 'test_package'}:
        return {'status': 'unqualified', 'reason': 'invalid-browser-identity'}
    output = {'status': 'qualified-identity-only', 'artifacts': {}}
    for key, value in identities.items():
        path = Path(value)
        if not path.is_file():
            output['status'] = 'unqualified'
            output['artifacts'][key] = {'path': str(path), 'missing': True}
        else:
            output['artifacts'][key] = {'path': str(path), 'sha256': digest(path)}
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', required=True, type=Path)
    p.add_argument('--cache', required=True, type=Path)
    p.add_argument('--mode', choices=['characterize', 'qualify', 'resolve'], required=True)
    p.add_argument('--offline', action='store_true')
    p.add_argument('--browser-path', type=Path, help='existing explicit Playwright browser cache; never downloads')
    args = p.parse_args()
    destination = args.destination.absolute()
    for item in [destination, args.cache.absolute()]:
        if '..' in item.parts:
            p.error('parent traversal in destination/cache path')
        if any(parent.is_symlink() for parent in [item, *item.parents]):
            p.error('symlinked destination/cache path')
    if destination.is_relative_to(args.cache.absolute()) or args.cache.absolute().is_relative_to(destination):
        p.error('cache and proof destination must not overlap')
    if destination == ROOT or ROOT.is_relative_to(destination):
        p.error('destination overlaps source root')
    if args.cache.absolute().is_relative_to(ROOT) and not args.cache.absolute().is_relative_to(ROOT / 'platform/deployment/.local'):
        p.error('cache must be outside source or under deployment/.local')
    if destination.exists() or destination.is_symlink():
        p.error('destination must be absent')
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        p.error('only Linux x86_64 is qualified')
    if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / 'platform/deployment/.local'):
        p.error('repository destination must be under deployment/.local')
    node = TOOLS / 'node/bin/node'
    npm = TOOLS / 'npm/bin/npm-cli.js'
    try:
        toolchain_proof = verify_tools()
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    package = json.loads((ROOT / 'package.json').read_text())
    owners = sorted({Path(x).relative_to(ROOT) for pattern in package['workspaces']
                     for x in glob.glob(str(ROOT / pattern)) if (Path(x) / 'package.json').is_file()})
    if args.mode == 'characterize':
        owners = [owner for owner in owners if owner != Path('platform/env-web-qualification')]
    # Every actual workspace is copied, including source and file: dependencies. Unknown
    # local dependencies fail preflight rather than silently borrowing checkout sources.
    for source in [ROOT / 'package.json', ROOT / 'package-lock.json']:
        if source.is_symlink():
            p.error(f'symlinked root source: {source}')
    browser_input = Path('apps/scribeswell/data/hebrew-lexicon/lexicon.json')
    if args.browser_path:
        source = ROOT / browser_input
        if not source.is_file() or any(item.is_symlink() for item in [source, *source.parents]):
            p.error('missing or symlinked public browser lexicon fixture')
    for owner in owners:
        if any(parent.is_symlink() for parent in [(ROOT / owner), *(ROOT / owner).parents]):
            p.error(f'symlinked workspace root: {owner}')
        for source in (ROOT / owner).rglob('*'):
            if source.is_symlink() and not any(part in {'node_modules', '.local'} for part in source.relative_to(ROOT / owner).parts):
                p.error(f'symlinked workspace source: {source}')
        manifest = json.loads((ROOT / owner / 'package.json').read_text())
        if owner == Path('platform/env-web-qualification') and (ROOT / owner / 'package-lock.json').exists():
            p.error(f'nested workspace lock: {owner}')
        for group in ['dependencies', 'devDependencies', 'optionalDependencies']:
            for value in manifest.get(group, {}).values():
                if value.startswith('file:'):
                    target = (ROOT / owner / value[5:]).resolve()
                    if not any(target.is_relative_to(ROOT / item) for item in owners):
                        p.error(f'uncopied local dependency: {target}')
    workspace_names = {json.loads((ROOT / owner / 'package.json').read_text())['name']: str(owner) for owner in owners}
    if args.mode == 'qualify':
        validate_lock(json.loads((ROOT / 'package-lock.json').read_text()), workspace_names)
    destination.mkdir(parents=True, mode=0o700)
    copy = destination / 'root'
    copy.mkdir()
    for name in ['package.json', 'package-lock.json']:
        shutil.copy2(ROOT / name, copy / name)
    for owner in owners:
        shutil.copytree(ROOT / owner, copy / owner, ignore=shutil.ignore_patterns(
            'package-lock.json', 'node_modules', 'dist', '.local', '.env', '.env.*', '*.tsbuildinfo', 'test-results', 'playwright-report'))
    if args.browser_path:
        (copy / browser_input).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / browser_input, copy / browser_input)
        # Reader tests create their own synthetic data here. Never copy PtS content.
        (copy / 'apps/pts/reference').mkdir(parents=True)
    config = destination / 'config'
    config.mkdir()
    for name in ['user', 'global']:
        (config / name).write_text('')
    args.cache.mkdir(parents=True, exist_ok=True)
    shim = destination / 'bin'
    shim.mkdir()
    (shim / 'npm').write_text('#!/bin/sh\nexec ' + shlex.quote(str(node)) + ' ' + shlex.quote(str(npm)) + ' \"$@\"\n')
    (shim / 'npm').chmod(0o700)
    env = {'PATH': f'{shim}:{TOOLS / "node/bin"}:/usr/bin:/bin', 'LC_ALL': 'C.UTF-8',
           'NPM_CONFIG_USERCONFIG': str(config / 'user'), 'NPM_CONFIG_GLOBALCONFIG': str(config / 'global'),
           'NPM_CONFIG_CACHE': str(args.cache.absolute()), 'NPM_CONFIG_REGISTRY': 'https://registry.npmjs.org/',
           'NPM_CONFIG_FETCH_RETRIES': '0', 'NPM_CONFIG_FETCH_TIMEOUT': '30000',
           'NPM_CONFIG_AUDIT': 'false', 'NPM_CONFIG_FUND': 'false', 'CI': '1', 'ENV_SUPABASE_BINARY': str(TOOLS / 'supabase/supabase')}
    if args.browser_path:
        env['PLAYWRIGHT_BROWSERS_PATH'] = str(args.browser_path.absolute())
    records = []

    def run(label, command, cwd=copy, expected=0):
        result = execute([str(v) for v in command], cwd=cwd, env=env)
        (destination / f'{label}.log').write_text(result.stdout)
        records.append({'label': label, 'command': [str(v) for v in command],
                        'cwd': str(cwd.relative_to(copy)), 'exit_code': result.returncode})
        print(f'{label}: exit {result.returncode}', flush=True)
        (destination / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
        if expected is not None and result.returncode != expected:
            raise RuntimeError(f'{label}: expected {expected}; see {destination / (label + ".log")}')
        return result

    provenance = {'node': digest(node), 'npm': digest(npm), 'lock_before': digest(ROOT / 'package-lock.json'),
                  'host': platform.platform(), 'runtime_ready': False,
                  'runner_sha256': digest(Path(__file__)), 'toolchain': toolchain_proof,
                  'browser_identity': {'status': 'unqualified', 'reason': 'not-installed-yet' if args.browser_path else 'no-explicit-browser-path'},
                  'browser_inputs': [str(browser_input)] if args.browser_path else [],
                  'empty_directories': ['apps/pts/reference'] if args.browser_path else [], 'workspaces': [str(x) for x in owners],
                  'sources': {str(path.relative_to(copy)): digest(path) for path in sorted(copy.rglob('*')) if path.is_file()}}
    (destination / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    if args.mode == 'resolve':
        run('resolve', [node, npm, 'install', '--package-lock-only', '--ignore-scripts', '--save-exact', '--allow-remote=all', *(['--offline'] if args.offline else [])])
        run('refresh-legacy-types', [node, npm, 'update', '@types/react', '@types/prop-types',
                                   '--workspace', 'platform/shared', '--package-lock-only',
                                   '--ignore-scripts', '--allow-remote=all', *(['--offline'] if args.offline else [])])
        workspace_names = {json.loads((copy / owner / 'package.json').read_text())['name']: str(owner) for owner in owners}
        validate_lock(json.loads((copy / 'package-lock.json').read_text()), workspace_names)
        (destination / 'lock-validation.json').write_text(json.dumps({'status': 'passed', 'lock_sha256': digest(copy / 'package-lock.json'), 'registry': 'https://registry.npmjs.org/', 'lifecycle_scripts': False}, indent=2) + '\n')
        return
    run('ci', [node, npm, 'ci', '--ignore-scripts', *(['--offline'] if args.offline else [])])
    if digest(copy / 'package-lock.json') != provenance['lock_before']:
        raise RuntimeError('ci changed lock')
    provenance['browser_identity'] = browser_identity(copy, args.browser_path, env, node,
        Path('platform/env-web-qualification') if args.mode == 'qualify' else Path('apps/scribeswell/web'))
    if provenance['browser_identity'].get('status') == 'qualified-identity-only':
        env['ENV_CHROMIUM_EXECUTABLE'] = provenance['browser_identity']['artifacts']['executable']['path']
    (destination / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    run('shared', [node, npm, 'run', 'type-check', '--workspace', 'platform/shared'], expected=None)
    for owner in ['app-directory-client', 'ui-business']:
        run(owner, [node, copy / 'node_modules/typescript/bin/tsc', '--noEmit', '-p', f'platform/{owner}/tsconfig.json'], expected=None)
    run('scribeswell-build', [node, npm, 'run', 'build', '--workspace', 'apps/scribeswell/web'], expected=None)
    if args.browser_path:
        run('scribeswell-browser', [node, npm, 'run', 'test:browser', '--workspace', 'apps/scribeswell/web'], expected=None)
    else:
        (destination / 'scribeswell-browser.log').write_text('NOT RUN: no explicit --browser-path; browser proof remains unqualified.\n')
        records.append({'label': 'scribeswell-browser', 'exit_code': None, 'status': 'not-run-no-explicit-browser-path'})
        (destination / 'commands.json').write_text(json.dumps(records, indent=2) + '\n')
    if args.mode == 'qualify':
        for command in ['type-check', 'test', 'build', 'tools']:
            run(f'fixture-{command}', [node, npm, 'run', command, '--workspace', 'platform/env-web-qualification'])
        if args.browser_path:
            run('fixture-browser-smoke', [node, 'scripts/browser-smoke.mjs'], cwd=copy / 'platform/env-web-qualification')
    print(destination, flush=True)


if __name__ == '__main__':
    main()
