# DSA Telegram Bot

A lightweight Telegram bot that sends daily Data Structures and Algorithms (DSA) problems to help build a habit of thinking about DSA without dedicated practice sessions.

## Features

- 📅 **Daily Problems**: Automatically sends one random DSA problem every day at 11:00 AM IST
- 🎲 **Manual Fetching**: Get problems on-demand with `/today` or `/another`
- ⚙️ **Difficulty Filtering**: Set your preferred difficulty level (easy, medium, hard)
- ✅ **Interactive Tracking**: Mark problems as Done/Later/Discard with inline buttons
- 🔄 **Smart Problem Selection**: Never repeats problems you've completed or seen recently
- ➕ **Add Problems**: Contribute new problems to the database via interactive `/add` command
- 💾 **Google Sheets Integration**: All problems stored in Google Sheets
- 🚀 **Lightweight**: In-memory storage, minimal resource usage

## Quick Start

### Local Development

1. **Clone and setup:**
```bash
git clone <your-repo-url>
cd dsaTelegram
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

3. **Configure credentials:**
   - Copy `credentials.json` to the project directory (Google service account credentials)
   - Copy `run_bot.sh.example` to `run_bot.sh` and add your tokens
   - Or set environment variables:
     ```bash
     export TELEGRAM_BOT_TOKEN="your_token"
     export GOOGLE_SHEETS_ID="your_sheet_id"
     ```

4. **Test configuration:**
```bash
python3 test_config.py.example  # Edit with your tokens first
```

5. **Run the bot:**
```bash
./run_bot.sh  # Or: python3 bot.py
```

## Prerequisites

- Python 3.10 or higher (Python 3.9.6 works but shows a warning)
- A Telegram bot token (get it from [@BotFather](https://t.me/botfather))
- Google Cloud project with Sheets API enabled
- Service account credentials JSON file

## GitHub Setup

This repository is configured to exclude sensitive files:

- `credentials.json` - Google service account credentials
- `run_bot.sh` - Contains your tokens (use `run_bot.sh.example` instead)
- `setup_env.sh` - Contains your tokens (use `setup_env.sh.example` instead)
- `test_config.py` - Contains your tokens (use `test_config.py.example` instead)

**Before pushing to GitHub:**
1. Ensure `credentials.json` is in `.gitignore` (already configured)
2. Use the `.example` files as templates
3. Never commit files with actual tokens

## Deployment

For production deployment on RedHat Linux, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions including:
- Systemd service setup
- Environment configuration
- Monitoring and troubleshooting

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token you receive (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Set Up Google Sheets

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Sheets API:**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

3. **Create Service Account:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "dsa-bot-service")
   - Click "Create and Continue"
   - Skip optional steps and click "Done"

4. **Generate Credentials:**
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Download the JSON file and save it as `credentials.json` in the project root

5. **Create Google Sheet:**
   - Create a new Google Sheet
   - Add a header row with: `id | title | difficulty | topic | url`
   - Share the sheet with the service account email (found in `credentials.json` as `client_email`)
   - Give it "Editor" permissions
   - Copy the Sheet ID from the URL:
     ```
     https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
     ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (optional, or set environment variables directly):

```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
export GOOGLE_SHEETS_ID="your_google_sheet_id_here"
export GOOGLE_SHEETS_RANGE="Sheet1!A2:E"  # Optional, defaults to this
export GOOGLE_CREDENTIALS_FILE="credentials.json"  # Optional, defaults to this
```

Or set them directly in your shell:

```bash
export TELEGRAM_BOT_TOKEN="your_token"
export GOOGLE_SHEETS_ID="your_sheet_id"
```

### 5. Run the Bot

**Option 1: Using the run script (recommended)**
```bash
./run_bot.sh
```

**Option 2: Manual run**
```bash
# Set environment variables first
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export GOOGLE_SHEETS_ID="your_google_sheets_id"

# Run the bot
python3 bot.py
```

**Option 3: Test configuration first**
```bash
python3 test_config.py  # Verify everything is set up correctly
python3 bot.py           # Then run the bot
```

The bot will start polling for updates and schedule the daily problem delivery.

## Bot Commands

- `/start` - Show welcome message and available commands
- `/today` - Get today's DSA problem (respects your difficulty preference)
- `/another` - Get another random problem
- `/level [default|easy|medium|hard]` - Set your preferred difficulty level
- `/add` - Add a new problem to the database (interactive flow)

## Project Structure

```
dsaTelegram/
├── bot.py              # Main entry point
├── handlers.py         # Command handlers
├── scheduler.py        # Daily job scheduler
├── sheets.py           # Google Sheets integration
├── models.py           # Data models (Problem, UserPrefs)
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── credentials.json    # Google service account credentials (not in repo)
```

## Architecture Notes

### In-Memory Storage
- User preferences (difficulty settings) are stored in memory
- Conversation state for `/add` command is stored in memory
- Data is lost on bot restart (by design for minimal resource usage)

### Google Sheets Format
The sheet should have the following columns:
- `id`: Unique identifier (can be auto-generated)
- `title`: Problem title
- `difficulty`: One of `easy`, `medium`, or `hard`
- `topic`: Problem topic (e.g., "Arrays", "Trees", "Dynamic Programming")
- `url`: Link to the problem

### Scheduler
- Uses APScheduler with timezone support
- Runs daily at 11:00 AM IST (Asia/Kolkata)
- Sends problems to all users who have used `/start`

## Troubleshooting

### Bot not responding
- Check that `TELEGRAM_BOT_TOKEN` is set correctly
- Verify the bot is running and not crashed
- Check logs for error messages

### Google Sheets errors
- Verify `credentials.json` is in the project root
- Check that the service account email has access to the sheet
- Ensure the sheet ID is correct
- Verify the sheet has the correct column headers

### Scheduler not working
- Check that the timezone is set correctly
- Verify APScheduler is running (check logs)
- Ensure the bot is running continuously (not just once)

## Running on a Server

For production deployment on a Linux server:

1. Use a process manager like `systemd` or `supervisord`
2. Set environment variables in the service file
3. Ensure the bot runs continuously
4. Set up log rotation
5. Consider using a virtual environment

Example systemd service file (`/etc/systemd/system/dsa-bot.service`):

```ini
[Unit]
Description=DSA Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/dsaTelegram
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="GOOGLE_SHEETS_ID=your_sheet_id"
ExecStart=/usr/bin/python3 /path/to/dsaTelegram/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

This project is provided as-is for educational purposes.
