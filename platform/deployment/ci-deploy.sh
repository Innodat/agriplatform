#!/usr/bin/env bash
set -euo pipefail
: "${DEPLOY_ENV:?}" "${RELEASE_SHA:?}" "${DEPLOY_HOST:?}" "${DEPLOY_USER:?}" "${SSH_PRIVATE_KEY:?}" "${SSH_KNOWN_HOSTS:?}"
[[ "$DEPLOY_ENV" == staging || "$DEPLOY_ENV" == production ]]
[[ "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]
[[ "$DEPLOY_HOST" =~ ^[a-zA-Z0-9.-]+$ && "$DEPLOY_USER" =~ ^[a-z_][a-z0-9_-]*$ ]]
install -d -m 700 "$HOME/.ssh"
printf '%s\n' "$SSH_PRIVATE_KEY" > "$HOME/.ssh/deploy_key"
chmod 600 "$HOME/.ssh/deploy_key"
printf '%s\n' "$SSH_KNOWN_HOSTS" > "$HOME/.ssh/known_hosts"
trap 'rm -f "$HOME/.ssh/deploy_key"' EXIT
python3 - <<'PYCONFIG'
import json,os
from pathlib import Path
Path('public-config.json').write_text(json.dumps({key:os.environ[field] for key,field in [('environment','DEPLOY_ENV'),('site','PUBLIC_SITE_ORIGIN'),('api','PUBLIC_API_ORIGIN'),('supabase_url','VITE_SUPABASE_URL')]}))
PYCONFIG
# Tracked source only, no local environment, archives or ignored libraries.
git archive --format=tar "$RELEASE_SHA" > /tmp/release-source.tar
remote="${DEPLOY_USER}@${DEPLOY_HOST}"
options=(-i "$HOME/.ssh/deploy_key" -o BatchMode=yes -o StrictHostKeyChecking=yes)
ssh "${options[@]}" "$remote" "mkdir -p /srv/agriplatform/incoming/$RELEASE_SHA"
scp "${options[@]}" /tmp/release-source.tar images.json public-config.json "$remote:/srv/agriplatform/incoming/$RELEASE_SHA/"
# Target account needs a narrowly reviewed root wrapper or root access; bootstrap and registry login are manual setup.
ssh "${options[@]}" "$remote" "tar -xf /srv/agriplatform/incoming/$RELEASE_SHA/release-source.tar -C /srv/agriplatform/incoming/$RELEASE_SHA && python3 /srv/agriplatform/incoming/$RELEASE_SHA/platform/deployment/host-release.py --public-config /srv/agriplatform/incoming/$RELEASE_SHA/public-config.json --environment $DEPLOY_ENV --sha $RELEASE_SHA --images /srv/agriplatform/incoming/$RELEASE_SHA/images.json --config /etc/agriplatform/$DEPLOY_ENV.json --release-dir /srv/agriplatform/releases/$RELEASE_SHA-${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}"
