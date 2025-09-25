#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Repo root is 2 levels up from this file
REPO_ROOT = Path(__file__).resolve().parents[2]
TS_DIR = REPO_ROOT / "packages" / "tools" / "ts"
PY_DIR = REPO_ROOT / "packages" / "tools" / "py"

def discover_wrappers():
    wrappers = {}
    # Scan TS wrappers
    for file in TS_DIR.glob("*.ts"):
        name = file.stem.replace("run-", "")
        wrappers[name] = ("ts-node", str(file))
    # Scan PY wrappers
    for file in PY_DIR.glob("*.py"):
        name = file.stem.replace("run_", "").replace("run-", "")
        wrappers[name] = ("python", str(file))
    return wrappers

def main():
    WRAPPERS = discover_wrappers()

    if len(sys.argv) < 2 or sys.argv[1] not in WRAPPERS:
        print(f"❌ Unknown or missing command: {sys.argv[1:] or 'None'}")
        print("Available commands:", ", ".join(sorted(WRAPPERS.keys())))
        sys.exit(1)

    cmd_key = sys.argv[1]
    runner, path = WRAPPERS[cmd_key]

    exec_path = Path(path)
    if not exec_path.exists():
        print(f"❌ Wrapper not found: {exec_path}")
        sys.exit(1)

    print(f"▶ Routing '{cmd_key}' → {runner} {exec_path.relative_to(REPO_ROOT)}")
    result = subprocess.run([runner, str(exec_path), *sys.argv[2:]],
                            shell=(sys.platform == "win32"))
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()