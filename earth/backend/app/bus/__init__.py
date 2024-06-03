import asyncio
import os

from eventbus.bus import Config, Counter, CurrentState, Printer

from ..env import env
from .certificates import Certificates
from .secrets import Secrets

config = Config(config_file=os.path.join(env.CONFIG_DIR, "config.json"))
state = CurrentState()
Secrets()
Certificates()
# Printer()

counter = Counter(eid="counter.count", interval=3)
loop = asyncio.get_event_loop()
loop.create_task(counter.counter_task())
