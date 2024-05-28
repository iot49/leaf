import logging

import version  # type: ignore
from ota32 import OTA as OTA32  # type: ignore

from app import wifi  # type: ignore
from eventbus import EventBus, event_type, post

from . import DOMAIN

logger = logging.getLogger(__name__)


class OTA(EventBus):
    async def post(self, event):
        if event.get("type") == event_type.OTA:
            try:
                await self.perform_ota(**event.get("param", {}))
            except TypeError as e:
                await post({"type": event_type.OTA_FAILED, "incorrect param": str(e)})

    async def perform_ota(self, tag=version.TAG, sha=None, dry_run=False):
        if version.TAG == tag:
            logger.debug(f"already on release {tag} - no OTA needed")
            await post({"type": event_type.OTA_COMPLETE, "tag": tag})
            return

        async with wifi:
            try:
                ota = OTA32(self.progress_cb, dry_run=dry_run)
                # url = f"https://github.com/{version.GITHUB_REPOSITORY}/releases/download/{tag}/{version.BOARD}-firmware.bin"
                url = f"http://{DOMAIN}/api/vm/{tag}/{version.BOARD}/firmware.bin"
                await ota.ota(url, sha)
                await post({"type": event_type.OTA_COMPLETE, "tag": tag})
            except OSError as e:
                logger.debug(f"OTA failed: {e}")
                await post({"type": event_type.OTA_FAILED, "error": str(e)})

    async def progress_cb(self, bytes_written):
        await post({"type": event_type.OTA_PROGRESS, "bytes_written": bytes_written})


OTA()
