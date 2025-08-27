#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
export UVICORN_WORKERS=${UVICORN_WORKERS:-1}
uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-8000} --reload
