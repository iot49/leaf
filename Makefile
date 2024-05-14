#!/usr/bin/make


help:
	@echo "make serve"
	@echo "    Serve backend (api) without docker. Automatically reloads on changes."
	@echo
	@echo "make serve-alembic"
	@echo "    Apply alembic migrations, then serve backend (api). Automatically reloads on changes."
	@echo
	@echo "make add-migration"
	@echo "    Add a new alembic migration. Run this after making changes to the database schema."
	@echo
	@echo "make test"
	@echo "    Run pytest and coverage on local copy (no docker)."
	@echo
	@echo "make clean"
	@echo "    Remove python cache files."
	@echo
	@echo "make up"
	@echo "    Start development container. Volume mount backend api sources and reload on changes."
	@echo "    App available on https://leaf49.org and https://localhost:8000."
	@echo
	@echo "make up-build"
	@echo "    Rebuild container and start docker app."
	@echo
	@echo "make up-prod"
	@echo "    Start productions using production image for api."
	@echo
	@echo "make down"
	@echo "    Stop containers."
	@echo
	@echo "make build-prod"
	@echo "    Build production image for api locally."
	@echo "    Note: github actions automatically build production image and push to dockerhub."
	@echo "    Triggered by updates of backend or eventbus directories."
	@echo
	@echo "make balena-push"
	@echo "    Push app to balena server."
	@echo
	@echo "make build-docs"
	@echo "    Build static web content (frontend, jupyter book, api)."
	@echo
	@echo "make publish"
	@echo "    Build static content and push to gh-pages."
	
	

serve:
	cd earth/backend && \
	ENVIRONMENT="dev" \
	rye run uvicorn --host 0.0.0.0 --port 8001 --reload app.main:app

serve-alembic:
	rye run alembic upgrade head
	rye run uvicorn --port 8000 --reload app.main:app

add-migration:
	rye run alembic stamp head && \
	rye run alembic revision --autogenerate && \
	rye run alembic upgrade head

test:
	ENVIRONMENT="test" \
	cd eventbus && \
	rye run pytest -s # --cov="."
	cd earth/backend && \
	ENVIRONMENT="test" \
	rye run pytest -s --cov="." # -k test_bridge_2x2 # --cov="."

clean:
	@echo "Removing python cache files..."
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

up:
	docker compose -f earth/compose-dev-local.yml up

up-build:
	docker build -f earth/backend/Dockerfile.dev -t leaf-backend-dev .
	docker compose -f earth/compose-dev-local.yml up

up-prod:
	docker compose -f earth/compose-prod.yml up

down:
	docker compose -f earth/compose-dev.yml down

build-prod:
	docker build -f earth/backend/Dockerfile.prod -t leaf-backend .

balena-push:
	(cd earth && set -o allexport && source ../.env && set +o allexport && envsubst < "compose-balena.yml" > "docker-compose.yml";)
	cd earth && balena push -m boser/leaf
	cd earth && rm docker-compose.yml

ui:
	# cd ui && npm run build && rsync -av dist/ "/Users/boser/Dropbox/Apps/leaf49 (1)/ui"
	cd ui && npm run build
	./scripts/rsync-ui.sh

build-docs:
	# switch to mkdocs: https://realpython.com/python-project-documentation-with-mkdocs/
	pdoc -o gh-pages/eventbus eventbus
	jupyter-book build docs
	# pdoc -o gh-pages/backend earth/backend/app

serve-docs:
	cd gh-pages && \
	python -m http.server

publish: build-docs
	cp -a index.html gh-pages
	rsync -a docs/_build/html/ gh-pages/jupyter-book
	rsync -av frontend/dist/ gh-pages/frontend
	ghp-import -n -p -f gh-pages


.PHONY: help serve serve-alembic add-migration test clean up up up-build up-prod down build-prod balena-push ui build-docs publish
