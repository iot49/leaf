import contextlib
import json
import logging
import os
import shutil
from datetime import datetime, timezone

import yaml
from fastapi import HTTPException
from genericpath import isdir

from eventbus import post
from eventbus.event import put_config

from ...env import env
from . import router

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def new_cd(x):
    d = os.getcwd()
    os.chdir(x)
    try:
        yield
    finally:
        os.chdir(d)


# mergedeep
# https://mergedeep.readthedocs.io/en/latest/


@router.get("/update_config")
async def update_config():
    CONFIG_TEMPLATE_DIR = "config_template"
    CONFIG_DIR: str = env.CONFIG_DIR  # type: ignore

    VERSION = datetime.now(timezone.utc).replace(microsecond=0).isoformat()[:-6]

    logger.debug("Updating config...")
    logger.debug(f"cwd: {os.getcwd()}")
    logger.debug(f"CONFIG_DIR: {CONFIG_DIR}")
    logger.debug(f"VERSION: {VERSION}")

    # send existing config if recently updated
    if isdir(os.path.join(CONFIG_DIR, "backups", VERSION)):
        try:
            with open(os.path.join(CONFIG_DIR, "config.json")) as f:
                return yaml.dump(json.load(f), indent=2)
        except FileNotFoundError:
            pass

    # copy default template if no config exists
    if not os.path.isdir(os.path.join(CONFIG_DIR, "default-config")):
        for d in os.listdir(CONFIG_TEMPLATE_DIR):
            try:
                shutil.copytree(os.path.join(CONFIG_TEMPLATE_DIR, d), os.path.join(CONFIG_DIR, d))
            except FileExistsError:
                pass

    # create updated config from default and user config
    cfg = {}
    for file in os.listdir(os.path.join(CONFIG_DIR, "default-config")):
        path, ext = os.path.splitext(file)
        if ext == ".yaml" or ext == ".yml":
            try:
                cfg[path] = yaml.safe_load(open(os.path.join(CONFIG_DIR, "default-config", file), "r"))
            except (yaml.YAMLError, AttributeError) as e:
                raise HTTPException(status_code=400, detail=f"Error parsing {file}: {e}")

    # user customizations
    for file in os.listdir(os.path.join(CONFIG_DIR, "user-config")):
        path, ext = os.path.splitext(file)
        if ext == ".yaml" or ext == ".yml":
            try:
                cfg[path] = yaml.safe_load(open(os.path.join(CONFIG_DIR, "user-config", file), "r"))
            except (yaml.YAMLError, AttributeError) as e:
                raise HTTPException(status_code=400, detail=f"Error parsing {file}: {e}")
    logger.debug(f"config {json.dumps(cfg, indent=2)}")

    # env
    cfg.update({"domain": env.DOMAIN})
    cfg.update({"project_name": env.PROJECT_NAME})
    cfg.update({"environment": env.ENVIRONMENT.value})

    # version
    cfg.update({"version": VERSION})

    # save config
    with open(os.path.join(CONFIG_DIR, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)

    # broadcast the updated config to all connected trees and clients
    await post(put_config(dst="#all", data=cfg))

    # create backup
    shutil.copytree(os.path.join(CONFIG_DIR, "user-config"), os.path.join(CONFIG_DIR, "backups", VERSION))
    logger.debug(f"backup at {os.path.join(CONFIG_DIR, 'backups', VERSION)}")

    # return config as yaml
    return yaml.dump(cfg, indent=2)
