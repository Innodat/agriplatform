"""Literal wire fixtures exercise declaration validation, never trusted custody."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
import base64
import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from test_caller_preparation_input import VALID

TIME = '0001-01-01T00:00:00.000001Z'
TARGET = dict(kind='local_disposable', binding='fixture_db', host='127.0.0.1', port=5432,
              database='fixture_db', login='scribeswell_migrator')
REQUEST = json.loads(VALID)
COMMANDS = ('corpus.begin', 'corpus.recover', 'corpus.seal')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def snapshot(time):
    common = dict(database_login='scribeswell_corpus_operator', enabled=False, revision='1',
                  created_by_actor_id=REQUEST['preparer_actor_id'], updated_by_actor_id=REQUEST['preparer_actor_id'],
                  created_at=time, updated_at=time)
    custody = REQUEST['custody']
    principal = common | {key: custody[key] for key in ('executor_actor_id', 'actor_kind', 'actor_key', 'preparation_evidence_ref')}
    return dict(principal=principal, authorities=[common | dict(source_id='tanakh', command=c) for c in COMMANDS])


def records(mode='create', outcome=None, count=4):
    outcome = outcome or ('committed' if mode == 'create' else 'reused')
    admission = dict(request_b64=base64.b64encode(VALID).decode(), target=deepcopy(TARGET),
                     reviewed_commit='a'*40, image_digest='sha256:'+'b'*64,
                     admission_ref='fixture:admission', admission_class='synthetic_fixture')
    session = dict(session_user='scribeswell_migrator', current_user='scribeswell_migrator', database='fixture_db',
                   backend_pid=12, backend_start=TIME, server_identity_ref='fixture:server', ledger_head='scribeswell_0003',
                   transaction_isolation='read committed', transaction_read_only=False, authority_observation_ref='fixture:authority')
    before = dict(principal=None, authorities=[]) if mode == 'create' else snapshot(TIME)
    intended = snapshot(None if mode == 'create' else TIME)
    codes = dict(committed='preparation_committed', reused='preparation_reused', rejected='admission_denied',
                 rolled_back='preparation_rolled_back', unknown='outcome_unconfirmed')
    proof = dict(kind=dict(committed='commit_ack', reused='commit_ack', rejected='pre_write', rolled_back='rollback_ack', unknown='unconfirmed')[outcome],
                 evidence_ref=None if outcome == 'unknown' else 'fixture:proof')
    finish = ('finished', dict(outcome=outcome, code=codes[outcome], proof=proof))
    phases = [('admitted', admission), ('intent', dict(mode=mode, session=session, before=before, intended=intended)),
              ('prepared', dict(observed=snapshot(TIME)))]
    phases = phases[:count-1] + [finish]
    result = []
    for index, (kind, payload) in enumerate(phases, 1):
        result.append(dict(schema_version=1, run_id=REQUEST['run_id'], sequence=index,
                           previous_sha256=digest(result[-1]) if result else None,
                           request_sha256=digest(REQUEST), target_sha256=digest(TARGET),
                           recorded_by_actor_id=REQUEST['preparer_actor_id'], recorded_at=TIME, kind=kind, payload=payload))
    return result


def wire(rows):
    return tuple(canonical(row) for row in rows)


def relink(rows):
    for index, row in enumerate(rows):
        row['previous_sha256'] = digest(rows[index-1]) if index else None
    return rows


def codec():
    from apps.scribeswell.backend import caller_preparation_evidence
    return caller_preparation_evidence


def parse(rows):
    c = codec()
    return c.parse_attempt(wire(rows), request_raw=VALID, target=c.parse_target_descriptor(canonical(TARGET)))


def reject(call):
    c = codec()
    with pytest.raises(c.PreparationEvidenceError) as failure:
        call()
    error = failure.value
    assert str(error) == error.code == 'scribeswell_preparation_evidence_invalid'
    assert error.__cause__ is None and error.__context__ is None


def test_create_acceptance_and_immutable_roundtrip():
    c = codec()
    rows = records()
    result = parse(rows)
    assert len(result) == 4 and result[-1].payload.outcome == 'committed'
    assert tuple(c.encode_record(row) for row in result) == wire(rows)
    assert c.record_digest(wire(rows)[-1]) == digest(rows[-1])
    assert c.request_digest(VALID) == digest(REQUEST)
    assert c.target_digest(c.parse_target_descriptor(canonical(TARGET))) == digest(TARGET)
    with pytest.raises(FrozenInstanceError):
        result[2].payload.observed.principal.revision = '2'
    assert type(result[2].payload.observed.authorities) is tuple
    assert 'fixture:' not in repr(result[0]) and not hasattr(result[0], '__dict__')


def reply(rows):
    end = rows[-1]
    return dict(schema_version=1, run_id=end['run_id'], request_sha256=end['request_sha256'], target_sha256=end['target_sha256'],
                record_sequence=end['sequence'], record_sha256=digest(end), outcome=end['payload']['outcome'], code=end['payload']['code'])


@pytest.mark.parametrize('mode', ['create', 'reuse'])
def test_result_binds_terminal_and_accepts_transport_whitespace(mode):
    c = codec()
    rows = records(mode)
    raw = canonical(reply(rows))
    target = c.parse_target_descriptor(canonical(TARGET))
    value = c.parse_worker_result(raw + b' '*(4096-len(raw)), request_raw=VALID, target=target, records=wire(rows))
    assert c.encode_worker_result(value) == raw
    reject(lambda: c.parse_worker_result(raw+b' '*(4097-len(raw)), request_raw=VALID, target=target, records=wire(rows)))


@pytest.mark.parametrize('count,outcome', [(2,'rejected'),(2,'unknown'),(3,'rolled_back'),(3,'unknown'),(4,'rolled_back'),(4,'unknown')])
def test_other_valid_terminal_paths(count, outcome):
    assert parse(records(count=count, outcome=outcome))[-1].payload.outcome == outcome


@pytest.mark.parametrize('count', [1,2,3])
def test_nonterminal_prefix_is_valid_but_not_reply(count):
    c = codec()
    rows = records()[:count]
    assert len(parse(rows)) == count
    reject(lambda: c.parse_worker_result(canonical(reply(records())), request_raw=VALID,
                                        target=c.parse_target_descriptor(canonical(TARGET)), records=wire(rows)))


@pytest.mark.parametrize('mutate', [
    lambda r: r[0].update(extra=1), lambda r: r[0].update(schema_version=True),
    lambda r: r[0].update(sequence=0), lambda r: r[0].update(previous_sha256='a'*64),
    lambda r: r[1].update(previous_sha256='c'*64), lambda r: r[1].update(run_id='44444444-4444-4444-8444-444444444444'),
    lambda r: r[1].update(request_sha256='c'*64), lambda r: r[1].update(target_sha256='c'*64),
    lambda r: r[1].update(recorded_by_actor_id=REQUEST['custody']['executor_actor_id']),
    lambda r: r[0]['payload'].update(request_b64=base64.b64encode(VALID).decode()+'='),
    lambda r: r[0]['payload'].update(reviewed_commit='A'*40), lambda r: r[0]['payload'].update(image_digest='b'*64),
    lambda r: r[0]['payload'].update(admission_ref='unsafe private marker'),
    lambda r: r[0]['payload'].update(admission_class='trusted'),
    lambda r: r[1]['payload']['session'].update(transaction_read_only=0),
    lambda r: r[1]['payload']['session'].update(backend_pid=True),
    lambda r: r[1]['payload']['session'].update(database='other'),
    lambda r: r[1]['payload']['session'].update(current_user='scribeswell_corpus_operator'),
    lambda r: r[1]['payload']['session'].update(ledger_head='scribeswell_0002'),
    lambda r: r[1]['payload']['session'].update(transaction_isolation='serializable'),
    lambda r: r[1]['payload'].update(before=snapshot(TIME)),
    lambda r: r[1]['payload']['intended']['principal'].update(created_at=TIME),
    lambda r: r[2]['payload']['observed']['authorities'][0].update(updated_at='0001-01-01T00:00:00.000002Z'),
    lambda r: r[2]['payload']['observed']['principal'].update(updated_at=None),
    lambda r: r[2]['payload']['observed']['principal'].update(revision=1),
    lambda r: r[2]['payload']['observed']['principal'].update(enabled=True),
    lambda r: r[2]['payload']['observed']['principal'].update(actor_key='other'),
    lambda r: r[2]['payload']['observed']['principal'].update(created_by_actor_id=REQUEST['custody']['executor_actor_id']),
    lambda r: r[2]['payload']['observed']['authorities'][0].update(source_id='other'),
    lambda r: r[2]['payload']['observed']['authorities'].reverse(),
    lambda r: r[2]['payload']['observed']['authorities'].pop(),
    lambda r: r[3]['payload'].update(code='preparation_reused'),
    lambda r: r[3]['payload']['proof'].update(evidence_ref=None),
    lambda r: r[3]['payload']['proof'].update(kind='rollback_ack'),
    lambda r: r[3].update(sequence=3),
])
def test_bad_bound_records(mutate):
    rows = records()
    mutate(rows)
    # Relink all except deliberately broken previous digest.
    if rows[0]['previous_sha256'] is None and rows[1]['previous_sha256'] != 'c'*64:
        relink(rows)
    reject(lambda: parse(rows))


@pytest.mark.parametrize('field', list(records()[0]))
def test_envelope_requires_every_field(field):
    rows=records(); del rows[0][field]
    reject(lambda: parse(rows))


@pytest.mark.parametrize('time', ['0000-01-01T00:00:00.000000Z', '2025-02-29T00:00:00.000000Z',
    '2024-02-30T00:00:00.000000Z', '2024-01-01T00:00:60.000000Z', '2024-01-01T00:00:00Z',
    '2024-01-01T00:00:00.000000+00:00', '2024-01-01t00:00:00.000000Z', None, 1])
def test_bad_times(time):
    rows=records(); rows[0]['recorded_at']=time
    reject(lambda: parse(relink(rows)))


@pytest.mark.parametrize('change', [dict(port=True), dict(port=0), dict(port=65536), dict(binding='a-b'), dict(host='localhost'),
    dict(host='127.0.0.2'), dict(database='other'), dict(login='postgres'), dict(kind='other'), dict(extra=1)])
def test_target_rejections(change):
    reject(lambda: codec().parse_target_descriptor(canonical(TARGET | change)))


def test_supabase_direct_and_loopback_ipv6():
    c=codec()
    for target in [TARGET | dict(host='::1'), dict(kind='supabase', binding='https://a.supabase.co', host='db.a.supabase.co',
                                               port=5432, database='postgres', login='scribeswell_migrator')]:
        assert c.target_digest(c.parse_target_descriptor(canonical(target))) == digest(target)


@pytest.mark.parametrize('raw', [b'', b'null', b'[]', b'\xef\xbb\xbf{}', b'\xff', b'{"schema_version":1,"schema_version":1}',
    b'{"x":NaN}', b'{"x":1.0}', b'{"x":1e0}', b'{}{}', b'['*1000+b']'*1000, bytearray(b'{}'), None, b' '*32769])
def test_malformed_raw_has_safe_error(raw):
    reject(lambda: codec().parse_record(raw))


def test_record_spelling_is_canonical():
    raw=wire(records())[0]
    for bad in [b' '+raw, raw+b'\n', json.dumps(records()[0]).encode(), raw.replace(b'fixture', b'\\u0066ixture',1)]:
        reject(lambda: codec().parse_record(bad))


@pytest.mark.parametrize('field', list(reply(records())))
def test_reply_binds_every_field(field):
    c=codec(); rows=records(); value=reply(rows)
    value[field] = 3 if field in ('schema_version','record_sequence') else 'invalid'
    reject(lambda: c.parse_worker_result(canonical(value), request_raw=VALID,
        target=c.parse_target_descriptor(canonical(TARGET)), records=wire(rows)))


def test_independent_expected_inputs_and_raw_request_identity():
    c=codec(); rows=records(); target=c.parse_target_descriptor(canonical(TARGET))
    # Same semantic request, different original bytes must not silently replace custody.
    assert c.request_digest(VALID+b' ') == c.request_digest(VALID)
    reject(lambda: c.parse_attempt(wire(rows), request_raw=VALID+b' ', target=target))
    reject(lambda: c.parse_attempt(wire(rows), request_raw=VALID,
        target=replace(target, binding='other',database='other')))
    for bad in [(), wire(rows)*2, list(wire(rows)), iter(wire(rows))]:
        reject(lambda: c.parse_attempt(bad, request_raw=VALID, target=target))


def test_encoders_revalidate_manual_values_and_clear_outer_context():
    c=codec(); value=parse(records())[0]
    for bad in [replace(value,schema_version=True), replace(value,payload={}),
                replace(value,payload=replace(value.payload,target=replace(value.payload.target,port=False)))]:
        reject(lambda: c.encode_record(bad))
    try:
        raise RuntimeError('private-marker')
    except RuntimeError:
        reject(lambda: c.parse_record(b'invalid private-marker'))
        reject(lambda: c.request_digest(b'invalid private-marker'))


def test_reuse_preserves_all_original_values():
    rows=records('reuse'); rows[2]['payload']['observed']['principal']['updated_at']='0001-01-01T00:00:00.000002Z'
    reject(lambda: parse(relink(rows)))


def test_fixed_wire_and_digest_oracles():
    c=codec()
    raw=b'{"binding":"fixture_db","database":"fixture_db","host":"127.0.0.1","kind":"local_disposable","login":"scribeswell_migrator","port":5432}'
    assert canonical(TARGET) == raw
    assert c.target_digest(c.parse_target_descriptor(raw)) == 'aea71c02c02a982835f9d6fe4b29ca2e537c5da4d4b1bd33dad2adc349f53b6a'
    assert c.request_digest(VALID) == '41a8e946917b6f372b4042f31a695c879b7a9849c754d66851cf7adbaa60ef0d'
    assert c.record_digest(wire(records())[0]) == '94d7a0f747da402c0933a6b16e7c09be9d7433cc8b71060580050f9c3ba7ef7a'


# Every nested closed shape gets independent extra/missing/type rejection checks.
SHAPES = [(0,('payload',)), (0,('payload','target')), (1,('payload',)),
          (1,('payload','session')), (1,('payload','before')), (1,('payload','intended')),
          (1,('payload','intended','principal')), (1,('payload','intended','authorities',0)),
          (2,('payload',)), (2,('payload','observed')), (2,('payload','observed','principal')),
          (2,('payload','observed','authorities',0)), (3,('payload',)), (3,('payload','proof'))]


@pytest.mark.parametrize('index,path',SHAPES)
@pytest.mark.parametrize('mutation',['extra','missing','type'])
def test_all_nested_shapes_closed(index,path,mutation):
    rows=records(); parent=rows[index]
    for part in path[:-1]:
        parent=parent[part]
    node=parent[path[-1]]
    if mutation == 'extra':
        node['extra']=None
    elif mutation == 'missing':
        del node[next(iter(node))]
    else:
        parent[path[-1]]=[]
    reject(lambda: parse(relink(rows)))


@pytest.mark.parametrize('count,outcome',[(2,'committed'),(2,'rolled_back'),(2,'reused'),(3,'committed'),(3,'reused'),(3,'rejected'),(4,'rejected')])
def test_forbidden_terminal_paths(count,outcome):
    reject(lambda: parse(records(count=count,outcome=outcome)))


def test_no_record_after_terminal_or_missing_middle():
    rows=records(count=2,outcome='unknown')
    rows.append(records()[2])
    reject(lambda: parse(relink(rows)))
    rows=records(); rows.pop(1)
    reject(lambda: parse(relink(rows)))
    reject(lambda: parse(records('reuse',outcome='committed')))
    reject(lambda: parse(records('create',outcome='reused')))


@pytest.mark.parametrize('change',[dict(binding='https://a.supabase.co/'),dict(binding='https://A.supabase.co'),
    dict(host='db.b.supabase.co'),dict(host='aws.pooler.supabase.com'),dict(database='other'),
    dict(binding='https://a-b.supabase.co',host='db.a-b.supabase.co'),
    dict(binding='https://'+'a'*64+'.supabase.co',host='db.'+'a'*64+'.supabase.co')])
def test_supabase_target_projection_rejects_aliases(change):
    target=dict(kind='supabase',binding='https://a.supabase.co',host='db.a.supabase.co',port=5432,database='postgres',login='scribeswell_migrator')
    reject(lambda: codec().parse_target_descriptor(canonical(target|change)))


def test_base64_rejects_noncanonical_pad_bits_and_whitespace():
    rows=records(); encoded=rows[0]['payload']['request_b64']
    # Fixture has two padding characters. Alternate low pad bits decode identically.
    assert encoded.endswith('==')
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    alias=encoded[:-3]+alphabet[alphabet.index(encoded[-3])+1]+'=='
    assert base64.b64decode(alias)==VALID
    for bad in [alias, encoded.rstrip('='), encoded+'\n', '!!!!', '_'+encoded[1:], base64.b64encode(b' '*8193).decode()]:
        rows=records(); rows[0]['payload']['request_b64']=bad
        reject(lambda: parse(relink(rows)))


def test_depth_duplicate_and_bytes_limits():
    c=codec(); raw=wire(records())[0]
    for bad in [raw.replace(b'"schema_version":1',b'"schema_version":1,"schema_version":1',1),
                raw.replace(b'"port":5432',b'"port":5432,"port":5432'), raw+b' '*(32769-len(raw)),
                raw.replace(b'"sequence":1',b'"sequence":1.0'),raw.replace(b'"sequence":1',b'"sequence":NaN'),
                raw.replace(b'"sequence":1',b'"sequence":'+b'9'*5000)]:
        reject(lambda: c.parse_record(bad))
    for depth in (8,9,2000):
        reject(lambda: c.parse_record(b'{"x":'+b'['*depth+b'0'+b']'*depth+b'}'))
    reject(lambda: c.parse_target_descriptor(b' '*32769))
    # Lower phase clocks need not be monotonic; they are declarations, not authority.
    rows=records(); rows[0]['recorded_at']='9999-12-31T23:59:59.999999Z'
    assert len(parse(relink(rows)))==4


def test_hostile_encoder_objects_never_invoke_hooks():
    c=codec(); record=parse(records())[0]
    class Hostile:
        def __deepcopy__(self,*args):
            pytest.fail('deepcopy invoked')
        def __iter__(self):
            pytest.fail('iterator invoked')
        def __str__(self):
            pytest.fail('coercion invoked')
        def __eq__(self,other):
            pytest.fail('equality invoked')
    class OtherRecord(c.AttemptRecord):
        pass
    for bad in [Hostile(),replace(record,payload=Hostile()),replace(record,payload=replace(record.payload,admission_ref=Hostile())),
                replace(record,payload=replace(record.payload,admission_ref='x'*131073)),
                OtherRecord(**{name:getattr(record,name) for name in record.__slots__})]:
        reject(lambda: c.encode_record(bad))
    terminal=reply(records()); value=c.WorkerResult(**terminal)
    reject(lambda: c.encode_worker_result(replace(value,record_sequence=True)))
    reject(lambda: c.target_digest(replace(record.payload.target,port=Hostile())))
    # Cyclic models are constructible using object.__setattr__; depth budget bounds them.
    cyclic=replace(record)
    object.__setattr__(cyclic,'payload',cyclic)
    reject(lambda: c.encode_record(cyclic))


def test_fresh_stdlib_interpreter_has_no_runtime_effects(tmp_path):
    import subprocess
    script=r'''
import base64, builtins, dataclasses, datetime, functools, hashlib, json, math, os, re, sys, typing, uuid
rows,request,target=json.loads(sys.stdin.buffer.read())
rows=tuple(base64.b64decode(row) for row in rows)
request=base64.b64decode(request)
sys.path.insert(0,sys.argv[1]); paths=list(sys.path)
original=builtins.__import__
def guarded(name,*args,**kwargs):
    allowed={'apps','apps.scribeswell','apps.scribeswell.backend','apps.scribeswell.migrations',
        'apps.scribeswell.backend.caller_preparation_evidence','apps.scribeswell.backend.caller_preparation_input',
        'apps.scribeswell.migrations.release_profile'}
    assert name.split('.')[0] in sys.stdlib_module_names or name in allowed
    return original(name,*args,**kwargs)
builtins.__import__=guarded
def forbidden(*args,**kwargs):
    raise AssertionError('unexpected runtime effect')
os.getenv=forbidden
class ForbiddenEnvironment:
    __getitem__=__iter__=__contains__=__len__=get=items=keys=values=copy=forbidden
os.environ=ForbiddenEnvironment()
from apps.scribeswell.backend import caller_preparation_evidence as c
assert sys.path==paths
builtins.open=forbidden
def audit(event,args):
    if event=='open' or event.startswith(('socket.','subprocess.','os.putenv','os.listdir','os.scandir')):
        forbidden()
sys.addaudithook(audit)
target=c.parse_target_descriptor(json.dumps(target).encode())
parsed=c.parse_attempt(rows,request_raw=request,target=target)
assert tuple(c.encode_record(row) for row in parsed)==rows
assert c.record_digest(rows[0])==hashlib.sha256(rows[0]).hexdigest()
assert len(c.target_digest(target))==len(c.request_digest(request))==64
end=parsed[-1]
reply=c.WorkerResult(1,end.run_id,end.request_sha256,end.target_sha256,4,c.record_digest(rows[-1]),'committed','preparation_committed')
assert c.parse_worker_result(c.encode_worker_result(reply),request_raw=request,target=target,records=rows)==reply
try:
    c.parse_record(b'invalid private-marker')
except c.PreparationEvidenceError as error:
    assert error.__context__ is None and error.__cause__ is None
else:
    raise AssertionError('invalid accepted')
assert sys.path==paths
'''
    payload=canonical([[base64.b64encode(raw).decode() for raw in wire(records())],base64.b64encode(VALID).decode(),TARGET])
    result=subprocess.run([sys.executable,'-I','-S','-c',script,str(Path(__file__).resolve().parents[3])],
                          input=payload,cwd=tmp_path,env={},capture_output=True,timeout=15)
    assert result.returncode==0,result.stderr.decode()


@pytest.mark.parametrize('code', ['admission_denied', 'target_mismatch', 'preparation_conflict'])
def test_all_prewrite_codes_roundtrip(code):
    c = codec()
    rows = records(count=2, outcome='rejected')
    rows[-1]['payload']['code'] = code
    result = c.parse_worker_result(canonical(reply(rows)), request_raw=VALID,
        target=c.parse_target_descriptor(canonical(TARGET)), records=wire(rows))
    assert result.code == code
    assert c.encode_worker_result(result) == canonical(reply(rows))


@pytest.mark.parametrize('kind', ['rollback_ack', 'ended_no_effects'])
@pytest.mark.parametrize('count', [3, 4])
def test_all_rollback_proofs_preserved(kind, count):
    c = codec()
    rows = records(count=count, outcome='rolled_back')
    rows[-1]['payload']['proof']['kind'] = kind
    assert parse(rows)[-1].payload.proof.kind == kind
    assert c.encode_record(parse(rows)[-1]) == canonical(rows[-1])


@pytest.mark.parametrize('target', [TARGET | dict(host='::1'),
    dict(kind='supabase', binding='https://a.supabase.co', host='db.a.supabase.co',
         port=65535, database='postgres', login='scribeswell_migrator')])
@pytest.mark.parametrize('mode', ['create', 'reuse'])
def test_other_target_complete_attempt_and_reply(target, mode):
    c = codec()
    rows = records(mode)
    rows[0]['payload']['target'] = target
    rows[1]['payload']['session']['database'] = target['database']
    for row in rows:
        row['target_sha256'] = digest(target)
    relink(rows)
    expected = c.parse_target_descriptor(canonical(target))
    parsed = c.parse_attempt(wire(rows), request_raw=VALID, target=expected)
    assert parsed[1].payload.session.database == target['database']
    result = c.parse_worker_result(canonical(reply(rows)), request_raw=VALID, target=expected, records=wire(rows))
    assert result.outcome == ('committed' if mode == 'create' else 'reused')
    assert tuple(c.encode_record(row) for row in parsed) == wire(rows)
    rows[1]['payload']['session']['database'] = 'wrong_db'
    reject(lambda: c.parse_attempt(wire(relink(rows)), request_raw=VALID, target=expected))


def test_reuse_accepts_eight_distinct_unchanged_times():
    rows = records('reuse')
    varied = snapshot(TIME)
    for index, row in enumerate([varied['principal'], *varied['authorities']]):
        row['created_at'] = f'2024-02-29T01:02:03.{index*2:06d}Z'
        row['updated_at'] = f'2024-02-29T01:02:03.{index*2+1:06d}Z'
    rows[1]['payload']['before'] = deepcopy(varied)
    rows[1]['payload']['intended'] = deepcopy(varied)
    rows[2]['payload']['observed'] = deepcopy(varied)
    assert len(parse(relink(rows))) == 4
    rows[2]['payload']['observed']['authorities'][1]['updated_at'] = TIME
    reject(lambda: parse(relink(rows)))


@pytest.mark.parametrize('time', ['0001-01-01T00:00:00.000000Z', '9999-12-31T23:59:59.999999Z',
    '2024-02-29T00:00:00.000000Z', '2000-02-29T23:59:59.999999Z'])
def test_valid_gregorian_boundaries_in_all_timestamp_roles(time):
    rows = records()
    for row in rows:
        row['recorded_at'] = time
    rows[1]['payload']['session']['backend_start'] = time
    rows[2]['payload']['observed'] = snapshot(time)
    assert parse(relink(rows))[2].payload.observed.principal.created_at == time


def test_descriptor_transport_limit_isolated_from_shape_and_json_validity():
    c = codec()
    raw = canonical(TARGET)
    at_limit = raw + b' '*(32768-len(raw))
    assert c.parse_target_descriptor(at_limit) == c.parse_target_descriptor(raw)
    reject(lambda: c.parse_target_descriptor(at_limit+b' '))
    # Closed v1 valid records never reach depth 8 or 32768 bytes: overdeep or
    # oversized record probes also violate shape/canonical/field bounds. They
    # prove safe rejection, not independent coverage of these redundant guards.


@pytest.mark.parametrize('decoder', ['target', 'reply'])
@pytest.mark.parametrize('mutation', ['duplicate', 'bom', 'utf8', 'float', 'nonfinite', 'trailing', 'bool', 'depth'])
def test_other_public_decoders_reject_malformed_transport(decoder, mutation):
    c = codec()
    raw = canonical(TARGET if decoder == 'target' else reply(records()))
    field = b'"port":5432' if decoder == 'target' else b'"schema_version":1'
    replacement = dict(duplicate=field+b','+field, float=field.split(b':')[0]+b':1.0',
                       nonfinite=field.split(b':')[0]+b':NaN', bool=field.split(b':')[0]+b':true')
    if mutation in replacement:
        raw = raw.replace(field, replacement[mutation], 1)
    elif mutation == 'bom':
        raw = b'\xef\xbb\xbf'+raw
    elif mutation == 'utf8':
        raw = b'\xff'+raw
    elif mutation == 'trailing':
        raw += b'{}'
    else:
        raw = b'['*1000+raw+b']'*1000
    if decoder == 'target':
        reject(lambda: c.parse_target_descriptor(raw))
    else:
        reject(lambda: c.parse_worker_result(raw, request_raw=VALID,
            target=c.parse_target_descriptor(canonical(TARGET)), records=wire(records())))


@pytest.mark.parametrize('change', ['session', 'snapshot', 'authority', 'proof', 'outcome', 'payload_type'])
def test_encoders_revalidate_other_manual_phase_models(change):
    c = codec()
    values = parse(records())
    if change == 'session':
        value = replace(values[1], payload=replace(values[1].payload,
            session=replace(values[1].payload.session, backend_pid=True)))
    elif change == 'snapshot':
        value = replace(values[2], payload=replace(values[2].payload,
            observed=replace(values[2].payload.observed, principal=None)))
    elif change == 'authority':
        observed = values[2].payload.observed
        bad_row = replace(observed.authorities[0], revision=1)
        value = replace(values[2], payload=replace(values[2].payload,
            observed=replace(observed, authorities=(bad_row, *observed.authorities[1:]))))
    elif change == 'proof':
        value = replace(values[3], payload=replace(values[3].payload,
            proof=replace(values[3].payload.proof, evidence_ref=None)))
    elif change == 'outcome':
        value = replace(values[3], payload=replace(values[3].payload, outcome='unknown'))
    else:
        value = replace(values[3], payload=values[0].payload)
    reject(lambda: c.encode_record(value))


@pytest.mark.parametrize('field,bad', [('schema_version', True), ('run_id', 'invalid'), ('request_sha256', 'A'*64),
    ('target_sha256', '0'*63), ('record_sequence', 5), ('record_sha256', None), ('outcome', 'unknown'), ('code', [])])
def test_encoder_revalidates_all_worker_result_fields(field, bad):
    c = codec()
    value = c.WorkerResult(**reply(records()))
    reject(lambda: c.encode_worker_result(replace(value, **{field: bad})))
