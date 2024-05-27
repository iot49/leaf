from eventbus.eid import eid2addr, eid2eid, eid2lid
from eventbus.event import (
    get_auth,
    get_src_addr,
    get_state,
    hello_connected,
    make_event,
    ping,
    pong,
    put_config,
)
from eventbus.event_type import GET_AUTH, GET_STATE, HELLO_CONNECTED, PING, PONG, PUT_CONFIG, STATE, STATE_ACTION


def is_subset(first, second):
    sentinel = object()
    return all(first[key] == second.get(key, sentinel) for key in first)


def test_make():
    event = make_event(GET_STATE, "@5", a="a")
    proto = {"a": "a", "type": "get_state", "dst": "@5", "src": get_src_addr()}
    assert event == proto


def test_eid():
    eid = "a.b:c.d"
    assert eid2lid(eid) == "a.b:c"
    assert eid2addr(eid) == "a.b"
    assert eid2eid("c.d") == "#earth:c.d"
    assert eid2lid("#earth:c.d") == "#earth:c"
    assert eid2addr("#earth:c.d") == "#earth"


def test_events():
    assert ping == {"type": PING}
    assert pong == {"type": PONG}
    assert get_state() == {"type": GET_STATE, "dst": "#server", "src": get_src_addr()}
    event = hello_connected(param={})
    proto = {"type": HELLO_CONNECTED, "param": {}}
    assert event == proto
    event = put_config({"a": 1})
    proto = {"data": {"a": 1}, "type": PUT_CONFIG, "dst": "#server", "src": get_src_addr()}
    assert event == proto
    assert is_subset({"type": GET_AUTH}, get_auth())


async def test_state():
    from eventbus.event import State

    leaf_id = "leaf_id"
    attr_id = "attr_id"
    entity = f"{leaf_id}.{attr_id}"
    value = 123
    state_event = State(entity)
    await state_event.update(value)
    proto = {
        "type": STATE,
        "value": value,
        "src": get_src_addr(),
        "dst": "#clients",
    }
    assert is_subset(proto, state_event.event)

    ts = state_event.event["timestamp"]
    await state_event.update(value + 1)
    proto["value"] = value + 1
    assert is_subset(proto, state_event.event)
    assert state_event.event["timestamp"] >= ts

    act_event = await state_event.act("action", "param")

    proto = {
        "type": STATE_ACTION,
        "action": "action",
        "param": "param",
        "eid": state_event.eid,
        "src": get_src_addr(),
        "dst": eid2addr(state_event.eid),
    }
    assert is_subset(proto, act_event)
