"""Image-assisted proposals are reviewable units, never automatic approvals."""

import json
from pathlib import Path

import pytest

from psalm_engine.guide_review import extract_guide
from psalm_engine.review_items import build_item_packet, export_item_review, render_item_review

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def raw_packets(tmp_path_factory):
    output = tmp_path_factory.mktemp("raw-guide-packets")
    for guide in ["1", "23", "133", "42-43"]:
        data = extract_guide(ROOT / f"resources/psalms-{guide}.pdf")
        (output / f"psalms-{guide}.json").write_text(json.dumps(data))
    return output


@pytest.fixture(scope="module")
def packet(raw_packets):
    return build_item_packet(
        raw_packets / "psalms-23.json",
        ROOT / "src/psalm_engine/review_specs/psalms-23.json",
        ROOT / "resources",
    )


def test_items_join_footnotes_and_have_editable_defaults(packet):
    items = packet["items"]
    assert 10 < len(items) < 30
    assert all(i["category"] and i["summary"] and i["references"] for i in items)
    assert all(i["reviewer_status"] == "pending" for i in items)
    assert not any(i["title"].strip().isdigit() for i in items)
    assert set(packet["units"]["n12"]["passage_ids"])
    assert packet["units"]["n12"]["page"] == 22
    assert "Left-dislocation" in packet["units"]["n12"]["text"]
    assert any("n12" in i["support"] and "Ps 23:4" in i["references"] for i in items)
    assert packet["units"]["n2"]["label"] == "Footnote 2 (printed 22)"
    assert len(packet["coverage"]) == 71  # All old fragments accounted for, not review cards.


def test_workflow_export_is_scoped_and_detects_changes(packet, tmp_path):
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet))
    from psalm_engine.review_items import decision_envelope

    item = next(i for i in packet["items"] if "n12" in i["support"])
    decision = {
        k: item[k] for k in ["id", "item_sha256", "category", "kind", "summary", "alternatives"]
    }
    decision.update(
        status="approved", reviewer="Synthetic test reviewer", notes="Synthetic test only"
    )
    envelope = decision_envelope(packet_path, [decision])
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(envelope))
    export_item_review(packet_path, path, 23, tmp_path / "export")
    text = (tmp_path / "export/annotations.jsonl").read_text()
    claim = json.loads(text)
    assert claim["value"] == item["summary"]
    assert any(e["page"] == 22 and "Footnote 12" in e["locator"] for e in claim["evidence"])
    assert "Left-dislocation" not in text  # Raw source note is not copied into the prompt claim.
    envelope["decisions"][0]["status"] = "pending"
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError):
        export_item_review(packet_path, path, 23, tmp_path / "pending")
    envelope["decisions"][0]["status"] = "approved"
    envelope["decisions"][0]["item_sha256"] = "0" * 64
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="changed"):
        export_item_review(packet_path, path, 23, tmp_path / "changed")


def test_render_has_save_restore_and_categories(packet, tmp_path):
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet))
    render_item_review(packet_path, tmp_path / "index.html")
    text = (tmp_path / "index.html").read_text()
    assert "Save work" in text and "Load work" in text
    assert "Category" in text and "imagery" in text
    assert "Footnote 12" in text
    assert "image" in text and "Export decisions" in text


@pytest.mark.parametrize("guide", ["1", "23", "133", "42-43"])
def test_all_image_guides_have_complete_note_and_image_coverage(guide, raw_packets):
    packet = build_item_packet(
        raw_packets / f"psalms-{guide}.json",
        ROOT / f"src/psalm_engine/review_specs/psalms-{guide}.json",
        ROOT / "resources",
    )
    supports = {u for i in packet["items"] for u in i["support"]}
    notes = {u for u in packet["units"] if u.startswith("n")}
    assert notes <= supports | set(packet["context_note_ids"])
    assert set(map(int, packet["page_images"])) == {u["page"] for u in packet["units"].values()}
    assert all(row["classification"] in {"support", "context"} for row in packet["coverage"])
    if guide == "42-43":
        assert any(i["psalms"] == [43] for i in packet["items"])
        assert all(u["section"] == "Appendix B" for u in packet["units"].values())


def test_export_keeps_psalm_applicability_and_allows_context_only(raw_packets, tmp_path):
    from psalm_engine.guide_review import export_review
    from psalm_engine.review_items import decision_envelope

    packet = build_item_packet(
        raw_packets / "psalms-42-43.json",
        ROOT / "src/psalm_engine/review_specs/psalms-42-43.json",
        ROOT / "resources",
    )
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet))
    selected = [next(i for i in packet["items"] if i["psalms"] == [p]) for p in [42, 43]]
    decisions = []
    for item in selected:
        d = {
            k: item[k] for k in ["id", "item_sha256", "category", "kind", "summary", "alternatives"]
        }
        d.update(
            status="approved", reviewer="Synthetic scope test reviewer", notes="Synthetic test only"
        )
        decisions.append(d)
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(decision_envelope(packet_path, decisions)))
    export_review(packet_path, path, 43, tmp_path / "ps43")
    claims = [
        json.loads(line) for line in (tmp_path / "ps43/annotations.jsonl").read_text().splitlines()
    ]
    assert len(claims) == 1
    assert claims[0]["applicable_psalms"] == [43]
    assert claims[0]["value"] == selected[1]["summary"]
    for decision in decisions:
        decision["status"] = "context"
    path.write_text(json.dumps(decision_envelope(packet_path, decisions)))
    export_review(packet_path, path, 43, tmp_path / "context")
    assert (tmp_path / "context/annotations.jsonl").read_text() == ""
    assert (tmp_path / "context/review-provenance.json").is_file()
