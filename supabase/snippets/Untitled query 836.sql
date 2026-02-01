
select
  p.polname,
  p.polcmd,                -- r=SELECT, a=INSERT, w=UPDATE, d=DELETE
  p.polpermissive as permissive, -- false means RESTRICTIVE
  pg_get_expr(p.polqual, p.polrelid)       as using_expr,
  pg_get_expr(p.polwithcheck, p.polrelid)  as with_check_expr
from pg_policy p
join pg_class c on p.polrelid = c.oid
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'finance' and c.relname = 'receipt'
order by p.polcmd, p.polname;
