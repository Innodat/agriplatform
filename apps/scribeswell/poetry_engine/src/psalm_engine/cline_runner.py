"""Cline 3 command adapter. Credentials remain in Cline's authentication store."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .experiment import check_response
from .guide_scope import validate_request_scope
from .models import GenerationRequest, GenerationResponse

TRANSPORT_INSTRUCTIONS = """
This is a self-contained translation experiment, not a coding task.
Use only the supplied request evidence. Do not inspect files, browse, invoke tools,
delegate, or retrieve previous conversations. Return exactly one JSON object matching
response_schema, without markdown fences or surrounding prose. Produce one complete
Psalm draft, retaining verse order. Do not claim human approval. Set usage to null;
the transport records usage if available. Complete using submit_and_exit with
summary containing exactly the final JSON and verified=false. No other tools are
permitted, including team_status, team tasks, skills or filesystem inspection.
The response is consumed by a JSON parser: the first character must be { and the
last character must be }. Do not wrap JSON in Markdown. Every item in candidates[].lines
must be a nonempty verse line. Do not insert empty strings or whitespace-only lines
for stanza spacing. Use the exact field names in response_schema; no additional fields.
"""


def tool_control(payload: dict) -> dict:
    name = payload.get("tool_call", {}).get("name") or payload.get("preToolUse", {}).get("toolName")
    if name == "submit_and_exit":
        return {}
    return {"cancel": True, "errorMessage": "Translation experiment forbids external tools."}


def extract_response(output: str, request: GenerationRequest) -> GenerationResponse:
    """Accept only a completed run, never partial text or an echoed request."""
    completed = []
    usage = None
    for line in output.splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise TypeError("Invalid Cline event")
        if row.get("type") == "error":
            raise ValueError("Cline reported an error")
        if row.get("type") == "run_result":
            if row.get("finishReason") != "completed":
                raise ValueError("Cline did not complete the translation")
            model = row.get("model", {})
            if model.get("id") != request.model or model.get("provider") != request.provider:
                raise ValueError("Cline runtime provider/model differs from the request")
            completed.append(row.get("text", ""))
            counts = row.get("aggregateUsage", row.get("usage"))
            keys = ("inputTokens", "outputTokens")
            if isinstance(counts, dict) and all(
                type(counts.get(k)) is int and counts[k] >= 0 for k in keys
            ):
                usage = {k: counts[k] for k in keys}
        if row.get("type") != "agent_event":
            continue
        event = row.get("event", {})
        if event.get("type") == "error":
            raise ValueError("Cline reported an agent error")
        if event.get("contentType") == "tool" and event.get("toolName") != "submit_and_exit":
            raise ValueError("Cline attempted a forbidden tool; discard this condition")
        if event.get("type") == "done" and event.get("reason") != "completed":
            raise ValueError("Cline did not complete the translation")
    if len(completed) != 1:
        raise ValueError("Expected exactly one completed Cline response")
    response = GenerationResponse.model_validate_json(completed[0])
    response.usage = usage  # Never trust token counts composed by the model.
    check_response(request, response, synthetic=False)
    return response


def generate(request: GenerationRequest, executable: str = "cline") -> GenerationResponse:
    validate_request_scope(request)
    if request.provider != "cline":
        raise ValueError("This adapter requires provider cline")
    if request.settings:
        raise ValueError("Cline adapter supports default settings ({}) only")
    with tempfile.TemporaryDirectory(prefix="psalm-cline-") as directory:
        root = Path(directory)
        work = root / "work"
        work.mkdir()
        hooks = work / ".cline" / "hooks"
        hooks.mkdir(parents=True)
        hook = hooks / "PreToolUse"
        hook_trace = root / "tool-policy.jsonl"
        # Use this interpreter directly; do not depend on Cline's Python PATH.
        hook.write_text(
            f"#!{sys.executable}\nimport json,sys\n"
            "from psalm_engine.cline_runner import tool_control\n"
            "p=json.load(sys.stdin)\n"
            "n=p.get('tool_call',{}).get('name') or "
            "p.get('preToolUse',{}).get('toolName')\n"
            f"with open({str(hook_trace)!r},'a') as f: "
            "f.write(json.dumps({'name':n})+'\\n')\n"
            "print(json.dumps(tool_control(p)))\n"
        )
        hook.chmod(0o700)
        command = [
            executable,
            "--json",
            "--provider",
            request.provider,
            "--model",
            request.model,
            "--auto-approve",
            "true",
            "--compaction",
            "off",
            "--retries",
            "1",
            "--timeout",
            "240",
            "--cwd",
            str(work),
            "--hooks-dir",
            str(hooks),
            "--system",
            request.system + TRANSPORT_INSTRUCTIONS,
            "--",
            request.model_dump_json(),
        ]
        env = dict(os.environ)
        # --data-dir also replaces the credential store, causing unauthenticated
        # requests. Keep native authentication while isolating mutable run state.
        env["CLINE_PROVIDER_SETTINGS_PATH"] = env.get(
            "CLINE_PROVIDER_SETTINGS_PATH",
            str(Path.home() / ".cline" / "data" / "settings" / "providers.json"),
        )
        env.pop("CLINE_SANDBOX", None)
        env.pop("CLINE_SANDBOX_DATA_DIR", None)
        env["CLINE_DATA_DIR"] = str(root / "state")
        for name, subdir in (
            ("CLINE_DB_DATA_DIR", "db"),
            ("CLINE_SESSION_DATA_DIR", "sessions"),
            ("CLINE_TEAM_DATA_DIR", "teams"),
        ):
            env[name] = str(root / "state" / subdir)
        env["CLINE_HOOKS_LOG_PATH"] = str(root / "state" / "logs" / "hooks.jsonl")
        env["CLINE_SESSION_BACKEND_MODE"] = "local"
        try:
            result = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                text=True,
                capture_output=True,
                timeout=270,
                cwd=work,
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Cline timed out; prepare a new experiment attempt") from None
        if result.returncode:
            raise RuntimeError(f"Cline exited with code {result.returncode}")
        if hook_trace.exists() and any(
            json.loads(line).get("name") != "submit_and_exit"
            for line in hook_trace.read_text().splitlines()
        ):
            raise ValueError("Cline attempted a forbidden tool; discard this condition")
        return extract_response(result.stdout, request)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cline", default="cline")
    parser.add_argument("--expected-version", default="3.0.61")
    parser.add_argument("--provenance-dir", type=Path)
    args = parser.parse_args()
    try:
        version = subprocess.run(
            [args.cline, "--version"], capture_output=True, text=True, timeout=20, check=True
        ).stdout.strip()
        if version != args.expected_version:
            raise ValueError("Cline version changed; validate the transport before using it")
        request = GenerationRequest.model_validate_json(sys.stdin.read())
        if args.provenance_dir:
            args.provenance_dir.mkdir(parents=True, exist_ok=True)
            # request_id is model data; never use it as a filesystem path.
            from hashlib import sha256

            name = sha256(request.request_id.encode()).hexdigest()
            with (args.provenance_dir / f"{name}.cline.json").open("x") as f:
                json.dump(
                    {
                        "request_id": request.request_id,
                        "cline_version": version,
                        "provider": request.provider,
                        "model": request.model,
                        "settings": request.settings,
                        "compaction": "off",
                        "system_suffix": TRANSPORT_INSTRUCTIONS,
                        "timeout_seconds": 240,
                        "tool_policy": "deny all except submit_and_exit",
                        "model_verification": "CLI selection, runtime result and response identity",
                    },
                    f,
                    indent=2,
                )
        print(generate(request, args.cline).model_dump_json())
    except (ValueError, TypeError, RuntimeError, OSError, subprocess.SubprocessError) as error:
        # Provider stderr, validation errors and command arguments can contain secrets/input.
        print(
            f"Cline adapter failed ({type(error).__name__}); no valid translation returned.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
