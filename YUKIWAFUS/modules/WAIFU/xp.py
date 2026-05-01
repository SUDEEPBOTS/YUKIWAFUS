import asyncio
import random
from html import escape

from pyrogram import Client, enums, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from YUKIWAFUS import app
from YUKIWAFUS.database.Mangodb import game_statsdb, balancedb, chatsdb
from YUKIWAFUS.utils.helpers import sc

# ══════════════════════════════════════════════════════════════════════════════
# ✅ CONFIG
# ══════════════════════════════════════════════════════════════════════════════
XP_PER_MSG_MIN  = 3
XP_PER_MSG_MAX  = 8
XP_COOLDOWN     = 10        # seconds between XP gains per user per chat
LEVEL_UP_DELETE = 30        # auto-delete level-up notif after N seconds

# ── Level thresholds — XP needed to reach level N ────────────────────────────
def xp_for_level(level: int) -> int:
    """XP required to reach `level` from level 0."""
    return int(100 * (level ** 1.5))


def level_from_xp(xp: int) -> int:
    level = 0
    while xp >= xp_for_level(level + 1):
        level += 1
    return level


def xp_progress(xp: int) -> tuple[int, int, int]:
    """Returns (current_level, xp_in_level, xp_needed_for_next)."""
    level     = level_from_xp(xp)
    xp_start  = xp_for_level(level)
    xp_end    = xp_for_level(level + 1)
    return level, xp - xp_start, xp_end - xp_start


# ── Level perks — coins bonus on level up ────────────────────────────────────
LEVEL_COIN_REWARD = {
    5:  100,
    10: 250,
    15: 400,
    20: 600,
    25: 800,
    30: 1000,
}

LEVEL_TITLES = {
    5:  "🌱 ɴᴏᴠɪᴄᴇ",
    10: "⚔️ ꜰɪɢʜᴛᴇʀ",
    15: "🔥 ᴡᴀʀʀɪᴏʀ",
    20: "💎 ᴇʟɪᴛᴇ",
    25: "🌟 ᴍᴀsᴛᴇʀ",
    30: "👑 ʟᴇɢᴇɴᴅ",
}

# ── Progress bar ──────────────────────────────────────────────────────────────
def _progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int((current / total) * length) if total else 0
    filled = min(filled, length)
    bar    = "█" * filled + "░" * (length - filled)
    return f"[{bar}]"


# ── In-memory cooldown ────────────────────────────────────────────────────────
_xp_cd: dict = {}   # (user_id, chat_id) → last xp time


# ══════════════════════════════════════════════════════════════════════════════
# ✅ DB HELPERS
# ══════════════════════════════════════════════════════════════════════════════
async def get_user_xp(user_id: int, chat_id: int) -> dict:
    doc = await game_statsdb.find_one({"user_id": user_id, "chat_id": chat_id})
    return doc or {"user_id": user_id, "chat_id": chat_id, "xp": 0, "level": 0}


async def add_user_xp(user_id: int, chat_id: int, amount: int) -> dict:
    result = await game_statsdb.find_one_and_update(
        {"user_id": user_id, "chat_id": chat_id},
        {"$inc": {"xp": amount}},
        upsert=True,
        return_document=True,
    )
    return result or {"xp": amount}


async def add_coins(user_id: int, amount: int):
    await balancedb.update_one(
        {"user_id": user_id},
        {"$inc": {"coins": amount}},
        upsert=True,
    )


async def is_xp_enabled(chat_id: int) -> bool:
    doc = await chatsdb.find_one({"chat_id": chat_id})
    return doc.get("xp_enabled", True) if doc else True


async def set_xp_enabled(chat_id: int, enabled: bool):
    await chatsdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"xp_enabled": enabled}},
        upsert=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ✅ MESSAGE LISTENER — XP gain
# ══════════════════════════════════════════════════════════════════════════════
@app.on_message(filters.group & ~filters.bot & ~filters.service & ~filters.command([]))
async def xp_listener(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not await is_xp_enabled(chat_id):
        return

    # Cooldown check
    import time
    now = time.time()
    key = (user_id, chat_id)
    if now - _xp_cd.get(key, 0) < XP_COOLDOWN:
        return
    _xp_cd[key] = now

    xp_gain = random.randint(XP_PER_MSG_MIN, XP_PER_MSG_MAX)

    old_doc    = await get_user_xp(user_id, chat_id)
    old_xp     = old_doc.get("xp", 0)
    old_level  = level_from_xp(old_xp)

    new_doc    = await add_user_xp(user_id, chat_id, xp_gain)
    new_xp     = new_doc.get("xp", old_xp + xp_gain)
    new_level  = level_from_xp(new_xp)

    # Level up!
    if new_level > old_level:
        asyncio.create_task(_notify_level_up(client, message, user_id, new_level))


async def _notify_level_up(client, message: Message, user_id: int, new_level: int):
    user    = message.from_user
    ref     = f"<a href='tg://user?id={user.id}'>{escape(user.first_name)}</a>"

    # Perk coins
    coin_reward = LEVEL_COIN_REWARD.get(new_level, 0)
    if coin_reward:
        await add_coins(user_id, coin_reward)

    title = LEVEL_TITLES.get(new_level, "")
    title_line = f"\n🏷 {sc('New Title')} : <b>{title}</b>" if title else ""
    coin_line  = f"\n🪙 +<b>{coin_reward} {sc('bonus coins')}!</b>" if coin_reward else ""

    msg = await message.reply_text(
        f"<blockquote>"
        f"<emoji id='6294063539069917326'>⚡</emoji> "
        f"<b>{sc('Level Up')}!</b>"
        f"</blockquote>\n\n"
        f"🎉 {ref} {sc('reached')} <b>{sc('Level')} {new_level}</b>!"
        f"{title_line}"
        f"{coin_line}",
        parse_mode=enums.ParseMode.HTML,
    )

    await asyncio.sleep(LEVEL_UP_DELETE)
    try:
        await msg.delete()
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# ✅ /level — show XP card
# ══════════════════════════════════════════════════════════════════════════════
@app.on_message(filters.command(["level", "xp", "rank"]))
async def level_cmd(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    chat_id = message.chat.id
    doc     = await get_user_xp(target.id, chat_id)
    total_xp = doc.get("xp", 0)

    level, xp_in_level, xp_needed = xp_progress(total_xp)
    bar    = _progress_bar(xp_in_level, xp_needed)
    ref    = f"<a href='tg://user?id={target.id}'>{escape(target.first_name)}</a>"

    # Rank in this chat
    rank_pos = await game_statsdb.count_documents(
        {"chat_id": chat_id, "xp": {"$gt": total_xp}}
    ) + 1

    title = ""
    for lvl in sorted(LEVEL_TITLES.keys(), reverse=True):
        if level >= lvl:
            title = LEVEL_TITLES[lvl]
            break

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"🏆 {sc('Group Top')}",
            callback_data=f"xp_top:{chat_id}",
        ),
    ]])

    await message.reply_photo(
        photo=config.WAIFU_PICS[0],
        caption=(
            f"<blockquote>"
            f"<emoji id='6294063539069917326'>⚡</emoji> "
            f"<b>{sc('XP Card')} — {ref}</b>"
            f"</blockquote>\n\n"
            f"🏅 <b>{sc('Level')} :</b> <code>{level}</code>\n"
            f"✨ <b>{sc('Total XP')} :</b> <code>{total_xp:,}</code>\n"
            f"📊 <b>{sc('Progress')} :</b> {bar} "
            f"<code>{xp_in_level}/{xp_needed}</code>\n"
            f"🏆 <b>{sc('Chat Rank')} :</b> <code>#{rank_pos}</code>\n"
            + (f"🏷 <b>{sc('Title')} :</b> {title}\n" if title else "") +
            f"\n<i>{sc('Keep chatting to level up')}~</i>"
        ),
        parse_mode=enums.ParseMode.HTML,
        reply_markup=keyboard,
        has_spoiler=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ✅ Top XP leaderboard callback
# ══════════════════════════════════════════════════════════════════════════════
@app.on_callback_query(filters.regex(r"^xp_top:"))
async def xp_top_cb(client: Client, cq: CallbackQuery):
    chat_id = int(cq.data.split(":")[1])

    cursor = game_statsdb.find(
        {"chat_id": chat_id}, {"user_id": 1, "xp": 1}
    ).sort("xp", -1).limit(10)

    top = await cursor.to_list(length=10)

    if not top:
        return await cq.answer(sc("No XP data yet!"), show_alert=True)

    text = (
        f"<blockquote>"
        f"<emoji id='6294063539069917326'>⚡</emoji> "
        f"<b>{sc('Top XP — This Group')}</b>"
        f"</blockquote>\n\n"
    )

    medals = ["🥇", "🥈", "🥉"]
    for i, doc in enumerate(top, 1):
        medal   = medals[i - 1] if i <= 3 else f"{i}."
        level   = level_from_xp(doc.get("xp", 0))
        try:
            u    = await client.get_users(doc["user_id"])
            name = escape(u.first_name)
        except Exception:
            name = str(doc["user_id"])
        text += f"{medal} <b>{name}</b> — Lv.<code>{level}</code> · <code>{doc['xp']:,}</code> xp\n"

    await cq.message.reply_text(text, parse_mode=enums.ParseMode.HTML)
    await cq.answer()


# ══════════════════════════════════════════════════════════════════════════════
# ✅ /xpon / /xpoff — group admin toggle
# ══════════════════════════════════════════════════════════════════════════════
@app.on_message(filters.command("xpon") & filters.group)
async def xpon_cmd(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status.value not in ("administrator", "owner"):
        return await message.reply_text(f"❌ {sc('Admins only!')}")

    await set_xp_enabled(message.chat.id, True)
    await message.reply_text(
        f"<blockquote>"
        f"<emoji id='6001483331709966655'>✅</emoji> "
        f"<b>{sc('XP system enabled in this group')}!</b>"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_message(filters.command("xpoff") & filters.group)
async def xpoff_cmd(client: Client, message: Message):
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status.value not in ("administrator", "owner"):
        return await message.reply_text(f"❌ {sc('Admins only!')}")

    await set_xp_enabled(message.chat.id, False)
    await message.reply_text(
        f"<blockquote>"
        f"<emoji id='5998834801472182366'>❌</emoji> "
        f"<b>{sc('XP system disabled in this group')}.</b>"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML,
    )

