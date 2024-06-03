from eventbus import event_type, eventbus
from eventbus.bus import Config
from eventbus.event import get_config, put_config


async def test_config():
    n = 0
    cfg = {"test_config": "test"}

    @eventbus.on(event_type.PUT_CONFIG)
    def put(data, **event):
        nonlocal n, cfg
        assert data == {} if n == 0 else cfg
        n += 1

    config = Config("")
    await eventbus.emit(get_config())
    assert config.get() == {}

    await eventbus.emit(put_config(cfg))
