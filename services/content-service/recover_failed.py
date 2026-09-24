"""Explicit operator recovery after stopping and reconciling an interrupted finalizer.

Retains metadata, sealed bytes and audit; the next import gets a new identity.
Requires content-owner migration/recovery authority, never runtime credentials.
"""
import argparse
import os
from uuid import UUID, uuid4
from sqlalchemy import create_engine, text


def abandon(connection, org, content_id, actor):
    connection.execute(text("SELECT set_config('app.org_id',:org,true),set_config('app.actor_id',:actor,true)"),
                       {'org':str(org),'actor':actor})
    changed=connection.execute(text("UPDATE content.objects SET state='failed' WHERE id=:id AND state='finalizing' RETURNING id"),
                               {'id':str(content_id)}).scalar()
    if not changed:
        raise ValueError('Only a reconciled, stopped finalizing object can be abandoned')
    connection.execute(text("INSERT INTO content.events(org_id,id,content_id,operation) VALUES(:org,:id,:content,'failed_finalization_retained')"),
                       {'org':org,'id':uuid4(),'content':str(content_id)})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--org',type=UUID,required=True)
    parser.add_argument('--content-id',type=UUID,required=True)
    parser.add_argument('--actor',required=True)
    parser.add_argument('--finalizer-stopped-and-reconciled',action='store_true',required=True)
    args=parser.parse_args()
    db=create_engine(os.environ['CONTENT_RECOVERY_DATABASE_URL'],hide_parameters=True)
    with db.begin() as connection:
        abandon(connection,args.org,args.content_id,args.actor)
    print('Failed identity and bytes retained. Retry import to obtain a fresh content identity.')


if __name__=='__main__':main()
