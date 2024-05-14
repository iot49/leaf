import os

from app.env import env as env  # noqa: E402
from eventbus.bus import Config, CurrentState

from .certificates import Certificates
from .secrets import Secrets

config = Config(config_file=os.path.join(env.CONFIG_DIR, "config.json"))  # type: ignore
state = CurrentState()
Secrets()
Certificates()
