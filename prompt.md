You are a senior Python backend engineer.

Help me build a lightweight Telegram bot in Python that sends one daily DSA problem to the user to help build a habit of thinking about DSA without dedicated practice sessions.

🔹 Core Constraints

Language: Python 3.10+

Platform: Telegram bot

Update method: Polling (NOT webhooks)

Scheduler: APScheduler

Data source: Google Sheets

Persistence: In-memory only (no database)

Runtime target: always-on Linux server (RedHat) with minimal CPU/memory usage

🔹 Libraries to use

python-telegram-bot

google-api-python-client

google-auth

APScheduler

🔹 Bot Purpose

Automatically send one random DSA problem daily at 11:00 AM IST

Allow user to fetch problems manually

🔹 Google Sheets (Problem Source)

Sheet columns:

id | title | difficulty | topic | url 


Read all rows

Filter by difficulty (If Given)

Pick random problem

Append new rows via /add

🔹 Bot Commands
/start

Welcome message

/today

Send today’s DSA problem

/another

Send another random problem

/level default|easy|medium|hard

Set preferred difficulty (store in memory per user, default if nothing given)

/add

Interactive conversation flow:

Ask title

Ask difficulty

Ask topic

Ask URL

Append row to Google Sheets

Maintain per-user conversation state in memory.

🔹 Scheduler

Use APScheduler

Timezone: Asia/Kolkata

Call same function as /today

🔹 Architecture
bot.py              # main entry
handlers.py         # command handlers
scheduler.py        # daily job
sheets.py           # Google Sheets read/write
models.py           # Problem, UserPrefs
config.py           # tokens, IDs

🔹 Output Expectations

Fully working Python project

Clear instructions to:

Create Telegram bot

Configure credentials

Run locally

Clean, readable code

Give suggestion while developing if you think, as a senior engineer something can be done in a better way.


🔹 Telegram Token
Done! Congratulations on your new bot. You will find it at t.me/dailyDSAbot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
8360199035:AAHRWzkiBJsM0R3sWqLqBUajB4baO2tDMcA
Keep your token secure and store it safely, it can be used by anyone to control your bot.

For a description of the Bot API, see this page: https://core.telegram.org/bots/api