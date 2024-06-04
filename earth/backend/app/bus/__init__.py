import asyncio
import os

from eventbus.bus import Config, Counter, CurrentState, Reflect

from ..env import env
from .certificates import Certificates
from .secrets import Secrets

config = Config(config_file=os.path.join(env.CONFIG_DIR, "config.json"))
state = CurrentState()
print("created CurrentState, id=", id(state))
Secrets()
Certificates()
reflect = Reflect(interval=10)
counter = Counter(eid="counter.count", interval=10)
loop = asyncio.get_event_loop()
loop.create_task(reflect.emitter_task())
loop.create_task(counter.counter_task())
