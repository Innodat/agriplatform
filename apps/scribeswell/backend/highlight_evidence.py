"""Pure exact-token comparison; callers own publication/snapshot authority.

A ready result means internally coherent supplied data, never independently verified
current publication. No caller should accept new anchors using this module alone.
"""
from uuid import UUID
import re

from corpus_evidence import LABEL, SHA256, EvidenceError, verse_token_digest
from corpus_source import BOOK_METADATA

IDENTITY = ('source_id', 'catalogue_version', 'versification_id', 'tokenization_version')
COORDINATE = ('book', 'chapter', 'verse')
BOOKS = frozenset(book['osis_id'] for book in BOOK_METADATA)
DECIMAL_ID = re.compile(r'[1-9][0-9]{0,18}', re.ASCII)
MAX_ID = 2 ** 63 - 1


class HighlightEvidenceError(ValueError):
    """Fixed safe identifier; contains no source text or user content."""


def _require(condition):
    if not condition:
        raise HighlightEvidenceError('highlight_evidence.segment_invalid')


def _position(value, maximum):
    return type(value) is int and 1 <= value <= maximum


def _ids(values, count):
    return (isinstance(values, list) and len(values) == count
            and all(isinstance(value, str) and DECIMAL_ID.fullmatch(value)
                    and int(value) <= MAX_ID for value in values)
            and len(set(values)) == count)


def _identity(value):
    _require(isinstance(value, dict))
    for key in IDENTITY:
        item = value.get(key)
        _require(isinstance(item, str) and LABEL.fullmatch(item) is not None)
    _require(isinstance(value.get('book'), str) and value['book'] in BOOKS)
    _require(_position(value.get('chapter'), 150) and _position(value.get('verse'), 176))
    revision = value.get('source_revision')
    _require(isinstance(revision, str))
    try:
        parsed = UUID(revision)
    except (ValueError, AttributeError):
        raise HighlightEvidenceError('highlight_evidence.segment_invalid') from None
    _require(parsed.int != 0 and str(parsed) == revision)
    digest = value.get('verse_token_digest')
    _require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None)


def observe_verse(publication, words):
    """Check complete ordered words against a trusted snapshot observation.

    The adapter must supply publication and words from one bounded repeatable read.
    Invalid or unavailable observations fail closed without breaking public reading.
    """
    unavailable = {'version': 1, 'status': 'unavailable'}
    try:
        _identity(publication)
        _require(type(publication.get('version')) is int and publication['version'] == 1
                 and publication.get('status') == 'ready')
        _require(isinstance(words, list) and 1 <= len(words) <= 512)
        tokens, identifiers = [], []
        for position, word in enumerate(words, 1):
            _require(isinstance(word, dict) and type(word.get('position')) is int
                     and word['position'] == position)
            tokens.append([position, word.get('surface_he')])
            identifiers.append(word.get('id'))
        _require(_ids(identifiers, len(words)))
        _require(_ids(publication.get('observed_word_ids'), len(words)))
        _require(identifiers == publication['observed_word_ids'])
        digest = verse_token_digest(*(publication[key] for key in IDENTITY),
                                    *(publication[key] for key in COORDINATE), tokens)
        _require(digest == publication['verse_token_digest'])
    except (HighlightEvidenceError, EvidenceError):
        return unavailable
    return dict(version=1, status='ready',
                **{key: publication[key] for key in (*IDENTITY, *COORDINATE,
                                                     'source_revision', 'verse_token_digest')},
                observed_word_ids=list(identifiers), token_count=len(words))


def segment_status(segment, evidence):
    """Classify a structurally valid saved segment without rewriting it.

    Evidence must be the result of observe_verse for a trusted current snapshot.
    Saved IDs/revisions are retained provenance, not cross-revision text identity.
    """
    _identity(segment)
    start, end = segment.get('start_position'), segment.get('end_position')
    _require(_position(start, 512) and _position(end, 512) and start <= end)
    _require(_ids(segment.get('observed_word_ids'), end - start + 1))
    if not isinstance(evidence, dict) or evidence.get('status') != 'ready':
        return 'unavailable'
    try:
        _identity(evidence)
        _require(type(evidence.get('version')) is int and evidence['version'] == 1)
        count = evidence.get('token_count')
        _require(_position(count, 512) and _ids(evidence.get('observed_word_ids'), count))
    except HighlightEvidenceError:
        return 'unavailable'
    if (any(segment[key] != evidence[key] for key in (*IDENTITY, *COORDINATE,
                                                    'verse_token_digest'))
            or end > count):
        return 'needs_review'
    return 'valid'
