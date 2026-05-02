import asyncio
import random

from pyrogram import Client, enums, filters
from pyrogram.types import Message

import config
from YUKIWAFUS import app
from YUKIWAFUS.database.Mangodb import chatsdb
from YUKIWAFUS.utils.api import get_random_waifu
from YUKIWAFUS.utils.helpers import sc

# ── Config ────────────────────────────────────────────────────────────────────
SPAWN_AFTER   = 20       # spawn after every N messages
SPAWN_TIMEOUT = 120      # waifu disappears after 2 min
SPAWN_VARY    = 5        # ±5 messages random variance

RARITY_EMOJI = {
    "Common":    "⚪",
    "Uncommon":  "🟢",
    "Rare":      "🔵",
    "Epic":      "🟣",
    "Legendary": "🟡",
    "Mythic":    "🔴",
}

# ── In-memory ─────────────────────────────────────────────────────────────────
message_counts: dict = {}   # chat_id → count
spawn_targets: dict  = {}   # chat_id → target count
active_spawns: dict  = {}   # chat_id → waifu data (imported by guess.py)


# ── DB Helpers ────────────────────────────────────────────────────────────────
async def is_chat_enabled(chat_id: int) -> bool:
    doc = await chatsdb.find_one({"chat_id": chat_id})
    return doc.get("spawn", True) if doc else True


async def set_chat_spawn(chat_id: int, enabled: bool):
    await chatsdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"spawn": enabled}},
        upsert=True,
    )


async def get_next_target(chat_id: int) -> int:          # ✅ async fix
    doc = await chatsdb.find_one({"chat_id": chat_id})
    custom = doc.get("spawn_after", SPAWN_AFTER) if doc else SPAWN_AFTER
    base = custom + random.randint(-SPAWN_VARY, SPAWN_VARY)
    return message_counts.get(chat_id, 0) + max(5, base)


# ── Message Counter ───────────────────────────────────────────────────────────
@app.on_message(filters.group & ~filters.bot & ~filters.service)
async def count_messages(client: Client, message: Message):
    chat_id = message.chat.id

    if not await is_chat_enabled(chat_id):
        return

    # Init — set both immediately before any await to avoid race condition
    if chat_id not in message_counts:
        message_counts[chat_id] = 0
        spawn_targets[chat_id] = SPAWN_AFTER   # safe default before await
        spawn_targets[chat_id] = await get_next_target(chat_id)

    message_counts[chat_id] += 1

    # Already active spawn
    if chat_id in active_spawns:
        return

    # Time to spawn?
    if message_counts[chat_id] >= spawn_targets.get(chat_id, SPAWN_AFTER):
        message_counts[chat_id] = 0
        spawn_targets[chat_id] = await get_next_target(chat_id)  # ✅ await
        asyncio.create_task(spawn_waifu(client, chat_id))


# ── Spawn Logic ───────────────────────────────────────────────────────────────
async def spawn_waifu(client: Client, chat_id: int):
    waifu = await get_random_waifu()
    if not waifu:
        return

    rarity = waifu.get("rarity", "Common")
    emoji  = RARITY_EMOJI.get(rarity, "◈")

    caption = (
        f"<blockquote>"
        f"{emoji} <b>{sc('A wild waifu has appeared')}!</b>\n"
        f"🏷 {sc('Rarity')}: <b>{rarity}</b>"
        f"</blockquote>\n\n"
        f"<i>{sc('Can you guess her name?')}</i>\n"
        f"<code>/guess &lt;name&gt;</code>"
    )

    try:
        msg = await client.send_photo(
            chat_id=chat_id,
            photo=waifu["img_url"],
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
        )

        # Register in active_spawns (guess.py reads this)
        active_spawns[chat_id] = {
            **waifu,
            "message_id": msg.id,
            "chat_id": chat_id,
        }

        # Auto-disappear
        await asyncio.sleep(SPAWN_TIMEOUT)

        if chat_id in active_spawns and active_spawns[chat_id].get("message_id") == msg.id:
            active_spawns.pop(chat_id, None)
            try:
                await msg.edit_caption(
                    f"💨 <b>{sc('The waifu ran away')}!</b>\n"
                    f"<i>{sc('Nobody guessed in time')}~</i>",
                    parse_mode=enums.ParseMode.HTML,
                )
            except Exception:
                pass

    except Exception:
        active_spawns.pop(chat_id, None)


# ── /spawnon & /spawnoff ──────────────────────────────────────────────────────
@app.on_message(filters.command("spawnon") & filters.group)
async def spawnon_handler(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status.value not in ("administrator", "creator"):
        return await message.reply_text(f"❌ {sc('Admins only!')}")

    await set_chat_spawn(message.chat.id, True)
    await message.reply_text(f"✅ {sc('Waifu spawn enabled in this group!')}")


@app.on_message(filters.command("spawnoff") & filters.group)
async def spawnoff_handler(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status.value not in ("administrator", "creator"):
        return await message.reply_text(f"❌ {sc('Admins only!')}")

    await set_chat_spawn(message.chat.id, False)
    active_spawns.pop(message.chat.id, None)
    await message.reply_text(f"✅ {sc('Waifu spawn disabled in this group!')}")


# ── /fspawn (force spawn - sudo only) ────────────────────────────────────────
@app.on_message(filters.command("fspawn") & filters.user(config.SUDO_USERS + [config.OWNER_ID]))
async def fspawn_handler(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in active_spawns:
        return await message.reply_text(f"⚠️ {sc('A waifu is already active here!')}")

    try:
        await message.delete()
    except Exception:
        pass  # Bot might not have delete permission in group — that's fine

    asyncio.create_task(spawn_waifu(client, chat_id))


# ── /setspawn ─────────────────────────────────────────────────────────────────
@app.on_message(filters.command("setspawn") & filters.group)
async def setspawn_handler(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status.value not in ("administrator", "creator"):
        return await message.reply_text(f"❌ {sc('Admins only!')}")

    if len(message.command) < 2:
        current = SPAWN_AFTER
        doc = await chatsdb.find_one({"chat_id": message.chat.id})
        if doc and doc.get("spawn_after"):
            current = doc["spawn_after"]
        return await message.reply_text(
            f"ℹ️ {sc('Current spawn rate')}: <b>{current} {sc('messages')}</b>\n\n"
            f"{sc('Usage')}: <code>/setspawn &lt;number&gt;</code>\n"
            f"{sc('Example')}: <code>/setspawn 30</code>",
            parse_mode=enums.ParseMode.HTML,
        )

    try:
        count = int(message.command[1])
        if count < 5:
            return await message.reply_text(f"❌ {sc('Minimum is 5 messages.')}")
        if count > 500:
            return await message.reply_text(f"❌ {sc('Maximum is 500 messages.')}")
    except ValueError:
        return await message.reply_text(f"❌ {sc('Enter a valid number.')}")

    await chatsdb.update_one(
        {"chat_id": message.chat.id},
        {"$set": {"spawn_after": count}},
        upsert=True,
    )

    # Update in-memory target
    spawn_targets[message.chat.id] = message_counts.get(message.chat.id, 0) + count

    await message.reply_text(
        f"✅ {sc('Spawn rate set to')} <b>{count} {sc('messages')}</b>!",
        parse_mode=enums.ParseMode.HTML,
    )

