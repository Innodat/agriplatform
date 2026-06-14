"""
OSHB Morphology Code Parser
===========================
Decodes Open Scriptures Hebrew Bible (OSHB) morphology codes into structured fields.

Reference: https://hb.openscriptures.org/parsing/HebrewMorphologyCodes.html

Format:  <language_prefix><segment>[/<segment>...]
  - Language prefix: H (Hebrew) or A (Aramaic) — appears only on first segment
  - Each segment: <POS_letter>[<feature_letters>...]

Examples:
  "HNcbsa"   → Hebrew, Noun common both singular absolute
  "HC/Td"    → Hebrew, Conjunction / Article definite
  "Vqp3ms"   → Verb qal perfect 3rd masculine singular
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Language ─────────────────────────────────────────────────────────────────

LANGUAGE_MAP = {
    "H": "hebrew",
    "A": "aramaic",
}

# ── Part of Speech ────────────────────────────────────────────────────────────

POS_MAP = {
    "A": "adjective",
    "C": "conjunction",
    "D": "adverb",
    "N": "noun",
    "P": "pronoun",
    "R": "preposition",
    "S": "suffix",
    "T": "particle",
    "V": "verb",
}

# ── Noun / Adjective / Pronoun sub-type (position 1 after POS) ───────────────

NOUN_TYPE_MAP = {
    "c": "common",
    "g": "gentilic",
    "p": "proper",
}

# ── Gender ────────────────────────────────────────────────────────────────────

GENDER_MAP = {
    "b": "both",
    "c": "common",
    "f": "feminine",
    "m": "masculine",
    "u": "unknown",
}

# ── Number ────────────────────────────────────────────────────────────────────

NUMBER_MAP = {
    "d": "dual",
    "p": "plural",
    "s": "singular",
    "u": "unknown",
}

# ── State ─────────────────────────────────────────────────────────────────────

STATE_MAP = {
    "a": "absolute",
    "c": "construct",
    "d": "determined",
}

# ── Person ────────────────────────────────────────────────────────────────────

PERSON_MAP = {
    "1": "first",
    "2": "second",
    "3": "third",
}

# ── Verb Stem ─────────────────────────────────────────────────────────────────

VERB_STEM_MAP = {
    "q": "qal",
    "N": "niphal",
    "p": "piel",
    "P": "pual",
    "h": "hiphil",
    "H": "hophal",
    "t": "hithpael",
    "o": "polel",
    "O": "polal",
    "r": "hithpolel",
    "m": "poel",
    "M": "poal",
    "k": "palel",
    "K": "pulal",
    "Q": "qal_passive",
    "l": "pilpel",
    "L": "polpal",
    "f": "hithpalpel",
    "D": "nithpael",
    "j": "pealal",
    "i": "pilel",
    "u": "hothpaal",
    "c": "tiphil",
    "v": "hishtaphel",
    "w": "nithpalel",
    "y": "nithpoel",
    "z": "hithpoel",
    # Aramaic stems
    "G": "peal",
    "C": "pael",
    "U": "aphel",
    "F": "haphel",
    "E": "saphel",
    "Y": "shaphel",
    "Z": "ethpeel",
    "B": "ethpaal",
    "W": "ithpeel",
    "d": "ithpaal",
    "T": "hishtaphel_aramaic",
    "V": "ishtaphel",
    "g": "ettaphal",
    "e": "ethaphel",
    "I": "ithpolel",
    "J": "ithpoel",
    "X": "hithpalpel_aramaic",
}

# ── Verb Aspect ───────────────────────────────────────────────────────────────

VERB_ASPECT_MAP = {
    "p": "perfect",
    "q": "sequential_perfect",
    "i": "imperfect",
    "w": "sequential_imperfect",
    "h": "cohortative",
    "j": "jussive",
    "v": "imperative",
    "r": "participle_active",
    "s": "participle_passive",
    "a": "infinitive_absolute",
    "c": "infinitive_construct",
}


@dataclass
class ParsedMorpheme:
    language: str           = "hebrew"
    part_of_speech: str     = "unknown"
    pos_code: str           = ""
    gender: Optional[str]   = None
    number: Optional[str]   = None
    state: Optional[str]    = None
    verb_stem: Optional[str]  = None
    verb_aspect: Optional[str] = None
    person: Optional[str]   = None


def _parse_segment(segment: str, language: str) -> ParsedMorpheme:
    """Parse a single morpheme segment (after stripping language prefix)."""
    m = ParsedMorpheme(language=language, pos_code=segment)

    if not segment:
        m.part_of_speech = "unknown"
        return m

    pos_letter = segment[0]
    rest = segment[1:]

    m.part_of_speech = POS_MAP.get(pos_letter, "unknown")

    if pos_letter == "V":
        # Verb: V<stem><aspect><person><gender><number>
        # e.g. Vqp3ms → stem=q, aspect=p, person=3, gender=m, number=s
        if len(rest) >= 1:
            m.verb_stem = VERB_STEM_MAP.get(rest[0])
        if len(rest) >= 2:
            m.verb_aspect = VERB_ASPECT_MAP.get(rest[1])
        if len(rest) >= 3:
            m.person = PERSON_MAP.get(rest[2])
        if len(rest) >= 4:
            m.gender = GENDER_MAP.get(rest[3])
        if len(rest) >= 5:
            m.number = NUMBER_MAP.get(rest[4])

    elif pos_letter in ("N", "A"):
        # Noun/Adjective: N<type><gender><number><state>
        # e.g. Ncbsa → type=c(common), gender=b(both), number=s, state=a
        # type letter is skipped (not stored separately)
        if len(rest) >= 2:
            m.gender = GENDER_MAP.get(rest[1])
        if len(rest) >= 3:
            m.number = NUMBER_MAP.get(rest[2])
        if len(rest) >= 4:
            m.state = STATE_MAP.get(rest[3])

    elif pos_letter == "P":
        # Pronoun: P<type><person><gender><number>
        if len(rest) >= 2:
            m.person = PERSON_MAP.get(rest[1])
        if len(rest) >= 3:
            m.gender = GENDER_MAP.get(rest[2])
        if len(rest) >= 4:
            m.number = NUMBER_MAP.get(rest[3])

    elif pos_letter == "S":
        # Suffix: S<type><person><gender><number>
        if len(rest) >= 2:
            m.person = PERSON_MAP.get(rest[1])
        if len(rest) >= 3:
            m.gender = GENDER_MAP.get(rest[2])
        if len(rest) >= 4:
            m.number = NUMBER_MAP.get(rest[3])

    elif pos_letter == "T":
        # Particle: T<type> — no inflection features
        pass

    elif pos_letter == "R":
        # Preposition: R[type] — no inflection features
        pass

    elif pos_letter == "C":
        # Conjunction — no features
        pass

    elif pos_letter == "D":
        # Adverb — no features
        pass

    return m


def parse_morph_code(morph_code: str) -> list[ParsedMorpheme]:
    """
    Parse a full OSHB morph code string into a list of ParsedMorpheme objects.

    Args:
        morph_code: e.g. "HC/Td/Ncbsa" or "HVqp3ms"

    Returns:
        List of ParsedMorpheme, one per '/' segment.
        Returns [ParsedMorpheme(part_of_speech='unknown')] on empty/None input.
    """
    if not morph_code:
        return [ParsedMorpheme(part_of_speech="unknown", pos_code="")]

    code = morph_code.strip()

    # Detect language prefix on first character
    language = "hebrew"
    if code and code[0] in LANGUAGE_MAP:
        language = LANGUAGE_MAP[code[0]]
        code = code[1:]  # strip language prefix

    segments = code.split("/")
    result = []
    for seg in segments:
        seg = seg.strip()
        if seg:
            result.append(_parse_segment(seg, language))

    return result if result else [ParsedMorpheme(part_of_speech="unknown", pos_code="")]
