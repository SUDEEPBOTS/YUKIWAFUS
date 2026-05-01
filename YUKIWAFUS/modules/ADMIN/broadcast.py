import asyncio

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from pyrogram.types import Message

import config
from YUKIWAFUS import app
from YUKIWAFUS.database.Mangodb import usersdb, chatsdb
from YUKIWAFUS.utils.helpers import sc

IS_BROADCASTING = False


# ── DB Helpers ────────────────────────────────────────────────────────────────
async def get_all_chats() -> list:
    return [doc["chat_id"] async for doc in chatsdb.find({"chat_id": {"$lt": 0}})]

async def get_all_users() -> list:
    return [doc["user_id"] async for doc in usersdb.find({"user_id": {"$gt": 0}})]


# ── /broadcast ────────────────────────────────────────────────────────────────
@app.on_message(filters.command("broadcast") & filters.user(config.SUDO_USERS + [config.OWNER_ID]))
async def broadcast_handler(client: Client, message: Message):
    global IS_BROADCASTING

    if IS_BROADCASTING:
        return await message.reply_text(f"⚠️ {sc('Broadcast already in progress!')}")

    # ── Flags ─────────────────────────────────────────────────────────────────
    flags = message.text.lower()
    to_groups = "-nogroup" not in flags
    to_users  = "-user" in flags
    pin       = "-pin" in flags
    pin_loud  = "-pinloud" in flags

    # ── Get content ───────────────────────────────────────────────────────────
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text(
            f"❓ {sc('Reply to a message to broadcast it.')}\n\n"
            f"<b>{sc('Flags')}:</b>\n"
            f"<code>-user</code> — {sc('send to users too')}\n"
            f"<code>-nogroup</code> — {sc('skip groups')}\n"
            f"<code>-pin</code> — {sc('pin silently')}\n"
            f"<code>-pinloud</code> — {sc('pin with notification')}",
            parse_mode=enums.ParseMode.HTML,
        )

    IS_BROADCASTING = True
    status = await message.reply_text(f"📢 {sc('Broadcasting...')}")

    total_groups = total_users = sent_g = sent_u = failed_g = failed_u = pin_count = 0

    # ── Broadcast to Groups ───────────────────────────────────────────────────
    if to_groups:
        chats = await get_all_chats()
        total_groups = len(chats)
        for chat_id in chats:
            try:
                m = await client.forward_messages(
                    chat_id=chat_id,
                    from_chat_id=reply.chat.id,
                    message_ids=reply.id,
                )
                if pin or pin_loud:
                    try:
                        await m.pin(disable_notification=pin)
                        pin_count += 1
                    except Exception:
                        pass
                sent_g += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                wait = int(fw.value)
                if wait > 200:
                    failed_g += 1
                    continue
                await asyncio.sleep(wait)
                try:
                    await client.forward_messages(chat_id, reply.chat.id, reply.id)
                    sent_g += 1
                except Exception:
                    failed_g += 1
            except Exception:
                failed_g += 1

    # ── Broadcast to Users ────────────────────────────────────────────────────
    if to_users:
        users = await get_all_users()
        total_users = len(users)
        for user_id in users:
            try:
                await client.forward_messages(
                    chat_id=user_id,
                    from_chat_id=reply.chat.id,
                    message_ids=reply.id,
                )
                sent_u += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                wait = int(fw.value)
                if wait > 200:
                    failed_u += 1
                    continue
                await asyncio.sleep(wait)
            except (UserIsBlocked, InputUserDeactivated):
                failed_u += 1
            except Exception:
                failed_u += 1

    IS_BROADCASTING = False

    # ── Result ────────────────────────────────────────────────────────────────
    text = f"<blockquote>📢 <b>{sc('Broadcast Complete')}</b></blockquote>\n\n"

    if to_groups:
        text += (
            f"👥 <b>{sc('Groups')}:</b>\n"
            f"  ✅ {sc('Sent')}: <b>{sent_g}</b>\n"
            f"  ❌ {sc('Failed')}: <b>{failed_g}</b>\n"
            f"  📌 {sc('Pinned')}: <b>{pin_count}</b>\n\n"
        )
    if to_users:
        text += (
            f"👤 <b>{sc('Users')}:</b>\n"
            f"  ✅ {sc('Sent')}: <b>{sent_u}</b>\n"
            f"  ❌ {sc('Failed')}: <b>{failed_u}</b>\n"
        )

    await status.edit_text(text, parse_mode=enums.ParseMode.HTML)

