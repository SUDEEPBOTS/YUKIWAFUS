import asyncio
import importlib

from pyrogram import idle

import config
from YUKIWAFUS import LOGGER, app
from YUKIWAFUS.modules import ALL_MODULES


async def init():
    await app.start()

    for module in ALL_MODULES:
        importlib.import_module("YUKIWAFUS.modules." + module)

    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGGER.info("  ✦ All Modules Loaded  ✦")
    LOGGER.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    LOGGER.info(
        "╔═════ஜ۩۞۩ஜ════╗\n"
        "  ✦ YUKIWAFUS Started ✦\n"
        "╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()
    await app.stop()
    LOGGER.info("YUKIWAFUS Stopped.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
  
