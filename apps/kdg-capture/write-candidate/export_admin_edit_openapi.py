"""Owner-only candidate OpenAPI export; no engine, credentials or startup I/O."""
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/'api'))
DESTINATION=HERE/'admin-edit-openapi.json'


def render():
    from admin_edit_http import _create_app
    return json.dumps(_create_app(None,None,None,None).openapi(),sort_keys=True,indent=2)+'\n'


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    if args not in ([],['--check']):
        print('admin_edit_openapi_arguments_invalid',file=sys.stderr)
        return 1
    try:
        if DESTINATION.is_symlink():
            raise ValueError('invalid_output')
        content=render()
        if args:
            if not DESTINATION.is_file() or DESTINATION.read_text(encoding='utf-8')!=content:
                print('admin_edit_openapi_stale',file=sys.stderr)
                return 1
        else:
            DESTINATION.write_text(content,encoding='utf-8')
        print('admin_edit_openapi_current' if args else 'admin_edit_openapi_exported')
        return 0
    except Exception:
        print('admin_edit_openapi_export_failed',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
