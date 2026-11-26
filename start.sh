#!/usr/bin/env bash
set -e

python3 server.py &
exec python3 -m Zaid
