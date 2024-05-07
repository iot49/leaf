# Leaf

## Configure repo

### submodule

```bash
cd trees/vm
git submodule add https://github.com/micropython/micropython.git
```

## Deploy

1) Earth (FastAPI)
   a) dockerhub: ttmetro/leaf-backend
   b) built by github action earth-backend.yml
   c) deploy to balena: `make balena-push`
2) UI (LitElement)
   * create latest release and push to balena (static content): `make balena-ui`
   * Note: `mv ui/dist/assets/svg ui/dist/assets/icons`
1) Trees (MicroPython)
   * push tag `v*` builds VM and publishes as release
   * flash or ota update


### .github secrets

In github repo, choose

* Settings
* Secrets and variables
* Actions
* New repository secret


## Core Components

### Trees

Micropython app for collecting sensor data.


### UI

Web frontend based on lit-element.

### Earth

Cloud backend for managing apps and credentials.

Created from the following [template](https://github.com/allient/create-fastapi-project):

```bash
pip install create-fastapi-project
create-fastapi-project
```

* [Source](https://github.com/allient/create-fastapi-project/tree/main/create_fastapi_project/templates/full)
* [Documentation](https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/blob/main/README.md)
* [Our Journey Using Async FastAPI to Harnessing the Power of Modern Web APIs](https://medium.com/allient/our-journey-using-async-fastapi-to-harnessing-the-power-of-modern-web-apis-90301827f14c)

