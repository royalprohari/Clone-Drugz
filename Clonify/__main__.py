import asyncio
import importlib
import logging

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

from autorestart import autorestart  # autorestart

# Setup simple console logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(message)s",
)


async def init():
    if not config.STRING1:
        LOGGER(__name__).error("String Session not filled, please provide a valid session.")
        exit()

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
    LOGGER("Clonify.plugins").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    await userbot.start()
    await PRO.start()

    try:
        await PRO.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("Clonify").error(
            "𝗣𝗹𝗭 𝗦𝗧𝗔𝗥𝗧 𝗬𝗢𝗨𝗥 𝗟𝗢𝗚 𝗚𝗥𝗢𝗨𝗣 𝗩𝗢𝗜𝗖𝗘𝗖𝗛𝗔𝗧/𝗖𝗛𝗔𝗡𝗡𝗘𝗟\n\n𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗦𝗧𝗢𝗣........"
        )
        exit()
    except Exception as e:
        LOGGER("Clonify").warning(f"Stream call failed: {e}")

    await PRO.decorators()
    await restart_bots()

    LOGGER("Clonify").info(
        "╔═════ஜ۩۞۩ஜ════╗\n  ☠︎︎𝗠𝗔𝗗𝗘 𝗕𝗬 𝗣𝗿𝗼𝗕𝗼t𝘀☠︎︎\n╚═════ஜ۩۞۩ஜ════╝"
    )

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("Clonify").info("𝗦𝗧𝗢𝗣 𝗠𝗨𝗦𝗜𝗖🎻 𝗕𝗢𝗧..")


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(init())

        # AutoRestart section (using logging instead of undefined log())
        logging.info("AutoRestart system started.")
        autorestart()

    except KeyboardInterrupt:
        logging.warning("AutoRestart system stopped manually.")
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
