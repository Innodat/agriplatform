"""Checksum-pinned section boundaries for the supplied guides; no source text.

Real-PDF extraction tests verify this inventory. Unknown guide revisions must have
their boundaries checked before their claims can enter prompts.
"""

import json
import re
from pathlib import Path

from .models import Claim, GenerationRequest, Source

POLICY = "psalm-guides-appendices-b-c-only-v1"
SECTIONS = {"Appendix B": "Exegetical Layout", "Appendix C": "Flower Garden"}
GUIDE_SCOPES = json.loads(Path(__file__).with_suffix(".json").read_text())
BY_HASH = {row["sha256"]: row for row in GUIDE_SCOPES}


def guide_sections(source: Source) -> dict[str, list[int]] | None:
    known = BY_HASH.get(source.sha256)
    if known:
        return known["sections"]
    if any(
        re.fullmatch(r"psalms-\d+(?:-\d+)?\.pdf", Path(name).name, re.IGNORECASE)
        for name in (source.dataset, source.uri)
    ):
        raise ValueError("Unverified Psalm guide revision; check Appendix B/C boundaries")
    return None


def permitted_pdf_claim(claim: Claim, sources: dict[str, Source]) -> bool:
    """Every PDF citation must be paged and every guide citation in B or C."""
    pdf_evidence = [e for e in claim.evidence if e.source_id.startswith("pdf:")]
    if not pdf_evidence:
        return False
    for evidence in pdf_evidence:
        if evidence.page is None:
            return False
        sections = guide_sections(sources[evidence.source_id])
        if sections is not None and not any(evidence.page in pages for pages in sections.values()):
            return False
    return True


def validate_request_scope(request: GenerationRequest) -> None:
    """Reject old out-of-scope evidence before any provider is invoked."""
    assisted = request.input.get("representation", {})
    sources = {s["id"]: Source.model_validate(s) for s in assisted.get("sources", [])}
    for row in assisted.get("claims", []) + assisted.get("principles", []):
        claim = Claim.model_validate(row)
        if any(e.source_id.startswith("pdf:") for e in claim.evidence) and not (
            permitted_pdf_claim(claim, sources)
        ):
            raise ValueError("Prepared request violates Appendix B/C scope; prepare a new run")
