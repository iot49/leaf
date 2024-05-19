import os

from eventbus.bus import Config, CurrentState

from ..env import env as env
from .certificates import Certificates
from .secrets import Secrets

config = Config(config_file=os.path.join(env.CONFIG_DIR, "config.json"))
state = CurrentState()
Secrets()
Certificates()
