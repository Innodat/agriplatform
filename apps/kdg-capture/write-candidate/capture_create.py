"""App-owned fresh create body; inert until an owner installs current authority.

Caller supplies current backend-verified organization admission, durable actor and
membership plus exact create permission/own_account resource scope. These parameters
are not credentials: never construct them from browser assertions. Use the SAME
outcomes.write context and original budget installed by write.transaction(). Network
verification belongs before that transaction, within the original budget.

Return is private/provisional; acknowledge only after the enclosing durable commit.
Existing operations deliberately stop here: the outer handler must authorize the
actual stored target before recovery/disclosure. No incoming semantics decide replay.
"""
from datetime import date
import json
import re
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

import operation_outcomes as outcomes
from capture_commands import CreateCommand, CommandError, validate_answers
from questionnaire import DefinitionError, parse_definition

write = outcomes.write
ASSIGNED = 'kdg_capture.capture.create.assigned'
ALL = 'kdg_capture.capture.create.all'

# All owner child/assignment mutation commands MUST acquire this exact org+child
# key BEFORE reads/mutations, after any operation lock. Coordinates participants,
# not arbitrary SQL. No parent UPDATE grant or SECURITY DEFINER function required.
# hashtextextended hashes lock identity, never payload or authorization evidence.
CHILD_LOCK = """SELECT pg_advisory_xact_lock(hashtextextended(
'kdg_capture:child:v1:' || :org || ':' || :child, 0))"""
CHILD = '''SELECT active FROM kdg_capture.child WHERE org_id=CAST(:org AS uuid)
AND id=CAST(:child AS uuid)'''
ELIGIBILITY = '''SELECT membership_id,observed_active FROM kdg_capture.child_eligibility
WHERE org_id=CAST(:org AS uuid) AND account_id=CAST(:account AS uuid)
AND child_id=CAST(:child AS uuid) AND ref=:ref'''
ASSIGNMENT = '''SELECT membership_id,active FROM kdg_capture.child_assignment
WHERE org_id=CAST(:org AS uuid) AND account_id=CAST(:account AS uuid)
AND child_id=CAST(:child AS uuid)'''
VERSION = '''SELECT questionnaire_id,definition FROM kdg_capture.questionnaire_version
WHERE org_id=CAST(:org AS uuid) AND id=CAST(:version AS uuid)'''
CAPTURE_INSERT = '''INSERT INTO kdg_capture.capture
(id,org_id,child_id,questionnaire_id,questionnaire_version_id,owner_account_id,owner_actor_id,
child_eligibility_ref,creator_membership_id,observation_date,answers,captured_at,revision,created_by,updated_by)
VALUES(CAST(:capture AS uuid),CAST(:org AS uuid),CAST(:child AS uuid),CAST(:questionnaire AS uuid),
CAST(:version AS uuid),CAST(:account AS uuid),CAST(:actor AS uuid),:ref,:member,:date,
CAST(:answers AS jsonb),:device,1,CAST(:actor AS uuid),CAST(:actor AS uuid))'''
HISTORY_INSERT = '''INSERT INTO kdg_capture.capture_revision
(org_id,capture_id,revision,owner_account_id,owner_actor_id,child_id,questionnaire_id,questionnaire_version_id,
observation_date,answers,captured_at,executor_account_id,executor_actor_id,initiator_actor_id,outcome_id,command_type,operation_id)
SELECT c.org_id,c.id,c.revision,c.owner_account_id,c.owner_actor_id,c.child_id,c.questionnaire_id,c.questionnaire_version_id,
c.observation_date,c.answers,c.captured_at,CAST(:account AS uuid),CAST(:actor AS uuid),CAST(:actor AS uuid),
CAST(:outcome AS uuid),'capture.create',CAST(:operation AS uuid)
FROM kdg_capture.capture c WHERE c.org_id=CAST(:org AS uuid) AND c.id=CAST(:capture AS uuid)
AND c.owner_account_id=CAST(:account AS uuid)'''


def _one(conn, budget, statement, parameters):
    try:
        value = write.execute(conn, budget, statement, parameters).mappings().one_or_none()
    except SQLAlchemyError:
        raise write.WriteError('internal_error') from None
    budget.remaining()
    return value


def child_lock(conn, budget, context, child_id):
    """Owner coordination primitive; requires the installed write transaction.

    Future child/assignment commands reuse this function and ordering. Neither this
    lock nor an actor/eligibility record grants domain authority.
    """
    if (type(context) is not write.VerifiedContext
        or context.mode not in ('own_write', 'all_write')
        or not conn.in_transaction() or conn.connection.driver_connection.autocommit):
        raise write.WriteError('invalid_write_context')
    try:
        child = outcomes._identifier(child_id)
    except (ValueError, TypeError):
        raise write.WriteError('invalid_command') from None
    write.execute(conn, budget, CHILD_LOCK, dict(org=context.org_id, child=child))


def create_in_transaction(conn, budget, context, command, *, membership_id, permission):
    """Fresh-only body; caller owns rollback/commit and must let errors escape.

    membership_id is the positive decimal ID from current verified organization
    membership; permission is the exact current granted create capability. Both
    create permissions require own_write (Access own_account), never all_write.
    Shape validation here cannot replace the caller's HTTP authority verification.
    """
    if (type(context) is not write.VerifiedContext or context.mode != 'own_write'
        or type(membership_id) is not str or re.fullmatch('[1-9][0-9]{0,18}', membership_id) is None
        or int(membership_id) > 9223372036854775807
        or permission not in (ASSIGNED, ALL)):
        raise write.WriteError('invalid_write_context')
    try:
        command = CreateCommand.model_validate(command)
        if command.capture_id == command.operation_id:
            raise ValueError('distinct_capture_and_operation_required')
    except (ValueError, TypeError):
        raise write.WriteError('validation_failed') from None
    key = write.OutcomeKey('kdg_capture', context.org_id, context.account_id,
                           'capture.create', command.operation_id)
    outcomes._scope(conn, key, context, True)
    write.outcome_lock(conn, budget, key, context)
    if outcomes.lookup_private(conn, budget, key, context) is not None:
        raise write.WriteError('operation_verification_unavailable')
    child_lock(conn, budget, context, command.child_id)
    parameters = dict(org=context.org_id, account=context.account_id, actor=context.actor_id,
        child=command.child_id, ref=command.child_eligibility_ref,
        version=command.questionnaire_version_id, member=int(membership_id))
    child = _one(conn, budget, CHILD, parameters)
    eligibility = _one(conn, budget, ELIGIBILITY, parameters)
    if (child is None or eligibility is None or eligibility['observed_active'] is not True
        or eligibility['membership_id'] != parameters['member']):
        raise write.WriteError('child_eligibility_unavailable')
    # Prior active observation supports ordinary child inactivity. Historical
    # revisions and historical create permission never supply current authority.
    if permission == ASSIGNED:
        assignment = _one(conn, budget, ASSIGNMENT, parameters)
        if (assignment is None or assignment['active'] is not True
            or assignment['membership_id'] != parameters['member']):
            raise write.WriteError('assignment_unavailable')
    version = _one(conn, budget, VERSION, parameters)
    if version is None:
        raise write.WriteError('questionnaire_version_unavailable')
    try:
        definition = parse_definition(json.dumps(version['definition']))
    except (DefinitionError, ValueError, TypeError):
        raise write.WriteError('questionnaire_version_unavailable') from None
    try:
        validate_answers(command, definition)
    except CommandError:
        raise write.WriteError('validation_failed') from None
    parameters.update(capture=command.capture_id, questionnaire=str(version['questionnaire_id']),
        date=date.fromisoformat(command.observation_date), device=command.captured_at,
        answers=json.dumps({key: value.model_dump() for key, value in command.answers.items()},
                           separators=(',', ':')))
    budget.remaining()
    write.execute(conn, budget, CAPTURE_INSERT, parameters)
    receipt = outcomes.CaptureReceipt(operation_id=command.operation_id, command_type='capture.create',
        command_version=1, status='committed', result=dict(capture_id=command.capture_id, revision='1'))
    internal_id = str(uuid4())
    outcomes.append(conn, budget, key, context, outcome_id=internal_id, receipt=receipt)
    parameters.update(outcome=internal_id, operation=command.operation_id)
    if write.execute(conn, budget, HISTORY_INSERT, parameters).rowcount != 1:
        raise write.WriteError('internal_error')
    budget.remaining()
    return receipt
