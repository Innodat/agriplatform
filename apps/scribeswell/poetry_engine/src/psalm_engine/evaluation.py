"""Human rubric: preserve all dimensions; never substitute automated quality claims."""

from typing import Literal

from pydantic import Field, model_validator

from .models import Record

CATEGORIES = [
    "source_meaning_fidelity",
    "theological_fidelity",
    "lexical_accuracy",
    "handling_of_ambiguity",
    "imagery",
    "parallelism",
    "discourse_progression",
    "natural_afrikaans",
    "poetic_quality",
    "song_adaptation_suitability",
    "decision_transparency",
    "revision_ease",
]


class Evaluation(Record):
    request_id: str
    candidate_id: str
    reviewer: str = Field(min_length=1)
    role: str = Field(min_length=1)
    scores: dict[str, int]
    weights: dict[str, float] = Field(default_factory=lambda: dict.fromkeys(CATEGORIES, 1.0))
    critical_meaning_errors: list[str] = Field(default_factory=list)
    unsupported_additions: list[str] = Field(default_factory=list)
    omissions: list[str] = Field(default_factory=list)
    flattened_metaphors: list[str] = Field(default_factory=list)
    interpretation_as_translation: list[str] = Field(default_factory=list)
    awkward_afrikaans: list[str] = Field(default_factory=list)
    poetic_gains: list[str] = Field(default_factory=list)
    poetic_losses: list[str] = Field(default_factory=list)
    preferred: bool = False
    translator_revision: str = ""
    comments: str = ""
    status: Literal["reviewed"] = "reviewed"

    @model_validator(mode="after")
    def complete_rubric(self):
        if set(self.scores) != set(CATEGORIES) or any(
            not 1 <= n <= 5 for n in self.scores.values()
        ):
            raise ValueError("Every rubric category requires a score from 1 to 5")
        if (
            set(self.weights) != set(CATEGORIES)
            or any(w < 0 for w in self.weights.values())
            or sum(self.weights.values()) <= 0
        ):
            raise ValueError("Weights must cover all categories, be nonnegative and sum above zero")
        return self

    def weighted_score(self) -> float:
        return sum(self.scores[k] * self.weights[k] for k in CATEGORIES) / sum(
            self.weights.values()
        )
