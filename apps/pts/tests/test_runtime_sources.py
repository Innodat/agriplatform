"""Keep PtS's explicit packaged owner code closed over its entrypoint imports."""
import ast
from pathlib import Path

from apps.pts.deployment import package_runtime, verify_runtime


def test_packaged_owner_code_covers_main_backend_imports():
    owner = Path(__file__).resolve().parents[1]
    main = ast.parse((owner / 'backend/main.py').read_text())
    required = {
        'backend/' + node.module.replace('.', '/') + '.py'
        for node in ast.walk(main)
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module
    }
    assert required and all((owner / name).is_file() for name in required)
    # package_runtime copies SOURCES into owner-code; the verifier binds INPUTS
    # to those exact bytes. Both inventories must cover the entrypoint's imports.
    assert required <= set(package_runtime.SOURCES), required - set(package_runtime.SOURCES)
    assert required <= set(verify_runtime.INPUTS), required - set(verify_runtime.INPUTS)
