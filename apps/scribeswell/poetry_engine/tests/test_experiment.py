"""Synthetic structural tests, never translation-quality evidence."""

import json

import pytest

from psalm_engine.alignment import align_tokens
from psalm_engine.experiment import prepare_experiment, run_experiment
from psalm_engine.models import CanonicalPsalmRepresentation, Claim, Evidence, Source, Token


def representation():
    sources = [
        Source(
            id=s,
            dataset=s,
            revision="synthetic-test",
            sha256="0" * 64,
            uri="synthetic:test",
            license="synthetic",
        )
        for s in ("morphhb", "bhsa")
    ]
    tokens = [
        Token(
            id="m1", source_id="morphhb", verse=1, position=1, surface="אב", morphology="synthetic"
        ),
        Token(id="b1", source_id="bhsa", verse=1, position=1, surface="א"),
        Token(id="b2", source_id="bhsa", verse=1, position=2, surface="ב"),
    ]
    return CanonicalPsalmRepresentation(
        psalm=23,
        sources=sources,
        tokens=tokens,
        alignments=align_tokens(tokens[:1], tokens[1:]),
        synthetic=True,
    )


def test_alignment_preserves_split_and_unmatched_tokens():
    rep = representation()
    assert rep.alignments[0].left_ids == ["m1"]
    assert rep.alignments[0].right_ids == ["b1", "b2"]
    extra = Token(id="b3", source_id="bhsa", verse=2, position=1, surface="ג")
    aligned = align_tokens(rep.tokens[:1], rep.tokens[1:] + [extra])
    assert aligned[-1].status == "unmatched"
    assert aligned[-1].right_ids == ["b3"]


def test_conditions_do_not_leak_assisted_evidence_into_baseline(tmp_path):
    rep = representation()
    run = prepare_experiment(
        rep, tmp_path, conditions=["A", "B", "C"], provider="test", model="test"
    )
    a = json.loads((run / "A.request.json").read_text())
    c = json.loads((run / "C.request.json").read_text())
    assert "morphology" not in json.dumps(a["input"])
    assert "representation" in c["input"]
    assert not (run / "results.json").exists()


def test_condition_d_requires_actual_human_review(tmp_path):
    rep = representation()
    with pytest.raises(ValueError, match="reviewed PDF"):
        prepare_experiment(rep, tmp_path, conditions=["D"], provider="test", model="test")
    with pytest.raises(ValueError, match="reviewer"):
        Claim(
            id="x",
            category="metaphor",
            value="synthetic",
            method="human",
            reviewer_status="approved",
            evidence=[Evidence(source_id="morphhb", locator="test")],
        )


def test_generation_failure_is_not_reported_as_completed(tmp_path):
    run = prepare_experiment(
        representation(), tmp_path, conditions=["A", "C"], provider="test", model="test"
    )

    class Broken:
        def generate(self, request):
            raise RuntimeError("provider failed")

    with pytest.raises(RuntimeError, match="provider failed"):
        run_experiment(run, Broken())
    assert json.loads((run / "status.json").read_text())["status"] == "failed"
    assert not (run / "comparison.md").exists()


def test_representation_rejects_unaccounted_token():
    rep = representation().model_dump()
    rep["alignments"] = []
    with pytest.raises(ValueError, match="alignment"):
        CanonicalPsalmRepresentation.model_validate(rep)


def test_complete_synthetic_run_records_comparison_and_rejects_overwrite(tmp_path):
    from psalm_engine.models import Candidate, GenerationResponse

    class SyntheticGenerator:
        def generate(self, request):
            return GenerationResponse(
                request_id=request.request_id,
                provider=request.provider,
                model=request.model,
                language=request.language,
                mode=request.mode,
                settings=request.settings,
                candidates=[Candidate(id="synthetic-1", lines=["SYNTHETIC STRUCTURAL TEST ONLY"])],
                synthetic=True,
            )

    run = prepare_experiment(representation(), tmp_path, ["A", "B", "C"], "test", "test")
    run_experiment(run, SyntheticGenerator())
    assert "SYNTHETIC TEST OUTPUT" in (run / "comparison.md").read_text()
    assert len(json.loads((run / "results.json").read_text())) == 3
    assert (
        json.loads((run / "evaluation-template.json").read_text())[0]["scores"]["imagery"] is None
    )
    with pytest.raises(FileExistsError):
        run_experiment(run, SyntheticGenerator())


def test_changed_request_cannot_be_generated(tmp_path):
    run = prepare_experiment(representation(), tmp_path, ["A"], "test", "test")
    (run / "A.request.json").write_text("{}")
    with pytest.raises(ValueError, match="Request changed"):
        run_experiment(run, None)


def test_pdf_claims_and_principles_are_absent_from_c(tmp_path):
    rep = representation()
    rep.sources.append(
        Source(
            id="pdf:test",
            dataset="synthetic",
            revision="test",
            sha256="0" * 64,
            uri="synthetic:test",
            license="synthetic",
        )
    )
    claim = Claim(
        id="principle",
        category="poetry",
        value="UNIQUE_PDF_DERIVED_VALUE",
        method="human",
        reviewer_status="approved",
        reviewer="Synthetic test reviewer",
        evidence=[Evidence(source_id="pdf:test", locator="synthetic", page=1)],
    )
    rep.claims.append(claim)
    rep.principles.append(claim)
    run = prepare_experiment(rep, tmp_path, ["C", "D"], "test", "test")
    assert "UNIQUE_PDF_DERIVED_VALUE" not in (run / "C.request.json").read_text()
    assert "UNIQUE_PDF_DERIVED_VALUE" in (run / "D.request.json").read_text()


def test_rubric_requires_all_scores_and_keeps_categories():
    from psalm_engine.evaluation import CATEGORIES, Evaluation

    with pytest.raises(ValueError):
        Evaluation(
            request_id="r",
            candidate_id="c",
            reviewer="Synthetic test reviewer",
            role="test",
            scores={},
        )
    evaluation = Evaluation(
        request_id="r",
        candidate_id="c",
        reviewer="Synthetic test reviewer",
        role="test",
        scores=dict.fromkeys(CATEGORIES, 4),
    )
    assert evaluation.weighted_score() == 4
    assert len(evaluation.scores) == 12


def test_note_cannot_cite_evidence_absent_from_baseline(tmp_path):
    from psalm_engine.experiment import check_response
    from psalm_engine.models import Candidate, DecisionNote, GenerationRequest, GenerationResponse

    run = prepare_experiment(representation(), tmp_path, ["A"], "test", "test")
    request = GenerationRequest.model_validate_json((run / "A.request.json").read_text())
    response = GenerationResponse(
        request_id=request.request_id,
        provider="test",
        model="test",
        language="af",
        mode="poetic",
        settings={},
        synthetic=True,
        candidates=[
            Candidate(
                id="c",
                lines=["synthetic"],
                notes=[DecisionNote(note="synthetic", evidence_refs=["b1"])],
            )
        ],
    )
    with pytest.raises(ValueError, match="absent"):
        check_response(request, response, True)


def test_empty_surface_requires_explicit_source_annotation():
    with pytest.raises(ValueError, match="explicitly"):
        Token(id="x", source_id="bhsa", verse=1, position=1, surface="")
    token = Token(
        id="x", source_id="bhsa", verse=1, position=1, surface="", surface_status="source_empty"
    )
    assert token.surface_status == "source_empty"


def test_false_alignment_is_rejected():
    rep = representation().model_dump()
    rep["tokens"][0]["surface"] = "ג"
    with pytest.raises(ValueError, match="does not match"):
        CanonicalPsalmRepresentation.model_validate(rep)


def test_command_provider_runs_complete_structural_experiment(tmp_path):
    import sys

    from psalm_engine.generation import CommandGenerator

    runner = tmp_path / "synthetic_runner.py"
    runner.write_text("""import json,sys
r=json.load(sys.stdin)
response={k:r[k] for k in ['request_id','provider','model','language','mode','settings']}
response.update(synthetic=True,candidates=[{'id':'test','lines':['SYNTHETIC TEST ONLY']}])
print(json.dumps(response))
""")
    run = prepare_experiment(
        representation(), tmp_path, ["A", "C"], "synthetic-test", "synthetic-test"
    )
    run_experiment(run, CommandGenerator([sys.executable, str(runner)]))
    assert (run / "comparison.md").exists()
    assert (
        json.loads((run / "status.json").read_text())["status"]
        == "generated; awaiting human evaluation"
    )
