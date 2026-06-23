"""
import_bible.py — Full Tanakh importer
======================================
Reads the OSHB hebrew.json source file and populates the bible schema in Supabase.

Usage:
    python tools/py/import_bible.py --source <path/to/hebrew.json> [--dry-run] [--book Gen]

Requirements:
    pip install supabase python-dotenv tqdm

Environment variables (from .env or environment):
    SUPABASE_URL          — project URL
    SUPABASE_SERVICE_KEY  — service role key (bypasses RLS for import)

JSON shape expected (OSHB format):
    {
      "Gen": {
        "1": {
          "1": [
            { "w": "בְּ", "morph": "HR/Sp3ms", "strong": "H0" },
            ...
          ]
        }
      },
      ...
    }

Each word object may have:
    w      — surface Hebrew text (required)
    morph  — OSHB morph code (optional)
    strong — Strong's number (optional)
    x      — alternate/display form (optional)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from oshb_morph import parse_morph_code

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.local", override=True)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY", "")

# ── Book metadata ─────────────────────────────────────────────────────────────
# Canonical Tanakh order: Torah (1-5), Nevi'im (6-24), Ketuvim (25-39)
BOOK_METADATA: list[dict] = [
    # Torah
    {"id": 1,  "osis_id": "Gen",  "name_en": "Genesis",          "name_he": "בְּרֵאשִׁית", "testament": "torah",    "book_order": 1},
    {"id": 2,  "osis_id": "Exod", "name_en": "Exodus",           "name_he": "שְׁמוֹת",     "testament": "torah",    "book_order": 2},
    {"id": 3,  "osis_id": "Lev",  "name_en": "Leviticus",        "name_he": "וַיִּקְרָא",  "testament": "torah",    "book_order": 3},
    {"id": 4,  "osis_id": "Num",  "name_en": "Numbers",          "name_he": "בְּמִדְבַּר", "testament": "torah",    "book_order": 4},
    {"id": 5,  "osis_id": "Deut", "name_en": "Deuteronomy",      "name_he": "דְּבָרִים",   "testament": "torah",    "book_order": 5},
    # Nevi'im
    {"id": 6,  "osis_id": "Josh", "name_en": "Joshua",           "name_he": "יְהוֹשֻׁעַ", "testament": "nevi_im",  "book_order": 1},
    {"id": 7,  "osis_id": "Judg", "name_en": "Judges",           "name_he": "שׁוֹפְטִים",  "testament": "nevi_im",  "book_order": 2},
    {"id": 8,  "osis_id": "1Sam", "name_en": "1 Samuel",         "name_he": "שְׁמוּאֵל א", "testament": "nevi_im",  "book_order": 3},
    {"id": 9,  "osis_id": "2Sam", "name_en": "2 Samuel",         "name_he": "שְׁמוּאֵל ב", "testament": "nevi_im",  "book_order": 4},
    {"id": 10, "osis_id": "1Kgs", "name_en": "1 Kings",          "name_he": "מְלָכִים א",  "testament": "nevi_im",  "book_order": 5},
    {"id": 11, "osis_id": "2Kgs", "name_en": "2 Kings",          "name_he": "מְלָכִים ב",  "testament": "nevi_im",  "book_order": 6},
    {"id": 12, "osis_id": "Isa",  "name_en": "Isaiah",           "name_he": "יְשַׁעְיָהוּ","testament": "nevi_im",  "book_order": 7},
    {"id": 13, "osis_id": "Jer",  "name_en": "Jeremiah",         "name_he": "יִרְמְיָהוּ", "testament": "nevi_im",  "book_order": 8},
    {"id": 14, "osis_id": "Ezek", "name_en": "Ezekiel",          "name_he": "יְחֶזְקֵאל",  "testament": "nevi_im",  "book_order": 9},
    {"id": 15, "osis_id": "Hos",  "name_en": "Hosea",            "name_he": "הוֹשֵׁעַ",    "testament": "nevi_im",  "book_order": 10},
    {"id": 16, "osis_id": "Joel", "name_en": "Joel",             "name_he": "יוֹאֵל",      "testament": "nevi_im",  "book_order": 11},
    {"id": 17, "osis_id": "Amos", "name_en": "Amos",             "name_he": "עָמוֹס",      "testament": "nevi_im",  "book_order": 12},
    {"id": 18, "osis_id": "Obad", "name_en": "Obadiah",          "name_he": "עֹבַדְיָה",   "testament": "nevi_im",  "book_order": 13},
    {"id": 19, "osis_id": "Jonah","name_en": "Jonah",            "name_he": "יוֹנָה",      "testament": "nevi_im",  "book_order": 14},
    {"id": 20, "osis_id": "Mic",  "name_en": "Micah",            "name_he": "מִיכָה",      "testament": "nevi_im",  "book_order": 15},
    {"id": 21, "osis_id": "Nah",  "name_en": "Nahum",            "name_he": "נַחוּם",      "testament": "nevi_im",  "book_order": 16},
    {"id": 22, "osis_id": "Hab",  "name_en": "Habakkuk",         "name_he": "חֲבַקּוּק",   "testament": "nevi_im",  "book_order": 17},
    {"id": 23, "osis_id": "Zeph", "name_en": "Zephaniah",        "name_he": "צְפַנְיָה",   "testament": "nevi_im",  "book_order": 18},
    {"id": 24, "osis_id": "Hag",  "name_en": "Haggai",           "name_he": "חַגַּי",      "testament": "nevi_im",  "book_order": 19},
    {"id": 25, "osis_id": "Zech", "name_en": "Zechariah",        "name_he": "זְכַרְיָה",   "testament": "nevi_im",  "book_order": 20},
    {"id": 26, "osis_id": "Mal",  "name_en": "Malachi",          "name_he": "מַלְאָכִי",   "testament": "nevi_im",  "book_order": 21},
    # Ketuvim
    {"id": 27, "osis_id": "Ps",   "name_en": "Psalms",           "name_he": "תְּהִלִּים",  "testament": "ketuvim",  "book_order": 1},
    {"id": 28, "osis_id": "Prov", "name_en": "Proverbs",         "name_he": "מִשְׁלֵי",    "testament": "ketuvim",  "book_order": 2},
    {"id": 29, "osis_id": "Job",  "name_en": "Job",              "name_he": "אִיּוֹב",     "testament": "ketuvim",  "book_order": 3},
    {"id": 30, "osis_id": "Song", "name_en": "Song of Songs",    "name_he": "שִׁיר הַשִּׁירִים","testament": "ketuvim","book_order": 4},
    {"id": 31, "osis_id": "Ruth", "name_en": "Ruth",             "name_he": "רוּת",        "testament": "ketuvim",  "book_order": 5},
    {"id": 32, "osis_id": "Lam",  "name_en": "Lamentations",     "name_he": "אֵיכָה",      "testament": "ketuvim",  "book_order": 6},
    {"id": 33, "osis_id": "Eccl", "name_en": "Ecclesiastes",     "name_he": "קֹהֶלֶת",    "testament": "ketuvim",  "book_order": 7},
    {"id": 34, "osis_id": "Esth", "name_en": "Esther",           "name_he": "אֶסְתֵּר",    "testament": "ketuvim",  "book_order": 8},
    {"id": 35, "osis_id": "Dan",  "name_en": "Daniel",           "name_he": "דָּנִיֵּאל",  "testament": "ketuvim",  "book_order": 9},
    {"id": 36, "osis_id": "Ezra", "name_en": "Ezra",             "name_he": "עֶזְרָא",     "testament": "ketuvim",  "book_order": 10},
    {"id": 37, "osis_id": "Neh",  "name_en": "Nehemiah",         "name_he": "נְחֶמְיָה",   "testament": "ketuvim",  "book_order": 11},
    {"id": 38, "osis_id": "1Chr", "name_en": "1 Chronicles",     "name_he": "דִּבְרֵי הַיָּמִים א","testament": "ketuvim","book_order": 12},
    {"id": 39, "osis_id": "2Chr", "name_en": "2 Chronicles",     "name_he": "דִּבְרֵי הַיָּמִים ב","testament": "ketuvim","book_order": 13},
]

OSIS_TO_META = {b["osis_id"]: b for b in BOOK_METADATA}

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
            self.sb.schema("bible").table(table).upsert(
                batch, on_conflict=on_conflict
            ).execute()

    # ── seed books ────────────────────────────────────────────────────────────

    def seed_books(self) -> None:
        print("📚 Seeding books...")
        if not self.dry_run:
            self._upsert("book", BOOK_METADATA, on_conflict="id")
        self.stats["books"] = len(BOOK_METADATA)
        print(f"   ✓ {len(BOOK_METADATA)} books")

    # ── import one book ───────────────────────────────────────────────────────

    def import_book(self, osis_id: str, book_data: dict) -> None:
        meta = OSIS_TO_META.get(osis_id)
        if not meta:
            print(f"   ⚠ Unknown book OSIS id: {osis_id!r} — skipping")
            return

        book_id = meta["id"]
        chapter_rows: list[dict] = []
        verse_rows: list[dict] = []
        word_rows: list[dict] = []
        morpheme_rows: list[dict] = []

        # ── chapters ──────────────────────────────────────────────────────────
        for ch_str, ch_data in book_data.items():
            try:
                chapter_num = int(ch_str)
            except ValueError:
                continue

            chapter_rows.append({"book_id": book_id, "chapter_num": chapter_num})

        # Upsert chapters and fetch back IDs
        if not self.dry_run:
            self._upsert("chapter", chapter_rows, on_conflict="book_id,chapter_num")
            ch_resp = (
                self.sb.schema("bible")
                .table("chapter")
                .select("id,chapter_num")
                .eq("book_id", book_id)
                .execute()
            )
            chapter_id_map: dict[int, int] = {
                row["chapter_num"]: row["id"] for row in ch_resp.data
            }
        else:
            chapter_id_map = {int(k): -(int(k)) for k in book_data.keys()}

        self.stats["chapters"] += len(chapter_rows)

        # ── verses ────────────────────────────────────────────────────────────
        for ch_str, ch_data in book_data.items():
            try:
                chapter_num = int(ch_str)
            except ValueError:
                continue

            chapter_id = chapter_id_map.get(chapter_num)
            if chapter_id is None:
                continue

            for v_str, v_words in ch_data.items():
                try:
                    verse_num = int(v_str)
                except ValueError:
                    continue

                verse_rows.append({
                    "chapter_id": chapter_id,
                    "verse_num": verse_num,
                    "book_id": book_id,
                    "chapter_num": chapter_num,
                })

        # Upsert verses and fetch back IDs
        if not self.dry_run:
            self._upsert("verse", verse_rows, on_conflict="chapter_id,verse_num")
            # Fetch all verse IDs for this book at once
            v_resp = (
                self.sb.schema("bible")
                .table("verse")
                .select("id,chapter_id,verse_num")
                .eq("book_id", book_id)
                .execute()
            )
            verse_id_map: dict[tuple[int, int], int] = {
                (row["chapter_id"], row["verse_num"]): row["id"]
                for row in v_resp.data
            }
        else:
            verse_id_map = {}

        self.stats["verses"] += len(verse_rows)

        # ── words + morphemes ─────────────────────────────────────────────────
        for ch_str, ch_data in book_data.items():
            try:
                chapter_num = int(ch_str)
            except ValueError:
                continue

            chapter_id = chapter_id_map.get(chapter_num)
            if chapter_id is None:
                continue

            for v_str, v_words in ch_data.items():
                try:
                    verse_num = int(v_str)
                except ValueError:
                    continue

                verse_id = verse_id_map.get((chapter_id, verse_num))
                if verse_id is None and not self.dry_run:
                    continue

                if not isinstance(v_words, list):
                    continue

                for pos_idx, word_obj in enumerate(v_words):
                    if not isinstance(word_obj, dict):
                        continue

                    surface = word_obj.get("w") or word_obj.get("text") or ""
                    if not surface:
                        continue

                    morph_code: Optional[str] = word_obj.get("morph") or word_obj.get("m")
                    strong: Optional[str] = word_obj.get("strong") or word_obj.get("s")
                    display: Optional[str] = word_obj.get("x")
                    position = pos_idx + 1  # 1-based

                    word_rows.append({
                        "verse_id": verse_id if verse_id else 0,
                        "position": position,
                        "surface_he": surface,
                        "display_he": display,
                        "lemma_strong": strong,
                        "morph_code": morph_code,
                    })

        # Upsert words and fetch back IDs
        if not self.dry_run and word_rows:
            self._upsert("word", word_rows, on_conflict="verse_id,position")
            # Fetch word IDs for this book's verses
            verse_ids = list(verse_id_map.values())
            # Fetch in batches to avoid URL length limits
            word_id_map: dict[tuple[int, int], int] = {}
            for id_batch in chunked(verse_ids, 200):
                w_resp = (
                    self.sb.schema("bible")
                    .table("word")
                    .select("id,verse_id,position")
                    .in_("verse_id", id_batch)
                    .execute()
                )
                for row in w_resp.data:
                    word_id_map[(row["verse_id"], row["position"])] = row["id"]
        else:
            word_id_map = {}

        self.stats["words"] += len(word_rows)

        # ── morphemes ─────────────────────────────────────────────────────────
        for ch_str, ch_data in book_data.items():
            try:
                chapter_num = int(ch_str)
            except ValueError:
                continue

            chapter_id = chapter_id_map.get(chapter_num)
            if chapter_id is None:
                continue

            for v_str, v_words in ch_data.items():
                try:
                    verse_num = int(v_str)
                except ValueError:
                    continue

                verse_id = verse_id_map.get((chapter_id, verse_num))
                if verse_id is None and not self.dry_run:
                    continue

                if not isinstance(v_words, list):
                    continue

                for pos_idx, word_obj in enumerate(v_words):
                    if not isinstance(word_obj, dict):
                        continue

                    surface = word_obj.get("w") or word_obj.get("text") or ""
                    if not surface:
                        continue

                    morph_code = word_obj.get("morph") or word_obj.get("m")
                    position = pos_idx + 1

                    word_id = word_id_map.get((verse_id, position)) if verse_id else None

                    if morph_code and (word_id or self.dry_run):
                        try:
                            parsed_morphemes = parse_morph_code(morph_code)
                            for seg_idx, pm in enumerate(parsed_morphemes):
                                morpheme_rows.append({
                                    "word_id": word_id if word_id else 0,
                                    "segment_index": seg_idx,
                                    "language": pm.language,
                                    "part_of_speech": pm.part_of_speech,
                                    "pos_code": pm.pos_code,
                                    "gender": pm.gender,
                                    "number": pm.number,
                                    "state": pm.state,
                                    "verb_stem": pm.verb_stem,
                                    "verb_aspect": pm.verb_aspect,
                                    "person": pm.person,
                                })
                        except Exception as e:
                            self.stats["errors"] += 1
                            if self.dry_run:
                                print(f"   ⚠ morph parse error for {morph_code!r}: {e}")

        if not self.dry_run and morpheme_rows:
            self._upsert("morpheme", morpheme_rows, on_conflict="word_id,segment_index")

        self.stats["morphemes"] += len(morpheme_rows)

    # ── run ───────────────────────────────────────────────────────────────────

    def run(self, source_path: Path, only_book: Optional[str] = None) -> None:
        print(f"📖 Loading {source_path}...")
        with open(source_path, encoding="utf-8") as f:
            data = json.load(f)

        print(f"   Found {len(data)} book(s) in source file.")

        self.seed_books()

        books_to_import = (
            {only_book: data[only_book]}
            if only_book and only_book in data
            else data
        )

        total = len(books_to_import)
        for idx, (osis_id, book_data) in enumerate(books_to_import.items(), 1):
            print(f"[{idx:2}/{total}] Importing {osis_id}...")
            t0 = time.time()
            self.import_book(osis_id, book_data)
            elapsed = time.time() - t0
            print(f"         ✓ done in {elapsed:.1f}s")

        print("\n── Import complete ──────────────────────────────────────")
        for k, v in self.stats.items():
            print(f"   {k:12}: {v:,}")
        if self.dry_run:
            print("\n   (DRY RUN — no data written to database)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import full Tanakh from OSHB hebrew.json into Supabase bible schema"
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
    args = parser.parse_args()

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
    importer.run(source_path=source, only_book=args.book)


if __name__ == "__main__":
    main()
