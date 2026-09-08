"""
import_bible.py — Full Tanakh importer
======================================
Reads the OSHB hebrew.json source file and populates the scribeswell schema in Supabase.

Usage:
    python tools/py/import_bible.py --source <path/to/hebrew.json> [--dry-run] [--book Gen]

Requirements:
    pip install supabase python-dotenv tqdm

Environment variables (from .env or environment):
    SUPABASE_URL          — project URL
    SUPABASE_SECRET_KEY  — service role key (bypasses RLS for import)

Source format: {"Genesis": [[[ ["Hebrew surface", "Strong code", "morphology"] ]]]}.
Chapter, verse and word positions are one-based list positions. The first two word
fields may be swapped in the supplied export. All records are validated before writes.
Use --verify-only for a read-only comparison; imports upsert and then verify each chapter.
Writes are not atomic across a book: an interrupted run exits unsuccessfully and can
be resumed with --book. Existing IDs are preserved. Unexpected extra rows fail verification.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).parent))

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from oshb_morph import parse_morph_code
from pagination import fetch_all

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.local")
load_dotenv(Path(__file__).resolve().parents[2] / "backend" / ".env")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")

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


# ── Batch helpers ─────────────────────────────────────────────────────────────

BATCH_SIZE = 500


def chunked(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


# ── Importer ──────────────────────────────────────────────────────────────────

class BibleImporter:
    def __init__(self, supabase_url: str, secret_key: str, dry_run: bool = False):
        self.dry_run = dry_run
        if not dry_run:
            try:
                from supabase import create_client
                self.sb = create_client(supabase_url, secret_key)
            except ImportError:
                print("❌ supabase package not installed. Run: pip install supabase")
                sys.exit(1)
        else:
            self.sb = None

        self.stats = {
            "books": 0, "chapters": 0, "verses": 0,
            "words": 0, "morphemes": 0, "errors": 0,
        }

    # ── upsert helpers ────────────────────────────────────────────────────────

    def _upsert(self, table: str, rows: list[dict], on_conflict: str) -> None:
        if self.dry_run or not rows:
            return
        for batch in chunked(rows, BATCH_SIZE):
            self.sb.schema("scribeswell").table(table).upsert(
                batch, on_conflict=on_conflict
            ).execute()

    # ── seed books ────────────────────────────────────────────────────────────

    def seed_books(self) -> None:
        print("📚 Seeding books...")
        if not self.dry_run:
            self._upsert("book", BOOK_METADATA, on_conflict="id")
        self.stats["books"] = len(BOOK_METADATA)
        print(f"   ✓ {len(BOOK_METADATA)} books")

    def _read(self, table, **filters):
        query = self.sb.schema("scribeswell").table(table).select("*", count="exact")
        for key, value in filters.items():
            query = query.eq(key, value)
        return fetch_all(query.order("id"))

    def validate_book(self, book_name, book_data):
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
                    self.decode_word(word, f"{book_name} {c}:{v} word {pos}")

    @staticmethod
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

    @staticmethod
    def _compare(actual, expected, keys, reference):
        def indexed(rows):
            result = {tuple(row[k] for k in keys): row for row in rows}
            if len(result) != len(rows):
                raise RuntimeError(f"{reference}: duplicate keys")
            return result
        got, want = indexed(actual), indexed(expected)
        if got.keys() != want.keys():
            raise RuntimeError(f"{reference}: missing {len(want.keys() - got.keys())}, unexpected {len(got.keys() - want.keys())} records")
        for key, row in want.items():
            if any(got[key].get(k) != value for k, value in row.items()):
                raise RuntimeError(f"{reference}: stored values differ at {key}")

    def import_book(self, book_name: str, book_data: list, verify_only=False) -> None:
        self.validate_book(book_name, book_data)
        book_id = NAME_EN_TO_META[book_name]["id"]
        chapters = [{"book_id": book_id, "chapter_num": c} for c in range(1, len(book_data)+1)]
        if self.dry_run:
            self.stats["chapters"] += len(chapters)
            for c, verses in enumerate(book_data, 1):
                self.stats["verses"] += len(verses)
                for v, words in enumerate(verses, 1):
                    for pos, word in enumerate(words, 1):
                        _, morphs = self.decode_word(word, f"{book_name} {c}:{v} word {pos}")
                        self.stats["words"] += 1
                        self.stats["morphemes"] += len(morphs)
            return
        if not verify_only:
            self._upsert("chapter", chapters, "book_id,chapter_num")
        actual = self._read("chapter", book_id=book_id)
        self._compare(actual, chapters, ["chapter_num"], book_name + " chapters")
        chapter_ids = {r["chapter_num"]: r["id"] for r in actual}
        self.stats["chapters"] += len(chapters)
        for c, verses in enumerate(book_data, 1):
            ref = f"{book_name} {c}"
            chapter_id = chapter_ids[c]
            expected_verses = [{"chapter_id": chapter_id, "verse_num": v, "book_id": book_id, "chapter_num": c}
                               for v in range(1, len(verses)+1)]
            if not verify_only:
                self._upsert("verse", expected_verses, "chapter_id,verse_num")
            actual_verses = self._read("verse", chapter_id=chapter_id)
            self._compare(actual_verses, expected_verses, ["verse_num"], ref + " verses")
            verse_ids = {r["verse_num"]: r["id"] for r in actual_verses}
            words, morphs_by_key = [], {}
            for v, source_words in enumerate(verses, 1):
                for pos, source_word in enumerate(source_words, 1):
                    word, morphs = self.decode_word(source_word, f"{ref}:{v} word {pos}")
                    key = (verse_ids[v], pos)
                    words.append({"verse_id": key[0], "position": pos, **word})
                    morphs_by_key[key] = morphs
            if not verify_only:
                self._upsert("word", words, "verse_id,position")
            actual_words = fetch_all(self.sb.schema("scribeswell").table("word").select("*", count="exact")
                                     .in_("verse_id", list(verse_ids.values())).order("id"))
            self._compare(actual_words, words, ["verse_id", "position"], ref + " words")
            morphemes = []
            for word in actual_words:
                for i, morph in enumerate(morphs_by_key[(word["verse_id"], word["position"]) ]):
                    morphemes.append({"word_id": word["id"], "segment_index": i, **morph})
            if not verify_only:
                self._upsert("morpheme", morphemes, "word_id,segment_index")
            actual_morphs = []
            for batch in chunked([w["id"] for w in actual_words], 100):
                actual_morphs.extend(fetch_all(self.sb.schema("scribeswell").table("morpheme")
                    .select("*", count="exact").in_("word_id", batch).order("id")))
            self._compare(actual_morphs, morphemes, ["word_id", "segment_index"], ref + " morphemes")
            self.stats["verses"] += len(verses)
            self.stats["words"] += len(words)
            self.stats["morphemes"] += len(morphemes)
        print(f"   Verified {book_name}: {len(chapters)} chapters", flush=True)

    def run(self, source_path: Path, only_book: str | None = None, verify_only=False) -> None:
        data = json.loads(source_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data:
            raise ValueError("Source must be a nonempty mapping of English book names to chapter lists")
        if only_book:
            meta = OSIS_TO_META.get(only_book) or NAME_EN_TO_META.get(only_book)
            if not meta or meta["name_en"] not in data:
                raise ValueError(f"Requested book {only_book!r} is unavailable")
            data = {meta["name_en"]: data[meta["name_en"]]}
        elif set(data) != set(NAME_EN_TO_META):
            raise ValueError("Full import requires exactly the 39 known books; use --book for a partial source")
        # Validate the entire selected source before the first database write.
        for name, chapters in data.items():
            self.validate_book(name, chapters)
        if verify_only:
            self._compare(self._read("book"), BOOK_METADATA, ["id"], "books")
            self.stats["books"] = len(BOOK_METADATA)
        else:
            self.seed_books()
        for name, chapters in data.items():
            print(f"{'Checking' if verify_only else 'Importing'} {name}...", flush=True)
            self.import_book(name, chapters, verify_only=verify_only)
        print(json.dumps({"status": "validated" if self.dry_run else "verified", "source_sha256":
                          hashlib.sha256(source_path.read_bytes()).hexdigest(), "counts": self.stats}), flush=True)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import full Tanakh from OSHB hebrew.json into Supabase scribeswell schema"
    )
    parser.add_argument(
        "--source", required=True,
        help="Path to hebrew.json (OSHB format)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and validate without writing to database"
    )
    parser.add_argument(
        "--book", default=None,
        help="Import only one book by OSIS id (e.g. Gen, Exod)"
    )
    parser.add_argument("--verify-only", action="store_true", help="Compare stored data with source without writing")
    args = parser.parse_args()
    if args.dry_run and args.verify_only:
        parser.error("--dry-run and --verify-only are mutually exclusive")

    source = Path(args.source)
    if not source.exists():
        print(f"❌ Source file not found: {source}")
        sys.exit(1)

    if not args.dry_run:
        if not SUPABASE_URL:
            print("❌ SUPABASE_URL not set in environment")
            sys.exit(1)
        if not SUPABASE_SECRET_KEY:
            print("❌ SUPABASE_SECRET_KEY not set in environment")
            sys.exit(1)

    importer = BibleImporter(
        supabase_url=SUPABASE_URL,
        secret_key=SUPABASE_SECRET_KEY,
        dry_run=args.dry_run,
    )
    importer.run(source_path=source, only_book=args.book, verify_only=args.verify_only)


if __name__ == "__main__":
    main()
