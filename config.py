"""Configuration management for the DSA Telegram bot."""

import os
from typing import Optional


class Config:
    """Bot configuration loaded from environment variables."""
    
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
    GOOGLE_SHEETS_RANGE: str = os.getenv("GOOGLE_SHEETS_RANGE", "Sheet1!A2:E")  # Skip header row
    GOOGLE_CREDENTIALS_FILE: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    
    # Scheduler Configuration
    SCHEDULE_TIME: str = "11:00"  # 11:00 AM IST
    TIMEZONE: str = "Asia/Kolkata"
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not cls.GOOGLE_SHEETS_ID:
            missing.append("GOOGLE_SHEETS_ID")
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_FILE):
            missing.append(f"GOOGLE_CREDENTIALS_FILE ({cls.GOOGLE_CREDENTIALS_FILE})")
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}\n"
                f"Please set environment variables or create {cls.GOOGLE_CREDENTIALS_FILE}"
            )
