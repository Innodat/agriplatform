"""Stable PostgreSQL catalogue representation; deliberately excludes data and OIDs."""
QUERIES = {
'schema': "SELECT nspname, pg_get_userbyid(nspowner), nspacl::text FROM pg_namespace WHERE nspname='scribeswell'",
'relations': """SELECT c.relname,c.relkind,c.relpersistence,pg_get_userbyid(c.relowner),c.relrowsecurity,c.relforcerowsecurity,c.reloptions,c.relacl::text,c.relreplident,c.relispartition,c.reltablespace<>0
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND c.relname<>'alembic_version' AND c.relname<>'alembic_version_pkc' ORDER BY 1""",
'columns': """SELECT c.relname,a.attnum,a.attname,format_type(a.atttypid,a.atttypmod),a.attnotnull,a.attidentity,a.attgenerated,a.attisdropped,pg_get_expr(d.adbin,d.adrelid),a.attacl::text,a.attcollation::regcollation::text
 FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum
 WHERE n.nspname='scribeswell' AND c.relkind IN ('r','v','p','m','f') AND c.relname<>'alembic_version' AND a.attnum>0 ORDER BY 1,2""",
'constraints': """SELECT c.relname,k.conname,k.contype,k.condeferrable,k.condeferred,k.convalidated,pg_get_constraintdef(k.oid,true) FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND c.relname<>'alembic_version' ORDER BY 1,2""",
'indexes': """SELECT c.relname,pg_get_indexdef(i.indexrelid),i.indisvalid,i.indisready,i.indislive FROM pg_index i JOIN pg_class c ON c.oid=i.indrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND c.relname<>'alembic_version' ORDER BY 1,2""",
'views': """SELECT c.relname,pg_get_viewdef(c.oid,true) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND c.relkind IN ('v','m') ORDER BY 1""",
'policies': """SELECT tablename,policyname,permissive,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='scribeswell' ORDER BY 1,2""",
'sequences': """SELECT c.relname,format_type(s.seqtypid,NULL),s.seqstart,s.seqincrement,s.seqmax,s.seqmin,s.seqcache,s.seqcycle,t.relname,a.attname,d.deptype FROM pg_sequence s JOIN pg_class c ON c.oid=s.seqrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_depend d ON d.classid='pg_class'::regclass AND d.objid=c.oid AND d.refclassid='pg_class'::regclass AND d.deptype IN ('a','i') LEFT JOIN pg_class t ON t.oid=d.refobjid LEFT JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=d.refobjsubid WHERE n.nspname='scribeswell' ORDER BY 1""",
'default_acl': """SELECT pg_get_userbyid(d.defaclrole),d.defaclobjtype,d.defaclacl::text FROM pg_default_acl d JOIN pg_namespace n ON n.oid=d.defaclnamespace WHERE n.nspname='scribeswell' ORDER BY 1,2""",
'functions': "SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='scribeswell' ORDER BY 1",
'extra_types': """SELECT t.typname,t.typtype FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='scribeswell' AND t.typrelid=0 AND t.typelem=0 ORDER BY 1""",
'rules': """SELECT c.relname,r.rulename,pg_get_ruledef(r.oid,true) FROM pg_rewrite r JOIN pg_class c ON c.oid=r.ev_class JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND r.rulename<>'_RETURN' ORDER BY 1,2""",
 'triggers': """SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid,true),t.tgenabled FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scribeswell' AND NOT t.tgisinternal ORDER BY 1,2""",
 'internal_constraint_triggers': """SELECT c.relname,k.conname,own.relname,t.tgfoid::regproc::text,t.tgtype,t.tgenabled,t.tgdeferrable,t.tginitdeferred,t.tgattr::text,pg_get_expr(t.tgqual,t.tgrelid)
 FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_constraint k ON k.oid=t.tgconstraint LEFT JOIN pg_class own ON own.oid=k.conrelid
 WHERE n.nspname='scribeswell' AND t.tgisinternal ORDER BY 1,2,3,4,5,6,7,8,9,10""",
 'extensions': "SELECT e.extname FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace WHERE n.nspname='scribeswell' ORDER BY 1",
 'other_schema_objects': """SELECT 'collation',collname FROM pg_collation WHERE collnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'operator',oprname FROM pg_operator WHERE oprnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'operator_class',opcname FROM pg_opclass WHERE opcnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'operator_family',opfname FROM pg_opfamily WHERE opfnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'conversion',conname FROM pg_conversion WHERE connamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'text_search_config',cfgname FROM pg_ts_config WHERE cfgnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'text_search_dict',dictname FROM pg_ts_dict WHERE dictnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'text_search_parser',prsname FROM pg_ts_parser WHERE prsnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'text_search_template',tmplname FROM pg_ts_template WHERE tmplnamespace='scribeswell'::regnamespace
 UNION ALL SELECT 'statistics',stxname FROM pg_statistic_ext WHERE stxnamespace='scribeswell'::regnamespace
 ORDER BY 1,2""",
 'publications': "SELECT pubname,tablename FROM pg_publication_tables WHERE schemaname='scribeswell' ORDER BY 1,2",
}

HEAD_FUNCTIONS = """SELECT p.proname,pg_get_function_identity_arguments(p.oid),
 pg_get_functiondef(p.oid),pg_get_userbyid(p.proowner),p.prosecdef,p.proconfig,
 p.proacl::text,p.provolatile,p.proparallel,p.proleakproof,p.proisstrict,
 p.prokind,l.lanname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 JOIN pg_language l ON l.oid=p.prolang WHERE n.nspname='scribeswell' ORDER BY 1,2"""

def snapshot(connection, *, head=False):
    # JSON round-trip gives driver-independent array/list normalization.
    import json
    return json.loads(json.dumps({key: [list(row) for row in connection.exec_driver_sql(query).fetchall()] for key,query in (QUERIES | ({'functions':HEAD_FUNCTIONS} if head else {})).items()}, default=str))
