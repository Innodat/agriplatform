"""Real-source adapter checks plus synthetic malformed-input cases."""

from pathlib import Path

import pytest

from psalm_engine.alignment import align_tokens
from psalm_engine.models import CanonicalPsalmRepresentation
from psalm_engine.sources import load_bhsa, load_morphhb

ROOT = Path(__file__).resolve().parents[1]


def test_real_psalm_23_source_coverage():
    m, left, units = load_morphhb(
        ROOT / "data/raw/morphhb/Ps.xml", 23, "3d15126fb1ef74867fc1434be1942e837932691f"
    )
    b, right, extra = load_bhsa(ROOT / "data/raw/bhsa-2021", 23)
    rep = CanonicalPsalmRepresentation(
        psalm=23,
        sources=[m, b],
        tokens=left + right,
        units=units + extra,
        alignments=align_tokens(left, right),
    )
    assert len(left) == 57
    assert {t.verse for t in left} == {1, 2, 3, 4, 5, 6}
    assert {t.verse for t in right} == {1, 2, 3, 4, 5, 6}
    assert sum(len(a.left_ids) for a in rep.alignments) == len(left)
    assert sum(len(a.right_ids) for a in rep.alignments) == len(right)
    assert any(len(a.right_ids) > 1 for a in rep.alignments)


def test_morphhb_missing_source_id_fails(tmp_path):
    path = tmp_path / "synthetic.xml"
    path.write_text(
        '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace"><verse osisID="Ps.23.1"><w morph="HNcmsa">אב</w></verse></osis>'
    )
    with pytest.raises(ValueError, match="missing MorphHB ID"):
        load_morphhb(path, 23, "synthetic")
