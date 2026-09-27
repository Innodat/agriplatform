"""Compatibility entry point for the backend-owned canonical OSHB decoder."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'backend'))
from services.oshb_morph import ParsedMorpheme, parse_morph_code  # noqa: E402,F401
