"""Fail before any deployment side effects when the environment is incomplete."""
import os
import re
required=['DEPLOY_ENV','RELEASE_SHA','PUBLIC_SITE_ORIGIN','PUBLIC_API_ORIGIN','VITE_SUPABASE_URL','VITE_SUPABASE_ANON_KEY','DEPLOY_HOST','DEPLOY_USER','SSH_PRIVATE_KEY','SSH_KNOWN_HOSTS','NETLIFY_AUTH_TOKEN','NETLIFY_SITE_ID']
missing=[name for name in required if not os.environ.get(name)]
if missing:raise SystemExit('Missing deployment inputs: '+', '.join(missing))
if os.environ['DEPLOY_ENV'] not in ('staging','production') or not re.fullmatch('[0-9a-f]{40}',os.environ['RELEASE_SHA']):raise SystemExit('Invalid environment or exact commit SHA')
print('Required deployment inputs are present (values not printed)')
