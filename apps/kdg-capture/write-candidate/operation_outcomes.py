"""Inert app-owned storage candidate; no connections, migrations or mounted routes.

Owners import this module and use its ``write`` export for transaction/context/key
construction. Generated test-support loaders are independent test inventories, not
runtime import paths. Re-importing this adapter reuses the single helper identity.
"""
import importlib.util
import json
import sys
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from sqlalchemy.exc import SQLAlchemyError

NAME = 'kdg_capture_owned_write_context'
if NAME not in sys.modules:
    source = Path(__file__).resolve().parents[1] / 'write-tools/transaction_context.py'
    spec = importlib.util.spec_from_file_location(NAME, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[NAME] = module
    spec.loader.exec_module(module)
write = sys.modules[NAME]


def _identifier(value):
    if type(value) is not str:
        raise ValueError('invalid_identifier')
    try:
        if UUID(value).int and str(UUID(value)) == value:
            return value
    except ValueError:
        pass
    raise ValueError('invalid_identifier') from None


Identifier = Annotated[str, Field(strict=True)]
Version = Annotated[StrictInt, Field(ge=1, le=1)]
Command = Literal['capture.create', 'capture.edit']


class Closed(BaseModel):
    model_config = ConfigDict(
        extra='forbid', frozen=True, strict=True,
        hide_input_in_errors=True, revalidate_instances='always',
    )

    def __repr__(self):
        return '<' + type(self).__name__ + ' redacted>'

    def __str__(self):
        return self.__repr__()


class CaptureResult(Closed):
    capture_id: Identifier
    revision: Annotated[str, Field(
        strict=True, pattern='^[1-9][0-9]{0,18}$', max_length=19,
    )]
    _id = field_validator('capture_id', mode='before')(_identifier)

    @field_validator('revision')
    @classmethod
    def revision_bound(cls, value):
        if int(value) > 9223372036854775807:
            raise ValueError('invalid_revision')
        return value


class CaptureReceipt(Closed):
    operation_id: Identifier
    command_type: Command
    command_version: Version
    status: Literal['committed']
    result: CaptureResult
    _id = field_validator('operation_id', mode='before')(_identifier)


class StoredOutcome(Closed):
    id: Identifier
    org_id: Identifier
    executor_account_id: Identifier
    executor_actor_id: Identifier
    command_type: Command
    operation_id: Identifier
    command_version: Version
    result_version: Version
    result: CaptureResult
    initiator_actor_id: Identifier | None
    committed_at: datetime
    _ids = field_validator(
        'id', 'org_id', 'executor_account_id', 'executor_actor_id',
        'operation_id', mode='before',
    )(_identifier)

    @field_validator('initiator_actor_id', mode='before')
    @classmethod
    def initiator(cls, value):
        return None if value is None else _identifier(value)

    @field_validator('committed_at')
    @classmethod
    def utc_timestamp(cls, value):
        if value.utcoffset() is None:
            raise ValueError('invalid_timestamp')
        return value.astimezone(timezone.utc)

    def receipt(self):
        """Private projection only; the caller must authorize before disclosure."""
        return CaptureReceipt(
            operation_id=self.operation_id, command_type=self.command_type,
            command_version=self.command_version, status='committed', result=self.result,
        )


SELECT = '''SELECT id,org_id,executor_account_id,executor_actor_id,command_type,operation_id,
command_version,result_version,result,initiator_actor_id,committed_at
FROM kdg_capture.operation_outcome WHERE org_id=CAST(:org AS uuid)
AND executor_account_id=CAST(:account AS uuid) AND command_type=:command
AND operation_id=CAST(:operation AS uuid)'''
INSERT = '''INSERT INTO kdg_capture.operation_outcome
(id,org_id,executor_account_id,executor_actor_id,command_type,operation_id,
command_version,result_version,result,initiator_actor_id,committed_at)
VALUES(CAST(:id AS uuid),CAST(:org AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),
:command,CAST(:operation AS uuid),:version,1,CAST(:result AS jsonb),CAST(:actor AS uuid),statement_timestamp())'''


def _scope(conn, key, context, writing=False):
    # Reuse the same verified context installed on this connection by transaction().
    # Shape/scope checks do not authenticate a backend assertion or read back GUCs.
    if (
        type(key) is not write.OutcomeKey
        or type(context) is not write.VerifiedContext
        or key.owner_schema != 'kdg_capture'
        or key.command_type not in ('capture.create', 'capture.edit')
        or (key.org_id, key.account_id) != (context.org_id, context.account_id)
        or (writing and context.mode not in ('own_write', 'all_write'))
        or not conn.in_transaction()
        or conn.connection.driver_connection.autocommit
    ):
        raise write.WriteError('invalid_write_context')
    return dict(
        org=key.org_id, account=key.account_id,
        command=key.command_type, operation=key.operation_id,
    )


def lookup_private(conn, budget, key, context):
    """Private scoped discovery, never HTTP recovery or current authority evidence.

    No received target/payload participates. A caller must authorize the actual stored
    resource before disclosure; absent data alone grants no public unresolved response.
    """
    parameters = _scope(conn, key, context)
    try:
        row = write.execute(conn, budget, SELECT, parameters).mappings().one_or_none()
    except SQLAlchemyError:
        raise write.WriteError('internal_error') from None
    budget.remaining()
    if row is None:
        return None
    try:
        if not isinstance(row, Mapping):
            raise ValueError('invalid_row')
        values = dict(row)
        # Only native DB UUID values are normalized. Wire receipt IDs stay strict.
        for field in (
            'id', 'org_id', 'executor_account_id', 'executor_actor_id',
            'operation_id', 'initiator_actor_id',
        ):
            if isinstance(values.get(field), UUID):
                values[field] = str(values[field])
        found = StoredOutcome.model_validate(values)
        stored_scope = (
            found.org_id, found.executor_account_id,
            found.command_type, found.operation_id,
        )
        if stored_scope != (key.org_id, key.account_id, key.command_type, key.operation_id):
            raise ValueError('foreign_row')
        if found.id == found.operation_id:
            raise ValueError('invalid_internal_id')
        budget.remaining()
        return found
    except (ValueError, TypeError):
        raise write.WriteError('operation_verification_unavailable') from None


def append(conn, budget, key, context, *, outcome_id, receipt):
    """Append after lock/recheck and applicable domain state, before linked history.

    Reserve outcome_id, write applicable domain state, append outcome, then insert
    revision/evidence rows referencing it; commit everything together. Plain INSERT:
    uniqueness races abort the owner transaction, never silently retain new business
    effects while returning someone else's receipt. No success acknowledgement is
    returned. Only an enclosing durable commit permits one.
    """
    parameters = _scope(conn, key, context, True)
    try:
        internal_id = _identifier(outcome_id)
        value = CaptureReceipt.model_validate(receipt)
        if internal_id == key.operation_id:
            raise ValueError('invalid_internal_id')
        if (value.operation_id, value.command_type) != (key.operation_id, key.command_type):
            raise ValueError('wrong_receipt')
    except (ValueError, TypeError):
        raise write.WriteError('invalid_command') from None
    parameters.update(
        id=internal_id, actor=context.actor_id, version=value.command_version,
        result=json.dumps(value.result.model_dump(), separators=(',', ':')),
    )
    write.execute(conn, budget, INSERT, parameters)
    return None
