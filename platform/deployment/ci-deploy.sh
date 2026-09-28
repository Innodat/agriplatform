#!/usr/bin/env bash
set -euo pipefail
: "${DEPLOY_ENV:?}" "${RELEASE_SHA:?}" "${DEPLOY_HOST:?}" "${DEPLOY_USER:?}" "${SSH_PRIVATE_KEY:?}" "${SSH_KNOWN_HOSTS:?}"
[[ "$DEPLOY_ENV" == staging || "$DEPLOY_ENV" == production ]]
[[ "$RELEASE_SHA" =~ ^[0-9a-f]{40}$ ]]
[[ "$DEPLOY_HOST" =~ ^[a-zA-Z0-9.-]+$ && "$DEPLOY_USER" =~ ^[a-z_][a-z0-9_-]*$ ]]
if [[ "$DEPLOY_ENV" == production ]]; then
  python3 platform/deployment/wireguard/runner.py validate
fi
ssh_directory=$(mktemp -d)
trap 'rm -f "$ssh_directory/deploy_key" "$ssh_directory/known_hosts"; rmdir "$ssh_directory"' EXIT
printf '%s\n' "$SSH_PRIVATE_KEY" > "$ssh_directory/deploy_key"
chmod 600 "$ssh_directory/deploy_key"
printf '%s\n' "$SSH_KNOWN_HOSTS" > "$ssh_directory/known_hosts"
chmod 600 "$ssh_directory/known_hosts"
python3 - <<'PYCONFIG'
import json,os
from pathlib import Path
Path('public-config.json').write_text(json.dumps({key:os.environ[field] for key,field in [('environment','DEPLOY_ENV'),('site','PUBLIC_SITE_ORIGIN'),('api','PUBLIC_API_ORIGIN'),('supabase_url','VITE_SUPABASE_URL')]}))
PYCONFIG
# Tracked source only, no local environment, archives or ignored libraries.
git archive --format=tar "$RELEASE_SHA" > /tmp/release-source.tar
remote="${DEPLOY_USER}@${DEPLOY_HOST}"
options=(-i "$ssh_directory/deploy_key" -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes -o GlobalKnownHostsFile=/dev/null -o "UserKnownHostsFile=$ssh_directory/known_hosts" -o ConnectTimeout=10 -o ConnectionAttempts=2 -o ServerAliveInterval=15 -o ServerAliveCountMax=3)
ssh "${options[@]}" "$remote" true
ssh "${options[@]}" "$remote" "mkdir -p /srv/agriplatform/incoming/$RELEASE_SHA"
scp "${options[@]}" /tmp/release-source.tar images.json public-config.json "$remote:/srv/agriplatform/incoming/$RELEASE_SHA/"
# Target account needs a narrowly reviewed root wrapper or root access; bootstrap and registry login are manual setup.
ssh "${options[@]}" "$remote" "tar -xf /srv/agriplatform/incoming/$RELEASE_SHA/release-source.tar -C /srv/agriplatform/incoming/$RELEASE_SHA && python3 /srv/agriplatform/incoming/$RELEASE_SHA/platform/deployment/host-release.py --public-config /srv/agriplatform/incoming/$RELEASE_SHA/public-config.json --environment $DEPLOY_ENV --sha $RELEASE_SHA --images /srv/agriplatform/incoming/$RELEASE_SHA/images.json --config /etc/agriplatform/$DEPLOY_ENV.json --release-dir /srv/agriplatform/releases/$RELEASE_SHA-${GITHUB_RUN_ID:?}-${GITHUB_RUN_ATTEMPT:?}"
