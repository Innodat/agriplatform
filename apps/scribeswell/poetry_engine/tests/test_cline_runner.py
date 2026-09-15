"""Cline transport acceptance tests; all model text here is synthetic."""

import json
import subprocess

import pytest

from psalm_engine.cline_runner import extract_response, generate, tool_control
from psalm_engine.models import GenerationRequest, GenerationResponse


@pytest.fixture
def generation_request():
    return GenerationRequest(
        provider="cline",
        model="anthropic/claude-sonnet-5",
        language="af",
        mode="poetic",
        condition="A",
        system="Translate only supplied evidence.",
        input={"allowed_evidence_refs": ["Ps.23.1"]},
        response_schema=GenerationResponse.model_json_schema(),
    )


def stream(generation_request, **changes):
    response = {
        k: getattr(generation_request, k)
        for k in ("request_id", "provider", "model", "language", "mode", "settings")
    }
    response.update(candidates=[{"id": "a", "lines": ["SYNTHETIC TRANSPORT TEST"]}])
    response.update(changes)
    return json.dumps(
        {
            "type": "run_result",
            "finishReason": "completed",
            "text": json.dumps(response),
            "model": {"id": generation_request.model, "provider": generation_request.provider},
            "usage": {"inputTokens": 123, "outputTokens": 45},
        }
    )


def test_completed_response_ignores_partial_text_and_unverified_usage(generation_request):
    partial = json.dumps(
        {
            "type": "agent_event",
            "event": {"type": "content_start", "contentType": "text", "text": "incomplete"},
        }
    )
    response = extract_response(
        partial + "\n" + stream(generation_request, usage={"tokens": 999}), generation_request
    )
    assert response.candidates[0].lines == ["SYNTHETIC TRANSPORT TEST"]
    assert response.usage == {"inputTokens": 123, "outputTokens": 45}


def test_runtime_model_mismatch_fails_even_when_model_echoes_request(generation_request):
    event = json.loads(stream(generation_request))
    event["model"]["id"] = "different-backend-model"
    with pytest.raises(ValueError, match="model"):
        extract_response(json.dumps(event), generation_request)


def test_missing_runtime_usage_is_not_invented(generation_request):
    event = json.loads(stream(generation_request, usage={"tokens": 999}))
    del event["usage"]
    assert extract_response(json.dumps(event), generation_request).usage is None


def test_partial_done_without_terminal_result_is_rejected(generation_request):
    event = json.loads(stream(generation_request))
    output = json.dumps(
        {
            "type": "agent_event",
            "event": {
                "type": "done",
                "reason": "completed",
                "text": event["text"],
            },
        }
    )
    with pytest.raises(ValueError):
        extract_response(output, generation_request)


@pytest.mark.parametrize(
    "change",
    [
        {"model": "another-model"},
        {"provider": "anthropic"},
        {"settings": {"temperature": 1}},
        {
            "candidates": [
                {
                    "id": "a",
                    "lines": ["test"],
                    "notes": [{"note": "test", "evidence_refs": ["UNSUPPLIED"]}],
                }
            ]
        },
    ],
)
def test_mismatches_and_invented_evidence_fail(generation_request, change):
    with pytest.raises(ValueError):
        extract_response(stream(generation_request, **change), generation_request)


@pytest.mark.parametrize(
    "output",
    [
        "not json",
        "{}",
        '{"type":"error"}',
        '{"type":"agent_event","event":{"type":"done","reason":"aborted","text":"{}"}}',
    ],
)
def test_incomplete_or_malformed_stream_fails(generation_request, output):
    with pytest.raises(ValueError):
        extract_response(output, generation_request)


def test_tools_are_rejected_even_if_followed_by_valid_response(generation_request):
    event = json.dumps(
        {
            "type": "agent_event",
            "event": {"type": "content_start", "contentType": "tool", "toolName": "read_file"},
        }
    )
    with pytest.raises(ValueError, match="tool"):
        extract_response(event + "\n" + stream(generation_request), generation_request)
    assert tool_control({"tool_call": {"name": "read_file"}})["cancel"] is True
    assert tool_control({"tool_call": {"name": "submit_and_exit"}}) == {}
    assert tool_control({})["cancel"] is True


def test_fresh_tasks_use_isolated_directories_and_explicit_model(generation_request, monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stream(generation_request), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    generate(generation_request)
    generate(generation_request)
    first, second = calls
    assert first[1]["cwd"] != second[1]["cwd"]
    assert "--id" not in first[0]
    assert first[0][first[0].index("--model") + 1] == generation_request.model
    assert first[0][first[0].index("--provider") + 1] == "cline"
    assert first[0][first[0].index("--auto-approve") + 1] == "true"
    assert first[1]["stdin"] == subprocess.DEVNULL
    assert first[0][-1] == generation_request.model_dump_json()
    assert "--data-dir" not in first[0]
    assert first[1]["env"]["CLINE_SESSION_DATA_DIR"] != second[1]["env"]["CLINE_SESSION_DATA_DIR"]
    assert (
        first[1]["env"]["CLINE_PROVIDER_SETTINGS_PATH"]
        == second[1]["env"]["CLINE_PROVIDER_SETTINGS_PATH"]
    )


def test_nonzero_exit_is_sanitized(generation_request, monkeypatch):
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "secret", "secret")
    )
    with pytest.raises(RuntimeError, match="Cline exited") as error:
        generate(generation_request)
    assert "secret" not in str(error.value)


def test_timeout_is_sanitized(generation_request, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("secret", 240)

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="timed out"):
        generate(generation_request)


def test_unsupported_settings_fail_before_generation(generation_request, monkeypatch):
    generation_request.settings = {"temperature": 0.3}
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: pytest.fail("must not run"))
    with pytest.raises(ValueError, match="settings"):
        generate(generation_request)


def test_response_schema_forbids_blank_poetry_lines():
    item = GenerationResponse.model_json_schema()["$defs"]["Candidate"]["properties"]["lines"][
        "items"
    ]
    assert item["minLength"] == 1
    assert item["pattern"] == r"\S"


@pytest.mark.parametrize("tool", ["submit_and_exit", "read_files"])
def test_installed_hook_controls_tools_in_isolated_directory(generation_request, monkeypatch, tool):
    from pathlib import Path

    real_run = subprocess.run

    def fake_cline(command, **kwargs):
        hook = Path(command[command.index("--hooks-dir") + 1]) / "PreToolUse"
        result = real_run(
            [str(hook)],
            input=json.dumps({"tool_call": {"name": tool}}),
            capture_output=True,
            text=True,
            cwd=kwargs["cwd"],
            check=True,
        )
        assert json.loads(result.stdout) == tool_control({"tool_call": {"name": tool}})
        return subprocess.CompletedProcess(command, 0, stream(generation_request), "")

    monkeypatch.setattr(subprocess, "run", fake_cline)
    if tool == "submit_and_exit":
        generate(generation_request)
    else:
        with pytest.raises(ValueError, match="forbidden tool"):
            generate(generation_request)
