"""Unmounted own-read operation recovery; no engine, route or startup I/O.

Connection acquisition/exclusive ownership and future HTTP adaptation follow the
create boundary's contract. No received target, create grant or assignment confers
receipt disclosure. Absence does not rule out a concurrent later commit.
"""
import re
from typing import Literal
from uuid import UUID

from pydantic import field_validator
from sqlalchemy.exc import SQLAlchemyError

from context import Context, PERMISSION
import capture_create_handler as protected
import operation_outcomes as outcomes

write = outcomes.write


class Lookup(outcomes.Closed):
    operation_id: outcomes.Identifier
    command_type: outcomes.Command
    _id = field_validator('operation_id', mode='before')(outcomes._identifier)


class Unresolved(Lookup):
    status: Literal['unresolved'] = 'unresolved'


TARGET = '''SELECT id,org_id,owner_account_id FROM kdg_capture.capture
WHERE org_id=CAST(:org AS uuid) AND owner_account_id=CAST(:account AS uuid)
AND id=CAST(:capture AS uuid)'''


def _transaction(conn, budget, context, lookup, evidence):
    with write.transaction(conn, budget, context):
        key = write.OutcomeKey('kdg_capture', context.org_id, context.account_id,
                               lookup.command_type, lookup.operation_id)
        found = outcomes.lookup_private(conn, budget, key, context)
        if found is None:
            result = Unresolved(**lookup.model_dump())
        else:
            # Authorize the actual stored resource, never a received target. No
            # revision read: the original receipt may predate current capture state.
            row = write.execute(conn, budget, TARGET, dict(org=context.org_id,
                account=context.account_id, capture=found.result.capture_id)).mappings().one_or_none()
            budget.remaining()
            try:
                normalized = {key: str(value) if isinstance(value, UUID) else value
                              for key, value in dict(row).items()}
                if (normalized['id'], normalized['org_id'], normalized['owner_account_id']) != (
                    found.result.capture_id, context.org_id, context.account_id):
                    raise ValueError('foreign_target')
            except (ValueError, TypeError, KeyError):
                raise write.WriteError('operation_verification_unavailable') from None
            result = found.receipt()
    budget.remaining()
    return result


class RecoveryHandler(protected.CreateHandler):
    _permissions = (PERMISSION,)
    _evidence_type = Context

    async def execute(self, conn, operation_id, command_type, authorization):
        """Required closed discriminator; current own-read evidence precedes SQL."""
        budget = write.Budget()
        try:
            if conn.in_transaction() or conn.connection.driver_connection.autocommit:
                raise write.WriteError('invalid_write_context')
            try:
                lookup = Lookup(operation_id=operation_id, command_type=command_type)
            except ValueError:
                raise protected.HandlerError(422, 'validation_failed') from None
            if type(authorization) is not str or not re.fullmatch(r'Bearer [\x21-\x7e]+', authorization, flags=re.IGNORECASE):
                raise protected.HandlerError(401, 'authentication_required')
            evidence, observed_at = await self._authorize('Bearer ' + authorization.split(' ', 1)[1], budget)
            context = write.VerifiedContext(self.org_id, evidence.account_id, evidence.actor_id,
                                            'own_read', observed_at)
            return await protected._complete_worker(conn, budget, context, lookup, evidence, _transaction)
        except write.WriteError as error:
            code = str(error)
            if code == 'internal_error':
                code = 'operation_verification_unavailable'
            raise protected.HandlerError(protected.WRITE_STATUS.get(code, 500),
                code if code in protected.WRITE_STATUS else 'internal_error') from None
        except SQLAlchemyError:
            raise protected.HandlerError(503, 'operation_verification_unavailable') from None
