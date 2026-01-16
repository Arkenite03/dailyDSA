"""Main entry point for the DSA Telegram bot."""

import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import CallbackQueryHandler

from config import Config
from handlers import Handlers
from scheduler import Scheduler
from sheets import SheetsService

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function to start the bot."""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)
    
    # Initialize services
    try:
        sheets_service = SheetsService()
        handlers = Handlers(sheets_service)
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("today", handlers.today))
    application.add_handler(CommandHandler("another", handlers.another))
    application.add_handler(CommandHandler("level", handlers.level))
    application.add_handler(CommandHandler("settime", handlers.settime))
    application.add_handler(handlers.get_conversation_handler())
    
    # Register callback query handler for problem action buttons
    application.add_handler(CallbackQueryHandler(handlers.handle_problem_action, pattern="^problem_"))
    
    # Initialize and start scheduler
    scheduler = Scheduler(handlers)
    
    # Start the scheduler after application initializes
    async def post_init(app: Application) -> None:
        """Initialize scheduler after application is ready."""
        scheduler.start(app)
    
    application.post_init = post_init
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
