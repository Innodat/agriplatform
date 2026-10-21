"""Explicit native disposable target binding; never discovers credentials/endpoints."""
from dataclasses import dataclass
from pathlib import Path
import os
import re
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'platform/deployment'))
import dev
import native_cli

ENV_REF = 'platform/deployment/environments/kdg-local.json'
RUN_REF = 'platform/deployment/.local/kdg'


class TargetError(ValueError):
    code = 'identity_operator_target_invalid'
    def __init__(self):
        super().__init__(self.code)


@dataclass(frozen=True, repr=False)
class Target:
    path: Path
    run_id: str
    database: str
    port: int
    password: str
    owner_id: str = 'identity'


def _require(condition):
    if not condition:
        raise TargetError()


def _path(value):
    path = Path(value)
    _require('..' not in path.parts)
    return Path(os.path.abspath(path))


def _binding(environment_target, run_id, owner='identity', namespace=None):
    _require(namespace is None or (owner=='access' and type(namespace) is str and re.fullmatch('[0-9a-f]{8}',namespace) is not None))
    _require(owner in ('identity','access'))
    _require(type(run_id) is str and str(UUID(run_id)) == run_id and UUID(run_id).int != 0)
    source = _path(environment_target)
    _require(source == ROOT / ENV_REF)
    raw = dev.read(source)
    environment = dev.decode(raw)
    dev.validate(environment, dev.decode(dev.read(ROOT / dev.SCHEMA)))
    _require(environment['workspace_root'] == str(ROOT)
        and environment['environment_kind'] in ('local_disposable', 'ci_disposable')
        and owner in environment['owner_ids'])
    run = ROOT / RUN_REF / run_id
    native_cli.check_run(run, environment, raw, run_id)
    secret_ref = str(Path(RUN_REF) / run_id / ('secrets/'+owner+'.env'))
    _require(secret_ref in [ref.replace('{run_id}', run_id) for ref in environment['secret_refs']])
    with dev.directory(run / 'secrets') as secrets:
        dev.check_private(secrets)
        secret = dev.read_at(secrets, owner+'.env', protected=True)
    _require(len(secret) <= 1024)
    # Literal bytes: no shell, dotenv, environment or interpolation semantics.
    _require(re.fullmatch(owner.upper().encode()+rb'_OPERATOR_PASSWORD=[^\x00\r\n]+\n?', secret) is not None)
    password = secret.removesuffix(b'\n').split(b'=', 1)[1].decode('utf-8', errors='strict')
    _require('$' not in password and '`' not in password)
    descriptor = dict(schema_version=1, owner_id=owner, environment_kind=environment['environment_kind'],
        run_id=run_id, environment_target_ref=ENV_REF, target_sha256=dev.digest(raw),
        database=('idop_' if owner=='identity' else 'acop_') + UUID(run_id).hex + ('_'+namespace if namespace is not None else ''), database_login=owner+'_operator', secret_ref=secret_ref)
    if namespace is not None:
        descriptor['namespace'] = namespace
    return descriptor, Target(run / (owner+'-operator'+('-'+namespace if namespace is not None else '')+'.json'), run_id, descriptor['database'],
                              environment['ports']['database'], password, owner)


def prepare_target(environment_target, run_id, *, owner='identity', namespace=None):
    """Bind existing native configuration/secret, exclusively; creates no DB or role."""
    failed = False
    try:
        descriptor, target = _binding(environment_target, run_id, owner, namespace)
        with dev.directory(target.path.parent) as run:
            dev.check_private(run)
            native_cli.write_private(run, target.path.name,
                (__import__('json').dumps(descriptor, sort_keys=True) + '\n').encode())
        return target.path
    except (OSError, ValueError, TypeError, KeyError, RecursionError, dev.Refusal):
        failed = True
    if failed:
        raise TargetError()


def load_target(path, *, owner='identity'):
    failed = False
    try:
        path = _path(path)
        namespace = None
        if owner=='access' and path.name != 'access-operator.json':
            match = re.fullmatch(r'access-operator-([0-9a-f]{8})\.json',path.name)
            _require(match is not None)
            namespace = match.group(1)
        _require(path.name == owner+'-operator'+('-'+namespace if namespace is not None else '')+'.json' and path.parent.parent == ROOT / RUN_REF)
        expected, target = _binding(ROOT / ENV_REF, path.parent.name, owner, namespace)
        with dev.directory(path.parent) as run:
            dev.check_private(run)
            actual = dev.decode(dev.read_at(run, path.name, protected=True))
        # JSON identity distinguishes bool/int and disallows extra fields.
        _require(type(actual) is dict and __import__('json').dumps(actual, sort_keys=True)
                 == __import__('json').dumps(expected, sort_keys=True))
        return target
    except (OSError, ValueError, TypeError, KeyError, RecursionError, dev.Refusal):
        failed = True
    if failed:
        raise TargetError()
