import json
from typing import Any

from .. import Event, EventBus, event_type, post
from ..event import put_config


class Config(EventBus):
    """Configuration."""

    def __init__(self, config_file: str):
        from .. import subscribe

        super().__init__()
        config = {}
        try:
            with open(config_file) as f:
                config = json.load(f)
        except FileNotFoundError:
            pass
        self._config = config

        subscribe(self)

    async def post(self, event: Event) -> None:
        et = event["type"]
        if et == event_type.GET_CONFIG:
            await post(put_config(dst=event["src"], data=self._config))
        elif et == event_type.UPDATE_CONFIG:
            self._config = event["data"]

    def get(self, path=None, default=None) -> Any:
        """Get configuration value.

        Examples:
            config.get("version") -> "1.0.0"
            config.get("wifi")
        """
        if not path:
            return self._config
        path = path.split("/")
        res = self._config
        try:
            for p in path:
                res = res[p]
        except (KeyError, AttributeError):
            return default
        return res
