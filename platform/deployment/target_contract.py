"""Pure project/role binding shared by host preflight and migration adapter."""
import re
from urllib.parse import urlsplit, parse_qs, unquote

def database_url(value,project,role):
 p=urlsplit(project);match=re.fullmatch(r'([a-z0-9]+)\.supabase\.co',p.hostname or '')
 if p.scheme!='https' or not match:raise ValueError('invalid Supabase project')
 ref=match[1];u=urlsplit(value);username=unquote(u.username or '');host=u.hostname or '';query=parse_qs(u.query,keep_blank_values=True)
 direct=host==f'db.{ref}.supabase.co' and username==role
 pooler=host.endswith('.pooler.supabase.com') and username==f'{role}.{ref}'
 if u.scheme not in ('postgresql','postgresql+psycopg') or not (direct or pooler) or not u.password or u.path!='/postgres' or u.fragment:raise ValueError('database project/role mismatch')
 if query.get('sslmode') not in (['require'],['verify-full']) or set(query)-{'sslmode','connect_timeout'}:raise ValueError('explicit TLS database URL required')
 if 'connect_timeout' in query:
  values=query['connect_timeout']
  if len(values)!=1 or not re.fullmatch(r'[0-9]+',values[0]) or not 1<=int(values[0])<=10:raise ValueError('invalid database connect_timeout')
 return value
