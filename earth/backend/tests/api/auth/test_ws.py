from app import bus
from httpx_ws import aconnect_ws
from tests.util import is_subset

from eventbus.event import State, bye, get_cert, get_config, get_secrets
from eventbus.event_type import GET_AUTH, HELLO_INVALID_TOKEN, PUT_AUTH

from .conftest import EventQueue, set_src, yield_ws


async def test_ws_client(async_websocket_client, client_token):
    async for ws in yield_ws(async_websocket_client, client_token, "ws"):
        # send a state update from earth to client
        # s = state(eid="test.attr", value=123)
        eid = "test.attr"
        s = State(eid)
        await s.update(123)
        assert s.event == await ws.receive_json()
        await s.update(456)
        assert s.event == await ws.receive_json()


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


async def test_ws_gateway(async_client, async_websocket_client, create_trees):
    # gateway connection
    for i, tree in enumerate(create_trees):
        response = await async_client.get(f"/api/gateway_token/{tree.get('uuid')}")
        assert response.status_code == 200
        gateway_token = response.json()
        eq = EventQueue().queue
        connection_status_proto = {
            "eid": f'{tree["tree_id"]}.gateway:status.connected',
            "value": True,
            "type": "state",
            "dst": "#clients",
            "src": "#earth",
        }
        async for ws in yield_ws(async_websocket_client, gateway_token, "gateway/ws"):
            # get connection status
            assert is_subset(connection_status_proto, await eq.get())

            # send state update from gateway to clients
            src_addr = f'{tree["tree_id"]}.gateway'
            eid = f"{src_addr}:test.attr"
            s = State(eid=eid)
            s.event["value"] = 123
            s.event["src"] = src_addr
            await ws.send_json(s.event)
            assert s.event == await eq.get()
        connection_status_proto["value"] = False
        assert is_subset(connection_status_proto, await eq.get())


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


async def test_get_config(async_websocket_client, client_token):
    async for ws in yield_ws(async_websocket_client, client_token, "ws"):
        await ws.send_json(get_config())
        assert is_subset({"type": "put_config", "data": bus.config.get()}, await ws.receive_json())


async def test_get_secrets(async_client, async_websocket_client, create_trees):
    for i, tree in enumerate(create_trees):
        response = await async_client.get(f"/api/gateway_token/{tree.get('uuid')}")
        assert response.status_code == 200
        gateway_token = response.json()
        # eq = EventQueue().queue
        async for ws in yield_ws(async_websocket_client, gateway_token, "gateway/ws"):
            # config
            await ws.send_json(set_src(get_config(), tree.get("tree_id")))
            assert is_subset({"type": "put_config", "data": bus.config.get()}, await ws.receive_json())
            # secrets
            await ws.send_json(set_src(get_secrets(), tree.get("tree_id")))
            proto = {
                "type": "put_secrets",
                "data": {
                    "domain": f"{tree['tree_id']}.ws.leaf49.org",
                    "tree": {"tree_id": tree["tree_id"], "disabled": False},
                },
            }
            # print("\nresponse", await ws.receive_json())
            assert is_subset(proto, await ws.receive_json())
            # certificates
            await ws.send_json(set_src(get_cert(), tree.get("tree_id")))
            proto = {
                "data": {
                    "tree_id": tree.get("tree_id"),
                    "domain": f"{tree.get('tree_id')}.ws.leaf49.org",
                    "cert": "\n",
                    "privkey": "\n",
                    "version": "1970-01-01T00:00:00",
                },
                "type": "put_cert",
                "dst": tree.get("tree_id"),
                "src": "#earth",
            }
            assert is_subset(proto, await ws.receive_json())
