"""Synthetic loopback Access server over unchanged, source-bound retained data.

No preparation, command, migration, grant or write path is invoked here.
"""
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import stat
import sys
from unittest.mock import patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qualify_organization_check as owner
from fastapi import HTTPException
import uvicorn
from sqlalchemy import event

FIXTURE = owner.ROOT / 'platform/deployment/.local/identity-baseline/organization-check-reviewed3-20261022'
RETAINED_SHA = '2c341e184cc151eaa017a9c46e96028959165c867e02eed5528cfb43f1f2f48b'


def cases(state):
    columns = [r[1] for r in state['catalog_columns']
               if r[0] == 'grants' and not r[1].startswith('........pg.dropped.')]
    rows = []
    for row in state['grants']:
        if len(row) != len(columns):
            raise ValueError('retained_shape_invalid')
        rows.append(dict(zip(columns, row)))
    mapped = {r['account_id']: r['actor_id'] for r in state['identity']['account_actor']}
    active_members = {(r['org_id'], r['user_id'], r['id']): r for r in state['identity']['org_member']
                      if r['deleted_at'] is None}
    live = [r for r in rows if r['permission'] == owner.READ and r['revoked_at'] is None
            and (r['org_id'], r['user_id'], r['membership_id']) in active_members]
    positive = [r for r in live if r['user_id'] in mapped]
    unmapped = [r for r in live if r['user_id'] not in mapped]
    granted = {r['user_id'] for r in live}
    denied = [account for account in mapped if account not in granted
              and any(m['user_id'] == account and m['org_id'] == owner.ORG
                      for m in active_members.values())]
    if not (len(positive) == len(unmapped) == len(denied) == 1):
        raise ValueError('retained_cases_invalid')
    target = positive[0]
    if target['org_id'] != owner.ORG or unmapped[0]['org_id'] != owner.ORG:
        raise ValueError('retained_scope_invalid')
    return {'org_id': owner.ORG, 'positive': target['user_id'], 'actor_id': mapped[target['user_id']],
            'membership_id': str(target['membership_id']), 'denied': denied[0],
            'unmapped': unmapped[0]['user_id']}


def run(proof, fd):
    if not __debug__:
        raise ValueError('optimized_python_prohibited')
    if proof.is_symlink() or proof.parent != owner.ROOT / 'platform/deployment/.local/kdg-configured-context-20261022':
        raise ValueError('proof_invalid')
    info = proof.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('proof_invalid')
    retained_path = FIXTURE / 'organization-check-retained.json'
    if owner.sha256(retained_path.read_bytes()).hexdigest() != RETAINED_SHA:
        raise ValueError('retained_receipt_changed')
    private, _ = owner.base.load_fixture(FIXTURE)
    qualification = owner.Qualification(FIXTURE, private)
    qualification.verify_retained()
    retained = json.loads(retained_path.read_text())
    selected = cases(retained['state'])
    key = secrets.token_urlsafe(32)
    db = qualification.auxiliary_db('bridge', 'access_runtime')
    checks = {'permission_reads': 0}
    @event.listens_for(db, 'before_cursor_execute')
    def counted(conn, cursor, statement, parameters, context, executemany):
        if 'FROM access.check_organization_permission' in statement:
            checks['permission_reads'] += 1
    try:
        with db.connect() as connection:
            connection.exec_driver_sql('SET TRANSACTION READ ONLY')
            row = connection.exec_driver_sql("SELECT session_user,current_user,rolsuper,rolbypassrls FROM pg_roles WHERE rolname=session_user").one()
            if tuple(row) != ('access_runtime', 'access_runtime', False, False):
                raise ValueError('runtime_role_invalid')
        identities = {'Bearer synthetic-'+kind: UUID(selected[kind]) for kind in ('positive','denied','unmapped')}
        def authenticate(token):
            if token not in identities:
                raise HTTPException(401, {'code':'authentication_required'})
            return identities[token]
        with patch.dict(os.environ, {'KDG_ORG_ID':selected['org_id'], 'KDG_SERVICE_KEY':key}):
            app = owner.runtime.create_app(db=db, authenticate=authenticate)
        channel = socket.socket(fileno=fd)
        if channel.family != socket.AF_INET or channel.getsockname()[0] != '127.0.0.1':
            raise ValueError('socket_invalid')
        # Private synthetic facts only. Neither this file nor the key is printed.
        ready = proof / 'access-ready.json'
        descriptor = os.open(ready, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w') as output:
            json.dump(selected | {'service_key':key}, output)
        server = uvicorn.Server(uvicorn.Config(app, access_log=False, log_level='warning', timeout_graceful_shutdown=3,
                    ssl_certfile=str(proof/'tls-cert.pem'), ssl_keyfile=str(proof/'tls-key.pem')))
        # Uvicorn re-emits SIGTERM after graceful shutdown. Keep this test process
        # alive long enough to verify unchanged retained state and record exit0.
        signal.signal(signal.SIGTERM, lambda signum, frame: None)
        server.run(sockets=[channel])
        if not server.started:
            raise RuntimeError('server_did_not_start')
    finally:
        db.dispose()
    qualification.verify_retained()
    descriptor = os.open(proof/'access-summary.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as output:
        json.dump(checks, output)
    print(json.dumps({'stage':'access_server_stopped_retained_state_verified','status':'passed'}),flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError('arguments_invalid')
        run(Path(sys.argv[1]), int(sys.argv[2]))
    except Exception as error:
        print('synthetic_access_fixture_failed:'+type(error).__name__, file=sys.stderr)
        raise SystemExit(1) from None
