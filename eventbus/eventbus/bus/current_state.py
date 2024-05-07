from .. import Event, EventBus, event_type, post
from ..event import state


class CurrentState(EventBus):
    """Keep tack of state values."""

    def __init__(self):
        from .. import subscribe

        super().__init__()
        self._state = {}
        subscribe(self)

    async def post(self, event: Event) -> None:
        """Update state or send current values. Called by the bridge.

        Events:
        - state
        - get_state
        - put_state (outgoing)
        """
        et = event["type"]
        if et == event_type.STATE:
            # update current state
            self._state[event["eid"]] = (event["value"], event["timestamp"])
        elif et == event_type.GET_STATE:
            # send current state values
            dst = event["src"]
            assert dst is not None
            for eid, (value, ts) in self._state.items():
                await post(state(eid, value, dst=dst, timestamp=ts))

    @property
    def state(self) -> dict:
        """Return current state values.
        Returns:
            dict: Current state values. Do not modify!
        """
        return self._state
