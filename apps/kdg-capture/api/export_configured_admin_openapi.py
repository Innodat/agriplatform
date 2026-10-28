"""Offline active read composition export; no configuration or database construction."""
import json
from pathlib import Path
import sys


def schema():
    from main import create_app
    from admin_runtime import compose_schema, handlers
    admin, audit = handlers()
    return compose_schema(create_app().openapi(),
        admin._create_app(None, None, None).openapi(),
        audit._create_app(None, None, None, None).openapi())


def main():
    if sys.argv[1:] not in ([], ['--check']):
        print('configured_admin_openapi_arguments_invalid', file=sys.stderr)
        return 1
    try:
        destination = Path(__file__).with_name('configured-admin.openapi.json')
        if destination.is_symlink():
            raise ValueError()
        encoded = json.dumps(schema(), sort_keys=True, indent=2) + '\n'
        if sys.argv[1:] == ['--check']:
            if not destination.is_file() or destination.read_text(encoding='utf-8') != encoded:
                print('configured_admin_openapi_stale', file=sys.stderr)
                return 1
        else:
            destination.write_text(encoded, encoding='utf-8')
        print('configured_admin_openapi_current' if sys.argv[1:] else 'configured_admin_openapi_exported')
        return 0
    except Exception:
        print('configured_admin_openapi_export_failed', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main())
