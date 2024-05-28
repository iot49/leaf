import asyncio
import os

from eventbus.bus import Config, Counter, CurrentState

from ..env import env as env
from .certificates import Certificates
from .secrets import Secrets

config = Config(config_file=os.path.join(env.CONFIG_DIR, "config.json"))
state = CurrentState()
Secrets()
Certificates()

counter = Counter(eid="counter.count", interval=1)
asyncio.create_task(counter.counter_task())
