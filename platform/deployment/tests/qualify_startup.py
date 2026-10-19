#!/usr/bin/env python3
"""Guarded synthetic startup proofs and explicit real postgres-bootstrap control."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dev
import startup_lifecycle
from startup_lifecycle import auth_catalog_exec as _original_auth_catalog_exec
from startup_lifecycle import cli_db_backend_exec as _original_cli_db_backend_exec
import startup
import volumes
import qualify_volumes
import qualify_daemon_images
import daemon_images
import qualify_resources

BOOTSTRAP_CONTROLS = ['postgres-bootstrap']
EXECUTION_CONTROLS = ['pinned-cli-postgres', 'pinned-cli-postgres-persistence', 'pinned-cli-postgres-initialized', 'pinned-cli-postgres-auth-boundary', 'pinned-cli-postgres-auth-migration', 'pinned-cli-postgres-auth-catalog', 'pinned-cli-postgres-cli-db-backend']

GUARDED_CONTROLS = ['guarded-fresh'] + ['guarded-' + name for name in qualify_resources.GUARDED_FAILURES]


def _auth_catalog_corruption_exec(mode):
    """Internal rollback-only SQL fixture; never accepted by production routes."""
    import copy
    if mode not in ('pre', 'post'): startup_lifecycle.refuse()
    def literal(value): return "'"+value.replace("'", "''")+"'"
    body=copy.deepcopy(_original_auth_catalog_exec(mode));query=body['Cmd'][-1]
    prefix="BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
    assert query.startswith(prefix) and query.endswith(' COMMIT;')
    predicate=query[len(prefix):-len(' COMMIT;')]
    if mode=='pre':
        mutations=["INSERT INTO auth.schema_migrations(version) VALUES ('20260831180000')",
            'CREATE TABLE auth.mfa_recovery_code_sets(id uuid)','CREATE TABLE auth.mfa_recovery_codes(id uuid)',
            'CREATE TABLE auth.one_time_tokens(expires_at timestamptz)']
        mutations += ["DELETE FROM auth.schema_migrations WHERE version="+literal(v) for v in startup_lifecycle.AUTH_POSTGRES_BASELINE_VERSIONS]
        mutations += ["INSERT INTO auth.schema_migrations(version) VALUES ('synthetic-extra')",
            "ALTER TABLE auth.schema_migrations DROP CONSTRAINT schema_migrations_pkey; INSERT INTO auth.schema_migrations(version) VALUES ('20171026211738')",
            "ALTER TABLE auth.schema_migrations DROP CONSTRAINT schema_migrations_pkey; ALTER TABLE auth.schema_migrations ALTER COLUMN version DROP NOT NULL; INSERT INTO auth.schema_migrations(version) VALUES (NULL)"]
    else:
        mutations=["DELETE FROM auth.schema_migrations WHERE version="+literal(v) for v in startup_lifecycle.AUTH_CATALOG_VERSIONS]
        mutations += ["INSERT INTO auth.schema_migrations(version) VALUES ('synthetic-extra')",
            "ALTER TABLE auth.schema_migrations DROP CONSTRAINT schema_migrations_pkey; INSERT INTO auth.schema_migrations(version) VALUES ('00')",
            "ALTER TABLE auth.schema_migrations DROP CONSTRAINT schema_migrations_pkey; ALTER TABLE auth.schema_migrations ALTER COLUMN version DROP NOT NULL; INSERT INTO auth.schema_migrations(version) VALUES (NULL)"]
        mutations += ['ALTER TABLE auth.'+name+' RENAME TO env_catalog_hidden_'+name for name in ('users','identities','sessions','one_time_tokens','mfa_recovery_code_sets','mfa_recovery_codes')]
        mutations += ['ALTER TABLE auth.one_time_tokens DROP COLUMN expires_at',
            'ALTER TABLE auth.one_time_tokens ALTER COLUMN expires_at TYPE text USING expires_at::text',
            'ALTER TABLE auth.one_time_tokens ALTER COLUMN expires_at SET NOT NULL',
            'ALTER TABLE auth.sessions RENAME TO env_catalog_sessions; CREATE VIEW auth.sessions AS SELECT * FROM auth.env_catalog_sessions']
    # Every corruption and predicate is rolled back inside its own subtransaction.
    # Only the original predicate's P0001 is accepted; other errors fail the exec.
    checks=("DO $qualification$ DECLARE mutation text; rejected boolean; predicate text := "+literal(predicate)+"; BEGIN FOREACH mutation IN ARRAY ARRAY["+
        ','.join(literal(m) for m in mutations)+"]::text[] LOOP BEGIN EXECUTE mutation; EXECUTE 'SET LOCAL ROLE postgres'; rejected := false; BEGIN EXECUTE predicate; EXCEPTION WHEN raise_exception THEN rejected := true; END; EXECUTE 'RESET ROLE'; IF NOT rejected THEN RAISE EXCEPTION USING ERRCODE='XX001', MESSAGE='predicate accepted corrupt state'; END IF; RAISE EXCEPTION USING ERRCODE='ZX001', MESSAGE='rollback synthetic case'; EXCEPTION WHEN SQLSTATE 'ZX001' THEN NULL; END; END LOOP; END $qualification$; ")
    body['Cmd'][-1]=prefix.replace('BEGIN READ ONLY;','BEGIN;')+checks+'SET LOCAL ROLE postgres; '+predicate+' ROLLBACK;'
    body['Cmd'][body['Cmd'].index('-h')+1]='/var/run/postgresql'
    body['Cmd'][body['Cmd'].index('-U')+1]='supabase_admin'
    return body, len(mutations)

def _cli_db_backend_semantic_exec(mode):
    """Fixed typed session inputs exercise the unchanged production SQL predicates."""
    import copy
    if mode not in ('present', 'departed'): startup_lifecycle.refuse()
    def literal(value): return "'" + value.replace("'", "''") + "'"
    body = copy.deepcopy(_original_cli_db_backend_exec(mode))
    query = body['Cmd'][-1]
    prefix = "BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
    assert query.startswith(prefix) and query.endswith(' COMMIT;')
    predicate = query[len(prefix):-len(' COMMIT;')]
    columns = ('pid', 'backend_type', 'client_addr', 'usename', 'datname', 'client_port', 'state')
    types = ('integer', 'text', 'inet', 'text', 'text', 'integer', 'text')
    valid = (-1, 'client backend', '192.0.2.1', 'postgres', 'postgres', 49152, 'idle')
    def changed(index, value):
        row = list(valid)
        row[index] = value
        return tuple(row)
    def relation(rows):
        def cell(value, kind):
            if value == 'observer-pid': return 'pg_backend_pid()::integer'
            return ('NULL' if value is None else str(value) if type(value) is int else literal(value)) + '::' + kind
        if rows:
            return '(VALUES ' + ','.join('(' + ','.join(cell(v, t) for v, t in zip(row, types)) + ')' for row in rows) + ') AS backend_fixture(' + ','.join(columns) + ')'
        return '(SELECT ' + ','.join('NULL::' + t + ' AS ' + c for c, t in zip(columns, types)) + ' WHERE false) AS backend_fixture'
    ignored = [changed(0, 'observer-pid'), changed(2, None), changed(1, 'autovacuum worker'),
               changed(2, '127.0.0.1'), changed(2, '::1')]
    if mode == 'present':
        cases = [([valid], False), ([changed(2, '2001:db8::1')], False)]
        cases += [([row], True) for row in ignored]
        cases += [([], True), ([valid, valid], True)]
        cases += [([changed(index, value)], True) for index, value in
                  [(3, 'anon'), (4, 'other_database'), (6, 'active'), (3, None), (4, None),
                   (6, None), (5, None), (5, 0), (5, -1)]]
        cases += [([valid] + ignored, False)]
    else:
        # Exactly one real bounded departure timeout; all other cases exit immediately.
        cases = [([], False), (ignored, False), ([changed(3, 'anon')[:-1] + ('active',)], True)]
    checks = [(relation(rows), rejected, False) for rows, rejected in cases]
    # Fixed anon role datum exercises visibility denial without changing roles/grants.
    checks.append((relation([valid] if mode == 'present' else []), True, True))
    checks_sql = ','.join('(' + literal(source) + ',' + ('true' if rejected else 'false') + ','
                          + ('true' if anon else 'false') + ')' for source, rejected, anon in checks)
    wrapper = ("DO $qualification$ DECLARE production_predicate text := " + literal(predicate) + "; "
               "predicate text; source text; expected_rejected boolean; anon_observer boolean; rejected boolean; "
               "BEGIN FOR source, expected_rejected, anon_observer IN SELECT * FROM (VALUES " + checks_sql +
               ") AS cases(source, expected_rejected, anon_observer) LOOP rejected := false; "
               "predicate := replace(production_predicate, 'pg_stat_activity', source); "
               "IF anon_observer THEN predicate := replace(predicate, 'current_user', '''anon'''); END IF; "
               "BEGIN EXECUTE predicate; EXCEPTION WHEN SQLSTATE 'P0001' THEN rejected := true; END; "
               "IF rejected IS DISTINCT FROM expected_rejected THEN RAISE EXCEPTION USING ERRCODE='XX001', "
               "MESSAGE='semantic predicate result mismatch'; END IF; END LOOP; END $qualification$;")
    body['Cmd'][-1] = prefix + wrapper + ' ROLLBACK;'
    return body, len(checks)


def _cli_db_backend_late_zero_exec():
    """One delayed-zero regression, separately bounded by the existing five seconds."""
    import copy
    def literal(value): return "'" + value.replace("'", "''") + "'"
    body = copy.deepcopy(_original_cli_db_backend_exec('departed'))
    query = body['Cmd'][-1]
    prefix = "BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
    assert query.startswith(prefix) and query.endswith(' COMMIT;')
    predicate = query[len(prefix):-len(' COMMIT;')]
    # Referencing slept in the endpoint predicate forces the materialized delay
    # even though the eventual NULL endpoint yields no matching external backend.
    relation = ("(WITH delay AS MATERIALIZED (SELECT pg_sleep(3.05) AS slept) "
                "SELECT -1::integer AS pid, 'client backend'::text AS backend_type, "
                "NULLIF(delay.slept::text,'')::inet AS client_addr, 'postgres'::text AS usename, "
                "'postgres'::text AS datname, 49152::integer AS client_port, 'idle'::text AS state "
                "FROM delay) AS backend_fixture")
    predicate = predicate.replace('pg_stat_activity', relation)
    wrapper = ("DO $qualification$ DECLARE rejected boolean := false; BEGIN "
               "BEGIN EXECUTE " + literal(predicate) + "; "
               "EXCEPTION WHEN SQLSTATE 'P0001' THEN rejected := true; END; "
               "IF NOT rejected THEN RAISE EXCEPTION USING ERRCODE='XX001', "
               "MESSAGE='late zero predicate accepted'; END IF; END $qualification$;")
    body['Cmd'][-1] = prefix + wrapper + ' ROLLBACK;'
    return body


def _cli_db_backend_transition_exec(late=False):
    """Two fixed observations: occupied, then timely or late empty; no DB writes."""
    import copy
    if type(late) is not bool: startup_lifecycle.refuse()
    def literal(value): return "'" + value.replace("'", "''") + "'"
    body = copy.deepcopy(_original_cli_db_backend_exec('departed'))
    query = body['Cmd'][-1]
    prefix = "BEGIN READ ONLY; SET LOCAL statement_timeout = '5s'; SET LOCAL lock_timeout = '1s'; SET LOCAL idle_in_transaction_session_timeout = '5s'; "
    assert query.startswith(prefix) and query.endswith(' COMMIT;')
    predicate = query[len(prefix):-len(' COMMIT;')]
    # A transaction-local custom setting counts evaluations of the fixed input
    # relation, so the first count cannot silently be empty under scheduling delay.
    # ROLLBACK and process exit discard it; no role, table or business data changes.
    relation = ("(WITH observation AS MATERIALIZED (SELECT "
                "set_config('env.backend_observations', "
                "(current_setting('env.backend_observations')::integer + 1)::text, true)::integer AS n), "
                "delay AS MATERIALIZED (SELECT n, pg_sleep(CASE WHEN n = 2 THEN "
                + ('3.05' if late else '0') + " ELSE 0 END) AS slept FROM observation) "
                "SELECT -1::integer AS pid, 'client backend'::text AS backend_type, "
                "CASE WHEN n = 1 THEN '192.0.2.1'::inet "
                "ELSE NULLIF(delay.slept::text,'')::inet END AS client_addr, "
                "'postgres'::text AS usename, 'postgres'::text AS datname, "
                "49152::integer AS client_port, 'idle'::text AS state FROM delay) AS backend_fixture")
    predicate = predicate.replace('pg_stat_activity', relation)
    # The caught exception rolls back transaction-local settings. Carry only the
    # fixed observation ordinal in exception DETAIL before that rollback; the
    # original conditions, deadlines, exits and rejection messages stay intact.
    rejection = "RAISE EXCEPTION 'cli db backend departure failed'"
    assert predicate.count(rejection) == 2
    predicate = predicate.replace(rejection, rejection + " USING DETAIL = current_setting('env.backend_observations')")
    wrapper = ("DO $qualification$ DECLARE rejected boolean := false; observed_count text; BEGIN "
               "PERFORM set_config('env.backend_observations', '0', true); "
               "BEGIN EXECUTE " + literal(predicate) + "; "
               "EXCEPTION WHEN SQLSTATE 'P0001' THEN rejected := true; "
               "GET STACKED DIAGNOSTICS observed_count = PG_EXCEPTION_DETAIL; END; "
               "IF NOT rejected THEN observed_count := current_setting('env.backend_observations'); END IF; "
               "IF rejected IS DISTINCT FROM " + ('true' if late else 'false')
               + " OR observed_count IS DISTINCT FROM '2' "
               "THEN RAISE EXCEPTION USING ERRCODE='XX001', "
               "MESSAGE='temporal predicate result mismatch'; END IF; END $qualification$;")
    body['Cmd'][-1] = prefix + wrapper + ' ROLLBACK;'
    return body


def guarded_qualify(args, target):
    """One private peer connects the pinned CLI to the real retained ENV owner."""
    startup.existing_images(args)
    observations = qualify_daemon_images.expected_images(args.run_id)
    scenario = 'positive' if args.control == 'guarded-fresh' else args.control.removeprefix('guarded-')
    daemon = qualify_resources.GuardedDaemon(target, args.run_id, observations, scenario)
    args._image_observations = observations
    args._profile_control = 'fresh-lifecycle-positive'
    with daemon.serve() as endpoint:
        args._guarded_target = (args.target, endpoint)
        try:
            result = startup.qualify(args)
        except dev.Refusal as error:
            if qualify_resources.GUARDED_FAILURES.get(scenario, (None,))[0] != error.code:
                raise
            daemon.validate_events(success=False)
            raise
    daemon.validate_events()
    if scenario != 'positive' or result.get('guarded_volume_owner_proven') is not True:
        startup.fail('boundary_not_proven')
    result['api_events'] = [{'method': method, 'path': path} for method, path, _ in daemon.events]
    return result


def main(argv=None):
    try:
        parser = dev.Parser(add_help=False, allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--run-id', required=True)
        parser.add_argument('--control', choices=['positive', 'invalid-network', 'contaminated-workdir', 'reject-command', 'invalid-selection-plan',
                                                       'invalid-create-script', 'invalid-create-environment', 'invalid-create-routing', 'invalid-create-request',
                                                       'lifecycle-positive', 'invalid-lifecycle-target', 'invalid-lifecycle-archive', 'invalid-lifecycle-order',
                                                       'fresh-lifecycle-positive', 'fresh-existing', 'fresh-racing', 'fresh-invalid-lifecycle-target',
                                                       'fresh-invalid-lifecycle-archive', 'fresh-invalid-lifecycle-order'] + GUARDED_CONTROLS + BOOTSTRAP_CONTROLS + EXECUTION_CONTROLS,
                            default='positive')
        args = parser.parse_args(argv)
        if args.control in BOOTSTRAP_CONTROLS:
            import startup_lifecycle
            print(json.dumps(startup_lifecycle.qualify_bootstrap(args), sort_keys=True))
            return 0
        if args.control in EXECUTION_CONTROLS:
            print(json.dumps(startup.qualify(args), sort_keys=True))
            return 0
        networks = volumes.networks
        networks.validate_run_id(args.run_id)
        target = dev.decode(dev.read(Path(args.target).absolute()))
        if args.control in GUARDED_CONTROLS:
            print(json.dumps(guarded_qualify(args, target), sort_keys=True))
            return 0
        if not args.control.startswith('fresh-'):
            daemon = qualify_volumes.SyntheticDaemon(target, args.run_id)
            with daemon.serve() as endpoint:
                acquired = volumes.acquire(args.target, args.run_id, _socket_path=endpoint)
            daemon.validate_events()
            args._volume = acquired['volume']
        startup.existing_images(args)
        image_daemon = qualify_daemon_images.SyntheticDaemon(qualify_daemon_images.expected_images(args.run_id))
        with image_daemon.serve() as endpoint:
            args._image_observations = daemon_images.acquire(args.target, args.run_id, _socket_path=endpoint)
        image_daemon.validate_events()
        result = startup.qualify(args)
        print(json.dumps(result, sort_keys=True))
        return 0
    except dev.Refusal as error:
        print(json.dumps(dev.refusal_result(error)))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps({'ok': False, 'runtime_ready': False, 'stage': 'startup', 'code': 'startup_proof_refused'}))
    except KeyboardInterrupt:
        print(json.dumps({'ok': False, 'runtime_ready': False, 'stage': 'startup', 'code': 'interrupted'}))
    return 2


if __name__ == '__main__':
    sys.exit(main())
