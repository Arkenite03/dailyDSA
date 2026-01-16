"""Data models for the DSA Telegram bot."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Problem:
    """Represents a DSA problem."""
    id: str
    title: str
    difficulty: str
    topic: str
    url: str

    def __str__(self) -> str:
        """Format problem for display."""
        return (
            f"📚 *{self.title}*\n\n"
            f"🔹 Difficulty: {self.difficulty.capitalize()}\n"
            f"🔹 Topic: {self.topic}\n"
            f"🔹 Link: {self.url}"
        )


@dataclass
class UserPrefs:
    """User preferences stored in memory."""
    user_id: int
    difficulty: Optional[str] = None  # 'easy', 'medium', 'hard', or None for default
    schedule_time: Optional[str] = None  # Time in HH:MM format (24-hour), None for default

    def get_difficulty(self) -> Optional[str]:
        """Get user's preferred difficulty or None for default."""
        return self.difficulty if self.difficulty != 'default' else None
    
    def get_schedule_time(self) -> str:
        """Get user's preferred schedule time or default."""
        return self.schedule_time if self.schedule_time else "11:00"