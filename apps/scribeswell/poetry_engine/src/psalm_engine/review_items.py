"""Coherent, image-assisted proposals and portable, explicit human decisions.

Specifications contain assistant-authored summaries and source selectors, not
human approvals. Full extracted evidence stays in ignored local review packets.
"""

import html
import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .guide_review import VERSION as RAW_VERSION
from .guide_scope import POLICY, guide_sections
from .models import Claim, Evidence, Record, Source, now
from .storage import digest, write_json

FORMAT = "pts-review-items-1"
DECISIONS = "pts-review-decisions-1"
CATEGORIES = {
    "ambiguity": "Ambiguity and alternatives",
    "cultural_context": "Cultural context",
    "discourse": "Discourse and progression",
    "emphasis": "Emphasis",
    "figures_of_speech": "Figures of speech",
    "genre": "Genre",
    "grammar": "Grammar",
    "imagery": "Imagery",
    "inclusio": "Inclusio / framing",
    "chiasm": "Chiasm",
    "lexical_semantics": "Word meaning",
    "parallelism": "Parallelism",
    "participants": "Speaker and addressee",
    "refrain": "Refrain",
    "repetition": "Repetition and lexical links",
    "sound": "Sound patterns",
    "structure": "Stanza and line structure",
    "theological_terms": "Theological terms",
    "wordplay": "Wordplay",
}


def fingerprint(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def item_hash(item: dict, packet: dict) -> str:
    data = {k: v for k, v in item.items() if k != "item_sha256"}
    units = [packet["units"][u] for u in item["support"]]
    images = {str(u["page"]): packet["page_images"][str(u["page"])] for u in units}
    return fingerprint({"item": data, "units": units, "images": images})


def build_item_packet(raw_path: Path, spec_path: Path, resources: Path) -> dict:
    raw, spec = json.loads(raw_path.read_text()), json.loads(spec_path.read_text())
    if raw.get("scope_policy") != POLICY or raw.get("extractor_version") != RAW_VERSION:
        raise ValueError("Raw packet must use current Appendix B/C scope")
    source = Source.model_validate(raw["source"])
    if digest(Path(source.uri)) != source.sha256 or spec["pdf_sha256"] != source.sha256:
        raise ValueError("Source PDF changed since visual capture")
    if source.dataset != spec["guide"]:
        raise ValueError("Specification references another guide")
    sections = guide_sections(source)
    if sections is None:
        raise ValueError("A verified guide scope is required")
    rows = raw["passages"]
    for row in rows:
        if (
            row["source_id"] != source.id
            or sha256(row["text"].encode()).hexdigest() != row["text_sha256"]
        ):
            raise ValueError("Raw source passage changed")
        if row["page"] not in sections.get(row["section"], []):
            raise ValueError("Raw passage is outside Appendix B/C")
    units: dict[str, dict] = {}
    page_images = {}
    for image in spec["images"]:
        path = (resources / image["file"]).resolve()
        if not path.is_relative_to(resources.resolve()) or digest(path) != image["sha256"]:
            raise ValueError("Source image changed or is outside resources")
        for position, page in enumerate(image["pages"]):
            if str(page) in page_images:
                raise ValueError("Ambiguous image mapping")
            if not any(page in pages for pages in sections.values()):
                raise ValueError("Image maps outside Appendix B/C")
            page_images[str(page)] = {
                "uri": str(path),
                "sha256": image["sha256"],
                "position": position,
                "panels": len(image["pages"]),
                "mapping_method": "assistant visual inspection; human review pending",
            }

    def select(page, first=None, blocks=None):
        return [
            r
            for r in rows
            if r["page"] == page
            and (
                int(r["id"].rsplit("-b", 1)[1]) >= first
                if first is not None
                else int(r["id"].rsplit("-b", 1)[1]) in blocks
            )
        ]

    def make_units(selected, labels):
        """Join continuations and keep every original block overlapping each note."""
        text = "\n".join(r["text"] for r in selected)
        offsets, offset = [], 0
        for row in selected:
            offsets.append((offset, offset + len(row["text"]), row["id"]))
            offset += len(row["text"]) + 1
        starts = []
        for printed, identifier, label in labels:
            matches = list(re.finditer(rf"(?m)^{printed}(?!\d)\s*[.]?\s*", text))
            if len(matches) != 1:
                raise ValueError(f"Cannot reliably connect {label} on page {selected[0]['page']}")
            starts.append((matches[0].start(), identifier, label))
        if starts != sorted(starts):
            raise ValueError("Footnote order differs from inspected image")
        for n, (start, identifier, label) in enumerate(starts):
            end = starts[n + 1][0] if n + 1 < len(starts) else len(text)
            units[identifier] = {
                "id": identifier,
                "page": selected[0]["page"],
                "section": selected[0]["section"],
                "label": label,
                "text": text[start:end].strip(),
                "passage_ids": [id for a, b, id in offsets if a < end and b > start],
            }

    for plan in spec["footnote_pages"]:
        labels = []
        for printed in plan["printed_numbers"]:
            actual = plan["number_aliases"].get(str(printed), printed)
            label = f"Footnote {actual}" + (f" (printed {printed})" if actual != printed else "")
            labels.append((printed, f"n{actual}", label))
        make_units(select(plan["page"], first=plan["first_block"]), labels)
    for extra in spec["extra_units"]:
        selected = select(extra["page"], blocks=extra["blocks"])
        if len(selected) != len(extra["blocks"]):
            raise ValueError("Missing supporting source block")
        if extra["split_numbered"]:
            make_units(
                selected,
                [(n, f"{extra['id']}{n}", f"Flower Garden commentary {n}") for n in range(1, 12)],
            )
        else:
            units[extra["id"]] = {
                "id": extra["id"],
                "page": extra["page"],
                "section": selected[0]["section"],
                "label": extra["label"],
                "text": "\n".join(r["text"] for r in selected),
                "passage_ids": [r["id"] for r in selected],
            }
    packet = {
        "review_format": FORMAT,
        "scope_policy": POLICY,
        "source": source.model_dump(),
        "psalms": raw["psalms"],
        "spec_sha256": digest(spec_path),
        "raw_packet_sha256": digest(raw_path),
        "created_at": now().isoformat(),
        "units": units,
        "page_images": page_images,
        "items": [],
        "context_note_ids": spec["context_note_ids"],
        "categories": CATEGORIES,
        "limitations": [
            "Assistant-prepared proposals, not human-approved research.",
            "Extracted supporting text may have spacing or character errors; check the images.",
            "Only concise, explicitly reviewed claims enter prompts; guide translations are supporting context.",
        ],
    }
    item_ids = set()
    for proposal in spec["items"]:
        if proposal["category"] not in CATEGORIES or not proposal["summary"].strip():
            raise ValueError("Every proposal needs a substantive claim and category default")
        if not set(proposal["psalms"]) <= set(raw["psalms"]):
            raise ValueError("Item is outside the guide Psalm scope")
        if not proposal["support"] or any(u not in units for u in proposal["support"]):
            raise ValueError(f"Missing support for {proposal['id']}")
        item = dict(
            proposal,
            id=f"{Path(spec['guide']).stem}-{proposal['id']}",
            reviewer_status="pending",
            method="llm",
            preparation="assistant image-assisted source grouping",
        )
        if item["id"] in item_ids:
            raise ValueError("Duplicate item ID")
        item_ids.add(item["id"])
        item["item_sha256"] = item_hash(item, packet)
        packet["items"].append(item)
    support_ids = {u for i in packet["items"] for u in i["support"]}
    if {u for u in units if u.startswith("n")} - support_ids - set(spec["context_note_ids"]):
        raise ValueError("An explanatory footnote is unaccounted for")
    supported_blocks = {p for u in support_ids for p in units[u]["passage_ids"]}
    packet["coverage"] = [
        {
            "passage_id": r["id"],
            "page": r["page"],
            "classification": "support" if r["id"] in supported_blocks else "context",
            "reason": "Connected to a review item"
            if r["id"] in supported_blocks
            else "Source heading, legend, verse layout, marker or reference context; no separate approval",
        }
        for r in rows
    ]
    packet["context"] = [r for r in rows if r["id"] not in supported_blocks]
    return packet


class ItemDecision(Record):
    id: str
    item_sha256: str
    status: Literal["approved", "rejected", "disputed", "context"]
    reviewer: str = Field(min_length=1)
    kind: Literal["analysis", "principle"]
    category: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    alternatives: list[str] = Field(default_factory=list)
    notes: str = ""

    @model_validator(mode="after")
    def substantive(self):
        if not all(s.strip() for s in [self.reviewer, self.category, self.summary]):
            raise ValueError("Explicit reviewer, category and claim are required")
        if self.status in {"rejected", "disputed"} and not self.notes.strip():
            raise ValueError("Explain rejection or disagreement in the notes")
        return self


def decision_envelope(packet_path: Path, decisions: list[dict]) -> dict:
    return {"format": DECISIONS, "packet_sha256": digest(packet_path), "decisions": decisions}


def export_item_review(packet_path: Path, decisions_path: Path, psalm: int, output: Path) -> None:
    packet = json.loads(packet_path.read_text())
    if packet.get("review_format") != FORMAT or packet.get("scope_policy") != POLICY:
        raise ValueError("Unsupported review packet")
    envelope = json.loads(decisions_path.read_text())
    if envelope.get("format") != DECISIONS or envelope.get("packet_sha256") != digest(packet_path):
        raise ValueError("Review packet changed since decisions were recorded")
    source = Source.model_validate(packet["source"])
    if digest(Path(source.uri)) != source.sha256:
        raise ValueError("Source PDF changed")
    sections = guide_sections(source)
    if sections is None or psalm not in packet["psalms"]:
        raise ValueError("Unknown guide or inapplicable Psalm")
    decisions = [ItemDecision.model_validate(d) for d in envelope["decisions"]]
    if not decisions or len({d.id for d in decisions}) != len(decisions):
        raise ValueError("Nonempty, unique explicit decisions are required")
    items = {i["id"]: i for i in packet["items"]}
    claims: dict[str, list[Claim]] = {"annotations": [], "principles": []}
    for decision in decisions:
        item = items[decision.id]
        if (
            decision.item_sha256 != item["item_sha256"]
            or item_hash(item, packet) != item["item_sha256"]
        ):
            raise ValueError("Reviewed item or supporting evidence changed")
        if not set(item["psalms"]) <= set(packet["psalms"]):
            raise ValueError("Item Psalm scope changed")
        evidence = []
        for id in item["support"]:
            unit = packet["units"][id]
            if unit["page"] not in sections.get(unit["section"], []):
                raise ValueError("Evidence outside Appendix B/C scope")
            image = packet["page_images"][str(unit["page"])]
            if digest(Path(image["uri"])) != image["sha256"]:
                raise ValueError("Supporting image changed")
            evidence.append(
                Evidence(
                    source_id=source.id,
                    page=unit["page"],
                    locator=f"{source.dataset}, {unit['section']}, page {unit['page']}, {unit['label']}; "
                    + "; ".join(item["references"]),
                    note="Human-reviewed concise claim; source text and image remain in the local review packet.",
                )
            )
        if decision.status == "context" or psalm not in item["psalms"]:
            continue
        claims["principles" if decision.kind == "principle" else "annotations"].append(
            Claim(
                id=f"{item['id']}-review-{digest(decisions_path)[:12]}",
                category=decision.category,
                value=decision.summary,
                evidence=evidence,
                method="human",
                reviewer_status=decision.status,
                reviewer=decision.reviewer,
                reviewer_notes=decision.notes,
                applicable_psalms=item["psalms"],
                alternatives=decision.alternatives,
                supersedes=item["id"],
                revision=2,
            )
        )
    # Context-only reviews are valid audits, even with no prompt claims.
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in claims.items():
        (output / f"{name}.jsonl").write_text("".join(r.model_dump_json() + "\n" for r in rows))
    write_json(output / "pdf-evidence.json", {"source": source.model_dump()})
    write_json(
        output / "review-provenance.json",
        {
            "scope_policy": POLICY,
            "psalm": psalm,
            "packet_sha256": digest(packet_path),
            "decisions_sha256": digest(decisions_path),
            "decisions": [d.model_dump() for d in decisions],
            "created_at": now().isoformat(),
        },
    )


def render_item_review(packet_path: Path, output: Path) -> None:
    packet = json.loads(packet_path.read_text())
    payload = json.dumps(
        {"packet": packet, "packet_sha256": digest(packet_path)}, ensure_ascii=False
    )
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = Path(__file__).with_name("review_page.html").read_text()
    script = Path(__file__).with_name("review_page.js").read_text()
    with output.open("x") as stream:
        stream.write(template.replace("<!--DATA-->", payload).replace("<!--SCRIPT-->", script))


def prepare_item_reviews(packets: Path, resources: Path, output: Path) -> None:
    specs = sorted(Path(__file__).with_name("review_specs").glob("*.json"))
    output.mkdir(parents=True, exist_ok=False)
    entries = []
    for spec in specs:
        packet = build_item_packet(packets / spec.name, spec, resources)
        path = output / spec.name
        write_json(path, packet)
        render_item_review(path, output / f"{spec.stem}.html")
        entries.append(
            {
                "guide": packet["source"]["dataset"],
                "items": len(packet["items"]),
                "raw_fragments": len(packet["coverage"]),
                "packet_sha256": digest(path),
            }
        )
    write_json(
        output / "inventory.json",
        {
            "review_format": FORMAT,
            "guides": entries,
            "status": "assistant proposals; human review pending",
        },
    )
    links = "".join(
        f'<li><a href="{Path(e["guide"]).stem}.html">{html.escape(e["guide"])}</a>'
        f" — {e['items']} coherent items (from {e['raw_fragments']} source fragments)</li>"
        for e in entries
    )
    (output / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>PtS · Image-assisted review</title>'
        "<style>body{font:18px/1.7 system-ui;max-width:850px;margin:70px auto;padding:20px;"
        "background:#f6f4ed;color:#233a36}a{color:#136759}li{padding:12px}</style>"
        "<h1>PtS · Image-assisted review</h1><p>Review coherent observations, with connected footnotes, "
        "images and editable category defaults. Only Appendix B/C. All decisions start pending.</p>"
        f"<ul>{links}</ul><p>This set covers the four supplied image guides. Other guides have not "
        "yet received this visual curation; their old fragments are not equivalent review items.</p>"
    )
