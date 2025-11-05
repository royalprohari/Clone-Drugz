import re
import logging
import asyncio
import importlib
from sys import argv
from pyrogram import idle, Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from Clonify.utils.database import get_assistant, clonebotdb
from Clonify.utils.database.clonedb import has_user_cloned_any_bot, get_owner_id_from_db
from config import API_ID, API_HASH, OWNER_ID, LOGGER_ID, CLONE_LOGGER, SUPPORT_CHAT
from Clonify import app
from Clonify.misc import SUDOERS
from Clonify.utils.decorators.language import language
import requests
import pyrogram.errors
from datetime import datetime

CLONES = set()

C_BOT_DESC = (
    "Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\n"
    "Vɪsɪᴛ: @CloneMusicRobot ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n"
    " - Uᴘᴅᴀᴛᴇ: @HeartBeat_Offi\n"
    " - Sᴜᴘᴘᴏʀᴛ: @HeartBeat_Fam"
)

C_BOT_COMMANDS = [
    {"command": "/start", "description": "𝗌ᴛᴀʀᴛ ʙᴏᴛ"},
    {"command": "/help", "description": "ɢᴇᴛ ᴄᴏᴍᴍᴀɴᴅ𝗌"},
    {"command": "/clone", "description": "ᴍᴀᴋᴇ ᴏᴡɴ ʙᴏᴛ"},
    {"command": "/play", "description": "ᴘʟᴀʏ 𝗌ᴏɴɢ"},
    {"command": "/pause", "description": "ᴘᴀᴜ𝗌ᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ"},
    {"command": "/resume", "description": "ʀᴇ𝗌ᴜᴍᴇ ᴘᴀᴜѕᴇᴅ ᴛʀᴀᴄᴋ"},
    {"command": "/skip", "description": "𝗌ᴋɪᴘ ᴄᴜʀʀᴇɴᴛ 𝗌ᴏɴɢ"},
    {"command": "/end", "description": "𝗌ᴛᴏᴘ 𝗌ᴏɴɢ"}
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
            session_name=":memory_clone:",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="Clonify.cplugin"),
            workdir="/dev/shm",
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
            return await message.reply_text(_["C_B_H_4"])
        else:
            return await mi.edit_text(f"An error occurred: {str(e)}")

    await mi.edit_text(_["C_B_H_5"])
    try:
        await app.send_message(
            CLONE_LOGGER,
            f"**#NewClonedBot**\n\n**Bᴏᴛ:** {bot.mention}\n**Username:** @{bot.username}\n**Bot ID:** `{bot_id}`\n\n**Owner:** [{c_b_owner_fname}](tg://user?id={c_bot_owner})",
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

        # Set commands
        requests.post(f"https://api.telegram.org/bot{bot_token}/setMyCommands", json={"commands": C_BOT_COMMANDS})
        # Set description
        requests.post(f"https://api.telegram.org/bot{bot_token}/setMyDescription", data={"description": C_BOT_DESC})

        await mi.edit_text(_["C_B_H_6"].format(bot.username))
    except Exception as e:
        logging.exception("Error while cloning bot.")
        await mi.edit_text(f"⚠️ Error: {e}")


@app.on_message(filters.command("delbot") & SUDOERS)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            return await message.reply_text(_["C_B_H_8"])

        query_value = message.command[1]
        if query_value.startswith("@"):
            query_value = query_value[1:]
        await message.reply_text(_["C_B_H_9"])

        cloned_bot = clonebotdb.find_one({"$or": [{"token": query_value}, {"username": query_value}]})
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
    """Restart all cloned bots with logging."""
    global CLONES
    try:
        logging.info("Restarting all cloned bots...")
        bots = list(clonebotdb.find())
        bot_number = 1

        for bot in bots:
            bot_token = bot["token"]

            # Verify token
            response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            if response.status_code != 200:
                logging.error(f"Invalid/expired token for bot: {bot_token}")
                clonebotdb.delete_one({"token": bot_token})
                continue

            ai = Client(
                session_name=f":memory:{bot_number}",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=bot_token,
                plugins=dict(root="Clonify.cplugin"),
                workdir="/dev/shm",
            )
            await ai.start()

            bot_data = await ai.get_me()
            if bot_data.id not in CLONES:
                CLONES.add(bot_data.id)

            # Log bot info
            log_message = f"✅ Started bot #{bot_number} -> Name: {bot_data.first_name}, Username: @{bot_data.username}, ID: {bot_data.id}"
            logging.info(log_message)
            print(log_message)

            bot_number += 1
            await asyncio.sleep(3)

        await app.send_message(CLONE_LOGGER, "✅ All cloned bots started successfully!")
    except Exception as e:
        logging.exception("Error while restarting bots.")


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
        await message.reply_text("Error deleting all cloned bots.")


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    user_id = message.from_user.id
    cloned_bots = list(clonebotdb.find({"user_id": user_id}))
    if not cloned_bots:
        return await message.reply_text(_["C_B_H_16"])

    text = f"**Your Cloned Bots ({len(cloned_bots)}):**\n\n"
    for bot in cloned_bots:
        text += f"• Name: {bot['name']} — @{bot['username']}\n"
    await message.reply_text(text)


@app.on_message(filters.command("cloned") & SUDOERS)
@language
async def list_cloned_bots(client, message, _):
    cloned_bots = list(clonebotdb.find())
    if not cloned_bots:
        return await message.reply_text(_["C_B_H_13"])

    text = f"**Total Cloned Bots:** `{len(cloned_bots)}`\n\n"
    for bot in cloned_bots[:10]:
        try:
            owner = await client.get_users(bot["user_id"])
            owner_name = owner.first_name
            owner_link = f"tg://user?id={bot['user_id']}"
        except Exception:
            owner_name = "Unknown"
            owner_link = "#"
        text += f"• {bot['name']} (@{bot['username']}) — Owner: [{owner_name}]({owner_link})\n"
    await message.reply_text(text)


@app.on_message(filters.command("totalbots") & SUDOERS)
@language
async def total_cloned_bots(client, message, _):
    total = clonebotdb.count_documents({})
    await message.reply_text(f"**Total Cloned Bots:** `{total}`")
