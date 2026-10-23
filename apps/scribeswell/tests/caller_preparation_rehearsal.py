"""Test-only initial mapping protocol. Never a live custody verifier or runner.

The caller owns the transaction/commit and the synthetic actor/session binding.
This helper has no CLI, owner evidence intake or production deadline supervisor.
"""
from baseline import _checked_authority_ledger, REVISION

PRINCIPAL = 'scribeswell.corpus_operator_principal'
AUTHORITY = 'scribeswell.corpus_operator_authority'
COMMANDS = ('corpus.begin', 'corpus.recover', 'corpus.seal')
LOGIN = 'scribeswell_corpus_operator'


def locked_state(connection):
    """Acquire documented locks, then bounded full-row observations."""
    if not connection.in_transaction() or connection.connection.dbapi_connection.autocommit:
        raise ValueError('fixture_transaction_required')
    connection.exec_driver_sql("SET LOCAL search_path=pg_catalog,pg_temp")
    connection.exec_driver_sql("SET LOCAL statement_timeout='1500ms'")
    connection.exec_driver_sql("SET LOCAL lock_timeout='500ms'")
    connection.exec_driver_sql("SET LOCAL idle_in_transaction_session_timeout='3s'")
    if connection.exec_driver_sql('SHOW transaction_isolation').scalar() != 'read committed':
        raise ValueError('fixture_read_committed_required')
    if connection.exec_driver_sql('SHOW transaction_read_only').scalar() != 'off':
        raise ValueError('fixture_writable_required')
    if _checked_authority_ledger(connection) != REVISION:
        raise ValueError('fixture_head_required')
    for table in (PRINCIPAL, AUTHORITY):
        connection.exec_driver_sql('LOCK TABLE '+table+' IN SHARE ROW EXCLUSIVE MODE')
    return tuple(tuple(tuple(row) for row in connection.exec_driver_sql(
        'SELECT * FROM '+table+' ORDER BY '+order+' LIMIT '+limit))
        for table, order, limit in ((PRINCIPAL,'database_login','2'),(AUTHORITY,'database_login,source_id,command','4')))


def matches_initial(state, custody, preparer):
    principal, authorities = state
    expected = (LOGIN, False, 1, custody['executor_actor_id'], custody['actor_kind'],
                custody['actor_key'], custody['preparation_evidence_ref'], preparer, preparer)
    # Full state includes server timestamps, compared separately on no-op/recovery.
    if len(principal) != 1 or tuple(str(x) if i in (3,7,8) else x for i,x in enumerate(principal[0][:9])) != expected:
        return False
    return len(authorities) == 3 and all(
        tuple(str(x) if i in (5,6) else x for i,x in enumerate(row[:7])) ==
        (LOGIN, custody['source_id'], command, False, 1, preparer, preparer)
        for row, command in zip(authorities, COMMANDS))


def stage_initial(connection, custody, preparer):
    before = locked_state(connection)
    if before != ((), ()):
        if matches_initial(before, custody, preparer):
            return 'unchanged'
        raise ValueError('fixture_preparation_conflict')
    connection.exec_driver_sql('INSERT INTO '+PRINCIPAL+'''(database_login,enabled,revision,
        executor_actor_id,actor_kind,actor_key,preparation_evidence_ref,created_by_actor_id,updated_by_actor_id)
        VALUES (%s,false,1,%s,%s,%s,%s,%s,%s)''',
        (LOGIN,custody['executor_actor_id'],custody['actor_kind'],custody['actor_key'],custody['preparation_evidence_ref'],preparer,preparer))
    for command in COMMANDS:
        connection.exec_driver_sql('INSERT INTO '+AUTHORITY+'''(database_login,source_id,command,
            enabled,revision,created_by_actor_id,updated_by_actor_id) VALUES (%s,%s,%s,false,1,%s,%s)''',
            (LOGIN,custody['source_id'],command,preparer,preparer))
    if not matches_initial(locked_state(connection), custody, preparer):
        raise ValueError('fixture_postcheck_failed')
    return 'created'


def reconcile(connection, before, intended, *, original_pid):
    """Fixture-only reconciliation: no automatic retry, repair or command lookup."""
    if connection.exec_driver_sql('SELECT 1 FROM pg_stat_activity WHERE pid=%s', (original_pid,)).first():
        return 'unknown'
    actual = locked_state(connection)
    if actual == intended:
        return 'committed'
    if actual == before:
        return 'unchanged-before'
    return 'conflict'
