import json

from app.event_handlers import eventbus_config, eventbus_state
from httpx_ws import aconnect_ws
from tests.util import is_subset

import eventbus
from eventbus.event import bye, get_config, get_src_addr, state, state_action, state_update, update_config
from eventbus.event_type import GET_AUTH, HELLO_CONNECTED, HELLO_INVALID_TOKEN, PUT_AUTH, PUT_CONFIG, UPDATE_CONFIG

DEBUG = False


def set_src(event, src):
    event["src"] = src
    return event


async def test_ws_client(async_websocket_client, client_token):
    # client connection
    async with aconnect_ws("ws", async_websocket_client) as ws:
        # authenticate
        auth = await ws.receive_json()
        assert auth["type"] == GET_AUTH
        await ws.send_json({"type": PUT_AUTH, "token": client_token})
        # get the hello message
        hello = await ws.receive_json()
        assert hello["type"] == HELLO_CONNECTED
        # send some a state update event
        s = state(eid="test.attr", value=123)
        await eventbus.post(s)
        assert s == await ws.receive_json()

        # update the state
        s = state_update(s, value=456)
        await eventbus.post(s)
        assert s == await ws.receive_json()
        await ws.send_json(bye())


async def test_ws_gateway(async_client, async_websocket_client, create_trees):
    # gateway connection
    for i, tree in enumerate(create_trees):
        gateway_token = tree["branches"][0]["gateway_token"]

        async with aconnect_ws("/gateway/ws", async_websocket_client) as ws:
            # authenticate
            auth = await ws.receive_json()
            assert auth["type"] == GET_AUTH
            await ws.send_json({"type": PUT_AUTH, "token": gateway_token})
            # get the hello message
            hello = await ws.receive_json()
            assert hello["type"] == HELLO_CONNECTED
            await ws.send_json(bye())
            # no active connections
            connections = await async_client.get("/api/connections")
            connections = connections.json()
            for conn in connections.values():
                assert not conn["connected"]


async def test_ws_client_invalid_token(async_websocket_client):
    # client connection
    async with aconnect_ws("ws", async_websocket_client) as ws:
        # authenticate
        auth = await ws.receive_json()
        assert auth["type"] == GET_AUTH
        await ws.send_json({"type": PUT_AUTH, "token": "invalid_token"})
        # get the hello message
        hello = await ws.receive_json()
        assert hello["type"] == HELLO_INVALID_TOKEN


async def test_ws_gateway_invalid_token(async_websocket_client, create_trees):
    # gateway connection
    for i, _ in enumerate(create_trees):
        async with aconnect_ws("/gateway/ws", async_websocket_client) as ws:
            # authenticate
            auth = await ws.receive_json()
            assert auth["type"] == GET_AUTH
            await ws.send_json({"type": PUT_AUTH, "token": "invalid_token"})
            # get the hello message
            hello = await ws.receive_json()
            assert hello["type"] == HELLO_INVALID_TOKEN
            await ws.send_json(bye())


async def test_ws_bridge(async_client, async_websocket_client, create_trees, client_token):
    if DEBUG:
        print()
        eventbus.bus.Printer()

    # connect two gateways and two clients
    async with (
        aconnect_ws(
            "/gateway/ws",
            async_websocket_client,
            headers={"Authorization": f"Bearer {create_trees[0]['branches'][0]['gateway_token']}"},
        ) as gateway_ws_0,
        aconnect_ws(
            "/gateway/ws",
            async_websocket_client,
            headers={"Authorization": f"Bearer {create_trees[1]['branches'][0]['gateway_token']}"},
        ) as gateway_ws_1,
        aconnect_ws("/ws", async_websocket_client, headers={"Authorization": f"Bearer {client_token}"}) as client_ws_0,
        aconnect_ws("/ws", async_websocket_client, headers={"Authorization": f"Bearer {client_token}"}) as client_ws_1,
    ):
        tree_0 = create_trees[0]["tree_id"]
        tree_1 = create_trees[1]["tree_id"]
        tree_0_gateway_token = create_trees[0]["branches"][0]["gateway_token"]
        tree_1_gateway_token = create_trees[1]["branches"][0]["gateway_token"]
        branch_00 = create_trees[0]["branches"][0]["branch_id"]
        branch_01 = create_trees[0]["branches"][1]["branch_id"]
        branch_10 = create_trees[1]["branches"][0]["branch_id"]
        branch_11 = create_trees[1]["branches"][1]["branch_id"]
        src_00 = f"{tree_0}:{branch_00}"
        src_01 = f"{tree_0}:{branch_01}"
        src_10 = f"{tree_1}:{branch_10}"
        src_11 = f"{tree_1}:{branch_11}"

        # start conversation
        auth = await client_ws_0.receive_json()
        assert auth["type"] == GET_AUTH
        await client_ws_0.send_json({"type": PUT_AUTH, "token": client_token})
        hello = await client_ws_0.receive_json()
        assert hello["type"] == HELLO_CONNECTED
        assert not hello["param"]["gateway"]
        assert hello["param"]["versions"]["config"] == eventbus_config.get("version")
        client_ws_0_addr = hello["param"]["peer"]

        auth = await client_ws_1.receive_json()
        assert auth["type"] == GET_AUTH
        await client_ws_1.send_json({"type": PUT_AUTH, "token": client_token})
        hello = await client_ws_1.receive_json()
        assert hello["type"] == HELLO_CONNECTED
        assert not hello["param"]["gateway"]
        assert hello["param"]["versions"]["config"] == eventbus_config.get("version")
        client_ws_1_addr = hello["param"]["peer"]

        auth = await gateway_ws_0.receive_json()
        assert auth["type"] == GET_AUTH
        await gateway_ws_0.send_json({"type": PUT_AUTH, "token": tree_0_gateway_token})
        hello = await gateway_ws_0.receive_json()
        assert hello["type"] == HELLO_CONNECTED
        assert hello["param"]["peer"] == tree_0
        assert hello["param"]["gateway"]
        assert hello["param"]["versions"]["config"] == eventbus_config.get("version")

        auth = await gateway_ws_1.receive_json()
        assert auth["type"] == GET_AUTH
        await gateway_ws_1.send_json({"type": PUT_AUTH, "token": tree_1_gateway_token})
        hello = await gateway_ws_1.receive_json()
        assert hello["type"] == HELLO_CONNECTED
        assert hello["param"]["peer"] == tree_1
        assert hello["param"]["gateway"]
        assert hello["param"]["versions"]["config"] == eventbus_config.get("version")

        # connection status
        assert eventbus_state.state[f"{tree_0}:gateway:status:connected"][0]
        assert eventbus_state.state[f"{tree_1}:gateway:status:connected"][0]
        assert is_subset({"eid": "tree_0:gateway:status:connected", "value": True}, await client_ws_0.receive_json())
        assert is_subset({"eid": "tree_1:gateway:status:connected", "value": True}, await client_ws_0.receive_json())
        assert is_subset({"eid": "tree_0:gateway:status:connected", "value": True}, await client_ws_1.receive_json())
        assert is_subset({"eid": "tree_1:gateway:status:connected", "value": True}, await client_ws_1.receive_json())

        # check active connections
        connections = await async_client.get("/api/connections")
        assert connections.status_code == 200
        connections = connections.json()
        assert len(connections) >= 4

        # state update from gateway goes to all to clients
        s = state(eid=f"{src_00}:test1:attr", value="test 1")
        await gateway_ws_0.send_json(s)
        assert s == await client_ws_0.receive_json()
        assert s == await client_ws_1.receive_json()
        s = state(eid=f"{src_11}:test1:attr", value="test 2")
        await gateway_ws_0.send_json(s)
        assert s == await client_ws_0.receive_json()
        assert s == await client_ws_1.receive_json()

        # clients can also send state updates
        s = state(eid=f"{src_00}:test1:attr", value="test 3")
        await client_ws_0.send_json(s)
        assert s == await client_ws_0.receive_json()
        assert s == await client_ws_1.receive_json()
        await client_ws_1.send_json(s)
        assert s == await client_ws_0.receive_json()
        assert s == await client_ws_1.receive_json()

        # actions go to the gateway/branch
        s = state(eid=f"{src_01}:test4:attr", value="test 4")
        a = state_action(s, "test_action_1")
        await client_ws_0.send_json(a)
        assert a == await gateway_ws_0.receive_json()
        s = state(eid=f"{src_10}.:test4:attr", value="test 4")
        a = state_action(s, "test_action_1")
        await client_ws_0.send_json(a)
        assert a == await gateway_ws_1.receive_json()

        # client 0 get config
        await client_ws_0.send_json(set_src(get_config(), client_ws_0_addr))
        assert is_subset(
            {"type": PUT_CONFIG, "dst": client_ws_0_addr, "src": get_src_addr()}, await client_ws_0.receive_json()
        )
        # gateway 1 branch 1 get config
        await gateway_ws_1.send_json(set_src(get_config(), src_11))
        assert is_subset({"type": PUT_CONFIG, "dst": src_11, "src": get_src_addr()}, await gateway_ws_1.receive_json())
        # update config
        await eventbus.post(update_config(data={"test": "test update"}, dst="#branches"))
        await eventbus.post(update_config(data={"test": "test update"}, dst="#clients"))
        proto = {
            "type": UPDATE_CONFIG,
            "src": get_src_addr(),
            "data": {"test": "test update"},
        }
        assert is_subset(proto, await gateway_ws_0.receive_json())
        assert is_subset(proto, await gateway_ws_1.receive_json())
        assert is_subset(proto, await client_ws_0.receive_json())
        assert is_subset(proto, await client_ws_1.receive_json())

        # end conversation
        await gateway_ws_0.send_json(bye())
        await gateway_ws_1.send_json(bye())
        await client_ws_0.send_json(bye())
        await client_ws_1.send_json(bye())

        # no active connections
        connections = await async_client.get("/api/connections")
        connections = connections.json()
        for conn in connections.values():
            assert not conn["connected"]
        if DEBUG:
            print(json.dumps(connections, indent=2))

        # connection status
        assert not eventbus_state.state[f"{tree_0}:gateway:status:connected"][0]
        assert not eventbus_state.state[f"{tree_1}:gateway:status:connected"][0]
