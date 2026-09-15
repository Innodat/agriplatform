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


def test_representation_rejects_analysis_for_another_psalm():
    rep = representation()
    rep.claims.append(
        Claim(
            id="synthetic-psalm1",
            category="test",
            value="SYNTHETIC TEST ONLY",
            method="rule",
            applicable_psalms=[1],
            evidence=[Evidence(source_id="morphhb", locator="synthetic")],
        )
    )
    with pytest.raises(ValueError, match="not applicable"):
        CanonicalPsalmRepresentation.model_validate(rep.model_dump())


def test_complete_synthetic_run_records_comparison_and_rejects_overwrite(tmp_path):
    from psalm_engine.models import Candidate, DecisionNote, GenerationResponse

    class SyntheticGenerator:
        def generate(self, request):
            return GenerationResponse(
                request_id=request.request_id,
                provider=request.provider,
                model=request.model,
                language=request.language,
                mode=request.mode,
                settings=request.settings,
                candidates=[
                    Candidate(
                        id="synthetic-1",
                        lines=["SYNTHETIC STRUCTURAL TEST ONLY"],
                        notes=[
                            DecisionNote(note="SYNTHETIC decision note", evidence_refs=["Ps.23.1"])
                        ],
                    )
                ],
                synthetic=True,
            )

    run = prepare_experiment(representation(), tmp_path, ["A", "B", "C"], "test", "test")
    run_experiment(run, SyntheticGenerator())
    assert "SYNTHETIC TEST OUTPUT" in (run / "comparison.md").read_text()
    assert "SYNTHETIC decision note (Ps.23.1)" in (run / "comparison.md").read_text()
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


def test_d_includes_approved_pdf_analysis_but_never_pending_or_unpaged(tmp_path):
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
    base = Claim(
        id="principle",
        category="poetry",
        value="SYNTHETIC PRINCIPLE",
        method="human",
        reviewer_status="approved",
        reviewer="Synthetic test reviewer",
        evidence=[Evidence(source_id="pdf:test", locator="synthetic", page=1)],
    )
    rep.principles.append(base)
    rep.claims.extend(
        [
            base.model_copy(update={"id": "analysis", "value": "SYNTHETIC APPROVED ANALYSIS"}),
            base.model_copy(
                update={
                    "id": "pending",
                    "value": "SYNTHETIC PENDING ANALYSIS",
                    "method": "llm",
                    "reviewer_status": "pending",
                }
            ),
            base.model_copy(
                update={
                    "id": "unpaged",
                    "value": "SYNTHETIC UNPAGED ANALYSIS",
                    "evidence": [Evidence(source_id="pdf:test", locator="unknown")],
                }
            ),
        ]
    )
    run = prepare_experiment(rep, tmp_path, ["A", "B", "C", "D"], "test", "test")
    for c in "ABC":
        assert "SYNTHETIC APPROVED ANALYSIS" not in (run / f"{c}.request.json").read_text()
    d = json.loads((run / "D.request.json").read_text())
    assert [c["id"] for c in d["input"]["representation"]["claims"]] == ["analysis"]
    assert "analysis" in d["input"]["allowed_evidence_refs"]


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


def test_psalm_guide_step_approval_cannot_enter_d(tmp_path):
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    legacy = Claim.model_validate_json(
        (root / "data/annotations/principles.reviewed-v2.jsonl").read_text()
    )
    rep = representation()
    rep.sources.append(
        Source(
            id=legacy.evidence[0].source_id,
            dataset="psalms-23.pdf",
            revision="test",
            sha256=legacy.evidence[0].source_id.removeprefix("pdf:"),
            uri=str(root / "resources/psalms-23.pdf"),
            license="local research",
        )
    )
    rep.principles.append(legacy)
    with pytest.raises(ValueError, match="reviewed PDF"):
        prepare_experiment(rep, tmp_path, ["D"], "test", "test")
    allowed = legacy.model_copy(deep=True)
    allowed.id = "synthetic-appendix-b"
    allowed.value = "SYNTHETIC APPENDIX B CLAIM"
    allowed.evidence[0].page = 20
    allowed.evidence[0].locator = "Synthetic test: Appendix B page 20"
    rep.principles.append(allowed)
    rep.claims.extend([legacy, allowed])
    mixed = allowed.model_copy(deep=True)
    mixed.id = "synthetic-mixed-sections"
    mixed.value = "SYNTHETIC MIXED SECTION CLAIM"
    mixed.evidence.extend(legacy.evidence)
    rep.principles.append(mixed)
    rep.claims.append(mixed)
    run = prepare_experiment(rep, tmp_path, ["D"], "test", "test")
    request = json.loads((run / "D.request.json").read_text())
    assert legacy.value not in json.dumps(request)
    assert allowed.value in json.dumps(request)
    assert mixed.value not in json.dumps(request)
    assert legacy.id not in request["input"]["allowed_evidence_refs"]
    assert set(json.loads((run / "manifest.json").read_text())["excluded_pdf_claim_ids"]) == {
        legacy.id,
        mixed.id,
    }

    # Simulate an intact old prepared request, including its recorded checksum.
    from psalm_engine.storage import digest

    request["input"]["representation"]["principles"].append(legacy.model_dump(mode="json"))
    request_path = run / "D.request.json"
    request_path.write_text(json.dumps(request))
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["request_hashes"]["D"] = digest(request_path)
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="violates Appendix B/C"):
        run_experiment(run, None)
    assert not (run / "execution.json").exists()

    from psalm_engine.cline_runner import generate
    from psalm_engine.generation import CommandGenerator
    from psalm_engine.models import GenerationRequest

    obsolete = GenerationRequest.model_validate(request)
    with pytest.raises(ValueError, match="violates Appendix B/C"):
        CommandGenerator(["must-not-execute"]).generate(obsolete)
    with pytest.raises(ValueError, match="violates Appendix B/C"):
        generate(obsolete, "must-not-execute")
