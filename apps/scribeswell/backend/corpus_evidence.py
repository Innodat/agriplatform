"""Reproducible source-artifact candidates, without database or publication authority."""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import json
import re

from corpus_source import BOOK_METADATA, NAME_EN_TO_META, decode_word

MAX_SOURCE_BYTES = 32 * 1024 * 1024
LABEL = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,63}', re.ASCII)
SHA256 = re.compile(r'[0-9a-f]{64}', re.ASCII)


class EvidenceError(ValueError):
    """A safe diagnostic identifier, never source text or arbitrary exception content."""
    def __init__(self, code):
        self.code = 'source_evidence.' + code
        super().__init__(self.code)


def _label(value):
    if not isinstance(value, str) or LABEL.fullmatch(value) is None:
        raise EvidenceError('identity_invalid')
    return value


def _integer(value, maximum):
    if type(value) is not int or not 1 <= value <= maximum:
        raise EvidenceError('position_invalid')


def _text(value, maximum=None):
    if not isinstance(value, str) or not value:
        raise EvidenceError('text_invalid')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError:
        raise EvidenceError('unicode_invalid') from None
    if maximum is not None and size > maximum:
        raise EvidenceError('surface_too_large')


def encode_verse_tokens(source_id, catalogue_version, versification_id,
                        tokenization_version, book, chapter, verse, tokens):
    """Encode explicit contiguous (position, exact surface) pairs as verse_tokens.v1.

    Validates representation and qualification bounds, not a reference catalogue.
    """
    labels = [_label(v) for v in (source_id, catalogue_version, versification_id,
                                  tokenization_version, book)]
    _integer(chapter, 150)
    _integer(verse, 176)
    if not isinstance(tokens, (list, tuple)) or not 1 <= len(tokens) <= 512:
        raise EvidenceError('tokens_invalid')
    checked = []
    for expected, token in enumerate(tokens, 1):
        if not isinstance(token, (list, tuple)) or len(token) != 2:
            raise EvidenceError('tokens_invalid')
        position, surface = token
        _integer(position, 512)
        if position != expected:
            raise EvidenceError('position_invalid')
        _text(surface, 2048)
        checked.append([position, surface])
    return json.dumps(['scribeswell.verse_tokens.v1', *labels, chapter, verse, checked],
                      ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def verse_token_digest(*args, **kwargs):
    return hashlib.sha256(encode_verse_tokens(*args, **kwargs)).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError('duplicate_json_key')
        result[key] = value
    return result


# Private worker execution scope: one exact pure source observation, never DB proof.
_QUALIFIED_SOURCE = ContextVar('scribeswell_qualified_source',default=None)


@contextmanager
def _qualified_source_execution():
    token=_QUALIFIED_SOURCE.set({})
    try:yield
    finally:_QUALIFIED_SOURCE.reset(token)


def build_source_candidate(raw, expected_source_sha256, *, source_id, catalogue_version,
                           versification_id, tokenization_version):
    """Qualify exact source bytes; worker-only reuse never caches database proof."""
    labels=dict(source_id=source_id,catalogue_version=catalogue_version,
                versification_id=versification_id,tokenization_version=tokenization_version)
    scope=_QUALIFIED_SOURCE.get()
    # Exact immutable bytes, expected checksum and every identity label must agree.
    # Invalid types still execute the original validator and safe error mapping.
    cacheable=(scope is not None and type(raw) is bytes and len(raw)<=MAX_SOURCE_BYTES
               and type(expected_source_sha256) is str and all(type(v) is str for v in labels.values()))
    key=(raw,expected_source_sha256,*labels.values()) if cacheable else None
    entry=scope.get('entry') if cacheable else None
    if entry is not None and entry[0]==key:
        return deepcopy(entry[1])
    result=_build_source_candidate(raw,expected_source_sha256,**labels)
    if cacheable:scope['entry']=(key,deepcopy(result))
    return result


def _build_source_candidate(raw, expected_source_sha256, *, source_id, catalogue_version,
                           versification_id, tokenization_version):
    """Qualify exactly these bytes and return a deterministic source-only inventory."""
    labels = dict(source_id=source_id, catalogue_version=catalogue_version,
                  versification_id=versification_id, tokenization_version=tokenization_version)
    for value in labels.values():
        _label(value)
    if not isinstance(expected_source_sha256, str) or not SHA256.fullmatch(expected_source_sha256):
        raise EvidenceError('checksum_invalid')
    if not isinstance(raw, bytes) or len(raw) > MAX_SOURCE_BYTES:
        raise EvidenceError('source_too_large')
    checksum = hashlib.sha256(raw).hexdigest()
    if checksum != expected_source_sha256:
        raise EvidenceError('checksum_mismatch')
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError('json_invalid')))
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError('json_invalid') from None
    if not isinstance(data, dict) or set(data) != set(NAME_EN_TO_META):
        raise EvidenceError('source_inventory_invalid')
    # Cache only deterministic decoding within this one qualification call. Every
    # occurrence still passes field bounds, position and exact verse digest checks.
    # The fixed-size cache retains no source across operations or returned values.
    from functools import lru_cache
    @lru_cache(maxsize=4096)
    def decoded_surface(fields):
        return decode_word(list(fields), 'source')[0]['surface_he']
    counts = dict(books=len(BOOK_METADATA), chapters=0, verses=0, tokens=0)
    inventory = []
    for meta in BOOK_METADATA:
        chapters = data[meta['name_en']]
        if not isinstance(chapters, list) or not 1 <= len(chapters) <= 150:
            raise EvidenceError('source_structure_invalid')
        counts['chapters'] += len(chapters)
        for chapter, verses in enumerate(chapters, 1):
            if not isinstance(verses, list) or not 1 <= len(verses) <= 176:
                raise EvidenceError('source_structure_invalid')
            counts['verses'] += len(verses)
            for verse, words in enumerate(verses, 1):
                if not isinstance(words, list) or not 1 <= len(words) <= 512:
                    raise EvidenceError('tokens_invalid')
                tokens = []
                for position, word in enumerate(words, 1):
                    if not isinstance(word, list) or len(word) != 3:
                        raise EvidenceError('source_word_invalid')
                    for field in word:
                        _text(field, 2048)
                    try:
                        surface = decoded_surface(tuple(word))
                    except ValueError:
                        raise EvidenceError('source_word_invalid') from None
                    tokens.append([position, surface])
                digest = verse_token_digest(**labels, book=meta['osis_id'], chapter=chapter,
                                            verse=verse, tokens=tokens)
                counts['tokens'] += len(tokens)
                inventory.append(dict(book=meta['osis_id'], chapter=chapter, verse=verse,
                                      token_count=len(tokens), verse_token_digest=digest))
    return dict(kind='scribeswell.source_evidence_candidate', version=1, publication=False,
                **labels, source_sha256=checksum, counts=counts, verses=inventory)


def serialize_candidate(candidate):
    return (json.dumps(candidate, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')
