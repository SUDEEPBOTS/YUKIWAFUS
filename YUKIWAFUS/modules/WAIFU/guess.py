import asyncio
import time
import random
from datetime import datetime
from html import escape

from pyrogram import Client, enums, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from YUKIWAFUS import app
from YUKIWAFUS.database.Mangodb import collectiondb, balancedb, game_statsdb
from YUKIWAFUS.utils.api import get_random_waifu

# ── In-memory state ───────────────────────────────────────────────────────────
active_waifus: dict = {}       # chat_id → waifu data + meta
guessed_chats: set = set()     # chat_ids where waifu already guessed
cooldowns: dict = {}           # user_id → last_guess timestamp

COOLDOWN_SEC = 10
COINS_REWARD = 40
WAIFU_TIMEOUT = 120            # waifu runs away after 2 min

RARITY_EMOJI = {
    "Common":    "⚪",
    "Uncommon":  "🟢",
    "Rare":      "🔵",
    "Epic":      "🟣",
    "Legendary": "🟡",
    "Mythic":    "🔴",
}


# ── Cooldown helpers ──────────────────────────────────────────────────────────
def is_on_cooldown(user_id: int) -> bool:
    last = cooldowns.get(user_id, 0)
    return (time.time() - last) < COOLDOWN_SEC

def remaining_cooldown(user_id: int) -> int:
    last = cooldowns.get(user_id, 0)
    return max(0, int(COOLDOWN_SEC - (time.time() - last)))

def set_cooldown(user_id: int):
    cooldowns[user_id] = time.time()


# ── DB helpers ────────────────────────────────────────────────────────────────
async def add_waifu_to_collection(user_id: int, username: str, first_name: str, waifu: dict):
    await collectiondb.update_one(
        {"user_id": user_id},
        {
            "$set": {"username": username, "first_name": first_name},
            "$push": {"waifus": waifu},
        },
        upsert=True,
    )

async def add_coins(user_id: int, amount: int) -> int:
    result = await balancedb.find_one_and_update(
        {"user_id": user_id},
        {"$inc": {"coins": amount}},
        upsert=True,
        return_document=True,
    )
    return (result or {}).get("coins", amount)

async def increment_guesses(user_id: int):
    await game_statsdb.update_one(
        {"user_id": user_id},
        {"$inc": {"total_guesses": 1}},
        upsert=True,
    )


# ── Send waifu to group ───────────────────────────────────────────────────────
async def send_waifu(client: Client, chat_id: int):
    """Fetch random waifu from API and send to group."""
    waifu = await get_random_waifu()
    if not waifu:
        return

    rarity = waifu.get("rarity", "Common")
    emoji = RARITY_EMOJI.get(rarity, "◈")

    caption = (
        f"<blockquote>🌸 <b>A wild waifu appeared!</b>\n"
        f"{emoji} <b>Rarity:</b> {rarity}</blockquote>\n\n"
        f"<i>Can you guess her name? Use /guess &lt;name&gt;</i>"
    )

    try:
        msg = await client.send_photo(
            chat_id=chat_id,
            photo=waifu["img_url"],
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
        )

        active_waifus[chat_id] = {
            **waifu,
            "message_id": msg.id,
            "timestamp": time.time(),
        }
        guessed_chats.discard(chat_id)

        # Auto runaway after timeout
        await asyncio.sleep(WAIFU_TIMEOUT)
        if chat_id in active_waifus and active_waifus[chat_id].get("message_id") == msg.id:
            active_waifus.pop(chat_id, None)
            await client.send_message(
                chat_id,
                f"💨 <b>The waifu ran away!</b> Nobody guessed her in time~",
                parse_mode=enums.ParseMode.HTML,
            )
    except Exception as e:
        pass


# ── /guess Command ────────────────────────────────────────────────────────────
@app.on_message(filters.command(["guess", "grab", "hunt", "collect", "protecc"]))
async def guess_handler(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Cooldown check
    if is_on_cooldown(user_id):
        return await message.reply_text(
            f"⏳ Cooldown! Wait <b>{remaining_cooldown(user_id)}s</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    # No active waifu
    if chat_id not in active_waifus:
        return await message.reply_text("❌ No waifu to guess right now!")

    # Already guessed
    if chat_id in guessed_chats:
        return await message.reply_text("❌ This waifu was already guessed!")

    guess = " ".join(message.command[1:]).strip().lower()
    if not guess:
        return await message.reply_text("Usage: <code>/guess &lt;name&gt;</code>", parse_mode=enums.ParseMode.HTML)

    waifu = active_waifus[chat_id]
    correct_name = waifu["name"].lower()
    name_parts = correct_name.split()

    is_correct = (
        guess == correct_name
        or sorted(guess.split()) == sorted(name_parts)
        or guess in name_parts
    )

    set_cooldown(user_id)

    if is_correct:
        guessed_chats.add(chat_id)
        active_waifus.pop(chat_id, None)

        time_taken = int(time.time() - waifu.get("timestamp", time.time()))
        new_balance = await add_coins(user_id, COINS_REWARD)
        await add_waifu_to_collection(
            user_id,
            message.from_user.username or "",
            message.from_user.first_name,
            waifu,
        )
        await increment_guesses(user_id)

        rarity = waifu.get("rarity", "Common")
        emoji = RARITY_EMOJI.get(rarity, "◈")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌸 My Harem", switch_inline_query_current_chat=f"col.{user_id}")]
        ])

        await message.reply_photo(
            photo=waifu["img_url"],
            caption=(
                f"<blockquote>🎊 <b><a href='tg://user?id={user_id}'>{escape(message.from_user.first_name)}</a></b> guessed correctly!</blockquote>\n\n"
                f"📛 <b>Name:</b> {waifu['name']}\n"
                f"{emoji} <b>Rarity:</b> {rarity}\n"
                f"🏷 <b>Tag:</b> {waifu.get('event_tag', 'Standard')}\n\n"
                f"🪙 <b>+{COINS_REWARD} coins</b> → Balance: <b>{new_balance}</b>\n"
                f"⏱ Time: <b>{time_taken}s</b>"
            ),
            parse_mode=enums.ParseMode.HTML,
            reply_markup=keyboard,
        )
    else:
        msg_id = waifu.get("message_id")
        keyboard = None
        if msg_id:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("👀 View Again", url=f"https://t.me/c/{str(chat_id)[4:]}/{msg_id}")]
            ])
        await message.reply_text(
            "❌ <b>Wrong!</b> Try again~ 🕵️",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=keyboard,
        )

