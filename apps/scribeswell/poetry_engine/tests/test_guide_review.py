"""Real guide layout checks plus explicitly synthetic review/transport cases."""

import json
from hashlib import sha256
from pathlib import Path

import pytest

from psalm_engine.guide_review import (
    VERSION,
    Passage,
    ReviewDecision,
    appendix_heading,
    export_review,
    extract_guide,
)
from psalm_engine.guide_scope import GUIDE_SCOPES, POLICY, guide_sections
from psalm_engine.models import Claim, Source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path", sorted((ROOT / "resources").glob("psalms-*.pdf")), ids=lambda path: path.stem
)
def test_every_supplied_guide_has_explicit_page_coverage(path):
    packet = extract_guide(path)
    assert [row["page"] for row in packet["coverage"]] == list(range(1, packet["page_count"] + 1))
    passages = {row["id"]: row for row in packet["passages"]}
    assert {p["section"] for p in passages.values()} <= {"Appendix B", "Appendix C"}
    for page in packet["coverage"]:
        if page["section"] in {"Appendix B", "Appendix C"}:
            assert page["passage_ids"]
            assert page["included"]
        else:
            assert page["passage_ids"] == []
            assert not page["included"]
            assert page["extraction_note"]
        for identifier in page["passage_ids"]:
            assert passages[identifier]["page"] == page["page"]
    assert any(p["section"] == "Appendix B" for p in passages.values())
    assert packet["included_sections"] == guide_sections(Source.model_validate(packet["source"]))


def test_appendix_reference_is_not_a_heading():
    assert appendix_heading("There are two guide translations in Appendix A:\n") is None
    assert appendix_heading("Appendix A: Guide Translations\nHebrew-mirror") == "A"


def test_real_psalm_23_keeps_only_appendices_b_and_c():
    packet = extract_guide(ROOT / "resources/psalms-23.pdf")
    assert packet["page_count"] == 24
    assert {r["page"] for r in packet["passages"]} == set(range(20, 25))
    text = "\n".join(p["text"] for p in packet["passages"])
    assert "NEPHESH" in text
    assert "metaphor changes here" in text
    assert "Flower Garden" in text
    assert "Poetic checklist" not in text
    for row in packet["passages"]:
        assert Passage.model_validate(row).reviewer_status == "pending"


def test_review_requires_person_and_explicit_claim():
    with pytest.raises(ValueError):
        ReviewDecision(
            passage_id="synthetic",
            passage_sha256="0" * 64,
            status="approved",
            reviewer=" ",
            kind="analysis",
            notes="synthetic test",
            psalms=[23],
            category="test",
        )


def test_export_checks_hashes_scope_and_keeps_full_text_out_of_claim(tmp_path):
    pdf = tmp_path / "synthetic.pdf"
    pdf.write_bytes(b"SYNTHETIC TEST ONLY")
    h = sha256(pdf.read_bytes()).hexdigest()
    text = "SYNTHETIC FULL SOURCE PASSAGE MUST NOT ENTER PROMPT"
    passage = Passage(
        id="synthetic-p1",
        source_id=f"pdf:{h}",
        guide=pdf.name,
        psalms=[23],
        page=1,
        section="Appendix B",
        text=text,
        text_sha256=sha256(text.encode()).hexdigest(),
        kind="guidance_or_analysis",
    )
    packet = tmp_path / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "scope_policy": POLICY,
                "extractor_version": VERSION,
                "source": {
                    "id": f"pdf:{h}",
                    "dataset": pdf.name,
                    "revision": h,
                    "sha256": h,
                    "uri": str(pdf),
                    "license": "synthetic",
                },
                "passages": [passage.model_dump()],
            }
        )
    )
    decisions = tmp_path / "decisions.json"
    d = ReviewDecision(
        passage_id=passage.id,
        passage_sha256=passage.text_sha256,
        status="approved",
        reviewer="Synthetic test reviewer",
        kind="analysis",
        summary="Synthetic concise claim",
        notes="Synthetic test decision; not research evidence",
        psalms=[23],
        category="test",
    )
    decisions.write_text(json.dumps([d.model_dump()]))
    output = tmp_path / "export"
    export_review(packet, decisions, 23, output)
    c = Claim.model_validate_json((output / "annotations.jsonl").read_text())
    assert c.value == d.summary
    assert text not in (output / "annotations.jsonl").read_text()
    assert c.evidence[0].page == 1
    assert c.applicable_psalms == [23]
    original = json.loads(packet.read_text())
    outside = json.loads(packet.read_text())
    outside["passages"][0]["section"] = "Step 9"
    packet.write_text(json.dumps(outside))
    with pytest.raises(ValueError, match="outside Appendix B/C"):
        export_review(packet, decisions, 23, tmp_path / "out-of-scope")
    packet.write_text(json.dumps(original))
    d.psalms = [1]
    decisions.write_text(json.dumps([d.model_dump()]))
    with pytest.raises(ValueError, match="Cross-guide"):
        export_review(packet, decisions, 1, tmp_path / "wrong-scope")
    d.psalms = [23]
    d.passage_sha256 = "0" * 64
    decisions.write_text(json.dumps([d.model_dump()]))
    with pytest.raises(ValueError, match="changed"):
        export_review(packet, decisions, 23, tmp_path / "changed")


def test_scope_inventory_matches_all_supplied_guides():
    assert {r["guide"] for r in GUIDE_SCOPES} == {
        p.name for p in (ROOT / "resources").glob("psalms-*.pdf")
    }


def test_obsolete_packets_cannot_export_even_approved_decisions(tmp_path):
    packet = tmp_path / "old-packet.json"
    packet.write_text(json.dumps({"extractor_version": "guide-passages-3"}))
    with pytest.raises(ValueError, match="Obsolete guide packet"):
        export_review(packet, tmp_path / "unused.json", 23, tmp_path / "export")
    assert not (tmp_path / "export").exists()


def test_ingest_pdf_respects_guide_scope(tmp_path):
    from psalm_engine.sources import ingest_pdf

    output = tmp_path / "guide.json"
    ingest_pdf(ROOT / "resources/psalms-23.pdf", output)
    packet = json.loads(output.read_text())
    assert packet["scope_policy"] == POLICY
    assert {p["page"] for p in packet["passages"]} == set(range(20, 25))
