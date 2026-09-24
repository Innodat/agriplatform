"""Explicit additive importer. No writes to the original and no silent replacement."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID
from sqlalchemy import text
from apps.pts.backend.collection import KINDS, validate
from apps.pts.backend.db import engine, scoped


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def import_library(conn, library):
    counts = validate(library)
    revision = digest(library)
    result = {'inserted': 0, 'conflicts': 0, 'unchanged': 0, 'counts': counts}
    snapshot = conn.execute(text('INSERT INTO pts.imports (org_id,id,payload) VALUES (current_setting(\'app.org_id\')::uuid,:id,CAST(:payload AS jsonb)) ON CONFLICT DO NOTHING RETURNING id'), {'id': revision, 'payload': json.dumps(library, ensure_ascii=False)}).scalar()
    if not snapshot:
        result['replayed'] = True
        result['conflicts'] = conn.execute(text('SELECT count(*) FROM pts.conflicts WHERE import_id=:id'), {'id': revision}).scalar_one()
        return result
    groups = [(kind, [(row['id'], row) for row in library[kind]]) for kind in KINDS]
    groups.append(('metadata', [(k, v) for k, v in library.items() if k not in KINDS]))
    for kind, rows in groups:
        for ordinal, (record_id, payload) in enumerate(rows):
            args = {'id': record_id, 'payload': json.dumps(payload, ensure_ascii=False), 'ordinal': ordinal}
            added = conn.execute(text(f"INSERT INTO pts.{kind}(org_id,id,payload,ordinal) VALUES(current_setting('app.org_id')::uuid,:id,CAST(:payload AS jsonb),:ordinal) ON CONFLICT DO NOTHING RETURNING id"), args).scalar()
            if added: result['inserted'] += 1; continue
            existing = conn.execute(text(f'SELECT payload FROM pts.{kind} WHERE id=:id'), args).scalar_one()
            if existing == payload: result['unchanged'] += 1; continue
            conn.execute(text("INSERT INTO pts.conflicts(org_id,import_id,kind,record_id,incoming) VALUES(current_setting('app.org_id')::uuid,:revision,:kind,:id,CAST(:payload AS jsonb)) ON CONFLICT DO NOTHING"), {**args, 'revision': revision, 'kind': kind})
            result['conflicts'] += 1
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--org', type=UUID, required=True)
    args = parser.parse_args()
    library = json.loads(args.source.read_text(encoding='utf-8'))
    db = engine(os.environ['PTS_IMPORT_DATABASE_URL'])
    with scoped(db, args.org, 'service:pts-import') as conn:
        # Serialize imports for this organization, without external I/O in the transaction.
        conn.execute(text("SELECT pg_advisory_xact_lock(hashtextextended(:org, 0))"), {'org': str(args.org)})
        result = import_library(conn, library)
    print(json.dumps(result))
    if result['conflicts']: raise SystemExit(2)


if __name__ == '__main__': main()
