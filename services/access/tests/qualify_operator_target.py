"""Consume a root-prepared native target/head6; no infrastructure provisioning."""
import argparse
from hashlib import sha256
import json
import signal
from pathlib import Path
import sys
from urllib.parse import urlsplit
from uuid import uuid4
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from identity_operator_target import load_target, ROOT
import operator_cli as cli
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

def check(condition, code):
    if not condition:
        raise RuntimeError(code)

def private_record(work, name, value):
    with cli.dev.directory(work) as fd:
        __import__('native_cli').write_private(fd, name, (json.dumps(value, sort_keys=True) + '\n').encode())

def verify_effect(before, after, value, receipt):
    check(set(before) == set(after), 'qualification_table_set_changed')
    keys = {'actor': 'id', 'operation_outcome': 'id', 'business_event': 'event_id'}
    added = {}
    for table, rows in before.items():
        if table not in keys:
            check(after[table] == rows, 'qualification_unrelated_table_changed')
            continue
        key = keys[table]
        old = {row[key]: row for row in rows}
        new = {row[key]: row for row in after[table]}
        check(len(old) == len(rows) and len(new) == len(after[table]), 'qualification_duplicate_identity')
        check(all((new.get(identity) == row for identity, row in old.items())), 'qualification_existing_row_changed')
        additions = [row for identity, row in new.items() if identity not in old]
        check(len(additions) == 1, 'qualification_effect_count_invalid')
        added[table] = additions[0]
    actor = added['actor']
    outcome = added['operation_outcome']
    event = added['business_event']
    payload = value['payload']
    result = receipt['result']
    actor_id = payload['actor_id']
    principals = [row for row in before['operator_principals'] if row['database_login'] == 'identity_operator']
    check(len(principals) == 1, 'qualification_principal_invalid')
    executor = principals[0]['executor_actor_id']
    check(all((actor.get(key) == payload[key] for key in ('kind', 'actor_key', 'display_name'))) and actor['id'] == actor_id, 'qualification_actor_invalid')
    check(actor['created_by'] == actor['updated_by'] == executor, 'qualification_actor_attribution_invalid')
    check(result['target'] == {'actor_id': actor_id} and result['disposition'] == 'created', 'qualification_receipt_target_invalid')
    check(outcome['operation_id'] == value['operation_id'] and outcome['command_type'] == value['command'] and (outcome['executor_actor_id'] == executor), 'qualification_outcome_identity_invalid')
    check(outcome['result'] == {key: child for key, child in result.items() if key != 'command'}, 'qualification_outcome_result_invalid')
    check(outcome['command_version'] == receipt['command_version'] and outcome['result_version'] == receipt['result_version'], 'qualification_outcome_version_invalid')
    check(event['event_id'] == result['event_id'] and event['outcome_id'] == outcome['id'] and (event['target'] == {'actor_id': actor_id}) and (event['target_key'] == actor_id), 'qualification_event_link_invalid')
    check(event['event_type'] == 'identity.actor_registered' and event['event_version'] == 1 and (event['executor_actor_id'] == executor), 'qualification_event_identity_invalid')
    check(event['transition'] == {'kind': payload['kind'], 'actor_key': payload['actor_key']} and event['reason_code'] == value['reason_code'] and (event['evidence_ref'] == value.get('evidence_ref')), 'qualification_event_transition_invalid')
    for row in (outcome, event):
        check(row['scope_kind'] == 'platform' and row['scope_id'] is None and (row['initiator_actor_id'] is None), 'qualification_effect_scope_invalid')

def qualify(target_path, fixture_path):
    target = load_target(target_path)
    fixture_path = Path(fixture_path).absolute()
    with cli.dev.directory(fixture_path.parent) as fd:
        cli.dev.check_private(fd)
        fixture = cli.dev.decode(cli.dev.read_at(fd, fixture_path.name, protected=True))
    check(type(fixture) is dict and set(fixture) == {'owner_url', 'run_id', 'database'}, 'qualification_fixture_invalid')
    parsed = urlsplit(fixture['owner_url'])
    check((fixture['run_id'], fixture['database']) == (target.run_id, target.database), 'qualification_binding_invalid')
    check((parsed.scheme, parsed.hostname, parsed.port, parsed.path, parsed.username, parsed.query, parsed.fragment) == ('postgresql', '127.0.0.1', target.port, '/' + target.database, 'identity_migrator', '', ''), 'qualification_owner_invalid')
    engine = create_engine(fixture['owner_url'].replace('postgresql://', 'postgresql+psycopg://', 1), poolclass=NullPool, hide_parameters=True, connect_args={'connect_timeout': 3, 'options': '-c statement_timeout=5000 -c lock_timeout=2000'})

    def snapshot():
        with engine.connect() as c:
            check(c.execute(text('SELECT version_num FROM identity.alembic_version')).scalar_one() == 'identity_0006', 'qualification_head_invalid')
            tables = c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='identity' AND table_type='BASE TABLE' ORDER BY table_name")).scalars().all()
            values = {}
            for table in tables:
                name = c.dialect.identifier_preparer.quote(table)
                rows = c.exec_driver_sql('SELECT to_jsonb(t) FROM identity.' + name + ' t').scalars().all()
                values[table] = sorted(rows, key=lambda value: json.dumps(value, sort_keys=True, default=str))
            return values
    run = target.path.parent
    work = run / ('operator-qualification-' + uuid4().hex)
    work.mkdir(mode=0o700)

    def invoke(arguments, expected_status=0, *, lost_response=False):
        launcher = 'import contextlib,io,json,sys\nfrom pathlib import Path\nsys.path.insert(0,str(Path(sys.argv[1]).parent))\nimport operator_cli as c\nif sys.argv[2]==\'lost\':\n    original=c.images.bounded_command\n    def substitute(command,cwd,env,timeout,limit,**kwargs):\n        source="import sys,json,time;from pathlib import Path;sys.path.insert(0,"+repr(str(Path(c.__file__).parent))+");import operator_cli as c;import native_cli;c.os.environ.clear();receipt=c.worker(json.loads(sys.stdin.buffer.read()));witness=Path("+repr(sys.argv[3])+");\\nwith c.dev.directory(witness.parent) as fd:native_cli.write_private(fd,witness.name,json.dumps(receipt).encode())\\ntime.sleep(30)"\n        return original([sys.executable,\'-I\',\'-B\',\'-c\',source],cwd,env,timeout,limit,**kwargs)\n    c.images.bounded_command=substitute\noutput=io.StringIO()\nwith contextlib.redirect_stdout(output):status=c.main(sys.argv[4:])\nprint(json.dumps({\'exit_status\':status,\'result\':json.loads(output.getvalue())}))\n'
        raw = cli.images.bounded_command([sys.executable, '-I', '-B', '-c', launcher, str(ROOT / 'services/access/operator_cli.py'), 'lost' if lost_response else 'normal', str(work / 'post-commit-witness.json'), *arguments], ROOT, {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, 16, 8192)
        envelope = cli.dev.decode(raw)
        check(type(envelope) is dict and set(envelope) == {'exit_status', 'result'}, 'qualification_transport_invalid')
        check(type(envelope['exit_status']) is int and envelope['exit_status'] == expected_status, 'qualification_exit_invalid')
        return envelope['result']

    def refused(arguments):
        return invoke(arguments, 2)
    base = ['--owner', 'identity', '--target', str(target.path)]
    value = dict(schema_version=1, operation_id=str(uuid4()), command='actor.register_system', scope={'kind': 'platform'}, reason_code='synthetic_fixture', payload=dict(actor_id=str(uuid4()), kind='service', actor_key='synthetic:target:' + uuid4().hex, display_name='Synthetic target qualification', expected_absent=True))
    body = json.dumps(value).encode()
    with cli.dev.directory(work) as fd:
        __import__('native_cli').write_private(fd, 'command.json', body)
    arguments = ['execute', *base, '--command-file', str(work / 'command.json')]
    try:
        before = snapshot()
        lost = invoke(arguments, 2, lost_response=True)
        check(lost == dict(code='operation_unavailable', operation_id=value['operation_id']), 'qualification_lost_response_invalid')
        receipt = invoke(['outcome', *base, '--command', 'actor.register_system', '--operation-id', value['operation_id']])
        cli._receipt(receipt, value['operation_id'])
        with cli.dev.directory(work) as fd:
            witness=cli.dev.decode(cli.dev.read_at(fd,'post-commit-witness.json',protected=True))
        check(witness==receipt,'qualification_commit_witness_mismatch')
        check(receipt['result']['disposition'] == 'created', 'qualification_not_created')
        after = snapshot()
        verify_effect(before, after, value, receipt)
        check(invoke(arguments) == receipt, 'qualification_replay_changed')
        check(invoke(['outcome', *base, '--command', 'actor.register_system', '--operation-id', value['operation_id']]) == receipt, 'qualification_lookup_changed')
        absent = str(uuid4())
        check(refused(['outcome', *base, '--command', 'actor.register_system', '--operation-id', absent]) == dict(operation_id=absent, status='unresolved'), 'qualification_unresolved_invalid')
        mismatch = refused(['execute', '--owner', 'identity', '--target', str(work / 'identity-operator.json'), '--command-file', str(work / 'command.json')])
        check(mismatch == dict(code='identity_operator_target_invalid', operation_id=value['operation_id']), 'qualification_target_refusal')
        with cli.dev.directory(work) as fd:
            __import__('native_cli').write_private(fd, 'malformed.json', b'{"secret":"do-not-echo"}')
        check(refused(['execute', *base, '--command-file', str(work / 'malformed.json')]) == {'code': 'identity_operator_input_invalid'}, 'qualification_input_refusal')
        check(snapshot() == after, 'qualification_replay_or_refusal_mutated')
        with engine.connect() as c:
            authority = c.execute(text("SELECT id,enabled FROM identity.operator_authorities WHERE database_login='identity_operator' AND command='actor.register_system' AND scope_kind='platform' AND org_id IS NULL AND application_id IS NULL AND target_account_id IS NULL")).one()
            check(authority.enabled is True, 'qualification_authority_not_enabled')
        recovery = dict(schema_version=1, run_id=target.run_id, database=target.database, database_login='identity_operator', authority_id=str(authority.id), original_enabled=authority.enabled)
        private_record(work, 'authority-restoration.json', recovery)
        try:
            with engine.begin() as c:
                c.execute(text('UPDATE identity.operator_authorities SET enabled=false WHERE id=:id'), {'id': authority.id})
            revoked = snapshot()
            denied = dict(code='access_denied', operation_id=value['operation_id'])
            check(refused(arguments) == denied, 'qualification_revoked_execute_disclosed')
            check(refused(['outcome', *base, '--command', 'actor.register_system', '--operation-id', value['operation_id']]) == denied, 'qualification_revoked_lookup_disclosed')
            check(snapshot() == revoked, 'qualification_revoked_mutated')
        finally:
            with engine.begin() as c:
                c.execute(text('UPDATE identity.operator_authorities SET enabled=:enabled WHERE id=:id'), {'id': authority.id, 'enabled': authority.enabled})
                restored_authority = c.execute(text('SELECT enabled,revision FROM identity.operator_authorities WHERE id=:id'), {'id': authority.id}).one()
                check(restored_authority.enabled is authority.enabled, 'qualification_authority_restore_failed')
            private_record(work, 'authority-restored.json', {**recovery, 'restored': True, 'revision': str(restored_authority.revision)})
        restored = snapshot()
        check({k: v for k, v in restored.items() if k != 'operator_authorities'} == {k: v for k, v in after.items() if k != 'operator_authorities'}, 'qualification_restore_business_changed')
        check(invoke(['outcome', *base, '--command', 'actor.register_system', '--operation-id', value['operation_id']]) == receipt, 'qualification_restored_lookup_changed')
        return dict(ok=True, run_id=target.run_id, operation_id=value['operation_id'], receipt=receipt, unchanged_after_replay_lookup_refusal=True, revoked_execute_lookup_denied=True, authority_enabled_restored=True, committed_response_loss_recovered=True, command_sha256=sha256(body).hexdigest())
    finally:
        engine.dispose()

def main():
    previous = {name: signal.getsignal(name) for name in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    previous_alarm = signal.alarm(0)

    def deadline(signum, frame):
        signal.alarm(0)
        raise cli.WorkerInterrupted()
    try:
        for name in previous:
            signal.signal(name, deadline)
        signal.alarm(120)
        parser = argparse.ArgumentParser(allow_abbrev=False)
        parser.add_argument('--target', required=True)
        parser.add_argument('--fixture', required=True)
        args = parser.parse_args()
        result = qualify(args.target, args.fixture)
    except Exception:
        print('{"code":"operator_target_qualification_failed"}')
        return 2
    finally:
        signal.alarm(0)
        for name, handler in previous.items():
            signal.signal(name, handler)
        if previous_alarm:
            signal.alarm(previous_alarm)
    print(json.dumps(result, sort_keys=True))
    return 0
if __name__ == '__main__':
    sys.exit(main())
