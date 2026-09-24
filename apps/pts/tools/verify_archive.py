"""Verify the ignored working archive against committed byte-identity evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from apps.pts.backend.collection import validate

def verify(root,manifest):
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if actual!=set(manifest):raise ValueError('archive file inventory differs from manifest')
    for relative,evidence in manifest.items():
        path=root/relative
        with path.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
        if digest!=evidence['sha256'] or path.stat().st_size!=evidence['bytes']:raise ValueError('archive checksum mismatch: '+relative)
    library=json.loads((root/'library.json').read_text())
    counts=validate(library)
    expected={'poems':312,'texts':190,'checked':33,'witnesses':275,'sources':19,'rights':19}
    if counts!=expected:raise ValueError('canonical baseline differs')
    for d in library['source_documents']:
        if d.get('local_path'):
            path=(root/d['local_path']).resolve()
            if not path.is_relative_to(root.resolve()) or not path.is_file():raise ValueError('missing/unsafe source document')
    return {'files':len(actual),'bytes':sum(v['bytes'] for v in manifest.values()),'counts':counts}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).parents[1]/'reference/poetry-library');args=parser.parse_args()
    manifest=json.loads((Path(__file__).parents[1]/'reference/copy-manifest.json').read_text())
    print(json.dumps(verify(args.root,manifest),indent=2))
