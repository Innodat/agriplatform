"""Explicit neutral sample owner. Not a generic engine, KDG API or production model."""
import json
import time
from uuid import UUID, uuid4

from atomic_write import (Budget, OutcomeKey, VerifiedContext, WriteError, execute,
                          outcome_lock, transaction, verify_existing)
from command_fingerprint import CommandFingerprint, FingerprintError, create_fingerprint


def receipt(result):
    # This is the sample command-specific compact receipt, never arbitrary JSON.
    if (type(result) is not dict or set(result) != {'record_id','revision'}
            or type(result['record_id']) is not str or type(result['revision']) is not str
            or len(result['revision']) > 19 or not result['revision'].isascii()
            or not result['revision'].isdigit() or result['revision'].startswith('0')
            or not 0 < int(result['revision']) <= 9223372036854775807):
        raise WriteError('operation_verification_unavailable')
    from uuid import UUID
    try:
        valid = UUID(result['record_id']).int and str(UUID(result['record_id'])) == result['record_id']
    except ValueError:
        valid = False
    if not valid:
        raise WriteError('operation_verification_unavailable')
    return dict(result)


def document(org, account, record, expected, value, command='record.edit'):
    return dict(org_id=org,executor_account_id=account,command_type=command,
                command_version=1,payload=dict(record_id=record,expected_revision=str(expected),value=value))


def run(conn, doc, operation, *, actor, authorize, keys, active='old', fail=None,
        budget=None, lookup=False):
    # Trusted owner validates a bounded normalized DTO before using these primitives.
    if (type(doc) is not dict or set(doc) != {'org_id','executor_account_id','command_type','command_version','payload'}
            or doc['command_type'] not in ('record.edit','record.adjust')
            or type(doc['command_version']) is not int or doc['command_version'] != 1
            or type(doc['payload']) is not dict
            or set(doc['payload']) != {'record_id','expected_revision','value'}
            or type(doc['payload']['value']) is not int
            or not -(2**31) <= doc['payload']['value'] < 2**31):
        raise WriteError('invalid_command')
    payload=doc['payload']
    target=receipt({'record_id':payload['record_id'],'revision':payload['expected_revision']})['record_id']
    # Reject untyped/noncanonical identity before the authority adapter sees it.
    for identity in (doc['org_id'],doc['executor_account_id'],operation,actor):
        try:
            valid = type(identity) is str and UUID(identity).int and str(UUID(identity)) == identity
        except ValueError:
            valid = False
        if not valid:
            raise WriteError('invalid_command') from None
    budget=budget or Budget()
    # All external authority happens here, before connection transaction or locks.
    # The callback is sample-test input standing in for a bounded owner HTTP check.
    if not authorize(doc, min(3,budget.remaining())):
        raise WriteError('access_denied')
    context=VerifiedContext(doc['org_id'],doc['executor_account_id'],actor,'own_write',time.monotonic())
    key=OutcomeKey('sample',context.org_id,context.account_id,doc['command_type'],operation)
    with transaction(conn,budget,context):
        outcome_lock(conn,budget,key,context)
        args=dict(org=context.org_id,account=context.account_id,command=key.command_type,op=operation)
        found=execute(conn,budget,"""SELECT * FROM sample.outcome WHERE org_id=CAST(:org AS uuid)
            AND executor_account_id=CAST(:account AS uuid) AND command_type=:command AND operation_id=CAST(:op AS uuid)""",args).mappings().first()
        if found:
            # Exact target previously checked. No authority callback occurs here.
            if str(found['target_id']) != target:
                raise WriteError('access_denied')
            fp=CommandFingerprint(found['fingerprint_version'],found['fingerprint_algorithm'],found['fingerprint_key_id'],found['fingerprint'])
            verify_existing(doc,fp,keys=keys,command_version=found['command_version'],result_version=found['result_version'])
            result=receipt(found['result'])
            if result['record_id'] != target:
                raise WriteError('operation_verification_unavailable')
        elif lookup:
            result=None
        else:
            row=execute(conn,budget,'SELECT * FROM sample.record WHERE id=CAST(:id AS uuid) FOR UPDATE',{'id':target}).mappings().first()
            if not row:
                raise WriteError('not_found')
            if str(row['revision']) != payload['expected_revision']:
                raise WriteError('revision_conflict')
            changed=row['value'] != payload['value']
            revision=row['revision']+int(changed)
            result=receipt(dict(record_id=target,revision=str(revision)))
            if changed:
                execute(conn,budget,"""UPDATE sample.record SET value=:value,revision=:revision,
                    updated_by=CAST(:actor AS uuid),updated_at=clock_timestamp() WHERE id=CAST(:id AS uuid)""",
                    dict(value=payload['value'],revision=revision,actor=actor,id=target))
            try:
                if type(keys) is not dict:
                    raise WriteError('operation_verification_unavailable')
                fp=create_fingerprint(doc,key_id=active,key=keys[active])
            except (KeyError, TypeError, FingerprintError):
                raise WriteError('operation_verification_unavailable') from None
            outcome=str(uuid4())
            execute(conn,budget,"""INSERT INTO sample.outcome(id,org_id,executor_account_id,executor_actor_id,
              command_type,operation_id,command_version,fingerprint_version,fingerprint_algorithm,
              fingerprint_key_id,fingerprint,result_version,result,target_id)
              VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),
              :command,CAST(:op AS uuid),1,:version,:algorithm,:key,:digest,1,CAST(:result AS jsonb),CAST(:target AS uuid))""",
              dict(args,id=outcome,actor=actor,version=fp.version,algorithm=fp.algorithm,key=fp.key_id,
                   digest=fp.digest,result=json.dumps(result) if fail != 'outcome' else '[]',target=target))
            if changed:
                execute(conn,budget,"""INSERT INTO sample.revision(org_id,record_id,owner_account_id,revision,value,
                  executor_account_id,executor_actor_id,command_type,operation_id,outcome_id)
                  VALUES(CAST(:org AS uuid),CAST(:target AS uuid),CAST(:account AS uuid),:revision,:value,
                  CAST(:account AS uuid),CAST(:actor AS uuid),:command,CAST(:op AS uuid),CAST(:outcome AS uuid))""",
                  dict(args,target=target,revision=revision,value=payload['value'],actor=actor,
                       outcome=str(uuid4()) if fail == 'evidence' else outcome))
    # Commit has happened here. A lost response cannot imply a rollback.
    return result
