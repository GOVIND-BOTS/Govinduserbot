#!/usr/bin/env bash
set -e

echo "Container UTC time: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "Container Unix timestamp: $(date -u '+%s')"

python3 server.py &
exec python3 -m Zaid
