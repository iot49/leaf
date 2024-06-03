from eventbus.event_emitter import EventEmitter


async def test_async_1():
    em = EventEmitter()
    event_stack = []

    @em.on("type1", "type2")
    def listener(**event):
        event_stack.append(event)

    await em.emit({"type": "type1", "a": 1})
    assert event_stack == [{"type": "type1", "a": 1}]


async def test_async_2():
    em = EventEmitter()
    event_stack = []

    @em.on("type1", "type2")
    def listener1(**event):
        event_stack.append(event)

    @em.on("type1")
    def listener2(**event):
        event_stack.append(event)

    await em.emit({"type": "type1", "a": 1})
    assert event_stack == [{"type": "type1", "a": 1}, {"type": "type1", "a": 1}]

    await em.emit({"type": "type2", "b": 2})
    assert event_stack == [{"type": "type1", "a": 1}, {"type": "type1", "a": 1}, {"type": "type2", "b": 2}]


async def test_all():
    em = EventEmitter()
    event_stack = []

    @em.on("type1", "type2")
    def listener1(**event):
        event_stack.append(event)

    @em.on("type1")
    def listener2(**event):
        event_stack.append(event)

    @em.on("*")
    def all(**event):
        event_stack.append(("all", event))

    await em.emit({"type": "type1", "a": 1})
    assert event_stack == [
        {"type": "type1", "a": 1},
        {"type": "type1", "a": 1},
        ("all", {"a": 1, "type": "type1"}),
    ]
    event_stack = []

    await em.emit({"type": "type2", "b": 2})
    assert event_stack == [{"type": "type2", "b": 2}, ("all", {"type": "type2", "b": 2})]
