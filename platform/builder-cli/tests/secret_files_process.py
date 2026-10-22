"""Synthetic subprocess proof; argv contains public paths/configuration only."""
import importlib
import json
from pathlib import Path
import sys


def main():
    source, directory, receipt_path, action, active = sys.argv[1:]
    sys.path.insert(0, source)
    secret = importlib.import_module('fingerprint_secret_files')
    fingerprint = importlib.import_module('command_fingerprint')
    config = secret.SecretFileConfig(active, directory, 'synthetic-ci', 'kdg_capture')
    command = {'command_type': 'capture.edit', 'payload': {'answer': True}}
    receipt = Path(receipt_path)
    if action == 'create':
        material = secret.load_active(config)
        stored = fingerprint.create_fingerprint(command, key_id=material.key_id, key=material.key)
        # Private retained-outcome surrogate, never stdout or a diagnostic artifact.
        descriptor = receipt.open('x')
        receipt.chmod(0o600)
        with descriptor:
            json.dump({'version': stored.version, 'algorithm': stored.algorithm,
                       'key_id': stored.key_id, 'digest': stored.digest.hex()}, descriptor)
    else:
        raw = json.loads(receipt.read_text())
        raw['digest'] = bytes.fromhex(raw['digest'])
        stored = fingerprint.CommandFingerprint(**raw)
        material = secret.load_verification(config, stored.key_id)
        if not fingerprint.verify_fingerprint(command, stored, keys={material.key_id: material.key}):
            raise RuntimeError()
        if fingerprint.verify_fingerprint({'command_type': 'capture.edit', 'payload': {'answer': False}},
                                          stored, keys={material.key_id: material.key}):
            raise RuntimeError()
    print('secret_fixture:ok')


try:
    main()
except Exception:
    print('secret_fixture:refused', file=sys.stderr)
    sys.exit(1)
