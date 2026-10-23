"""Closed native replay checks for committed controller state, not source publication."""
from baseline import BaselineError
from prepared_controller import checked_prepared, custody_state

MAX_ATTEMPTS = 10000
MAX_OUTCOMES = 20000


def deny(code='invalid'):
    raise BaselineError('scribeswell_history_' + code)


def invalid(connection, query, parameters=()):
    if connection.exec_driver_sql(query, parameters).scalar():
        deny()


def history(connection, expected):
    custody_state(connection, expected)
    if connection.exec_driver_sql('SELECT singleton FROM scribeswell.corpus_fence_control LIMIT 2').fetchall() != [(True,)]:
        deny()
    if connection.exec_driver_sql('SELECT 1 FROM scribeswell.corpus_write_binding LIMIT 1').first():
        deny()
    # Probe only cap+1 rows and retain no history payload in the client.
    for table, maximum in (('corpus_attempt', MAX_ATTEMPTS), ('corpus_command_outcome', MAX_OUTCOMES)):
        count = connection.exec_driver_sql('SELECT count(*) FROM (SELECT 1 FROM scribeswell.' + table + ' LIMIT %s) bounded', (maximum + 1,)).scalar()
        if count > maximum:
            deny('limit_exceeded')
    epoch = connection.exec_driver_sql('SELECT generation FROM scribeswell.corpus_epoch LIMIT 2').fetchall()
    if not epoch:
        invalid(connection, 'SELECT EXISTS (SELECT 1 FROM scribeswell.corpus_attempt) OR EXISTS (SELECT 1 FROM scribeswell.corpus_command_outcome)')
        return
    if len(epoch) != 1:
        deny()
    invalid(connection, """SELECT EXISTS (SELECT 1 FROM scribeswell.corpus_epoch e WHERE
        e.source_id<>%s OR NOT isfinite(e.created_at) OR NOT isfinite(e.updated_at)
        OR e.generation<>(SELECT count(*) FROM scribeswell.corpus_attempt)
        OR e.generation<>(SELECT max(generation) FROM scribeswell.corpus_attempt))
        OR EXISTS (SELECT 1 FROM scribeswell.corpus_attempt a WHERE a.source_id<>%s)
        OR NOT EXISTS (SELECT 1 FROM scribeswell.corpus_attempt WHERE generation=1)""", (expected['source_id'], expected['source_id']))
    # Native input validation is owner-only, fixed and pinned before invocation.
    # Aggregate forces evaluation for every bounded row without returning payloads.
    connection.exec_driver_sql('SELECT count(scribeswell.validate_corpus_command(semantic_command)) FROM scribeswell.corpus_command_outcome').scalar()
    invalid(connection, """SELECT EXISTS (
      SELECT 1 FROM scribeswell.corpus_command_outcome o
      JOIN scribeswell.corpus_attempt a USING (attempt_id,source_id,generation)
      JOIN scribeswell.corpus_operator_principal p USING (database_login)
      LEFT JOIN scribeswell.corpus_operator_authority u ON u.database_login=o.database_login
        AND u.source_id=o.source_id AND u.command=o.semantic_command->>'command'
      WHERE o.database_login<>'scribeswell_corpus_operator' OR o.source_id<>%s
       OR o.semantic_command->>'operation_id' IS DISTINCT FROM o.operation_id::text
       OR o.semantic_command#>>'{scope,source_id}' IS DISTINCT FROM o.source_id
       OR o.semantic_command#>'{payload,input}' IS DISTINCT FROM jsonb_build_object(
          'source_sha256',a.input_sha256,'catalogue_version',a.catalogue_version,
          'versification_id',a.versification_id,'tokenization_version',a.tokenization_version)
       OR u.command IS NULL OR o.principal_revision>p.revision OR o.authority_revision>u.revision
       OR (o.principal_revision=p.revision AND o.executor_actor_id<>p.executor_actor_id)
       OR (o.principal_revision=p.revision AND NOT p.enabled)
       OR (o.authority_revision=u.revision AND NOT u.enabled)
       OR o.result IS DISTINCT FROM jsonb_build_object('version',1,'operation_id',o.operation_id::text,
          'command',o.semantic_command->>'command','source_id',o.source_id,
          'executor_actor_id',o.executor_actor_id::text,'attempt_id',o.attempt_id::text,
          'generation',o.generation::text,'state',CASE WHEN o.semantic_command->>'command'='corpus.seal' THEN 'closed' ELSE 'updating' END))""", (expected['source_id'],))
    # Aggregate outcomes before coverage comparison: the pinned FK establishes
    # their owning attempt. Joining fresh unanalyzed tables first can force a
    # quadratic nested-loop plan under EXISTS, even for valid bounded history.
    invalid(connection, """WITH counts AS MATERIALIZED (
      SELECT attempt_id,
        count(*) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origins,
        count(*) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seals
      FROM scribeswell.corpus_command_outcome GROUP BY attempt_id)
      SELECT EXISTS (SELECT 1 FROM counts WHERE origins<>1 OR seals>1)
        OR (SELECT count(*) FROM counts)<>(SELECT count(*) FROM scribeswell.corpus_attempt)""")
    # Project each event once, then derive predecessor/successor facts in one
    # window pass. Avoid self-joining materialized full request/receipt payloads.
    invalid(connection, """WITH events AS MATERIALIZED (
      SELECT attempt_id,source_id,generation,
        max(executor_actor_id::text) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origin_actor,
        max(created_at) FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS origin_at,
        max(semantic_command->>'command') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS command,
        max(semantic_command#>>'{payload,expected_generation}') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS previous_generation,
        max(semantic_command#>>'{payload,expected_attempt_id}') FILTER (WHERE semantic_command->>'command'<>'corpus.seal') AS previous_attempt,
        max(executor_actor_id::text) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_actor,
        max(created_at) FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_at,
        max(semantic_command#>>'{payload,expected_generation}') FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_generation,
        max(semantic_command#>>'{payload,expected_attempt_id}') FILTER (WHERE semantic_command->>'command'='corpus.seal') AS seal_attempt
      FROM scribeswell.corpus_command_outcome GROUP BY attempt_id,source_id,generation),
    ordered AS MATERIALIZED (
      SELECT *,lag(attempt_id::text) OVER w AS predecessor,
        lead(origin_actor) OVER w AS following_actor,lead(origin_at) OVER w AS following_at,
        first_value(origin_actor) OVER w AS first_actor,first_value(origin_at) OVER w AS first_at
      FROM events WINDOW w AS (ORDER BY generation)),
    epoch AS MATERIALIZED (SELECT * FROM scribeswell.corpus_epoch LIMIT 1)
    SELECT (SELECT count(*) FROM scribeswell.corpus_attempt a
      JOIN ordered b USING (attempt_id,source_id,generation) CROSS JOIN epoch e
      WHERE (a.generation=1 AND b.command<>'corpus.begin')
       OR (a.generation>1 AND (b.command<>'corpus.recover'
          OR b.previous_generation IS DISTINCT FROM (a.generation-1)::text
          OR b.previous_attempt IS DISTINCT FROM b.predecessor))
       OR (b.seal_actor IS NOT NULL AND (b.seal_generation IS DISTINCT FROM a.generation::text
          OR b.seal_attempt IS DISTINCT FROM a.attempt_id::text))
       OR a.created_by_actor_id::text<>b.origin_actor OR a.created_at<>b.origin_at
       OR (a.generation<e.generation AND a.state<>'retired')
       OR (a.generation=e.generation AND (
          a.attempt_id<>e.attempt_id OR a.input_sha256<>e.input_sha256 OR a.state<>e.state
          OR (a.state='closed') IS DISTINCT FROM (b.seal_actor IS NOT NULL)))
       OR a.updated_by_actor_id::text IS DISTINCT FROM coalesce(b.following_actor,b.seal_actor,b.origin_actor)
       OR a.updated_at IS DISTINCT FROM coalesce(b.following_at,b.seal_at,b.origin_at))>0
    OR EXISTS (SELECT 1 FROM epoch e JOIN ordered b ON b.attempt_id=e.attempt_id
      WHERE e.created_by_actor_id::text<>b.first_actor OR e.created_at<>b.first_at
       OR e.updated_by_actor_id::text<>coalesce(b.seal_actor,b.origin_actor)
       OR e.updated_at<>coalesce(b.seal_at,b.origin_at))""")
    invalid(connection, """WITH ordered AS (
      SELECT principal_revision,executor_actor_id,authority_revision,
        lag(principal_revision) OVER w AS previous_revision,
        lag(executor_actor_id) OVER w AS previous_actor,
        lag(authority_revision) OVER (PARTITION BY semantic_command->>'command' ORDER BY generation) AS previous_authority
      FROM scribeswell.corpus_command_outcome
      WINDOW w AS (ORDER BY generation,CASE WHEN semantic_command->>'command'='corpus.seal' THEN 1 ELSE 0 END))
      SELECT EXISTS (SELECT 1 FROM ordered WHERE principal_revision<previous_revision
        OR (principal_revision=previous_revision AND executor_actor_id<>previous_actor)
        OR authority_revision<previous_authority)""")


def preflight_controller_history(connection, expected_actor):
    try:
        state, expected = checked_prepared(connection, expected_actor, controller_history=True)
        history(connection, expected)
        return state
    except BaselineError:
        raise
    except Exception:
        raise BaselineError('scribeswell_history_validation_failed') from None
