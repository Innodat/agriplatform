"""Explicit synthetic create/edit owner; no API, UI, or reusable domain engine."""
import json
import time
from uuid import UUID, uuid4
from first_committed_write import (Budget, OutcomeKey, VerifiedContext, WriteError,
                                   execute, outcome_lock, transaction, receipt)


def document(org,account,record,expected,value,version=1):
    return dict(org_id=org,executor_account_id=account,command_version=version,
                payload=dict(record_id=record,expected_revision=str(expected),value=value))


def _id(value):
    try:
        if type(value) is str and UUID(value).int and str(UUID(value))==value:return value
    except ValueError:pass
    raise WriteError('invalid_command') from None


def _validate(doc,operation,actor,command):
    if (command not in ('record.create','record.edit') or type(doc) is not dict
            or set(doc)!={'org_id','executor_account_id','command_version','payload'}
            or type(doc['command_version']) is not int or doc['command_version'] not in (1,2)
            or type(doc['payload']) is not dict
            or set(doc['payload'])!={'record_id','expected_revision','value'}):
        raise WriteError('invalid_command')
    payload=doc['payload'];revision=payload['expected_revision']
    if (type(payload['value']) is not int or not -(2**31)<=payload['value']<2**31
            or type(revision) is not str or not revision.isascii() or not revision.isdigit()
            or len(revision)>19 or (revision.startswith('0') and revision!='0')
            or int(revision)>9223372036854775807):raise WriteError('invalid_command')
    for identity in (doc['org_id'],doc['executor_account_id'],payload['record_id'],operation,actor):_id(identity)


class _Restart(Exception):pass


def run(conn,doc,operation,*,actor,authorize,command='record.edit',budget=None,lookup=False,fail=None):
    # command is chosen by the server handler; it is absent from the request DTO.
    _validate(doc,operation,actor,command)
    budget=budget or Budget()
    key=OutcomeKey('sample',doc['org_id'],doc['executor_account_id'],command,operation)
    args=dict(org=key.org_id,account=key.account_id,command=command,op=operation)
    select="""SELECT * FROM sample.outcome WHERE org_id=CAST(:org AS uuid)
      AND executor_account_id=CAST(:account AS uuid) AND command_type=:command AND operation_id=CAST(:op AS uuid)"""
    # Private discovery uses verified backend identity only, never releases metadata.
    ctx=VerifiedContext(key.org_id,key.account_id,actor,'own_read',time.monotonic())
    with transaction(conn,budget,ctx):
        found=execute(conn,budget,select,args).mappings().first()
    target=str(found['target_id']) if found else doc['payload']['record_id']
    while True:
        budget.remaining()
        # The only network adapter call is outside every transaction and lock.
        timeout=min(3,budget.remaining())
        try:
            allowed=authorize(target,command,timeout)
        except Exception:
            raise WriteError('authorization_unavailable') from None
        if not allowed:
            raise WriteError('access_denied')
        context=VerifiedContext(key.org_id,key.account_id,actor,'own_write',time.monotonic())
        try:
            with transaction(conn,budget,context):
                outcome_lock(conn,budget,key,context)
                found=execute(conn,budget,select,args).mappings().first()
                if found:
                    if str(found['target_id'])!=target:
                        target=str(found['target_id'])
                        raise _Restart()
                    result=receipt(found['result'],command_type=found['command_type'],
                        command_version=found['command_version'],result_version=found['result_version'],target=target)
                elif lookup:
                    result=None
                else:
                    payload=doc['payload']
                    row=execute(conn,budget,'SELECT * FROM sample.record WHERE id=CAST(:id AS uuid) FOR UPDATE',dict(id=target)).mappings().first()
                    if command=='record.create':
                        if row:raise WriteError('revision_conflict')
                        if payload['expected_revision']!='0':raise WriteError('revision_conflict')
                        revision=1;changed=True
                        execute(conn,budget,"""INSERT INTO sample.record(id,org_id,owner_account_id,value,revision,created_by,updated_by)
                         VALUES(CAST(:target AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),:value,1,CAST(:actor AS uuid),CAST(:actor AS uuid))""",
                         dict(args,target=target,value=payload['value'],actor=actor))
                    else:
                        if not row:raise WriteError('not_found')
                        if row['closed']:raise WriteError('lifecycle_conflict')
                        if str(row['revision'])!=payload['expected_revision']:raise WriteError('revision_conflict')
                        changed=row['value']!=payload['value'];revision=row['revision']+int(changed)
                        if revision>9223372036854775807:raise WriteError('revision_conflict')
                        if changed:
                            execute(conn,budget,"""UPDATE sample.record SET value=:value,revision=:revision,
                              updated_by=CAST(:actor AS uuid),updated_at=clock_timestamp() WHERE id=CAST(:target AS uuid)""",
                              dict(target=target,value=payload['value'],revision=revision,actor=actor))
                    compact=dict(record_id=target,revision=str(revision))
                    result=receipt(compact,command_type=command,command_version=doc['command_version'],result_version=1,target=target)
                    outcome=str(uuid4())
                    execute(conn,budget,"""INSERT INTO sample.outcome(id,org_id,executor_account_id,executor_actor_id,
                     command_type,operation_id,command_version,result_version,result,target_id)
                     VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),
                     :command,CAST(:op AS uuid),:version,1,CAST(:result AS jsonb),CAST(:target AS uuid))""",
                     dict(args,id=outcome,actor=actor,version=doc['command_version'],result=json.dumps(compact) if fail!='outcome' else '[]',target=target))
                    if changed:
                        execute(conn,budget,"""INSERT INTO sample.revision(org_id,record_id,owner_account_id,revision,value,
                         executor_account_id,executor_actor_id,command_type,operation_id,outcome_id)
                         VALUES(CAST(:org AS uuid),CAST(:target AS uuid),CAST(:account AS uuid),:revision,:value,
                         CAST(:account AS uuid),CAST(:actor AS uuid),:command,CAST(:op AS uuid),CAST(:outcome AS uuid))""",
                         dict(args,target=target,revision=revision,value=payload['value'],actor=actor,
                              outcome=str(uuid4()) if fail=='evidence' else outcome))
            return result
        except _Restart:
            # Entire transaction rolled back before checking the raced stored target.
            continue
