#!/usr/bin/env bash
set -e
export PYTHONPATH=.
uvicorn smart_librarian.backend.api_server:app --host 0.0.0.0 --port 8000 --reload
