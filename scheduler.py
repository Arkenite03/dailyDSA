"""Scheduler for daily DSA problem delivery."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from config import Config
from handlers import Handlers

logger = logging.getLogger(__name__)


class Scheduler:
    """Manages the daily problem scheduler."""
    
    def __init__(self, handlers: Handlers):
        """Initialize scheduler with handlers."""
        self.scheduler = AsyncIOScheduler(timezone=Config.TIMEZONE)
        self.handlers = handlers
        self.application: Application = None
        # Store scheduler reference in handlers for rescheduling
        handlers.scheduler = self
    
    def start(self, application: Application) -> None:
        """Start the scheduler and schedule jobs for all users."""
        self.application = application
        
        # Schedule jobs for all existing users
        self._schedule_all_users()
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Scheduling per-user daily problems.")
    
    def _schedule_all_users(self) -> None:
        """Schedule daily problem jobs for all users."""
        # Import here to avoid circular import
        from handlers import user_prefs
        
        for user_id, prefs in user_prefs.items():
            schedule_time = prefs.get_schedule_time()
            self._schedule_user_job(user_id, schedule_time)
        
        default_time = Config.SCHEDULE_TIME
        logger.info(f"Scheduled jobs for {len(user_prefs)} users. Default time: {default_time}")
    
    def _schedule_user_job(self, user_id: int, time_str: str) -> None:
        """Schedule a daily job for a specific user at the given time."""
        job_id = f"daily_problem_user_{user_id}"
        
        # Remove existing job if it exists
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass  # Job doesn't exist, that's fine
        
        # Parse time
        hour, minute = map(int, time_str.split(':'))
        
        # Schedule new job
        self.scheduler.add_job(
            self._send_user_daily_problem,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=Config.TIMEZONE),
            id=job_id,
            name=f"Daily problem for user {user_id}",
            args=[user_id]
        )
        
        logger.info(f"Scheduled daily problem for user {user_id} at {time_str} {Config.TIMEZONE}")
    
    async def _send_user_daily_problem(self, user_id: int) -> None:
        """Send daily problem to a specific user."""
        try:
            await self.handlers.send_daily_problem_to_user(self.application.bot, user_id)
        except Exception as e:
            logger.error(f"Error sending daily problem to user {user_id}: {e}")
    
    def reschedule_user_job(self, user_id: int, time_str: str) -> None:
        """Reschedule a user's daily problem job."""
        self._schedule_user_job(user_id, time_str)
        logger.info(f"Rescheduled daily problem for user {user_id} to {time_str}")
    
    def schedule_new_user(self, user_id: int) -> None:
        """Schedule a job for a new user (called when they use /start)."""
        # Import here to avoid circular import
        from handlers import user_prefs
        
        if user_id in user_prefs:
            schedule_time = user_prefs[user_id].get_schedule_time()
        else:
            schedule_time = Config.SCHEDULE_TIME
        
        self._schedule_user_job(user_id, schedule_time)
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
