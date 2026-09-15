"""Recover this interrupted Psalm 23 run into a new, explicitly linked directory."""

import json
import shutil
import subprocess
import time
from pathlib import Path
from uuid import uuid4

from psalm_engine import cline_runner
from psalm_engine.evaluation import CATEGORIES
from psalm_engine.experiment import check_response
from psalm_engine.models import GenerationRequest, GenerationResponse, now
from psalm_engine.storage import code_revision, digest, write_json


def main():
    root = Path(__file__).resolve().parents[1]
    source = root / "runs/psalm-023-8613c860-d8e6-4c52-a60e-ba6948f59d1d"
    manifest = json.loads((source / "manifest.json").read_text())
    assert digest(source / "representation.json") == manifest["representation_sha256"]
    requests = {}
    for condition in manifest["conditions"]:
        path = source / f"{condition}.request.json"
        assert digest(path) == manifest["request_hashes"][condition]
        requests[condition] = GenerationRequest.model_validate_json(path.read_text())
    response = GenerationResponse.model_validate_json((source / "A.response.json").read_text())
    check_response(requests["A"], response, synthetic=False)
    saved = json.loads((source / "A.result.json").read_text())
    assert saved["response"] == response.model_dump(mode="json")
    provenance = json.loads((source / "A.cline.json").read_text())
    assert provenance["system_suffix"] == cline_runner.TRANSPORT_INSTRUCTIONS
    assert provenance["adapter_sha256"] == digest(Path(cline_runner.__file__))
    version = subprocess.run(["cline", "--version"], capture_output=True, text=True,
                             check=True, timeout=20).stdout.strip()
    assert version == provenance["cline_version"] == "3.0.61"
    run = root / "runs" / f"psalm-023-recovery-{uuid4()}"
    run.mkdir()
    for name in ["representation.json", "A.request.json", "B.request.json", "C.request.json",
                 "A.response.json", "A.result.json", "A.cline.json"]:
        shutil.copyfile(source / name, run / name)
    manifest["experiment_id"] = run.name
    manifest["recovered_from"] = source.name
    write_json(run / "manifest.json", manifest)
    write_json(run / "execution.json", {
        "started_at": now().isoformat(), "code": code_revision(),
        "recovered_from": source.name, "reused_conditions": ["A"],
        "original_execution": json.loads((source / "execution.json").read_text()),
        "recovery_reason": "Terminal crash; B artifacts are empty and C is absent.",
    })
    print(f"Recovery directory: {run}", flush=True)
    results = [saved]
    try:
        for condition in ["B", "C"]:
            request = requests[condition]
            write_json(run / f"{condition}.cline.json", {
                "cline_version": version, "condition": condition,
                "request_id": request.request_id, "provider": request.provider,
                "model": request.model, "settings": request.settings,
                "system_suffix": cline_runner.TRANSPORT_INSTRUCTIONS,
                "adapter_sha256": digest(Path(cline_runner.__file__)),
                "tool_policy": "deny all except submit_and_exit",
            })
            print(f"Generating {condition}", flush=True)
            started = time.monotonic()
            response = cline_runner.generate(request)
            elapsed = time.monotonic() - started
            check_response(request, response, synthetic=False)
            write_json(run / f"{condition}.response.json", response)
            record = {"condition": condition, "latency_seconds": elapsed,
                      "completed_at": now().isoformat(),
                      "response": response.model_dump(mode="json")}
            write_json(run / f"{condition}.result.json", record)
            results.append(record)
            print(f"Validated {condition} ({elapsed:.1f}s)", flush=True)
    except Exception as error:
        write_json(run / "status.json", {"status": "failed", "error_type": type(error).__name__,
                                         "completed_conditions": [r["condition"] for r in results]})
        raise
    write_json(run / "results.json", results)
    report = ["# Psalm 23 draft comparison", "",
              "Draft translations; awaiting human evaluation.", "",
              f"Recovery of `{source.name}`. A is reused with its original timing; B and C are new.", ""]
    forms = []
    for result in results:
        data = result["response"]
        report.extend([f"## Condition {result['condition']}", "",
                       f"Model: {data['provider']} / {data['model']}", ""])
        for candidate in data["candidates"]:
            report.extend([f"### Candidate {candidate['id']}", "", *candidate["lines"], "",
                           "Decision notes:", ""])
            report.extend(f"- {n['note']} ({', '.join(n['evidence_refs'])})" for n in candidate["notes"])
            report.extend(["", "Losses: " + "; ".join(candidate["losses"]),
                           "Uncertainty: " + "; ".join(candidate["uncertainty"]), ""])
            forms.append({"request_id": data["request_id"], "candidate_id": candidate["id"],
                          "reviewer": "", "role": "", "scores": dict.fromkeys(CATEGORIES),
                          "comments": "", "translator_revision": ""})
    with (run / "comparison.md").open("x") as stream:
        stream.write("\n".join(report))
    write_json(run / "evaluation-template.json", forms)
    write_json(run / "status.json", {"status": "generated; awaiting human evaluation"})
    print(f"Completed: {run / 'comparison.md'}", flush=True)


if __name__ == "__main__":
    main()
