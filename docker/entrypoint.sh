#!/bin/sh
set -e
mkdir -p /app/data /app/data/debug /app/data/secrets
RUN_UID=$(stat -c '%u' /app/data)
RUN_GID=$(stat -c '%g' /app/data)
chown -R "$RUN_UID:$RUN_GID" /app/data
exec setpriv --reuid="$RUN_UID" --regid="$RUN_GID" --clear-groups \
  sh -c '.venv/bin/alembic upgrade head && exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1'
