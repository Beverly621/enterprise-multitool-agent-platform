#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend"
alembic -c alembic.ini upgrade head

