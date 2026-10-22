"""Create-once owner seed: offline export of this owner's HTTP contract."""
import json
import sys
from pathlib import Path


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        print("openapi_arguments_invalid", file=sys.stderr)
        return 1
    try:
        destination = Path(__file__).with_name("openapi.json")
        if destination.is_symlink():
            print("openapi_output_invalid", file=sys.stderr)
            return 1
        from main import app
        schema = json.dumps(app.openapi(), sort_keys=True, indent=2) + "\n"
        if sys.argv[1:] == ["--check"]:
            if not destination.is_file() or destination.read_text(encoding="utf-8") != schema:
                print("openapi_stale", file=sys.stderr)
                return 1
        else:
            destination.write_text(schema, encoding="utf-8")
        print("openapi_current" if sys.argv[1:] else "openapi_exported")
        return 0
    except Exception:
        print("openapi_export_failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
