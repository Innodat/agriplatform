"""Pure closed-v1 declarations. Validation proves neither custody nor persistence.

parse_record checks one record's structure/local semantics; parse_attempt checks
its complete prefix against independently supplied original request/target.
parse_worker_result additionally requires a terminal prefix. None resolve proof
references, authenticate admissions, read storage or execute database operations.
"""
from dataclasses import dataclass, fields
from datetime import datetime
from functools import wraps
import base64
import hashlib
import json
import re
from uuid import UUID

from apps.scribeswell.backend.caller_preparation_input import parse_preparation_request


class PreparationEvidenceError(ValueError):
    """Fixed safe failure; no submitted payload or decoder/caller exception chain."""
    code = 'scribeswell_preparation_evidence_invalid'

    def __init__(self):
        super().__init__(self.code)


def _safe(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, TypeError, AttributeError, RecursionError, OverflowError):
            pass
        try:
            raise PreparationEvidenceError() from None
        except PreparationEvidenceError as error:
            error.__context__ = None
            raise
    return call


@dataclass(frozen=True, slots=True, repr=False)
class TargetDescriptor:
    kind: str
    binding: str
    host: str
    port: int
    database: str
    login: str


@dataclass(frozen=True, slots=True, repr=False)
class SessionObservation:
    session_user: str
    current_user: str
    database: str
    backend_pid: int
    backend_start: str
    server_identity_ref: str
    ledger_head: str
    transaction_isolation: str
    transaction_read_only: bool
    authority_observation_ref: str


@dataclass(frozen=True, slots=True, repr=False)
class PrincipalRow:
    database_login: str
    enabled: bool
    revision: str
    executor_actor_id: str
    actor_kind: str
    actor_key: str
    preparation_evidence_ref: str
    created_by_actor_id: str
    updated_by_actor_id: str
    created_at: str | None
    updated_at: str | None


@dataclass(frozen=True, slots=True, repr=False)
class AuthorityRow:
    database_login: str
    source_id: str
    command: str
    enabled: bool
    revision: str
    created_by_actor_id: str
    updated_by_actor_id: str
    created_at: str | None
    updated_at: str | None


@dataclass(frozen=True, slots=True, repr=False)
class Snapshot:
    principal: PrincipalRow | None
    authorities: tuple[AuthorityRow, ...]


@dataclass(frozen=True, slots=True, repr=False)
class AdmissionPayload:
    request_b64: str
    target: TargetDescriptor
    reviewed_commit: str
    image_digest: str
    admission_ref: str
    admission_class: str


@dataclass(frozen=True, slots=True, repr=False)
class IntentPayload:
    mode: str
    session: SessionObservation
    before: Snapshot
    intended: Snapshot


@dataclass(frozen=True, slots=True, repr=False)
class PreparedPayload:
    observed: Snapshot


@dataclass(frozen=True, slots=True, repr=False)
class Proof:
    kind: str
    evidence_ref: str | None


@dataclass(frozen=True, slots=True, repr=False)
class FinishedPayload:
    outcome: str
    code: str
    proof: Proof


@dataclass(frozen=True, slots=True, repr=False)
class AttemptRecord:
    schema_version: int
    run_id: str
    sequence: int
    previous_sha256: str | None
    request_sha256: str
    target_sha256: str
    recorded_by_actor_id: str
    recorded_at: str
    kind: str
    payload: AdmissionPayload | IntentPayload | PreparedPayload | FinishedPayload


@dataclass(frozen=True, slots=True, repr=False)
class WorkerResult:
    schema_version: int
    run_id: str
    request_sha256: str
    target_sha256: str
    record_sequence: int
    record_sha256: str
    outcome: str
    code: str


_MODELS = (TargetDescriptor, SessionObservation, PrincipalRow, AuthorityRow, Snapshot,
           AdmissionPayload, IntentPayload, PreparedPayload, Proof, FinishedPayload,
           AttemptRecord, WorkerResult)
_COMMANDS = ('corpus.begin', 'corpus.recover', 'corpus.seal')
_CODES = {'committed': ('preparation_committed',), 'reused': ('preparation_reused',),
          'rejected': ('admission_denied', 'target_mismatch', 'preparation_conflict'),
          'rolled_back': ('preparation_rolled_back',), 'unknown': ('outcome_unconfirmed',)}


def _require(condition):
    if not condition:
        raise ValueError()


def _match(value, pattern):
    _require(type(value) is str and re.fullmatch(pattern, value, re.ASCII) is not None)


def _uuid(value):
    _require(type(value) is str)
    parsed = UUID(value)
    _require(parsed.int != 0 and str(parsed) == value)


def _reference(value):
    _match(value, r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}')


def _hash(value):
    _match(value, r'[0-9a-f]{64}')


def _integer(value, low, high):
    _require(type(value) is int and low <= value <= high)


def _time(value):
    _match(value, r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z')
    datetime(int(value[:4]), int(value[5:7]), int(value[8:10]), int(value[11:13]),
             int(value[14:16]), int(value[17:19]), int(value[20:26]))


def _shape(value, model):
    _require(type(value) is dict and value.keys() == {field.name for field in fields(model)})


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def _sha(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _pairs(items):
    value = {}
    for key, item in items:
        _require(key not in value)
        value[key] = item
    return value


def _reject_number(raw):
    raise ValueError()


def _json(raw, limit, max_depth):
    _require(type(raw) is bytes and len(raw) <= limit)
    text = raw.decode('utf-8', errors='strict')
    _require(not text.startswith('\ufeff'))
    value = json.loads(text, object_pairs_hook=_pairs, parse_float=_reject_number, parse_constant=_reject_number)
    pending = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if type(item) in (dict, list):
            _require(depth <= max_depth)
            pending.extend((child, depth+1) for child in (item.values() if type(item) is dict else item))
    return value


def _project(value):
    """Bounded exact-type projection; never deepcopy or invoke caller hooks."""
    budget = [2048, 131072]

    def visit(item, depth):
        budget[0] -= 1
        _require(budget[0] >= 0 and depth <= 16)
        kind = type(item)
        if item is None or kind in (bool, int):
            if kind is int:
                _integer(item, 0, 2147483647)
            return item
        if kind is str:
            _require(len(item) <= 32768)
            budget[1] -= len(item)
            _require(budget[1] >= 0)
            return item
        if kind is tuple:
            _require(len(item) <= 4)
            return [visit(child, depth+1) for child in item]
        _require(kind in _MODELS)
        return {field.name: visit(object.__getattribute__(item, field.name), depth+1) for field in fields(kind)}
    return visit(value, 1)


def _target(value):
    _shape(value, TargetDescriptor)
    _require(value['login'] == 'scribeswell_migrator')
    _integer(value['port'], 1, 65535)
    _match(value['binding'], r'[\x00-\x7f]{1,8192}')
    _match(value['host'], r'[a-z0-9.:-]{1,253}')
    if value['kind'] == 'local_disposable':
        _match(value['binding'], r'[A-Za-z_][A-Za-z0-9_]{0,62}')
        _require(value['host'] in ('127.0.0.1', '::1') and value['database'] == value['binding'])
    else:
        _require(value['kind'] == 'supabase')
        _match(value['binding'], r'https://[a-z0-9]+\.supabase\.co')
        ref = value['binding'][8:-12]
        _require(len(ref) <= 63 and value['host'] == 'db.'+ref+'.supabase.co' and value['database'] == 'postgres')
    return TargetDescriptor(**value)


def _session(value):
    _shape(value, SessionObservation)
    _require(value['session_user'] == value['current_user'] == 'scribeswell_migrator')
    _match(value['database'], r'[A-Za-z_][A-Za-z0-9_]{0,62}')
    _integer(value['backend_pid'], 1, 2147483647)
    _time(value['backend_start'])
    _reference(value['server_identity_ref'])
    _reference(value['authority_observation_ref'])
    _require(value['ledger_head'] == 'scribeswell_0003' and value['transaction_isolation'] == 'read committed')
    _require(value['transaction_read_only'] is False)
    return SessionObservation(**value)


def _row(value, model, template):
    _shape(value, model)
    _require(value['database_login'] == 'scribeswell_corpus_operator' and value['enabled'] is False)
    _require(type(value['revision']) is str and value['revision'] == '1')
    for key in ('created_by_actor_id', 'updated_by_actor_id'):
        _uuid(value[key])
    for key in ('created_at', 'updated_at'):
        if template:
            _require(value[key] is None)
        else:
            _time(value[key])
    if model is PrincipalRow:
        _uuid(value['executor_actor_id'])
        _require(value['actor_kind'] == 'service')
        _match(value['actor_key'], r'[a-z][a-z0-9_.:-]{0,127}')
        _reference(value['preparation_evidence_ref'])
    else:
        _match(value['source_id'], r'[A-Za-z0-9][A-Za-z0-9._:-]{0,63}')
        _require(value['command'] in _COMMANDS)
    return model(**value)


def _snapshot(value, *, template=False, empty=False):
    _shape(value, Snapshot)
    _require(type(value['authorities']) is list)
    if empty:
        _require(value['principal'] is None and value['authorities'] == [])
        return Snapshot(None, ())
    principal = _row(value['principal'], PrincipalRow, template)
    _require(len(value['authorities']) == 3)
    authorities = tuple(_row(row, AuthorityRow, template) for row in value['authorities'])
    _require(tuple(row.command for row in authorities) == _COMMANDS)
    return Snapshot(principal, authorities)


def _original(value):
    _require(type(value) is str and len(value) <= 10924)
    raw = base64.b64decode(value, validate=True)
    _require(base64.b64encode(raw).decode('ascii') == value)
    return raw, parse_preparation_request(raw)


def _request_wire(request):
    # Only the existing parser creates these values; no caller models are accepted.
    return {field.name: ({inner.name: getattr(request.custody, inner.name) for inner in fields(request.custody)}
                         if field.name == 'custody' else getattr(request, field.name)) for field in fields(request)}


def _outcome(outcome, code):
    _require(type(outcome) is str and outcome in _CODES and type(code) is str and code in _CODES[outcome])


def _finished(value):
    _shape(value, FinishedPayload)
    _outcome(value['outcome'], value['code'])
    proof = value['proof']
    _shape(proof, Proof)
    kinds = {'committed': ('commit_ack',), 'reused': ('commit_ack',), 'rejected': ('pre_write',),
             'rolled_back': ('rollback_ack', 'ended_no_effects'), 'unknown': ('unconfirmed',)}
    _require(proof['kind'] in kinds[value['outcome']])
    if value['outcome'] == 'unknown':
        _require(proof['evidence_ref'] is None)
    else:
        _reference(proof['evidence_ref'])
    return FinishedPayload(value['outcome'], value['code'], Proof(**proof))


def _record(raw):
    value = _json(raw, 32768, 8)
    _require(raw == _canonical(value))
    _shape(value, AttemptRecord)
    _integer(value['schema_version'], 1, 1)
    _integer(value['sequence'], 1, 4)
    _uuid(value['run_id'])
    _uuid(value['recorded_by_actor_id'])
    _time(value['recorded_at'])
    for key in ('request_sha256', 'target_sha256'):
        _hash(value[key])
    if value['sequence'] == 1:
        _require(value['previous_sha256'] is None)
    else:
        _hash(value['previous_sha256'])
    kind, payload = value['kind'], value['payload']
    if kind == 'admitted':
        _require(value['sequence'] == 1)
        _shape(payload, AdmissionPayload)
        original, request = _original(payload['request_b64'])
        target = _target(payload['target'])
        _match(payload['reviewed_commit'], r'(?:[0-9a-f]{40}|[0-9a-f]{64})')
        _match(payload['image_digest'], r'sha256:[0-9a-f]{64}')
        _reference(payload['admission_ref'])
        _require(payload['admission_class'] in ('synthetic_fixture', 'owner_verified'))
        _require(value['run_id'] == request.run_id and value['recorded_by_actor_id'] == request.preparer_actor_id)
        _require(value['request_sha256'] == _sha(_request_wire(request)) and value['target_sha256'] == _sha(payload['target']))
        parsed = AdmissionPayload(**(payload | {'target': target}))
    elif kind == 'intent':
        _require(value['sequence'] == 2)
        _shape(payload, IntentPayload)
        _require(payload['mode'] in ('create', 'reuse'))
        create = payload['mode'] == 'create'
        before = _snapshot(payload['before'], empty=create)
        intended = _snapshot(payload['intended'], template=create)
        if not create:
            _require(before == intended)
        parsed = IntentPayload(payload['mode'], _session(payload['session']), before, intended)
    elif kind == 'prepared':
        _require(value['sequence'] == 3)
        _shape(payload, PreparedPayload)
        parsed = PreparedPayload(_snapshot(payload['observed']))
    else:
        _require(kind == 'finished' and value['sequence'] in (2, 3, 4))
        parsed = _finished(payload)
    return AttemptRecord(**(value | {'payload': parsed}))


def _bind_snapshot(snapshot, request):
    principal = snapshot.principal
    if principal is None:
        return
    for key in ('executor_actor_id', 'actor_kind', 'actor_key', 'preparation_evidence_ref'):
        _require(getattr(principal, key) == getattr(request.custody, key))
    for row in (principal, *snapshot.authorities):
        _require(row.created_by_actor_id == row.updated_by_actor_id == request.preparer_actor_id)
    _require(all(row.source_id == request.custody.source_id for row in snapshot.authorities))


def _attempt(records, request_raw, target):
    _require(type(records) is tuple and 1 <= len(records) <= 4)
    _require(all(type(raw) is bytes for raw in records) and sum(map(len, records)) <= 131072)
    request = parse_preparation_request(request_raw)
    _require(type(target) is TargetDescriptor)
    target_wire = _project(target)
    _target(target_wire)
    request_hash, target_hash = _sha(_request_wire(request)), _sha(target_wire)
    parsed = tuple(_record(raw) for raw in records)
    _require(parsed[0].kind == 'admitted')
    _require(_original(parsed[0].payload.request_b64)[0] == request_raw and parsed[0].payload.target == target)
    for index, record in enumerate(parsed):
        _require(record.sequence == index+1 and record.run_id == request.run_id and record.request_sha256 == request_hash
                 and record.target_sha256 == target_hash and record.recorded_by_actor_id == request.preparer_actor_id)
        _require(record.previous_sha256 == (hashlib.sha256(records[index-1]).hexdigest() if index else None))
    kinds = tuple(record.kind for record in parsed)
    _require(kinds in (('admitted',), ('admitted', 'intent'), ('admitted', 'intent', 'prepared'),
                       ('admitted', 'finished'), ('admitted', 'intent', 'finished'),
                       ('admitted', 'intent', 'prepared', 'finished')))
    intent = parsed[1].payload if len(parsed) > 1 and parsed[1].kind == 'intent' else None
    if intent:
        _require(intent.session.database == target.database)
        _bind_snapshot(intent.before, request)
        _bind_snapshot(intent.intended, request)
    if len(parsed) >= 3 and parsed[2].kind == 'prepared':
        observed = parsed[2].payload.observed
        _bind_snapshot(observed, request)
        if intent.mode == 'reuse':
            _require(observed == intent.intended)
        else:
            observed_wire = _project(observed)
            times = []
            for row in [observed_wire['principal'], *observed_wire['authorities']]:
                for key in ('created_at', 'updated_at'):
                    times.append(row[key])
                    row[key] = None
            _require(len(set(times)) == 1 and observed_wire == _project(intent.intended))
    if parsed[-1].kind == 'finished':
        allowed = ('rejected', 'unknown') if len(parsed) == 2 else ('rolled_back', 'unknown')
        if len(parsed) == 4:
            allowed += ('committed' if intent.mode == 'create' else 'reused',)
        _require(parsed[-1].payload.outcome in allowed)
    return parsed


def _reply(raw):
    value = _json(raw, 4096, 2)
    _shape(value, WorkerResult)
    _integer(value['schema_version'], 1, 1)
    _integer(value['record_sequence'], 2, 4)
    _uuid(value['run_id'])
    for key in ('request_sha256', 'target_sha256', 'record_sha256'):
        _hash(value[key])
    _outcome(value['outcome'], value['code'])
    return WorkerResult(**value)


@_safe
def parse_record(raw: bytes) -> AttemptRecord:
    """Check one canonical record; use parse_attempt for cross-record bindings."""
    return _record(raw)


@_safe
def encode_record(value: AttemptRecord) -> bytes:
    """Revalidate exact immutable model types and local semantics before encoding."""
    _require(type(value) is AttemptRecord)
    raw = _canonical(_project(value))
    _record(raw)
    return raw


@_safe
def record_digest(raw: bytes) -> str:
    _record(raw)
    return hashlib.sha256(raw).hexdigest()


@_safe
def parse_target_descriptor(raw: bytes) -> TargetDescriptor:
    return _target(_json(raw, 32768, 2))


@_safe
def target_digest(value: TargetDescriptor) -> str:
    _require(type(value) is TargetDescriptor)
    projected = _project(value)
    _target(projected)
    return _sha(projected)


@_safe
def request_digest(raw: bytes) -> str:
    return _sha(_request_wire(parse_preparation_request(raw)))


@_safe
def parse_attempt(records: tuple[bytes, ...], *, request_raw: bytes, target: TargetDescriptor) -> tuple[AttemptRecord, ...]:
    """Validate a complete retained prefix; no trust or durability is conferred."""
    return _attempt(records, request_raw, target)


@_safe
def parse_worker_result(raw: bytes, *, request_raw: bytes, target: TargetDescriptor,
                        records: tuple[bytes, ...]) -> WorkerResult:
    """Require a terminal bound prefix; parent must independently trust its custody."""
    result = _reply(raw)
    end = _attempt(records, request_raw, target)[-1]
    _require(end.kind == 'finished')
    for key in ('run_id', 'request_sha256', 'target_sha256'):
        _require(getattr(result, key) == getattr(end, key))
    _require(result.record_sequence == end.sequence and result.record_sha256 == hashlib.sha256(records[-1]).hexdigest())
    _require(result.outcome == end.payload.outcome and result.code == end.payload.code)
    return result


@_safe
def encode_worker_result(value: WorkerResult) -> bytes:
    """Validate shape only; acceptance still requires parse_worker_result context."""
    _require(type(value) is WorkerResult)
    raw = _canonical(_project(value))
    _reply(raw)
    return raw
