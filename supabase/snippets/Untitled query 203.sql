select
  t.tgname,
  t.tgenabled,
  pg_get_triggerdef(t.oid) as trigger_def
from pg_trigger t
join pg_class c on t.tgrelid = c.oid
join pg_namespace n on c.relnamespace = n.oid
where n.nspname = 'finance'
  and c.relname = 'receipt'
  and not t.tgisinternal;
