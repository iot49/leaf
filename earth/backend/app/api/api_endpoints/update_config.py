import json
import logging
import os
import shutil
from datetime import datetime, timezone

import yaml
from fastapi import HTTPException

from eventbus import post
from eventbus.event import put_config

from ...env import env
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# mergedeep
# https://mergedeep.readthedocs.io/en/latest/


@router.get("/update_config")
async def update_config():
    CONFIG_TEMPLATE = "default-config.yaml"
    CONFIG_DIR: str = env.CONFIG_DIR

    VERSION = datetime.now(timezone.utc).replace(microsecond=0).isoformat()[:-6]

    logger.debug("Updating config...")
    logger.debug(f"cwd: {os.getcwd()}")
    logger.debug(f"lsdir: {os.listdir()}")
    logger.debug(f"CONFIG_DIR: {CONFIG_DIR}")
    logger.debug(f"VERSION: {VERSION}")

    # copy default template if no config exists
    if not os.path.isfile(os.path.join(CONFIG_DIR, "config.yaml")):
        shutil.copyfile(CONFIG_TEMPLATE, os.path.join(CONFIG_DIR, "config.yaml"))

    # create new config.json
    try:
        cfg = yaml.safe_load(open(os.path.join(CONFIG_DIR, "config.yaml"), "r"))
    except (yaml.YAMLError, AttributeError, FileNotFoundError) as e:
        raise HTTPException(status_code=400, detail=f"Error parsing config.yaml: {e}")

    with open(os.path.join(CONFIG_DIR, "config.json"), "w") as f:
        cfg["version"] = VERSION
        cfg["domain"] = env.DOMAIN
        cfg["project_name"] = env.PROJECT_NAME
        cfg["environment"] = env.ENVIRONMENT.value
        json.dump(cfg, f, indent=2)

    # backup
    os.makedirs(os.path.join(CONFIG_DIR, "backups"), exist_ok=True)
    shutil.copyfile(os.path.join(CONFIG_DIR, "config.yaml"), os.path.join(CONFIG_DIR, "backups", VERSION + ".yaml"))

    # broadcast the updated config to all connected trees and clients
    print("Broadcasting config...")
    await post(put_config(dst="#clients", data=cfg))
    await post(put_config(dst="#branches", data=cfg))
    print(cfg)

    # return config
    return json.dumps(cfg, indent=2)
