"""App-owned personal-notes v1 wire contract. Private routes are explicitly opt-in.

Runtime consumers must qualify Access, safe errors, transactions and release gates
in docs/PERSONAL_NOTES_V1.md before exposing this contract.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Literal, Union
from urllib.parse import urlsplit
from uuid import UUID

from typing_extensions import TypeAliasType
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, TypeAdapter, model_validator

try:
    from .passage_references import PassageReference
except ImportError:
    from passage_references import PassageReference

MAX_BODY_BYTES = 65536
MAX_NOTE_BODY_BYTES = 262144
MAX_PASSAGE_BODY_BYTES = 131072
MAX_SEARCH_BODY_BYTES = 4096
MAX_JSON_DEPTH = 16
MAX_JSON_NODES = 8192
MAX_NOTE_JSON_NODES = 32768
MAX_REVISION = '9223372036854775807'
MARK_SETS = ((), ('bold',), ('italic',), ('bold', 'italic'))


def _revision_pattern() -> str:
    # Shorter positive decimals, then each strictly smaller 19-digit prefix,
    # finally the maximum itself. Same constraint in the DTO and JSON Schema.
    branches = [r'[1-9][0-9]{0,17}']
    for index, digit in enumerate(MAX_REVISION):
        low, high = (1 if index == 0 else 0), int(digit) - 1
        if low <= high:
            branches.append(MAX_REVISION[:index] + f'[{low}-{high}]' + f'[0-9]{{{18-index}}}')
    return '^(?:' + '|'.join([*branches, MAX_REVISION]) + ')$'


def _control(char: str) -> bool:
    return ord(char) < 32 or 127 <= ord(char) <= 159


def _unicode(value: str) -> str:
    value.encode('utf-8', errors='strict')
    return value


def _uuid(value: str) -> str:
    parsed = UUID(value)
    if not parsed.int or str(parsed) != value:
        raise ValueError('invalid identifier')
    return value


def _revision(value: str) -> str:
    if int(value) > int(MAX_REVISION):
        raise ValueError('revision overflow')
    return value


def _utc(value: str) -> str:
    datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    return value


def _title(value: str) -> str:
    if not value.strip() or any(_control(c) for c in value):
        raise ValueError('invalid title')
    return _unicode(value)


def _url(value: str) -> str:
    _unicode(value)
    if len(value.encode('utf-8')) > 2048 or any(c.isspace() or _control(c) for c in value):
        raise ValueError('invalid URL')
    if '\\' in value or re.search(r'%(?![0-9a-fA-F]{2})|%(?:0[0-9a-f]|1[0-9a-f]|7f|5c)', value, re.I):
        raise ValueError('invalid URL')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError('invalid URL')
    # Bracketed IPv6 is checked by urlsplit; DNS names must contain safe IDNA labels.
    host = parsed.hostname
    if ':' in host:
        if '%' in host:
            raise ValueError('invalid URL')
        IPv6Address(host)
    else:
        ascii_host = host.encode('idna').decode('ascii')
        if len(ascii_host) > 253 or any(not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
                                       for label in ascii_host.rstrip('.').split('.')):
            raise ValueError('invalid URL')
        last = ascii_host.rstrip('.').split('.')[-1]
        if last.isdigit() or re.fullmatch(r'0[xX][0-9a-fA-F]*', last):
            if str(IPv4Address(ascii_host)) != ascii_host:
                raise ValueError('invalid URL')
    if parsed.port is not None and not 1 <= parsed.port <= 65535:
        raise ValueError('invalid URL')
    return value


Identifier = Annotated[str, Field(min_length=36, max_length=36, pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    json_schema_extra={'not': {'const': '00000000-0000-0000-0000-000000000000'}}), AfterValidator(_uuid)]
Revision = Annotated[str, Field(pattern=_revision_pattern(), json_schema_extra={'not': {'pattern': r'[^0-9]'}}), AfterValidator(_revision)]
UtcTimestamp = Annotated[str, Field(min_length=27, max_length=27,
    pattern=r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$',
    description='Server UTC timestamp; calendar validity and attribution chronology require semantic validation.'), AfterValidator(_utc)]
Title = Annotated[str, Field(min_length=1, max_length=200, pattern=r'^[^\x00-\x1f\x7f-\x9f]+$',
    description='Nonblank scalar Unicode title, no Unicode Cc controls; whitespace is preserved.',
    json_schema_extra={'allOf': [{'type': 'string', 'pattern': r'\S'}], 'not': {'pattern': r'[\x00-\x1f\x7f-\x9f]'}}), AfterValidator(_title)]
ExternalUrl = Annotated[str, Field(min_length=1, max_length=2048,
    pattern=r'^[hH][tT][tT][pP][sS]?://[^/?#@\s\\\x00-\x1f\x7f-\x9f]+(?:[/?#][^\s\\\x00-\x1f\x7f-\x9f]*)?$',
    description='Absolute HTTP(S), no credentials/whitespace/Unicode Cc controls/backslash. '
                'Semantic validation also requires valid IDNA DNS or canonical IPv4/unscoped IPv6, '
                'port 1–65535, safe percent escapes, scalar Unicode and at most 2048 UTF-8 bytes.',
    json_schema_extra={'not': {'pattern': r'[\s\\\x00-\x1f\x7f-\x9f]'}}), AfterValidator(_url)]
Command = Literal['study.create', 'study.rename', 'study.passages.replace', 'study.delete', 'note.create', 'note.replace', 'note.delete']


class Closed(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, validate_default=True, hide_input_in_errors=True)

    def __repr__(self) -> str:
        return f'<{type(self).__name__}>'

    def __str__(self) -> str:
        return self.__repr__()


class TextInline(Closed):
    type: Literal['text']
    text: Annotated[str, Field(min_length=1, max_length=4096), AfterValidator(_unicode)]
    marks: tuple[Literal['bold', 'italic'], ...] = Field(max_length=2,
        json_schema_extra={'enum': [list(marks) for marks in MARK_SETS]})

    @model_validator(mode='after')
    def canonical_marks(self):
        if self.marks not in MARK_SETS:
            raise ValueError('invalid marks')
        return self


class ExternalLink(Closed):
    type: Literal['external_link']
    url: ExternalUrl
    content: tuple[TextInline, ...] = Field(min_length=1, max_length=64)


Inline = Annotated[Union[TextInline, ExternalLink], Field(discriminator='type')]


class Paragraph(Closed):
    type: Literal['paragraph']
    direction: Literal['auto', 'ltr', 'rtl']
    content: tuple[Inline, ...] = Field(max_length=256)


class ListBlock(Closed):
    type: Literal['list']
    style: Literal['bullet', 'ordered']
    items: tuple[Annotated[tuple[Paragraph, ...], Field(min_length=1, max_length=16)], ...] = Field(min_length=1, max_length=128)


Block = Annotated[Union[Paragraph, ListBlock], Field(discriminator='type')]


class DocumentV1(Closed):
    version: Annotated[int, Field(ge=1, le=1)]
    blocks: tuple[Block, ...] = Field(max_length=256)

    @model_validator(mode='after')
    def document_budget(self):
        pending = [self]
        nodes = text_size = 0
        while pending:
            value = pending.pop()
            if isinstance(value, BaseModel):
                nodes += 1
                if isinstance(value, TextInline):
                    text_size += len(value.text)
                elif isinstance(value, PassageLink):
                    text_size += len(value.label)
                pending.extend(value.__dict__.values())
            elif isinstance(value, tuple):
                pending.extend(value)
        if nodes > 2048 or text_size > 50000:
            raise ValueError('document budget exceeded')
        return self


class PassageLink(Closed):
    type: Literal['passage_link']
    reference: PassageReference
    label: Annotated[str, Field(min_length=1, max_length=200), AfterValidator(_unicode)]


InlineV2 = Annotated[Union[TextInline, ExternalLink, PassageLink], Field(discriminator='type')]


class ParagraphV2(Closed):
    type: Literal['paragraph']
    direction: Literal['auto', 'ltr', 'rtl']
    content: tuple[InlineV2, ...] = Field(max_length=256)


class ListBlockV2(Closed):
    type: Literal['list']
    style: Literal['bullet', 'ordered']
    items: tuple[Annotated[tuple[ParagraphV2, ...], Field(min_length=1, max_length=16)], ...] = Field(min_length=1, max_length=128)


BlockV2 = Annotated[Union[ParagraphV2, ListBlockV2], Field(discriminator='type')]


class DocumentV2(DocumentV1):
    version: Annotated[int, Field(ge=2, le=2)]
    blocks: tuple[BlockV2, ...] = Field(max_length=256)


class LegacyNoteValue(Closed):
    document: DocumentV1 | DocumentV2
    connections: tuple[()]
    highlights: tuple[()]


Label = Annotated[str, Field(min_length=1, max_length=64, pattern=r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$')]
Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]


class AnchorSegment(Closed):
    reference: PassageReference
    start_position: Annotated[int, Field(ge=1, le=512)]
    end_position: Annotated[int, Field(ge=1, le=512)]
    observed_word_ids: tuple[Revision, ...] = Field(min_length=1, max_length=512)
    verse_token_digest: Digest

    @model_validator(mode='after')
    def exact_segment(self):
        target = self.reference.target
        if target.kind != 'verse_range' or target.start != target.end or self.reference.versification_id != 'oshb-hebrew-json-c2d8e9e5':
            raise ValueError('single supported verse required')
        if self.end_position < self.start_position or len(self.observed_word_ids) != self.end_position-self.start_position+1 or len(set(self.observed_word_ids)) != len(self.observed_word_ids):
            raise ValueError('invalid selected positions')
        return self


class HighlightAnchor(Closed):
    version: Annotated[int, Field(ge=1, le=1, json_schema_extra={'const':1})]
    source_id: Label
    source_revision: Identifier
    catalogue_version: Label
    versification_id: Label
    tokenization_version: Label
    segments: tuple[AnchorSegment, ...] = Field(min_length=1, max_length=128)

    @model_validator(mode='after')
    def continuous(self):
        try:
            from .passage_references import BOOKS
        except ImportError:
            from passage_references import BOOKS
        previous = None
        book = self.segments[0].reference.book_id
        for segment in self.segments:
            ref = segment.reference
            if ref.book_id != book or ref.catalogue_version != self.catalogue_version or ref.versification_id != self.versification_id:
                raise ValueError('anchor identity mismatch')
            point = ref.target.start
            if previous:
                prior = previous.reference.target.start
                counts = BOOKS[book]['chapter_verse_counts']
                expected = (prior.chapter, prior.verse+1) if prior.verse < counts[prior.chapter-1] else (prior.chapter+1, 1)
                if (point.chapter,point.verse) != expected or segment.start_position != 1:
                    raise ValueError('discontinuous anchor')
            previous = segment
        ids = [identifier for segment in self.segments for identifier in segment.observed_word_ids]
        if len(set(ids)) != len(ids):
            raise ValueError('duplicate anchor IDs')
        return self


class NoteConnection(Closed):
    id: Identifier
    reference: PassageReference


class NoteHighlight(Closed):
    id: Identifier
    colour: Annotated[str, Field(pattern=r'^#[0-9A-F]{6}$')]
    anchor: HighlightAnchor


class AggregateNoteValue(Closed):
    format_version: Annotated[int, Field(ge=3, le=3, json_schema_extra={'const':3})]
    document: DocumentV1 | DocumentV2
    connections: tuple[NoteConnection, ...] = Field(max_length=128)
    highlights: tuple[NoteHighlight, ...] = Field(max_length=64)

    @model_validator(mode='after')
    def aggregate_budget(self):
        for items in (self.connections,self.highlights):
            if len({item.id for item in items}) != len(items):
                raise ValueError('duplicate identity')
        segments = [segment for highlight in self.highlights for segment in highlight.anchor.segments]
        if len(segments)>128 or sum(len(segment.observed_word_ids) for segment in segments)>4096:
            raise ValueError('aggregate budget exceeded')
        if len(json.dumps(self.model_dump(mode='json'),ensure_ascii=False,separators=(',',':')).encode())>MAX_NOTE_BODY_BYTES:
            raise ValueError('aggregate budget exceeded')
        return self


NoteValue = TypeAliasType('NoteValue', LegacyNoteValue | AggregateNoteValue)


class EnrollStudies(Closed):
    operation_id: Identifier


class EnrollmentResult(Closed):
    disposition: Literal['created', 'unchanged']
    account_id: Identifier
    actor_id: Identifier
    permission: Literal['scribeswell.studies.use']


class EnrollmentAck(Closed):
    operation_id: Identifier
    status: Literal['committed']
    result: EnrollmentResult


class CreateStudy(Closed):
    operation_id: Identifier
    title: Title | None  # required null requests atomic default allocation


class RenameStudy(Closed):
    operation_id: Identifier
    expected_revision: Revision
    title: Title


class CreateNote(Closed):
    operation_id: Identifier
    value: NoteValue


class ReplaceNote(Closed):
    operation_id: Identifier
    expected_revision: Revision
    value: NoteValue


class DeleteNote(Closed):
    operation_id: Identifier
    expected_revision: Revision


class DeleteStudy(Closed):
    operation_id: Identifier
    expected_revision: Revision


class PassageItem(Closed):
    id: Identifier
    reference: PassageReference


class ReplacePassages(Closed):
    operation_id: Identifier
    expected_revision: Revision
    items: tuple[PassageItem, ...] = Field(max_length=200)

    @model_validator(mode='after')
    def unique_entries(self):
        ids = [item.id for item in self.items]
        references = [json.dumps(item.reference.model_dump(mode='json'), sort_keys=True) for item in self.items]
        if len(set(ids)) != len(ids) or len(set(references)) != len(references):
            raise ValueError('duplicate passage')
        return self


class PassageList(Closed):
    study_id: Identifier
    revision: Revision
    items: tuple[PassageItem, ...] = Field(max_length=200)


class Attribution(Closed):
    created_at: UtcTimestamp
    updated_at: UtcTimestamp
    created_by_actor_id: Identifier
    updated_by_actor_id: Identifier

    @model_validator(mode='after')
    def chronological(self):
        if self.updated_at < self.created_at:
            raise ValueError('invalid attribution order')
        return self


class StudyView(Attribution):
    id: Identifier
    owner_account_id: Identifier
    title: Title
    revision: Revision


class NoteView(Attribution):
    id: Identifier
    study_id: Identifier
    owner_account_id: Identifier
    visibility: Literal['study']
    revision: Revision
    value: NoteValue


Cursor = Annotated[str, Field(min_length=1, max_length=512, pattern=r'^[A-Za-z0-9_-]+$',
    json_schema_extra={'not': {'pattern': r'[^A-Za-z0-9_-]'}})]


def _search_unicode(value: str) -> str:
    _unicode(value)
    if "\x00" in value: raise ValueError("invalid query")
    return value


class SearchStudies(Closed):
    query: Annotated[str, Field(max_length=200,
        description='Unicode scalar string without NUL; at most 200 codepoints before outer trim/NFC matching.',
        json_schema_extra={'not': {'pattern': r'\u0000'}}), AfterValidator(_search_unicode)]
    limit: Annotated[int, Field(ge=1, le=50)] = 20
    cursor: Cursor | None = None


class StudyPage(Closed):
    items: tuple[StudyView, ...] = Field(max_length=50)
    next_cursor: Cursor | None


class NotePage(Closed):
    items: tuple[NoteView, ...] = Field(max_length=50)
    next_cursor: Cursor | None


class OperationAck(Closed):
    model_config = ConfigDict(json_schema_extra={'oneOf': [
        {'properties': {'command': {'enum': ['study.create', 'study.rename', 'study.passages.replace', 'study.delete']}, 'note_id': {'type': 'null'}}},
        {'properties': {'command': {'enum': ['note.create', 'note.replace', 'note.delete']}, 'note_id': {'type': 'string'}}},
    ]})
    operation_id: Identifier
    command: Command
    study_id: Identifier
    note_id: Identifier | None
    revision: Revision

    @model_validator(mode='after')
    def resource_shape(self):
        if (self.command in ('study.create', 'study.rename', 'study.passages.replace', 'study.delete')) != (self.note_id is None):
            raise ValueError('invalid outcome resources')
        return self


class Committed(Closed):
    status: Literal['committed']
    outcome: OperationAck


class Unresolved(Closed):
    status: Literal['unresolved']


Outcome = Annotated[Union[Committed, Unresolved], Field(discriminator='status')]
OUTCOME_ADAPTER = TypeAdapter(Outcome)


class Problem(Closed):
    error: Literal['Request could not be completed']
    code: Literal['scribeswell_personal_notes_input_invalid', 'authentication_required',
                  'studies_access_denied', 'studies_access_unavailable', 'studies_storage_unavailable', 'resource_unavailable',
                  'operation_payload_mismatch', 'operation_unresolved', 'highlight_proof_invalid', 'highlight_proof_unavailable', 'note_format_unsupported', 'request_deadline_exceeded']
    details: None


class RevisionDetails(Closed):
    expected_revision: Revision
    current_revision: Revision


class RevisionProblem(Closed):
    error: Literal['Request could not be completed']
    code: Literal['note_revision_conflict', 'study_revision_conflict', 'passage_revision_conflict']
    details: RevisionDetails


ErrorResponse = Annotated[Union[Problem, RevisionProblem], Field(discriminator='code')]
COMMAND_MODELS = {'studies.search': SearchStudies, 'study.passages.replace': ReplacePassages, 'studies.enroll': EnrollStudies, 'study.create': CreateStudy, 'study.rename': RenameStudy, 'note.create': CreateNote, 'note.replace': ReplaceNote, 'note.delete': DeleteNote, 'study.delete': DeleteStudy}


class ContractInputError(ValueError):
    """Fixed safe error; original input and decoder errors never attached."""


def _reject_float(_):
    raise ValueError('numbers must be integers')


def _unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate key')
        value[key] = item
    return value


def parse_command(command: str, raw: bytes) -> SearchStudies | CreateStudy | RenameStudy | ReplacePassages | CreateNote | ReplaceNote | DeleteNote | DeleteStudy:
    """Strict bounded HTTP body decoder. No access, database or network work."""
    result = None
    try:
        if type(raw) is not bytes or not raw or len(raw) > (MAX_SEARCH_BODY_BYTES if command == 'studies.search' else MAX_PASSAGE_BODY_BYTES if command == 'study.passages.replace' else MAX_NOTE_BODY_BYTES if command in ('note.create','note.replace') else MAX_BODY_BYTES) or raw.startswith(b'\xef\xbb\xbf'):
            raise ValueError('invalid framing')
        tree = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_float=_reject_float, parse_constant=_reject_float)
        if not isinstance(tree, dict):
            raise ValueError('invalid root')
        pending = [(tree, 1)]
        nodes = 0
        while pending:
            value, depth = pending.pop()
            nodes += 1
            if nodes > (MAX_NOTE_JSON_NODES if command in ('note.create','note.replace') else MAX_JSON_NODES) or depth > MAX_JSON_DEPTH:
                raise ValueError('JSON budget exceeded')
            if isinstance(value, dict):
                for key in value:
                    _unicode(key)
                pending.extend((v, depth + 1) for v in value.values())
            elif isinstance(value, list):
                pending.extend((v, depth + 1) for v in value)
            elif isinstance(value, str):
                _unicode(value)
        result = COMMAND_MODELS[command].model_validate_json(raw)
    except (ValueError, TypeError, KeyError, RecursionError, OverflowError):
        pass
    if result is None:
        raise ContractInputError('scribeswell_personal_notes_input_invalid') from None
    return result


def openapi_contract() -> dict:
    """Generate planned OpenAPI from the DTO definitions, never from fake routes."""
    models = (SearchStudies, EnrollStudies, EnrollmentAck, CreateStudy, RenameStudy, ReplacePassages, PassageList, CreateNote, ReplaceNote, DeleteNote, DeleteStudy, StudyView, NoteView, StudyPage,
              NotePage, OperationAck, Outcome, ErrorResponse)
    schemas = {}
    for model in models:
        schema = TypeAdapter(model).json_schema(ref_template='#/components/schemas/{model}')
        schemas.update(schema.pop('$defs', {}))
        if isinstance(model, type) and issubclass(model, BaseModel):
            schemas[model.__name__] = schema
        else:
            schemas['Outcome' if model is Outcome else 'ErrorResponse'] = schema

    def ref(name):
        return {'$ref': f'#/components/schemas/{name}'}

    def operation(name, response, *, body=None, parameters=()):
        entry = {'operationId': name, 'security': [{'accountSession': []}],
                 'parameters': list(parameters), 'responses': {}}
        codes = {'400': ['scribeswell_personal_notes_input_invalid'], '401': ['authentication_required'],
                 '403': ['studies_access_denied'], '404': ['resource_unavailable'],
                 '409': ['note_revision_conflict', 'study_revision_conflict', 'passage_revision_conflict', 'note_format_unsupported', 'highlight_proof_invalid', 'operation_payload_mismatch', 'operation_unresolved'],
                 '503': ['studies_access_unavailable', 'studies_storage_unavailable', 'highlight_proof_unavailable', 'request_deadline_exceeded']}
        for status, description, schema in [('200', 'Acknowledged or current authorized result', response),
                                           ('400', 'Invalid input', 'ErrorResponse'),
                                           ('401', 'Authentication required', 'ErrorResponse'),
                                           ('403', 'Current Studies access denied', 'ErrorResponse'),
                                           ('404', 'Unavailable resource; does not reveal another owner', 'ErrorResponse'),
                                           ('409', 'Revision, operation payload or unresolved conflict', 'ErrorResponse'),
                                           ('503', 'Access, storage or deadline unavailable', 'ErrorResponse')]:
            response_schema = ref(schema)
            if status in codes:
                response_schema = {'allOf': [response_schema, {'properties': {'code': {'enum': codes[status]}}}]}
            entry['responses'][status] = {'description': description, 'headers': {
                'Cache-Control': {'schema': {'type': 'string', 'const': 'private, no-store'}}},
                'content': {'application/json': {'schema': response_schema}}}
        if body:
            entry['requestBody'] = {'required': True, 'content': {'application/json': {'schema': ref(body)}}}
        return entry

    def path_id(name):
        return {'name': name, 'in': 'path', 'required': True,
                'schema': TypeAdapter(Identifier).json_schema()}

    page = ({'name': 'limit', 'in': 'query', 'schema': {'type': 'integer', 'minimum': 1, 'maximum': 50, 'default': 20}},
            {'name': 'cursor', 'in': 'query', 'schema': TypeAdapter(Cursor).json_schema()})
    study, note, op = path_id('study_id'), path_id('note_id'), path_id('operation_id')
    return {'openapi': '3.1.0', 'info': {'title': 'Scribeswell personal notes — v1', 'version': '1.0.0'},
            'x-generated-file-warning': 'Generated by tools/py/export_personal_notes_contract.py; do not edit.',
            'x-runtime-status': 'opt-in-development-production-disabled',
            'x-command-input-limits': {'bytes': MAX_BODY_BYTES, 'note_bytes': MAX_NOTE_BODY_BYTES, 'note_json_nodes': MAX_NOTE_JSON_NODES, 'passage_collection_bytes': MAX_PASSAGE_BODY_BYTES, 'search_bytes': MAX_SEARCH_BODY_BYTES, 'json_depth': MAX_JSON_DEPTH,
                                       'json_nodes': MAX_JSON_NODES, 'document_nodes': 2048, 'text_codepoints': 50000,
                                       'url_utf8_bytes': 2048, 'revision_max': MAX_REVISION,
                                       'duplicate_keys': 'rejected', 'marks_order': ['bold', 'italic']},
            'x-normative-contract': '../docs/PERSONAL_NOTES_V1.md',
            'paths': {
                '/api/studies/search': {'post': operation('searchStudies', 'StudyPage', body='SearchStudies')},
                '/api/studies/enrollment': {'post': operation('enrollStudies', 'EnrollmentAck', body='EnrollStudies')},
                '/api/studies': {'post': operation('createStudy', 'OperationAck', body='CreateStudy'),
                                 'get': operation('listStudies', 'StudyPage', parameters=page)},
                '/api/studies/{study_id}': {'delete': operation('deleteStudy', 'OperationAck', body='DeleteStudy', parameters=(study,)), 'get': operation('readStudy', 'StudyView', parameters=(study,))},
                '/api/studies/{study_id}/passages': {'get': operation('readPassages', 'PassageList', parameters=(study,)), 'put': operation('replacePassages', 'OperationAck', body='ReplacePassages', parameters=(study,))},
                '/api/studies/{study_id}/title': {'put': operation('renameStudy', 'OperationAck', body='RenameStudy', parameters=(study,))},
                '/api/studies/{study_id}/notes': {'post': operation('createNote', 'OperationAck', body='CreateNote', parameters=(study,)),
                                                'get': operation('listNotes', 'NotePage', parameters=(study, *page))},
                '/api/studies/{study_id}/notes/{note_id}': {
                    'delete': operation('deleteNote', 'OperationAck', body='DeleteNote', parameters=(study, note)),
                    'get': operation('readNote', 'NoteView', parameters=(study, note)),
                    'put': operation('replaceNote', 'OperationAck', body='ReplaceNote', parameters=(study, note))},
                '/api/operations/{operation_id}': {'get': operation('lookupOperation', 'Outcome', parameters=(op,
                    {'name': 'command', 'in': 'query', 'required': True, 'schema': TypeAdapter(Command).json_schema()}))}},
            'components': {'schemas': schemas, 'securitySchemes': {'accountSession': {
                'type': 'http', 'scheme': 'bearer', 'description': 'Browser account session; current Access check required separately.'}}}}
