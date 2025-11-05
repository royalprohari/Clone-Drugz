import re
import logging
import asyncio
import importlib
from sys import argv
from pyrogram import idle, Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from Clonify.utils.database import get_assistant
from config import API_ID, API_HASH, OWNER_ID, LOGGER_ID, CLONE_LOGGER, SUPPORT_CHAT
from Clonify import app
from Clonify.misc import SUDOERS
from Clonify.utils.database import clonebotdb
from Clonify.utils.database.clonedb import has_user_cloned_any_bot, get_owner_id_from_db
from Clonify.utils.decorators.language import language
import pyrogram.errors
import requests
from datetime import datetime

CLONES = set()

C_BOT_DESC = (
    "Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\n"
    "Vɪsɪᴛ: @CloneMusicRobot ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n"
    " - Uᴘᴅᴀᴛᴇ: @HeartBeat_Offi\n"
    " - Sᴜᴘᴘᴏʀᴛ: @HeartBeat_Fam"
)

C_BOT_COMMANDS = [
    {"command": "/start", "description": "start bot"},
    {"command": "/help", "description": "get commands"},
    {"command": "/clone", "description": "make own bot"},
    {"command": "/play", "description": "play song"},
    {"command": "/pause", "description": "pause current track"},
    {"command": "/resume", "description": "resume paused track"},
    {"command": "/skip", "description": "skip current song"},
    {"command": "/end", "description": "stop song"},
]


@app.on_message(filters.command("clone"))
@language
async def clone_txt(client, message, _):
    userbot = await get_assistant(message.chat.id)
    userid = message.from_user.id
    has_already_cbot = await has_user_cloned_any_bot(userid)

    if has_already_cbot and message.from_user.id != OWNER_ID:
        return await message.reply_text(_["C_B_H_0"])

    if len(message.command) <= 1:
        return await message.reply_text(_["C_B_H_1"])

    bot_token = message.text.split("/clone", 1)[1].strip()
    mi = await message.reply_text(_["C_B_H_2"])

    try:
        ai = Client(
            session_name=":memory_clone:",  # Memory-only session
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="Clonify.cplugin"),
            workdir="/dev/shm",  # RAM-only storage
        )
        await ai.start()
        bot = await ai.get_me()
        bot_users = await ai.get_users(bot.username)
        bot_id = bot_users.id
        c_b_owner_fname = message.from_user.first_name
        c_bot_owner = message.from_user.id
    except (AccessTokenExpired, AccessTokenInvalid):
        return await mi.edit_text(_["C_B_H_3"])
    except Exception as e:
        if "database is locked" in str(e).lower():
            await message.reply_text(_["C_B_H_4"])
        else:
            await mi.edit_text(f"An error occurred: {str(e)}")
        return

    await mi.edit_text(_["C_B_H_5"])

    try:
        await app.send_message(
            CLONE_LOGGER,
            f"**#NewClonedBot**\n\n**Bᴏᴛ:** {bot.mention}\n**Username:** @{bot.username}\n"
            f"**Bot ID:** `{bot_id}`\n\n**Owner:** [{c_b_owner_fname}](tg://user?id={c_bot_owner})",
        )
        await userbot.send_message(bot.username, "/start")

        details = {
            "bot_id": bot.id,
            "is_bot": True,
            "user_id": message.from_user.id,
            "name": bot.first_name,
            "token": bot_token,
            "username": bot.username,
            "channel": "ProBotts",
            "support": "ProBotGc",
            "premium": False,
            "Date": False,
        }
        clonebotdb.insert_one(details)
        CLONES.add(bot.id)

        # Set bot commands
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/setMyCommands",
            json={"commands": C_BOT_COMMANDS},
        )

        # Set bot description
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/setMyDescription",
            data={"description": C_BOT_DESC},
        )

        await mi.edit_text(_["C_B_H_6"].format(bot.username))
    except BaseException as e:
        logging.exception("Error while cloning bot.")
        await mi.edit_text(
            f"⚠️ <b>ᴇʀʀᴏʀ:</b>\n\n<code>{e}</code>\n\n**Forward this message to @ProBotGc for help.**"
        )


@app.on_message(
    filters.command(
        [
            "delbot",
            "rmbot",
            "delcloned",
            "delclone",
            "deleteclone",
            "removeclone",
            "cancelclone",
        ]
    )
)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            return await message.reply_text(_["C_B_H_8"])

        query_value = " ".join(message.command[1:])
        if query_value.startswith("@"):
            query_value = query_value[1:]
        await message.reply_text(_["C_B_H_9"])

        cloned_bot = clonebotdb.find_one(
            {"$or": [{"token": query_value}, {"username": query_value}]}
        )

        if not cloned_bot:
            return await message.reply_text(_["C_B_H_11"])

        C_OWNER = get_owner_id_from_db(cloned_bot["bot_id"])
        OWNERS = [OWNER_ID, C_OWNER]
        if message.from_user.id not in OWNERS:
            return await message.reply_text(_["NOT_C_OWNER"].format(SUPPORT_CHAT))

        clonebotdb.delete_one({"_id": cloned_bot["_id"]})
        CLONES.discard(cloned_bot["bot_id"])

        await message.reply_text(_["C_B_H_10"])
        await app.send_message(CLONE_LOGGER, f"Deleted cloned bot:\n{cloned_bot}")
    except Exception as e:
        logging.exception(e)
        await message.reply_text(_["C_B_H_12"])


async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots...")
        bots = list(clonebotdb.find())

        for idx, bot in enumerate(bots, start=1):
            bot_token = bot["token"]

            # Verify bot token
            if requests.get(f"https://api.telegram.org/bot{bot_token}/getMe").status_code != 200:
                clonebotdb.delete_one({"token": bot_token})
                continue

            ai = Client(
                session_name=f":memory:{idx}",  # unique in-memory session
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                plugins=dict(root="Clonify.cplugin"),
                workdir="/dev/shm",  # RAM-only directory
            )

            try:
                await ai.start()
                bot_data = await ai.get_me()
                CLONES.add(bot_data.id)
                print(f"✅ Started bot #{idx} -> @{bot_data.username}")
                await asyncio.sleep(3)
            except Exception as e:
                logging.exception(f"Error starting bot #{idx}: {e}")
                continue

        await app.send_message(CLONE_LOGGER, "✅ All cloned bots started successfully!")
    except Exception as e:
        logging.exception(f"Error while restarting bots: {e}")


@app.on_message(filters.command("delallclone") & filters.user(OWNER_ID))
@language
async def delete_all_cloned_bots(client, message, _):
    try:
        await message.reply_text(_["C_B_H_14"])
        clonebotdb.delete_many({})
        CLONES.clear()
        await message.reply_text(_["C_B_H_15"])
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while deleting all cloned bots.")


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    try:
        user_id = message.from_user.id
        cloned_bots = list(clonebotdb.find({"user_id": user_id}))
        if not cloned_bots:
            return await message.reply_text(_["C_B_H_16"])

        text = f"**Your Cloned Bots ({len(cloned_bots)}):**\n\n"
        for bot in cloned_bots:
            text += f"• **{bot['name']}** — @{bot['username']}\n"
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("Error while fetching your cloned bots.")


@app.on_message(filters.command("cloned") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            return await message.reply_text(_["C_B_H_13"])

        total_clones = len(cloned_bots)
        text = f"**Total Cloned Bots:** `{total_clones}`\n\n"

        for bot in cloned_bots[:10]:
            try:
                owner = await client.get_users(bot["user_id"])
                owner_name = owner.first_name
                owner_link = f"tg://user?id={bot['user_id']}"
            except Exception:
                owner_name = "Unknown"
                owner_link = "#"

            text += (
                f"**{bot['name']}** (@{bot['username']})\n"
                f"Owner: [{owner_name}]({owner_link})\n\n"
            )

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("Error while listing cloned bots.")


@app.on_message(filters.command("totalbots") & SUDOERS)
@language
async def total_cloned_bots(client, message, _):
    try:
        total = clonebotdb.count_documents({})
        await message.reply_text(f"**Total Cloned Bots:** `{total}`")
    except Exception as e:
        logging.exception(e)
        await message.reply_text("Error while counting cloned bots.")
