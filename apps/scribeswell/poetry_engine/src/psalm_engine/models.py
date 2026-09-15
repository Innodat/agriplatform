"""Versioned evidence records. No inferred linguistic analysis is a source fact."""

from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def now() -> datetime:
    return datetime.now(UTC)


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Source(Record):
    id: str
    dataset: str
    revision: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    uri: str
    license: str
    attribution: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class Token(Record):
    id: str
    source_id: str
    verse: int = Field(ge=1)
    position: int = Field(ge=1)
    surface: str
    surface_status: Literal["present", "source_empty"] = "present"
    lemma: str | None = None
    morphology: str | None = None
    features: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def explicit_empty_source(self):
        if self.surface_status == "present" and not self.surface.strip():
            raise ValueError("Empty source surface must be explicitly recorded")
        if self.surface_status == "source_empty" and (self.source_id != "bhsa" or self.surface):
            raise ValueError("source_empty is reserved for actual empty BHSA source forms")
        return self


class Unit(Record):
    id: str
    source_id: str
    level: Literal["stanza", "strophe", "verse", "colon", "line", "clause", "phrase", "sentence"]
    token_ids: list[str] = Field(min_length=1)
    features: dict[str, Any] = Field(default_factory=dict)


class Evidence(Record):
    source_id: str
    locator: str = Field(min_length=1)
    token_ids: list[str] = Field(default_factory=list)
    page: int | None = Field(default=None, ge=1)
    note: str = ""


class Claim(Record):
    id: str
    category: str
    value: str = Field(min_length=1)
    scope: list[str] = Field(default_factory=list)
    applicable_psalms: list[Annotated[int, Field(ge=1, le=150)]] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence: list[Evidence] = Field(min_length=1)
    method: Literal["imported", "rule", "llm", "human"]
    reviewer_status: Literal["pending", "approved", "rejected", "disputed"] = "pending"
    reviewer: str | None = None
    reviewer_notes: str = ""
    revision: int = Field(default=1, ge=1)
    supersedes: str | None = None
    alternatives: list[str] = Field(default_factory=list)
    diagnostic_indicators: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def reviewed_by_person(self):
        if (self.reviewer_status != "pending" or self.method == "human") and not (
            self.reviewer and self.reviewer.strip()
        ):
            raise ValueError("A reviewed claim requires a named human reviewer")
        return self


class Alignment(Record):
    verse: int = Field(ge=1)
    left_ids: list[str]
    right_ids: list[str]
    status: Literal["consonantal_match", "unmatched"]
    method: str = "verse-local-contiguous-consonantal-v1"
    confidence: float = Field(ge=0, le=1)
    reviewer_status: Literal["pending", "approved", "disputed"] = "pending"
    note: str = ""


class TranslationBrief(Record):
    language: str = "af"
    audience: str = "adult readers; qualified translator review"
    desired_register: str = "natural contemporary Afrikaans"
    philosophy: str = (
        "preserve meaning, theological constraints, imagery and defensible poetic relationships"
    )
    required_features: list[str] = Field(
        default_factory=lambda: ["meaning", "imagery", "ambiguity"]
    )
    negotiable_features: list[str] = Field(default_factory=list)
    special_terms: dict[str, str] = Field(default_factory=dict)
    musical_constraints: dict[str, Any] | None = None
    instructions: str = ""


class CanonicalPsalmRepresentation(Record):
    schema_version: Literal["0.1.0"] = "0.1.0"
    representation_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=now)
    pipeline_version: str = "0.1.0"
    psalm: int = Field(ge=1, le=150)
    sources: list[Source] = Field(min_length=1)
    tokens: list[Token] = Field(min_length=1)
    units: list[Unit] = Field(default_factory=list)
    alignments: list[Alignment] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    principles: list[Claim] = Field(default_factory=list)
    brief: TranslationBrief = Field(default_factory=TranslationBrief)
    synthetic: bool = False
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def references_and_coverage(self):
        sources = {s.id for s in self.sources}
        tokens = {t.id: t for t in self.tokens}
        if len(sources) != len(self.sources) or len(tokens) != len(self.tokens):
            raise ValueError("Duplicate source/token identifiers")
        if any(t.source_id not in sources for t in self.tokens):
            raise ValueError("Token references an unknown source")
        positions = [(t.source_id, t.verse, t.position) for t in self.tokens]
        if len(positions) != len(set(positions)):
            raise ValueError("Duplicate source token positions")
        for unit in self.units:
            if unit.source_id not in sources or any(t not in tokens for t in unit.token_ids):
                raise ValueError("Unit references unknown source/token")
        for claim in self.claims + self.principles:
            if claim.applicable_psalms and self.psalm not in claim.applicable_psalms:
                raise ValueError("Claim is not applicable to this Psalm")
            if any(t not in tokens for t in claim.scope):
                raise ValueError("Claim scope references unknown token")
            for evidence in claim.evidence:
                if evidence.source_id not in sources or any(
                    t not in tokens or tokens[t].source_id != evidence.source_id
                    for t in evidence.token_ids
                ):
                    raise ValueError("Claim evidence references unknown source/token")
        covered = []
        for alignment in self.alignments:
            for source, ids in [("morphhb", alignment.left_ids), ("bhsa", alignment.right_ids)]:
                for tid in ids:
                    if (
                        tid not in tokens
                        or tokens[tid].source_id != source
                        or tokens[tid].verse != alignment.verse
                    ):
                        raise ValueError("Invalid alignment source/verse reference")
                    covered.append(tid)
            if alignment.status == "consonantal_match" and not (
                alignment.left_ids and alignment.right_ids
            ):
                raise ValueError("A matched alignment requires both sources")
            if alignment.status == "unmatched" and bool(alignment.left_ids) == bool(
                alignment.right_ids
            ):
                raise ValueError("Unmatched alignment must preserve tokens from exactly one source")
            if alignment.status == "consonantal_match":
                from .alignment import consonants

                left = consonants("".join(tokens[t].surface for t in alignment.left_ids))
                right = consonants("".join(tokens[t].surface for t in alignment.right_ids))
                if not left or left != right:
                    raise ValueError("Claimed consonantal alignment does not match source text")
        expected = {t.id for t in self.tokens if t.source_id in {"morphhb", "bhsa"}}
        if set(covered) != expected or len(covered) != len(expected):
            raise ValueError(
                "Every source token must occur exactly once in alignment, including unmatched tokens"
            )
        return self


Mode = Literal["literal", "poetic", "song-oriented-without-melody"]
Condition = Literal["A", "B", "C", "D"]


class GenerationRequest(Record):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    condition: Condition
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    language: str
    mode: Mode
    prompt_version: str = "0.1.0"
    system: str
    input: dict[str, Any]
    settings: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any]


class DecisionNote(Record):
    note: str
    evidence_refs: list[str] = Field(min_length=1)


class Candidate(Record):
    id: str
    lines: list[Annotated[str, Field(min_length=1, pattern=r"\S")]] = Field(min_length=1)
    notes: list[DecisionNote] = Field(default_factory=list)
    losses: list[str] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)


class GenerationResponse(Record):
    request_id: str
    provider: str
    model: str
    language: str
    mode: Mode
    candidates: list[Candidate] = Field(min_length=1)
    usage: dict[str, int] | None = None
    settings: dict[str, Any]
    synthetic: bool = False
