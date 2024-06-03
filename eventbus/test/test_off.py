from eventbus import eventbus


async def test_off():
    seq = []

    @eventbus.on("test")
    async def test1(**event):
        seq.append(event)

    @eventbus.on("test")
    async def test2(**event):
        seq.append(event)

    await eventbus.emit({"type": "test", "item": "one"})
    await eventbus.emit({"type": "test", "item": "two"})
    eventbus.off(test1)
    await eventbus.emit({"type": "test", "item": "three"})

    assert seq == [
        {"type": "test", "item": "one"},
        {"type": "test", "item": "one"},
        {"type": "test", "item": "two"},
        {"type": "test", "item": "two"},
        {"type": "test", "item": "three"},
    ]
