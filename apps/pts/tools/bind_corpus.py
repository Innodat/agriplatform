"""Controlled, one-time corpus binding after independently reviewed inventory.

No runtime caller may bind or replace a corpus. Operate only with pts_migrator;
all source reads and the singleton insert share the predecessor import lock.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import UUID
from sqlalchemy import text
from apps.pts.backend.db import engine,scoped
TABLES=('rights','sources','poems','witnesses','source_documents','metadata','imports','conflicts','attachments')

def inventory(conn):
    rows={table:list(conn.execute(text(f'SELECT to_jsonb(t) FROM pts.{table} t ORDER BY to_jsonb(t)::text')).scalars()) for table in TABLES}
    encoded=json.dumps(rows,sort_keys=True,separators=(',',':'),default=str).encode()
    return {'counts':{table:len(values) for table,values in rows.items()},'snapshot_sha256':hashlib.sha256(encoded).hexdigest()}

def bind(db,document):
    if set(document)!={'schema_version','executor_actor_id','legacy_partition_id','inventory_sha256','release_reference','counts','snapshot_sha256'} or document['schema_version']!=1:raise ValueError('corpus_binding_input_invalid')
    partition=str(UUID(document['legacy_partition_id']));actor=str(UUID(document['executor_actor_id']))
    for field in ('inventory_sha256','snapshot_sha256'):
        if not isinstance(document[field],str) or len(document[field])!=64 or any(c not in '0123456789abcdef' for c in document[field]):raise ValueError('corpus_binding_input_invalid')
    if not isinstance(document['release_reference'],str) or not 1<=len(document['release_reference'])<=200:raise ValueError('corpus_binding_input_invalid')
    with scoped(db,partition,actor,consistent=False) as conn:
        if conn.execute(text('SELECT current_user')).scalar_one()!='pts_migrator':raise ValueError('corpus_binding_requires_owner')
        conn.execute(text("SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='30s'"))
        conn.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:org,0))'),{'org':partition})
        previous=conn.execute(text('SELECT legacy_partition_id,inventory_sha256,release_reference FROM pts.corpus_binding WHERE singleton')).mappings().first()
        expected={field:document[field] for field in ('legacy_partition_id','inventory_sha256','release_reference')}
        if previous:
            if {key:str(value) for key,value in previous.items()}!=expected:raise ValueError('corpus_binding_already_exists')
            if inventory(conn)!={field:document[field] for field in ('counts','snapshot_sha256')}:raise ValueError('corpus_inventory_changed')
            return {'status':'unchanged'}
        actual=inventory(conn)
        if actual!={field:document[field] for field in ('counts','snapshot_sha256')}:raise ValueError('corpus_inventory_changed')
        conn.execute(text('INSERT INTO pts.corpus_binding(singleton,legacy_partition_id,inventory_sha256,release_reference,verified_at) VALUES(true,:partition,:inventory,:release,:verified)'),
            {'partition':partition,'inventory':document['inventory_sha256'],'release':document['release_reference'],'verified':datetime.now(timezone.utc)})
    return {'status':'bound'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed-input',type=Path,required=True);args=parser.parse_args()
    try:result=bind(engine(os.environ['PTS_MIGRATION_DATABASE_URL']),json.loads(args.reviewed_input.read_text()))
    except Exception:raise SystemExit('corpus_binding_failed_requires_reconciliation') from None
    print(json.dumps(result))
if __name__=='__main__':main()
