"""Local review of Appendix B/C only; never automatic scholarly approval.

All ten steps, introductory material and Appendix A are outside the source scope.
Full passage text and review HTML belong only in ignored local directories.
"""

import html
import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .guide_scope import POLICY, SECTIONS, guide_sections
from .models import Claim, Evidence, Record, Source, now
from .storage import digest, write_json

VERSION = "guide-passages-4"
APPENDIX = re.compile(r"^Appendix\s+([A-Z])\s*:", re.IGNORECASE | re.MULTILINE)
MIRROR = re.compile(r"Hebrew[\s\-–‑]*mirror", re.IGNORECASE)


class Passage(Record):
    id: str
    source_id: str
    guide: str
    psalms: list[int] = Field(min_length=1)
    page: int = Field(ge=1)
    section: str
    text: str = Field(min_length=1)
    text_sha256: str
    kind: Literal["guidance_or_analysis", "reference_translation"]
    method: Literal["imported"] = "imported"
    reviewer_status: Literal["pending"] = "pending"
    warnings: list[str] = Field(default_factory=list)


class ReviewDecision(Record):
    passage_id: str
    passage_sha256: str
    status: Literal["approved", "rejected", "disputed", "context"]
    reviewer: str = Field(min_length=1)
    kind: Literal["principle", "analysis"]
    summary: str = ""
    notes: str = Field(min_length=1)
    # Explicit applicability prevents accidentally applying Psalm 23 analysis to 1.
    psalms: list[int] = Field(min_length=1)
    category: str = Field(min_length=1)
    alternatives: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def substantive_review(self):
        if not self.reviewer.strip() or not self.notes.strip():
            raise ValueError("Reviewer and review notes are required")
        if self.status != "context" and not self.summary.strip():
            raise ValueError("Record a concise claim, separately from the source passage")
        if any(not 1 <= p <= 150 for p in self.psalms):
            raise ValueError("Invalid Psalm applicability")
        return self


def appendix_heading(text: str) -> str | None:
    match = APPENDIX.search(text)
    return match[1].upper() if match else None


def passage_blocks(text: str) -> list[str]:
    """Keep every nonblank paragraph, including questions and uncertain assertions."""
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def positioned_text(fragments: list[tuple[float, float, float, str]]) -> str:
    """Restore line/paragraph breaks suppressed by pypdf's visitor callbacks."""
    rows: list[list[tuple[float, float, float, str]]] = []
    for fragment in sorted(fragments, key=lambda f: (-f[1], f[0])):
        if not fragment[3].strip():
            continue
        if not rows or abs(rows[-1][0][1] - fragment[1]) > 3:
            rows.append([])
        rows[-1].append(fragment)
    output = []
    previous_y = previous_size = 0.0
    for row in rows:
        row.sort(key=lambda f: f[0])
        text = "".join(f[3].replace("\n", "") for f in row).strip()
        y, size = row[0][1], max(f[2] for f in row)
        new_paragraph = (
            previous_y - y > 1.5 * max(previous_size, size)
            or size >= 13
            or previous_size >= 13
            or bool(re.match(r"^(?:[•▪]\s*|\d+[.)]\s|[a-z][.)]\s)", text))
            or (text.isupper() and len(text) > 5)
        )
        output.append(("\n\n" if new_paragraph else "\n") + text)
        previous_y, previous_size = y, size
    return "".join(output).strip()


def extract_guide(path: Path) -> dict:
    from pypdf import PdfReader

    numbers = re.fullmatch(r"psalms-(\d+)(?:-(\d+))?", path.stem)
    if not numbers:
        raise ValueError(f"Guide filename must declare Psalm scope: {path.name}")
    psalms = list(range(int(numbers[1]), int(numbers[2] or numbers[1]) + 1))
    if not psalms or any(not 1 <= p <= 150 for p in psalms):
        raise ValueError("Invalid guide Psalm range")
    reader = PdfReader(path)
    source_hash = digest(path)
    source = Source(
        id=f"pdf:{source_hash}",
        dataset=path.name,
        revision=source_hash,
        sha256=source_hash,
        uri=str(path.resolve()),
        license="unknown; local research only",
        metadata={str(k): str(v) for k, v in (reader.metadata or {}).items()},
    )
    expected_sections = guide_sections(source)
    passages, coverage = [], []
    section = "Excluded guide material"
    found_sections: dict[str, list[int]] = {name: [] for name in SECTIONS}
    for number, page in enumerate(reader.pages, 1):
        full_text = page.extract_text() or ""
        heading = appendix_heading(full_text)
        if heading:
            section = f"Appendix {heading}"
            if section in SECTIONS and not re.search(
                rf"^Appendix\s+{heading}\s*:\s*{SECTIONS[section]}",
                full_text,
                re.IGNORECASE | re.MULTILINE,
            ):
                raise ValueError(f"Unexpected appendix title: {path.name} page {number}")
        included = section in SECTIONS
        if not included:
            coverage.append(
                {
                    "page": number,
                    "section": section,
                    "included": False,
                    "passage_ids": [],
                    "extraction_note": "Excluded by scope: only Appendix B and Appendix C are used.",
                }
            )
            continue
        if (
            abs(float(page.mediabox.width) - 595.32) > 2
            or abs(float(page.mediabox.height) - 841.92) > 2
            or page.rotation
        ):
            raise ValueError(f"Unverified page layout: {path.name} page {number}")
        kept: list[tuple[float, float, float, str]] = []

        def visit(text, cm, tm, font, size, kept=kept):
            x, y = float(tm[4]), float(tm[5])
            if 60 < y < 730:
                kept.append((x, y, float(size), text))

        page.extract_text(visitor_text=visit)
        body = positioned_text(kept)
        if not body:
            raise ValueError(
                f"Empty retained page: {path.name} page {number}; needs visual/OCR review"
            )
        if heading and appendix_heading(body) != heading:
            raise ValueError(f"Appendix heading outside body: {path.name} page {number}")
        if heading and not body.lower().startswith(f"appendix {heading.lower()}"):
            raise ValueError(f"Mixed section boundary requires review: {path.name} page {number}")
        found_sections[section].append(number)
        ids = []
        for ordinal, block in enumerate(passage_blocks(body), 1):
            text_hash = sha256(block.encode()).hexdigest()
            identifier = f"{path.stem}-{source_hash[:12]}-p{number:03}-b{ordinal:03}"
            warnings = [
                "Source assertions/questions are unreviewed; not established Hebrew facts.",
                "Check the PDF for colour, layout, diagrams, footnote placement and extraction errors.",
                (
                    "Use only Appendix B/C. Do not follow cross-references to steps, phases, "
                    "Appendix A or other excluded guide sections."
                ),
            ]
            if MIRROR.search(block):
                warnings.append("Cross-reference to excluded Hebrew mirror: do not retrieve it.")
            passage = Passage(
                id=identifier,
                source_id=source.id,
                guide=path.name,
                psalms=psalms,
                page=number,
                section=section,
                text=block,
                text_sha256=text_hash,
                kind="guidance_or_analysis",
                warnings=warnings,
            )
            passages.append(passage.model_dump())
            ids.append(identifier)
        coverage.append(
            {
                "page": number,
                "section": section,
                "included": True,
                "passage_ids": ids,
                "retained_text_sha256": sha256(body.encode()).hexdigest(),
                "visual_review": "pending; text extraction does not recover visual meaning",
            }
        )
    if not found_sections["Appendix B"]:
        raise ValueError(f"No verified Appendix B in {path.name}")
    if expected_sections is not None and found_sections != expected_sections:
        raise ValueError(f"Appendix boundaries differ from pinned scope: {path.name}")
    return {
        "extractor_version": VERSION,
        "scope_policy": POLICY,
        "source": source.model_dump(),
        "psalms": psalms,
        "page_count": len(reader.pages),
        "included_sections": found_sections,
        "absent_sections": [s for s, pages in found_sections.items() if not pages],
        "coverage": coverage,
        "passages": passages,
        "status": "Appendix B/C passages extracted; semantic and visual review pending",
    }


def extract_guides(resources: Path, output: Path) -> None:
    """Create immutable, local review packets for every supplied guide."""
    paths = sorted(resources.glob("psalms-*.pdf"))
    if not paths:
        raise ValueError("No Psalm guides found")
    output.mkdir(parents=True, exist_ok=False)
    entries = []
    try:
        for path in paths:
            packet = extract_guide(path)
            write_json(output / f"{path.stem}.json", packet)
            render_review(packet, output / f"{path.stem}.html")
            entries.append(
                {
                    "guide": path.name,
                    "psalms": packet["psalms"],
                    "sha256": packet["source"]["sha256"],
                    "pages": packet["page_count"],
                    "passages": len(packet["passages"]),
                    "included_sections": packet["included_sections"],
                    "absent_sections": packet["absent_sections"],
                }
            )
            print(
                f"{path.name}: {packet['page_count']} pages, {len(packet['passages'])} passages",
                flush=True,
            )
    except Exception as error:
        write_json(
            output / "status.json",
            {
                "status": "failed",
                "completed_guides": entries,
                "failed_guide": path.name,
                "error": str(error),
            },
        )
        raise
    write_json(
        output / "inventory.json",
        {
            "extractor_version": VERSION,
            "scope_policy": POLICY,
            "created_at": now().isoformat(),
            "guides": entries,
            "status": "all guide appendices B/C processed; human semantic and visual review pending",
        },
    )
    links = "\n".join(
        f'<li><a href="{Path(e["guide"]).stem}.html">{e["guide"]}</a> — '
        f"{e['passages']} passages; Appendix B pages {e['included_sections']['Appendix B']}; "
        f"Appendix C pages {e['included_sections']['Appendix C'] or 'not present'}</li>"
        for e in entries
    )
    (output / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Psalm guide review</title>'
        "<h1>Psalm guide review</h1><p>All extracted passages await review. "
        "Only separately approved claims may enter translation prompts. "
        "Only Appendix B (Exegetical Layout) and Appendix C (Flower Garden) are used. "
        "All ten steps, the three phases, Appendix A and introductory material are excluded. "
        "PDF rights remain unverified; keep local.</p>"
        f"<ul>{links}</ul>",
        encoding="utf-8",
    )


def render_review(packet: dict, output: Path) -> None:
    """Standalone browser form; downloads explicit decisions, never silently approves."""
    cards = []
    coverage_notes = "".join(
        f'<p><a href="{html.escape(Path(packet["source"]["uri"]).as_uri())}'
        f'#page={row["page"]}">Page {row["page"]}</a>: '
        f"{html.escape(row['extraction_note'])}</p>"
        for row in packet["coverage"]
        if row.get("extraction_note")
    )
    for row in packet["passages"]:
        p = Passage.model_validate(row)
        cards.append(
            f'<article data-id="{p.id}" data-hash="{p.text_sha256}">'
            f"<h2>Page {p.page} · {html.escape(p.section)}</h2>"
            f"<small>{p.id} · {p.kind}</small>"
            f'<p><a href="{html.escape(Path(packet["source"]["uri"]).as_uri())}'
            f'#page={p.page}" target="_blank">Open source page</a></p>'
            f"<pre>{html.escape(p.text)}</pre>"
            f'<p class="warning">{html.escape(" ".join(p.warnings))}</p>'
            '<label>Decision <select class="status"><option value="">Pending</option>'
            "<option>approved</option><option>rejected</option><option>disputed</option>"
            '<option value="context">Reference context only</option></select></label> '
            '<label>Record type <select class="kind"><option value="analysis">Psalm analysis</option>'
            '<option value="principle">Translation/evaluation guidance</option></select></label>'
            '<label>Category <input class="category" placeholder="e.g. imagery, discourse, workflow"></label>'
            '<label>Concise claim in your words <textarea class="summary"></textarea></label>'
            "<label>Review notes, qualifications and disagreements "
            '<textarea class="notes"></textarea></label></article>'
        )
    output.write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        f"<title>{html.escape(packet['source']['dataset'])} review</title>"
        "<style>body{max-width:960px;margin:2rem auto;font:17px/1.5 system-ui;padding:1rem}"
        "article{border-top:2px solid #ccc;padding:1rem 0}pre{white-space:pre-wrap;font:inherit;"
        "background:#f5f5f5;padding:1rem}label{display:block;margin:.5rem 0}"
        "textarea{display:block;width:98%;height:5rem}input{min-width:20rem}"
        ".warning{color:#694a10;font-size:.9rem}header{background:white;padding:1rem;"
        "position:sticky;top:0;border-bottom:1px solid #ddd}button{padding:.6rem}</style>"
        '<header><a href="index.html">All guides</a>'
        f"<h1>{html.escape(packet['source']['dataset'])} — review passages</h1>"
        '<label>Reviewer identifier <input id="reviewer"></label>'
        '<label>Find text <input id="search" type="search"></label>'
        '<button id="download">Download decisions</button>'
        "<p>Save decisions before closing. Nothing is submitted automatically.</p></header>"
        "<p>Keep qualifications and competing interpretations. Questions are not assertions. "
        "Check colour/layout against the PDF. Only Appendix B and Appendix C are in scope. "
        "Ignore cross-references to the ten steps, three phases, Appendix A and other excluded "
        "sections. Only concise reviewed claims from these appendices can be exported.</p>"
        + coverage_notes
        + "\n".join(cards)
        + "<script>const psalms="
        + json.dumps(packet["psalms"])
        + ";"
        + """
const cards=[...document.querySelectorAll('article')];
document.querySelector('#search').oninput=e=>cards.forEach(c=>{
 c.hidden=!c.textContent.toLowerCase().includes(e.target.value.toLowerCase());
});
document.querySelector('#download').onclick=()=>{
 const reviewer=document.querySelector('#reviewer').value.trim();
 const decisions=[];
 for(const card of cards){
  const get=c=>card.querySelector('.'+c).value.trim();
  if(!get('status'))continue;
  if(!reviewer || !get('notes') || !get('category') ||
     (get('status')!=='context' && !get('summary'))){
   alert('Each decision needs a reviewer, category, notes and a concise claim (except context).');
   return;
  }
  decisions.push({passage_id:card.dataset.id,passage_sha256:card.dataset.hash,
   status:get('status'),reviewer,kind:get('kind'),summary:get('summary'),notes:get('notes'),
   category:get('category'),psalms,alternatives:[]});
 }
 if(!decisions.length){alert('No decisions yet.');return;}
 const url=URL.createObjectURL(new Blob([JSON.stringify(decisions,null,2)],
  {type:'application/json'}));
 const a=document.createElement('a');a.href=url;a.download='guide-review-decisions.json';
 a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
</script></html>""",
        encoding="utf-8",
    )


def export_review(packet_path: Path, decisions_path: Path, psalm: int, output: Path) -> None:
    packet = json.loads(packet_path.read_text())
    if packet.get("review_format"):
        from .review_items import export_item_review

        export_item_review(packet_path, decisions_path, psalm, output)
        return
    if packet.get("scope_policy") != POLICY or packet.get("extractor_version") != VERSION:
        raise ValueError("Obsolete guide packet: regenerate with Appendix B/C scope")
    source = Source.model_validate(packet["source"])
    sections = guide_sections(source)
    if digest(Path(source.uri)) != source.sha256:
        raise ValueError("Source PDF changed after extraction")
    passages = {p.id: p for p in map(Passage.model_validate, packet["passages"])}
    decisions = [ReviewDecision.model_validate(d) for d in json.loads(decisions_path.read_text())]
    if not decisions or len({d.passage_id for d in decisions}) != len(decisions):
        raise ValueError("Need nonempty, unique passage decisions")
    claims: dict[str, list[Claim]] = {"principles": [], "annotations": []}
    for decision in decisions:
        passage = passages[decision.passage_id]
        if passage.section not in SECTIONS or (
            sections is not None and passage.page not in sections[passage.section]
        ):
            raise ValueError("Reviewed passage is outside Appendix B/C scope")
        if passage.source_id != source.id:
            raise ValueError("Passage references a different source")
        if (
            decision.passage_sha256 != passage.text_sha256
            or sha256(passage.text.encode()).hexdigest() != passage.text_sha256
        ):
            raise ValueError("Reviewed passage changed")
        if not set(decision.psalms) <= set(passage.psalms):
            raise ValueError("Cross-guide generalisation requires a separate reviewed claim")
        if decision.status == "context" or psalm not in decision.psalms:
            continue
        claims["principles" if decision.kind == "principle" else "annotations"].append(
            Claim(
                id=f"{passage.id}-review-{digest(decisions_path)[:12]}",
                category=decision.category,
                value=decision.summary,
                evidence=[
                    Evidence(
                        source_id=passage.source_id,
                        page=passage.page,
                        locator=f"{passage.guide}, {passage.section}, page {passage.page}, passage {passage.id}",
                        note="Reviewed summary of local source passage; not independently verified fact.",
                    )
                ],
                method="human",
                reviewer_status=decision.status,
                reviewer=decision.reviewer,
                reviewer_notes=decision.notes,
                supersedes=passage.id,
                revision=2,
                alternatives=decision.alternatives,
                applicable_psalms=decision.psalms,
            )
        )
    if not any(claims.values()):
        raise ValueError("No reviewed claims applicable to this Psalm")
    output.mkdir(parents=True, exist_ok=False)
    for name, records in claims.items():
        (output / f"{name}.jsonl").write_text(
            "".join(c.model_dump_json() + "\n" for c in records), encoding="utf-8"
        )
    write_json(output / "pdf-evidence.json", {"source": source.model_dump()})
    write_json(
        output / "review-provenance.json",
        {
            "psalm": psalm,
            "scope_policy": POLICY,
            "packet_sha256": digest(packet_path),
            "decisions_sha256": digest(decisions_path),
            "decisions": [d.model_dump() for d in decisions],
            "created_at": now().isoformat(),
        },
    )
