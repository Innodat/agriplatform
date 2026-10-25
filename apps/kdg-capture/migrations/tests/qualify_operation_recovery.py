"""SELECT-only qualification of the unmounted reader on the exact retained fixture.

No migration, seed, DML, preparation or cleanup. Access is synthetic MockTransport.
The historical create proof supplies retained identifiers, not current-source approval.
"""
import argparse
import asyncio
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import uuid4

import httpx
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture_commit_fixture as fixture
sys.path.insert(0, str(fixture.ROOT/'apps/kdg-capture/api'))
sys.path.insert(0, str(fixture.ROOT/'apps/kdg-capture/write-candidate'))
import operation_recovery as recovery

PROOF = fixture.FIXTURE.parent/'capture-commit-qualify-a5dad4fa02f445a4bc3711e012503e18.json'
SOURCES = (
    'apps/kdg-capture/write-candidate/operation_recovery.py',
    'apps/kdg-capture/write-candidate/capture_create_handler.py',
    'apps/kdg-capture/write-candidate/operation_outcomes.py',
    'apps/kdg-capture/write-tools/transaction_context.py',
    'apps/kdg-capture/api/context.py',
    'apps/kdg-capture/migrations/tests/qualify_operation_recovery.py',
    'apps/kdg-capture/migrations/tests/capture_commit_fixture.py',
    'apps/kdg-capture/migrations/tests/native_fixture.py',
)


def require(condition, identifier):
    if not condition:
        raise AssertionError(identifier)


def retained_proof():
    data = fixture.native.private_json(PROOF)
    require(data.get('qualified') is True and data.get('succeeded') is True
        and data.get('database') == fixture.DATABASE and data.get('run_id') == fixture.native.RUN
        and data.get('head') == fixture.STORAGE
        and data.get('fixture_sha256') == sha256(fixture.FIXTURE.read_bytes()).hexdigest(),
        'retained_proof_invalid')
    return data


def counts(admin):
    with fixture.native.connect(admin, readonly=True) as conn:
        return {table:conn.execute('SELECT count(*) FROM kdg_capture.'+table).fetchone()[0]
                for table in ('capture','operation_outcome','capture_revision')}


def make_handler(data, connection, *, account=None, org=None, denied=False):
    async def access(request):
        require(not connection.in_transaction(), 'external_wait_inside_transaction')
        require(json.loads(request.content) == dict(permission=recovery.PERMISSION,
            authorization_scope=dict(kind='organization', org_id=org or data['org_id'])),
            'own_read_permission_required')
        if denied:
            return httpx.Response(403,json=dict(detail=dict(code='access_denied')))
        return httpx.Response(200,json=dict(account_id=account or data['account_id'],
            actor_id=data['actor_id'],membership_id='1',decision_id=str(uuid4()),
            permission=recovery.PERMISSION,
            authorization_scope=dict(kind='organization',org_id=org or data['org_id']),
            resource_scope=dict(kind='own_account',account_id=account or data['account_id']),
            checked_at=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')))
    return recovery.RecoveryHandler(org_id=org or data['org_id'],
        access_url='https://access.invalid',service_key='synthetic-service-key',
        transport=httpx.MockTransport(access))


def qualify():
    require(__debug__, 'optimized_python_prohibited')
    value, original, admin = fixture.retained()
    applied = fixture.migration_qualified(value)
    identities = fixture.identities(value)
    data = retained_proof()
    before = counts(admin)
    fixture.sentinel(admin)
    engine = fixture.engine(value['urls']['runtime']).execution_options(postgresql_readonly=True)
    results = []
    try:
        with engine.connect() as conn:
            require(conn.execute(text('SHOW transaction_read_only')).scalar_one() == 'on',
                    'read_only_connection_required')
            conn.rollback()
            budget = recovery.write.Budget()
            context = recovery.write.VerifiedContext(data['org_id'],data['account_id'],data['actor_id'],
                'own_read',recovery.write.time.monotonic())
            with recovery.write.transaction(conn,budget,context):
                assignments = conn.execute(text('SELECT active FROM kdg_capture.child_assignment WHERE org_id=CAST(:org AS uuid) AND child_id=CAST(:child AS uuid)'),
                    dict(org=data['org_id'],child=data['child_id'])).scalars().all()
                require(assignments == [False], 'retained_assignment_must_be_inactive')
            command = data['commands']['fresh']
            async def read(operation, command_type='capture.create', **policy):
                handler = make_handler(data,conn,**policy)
                return await handler.execute(conn,operation,command_type,'Bearer synthetic-account-token')
            result = asyncio.run(read(command['operation_id']))
            require(result.model_dump() == dict(operation_id=command['operation_id'],
                command_type='capture.create',command_version=1,status='committed',
                result=dict(capture_id=command['capture_id'],revision='1')), 'original_receipt_required')
            results.append('original_create_receipt_after_assignment_removed')
            for name, operation, command_type, policy in (
                ('unknown_operation',str(uuid4()),'capture.create',{}),
                ('required_command_discriminator',command['operation_id'],'capture.edit',{}),
                ('foreign_account',command['operation_id'],'capture.create',dict(account=str(uuid4()))),
                ('foreign_organization',command['operation_id'],'capture.create',dict(org=str(uuid4())))):
                result = asyncio.run(read(operation,command_type,**policy))
                require(result.model_dump() == dict(operation_id=operation,command_type=command_type,
                    status='unresolved'), 'scoped_absence_required')
                results.append(name)
            try:
                asyncio.run(read(command['operation_id'],denied=True))
            except recovery.protected.HandlerError as error:
                require((error.status,error.error_id)==(403,'access_denied'),'access_denial_required')
                require(not conn.in_transaction(),'denial_entered_database')
            else:
                raise AssertionError('denial_unexpected_success')
            results.append('current_own_read_denial')
            require(conn.execute(text('SHOW transaction_read_only')).scalar_one()=='on',
                    'read_only_connection_lost')
            conn.rollback()
        require(counts(admin)==before,'retained_rows_changed')
        fixture.sentinel(admin)
        require(fixture.revision(value)==fixture.STORAGE,'revision_changed')
    finally:
        engine.dispose()
    result = dict(succeeded=True,qualified=True,read_only=True,cases=results,
        head=fixture.STORAGE,counts_before=before,counts_after=counts(admin),
        sentinel_unchanged=True,applied_receipt=applied,retained_identifier_receipt=str(PROOF),
        identities=identities,native_edit_receipt=False,
        sources={path:sha256((fixture.ROOT/path).read_bytes()).hexdigest() for path in SOURCES})
    destination=fixture.receipt('own-read',result)
    return dict(result,report=str(destination))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualify-retained',required=True,action='store_true')
    parser.parse_args()
    try:
        print(json.dumps(qualify(),sort_keys=True))
    except Exception as error:
        destination=fixture.receipt('own-read',dict(succeeded=False,error_type=type(error).__name__))
        print(json.dumps(dict(succeeded=False,error_type=type(error).__name__,report=str(destination))))
        raise SystemExit(1) from None
