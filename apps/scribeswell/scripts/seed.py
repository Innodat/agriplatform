#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
IMPORTER_SCRIPT = APP_ROOT / "tools" / "py" / "import_bible.py"
SOURCE_FILE = APP_ROOT / "scripts" / "hebrew.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed Scribeswell data"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing to database",
    )

    parser.add_argument(
        "--book",
        default=None,
        help="Import only one book by OSIS id, e.g. Gen, Exod",
    )

    parser.add_argument(
        "--source",
        default=str(SOURCE_FILE),
        help="Path to hebrew.json. Defaults to apps/scribeswell/scripts/hebrew.json",
    )

    args = parser.parse_args()

    source = Path(args.source).resolve()

    if not IMPORTER_SCRIPT.exists():
        print(f"❌ Importer script not found: {IMPORTER_SCRIPT}")
        sys.exit(1)

    if not source.exists():
        print(f"❌ Source file not found: {source}")
        sys.exit(1)

    cmd = [
        sys.executable,
        str(IMPORTER_SCRIPT),
        "--source",
        str(source),
    ]

    if args.dry_run:
        cmd.append("--dry-run")

    if args.book:
        cmd.extend(["--book", args.book])

    print("▶ Running Scribeswell seed importer")
    print(f"▶ Source: {source}")

    result = subprocess.run(
        cmd,
        cwd=str(APP_ROOT),
        env=os.environ.copy(),
    )

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
