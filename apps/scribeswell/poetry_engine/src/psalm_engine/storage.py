"""Portable JSON artifacts; never overwrite representations or experiment evidence."""

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def code_revision() -> dict[str, str | bool]:
    root = Path(__file__).resolve().parent
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()
    )
    files = sorted(root.glob("*.py"))
    code_hash = hashlib.sha256("".join(p.name + digest(p) for p in files).encode()).hexdigest()
    return {"git_commit": commit, "working_tree_dirty": dirty, "engine_code_sha256": code_hash}
