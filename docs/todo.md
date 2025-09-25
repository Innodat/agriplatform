BE
++

select
  settings->>'account_name' as account_name,
  settings->>'container_name' as container_name,
  cs.resolve_secret(settings->>'connection_secret') as connection_string
from cs.content_source
where name = 'Liseli Azure Storage';
