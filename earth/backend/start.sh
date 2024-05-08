#!/bin/bash

chown -R app:app /home/config

# setuidgid app "sh -c 'uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000'"

sleep infinity