"""
import_bible.py — Full Tanakh importer
======================================
Reads the OSHB hebrew.json source file and populates the scribeswell schema in Supabase.

Usage:
    python tools/py/import_bible.py --source <path/to/hebrew.json> [--dry-run] [--book Gen]

Requirements:
    pip install "psycopg[binary,pool]>=3.2,<4" python-dotenv

Environment variables (from .env or environment):
    SCRIBESWELL_IMPORT_DATABASE_URL — restricted scribeswell_import PostgreSQL URL

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
from dataclasses import asdict, dataclass
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(Path(__file__).parent))

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))
from oshb_morph import parse_morph_code
from database import Database, DatabaseUnavailable

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env.local")
load_dotenv(Path(__file__).resolve().parents[2] / "backend" / ".env")

IMPORT_DATABASE_URL = os.environ.get("SCRIBESWELL_IMPORT_DATABASE_URL", "")

from corpus_source import (BOOK_METADATA, OSIS_TO_META, NAME_EN_TO_META,
                           HEBREW_RE, DIGIT_RE, is_hebrew, is_lexical,
                           decode_word, validate_book)


from corpus_evidence import LABEL, SHA256, MAX_SOURCE_BYTES, _unique_object, EvidenceError, build_source_candidate
from corpus_publication_input import _uuid, _generation


class ImportBindingError(ValueError):
    def __init__(self):
        super().__init__('corpus_import.binding_invalid')


@dataclass(frozen=True)
class ImportBinding:
    source_id: str
    attempt_id: str
    generation: str
    input_sha256: str

    def __post_init__(self):
        valid = (isinstance(self.source_id, str) and LABEL.fullmatch(self.source_id)
                 and isinstance(self.input_sha256, str) and SHA256.fullmatch(self.input_sha256))
        try:
            _uuid(self.attempt_id)
            _generation(self.generation)
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise ImportBindingError()


# ── Batch helpers ─────────────────────────────────────────────────────────────

BATCH_SIZE = 500


def chunked(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


# ── Importer ──────────────────────────────────────────────────────────────────

class BibleImporter:
    def __init__(self, database_url: str, dry_run: bool = False, *, binding: ImportBinding | None = None):
        if binding is not None and not isinstance(binding, ImportBinding):
            raise ImportBindingError()
        self.binding = binding
        self._run_active = False
        self.dry_run = dry_run
        self.db = None
        if not dry_run:
            self.db = Database(database_url, 'scribeswell_import', production=os.environ.get('APP_ENV') == 'production', max_size=1)
            self.db.open()

        self.stats = {
            "books": 0, "chapters": 0, "verses": 0,
            "words": 0, "morphemes": 0, "errors": 0,
        }

    def close(self):
        if self.db is not None:
            self.db.close()

    # ── upsert helpers ────────────────────────────────────────────────────────

    def _upsert(self, table: str, rows: list[dict], on_conflict: str) -> None:
        if self.dry_run or not rows:
            return
        for batch in chunked(rows, BATCH_SIZE):
            self.db.upsert(table, batch, on_conflict)

    @contextmanager
    def _write_transaction(self):
        if self.binding is not None and not self._run_active:
            raise ImportBindingError()
        with self.db.transaction():
            if self.binding is not None:
                with self.db.connection() as connection:
                    connection.execute('SELECT scribeswell.bind_corpus_write(%s,%s,%s,%s)',
                                       (self.binding.source_id, int(self.binding.generation),
                                        self.binding.attempt_id, self.binding.input_sha256))
            yield

    # ── seed books ────────────────────────────────────────────────────────────

    def seed_books(self) -> None:
        print("📚 Seeding books...")
        if not self.dry_run:
            with self._write_transaction():
                self._upsert("book", BOOK_METADATA, on_conflict="id")
        self.stats["books"] = len(BOOK_METADATA)
        print(f"   ✓ {len(BOOK_METADATA)} books")

    def _read(self, table, **filters):
        return self.db.read(table, filters=filters)

    def validate_book(self, book_name, book_data):
        return validate_book(book_name, book_data)

    decode_word = staticmethod(decode_word)

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
        if self.binding is not None and not self.dry_run and not verify_only and not self._run_active:
            raise ImportBindingError()
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
        actual = self._read("chapter", book_id=book_id)
        if verify_only:
            self._compare(actual, chapters, ["chapter_num"], book_name + " chapters")
        elif any(row["chapter_num"] not in range(1, len(chapters) + 1) for row in actual):
            raise RuntimeError(f"{book_name} chapters: unexpected records")
        for c, verses in enumerate(book_data, 1):
            with (self.db.transaction() if verify_only else self._write_transaction()):
                ref = f"{book_name} {c}"
                if not verify_only:
                    self._upsert("chapter", [chapters[c - 1]], "book_id,chapter_num")
                chapter_rows = self._read("chapter", book_id=book_id, chapter_num=c)
                self._compare(chapter_rows, [chapters[c - 1]], ["chapter_num"], ref + " chapter")
                chapter_id = chapter_rows[0]["id"]
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
                actual_words = self.db.read("word", in_filters={"verse_id": list(verse_ids.values())})
                self._compare(actual_words, words, ["verse_id", "position"], ref + " words")
                morphemes = []
                for word in actual_words:
                    for i, morph in enumerate(morphs_by_key[(word["verse_id"], word["position"]) ]):
                        morphemes.append({"word_id": word["id"], "segment_index": i, **morph})
                if not verify_only:
                    self._upsert("morpheme", morphemes, "word_id,segment_index")
                actual_morphs = []
                for batch in chunked([w["id"] for w in actual_words], 100):
                    actual_morphs.extend(self.db.read("morpheme", in_filters={"word_id": batch}))
                self._compare(actual_morphs, morphemes, ["word_id", "segment_index"], ref + " morphemes")
                self.stats["chapters"] += 1
                self.stats["verses"] += len(verses)
                self.stats["words"] += len(words)
                self.stats["morphemes"] += len(morphemes)
        print(f"   Verified {book_name}: {len(chapters)} chapters", flush=True)

    def run(self, source_path: Path, only_book: str | None = None, verify_only=False) -> None:
        if self._run_active:
            raise ImportBindingError()
        with source_path.open('rb') as source:
            raw = source.read(MAX_SOURCE_BYTES + 1) if self.binding is not None else source.read()
        checksum = hashlib.sha256(raw).hexdigest()
        if self.binding is not None and (len(raw) > MAX_SOURCE_BYTES or checksum != self.binding.input_sha256):
            raise ImportBindingError()
        try:
            data = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object if self.binding else None)
        except (UnicodeError, ValueError, RecursionError):
            if self.binding is not None:
                raise ImportBindingError() from None
            raise
        if self.binding is not None:
            if type(data) is not dict or set(data) != set(NAME_EN_TO_META):
                raise ImportBindingError()
            # Even --book repairs must qualify the complete approved artifact first.
            try:
                # Local preflight labels qualify structure/bytes only. No manifest or
                # publication identity is created or inferred from this discarded result.
                build_source_candidate(raw, self.binding.input_sha256, source_id=self.binding.source_id,
                                       catalogue_version='import-preflight-v1',
                                       versification_id='import-preflight-v1',
                                       tokenization_version='import-preflight-v1')
            except EvidenceError:
                raise ImportBindingError() from None
        self._run_active = True
        try:
            self._run_data(data, checksum, only_book, verify_only)
        finally:
            self._run_active = False

    def _run_data(self, data, checksum, only_book, verify_only):
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
                          checksum, "counts": self.stats}), flush=True)


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
    parser.add_argument('--source-id', help='Source identity for an existing fenced attempt')
    parser.add_argument('--attempt-id', help='Current owner-issued attempt UUID')
    parser.add_argument('--generation', help='Current positive decimal attempt generation')
    parser.add_argument('--expected-source-sha256', help='Approved full artifact checksum')
    args = parser.parse_args()
    values = (args.source_id, args.attempt_id, args.generation, args.expected_source_sha256)
    binding = None
    if any(value is not None for value in values):
        if not all(value is not None for value in values):
            parser.error('all four fenced attempt options are required together')
        try:
            binding = ImportBinding(*values)
        except ImportBindingError:
            parser.error('fenced attempt options are invalid')
    if args.dry_run and args.verify_only:
        parser.error("--dry-run and --verify-only are mutually exclusive")

    source = Path(args.source)
    if not source.exists():
        print(f"❌ Source file not found: {source}")
        sys.exit(1)

    if not args.dry_run and not IMPORT_DATABASE_URL:
        parser.error("SCRIBESWELL_IMPORT_DATABASE_URL is required")
    importer = None
    try:
        importer = BibleImporter(IMPORT_DATABASE_URL, dry_run=args.dry_run, binding=binding)
        importer.run(source_path=source, only_book=args.book, verify_only=args.verify_only)
    except ImportBindingError:
        raise SystemExit('Import failed: approved source or attempt binding is invalid') from None
    except DatabaseUnavailable:
        raise SystemExit("Import failed: database unavailable; retry after recovery") from None
    finally:
        if importer is not None:
            importer.close()


if __name__ == "__main__":
    main()
