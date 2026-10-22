"""Pure publication-command qualification; prepared values convey no authority."""
from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Literal

from corpus_evidence import LABEL, SHA256, build_source_candidate, serialize_candidate

MAX_COMMAND_BYTES = 65536
_UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.ASCII)
_GENERATION = re.compile(r'[1-9][0-9]{0,18}', re.ASCII)
_EVIDENCE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,255}', re.ASCII)
ReasonCode = Literal['source_import', 'source_recovery', 'source_seal', 'synthetic_fixture']


class CommandValidationError(ValueError):
    """Fixed safe failure; never includes submitted input or decoder exceptions."""
    code = 'corpus_publication.input_invalid'

    def __init__(self) -> None:
        super().__init__(self.code)


@dataclass(frozen=True, slots=True, repr=False)
class SourceScope:
    source_id: str
    kind: Literal['source'] = field(default='source', init=False)


@dataclass(frozen=True, slots=True, repr=False)
class PublicationInput:
    source_sha256: str
    catalogue_version: str
    versification_id: str
    tokenization_version: str


@dataclass(frozen=True, slots=True, repr=False)
class BeginPayload:
    input: PublicationInput
    expected_absent: Literal[True]


@dataclass(frozen=True, slots=True, repr=False)
class RecoverPayload:
    input: PublicationInput
    expected_generation: str
    expected_attempt_id: str


@dataclass(frozen=True, slots=True, repr=False)
class SealPayload:
    input: PublicationInput
    expected_generation: str
    expected_attempt_id: str


@dataclass(frozen=True, slots=True, repr=False)
class _Envelope:
    schema_version: Literal[1]
    operation_id: str
    scope: SourceScope
    reason_code: ReasonCode
    evidence_ref: str


@dataclass(frozen=True, slots=True, repr=False)
class BeginCommand(_Envelope):
    payload: BeginPayload
    command: Literal['corpus.begin'] = field(default='corpus.begin', init=False)


@dataclass(frozen=True, slots=True, repr=False)
class RecoverCommand(_Envelope):
    payload: RecoverPayload
    command: Literal['corpus.recover'] = field(default='corpus.recover', init=False)


@dataclass(frozen=True, slots=True, repr=False)
class SealCommand(_Envelope):
    payload: SealPayload
    command: Literal['corpus.seal'] = field(default='corpus.seal', init=False)


Command = BeginCommand | RecoverCommand | SealCommand


@dataclass(frozen=True, slots=True, repr=False)
class SourceCounts:
    books: int
    chapters: int
    verses: int
    tokens: int


@dataclass(frozen=True, slots=True, repr=False)
class PreparedCommand:
    command: Command
    counts: SourceCounts
    source_candidate_sha256: str


def _require(condition: bool) -> None:
    if not condition:
        raise CommandValidationError()


def _object(value: object, keys: set[str]) -> dict:
    _require(type(value) is dict and value.keys() == keys)
    return value


def _match(value: object, pattern: re.Pattern) -> str:
    _require(type(value) is str and pattern.fullmatch(value) is not None)
    return value


def _uuid(value: object) -> str:
    result = _match(value, _UUID)
    _require(result != '00000000-0000-0000-0000-000000000000')
    return result


def _generation(value: object) -> str:
    result = _match(value, _GENERATION)
    _require(int(result) <= 9223372036854775807)
    return result


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result)
        result[key] = value
    return result


def _reject_number(value: str) -> None:
    raise CommandValidationError()


def _integer(value: str) -> int:
    _require(len(value.lstrip('-')) <= 19)
    return int(value)


def _decode(raw: bytes) -> object:
    _require(type(raw) is bytes and len(raw) <= MAX_COMMAND_BYTES)
    failed = False
    try:
        text = raw.decode('utf-8', errors='strict')
        _require(not text.startswith('\ufeff'))
        result = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                            parse_float=_reject_number, parse_constant=_reject_number)
    except (ValueError, UnicodeError, RecursionError):
        failed = True
    # Raise outside the except block: decoder exceptions retain submitted bytes.
    if failed:
        raise CommandValidationError()
    return result


def parse_command(raw: bytes) -> Command:
    """Parse the closed v1 command into frozen records, without checking authority."""
    body = _object(_decode(raw), {'schema_version', 'operation_id', 'command', 'scope',
                                 'payload', 'reason_code', 'evidence_ref'})
    _require(type(body['schema_version']) is int and body['schema_version'] == 1)
    operation_id = _uuid(body['operation_id'])
    variant = body['command']
    _require(type(variant) is str and variant in ('corpus.begin', 'corpus.recover', 'corpus.seal'))
    reasons = {'corpus.begin': 'source_import', 'corpus.recover': 'source_recovery',
               'corpus.seal': 'source_seal'}
    reason = body['reason_code']
    _require(type(reason) is str and reason in (reasons[variant], 'synthetic_fixture'))
    evidence = _match(body['evidence_ref'], _EVIDENCE)
    scope = _object(body['scope'], {'kind', 'source_id'})
    _require(type(scope['kind']) is str and scope['kind'] == 'source')
    source_scope = SourceScope(_match(scope['source_id'], LABEL))
    keys = {'input', 'expected_absent'} if variant == 'corpus.begin' else {
        'input', 'expected_generation', 'expected_attempt_id'}
    payload = _object(body['payload'], keys)
    identity = _object(payload['input'], {'source_sha256', 'catalogue_version',
                                          'versification_id', 'tokenization_version'})
    source_input = PublicationInput(_match(identity['source_sha256'], SHA256),
                                   *(_match(identity[key], LABEL) for key in (
                                       'catalogue_version', 'versification_id', 'tokenization_version')))
    envelope = dict(schema_version=1, operation_id=operation_id, scope=source_scope,
                    reason_code=reason, evidence_ref=evidence)
    if variant == 'corpus.begin':
        _require(payload['expected_absent'] is True)
        return BeginCommand(**envelope, payload=BeginPayload(source_input, True))
    generation = _generation(payload['expected_generation'])
    attempt = _uuid(payload['expected_attempt_id'])
    if variant == 'corpus.recover':
        return RecoverCommand(**envelope, payload=RecoverPayload(source_input, generation, attempt))
    return SealCommand(**envelope, payload=SealPayload(source_input, generation, attempt))


def prepare_command(raw: bytes, source_raw: bytes) -> PreparedCommand:
    """Recompute complete source qualification; retain only command/counts/hash.

    Source failures preserve the existing safe source_evidence.* identifiers.
    No execution, database correspondence, audit seal or publication is established.
    """
    command = parse_command(raw)
    identity = command.payload.input
    candidate = build_source_candidate(
        source_raw, identity.source_sha256, source_id=command.scope.source_id,
        catalogue_version=identity.catalogue_version, versification_id=identity.versification_id,
        tokenization_version=identity.tokenization_version)
    return PreparedCommand(command, SourceCounts(**candidate['counts']),
                           hashlib.sha256(serialize_candidate(candidate)).hexdigest())
