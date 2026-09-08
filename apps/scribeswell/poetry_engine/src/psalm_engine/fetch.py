"""Explicit pinned download of the minimum BHSA Text-Fabric features."""

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

from .sources import BHSA_FEATURES
from .storage import write_json


def fetch_bhsa(output: Path, revision: str, version: str = "2021") -> None:
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("Use a full immutable BHSA git commit SHA")
    if not version.isdigit():
        raise ValueError("BHSA version must be a year")
    output.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in BHSA_FEATURES:
        url = f"https://raw.githubusercontent.com/ETCBC/bhsa/{revision}/tf/{version}/{name}.tf"
        with urlopen(
            Request(url, headers={"User-Agent": "Scribeswell-local-research"}), timeout=60
        ) as response:
            content = response.read()
        (output / f"{name}.tf").write_bytes(content)
        hashes[f"{name}.tf"] = hashlib.sha256(content).hexdigest()
    write_json(
        output / "source.json",
        {
            "dataset": "BHSA",
            "revision": revision,
            "version": version,
            "dataset_license": "CC-BY-NC-4.0",
            "license_url": "https://github.com/ETCBC/bhsa#license",
            "attribution": "ETCBC, VU Amsterdam; https://doi.org/10.17026/dans-z6y-skyh",
            "files": hashes,
        },
    )
