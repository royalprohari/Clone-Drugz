import asyncio
import importlib
import logging
import signal
import sys

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Clonify import LOGGER, app, userbot
from Clonify.core.call import PRO
from Clonify.misc import sudo
from Clonify.plugins import ALL_MODULES
from Clonify.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS
from Clonify.plugins.tools.clone import restart_bots

from autorestart import autorestart


# ✅ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s",
)


def shutdown_handler(*_):
    logging.warning("🛑 SIGTERM/SIGINT received — shutting down...")
    try:
        for task in asyncio.all_tasks():
            task.cancel()
    except:
        pass
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)


async def init():

    if not config.STRING1:
        LOGGER(__name__).error("String Session not filled.")
        sys.exit(1)

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)

    except Exception as e:
        LOGGER(__name__).warning(f"Error loading banned users: {e}")

    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("Clonify.plugins" + all_module)

    LOGGER("Clonify.plugins").info("✅ All features loaded")

    await userbot.start()
    await PRO.start()

    # Stream call
    try:
        await PRO.stream_call(
            "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
        )

    except NoActiveGroupCall:
        LOGGER("Clonify").error(
            "START GROUP VOICE CHAT FIRST"
        )
        sys.exit(1)

    except Exception as e:
        LOGGER("Clonify").warning(f"Stream call failed: {e}")

    await PRO.decorators()
    await restart_bots()

    LOGGER("Clonify").info(
        "╔═════ஜ۩۞۩ஜ════╗\n"
        " ✅ CLONIFY IS LIVE ✅\n"
        "╚═════ஜ۩۞۩ஜ════╝"
    )

    # ✅ Run AutoRestart in background
    asyncio.create_task(autorestart())

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("Clonify").info("🛑 BOT STOPPED")


if __name__ == "__main__":

    try:
        asyncio.run(init())

    except KeyboardInterrupt:
        logging.warning("🛑 Stopped manually")

    except Exception as e:
        logging.exception(f"❌ Fatal error: {e}")
        sys.exit(1)
