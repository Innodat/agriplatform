"""Explicit publication-v1 adoption, preserving pinned controller definitions.

This is a targeted previous-object compatibility check, not a new head whitelist.
New object behavior and native grants remain release qualification requirements.
"""
from collections import Counter
from copy import deepcopy
import json

from baseline import APP, BaselineError, REVISION, PUBLICATION_REVISION, _checked_authority_ledger
from catalogue import snapshot
from prepared_controller import acl, custody, operator, TABLES
from controller_history import history


def deny():
    raise BaselineError('scribeswell_publication_profile_invalid')


def preserve_controller(connection, actual, expected, *, prepared):
    """Keep each exact pinned identity/definition/normalized ACL; allow additions."""
    actual, expected = deepcopy(actual), deepcopy(expected)
    acl_columns = {'schema':2, 'relations':7, 'columns':9, 'functions':6, 'default_acl':2}
    # Prepared v1 allows only the established controller execute grants and schema usage.
    if prepared:
        for key, names, index, privilege in (
                ('schema', {'scribeswell'}, 2, 'USAGE'),
                ('functions', {'execute_corpus_command','lookup_corpus_command_outcome'}, 6, 'EXECUTE')):
            for pinned in expected[key]:
                if pinned[0] not in names:
                    continue
                matches = [row for row in actual[key] if row[0] == pinned[0] and (key!='functions' or row[1]==pinned[1])]
                if len(matches)!=1:
                    deny()
                permitted = acl(connection,pinned[index])+[('scribeswell_migrator','scribeswell_corpus_operator',privilege,False)]
                if acl(connection,matches[0][index]) != sorted(permitted):
                    deny()
                matches[0][index]=pinned[index]
    if prepared:
        reads={'book','chapter','verse','word','corpus_fence_control','corpus_epoch','corpus_attempt','corpus_operator_principal','corpus_operator_authority'}
        for pinned in expected['relations']:
            if pinned[0] not in reads:
                continue
            matches=[row for row in actual['relations'] if row[0]==pinned[0]]
            if len(matches)!=1:
                deny()
            base=acl(connection,pinned[7]); observed=acl(connection,matches[0][7])
            if observed not in (base,sorted(base+[('scribeswell_migrator','scribeswell_corpus_operator','SELECT',False)])):
                deny()
            matches[0][7]=pinned[7]
    for key, rows in expected.items():
        observed = actual.get(key)
        if type(observed) is not list:
            deny()
        index=acl_columns.get(key)
        if index is not None:
            for row in rows + observed:
                row[index]=acl(connection,row[index])
        encode=lambda row: json.dumps(row,sort_keys=True,separators=(',',':'))
        if Counter(map(encode,rows))-Counter(map(encode,observed)):
            deny()
        # Existing objects must not gain alternate definitions/ACLs under the same
        # identity. Functions include signature; constraints include owning table.
        width = 2 if key in ('functions','columns','constraints','triggers','rules') else 1
        if key in ('schema','relations','columns','constraints','functions','views','triggers','rules','sequences'):
            pinned_ids={tuple(row[:width]) for row in rows}
            if Counter(map(encode,rows)) != Counter(encode(row) for row in observed if tuple(row[:width]) in pinned_ids):
                deny()


def preflight_publication(connection, expected_actor=None, *, reader=False):
    try:
        if (not connection.in_transaction() or connection.connection.dbapi_connection.autocommit
                or connection.get_isolation_level()!='READ COMMITTED'
                or connection.exec_driver_sql('SHOW transaction_read_only').scalar()!='off'):
            deny()
        connection.exec_driver_sql('SET LOCAL search_path=pg_catalog,pg_temp')
        for name,ceiling in (('statement_timeout',5000),('lock_timeout',2000)):
            current=int(connection.exec_driver_sql('SELECT setting FROM pg_catalog.pg_settings WHERE name=%s',(name,)).scalar())
            connection.exec_driver_sql('SELECT pg_catalog.set_config(%s,%s,true)',
                                       (name,str(min(current,ceiling) if current else ceiling)+'ms'))
        state=_checked_authority_ledger(connection)
        if state not in ((PUBLICATION_REVISION,'scribeswell_0005') if reader else (REVISION,PUBLICATION_REVISION)):
            deny()
        if expected_actor is not None:
            connection.exec_driver_sql('SELECT pg_catalog.pg_advisory_xact_lock(31003,1)')
        for table in TABLES:
            connection.exec_driver_sql('LOCK TABLE scribeswell.'+table+' IN SHARE MODE')
        expected=json.loads((APP/'migrations/reference-controller.json').read_text())
        preserve_controller(connection,snapshot(connection,head=True),expected,prepared=expected_actor is not None)
        if expected_actor is None:
            if connection.exec_driver_sql('SELECT singleton,enforcement FROM scribeswell.corpus_fence_control').fetchall()!=[(True,False)]:
                deny()
            for table in ('corpus_epoch','corpus_write_binding','corpus_operator_principal','corpus_operator_authority','corpus_attempt','corpus_command_outcome'):
                if connection.exec_driver_sql('SELECT 1 FROM scribeswell.'+table+' LIMIT 1').first():
                    deny()
        else:
            expected_actor=custody(expected_actor)
            operator(connection,publication=True)
            history(connection,expected_actor)
        # New object identities are checked by migration behavior/permission tests,
        # not a second catalogue snapshot. No privileges or rows are provisioned.
        return state
    except BaselineError:
        raise
    except Exception:
        raise BaselineError('scribeswell_publication_profile_failed') from None
