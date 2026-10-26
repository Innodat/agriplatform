"""Immutable source/audit candidate assembly; confers no publication authority."""
from dataclasses import dataclass
from uuid import UUID

from corpus_evidence import EvidenceError, build_source_candidate
from highlight_evidence import DECIMAL_ID, MAX_ID


class ManifestError(ValueError):
    """Safe fixed diagnostic, without source content or input values."""


@dataclass(frozen=True)
class VerseCandidate:
    book: str
    chapter: int
    verse: int
    verse_token_digest: str
    observed_word_ids: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, 'observed_word_ids', tuple(self.observed_word_ids))


@dataclass(frozen=True)
class ManifestCandidate:
    source_id: str
    catalogue_version: str
    versification_id: str
    tokenization_version: str
    source_sha256: str
    source_revision: str
    executor_actor_id: str
    attempt_id: str
    generation: int
    verses: tuple[VerseCandidate, ...]

    def __post_init__(self):
        object.__setattr__(self, 'verses', tuple(self.verses))

    @property
    def publication(self):
        return False


def _require(condition):
    if not condition:
        raise ManifestError('corpus_manifest.invalid')


def _uuid(value):
    _require(isinstance(value, str))
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        raise ManifestError('corpus_manifest.invalid') from None
    _require(parsed.int != 0 and str(parsed) == value)


def build_manifest_candidate(raw, expected_source_sha256, *, source_id, catalogue_version,
                             versification_id, tokenization_version, source_revision,
                             executor_actor_id, attempt_id, generation, expected_attempt_id,
                             expected_generation, observed):
    """Bind a fully qualified source to complete externally observed IDs.

    Expected attempt/generation must come from the caller's protected observation,
    not a browser or historical audit receipt. This function cannot verify custody,
    actual database surfaces, authority, or current activation. Only a future protected
    fenced audit/transition may turn a candidate into a published manifest.
    """
    for value in (source_revision, executor_actor_id, attempt_id, expected_attempt_id):
        _uuid(value)
    _require(type(generation) is int and 1 <= generation <= MAX_ID
             and type(expected_generation) is int and generation == expected_generation
             and attempt_id == expected_attempt_id)
    labels = dict(source_id=source_id, catalogue_version=catalogue_version,
                  versification_id=versification_id, tokenization_version=tokenization_version)
    try:
        source = build_source_candidate(raw, expected_source_sha256, **labels)
    except EvidenceError:
        raise ManifestError('corpus_manifest.invalid') from None
    _require(type(observed) is dict and len(observed) == len(source['verses']))
    for coordinate in observed:
        _require(type(coordinate) is tuple and len(coordinate) == 3
                 and type(coordinate[0]) is str and type(coordinate[1]) is int
                 and type(coordinate[2]) is int)
    seen, verses = set(), []
    for verse in source['verses']:
        coordinate = (verse['book'], verse['chapter'], verse['verse'])
        identifiers = observed.get(coordinate)
        _require(isinstance(identifiers, (list, tuple))
                 and len(identifiers) == verse['token_count'])
        for identifier in identifiers:
            _require(isinstance(identifier, str) and DECIMAL_ID.fullmatch(identifier)
                     and int(identifier) <= MAX_ID and identifier not in seen)
            seen.add(identifier)
        verses.append(VerseCandidate(*coordinate, verse['verse_token_digest'], tuple(identifiers)))
    return ManifestCandidate(**labels, source_sha256=source['source_sha256'],
                             source_revision=source_revision, executor_actor_id=executor_actor_id,
                             attempt_id=attempt_id, generation=generation, verses=tuple(verses))
