"""Provider-independent structured generation interface."""

import json
import subprocess
from typing import Protocol

from .models import GenerationRequest, GenerationResponse


class TranslationGenerator(Protocol):
    def generate(self, request: GenerationRequest) -> GenerationResponse: ...


class CommandGenerator:
    """Runner consumes one request JSON on stdin and emits one response JSON.

    Credentials stay in the runner's environment. No shell interpolation. A nonzero
    exit, timeout or invalid output is a failed experiment, never an empty candidate.
    """

    def __init__(self, command: list[str], timeout: int = 300):
        if not command:
            raise ValueError("Provider command is required")
        self.command, self.timeout = command, timeout

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        completed = subprocess.run(
            self.command,
            input=request.model_dump_json(),
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        if completed.returncode:
            # Runner stderr may contain secrets; do not persist it in the experiment.
            raise RuntimeError(f"Provider runner exited with code {completed.returncode}")
        return GenerationResponse.model_validate(json.loads(completed.stdout))
