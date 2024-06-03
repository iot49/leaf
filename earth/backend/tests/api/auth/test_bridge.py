from app import bus
from tests.util import is_subset

from eventbus import event_type
from eventbus.bus.server import Server
from eventbus.eid import eid2addr
from eventbus.event import State, get_config, make_event
from eventbus.eventbus import post

from .conftest import set_src, yield_ws


async def test_bridge_1x1(async_client, async_websocket_client, create_trees, client_token):
    async for client_ws in yield_ws(async_websocket_client, client_token, "ws"):
        tree = create_trees[0]
        response = await async_client.get(f"/api/gateway_token/{tree.get('uuid')}")
        assert response.status_code == 200
        gateway_token = response.json()
        async for gateway_ws in yield_ws(async_websocket_client, gateway_token, "gateway/ws"):
            # status connected ...
            assert is_subset({"type": "state"}, await client_ws.receive_json())

            # config: only to requester
            await client_ws.send_json(get_config())
            assert is_subset({"type": "put_config", "data": bus.config.get()}, await client_ws.receive_json())
            await gateway_ws.send_json(set_src(get_config(), tree.get("tree_id")))
            assert is_subset({"type": "put_config", "data": bus.config.get()}, await gateway_ws.receive_json())

            # state: gateway -> client
            src_addr = f'{tree["tree_id"]}.gateway'
            eid = f"{src_addr}:test.attr"
            s = State(eid)
            s.event["value"] = 123
            s.event["src"] = src_addr
            await gateway_ws.send_json(s.event)
            assert s.event == s._event
            assert s.event == await client_ws.receive_json()

            # action: client -> gateway
            turn_on = make_event(
                event_type.STATE_ACTION, dst=eid2addr(eid), eid=eid, action="turn_on", param={"duration": 10}
            )
            act_event = await s.act("turn_on", {"duration": 10})
            assert act_event == turn_on
            await client_ws.send_json(turn_on)
            proto = {
                "eid": eid,
                "action": "turn_on",
                "param": {"duration": 10},
                "type": "action",
                "dst": src_addr,
            }
            assert is_subset(proto, await gateway_ws.receive_json())


async def post_receive(poster, receivers, dst="#clients"):
    event = {"type": "test", "data": dst, "dst": dst}
    await poster.send_json(event)
    for receiver in receivers:
        rec = await receiver.receive_json()
        # print(f"POST_RECEIVE: {event} -> {rec}")
        assert is_subset({"type": "test", "data": dst}, rec)


async def test_bridge_2x2(async_client, async_websocket_client, create_trees, client_token):
    print()
    Server.CONNECTIONS.clear()
    trees = create_trees
    gateway_token = []
    for tree in trees:
        response = await async_client.get(f"/api/gateway_token/{tree.get('uuid')}")
        assert response.status_code == 200
        gateway_token.append(response.json())
    async for gateway_ws0 in yield_ws(async_websocket_client, gateway_token[0], "gateway/ws"):
        async for gateway_ws1 in yield_ws(async_websocket_client, gateway_token[1], "gateway/ws"):
            async for client_ws0 in yield_ws(async_websocket_client, client_token, "ws"):
                async for client_ws1 in yield_ws(async_websocket_client, client_token, "ws"):
                    gateway0_addr, gateway1_addr, client0_addr, client1_addr = Server.CONNECTIONS.keys()

                    # gateways -> clients
                    await post_receive(gateway_ws0, [client_ws0, client_ws1], "#clients")
                    await post_receive(gateway_ws1, [client_ws0, client_ws1], "#clients")

                    # gateway -> client
                    await post_receive(gateway_ws0, [client_ws0], client0_addr)
                    await post_receive(gateway_ws0, [client_ws1], client1_addr)
                    await post_receive(gateway_ws1, [client_ws0], client0_addr)
                    await post_receive(gateway_ws1, [client_ws1], client1_addr)

                    # client -> gateway
                    await post_receive(client_ws0, [gateway_ws0], gateway0_addr)
                    await post_receive(client_ws0, [gateway_ws1], gateway1_addr)
                    await post_receive(client_ws1, [gateway_ws0], gateway0_addr)
                    await post_receive(client_ws1, [gateway_ws1], gateway1_addr)

                    # finish: make sure all messages are received

                    # earth -> clients
                    await post({"type": "test", "data": "#clients", "dst": "#clients"})
                    assert is_subset({"type": "test", "data": "#clients"}, await client_ws0.receive_json())
                    assert is_subset({"type": "test", "data": "#clients"}, await client_ws1.receive_json())

                    # earth -> branches
                    await post({"type": "test", "data": "#branches", "dst": "#branches"})
                    assert is_subset({"type": "test", "data": "#branches"}, await gateway_ws0.receive_json())
                    assert is_subset({"type": "test", "data": "#branches"}, await gateway_ws1.receive_json())

    # assert we are disconnected from all connections
    assert all(not c["connected"] for c in Server.CONNECTIONS.values())
    assert all(c["disconnected_at"] > c["connected_at"] for c in Server.CONNECTIONS.values())
