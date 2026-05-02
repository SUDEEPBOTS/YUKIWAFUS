<div align="center">

<img src="https://i.ibb.co/x8tCyc9n/4a3347e4f573589a9bf8b2740f68a70a.jpg" width="280px" style="border-radius: 50%"/>

# 🌸 YUKIWAFUS

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=F783AC&center=true&vCenter=true&width=500&lines=Waifu+Collection+Bot;Powered+by+Pyrogram;Guess+%7C+Collect+%7C+Trade+%7C+Battle;70x+Better+Than+The+Rest+%F0%9F%94%A5" alt="Typing SVG" />

<br/>

[![Stars](https://img.shields.io/github/stars/YOURNAME/YUKIWAFUS?style=for-the-badge&logo=github&color=f783ac&labelColor=1a1a2e)](https://github.com/YOURNAME/YUKIWAFUS/stargazers)
[![Forks](https://img.shields.io/github/forks/YOURNAME/YUKIWAFUS?style=for-the-badge&logo=github&color=c084fc&labelColor=1a1a2e)](https://github.com/YOURNAME/YUKIWAFUS/network/members)
[![Issues](https://img.shields.io/github/issues/YOURNAME/YUKIWAFUS?style=for-the-badge&logo=github&color=fb7185&labelColor=1a1a2e)](https://github.com/YOURNAME/YUKIWAFUS/issues)
[![License](https://img.shields.io/github/license/YOURNAME/YUKIWAFUS?style=for-the-badge&color=a78bfa&labelColor=1a1a2e)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e)](https://python.org)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0.106-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white&labelColor=1a1a2e)](https://pyrogram.org)

<br/>

> **🌸 A premium Telegram waifu collection bot — guess, collect, trade & battle your waifus!**
> Built with Pyrogram · MongoDB · Async · Smart Anti-Spam

<br/>

[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20on-Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)](https://heroku.com/deploy?template=https://github.com/YOURNAME/YUKIWAFUS)
[![Deploy on Render](https://img.shields.io/badge/Deploy%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/deploy?repo=https://github.com/YOURNAME/YUKIWAFUS)
[![Deploy on Railway](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app/new/template?template=https://github.com/YOURNAME/YUKIWAFUS)

</div>

---

## ✨ Features

<img align="right" src="https://files.catbox.moe/ey2jzp.jpeg" width="180px"/>

- 🌸 **Auto Spawn** — Waifus spawn after N group messages
- 🎯 **Smart Guess** — Fuzzy name matching, multi-word support
- ⚔️ **Battle System** — 1v1 waifu battles with rarity stats
- 🗂 **Harem** — View your full collection inline
- ❤️ **Favourites** — Pin up to 5 waifus to your profile
- 🔄 **2-Way Trade** — Trade waifus with confirm/cancel
- 🌸 **Sakura Economy** — Earn coins, pay, leaderboard
- 🛡 **Anti-Spam** — Per-user rate limit, spawn farm protection
- 🔍 **Inline Search** — Search global DB or any user's collection
- 📊 **Stats & Ping** — Live bot health dashboard
- 📢 **Broadcast** — Owner-level announcements
- 🗃 **Group Logger** — Logs bot add/remove to log channel

---

## 🗂 Project Structure

```
YUKIWAFUS/
├── YUKIWAFUS/
│   ├── __init__.py          # Pyrogram client
│   ├── __main__.py          # Module auto-loader
│   ├── logging.py           # Colorlog setup
│   ├── database/
│   │   └── Mangodb.py       # All MongoDB collections
│   ├── utils/
│   │   ├── api.py           # Waifu API helpers
│   │   └── helpers.py       # sc(), cmd() utils
│   └── modules/
│       ├── WAIFU/
│       │   ├── start.py
│       │   ├── spawn.py     # Auto spawn + anti-spam
│       │   ├── guess.py
│       │   ├── harem.py
│       │   ├── hclaim.py
│       │   ├── battle.py
│       │   ├── fav.py
│       │   ├── trade.py
│       │   ├── balance.py
│       │   └── daily.py
│       ├── ADMIN/
│       │   ├── addwaifu.py
│       │   ├── sudo.py
│       │   └── broadcast.py
│       └── TOOLS/
│           ├── ping.py
│           ├── stats.py
│           ├── group.py
│           └── inline_query.py
├── config.py
└── requirements.txt
```

---

## ⚙️ Configuration

Create a `config.py` or set environment variables:

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | Telegram API Hash |
| `BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | ✅ | MongoDB connection string |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `LOG_CHANNEL` | ✅ | Channel/group ID for bot logs |
| `SUDO_USERS` | ❌ | List of sudo user IDs |
| `WAIFU_API_URL` | ✅ | Waifu API base URL |
| `WAIFU_PICS` | ❌ | List of fallback photo URLs |

---

## 🚀 Deployment

### 📦 Method 1 — VPS (Recommended)

**Requirements:** Ubuntu 20.04+ · Python 3.11+ · MongoDB

```bash
# 1. Clone the repo
git clone https://github.com/YOURNAME/YUKIWAFUS
cd YUKIWAFUS

# 2. Install Python 3.11 (if not present)
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip

# 3. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure
cp config.example.py config.py
nano config.py   # fill in your values

# 6. Run
python -m YUKIWAFUS
```

**Run as a background service (systemd):**

```bash
sudo nano /etc/systemd/system/yukiwafus.service
```

```ini
[Unit]
Description=YUKIWAFUS Telegram Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/YUKIWAFUS
ExecStart=/home/ubuntu/YUKIWAFUS/venv/bin/python -m YUKIWAFUS
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable yukiwafus
sudo systemctl start yukiwafus

# Check logs
sudo journalctl -u yukiwafus -f
```

---

### 🟣 Method 2 — Heroku

> ⚠️ Free tier no longer available. Requires Eco/Basic dyno ($5/mo)

1. Click **Deploy on Heroku** button above
2. Fill in all config vars in the Heroku dashboard
3. Set dyno type to `worker` (not `web`)
4. Enable the dyno after deploy

```bash
# Or via CLI
heroku create yukiwafus-bot
heroku config:set BOT_TOKEN=xxx API_ID=xxx API_HASH=xxx MONGO_URI=xxx
git push heroku main
heroku ps:scale worker=1
```

**`Procfile`** (create this in root):
```
worker: python -m YUKIWAFUS
```

---

### 🟢 Method 3 — Render

1. Click **Deploy on Render** button above
2. Select **Background Worker** (not Web Service)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python -m YUKIWAFUS`
5. Add all environment variables

> ✅ Render free tier works for bots (no sleep for background workers)

---

### 🚂 Method 4 — Railway

1. Click **Deploy on Railway** button above
2. Connect your GitHub repo
3. Add environment variables in the Railway dashboard
4. Railway auto-detects Python and deploys

```bash
# Or via CLI
railway login
railway init
railway up
```

---

### 🐳 Method 5 — Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "YUKIWAFUS"]
```

```bash
docker build -t yukiwafus .
docker run -d \
  -e BOT_TOKEN=xxx \
  -e API_ID=xxx \
  -e API_HASH=xxx \
  -e MONGO_URI=xxx \
  -e OWNER_ID=xxx \
  -e LOG_CHANNEL=xxx \
  --name yukiwafus \
  yukiwafus
```

---

## 📋 Commands

| Command | Description | Access |
|---|---|---|
| `/start` | Start the bot | All |
| `/guess <name>` | Guess active waifu | Groups |
| `/harem` | View your collection | All |
| `/fav <name>` | Add to favourites | All |
| `/unfav <name>` | Remove from favourites | All |
| `/myfav` | View favourites list | All |
| `/balance` | Check Sakura balance | All |
| `/pay <amount>` | Pay another user | All |
| `/trade <waifu> \| <waifu>` | Trade waifus | All |
| `/daily` | Claim daily reward | All |
| `/battle` | Battle another user | Groups |
| `/spawnon` | Enable waifu spawn | Admin |
| `/spawnoff` | Disable waifu spawn | Admin |
| `/setspawn <n>` | Set spawn rate | Admin |
| `/fspawn` | Force spawn | Sudo |
| `/addwaifu` | Add waifu to DB | Sudo |
| `/broadcast` | Broadcast message | Owner |
| `/addcoins` | Add coins to user | Sudo |
| `/deduct` | Deduct coins | Sudo |
| `/ping` | Bot ping & health | All |
| `/stats` | Bot statistics | All |

---

## 🛡 Anti-Spam System

YUKIWAFUS has a built-in smart anti-spam system in `spawn.py`:

- **Per-user rate limit** — 3 messages in 3 seconds = spam detected
- **5 min block** — spammer's messages don't count toward spawn
- **One-time warning** — user gets warned once per block session
- **Chat cooldown** — 10 sec between spawns (mass activity guard)
- **Global cooldown** — 2 sec between any spawn across all groups
- **Memory guard** — auto-cleans dicts at 10,000 entries

---

## 🤝 Contributing

```bash
# Fork → Clone → Branch → PR

git clone https://github.com/YOURNAME/YUKIWAFUS
git checkout -b feature/my-feature
# make changes
git commit -m "feat: my feature"
git push origin feature/my-feature
# open Pull Request on GitHub
```

---

## ⭐ Support

If this bot helped you, please **star the repo** — it helps a lot!

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=YOURNAME/YUKIWAFUS&type=Date)](https://star-history.com/#YOURNAME/YUKIWAFUS&Date)

</div>

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with 🌸 by **YUKIWAFUS Team**

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&pause=1000&color=F783AC&center=true&vCenter=true&width=400&lines=Thanks+for+using+YUKIWAFUS+%F0%9F%8C%B8;Star+the+repo+if+you+like+it!;Happy+collecting+waifus~" alt="footer" />

</div>

