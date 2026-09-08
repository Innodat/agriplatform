"""Local source adapters. Dataset downloads are a separate explicit command."""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Literal

from .models import Source, Token, Unit
from .storage import digest

NS = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
BHSA_FEATURES = [
    "otype",
    "oslots",
    "otext",
    "book",
    "chapter",
    "verse",
    "g_word_utf8",
    "lex_utf8",
    "sp",
    "function",
    "typ",
]

BHSA_FEATURES += [
    "voc_lex_utf8",
    "g_lex_utf8",
    "g_lex",
    "lex",
    "qere_utf8",
    "qere_trailer_utf8",
    "trailer_utf8",
    "g_cons_utf8",
    "qere",
    "g_word",
    "qere_trailer",
    "trailer",
    "g_cons",
    "gn",
    "nu",
    "ps",
    "st",
    "vs",
    "vt",
]


def load_morphhb(path: Path, psalm: int, revision: str) -> tuple[Source, list[Token], list[Unit]]:
    root = ET.parse(path).getroot()
    tokens, units, excluded_notes = [], [], []
    for verse in root.findall(".//o:verse", NS):
        ref = verse.get("osisID", "")
        if not ref.startswith(f"Ps.{psalm}."):
            continue
        number = int(ref.split(".")[2])
        ids = []
        for pos, word in enumerate(verse.findall("o:w", NS), 1):
            source_id, morphology = word.get("id"), word.get("morph")
            if not source_id or not morphology:
                raise ValueError(f"{ref}:{pos}: missing MorphHB ID or morphology")
            token = Token(
                id=f"morphhb:{source_id}",
                source_id="morphhb",
                verse=number,
                position=pos,
                surface="".join(word.itertext()),
                lemma=word.get("lemma"),
                morphology=morphology,
                features={"osis_ref": ref, "original_id": source_id},
            )
            tokens.append(token)
            ids.append(token.id)
        if not ids:
            raise ValueError(f"{ref}: no main-text words")
        units.append(Unit(id=f"morphhb:{ref}", source_id="morphhb", level="verse", token_ids=ids))
        for note in verse.findall("o:note", NS):
            excluded_notes.append(
                {
                    "verse": ref,
                    "type": note.get("type"),
                    "xml": ET.tostring(note, encoding="unicode"),
                }
            )
    if not tokens:
        raise ValueError(f"Psalm {psalm} absent from {path}")
    return (
        Source(
            id="morphhb",
            dataset="Open Scriptures Hebrew Bible",
            revision=revision,
            sha256=digest(path),
            uri=str(path.resolve()),
            license="CC-BY-4.0",
            attribution="Open Scriptures Hebrew Bible; https://github.com/openscriptures/morphhb",
            metadata={
                "reading_policy": "main-text direct w elements; note alternatives retained separately",
                "alternative_notes": excluded_notes,
            },
        ),
        tokens,
        units,
    )


def load_bhsa(path: Path, psalm: int) -> tuple[Source, list[Token], list[Unit]]:
    from tf.fabric import Fabric

    manifest_path = path / "source.json"
    manifest = json.loads(manifest_path.read_text())
    for name in BHSA_FEATURES:
        file = path / f"{name}.tf"
        if digest(file) != manifest["files"][file.name]:
            raise ValueError(f"BHSA file hash mismatch: {file.name}")
    api = Fabric(locations=str(path), silent="deep").load(
        "book chapter verse g_word_utf8 lex_utf8 sp function typ gn nu ps st vs vt", silent="deep"
    )
    if api is None:
        raise ValueError(f"Could not load local BHSA features from {path}")
    F, L = api.F, api.L
    verses = []
    for v in F.otype.s("verse"):
        books, chapters = L.u(v, otype="book"), L.u(v, otype="chapter")
        if (
            books
            and chapters
            and F.book.v(books[0]) == "Psalmi"
            and F.chapter.v(chapters[0]) == psalm
        ):
            verses.append(v)
    tokens, units = [], []
    seen_units = set()
    levels: list[Literal["clause", "phrase", "sentence"]] = ["clause", "phrase", "sentence"]
    psalm_words = {w for v in verses for w in L.d(v, otype="word")}
    for verse in verses:
        number = F.verse.v(verse)
        words = L.d(verse, otype="word")
        for pos, word in enumerate(words, 1):
            tokens.append(
                Token(
                    id=f"bhsa:{word}",
                    source_id="bhsa",
                    verse=number,
                    position=pos,
                    surface=F.g_word_utf8.v(word),
                    surface_status="present" if F.g_word_utf8.v(word) else "source_empty",
                    lemma=F.lex_utf8.v(word),
                    features={
                        "sp": F.sp.v(word),
                        "original_node": word,
                        **{
                            name: getattr(F, name).v(word)
                            for name in ["gn", "nu", "ps", "st", "vs", "vt"]
                        },
                    },
                )
            )
        units.append(
            Unit(
                id=f"bhsa:{verse}",
                source_id="bhsa",
                level="verse",
                token_ids=[f"bhsa:{w}" for w in words],
            )
        )
        for word in words:
            for level in levels:
                for node in L.u(word, otype=level):
                    if node in seen_units:
                        continue
                    seen_units.add(node)
                    # A source unit may cross verses; intersect only with this Psalm.
                    ids = [f"bhsa:{w}" for w in L.d(node, otype="word") if w in psalm_words]
                    units.append(
                        Unit(
                            id=f"bhsa:{node}",
                            source_id="bhsa",
                            level=level,
                            token_ids=ids,
                            features={"function": F.function.v(node), "type": F.typ.v(node)},
                        )
                    )
    if not tokens:
        raise ValueError(f"Psalm {psalm} absent from local BHSA")
    checksum = hashlib.sha256(json.dumps(manifest["files"], sort_keys=True).encode()).hexdigest()
    return (
        Source(
            id="bhsa",
            dataset="ETCBC BHSA",
            revision=manifest["revision"],
            sha256=checksum,
            uri=str(path.resolve()),
            license="CC-BY-NC-4.0",
            attribution="ETCBC, VU Amsterdam; https://doi.org/10.17026/dans-z6y-skyh",
            metadata={"version": manifest["version"], "files": manifest["files"]},
        ),
        tokens,
        units,
    )


def ingest_pdf(path: Path, output: Path) -> None:
    """Local page text for review. Never send extracted full text to a provider."""
    from pypdf import PdfReader

    from .storage import write_json

    sha = digest(path)
    reader = PdfReader(path)
    metadata = {str(k): str(v) for k, v in (reader.metadata or {}).items()}
    pages: list[dict[str, Any]] = [
        {
            "source_id": f"pdf:{sha}",
            "page": i,
            "text": page.extract_text() or "",
            "reviewer_status": "pending",
        }
        for i, page in enumerate(reader.pages, 1)
    ]
    if not any(p["text"].strip() for p in pages):
        raise ValueError("PDF contains no extractable text; OCR/human transcription is required")
    write_json(
        output,
        {
            "source": Source(
                id=f"pdf:{sha}",
                dataset=path.name,
                revision=sha,
                sha256=sha,
                uri=str(path.resolve()),
                license="unknown; local research only",
                metadata=metadata,
            ).model_dump(mode="json"),
            "pages": pages,
            "warning": "Unreviewed extracted text; not approved principles or unrestricted training data",
        },
    )
