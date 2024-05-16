#!/bin/bash

# credentials used by certbot
cat > /home/cloudflare/credentials <<EOF
dns_cloudflare_api_token = "${CF_API_TOKEN}"
EOF

chmod 600 /home/cloudflare/credentials

# we need access to certificates ...
chmod a+rx /home/letsencrypt/live
chmod a+rx /home/letsencrypt/archive

# fix ownership and permissions to edit files with code-server
chown -R app:app /home/config
chmod a+w /home/homeassistant/*.yaml  # homeassistant runs as root ...

setuidgid app uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000 --log-level error

# setuidgid app uvicorn alembic upgrade head && uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 8000
# setuidgid app uvicorn alembic upgrade head && gunicorn -w 3 -k uvicorn.workers.UvicornWorker app.main:app  --bind 0.0.0.0:8000 --preload --log-level=debug --timeout 120

# sleep infinity


