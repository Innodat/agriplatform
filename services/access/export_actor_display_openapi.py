"""Offline isolated candidate export; never imports or changes active main/OpenAPI."""
import json
import sys
from pathlib import Path


def main() -> int:
    if sys.argv[1:] not in ([], ['--check']):
        print('actor_display_openapi_arguments_invalid', file=sys.stderr)
        return 1
    try:
        from actor_display_http import create_app

        async def unavailable(actor_ids, deadline):
            raise RuntimeError('actor_display_export_only')

        schema = json.dumps(create_app({}, unavailable).openapi(), sort_keys=True, indent=2) + '\n'
        destination = Path(__file__).with_name('actor-display.openapi.json')
        if destination.is_symlink():
            raise ValueError()
        if sys.argv[1:] == ['--check']:
            if not destination.is_file() or destination.read_text(encoding='utf-8') != schema:
                print('actor_display_openapi_stale', file=sys.stderr)
                return 1
        else:
            destination.write_text(schema, encoding='utf-8')
        print('actor_display_openapi_current' if sys.argv[1:] else 'actor_display_openapi_exported')
        return 0
    except Exception:
        print('actor_display_openapi_export_failed', file=sys.stderr)
        return 1


if __name__ == '__main__':
    # Isolated Python deliberately omits the script directory from import search.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
