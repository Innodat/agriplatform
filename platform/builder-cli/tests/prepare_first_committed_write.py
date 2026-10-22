"""Retained first-committed fixture using the unmodified historical preparer.

Run with prepared Python --admin PRIVATE_JSON --proof NEW_EXCLUSIVE_DIRECTORY.
Staging and every partially prepared resource are retained, including on failure.
"""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from uuid import uuid4


def stage(proof):
    source=Path(__file__).resolve().parent
    proof.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    staged=proof.parent/(proof.name+'-preparer-'+uuid4().hex)
    staged.mkdir(mode=0o700,exist_ok=False)
    sources={'prepare_atomic_write.py':'prepare_atomic_write.py',
             'first_committed_fixture.sql':'atomic_write_fixture.sql'}
    hashes={}
    for original,destination in sources.items():
        shutil.copyfile(source/original,staged/destination)
        copied=(staged/destination).read_bytes()
        if copied!=(source/original).read_bytes():raise ValueError('fixture_staging_failed')
        hashes[destination]=sha256(copied).hexdigest()
    (staged/'staged.json').write_text(json.dumps(dict(retained=True,files=hashes)))
    return staged


def prepare(admin,proof):
    staged=stage(proof)
    spec=importlib.util.spec_from_file_location('retained_atomic_preparer',staged/'prepare_atomic_write.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.prepare(admin,proof)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--admin',type=Path,required=True)
    parser.add_argument('--proof',type=Path,required=True)
    args=parser.parse_args()
    try:
        prepare(args.admin,args.proof)
    except Exception:
        print('first_committed_fixture_preparation_failed',file=sys.stderr)
        raise SystemExit(1) from None
