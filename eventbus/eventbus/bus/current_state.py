from .. import Event, EventBus, event_type
from ..event import State


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
        et = event.get("type")
        if et == event_type.STATE:
            # update current state
            self._state[event["eid"]] = (event["value"], event["timestamp"])
        elif et == event_type.GET_STATE:
            # send current state values
            dst = event["src"]
            assert dst is not None
            # make copy of keys to protect against co-modification
            for eid in list(self._state.keys()):
                value, ts = self._state[eid]
                state = State(eid, dst=dst)
                await state.update(value, timestamp=ts)

    @property
    def state(self) -> dict:
        """Return current state values.
        Returns:
            dict: Current state values. Do not modify!
        """
        return self._state
