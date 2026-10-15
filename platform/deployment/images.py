#!/usr/bin/env python3
"""Qualify four planned base manifest identities; never pulls or starts images."""
import base64
import http.client
import json
import multiprocessing
import os
from pathlib import Path
import re
import selectors
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
import uuid

import dev
import toolchain

PINS = 'platform/deployment/image-pins.json'
SOURCE = 'platform/deployment/images.py'
COMMIT = '753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4'
SOURCE_PATHS = ['shared/services/Dockerfile', 'commands/start/start.gates.ts',
                'command-internal/docker-registry.ts']
IMAGES = [
    ('postgres', 'supabase/postgres:17.11.0.004', 'supabase/postgres', '17.11.0.004', 'supabase/postgres'),
    ('kong', 'library/kong:2.8.1', 'supabase/kong', '2.8.1', None),
    ('gotrue', 'supabase/gotrue:v2.197.0', 'supabase/gotrue', 'v2.197.0', 'supabase/gotrue'),
    ('postgrest', 'postgrest/postgrest:v16.4', 'supabase/postgrest', 'v16.4', 'postgrest/postgrest')]
INDEX_MEDIA = {'application/vnd.oci.image.index.v1+json',
               'application/vnd.docker.distribution.manifest.list.v2+json'}
MANIFEST_MEDIA = {'application/vnd.oci.image.manifest.v1+json',
                  'application/vnd.docker.distribution.manifest.v2+json'}
CONFIG_MEDIA = {'application/vnd.oci.image.config.v1+json',
                'application/vnd.docker.container.image.v1+json'}
LAYER_MEDIA = {'application/vnd.oci.image.layer.v1.tar',
               'application/vnd.oci.image.layer.v1.tar+gzip',
               'application/vnd.oci.image.layer.v1.tar+zstd',
               'application/vnd.docker.image.rootfs.diff.tar.gzip'}
LIMITS = {'manifest_bytes': 1024 * 1024, 'token_bytes': 65536, 'header_bytes': 16384,
          'request_seconds': 20, 'collection_seconds': 180, 'cli_seconds': 30,
          'owner_seconds': 180, 'cli_output_bytes': 1024 * 1024, 'max_descriptors': 100}
DIGEST = re.compile(r'sha256:[0-9a-f]{64}')


def fail(code, stage='images'):
    dev.refuse(stage, code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def load_pins(raw):
    expected = {'schema_version': 1, 'cli_version': '2.120.0', 'upstream_commit': COMMIT,
                'source_urls': ['https://github.com/supabase/cli/blob/' + COMMIT + '/apps/cli/src/' + p
                                for p in SOURCE_PATHS],
                'policy': {'backend': 'legacy', 'slim': False, 'dotenv_overrides': False,
                           'temp_overrides': False},
                'registry': 'public.ecr.aws', 'platform': {'os': 'linux', 'architecture': 'amd64'},
                'images': [dict(zip(['id', 'publisher_reference', 'repository', 'tag', 'cli_service'], row))
                           for row in IMAGES]}
    value = dev.decode(raw)
    if canonical(value) != canonical(expected):
        fail('invalid_selection')
    return value


def remaining(deadline):
    value = deadline - time.monotonic()
    if value <= 0:
        fail('metadata_deadline', 'registry')
    return value


def _https_worker(writer, reader, path, headers, limit):
    """No redirects/proxies; child bounds DNS/connect/TLS/header/read waits too."""
    reader.close()
    try:
        connection = http.client.HTTPSConnection('public.ecr.aws', timeout=LIMITS['request_seconds'])
        try:
            connection.request('GET', path, headers=headers)
            response = connection.getresponse()
            fields = response.getheaders()
            if sum(len(k) + len(v) + 4 for k, v in fields) > LIMITS['header_bytes']:
                raise ValueError()
            lowered = [key.lower() for key, _ in fields]
            if len(lowered) != len(set(lowered)):
                raise ValueError()
            body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError()
            result = {'status': response.status, 'headers': dict((k.lower(), v) for k, v in fields),
                      'body': base64.b64encode(body).decode()}
        finally:
            connection.close()
        writer.sendall(canonical(result).encode())
    except Exception:
        # Never forward a token, HTTP error body or exception text.
        pass
    finally:
        writer.close()


def https(path, headers, limit, deadline):
    # A bounded child is intentional: socket timeouts alone do not bound DNS or
    # a peer slowly emitting headers. Only safe metadata returns through this pipe.
    budget = min(remaining(deadline), LIMITS['request_seconds'])
    reader, writer = socket.socketpair()
    process = multiprocessing.get_context('fork').Process(
        target=_https_worker, args=(writer, reader, path, headers, limit))
    process.start()
    writer.close()
    raw = bytearray()
    request_deadline = time.monotonic() + budget
    try:
        while True:
            reader.settimeout(remaining(min(deadline, request_deadline)))
            chunk = reader.recv(65536)
            if not chunk:
                break
            raw.extend(chunk)
            if len(raw) > 2 * limit + LIMITS['header_bytes'] * 2:
                fail('metadata_too_large', 'registry')
        remaining(deadline)
        if not raw:
            fail('metadata_unavailable', 'registry')
        result = dev.decode(bytes(raw))
        body = base64.b64decode(result['body'], validate=True)
        if len(body) > limit:
            fail('metadata_too_large', 'registry')
        return result['status'], result['headers'], body
    except TimeoutError:
        fail('metadata_deadline', 'registry')
    finally:
        reader.close()
        if process.is_alive():
            process.terminate()
        process.join(1)
        if process.is_alive():
            process.kill()
            process.join(1)


class Registry:
    def __init__(self):
        self.deadline = time.monotonic() + LIMITS['collection_seconds']
        self.tokens = {}  # Anonymous credentials never leave memory.

    def manifest(self, repository, reference):
        if repository not in {row[2] for row in IMAGES} or not (
                reference in {row[3] for row in IMAGES if row[2] == repository}
                or DIGEST.fullmatch(reference)):
            fail('invalid_reference', 'registry')
        path = '/v2/' + repository + '/manifests/' + reference
        headers = {'Accept': ', '.join(sorted(INDEX_MEDIA | MANIFEST_MEDIA)),
                   'User-Agent': 'agriplatform-env-images/1', 'Accept-Encoding': 'identity'}
        if repository in self.tokens:
            headers['Authorization'] = 'Bearer ' + self.tokens[repository]
        status, response, raw = https(path, headers, LIMITS['manifest_bytes'], self.deadline)
        if status == 401:
            challenge = response.get('www-authenticate', '')
            # Public ECR's anonymous challenge uses the literal aws scope. The
            # subsequent request asks only for this selected repository's pull scope.
            if challenge != 'Bearer realm="https://public.ecr.aws/token/",service="public.ecr.aws",scope="aws"':
                fail('foreign_auth_challenge', 'registry')
            token_path = '/token/?' + urlencode({'service': 'public.ecr.aws',
                                               'scope': 'repository:' + repository + ':pull'})
            token_status, token_headers, token_raw = https(
                token_path, {'Accept': 'application/json', 'Accept-Encoding': 'identity'},
                LIMITS['token_bytes'], self.deadline)
            if token_status != 200 or token_headers.get('content-type', '').split(';')[0] != 'application/json':
                fail('token_response_invalid', 'registry')
            token_data = dev.decode(token_raw)
            token = token_data.get('token') if type(token_data) is dict else None
            if type(token) is not str or not re.fullmatch(r'[A-Za-z0-9._~+/=-]{1,60000}', token):
                fail('token_response_invalid', 'registry')
            self.tokens[repository] = token
            headers['Authorization'] = 'Bearer ' + token
            status, response, raw = https(path, headers, LIMITS['manifest_bytes'], self.deadline)
        if status != 200:
            fail('manifest_response_invalid', 'registry')
        if response.get('content-encoding', 'identity') != 'identity':
            fail('manifest_response_invalid', 'registry')
        media = response.get('content-type', '').split(';')[0]
        digest = 'sha256:' + dev.digest(raw)
        reported = response.get('docker-content-digest')
        if reported is not None and (not DIGEST.fullmatch(reported) or reported != digest):
            fail('manifest_digest_mismatch', 'registry')
        if DIGEST.fullmatch(reference) and reference != digest:
            fail('manifest_digest_mismatch', 'registry')
        document(raw, media)
        if not DIGEST.fullmatch(reference) and reported is None:
            # ECR may omit Docker-Content-Digest. Confirm that its digest address
            # returns exactly these bytes; a mutable tag alone is insufficient.
            addressed_raw, addressed_media, addressed_digest = self.manifest(repository, digest)
            if addressed_raw != raw or addressed_media != media or addressed_digest != digest:
                fail('manifest_digest_mismatch', 'registry')
        return raw, media, digest


def descriptor(value, allowed):
    if (type(value) is not dict or value.get('mediaType') not in allowed
            or type(value.get('digest')) is not str or not DIGEST.fullmatch(value['digest'])
            or type(value.get('size')) is not int or not 0 < value['size'] <= 2 ** 63 - 1
            or 'urls' in value or 'data' in value):
        fail('invalid_descriptor', 'registry')


def document(raw, media):
    if media not in INDEX_MEDIA | MANIFEST_MEDIA:
        fail('invalid_media_type', 'registry')
    if len(raw) > LIMITS['manifest_bytes']:
        fail('metadata_too_large', 'registry')
    value = dev.decode(raw)
    if (type(value) is not dict or type(value.get('schemaVersion')) is not int
            or value['schemaVersion'] != 2 or value.get('mediaType') != media):
        fail('invalid_manifest_schema', 'registry')
    if media in INDEX_MEDIA:
        entries = value.get('manifests')
        if type(entries) is not list or not 1 <= len(entries) <= LIMITS['max_descriptors']:
            fail('invalid_manifest_index', 'registry')
        seen = set()
        for entry in entries:
            descriptor(entry, MANIFEST_MEDIA)
            platform = entry.get('platform')
            if (type(platform) is not dict or type(platform.get('os')) is not str
                    or type(platform.get('architecture')) is not str or entry['digest'] in seen
                    or platform.get('os.features', []) != [] or platform.get('features', []) != []):
                fail('invalid_platform', 'registry')
            seen.add(entry['digest'])
        amd64 = [entry for entry in entries if entry['platform'].get('os') == 'linux'
                 and entry['platform'].get('architecture') == 'amd64'
                 and entry['platform'].get('variant', '') == '']
        if len(amd64) != 1:
            fail('linux_amd64_required', 'registry')
        return value, amd64[0]
    descriptor(value.get('config'), CONFIG_MEDIA)
    layers = value.get('layers')
    if type(layers) is not list or not 1 <= len(layers) <= 1000:
        fail('invalid_layers', 'registry')
    for layer in layers:
        descriptor(layer, LAYER_MEDIA)
    return value, None


def collect(pins):
    registry = Registry()
    artifacts, records = {}, []
    try:
        for item in pins['images']:
            raw, media, digest = registry.manifest(item['repository'], item['tag'])
            _, child = document(raw, media)
            # Platform cannot be established from a lone manifest without fetching
            # its config blob, forbidden by this metadata-only increment.
            if child is None:
                fail('platform_index_required', 'registry')
            name = item['id'] + '-index.json'
            artifacts[name] = raw
            child_raw, child_media, child_digest = registry.manifest(item['repository'], child['digest'])
            if (child_media != child['mediaType'] or len(child_raw) != child['size']
                    or child_digest != child['digest'] or child_media not in MANIFEST_MEDIA):
                fail('child_binding_mismatch', 'registry')
            document(child_raw, child_media)
            child_name = item['id'] + '-linux-amd64.json'
            artifacts[child_name] = child_raw
            records.append({'id': item['id'], 'publisher_reference': item['publisher_reference'],
                            'registry_reference': 'public.ecr.aws/' + item['repository'] + ':' + item['tag'],
                            'index': {'file': name, 'digest': digest, 'media_type': media, 'size': len(raw)},
                            'linux_amd64': {'file': child_name, 'digest': child_digest,
                                            'media_type': child_media, 'size': len(child_raw)}})
        return artifacts, records
    finally:
        registry.tokens.clear()


def bounded_command(command, cwd, env, timeout, limit):
    """Bound output and whole process group; child output is never printed."""
    process = subprocess.Popen([str(v) for v in command], cwd=cwd, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    deadline = time.monotonic() + timeout
    output, total = bytearray(), 0
    try:
        with selectors.DefaultSelector() as selector:
            for stream in [process.stdout, process.stderr]:
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ)
            while selector.get_map():
                budget = deadline - time.monotonic()
                if budget <= 0:
                    fail('command_deadline', 'images_cli')
                for key, _ in selector.select(budget):
                    # At most limit+1 bytes ever leave the kernel's bounded pipes.
                    chunk = os.read(key.fd, min(65536, limit - total + 1))
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    total += len(chunk)
                    if total > limit:
                        fail('command_output_too_large', 'images_cli')
                    if key.fileobj is process.stdout:
                        output.extend(chunk)
            budget = deadline - time.monotonic()
            if budget <= 0:
                fail('command_deadline', 'images_cli')
            try:
                process.wait(timeout=budget)
            except subprocess.TimeoutExpired:
                fail('command_deadline', 'images_cli')
            if process.returncode != 0:
                fail('command_refused', 'images_cli')
            return bytes(output)
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.stdout.close()
        process.stderr.close()
        process.wait(timeout=2)


def check_services(raw, pins):
    services = dev.decode(raw)
    if type(services) is not list or not 1 <= len(services) <= 100:
        fail('invalid_cli_services')
    names = set()
    for service in services:
        if (type(service) is not dict or set(service) != {'name', 'local', 'remote'}
                or type(service['name']) is not str or service['name'] in names
                or type(service['local']) is not str or service['remote'] != ''):
            fail('invalid_cli_services')
        names.add(service['name'])
    for item in pins['images']:
        if item['cli_service'] is None:
            continue
        found = [s for s in services if s['name'] == item['cli_service']]
        if len(found) != 1 or found[0]['local'] != item['tag']:
            fail('cli_pin_mismatch')
    return services


def capture_services(payload, target, run_id, pins):
    with tempfile.TemporaryDirectory(prefix='env-image-cli-') as temporary:
        work = Path(temporary)
        (work / 'supabase').mkdir(mode=0o700)
        config = work / 'supabase/config.toml'
        config.write_bytes(dev.configuration(target, run_id))
        config.chmod(0o600)
        for name in ['state', 'config', 'cache', 'tmp']:
            (work / name).mkdir(mode=0o700)
        env = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'CI': '1',
               'SUPABASE_WORKDIR': str(work), 'SUPABASE_HOME': str(work / 'state'),
               'XDG_CONFIG_HOME': str(work / 'config'), 'XDG_CACHE_HOME': str(work / 'cache'),
               'TMPDIR': str(work / 'tmp'), 'DOCKER_HOST': 'unix://' + str(work / 'no-daemon.sock'),
               'SUPABASE_TELEMETRY_DISABLED': '1', 'NO_UPDATE_NOTIFIER': '1'}
        command = [payload / 'supabase/supabase', 'services', '--output', 'json', '--agent', 'no',
                   '--workdir', work]
        check_cli_workdir(work, dev.configuration(target, run_id), after=False)
        raw = bounded_command(command, work, env, LIMITS['cli_seconds'], LIMITS['cli_output_bytes'])
        check_services(raw, pins)
        check_cli_workdir(work, dev.configuration(target, run_id), after=True)
        return raw


def check_cli_workdir(work, configuration, after):
    # services creates .temp/cli-latest (empty when its update lookup is disabled
    # or unavailable). That output is unrelated to project links/image overrides.
    if set(os.listdir(work)) != {'supabase', 'state', 'config', 'cache', 'tmp'}:
        fail('cli_state_not_unlinked')
    with dev.directory(work / 'supabase') as fd:
        dev.check_private(fd)
        names = set(os.listdir(fd))
        if names not in ([{'config.toml'}, {'config.toml', '.temp'}] if after else [{'config.toml'}]):
            fail('cli_state_not_unlinked')
        if dev.read_at(fd, 'config.toml', protected=True) != configuration:
            fail('cli_configuration_changed')
        if '.temp' in names:
            temporary = os.open('.temp', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            try:
                info = os.fstat(temporary)
                if (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o022
                        or set(os.listdir(temporary)) != {'cli-latest'}):
                    fail('cli_state_not_unlinked')
                latest = dev.read_at(temporary, 'cli-latest')
                info = os.stat('cli-latest', dir_fd=temporary, follow_symlinks=False)
                if (info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o022
                        or len(latest) > 128
                        or latest and not re.fullmatch(rb'v?[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}\n?', latest)):
                    fail('cli_state_not_unlinked')
            finally:
                os.close(temporary)


def existing_tools(args, target, raw, target_path, sources):
    """Require receipts first, then delegate to the existing repeat qualifier."""
    root = dev.ROOT / 'platform/deployment/.local/kdg-toolchains' / args.run_id
    try:
        with toolchain.anchored_directory(root) as (fd, run):
            if set(os.listdir(fd)) != {'payload', 'state', 'receipt.json'}:
                fail('existing_tools_required')
            receipt = dev.read_at(fd, 'receipt.json', protected=True)
            info = os.stat('receipt.json', dir_fd=fd, follow_symlinks=False)
            receipt_identity = (info.st_dev, info.st_ino)
            value = dev.decode(receipt)
            if type(value) is not dict or value.get('toolchain_ready') is not True:
                fail('existing_tools_required')
            # Owner command will verify every payload fingerprint and binding.
            with tempfile.TemporaryDirectory(prefix='env-image-owner-') as temporary:
                result = dev.decode(bounded_command(
                    [sys.executable, '-B', dev.ROOT / 'platform/deployment/toolchain.py', 'qualify',
                     '--target', target_path, '--run-id', args.run_id], Path(temporary),
                    {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'},
                    LIMITS['owner_seconds'], LIMITS['cli_output_bytes']))
            info = os.stat('receipt.json', dir_fd=fd, follow_symlinks=False)
            expected_result = {'ok': True, 'stage': 'qualified', 'code': 'toolchain_qualified',
                               'run_id': args.run_id, 'toolchain_ready': True, 'runtime_ready': False}
            if (canonical(result) != canonical(expected_result)
                    or dev.read_at(fd, 'receipt.json', protected=True) != receipt
                    or (info.st_dev, info.st_ino) != receipt_identity
                    or not toolchain.anchor_current(root, fd)):
                fail('tool_verification_refused')
    except FileNotFoundError:
        fail('existing_tools_required')
    dev.validate_prepared(target, raw, args.run_id, target_path, sources)
    return root / 'payload', dev.digest(receipt)


def source_evidence():
    return {name: dev.digest(dev.read(dev.ROOT / name)) for name in
            [SOURCE, PINS, 'platform/deployment/toolchain.py', toolchain.PINS]}


def write_at(fd, name, raw):
    file_fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    with os.fdopen(file_fd, 'wb') as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())
    os.fsync(fd)


def retained(fd, pins, binding):
    receipt_raw = dev.read_at(fd, 'receipt.json', protected=True)
    receipt = dev.decode(receipt_raw)
    expected_keys = {'schema_version', 'stage', 'runtime_ready', 'base_identities_ready',
                     'binding', 'limits', 'images', 'files', 'scope'}
    if (type(receipt) is not dict or set(receipt) != expected_keys
            or receipt.get('binding') != binding or receipt.get('limits') != LIMITS
            or receipt.get('schema_version') != 1 or type(receipt['schema_version']) is not int
            or receipt.get('stage') != 'base_images_qualified'
            or receipt.get('runtime_ready') is not False or receipt.get('base_identities_ready') is not True
            or receipt.get('scope') != 'planned_base_identities_only'):
        fail('evidence_binding_changed')
    names = {'services.json'} | {row[0] + suffix for row in IMAGES
                                for suffix in ['-index.json', '-linux-amd64.json']}
    if set(os.listdir(fd)) != names | {'receipt.json', '.qualify.lock'} or set(receipt['files']) != names:
        fail('unexpected_evidence_contents')
    artifacts = {name: dev.read_at(fd, name, protected=True) for name in names}
    if {name: dev.digest(value) for name, value in artifacts.items()} != receipt['files']:
        fail('evidence_bytes_changed')
    check_services(artifacts['services.json'], pins)
    records = receipt['images']
    if type(records) is not list or len(records) != len(IMAGES):
        fail('evidence_binding_changed')
    for item, record in zip(pins['images'], records):
        if type(record) is not dict or set(record) != {'id', 'publisher_reference', 'registry_reference', 'index', 'linux_amd64'}:
            fail('evidence_binding_changed')
        if (record['id'] != item['id'] or record['publisher_reference'] != item['publisher_reference']
                or record['registry_reference'] != 'public.ecr.aws/' + item['repository'] + ':' + item['tag']):
            fail('evidence_binding_changed')
        for kind, suffix in [('index', '-index.json'), ('linux_amd64', '-linux-amd64.json')]:
            evidence = record[kind]
            if type(evidence) is not dict or set(evidence) != {'file', 'digest', 'media_type', 'size'}:
                fail('evidence_binding_changed')
            name = item['id'] + suffix
            content = artifacts[name]
            if (evidence['file'] != name or evidence['digest'] != 'sha256:' + dev.digest(content)
                    or type(evidence['size']) is not int or evidence['size'] != len(content)):
                fail('evidence_binding_changed')
        _, child = document(artifacts[record['index']['file']], record['index']['media_type'])
        child_record = record['linux_amd64']
        if (child is None or child_record['media_type'] not in MANIFEST_MEDIA
                or child['digest'] != child_record['digest'] or child['size'] != child_record['size']
                or child['mediaType'] != child_record['media_type']):
            fail('child_binding_mismatch')
        document(artifacts[child_record['file']], child_record['media_type'])
    return receipt_raw


def qualify(args, *, existing_only=False):
    if str(uuid.UUID(args.run_id)) != args.run_id:
        fail('invalid_run_id', 'arguments')
    target_path = Path(args.target)
    if '..' in target_path.parts:
        fail('unsafe_path', 'paths')
    target_path = Path(os.path.abspath(target_path))
    raw = dev.read(target_path)
    target = dev.decode(raw)
    dev.validate(target, dev.decode(dev.read(dev.ROOT / dev.SCHEMA)))
    if target['workspace_root'] != str(dev.ROOT):
        fail('workspace_mismatch', 'paths')
    sources = dev.source_evidence()
    dev.validate_prepared(target, raw, args.run_id, target_path, sources)
    pin_raw = dev.read(dev.ROOT / PINS)
    pins = load_pins(pin_raw)
    image_sources = source_evidence()
    prepared = dev.ROOT / 'platform/deployment/.local/kdg' / args.run_id
    with dev.directory(prepared) as fd:
        inventory = dev.read_at(fd, 'inventory.json', protected=True)
    payload, receipt_hash = existing_tools(args, target, raw, target_path, sources)
    with toolchain.anchored_directory(payload) as (payload_fd, pinned_payload):
        return qualify_evidence(args, target, raw, target_path, sources, pins, pin_raw,
                                image_sources, inventory, payload, payload_fd, pinned_payload, receipt_hash, existing_only=existing_only)


def qualify_evidence(args, target, raw, target_path, sources, pins, pin_raw,
                     image_sources, inventory, payload, payload_fd, pinned_payload, receipt_hash, *, existing_only=False):
    binding = {'run_id': args.run_id, 'target_id': target['target_id'],
               'target_sha256': dev.digest(raw), 'preparation_sha256': dev.digest(inventory),
               'configuration_sha256': dev.digest(dev.configuration(target, args.run_id)),
               'preparation_sources': sources, 'source_sha256': image_sources,
               'selection_sha256': dev.digest(pin_raw), 'tool_receipt_sha256': receipt_hash}
    tool_root = payload.parent

    def inputs_current():
        dev.validate_prepared(target, raw, args.run_id, target_path, sources)
        with dev.directory(dev.ROOT / 'platform/deployment/.local/kdg' / args.run_id) as prepared_fd:
            dev.check_private(prepared_fd)
            if dev.read_at(prepared_fd, 'inventory.json', protected=True) != inventory:
                fail('qualification_input_changed')
        with toolchain.anchored_directory(tool_root) as (tool_fd, _):
            tool_raw = dev.read_at(tool_fd, 'receipt.json', protected=True)
        if (dev.read(target_path) != raw or source_evidence() != image_sources
                or dev.digest(tool_raw) != receipt_hash
                or not toolchain.anchor_current(payload, payload_fd)):
            fail('qualification_input_changed')
        # Reuse the installed-tool owner's fingerprint, never another fingerprint implementation.
        value = dev.decode(tool_raw)
        if toolchain.payload_fingerprint(pinned_payload) != value['payload']:
            fail('tool_payload_changed')

    inputs_current()
    base = dev.ROOT / 'platform/deployment/.local/kdg-base-images'
    run_path = base / args.run_id
    with toolchain.anchored_directory(base, create=not existing_only) as (parent, _):
        fresh = False
        if not existing_only:
            try:
                os.mkdir(args.run_id, 0o700, dir_fd=parent)
                os.fsync(parent)
                fresh = True
            except FileExistsError:
                pass
        fd = os.open(args.run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            dev.check_private(fd)
            lock = os.open('.qualify.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            info = os.fstat(lock)
            lock_identity = (info.st_dev, info.st_ino)
            complete = False

            def evidence_current():
                dev.check_private(parent)
                dev.check_private(fd)
                with toolchain.anchored_directory(run_path) as (current, _):
                    a, b = os.fstat(current), os.fstat(fd)
                    if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
                        fail('evidence_directory_changed')
                if not toolchain.anchor_current(base, parent):
                    fail('evidence_directory_changed')

            try:
                os.fsync(lock)
                os.fsync(fd)
                if not fresh:
                    before = retained(fd, pins, binding)
                    inputs_current()
                    if retained(fd, pins, binding) != before:
                        fail('evidence_bytes_changed')
                else:
                    if set(os.listdir(fd)) != {'.qualify.lock'}:
                        fail('unexpected_evidence_contents')
                    services = capture_services(pinned_payload, target, args.run_id, pins)
                    inputs_current()
                    artifacts, records = collect(pins)
                    artifacts['services.json'] = services
                    inputs_current()
                    evidence_current()
                    for name, content in artifacts.items():
                        write_at(fd, name, content)
                    receipt = {'schema_version': 1, 'stage': 'base_images_qualified',
                               'runtime_ready': False, 'base_identities_ready': True,
                               'scope': 'planned_base_identities_only', 'binding': binding, 'limits': LIMITS,
                               'images': records, 'files': {n: dev.digest(v) for n, v in artifacts.items()}}
                    inputs_current()
                    evidence_current()
                    if set(os.listdir(fd)) != set(artifacts) | {'.qualify.lock'}:
                        fail('unexpected_evidence_contents')
                    # Publish receipt last through an fsynced no-clobber hard link.
                    write_at(fd, '.receipt-pending', (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode())
                    inputs_current()
                    evidence_current()
                    if (set(os.listdir(fd)) != set(artifacts) | {'.qualify.lock', '.receipt-pending'}
                            or any(dev.read_at(fd, name, protected=True) != content
                                   for name, content in artifacts.items())
                            or dev.decode(dev.read_at(fd, '.receipt-pending', protected=True)) != receipt):
                        fail('evidence_bytes_changed')
                    pending = os.stat('.receipt-pending', dir_fd=fd, follow_symlinks=False)
                    pending_identity = (pending.st_dev, pending.st_ino)
                    os.link('.receipt-pending', 'receipt.json', src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
                    for name in ['.receipt-pending', 'receipt.json']:
                        installed = os.stat(name, dir_fd=fd, follow_symlinks=False)
                        if ((installed.st_dev, installed.st_ino) != pending_identity
                                or not stat.S_ISREG(installed.st_mode) or installed.st_nlink != 2
                                or installed.st_uid != os.getuid() or stat.S_IMODE(installed.st_mode) != 0o600):
                            fail('evidence_bytes_changed')
                    os.unlink('.receipt-pending', dir_fd=fd)
                    os.fsync(fd)
                    retained(fd, pins, binding)
                inputs_current()
                evidence_current()
                verified = dev.decode(retained(fd, pins, binding))
                selection_plan = {record['registry_reference']: 'public.ecr.aws/' + item['repository'] + '@' + record['linux_amd64']['digest']
                                  for item, record in zip(pins['images'], verified['images'])}
                if len({reference.rsplit('@', 1)[1] for reference in selection_plan.values()}) != 4:
                    fail('invalid_selection_plan')
                os.fsync(fd)
                complete = True
            finally:
                try:
                    # Failed fresh publication retains its lock, including failures
                    # after receipt linking. It can never be adopted by a later run.
                    if complete or not fresh:
                        release_lock(fd, lock_identity)
                finally:
                    os.close(lock)
        finally:
            os.close(fd)
    return {'ok': True, 'stage': 'base_images_qualified', 'code': 'base_images_qualified',
            'run_id': args.run_id, 'base_identities_ready': True, 'runtime_ready': False,
            'selection_plan': selection_plan}


def release_lock(fd, identity):
    try:
        info = os.stat('.qualify.lock', dir_fd=fd, follow_symlinks=False)
        if ((info.st_dev, info.st_ino) != identity or not stat.S_ISREG(info.st_mode)
                or info.st_nlink != 1 or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600):
            fail('qualification_lock_changed')
        os.unlink('.qualify.lock', dir_fd=fd)
        os.fsync(fd)
    except BaseException:
        # If unlink succeeded but its durability failed, restore only an absent
        # blocker. Never replace/remove another writer's file or repair a run.
        try:
            blocker = os.open('.qualify.lock', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                              0o600, dir_fd=fd)
        except FileExistsError:
            pass
        else:
            os.close(blocker)
        raise


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('command', choices=['qualify'])
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        result = qualify(parser.parse_args(argv))
        status = 0
    except dev.Refusal as error:
        result = {'ok': False, 'stage': error.stage, 'code': error.code,
                  'base_identities_ready': False, 'runtime_ready': False}
        status = 2
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError,
            UnicodeError, subprocess.SubprocessError, http.client.HTTPException):
        result = {'ok': False, 'stage': 'images', 'code': 'unsafe_or_unavailable_input',
                  'base_identities_ready': False, 'runtime_ready': False}
        status = 2
    print(json.dumps(result, sort_keys=True))
    return status


if __name__ == '__main__':
    sys.exit(main())
