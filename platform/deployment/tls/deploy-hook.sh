#!/bin/sh
set -eu
# Restrict to this lineage; the periodic timer also retries failed deploy hooks.
if [ "${RENEWED_LINEAGE:-}" = /etc/letsencrypt/live/api.scribeswell.com ]; then
    systemctl start agriplatform-tls.service
fi
