"""Pure OSHB source definitions shared by import and source evidence tools."""
import re
from dataclasses import asdict
from services.oshb_morph import parse_morph_code

# ── Book metadata ─────────────────────────────────────────────────────────────
# Canonical Tanakh order: Torah (1-5), Nevi'im (6-24), Ketuvim (25-39)
BOOK_METADATA: list[dict] = [
    # Torah
    {"id": 1,  "osis_id": "Gen",  "name_en": "Genesis",          "name_he": "בְּרֵאשִׁית", "testament": "old", "division": "torah",    "book_order": 1},
    {"id": 2,  "osis_id": "Exod", "name_en": "Exodus",           "name_he": "שְׁמוֹת",     "testament": "old", "division": "torah",    "book_order": 2},
    {"id": 3,  "osis_id": "Lev",  "name_en": "Leviticus",        "name_he": "וַיִּקְרָא",  "testament": "old", "division": "torah",    "book_order": 3},
    {"id": 4,  "osis_id": "Num",  "name_en": "Numbers",          "name_he": "בְּמִדְבַּר", "testament": "old", "division": "torah",    "book_order": 4},
    {"id": 5,  "osis_id": "Deut", "name_en": "Deuteronomy",      "name_he": "דְּבָרִים",   "testament": "old", "division": "torah",    "book_order": 5},
    # Nevi'im
    {"id": 6,  "osis_id": "Josh", "name_en": "Joshua",           "name_he": "יְהוֹשֻׁעַ", "testament": "old", "division": "nevi_im",  "book_order": 1},
    {"id": 7,  "osis_id": "Judg", "name_en": "Judges",           "name_he": "שׁוֹפְטִים",  "testament": "old", "division": "nevi_im",  "book_order": 2},
    {"id": 8,  "osis_id": "1Sam", "name_en": "I Samuel",         "name_he": "שְׁמוּאֵל א", "testament": "old", "division": "nevi_im",  "book_order": 3},
    {"id": 9,  "osis_id": "2Sam", "name_en": "II Samuel",        "name_he": "שְׁמוּאֵל ב", "testament": "old", "division": "nevi_im",  "book_order": 4},
    {"id": 10, "osis_id": "1Kgs", "name_en": "I Kings",          "name_he": "מְלָכִים א",  "testament": "old", "division": "nevi_im",  "book_order": 5},
    {"id": 11, "osis_id": "2Kgs", "name_en": "II Kings",         "name_he": "מְלָכִים ב",  "testament": "old", "division": "nevi_im",  "book_order": 6},
    {"id": 12, "osis_id": "Isa",  "name_en": "Isaiah",           "name_he": "יְשַׁעְיָהוּ", "testament": "old", "division": "nevi_im",  "book_order": 7},
    {"id": 13, "osis_id": "Jer",  "name_en": "Jeremiah",         "name_he": "יִרְמְיָהוּ", "testament": "old", "division": "nevi_im",  "book_order": 8},
    {"id": 14, "osis_id": "Ezek", "name_en": "Ezekiel",          "name_he": "יְחֶזְקֵאל",  "testament": "old", "division": "nevi_im",  "book_order": 9},
    {"id": 15, "osis_id": "Hos",  "name_en": "Hosea",            "name_he": "הוֹשֵׁעַ",    "testament": "old", "division": "nevi_im",  "book_order": 10},
    {"id": 16, "osis_id": "Joel", "name_en": "Joel",             "name_he": "יוֹאֵל",      "testament": "old", "division": "nevi_im",  "book_order": 11},
    {"id": 17, "osis_id": "Amos", "name_en": "Amos",             "name_he": "עָמוֹס",      "testament": "old", "division": "nevi_im",  "book_order": 12},
    {"id": 18, "osis_id": "Obad", "name_en": "Obadiah",          "name_he": "עֹבַדְיָה",   "testament": "old", "division": "nevi_im",  "book_order": 13},
    {"id": 19, "osis_id": "Jonah","name_en": "Jonah",            "name_he": "יוֹנָה",      "testament": "old", "division": "nevi_im",  "book_order": 14},
    {"id": 20, "osis_id": "Mic",  "name_en": "Micah",            "name_he": "מִיכָה",      "testament": "old", "division": "nevi_im",  "book_order": 15},
    {"id": 21, "osis_id": "Nah",  "name_en": "Nahum",            "name_he": "נַחוּם",      "testament": "old", "division": "nevi_im",  "book_order": 16},
    {"id": 22, "osis_id": "Hab",  "name_en": "Habakkuk",         "name_he": "חֲבַקּוּק",   "testament": "old", "division": "nevi_im",  "book_order": 17},
    {"id": 23, "osis_id": "Zeph", "name_en": "Zephaniah",        "name_he": "צְפַנְיָה",   "testament": "old", "division": "nevi_im",  "book_order": 18},
    {"id": 24, "osis_id": "Hag",  "name_en": "Haggai",           "name_he": "חַגַּי",      "testament": "old", "division": "nevi_im",  "book_order": 19},
    {"id": 25, "osis_id": "Zech", "name_en": "Zechariah",        "name_he": "זְכַרְיָה",   "testament": "old", "division": "nevi_im",  "book_order": 20},
    {"id": 26, "osis_id": "Mal",  "name_en": "Malachi",          "name_he": "מַלְאָכִי",   "testament": "old", "division": "nevi_im",  "book_order": 21},
    # Ketuvim
    {"id": 27, "osis_id": "Ps",   "name_en": "Psalms",           "name_he": "תְּהִלִּים",  "testament": "old", "division": "ketuvim",  "book_order": 1},
    {"id": 28, "osis_id": "Prov", "name_en": "Proverbs",         "name_he": "מִשְׁלֵי",    "testament": "old", "division": "ketuvim",  "book_order": 2},
    {"id": 29, "osis_id": "Job",  "name_en": "Job",              "name_he": "אִיּוֹב",     "testament": "old", "division": "ketuvim",  "book_order": 3},
    {"id": 30, "osis_id": "Song", "name_en": "Song of Solomon",  "name_he": "שִׁיר הַשִּׁירִים", "testament": "old", "division": "ketuvim",  "book_order": 4},
    {"id": 31, "osis_id": "Ruth", "name_en": "Ruth",             "name_he": "רוּת",        "testament": "old", "division": "ketuvim",  "book_order": 5},
    {"id": 32, "osis_id": "Lam",  "name_en": "Lamentations",     "name_he": "אֵיכָה",      "testament": "old", "division": "ketuvim",  "book_order": 6},
    {"id": 33, "osis_id": "Eccl", "name_en": "Ecclesiastes",     "name_he": "קֹהֶלֶת",    "testament": "old", "division": "ketuvim",  "book_order": 7},
    {"id": 34, "osis_id": "Esth", "name_en": "Esther",           "name_he": "אֶסְתֵּר",    "testament": "old", "division": "ketuvim",  "book_order": 8},
    {"id": 35, "osis_id": "Dan",  "name_en": "Daniel",           "name_he": "דָּנִיֵּאל",  "testament": "old", "division": "ketuvim",  "book_order": 9},
    {"id": 36, "osis_id": "Ezra", "name_en": "Ezra",             "name_he": "עֶזְרָא",     "testament": "old", "division": "ketuvim",  "book_order": 10},
    {"id": 37, "osis_id": "Neh",  "name_en": "Nehemiah",         "name_he": "נְחֶמְיָה",   "testament": "old", "division": "ketuvim",  "book_order": 11},
    {"id": 38, "osis_id": "1Chr", "name_en": "I Chronicles",     "name_he": "דִּבְרֵי הַיָּמִים א", "testament": "old", "division": "ketuvim",  "book_order": 12},
    {"id": 39, "osis_id": "2Chr", "name_en": "II Chronicles",     "name_he": "דִּבְרֵי הַיָּמִים ב", "testament": "old", "division": "ketuvim",  "book_order": 13},
]

OSIS_TO_META = {b["osis_id"]: b for b in BOOK_METADATA}
NAME_EN_TO_META = {b["name_en"]: b for b in BOOK_METADATA}

HEBREW_RE = re.compile(r'[\u0590-\u05FF]')
DIGIT_RE = re.compile(r'\d')


def is_hebrew(text):
    return bool(HEBREW_RE.search(text))


def is_lexical(text):
    # lexical codes always contain digits (e.g. 430, 7225, 1961 a, c/853)
    return bool(DIGIT_RE.search(text))


def decode_word(word, reference):
    if not isinstance(word, list) or len(word) != 3 or not all(isinstance(x, str) for x in word):
        raise ValueError(f"{reference}: expected three strings [surface/Strong, Strong/surface, morphology]")
    first_hebrew, second_hebrew = is_hebrew(word[0]), is_hebrew(word[1])
    if first_hebrew == second_hebrew:
        raise ValueError(f"{reference}: expected exactly one Hebrew surface form")
    surface, strong = (word[0], word[1]) if first_hebrew else (word[1], word[0])
    morph = word[2]
    if not morph or morph[0] not in ("H", "A") or any(not x for x in morph[1:].split("/")):
        raise ValueError(f"{reference}: missing or malformed morphology {morph!r}")
    parsed = parse_morph_code(morph)
    if any(m.part_of_speech == "unknown" for m in parsed):
        raise ValueError(f"{reference}: unrecognized morphology {morph!r}")
    return {"surface_he": surface, "display_he": surface.replace("/", ""),
            "lemma_strong": strong, "morph_code": morph}, [asdict(m) for m in parsed]


def validate_book(book_name, book_data):
    if book_name not in NAME_EN_TO_META:
        raise ValueError(f"Unknown book name: {book_name!r}")
    if not isinstance(book_data, list) or not book_data:
        raise ValueError(f"{book_name}: expected nonempty chapter list")
    for c, verses in enumerate(book_data, 1):
        if not isinstance(verses, list) or not verses:
            raise ValueError(f"{book_name} {c}: empty or malformed chapter")
        for v, words in enumerate(verses, 1):
            if not isinstance(words, list) or not words:
                raise ValueError(f"{book_name} {c}:{v}: empty or malformed verse")
            for pos, word in enumerate(words, 1):
                decode_word(word, f"{book_name} {c}:{v} word {pos}")

