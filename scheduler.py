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
    
    def start(self, application: Application) -> None:
        """Start the scheduler."""
        self.application = application
        
        # Schedule daily job at 11:00 AM IST
        hour, minute = map(int, Config.SCHEDULE_TIME.split(':'))
        
        self.scheduler.add_job(
            self._send_daily_problem_job,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=Config.TIMEZONE),
            id='daily_dsa_problem',
            name='Send daily DSA problem'
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started. Daily problem will be sent at {Config.SCHEDULE_TIME} {Config.TIMEZONE}")
    
    async def _send_daily_problem_job(self) -> None:
        """Internal job function that calls handler with bot."""
        # Pass the bot directly to the handler
        await self.handlers.send_daily_problem(self.application.bot)
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
