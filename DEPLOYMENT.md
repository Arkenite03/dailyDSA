# Deployment Guide for RedHat Linux

This guide will help you deploy the DSA Telegram Bot on a RedHat Linux server.

## Prerequisites

- RedHat Linux server with SSH access
- Python 3.10+ installed (or Python 3.9+ with warnings)
- Root or sudo access for systemd service setup
- Google service account credentials file (`credentials.json`)

## Step 1: Prepare the Server

### Install Python and pip (if not already installed)

```bash
# For RedHat/CentOS 8+
sudo dnf install python3 python3-pip

# For older versions
sudo yum install python3 python3-pip
```

### Verify Python version

```bash
python3 --version  # Should be 3.10+ (3.9+ works with warnings)
```

## Step 2: Clone/Upload the Project

### Option A: Clone from GitHub

```bash
cd ~
git clone <your-github-repo-url>
cd dsaTelegram
```

### Option B: Upload via SCP

```bash
# From your local machine
scp -r dsaTelegram/ user@your-server:/home/user/
```

## Step 3: Install Dependencies

```bash
cd ~/dsaTelegram  # or wherever you cloned/uploaded
pip3 install --user -r requirements.txt

# Or install system-wide (requires sudo)
sudo pip3 install -r requirements.txt
```

## Step 4: Configure Credentials

### 4.1 Upload credentials.json

```bash
# From your local machine
scp credentials.json user@your-server:/home/user/dsaTelegram/
```

### 4.2 Set Environment Variables

Create a systemd service file (see Step 5) or set environment variables in your shell:

```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export GOOGLE_SHEETS_ID="your_google_sheets_id"
```

## Step 5: Create Systemd Service (Recommended)

### 5.1 Create the service file

```bash
sudo nano /etc/systemd/system/dsa-bot.service
```

### 5.2 Copy and edit the service configuration

Use the `dsa-bot.service` file from the project, or create it with:

```ini
[Unit]
Description=DSA Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/dsaTelegram
Environment="TELEGRAM_BOT_TOKEN=your_telegram_bot_token"
Environment="GOOGLE_SHEETS_ID=your_google_sheets_id"
Environment="GOOGLE_CREDENTIALS_FILE=/home/your_username/dsaTelegram/credentials.json"
ExecStart=/usr/bin/python3 /home/your_username/dsaTelegram/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Important:** Replace:
- `your_username` with your actual username
- `/home/your_username/dsaTelegram` with your actual path
- `your_telegram_bot_token` with your actual token
- `your_google_sheets_id` with your actual sheet ID
- `/usr/bin/python3` with the path to your python3 (find with `which python3`)

### 5.3 Reload systemd and start the service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable dsa-bot.service

# Start the service
sudo systemctl start dsa-bot.service

# Check status
sudo systemctl status dsa-bot.service
```

### 5.4 Useful systemd commands

```bash
# View logs
sudo journalctl -u dsa-bot.service -f

# Stop the service
sudo systemctl stop dsa-bot.service

# Restart the service
sudo systemctl restart dsa-bot.service

# Disable auto-start on boot
sudo systemctl disable dsa-bot.service
```

## Step 6: Verify Deployment

### 6.1 Check service status

```bash
sudo systemctl status dsa-bot.service
```

You should see `active (running)`.

### 6.2 Check logs

```bash
sudo journalctl -u dsa-bot.service -n 50
```

Look for:
- "Starting bot..."
- "Scheduler started. Daily problem will be sent at 11:00 Asia/Kolkata"
- No error messages

### 6.3 Test the bot

Send `/start` to your bot on Telegram. You should receive a welcome message.

## Step 7: Firewall Configuration (if needed)

If your server has a firewall, ensure it's not blocking outbound connections:

```bash
# Check firewall status
sudo firewall-cmd --state

# If firewall is active, allow outbound connections (usually already allowed)
# The bot only needs outbound HTTPS to Telegram and Google APIs
```

## Troubleshooting

### Service fails to start

1. Check the service status:
   ```bash
   sudo systemctl status dsa-bot.service
   ```

2. Check logs:
   ```bash
   sudo journalctl -u dsa-bot.service -n 100
   ```

3. Verify paths and permissions:
   ```bash
   ls -la /path/to/dsaTelegram/credentials.json
   which python3
   ```

### Bot not responding

1. Check if the service is running:
   ```bash
   sudo systemctl status dsa-bot.service
   ```

2. Check recent logs for errors:
   ```bash
   sudo journalctl -u dsa-bot.service --since "10 minutes ago"
   ```

3. Verify environment variables are set correctly in the service file

4. Test configuration manually:
   ```bash
   cd /path/to/dsaTelegram
   export TELEGRAM_BOT_TOKEN="your_token"
   export GOOGLE_SHEETS_ID="your_sheet_id"
   python3 test_config.py
   ```

### Permission errors

If you see permission errors:

```bash
# Ensure credentials.json is readable
chmod 644 credentials.json

# Ensure bot.py is executable (optional)
chmod +x bot.py
```

### Python path issues

If you get "python3: command not found":

```bash
# Find python3 location
which python3

# Update the service file ExecStart path
```

## Alternative: Run without systemd

If you prefer not to use systemd, you can use `screen` or `tmux`:

```bash
# Install screen
sudo dnf install screen  # or: sudo yum install screen

# Start a screen session
screen -S dsa-bot

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export GOOGLE_SHEETS_ID="your_sheet_id"

# Run the bot
cd ~/dsaTelegram
python3 bot.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r dsa-bot
```

Or use `nohup`:

```bash
cd ~/dsaTelegram
export TELEGRAM_BOT_TOKEN="your_token"
export GOOGLE_SHEETS_ID="your_sheet_id"
nohup python3 bot.py > bot.log 2>&1 &
```

## Security Best Practices

1. **File Permissions:**
   ```bash
   chmod 600 credentials.json  # Only owner can read/write
   ```

2. **Service User:**
   - Create a dedicated user for the bot (recommended)
   - Don't run as root

3. **Environment Variables:**
   - Keep tokens in systemd service file (not in code)
   - Use `EnvironmentFile` if you prefer external file

4. **Logs:**
   - Regularly rotate logs to prevent disk space issues
   - Don't log sensitive information

## Updating the Bot

When you update the code:

```bash
# Pull latest changes (if using git)
cd ~/dsaTelegram
git pull

# Restart the service
sudo systemctl restart dsa-bot.service

# Check status
sudo systemctl status dsa-bot.service
```

## Monitoring

Set up monitoring to ensure the bot stays running:

```bash
# Check if service is running (can be added to cron)
systemctl is-active dsa-bot.service

# Or use a monitoring tool like monit or supervisor
```
