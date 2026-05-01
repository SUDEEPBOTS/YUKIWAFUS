import os
from dotenv import load_dotenv

load_dotenv("Simple.env")

# ── Bot ───────────────────────────────────────────────────────────────────────
API_ID          = int(os.getenv("API_ID", "0"))
API_HASH        = os.getenv("API_HASH", "")
BOT_TOKEN       = os.getenv("BOT_TOKEN", "")

# ── Owner & Sudo ──────────────────────────────────────────────────────────────
OWNER_ID        = int(os.getenv("OWNER_ID", "0"))
SUDO_USERS      = list(map(int, os.getenv("SUDO_USERS", "").split() if os.getenv("SUDO_USERS") else []))

# ── Database ──────────────────────────────────────────────────────────────────
MONGO_DB_URI    = os.getenv("MONGO_DB_URI", "")

# ── Channels & Chats ──────────────────────────────────────────────────────────
LOG_CHANNEL     = int(os.getenv("LOG_CHANNEL", "0"))
SUPPORT_CHAT    = os.getenv("SUPPORT_CHAT", "")
UPDATE_CHANNEL  = os.getenv("UPDATE_CHANNEL", "")

# ── Waifu API ─────────────────────────────────────────────────────────────────
WAIFU_API_URL   = os.getenv("WAIFU_API_URL", "https://wafus.vercel.app")
WAIFU_API_KEY   = os.getenv("WAIFU_API_KEY", "")

# ── Economy ───────────────────────────────────────────────────────────────────
GUESS_COINS     = int(os.getenv("GUESS_COINS", "40"))
BATTLE_REWARD   = int(os.getenv("BATTLE_REWARD", "100"))
CLAIM_COOLDOWN  = int(os.getenv("CLAIM_COOLDOWN", "86400"))   # 24h in seconds

# ── Bot Settings ──────────────────────────────────────────────────────────────
BANNED_USERS    = set()

