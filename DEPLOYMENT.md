# Deployment (RedHat, systemd --user, no sudo)

This guide targets a remote RedHat server where you do not have sudo access,
but you can use `systemd --user`. It uses a user service with auto-restart and
an easy deploy workflow.

## 1) Clone and set up Python env

```bash
git clone <your-repo-url> /ws/vishwsh2-sjc/dsaTelegram
cd /ws/vishwsh2-sjc/dsaTelegram

python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## 2) Create an env file (no secrets in git)

```bash
mkdir -p ~/.config/dsa-bot
cat > ~/.config/dsa-bot/env <<'EOF'
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GOOGLE_SHEETS_ID=your_google_sheet_id
GOOGLE_CREDENTIALS_FILE=/ws/vishwsh2-sjc/dsaTelegram/credentials.json
# Optional:
# GOOGLE_SHEETS_RANGE=Sheet1!A2:E
EOF
chmod 600 ~/.config/dsa-bot/env
```

Copy your `credentials.json` into the repo root:

```bash
cp /path/to/credentials.json /ws/vishwsh2-sjc/dsaTelegram/credentials.json
```

## 3) Install the user systemd service

Copy the template and edit only if your paths differ:

```bash
mkdir -p ~/.config/systemd/user
cp /ws/vishwsh2-sjc/dsaTelegram/dsa-bot.user.service ~/.config/systemd/user/dsa-bot.service
```

Then enable and start the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now dsa-bot.service
```

Check status:

```bash
systemctl --user status dsa-bot.service
```

Logs are written to files:

```bash
tail -f /ws/vishwsh2-sjc/dsaTelegram/logs/bot.log
tail -f /ws/vishwsh2-sjc/dsaTelegram/logs/bot.err
```

### Note about user services and logout

On most systems, `systemd --user` stops when you log out unless user lingering
is enabled. Without sudo, you cannot enable lingering yourself. Options:

- Ask an admin to run: `loginctl enable-linger your-user`
- Keep a persistent session (e.g. `tmux`) alive

## 4) Deploy new code easily

Use the included deploy script:

```bash
cd /ws/vishwsh2-sjc/dsaTelegram
./deploy.sh
```

What it does:

- `git pull`
- install/update dependencies in `.venv`
- restart the user service

If you prefer manual steps:

```bash
git pull
./.venv/bin/pip install -r requirements.txt
systemctl --user restart dsa-bot.service
```

