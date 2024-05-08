#!/bin/bash

chown -R app:app /home/config

setuidgid app uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000
# setuidgid app uvicorn alembic upgrade head && uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000
# setuidgid app uvicorn alembic upgrade head && gunicorn -w 3 -k uvicorn.workers.UvicornWorker app.main:app  --bind 0.0.0.0:8000 --preload --log-level=debug --timeout 120

sleep infinity