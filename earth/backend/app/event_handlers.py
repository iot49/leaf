import os

from eventbus.bus import Config, Counter, CurrentState


def init_eventbus():
    global eventbus_config, eventbus_state
    from app.env import env as env  # noqa: E402

    config_file = os.path.join(env.CONFIG_DIR, "config.json")  # type: ignore

    eventbus_config = Config(config_file=config_file)
    eventbus_state = CurrentState()
    Counter("counter.count")


eventbus_config = None
eventbus_state = None
init_eventbus()
