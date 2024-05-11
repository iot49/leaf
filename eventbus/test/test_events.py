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
    state_action,
    state_update,
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
    event = hello_connected("peer", param={})
    proto = {"type": HELLO_CONNECTED, "dst": "peer", "param": {}, "src": get_src_addr()}
    assert event == proto
    event = put_config({"a": 1})
    proto = {"data": {"a": 1}, "type": PUT_CONFIG, "dst": "#server", "src": get_src_addr()}
    assert event == proto
    assert is_subset({"type": GET_AUTH}, get_auth())


def test_state():
    from eventbus.event import state

    leaf_id = "leaf_id"
    attr_id = "attr_id"
    entity = f"{leaf_id}.{attr_id}"
    value = 123
    state_event = state(entity, value)
    proto = {
        "type": STATE,
        "value": value,
        "src": get_src_addr(),
        "dst": "#clients",
    }
    assert is_subset(proto, state_event)

    ts = state_event["timestamp"]
    state_event = state_update(state_event, value + 1)
    proto["value"] = value + 1
    assert is_subset(proto, state_event)
    assert state_event["timestamp"] >= ts

    action = state_action(state_event, "action", "param")
    proto = {
        "type": STATE_ACTION,
        "action": "action",
        "param": "param",
        "lid": eid2lid(state_event["eid"]),
        "src": get_src_addr(),
        "dst": eid2addr(state_event["eid"]),
    }
    assert is_subset(proto, action)
