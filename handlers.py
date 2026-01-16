"""Command handlers for the DSA Telegram bot."""

import logging
import time
from typing import Dict, Optional, Set

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler

from models import Problem, UserPrefs
from sheets import SheetsService

logger = logging.getLogger(__name__)

# Conversation states for /add command
TITLE, DIFFICULTY, TOPIC, URL = range(4)

# In-memory storage
user_prefs: Dict[int, UserPrefs] = {}
conversation_data: Dict[int, Dict] = {}  # Store temporary data during /add flow
user_completed_problems: Dict[int, Set[str]] = {}  # Track done/discarded problems per user
user_recent_problems: Dict[int, list] = {}  # Track recently sent problems (last 20) per user


class Handlers:
    """Command handlers for the bot."""
    
    def __init__(self, sheets_service: SheetsService):
        """Initialize handlers with sheets service."""
        self.sheets = sheets_service
    
    def _get_excluded_problem_ids(self, user_id: int) -> Set[str]:
        """Get set of problem IDs to exclude for a user (completed + recent)."""
        excluded = set()
        
        # Add completed/discarded problems
        if user_id in user_completed_problems:
            excluded.update(user_completed_problems[user_id])
        
        # Add recently sent problems (last 20)
        if user_id in user_recent_problems:
            excluded.update(user_recent_problems[user_id])
        
        return excluded
    
    def _create_problem_keyboard(self, problem_id: str) -> InlineKeyboardMarkup:
        """Create inline keyboard with Done/Later/Discard buttons."""
        keyboard = [
            [
                InlineKeyboardButton("✅ Done", callback_data=f"problem_done_{problem_id}"),
                InlineKeyboardButton("⏰ Later", callback_data=f"problem_later_{problem_id}"),
                InlineKeyboardButton("❌ Discard", callback_data=f"problem_discard_{problem_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_problem_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle callback queries for problem action buttons."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Initialize user tracking if needed
        if user_id not in user_completed_problems:
            user_completed_problems[user_id] = set()
        if user_id not in user_recent_problems:
            user_recent_problems[user_id] = []
        
        if data.startswith("problem_done_"):
            problem_id = data.replace("problem_done_", "")
            user_completed_problems[user_id].add(problem_id)
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("✅ Marked as done! Great job! 🎉")
        
        elif data.startswith("problem_discard_"):
            problem_id = data.replace("problem_discard_", "")
            user_completed_problems[user_id].add(problem_id)
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("❌ Problem discarded. I won't send this one again.")
        
        elif data.startswith("problem_later_"):
            problem_id = data.replace("problem_later_", "")
            # Don't mark as completed, just acknowledge
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("⏰ Saved for later! I'll keep this problem in rotation.")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # Initialize user preferences if not exists
        if user_id not in user_prefs:
            user_prefs[user_id] = UserPrefs(user_id=user_id)
        
        welcome_message = (
            f"👋 Hello {user_name}!\n\n"
            "Welcome to the DSA Daily Bot! 🚀\n\n"
            "I'll help you build a habit of thinking about Data Structures and Algorithms.\n\n"
            "📋 *Available Commands:*\n"
            "/start - Show this welcome message\n"
            "/today - Get today's DSA problem\n"
            "/another - Get another random problem\n"
            "/level [default|easy|medium|hard] - Set difficulty preference\n"
            "/add - Add a new problem to the database\n\n"
            "💡 *Features:*\n"
            "• Daily problems at 11:00 AM IST\n"
            "• Interactive buttons: ✅ Done, ⏰ Later, ❌ Discard\n"
            "• Smart tracking: Won't repeat problems you've completed!\n\n"
            "💡 *Tip:* Use the buttons below each problem to track your progress!"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /today command - send today's problem."""
        user_id = update.effective_user.id
        
        # Initialize user tracking if needed
        if user_id not in user_completed_problems:
            user_completed_problems[user_id] = set()
        if user_id not in user_recent_problems:
            user_recent_problems[user_id] = []
        
        # Get user's difficulty preference
        difficulty = None
        if user_id in user_prefs:
            difficulty = user_prefs[user_id].get_difficulty()
        
        # Get excluded problem IDs
        excluded_ids = self._get_excluded_problem_ids(user_id)
        
        try:
            problem = self.sheets.get_random_problem(difficulty, exclude_ids=excluded_ids)
            
            if problem:
                # Track this problem as recently sent
                user_recent_problems[user_id].append(problem.id)
                # Keep only last 20 recent problems
                if len(user_recent_problems[user_id]) > 20:
                    user_recent_problems[user_id] = user_recent_problems[user_id][-20:]
                
                message = (
                    "📅 *Today's DSA Problem*\n\n"
                    f"{problem}\n\n"
                    "💪 Good luck solving it!"
                )
                keyboard = self._create_problem_keyboard(problem.id)
                await update.message.reply_text(
                    message, 
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    "❌ No new problems available! You've completed all problems in your difficulty range.\n"
                    "Try changing your difficulty with /level or add more problems with /add"
                )
        except Exception as e:
            logger.error(f"Error fetching problem: {e}")
            await update.message.reply_text(
                "❌ Error fetching problem. Please try again later."
            )
    
    async def another(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /another command - send another random problem."""
        user_id = update.effective_user.id
        
        # Initialize user tracking if needed
        if user_id not in user_completed_problems:
            user_completed_problems[user_id] = set()
        if user_id not in user_recent_problems:
            user_recent_problems[user_id] = []
        
        # Get user's difficulty preference
        difficulty = None
        if user_id in user_prefs:
            difficulty = user_prefs[user_id].get_difficulty()
        
        # Get excluded problem IDs
        excluded_ids = self._get_excluded_problem_ids(user_id)
        
        try:
            problem = self.sheets.get_random_problem(difficulty, exclude_ids=excluded_ids)
            
            if problem:
                # Track this problem as recently sent
                user_recent_problems[user_id].append(problem.id)
                # Keep only last 20 recent problems
                if len(user_recent_problems[user_id]) > 20:
                    user_recent_problems[user_id] = user_recent_problems[user_id][-20:]
                
                message = (
                    "🎲 *Another Random Problem*\n\n"
                    f"{problem}\n\n"
                    "💪 Good luck solving it!"
                )
                keyboard = self._create_problem_keyboard(problem.id)
                await update.message.reply_text(
                    message,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                await update.message.reply_text(
                    "❌ No new problems available! You've completed all problems in your difficulty range.\n"
                    "Try changing your difficulty with /level or add more problems with /add"
                )
        except Exception as e:
            logger.error(f"Error fetching problem: {e}")
            await update.message.reply_text(
                "❌ Error fetching problem. Please try again later."
            )
    
    async def level(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /level command - set difficulty preference."""
        user_id = update.effective_user.id
        args = context.args
        
        # Initialize user preferences if not exists
        if user_id not in user_prefs:
            user_prefs[user_id] = UserPrefs(user_id=user_id)
        
        if not args:
            # Show current preference
            current = user_prefs[user_id].difficulty or "default"
            message = (
                f"📊 Your current difficulty preference: *{current.capitalize()}*\n\n"
                "To change it, use:\n"
                "/level default\n"
                "/level easy\n"
                "/level medium\n"
                "/level hard"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
            return
        
        difficulty = args[0].lower()
        valid_levels = ['default', 'easy', 'medium', 'hard']
        
        if difficulty not in valid_levels:
            await update.message.reply_text(
                f"❌ Invalid difficulty level. Use one of: {', '.join(valid_levels)}"
            )
            return
        
        user_prefs[user_id].difficulty = difficulty
        await update.message.reply_text(
            f"✅ Difficulty preference set to: *{difficulty.capitalize()}*",
            parse_mode='Markdown'
        )
    
    # /add command conversation handlers
    async def add_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the /add conversation."""
        user_id = update.effective_user.id
        conversation_data[user_id] = {}
        
        await update.message.reply_text(
            "➕ Let's add a new problem!\n\n"
            "Please send me the *title* of the problem:",
            parse_mode='Markdown'
        )
        return TITLE
    
    async def add_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle title input."""
        user_id = update.effective_user.id
        title = update.message.text.strip()
        
        if not title:
            await update.message.reply_text("❌ Title cannot be empty. Please try again:")
            return TITLE
        
        conversation_data[user_id]['title'] = title
        
        await update.message.reply_text(
            "✅ Title saved!\n\n"
            "Now, please send me the *difficulty* (easy, medium, or hard):",
            parse_mode='Markdown'
        )
        return DIFFICULTY
    
    async def add_difficulty(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle difficulty input."""
        user_id = update.effective_user.id
        difficulty = update.message.text.strip().lower()
        
        valid_difficulties = ['easy', 'medium', 'hard']
        if difficulty not in valid_difficulties:
            await update.message.reply_text(
                f"❌ Invalid difficulty. Please use one of: {', '.join(valid_difficulties)}"
            )
            return DIFFICULTY
        
        conversation_data[user_id]['difficulty'] = difficulty
        
        await update.message.reply_text(
            "✅ Difficulty saved!\n\n"
            "Now, please send me the *topic* (e.g., Arrays, Trees, Dynamic Programming):",
            parse_mode='Markdown'
        )
        return TOPIC
    
    async def add_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle topic input."""
        user_id = update.effective_user.id
        topic = update.message.text.strip()
        
        if not topic:
            await update.message.reply_text("❌ Topic cannot be empty. Please try again:")
            return TOPIC
        
        conversation_data[user_id]['topic'] = topic
        
        await update.message.reply_text(
            "✅ Topic saved!\n\n"
            "Finally, please send me the *URL* of the problem:",
            parse_mode='Markdown'
        )
        return URL
    
    async def add_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle URL input and save the problem."""
        user_id = update.effective_user.id
        url = update.message.text.strip()
        
        if not url:
            await update.message.reply_text("❌ URL cannot be empty. Please try again:")
            return URL
        
        # Validate URL format (basic check)
        if not (url.startswith('http://') or url.startswith('https://')):
            await update.message.reply_text(
                "❌ Invalid URL format. Please provide a valid URL starting with http:// or https://"
            )
            return URL
        
        conversation_data[user_id]['url'] = url
        
        # Create problem object
        data = conversation_data[user_id]
        # Generate ID based on current problem count + timestamp for uniqueness
        problem_count = len(self.sheets.get_all_problems())
        problem_id = f"{problem_count + 1}_{int(time.time())}"
        
        problem = Problem(
            id=problem_id,
            title=data['title'],
            difficulty=data['difficulty'],
            topic=data['topic'],
            url=data['url']
        )
        
        try:
            # Add to Google Sheets
            self.sheets.add_problem(problem)
            
            # Clean up conversation data
            del conversation_data[user_id]
            
            await update.message.reply_text(
                f"✅ Problem added successfully!\n\n{problem}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error adding problem: {e}")
            await update.message.reply_text(
                f"❌ Error adding problem: {str(e)}\n\n"
                "Please try again later or contact the administrator."
            )
            del conversation_data[user_id]
        
        return ConversationHandler.END
    
    async def add_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the /add conversation."""
        user_id = update.effective_user.id
        if user_id in conversation_data:
            del conversation_data[user_id]
        
        await update.message.reply_text("❌ Problem addition cancelled.")
        return ConversationHandler.END
    
    def get_conversation_handler(self) -> ConversationHandler:
        """Get the conversation handler for /add command."""
        return ConversationHandler(
            entry_points=[self.add_start],
            states={
                TITLE: [self.add_title],
                DIFFICULTY: [self.add_difficulty],
                TOPIC: [self.add_topic],
                URL: [self.add_url],
            },
            fallbacks=[self.add_cancel],
        )
    
    async def send_daily_problem(self, context_or_bot) -> None:
        """Send daily problem to all registered users.
        
        Args:
            context_or_bot: Either a ContextTypes.DEFAULT_TYPE or a Bot instance
        """
        # Get bot from context or use directly
        if hasattr(context_or_bot, 'bot'):
            bot = context_or_bot.bot
        else:
            bot = context_or_bot
        
        # Get all users who have used /start
        users = list(user_prefs.keys())
        
        if not users:
            logger.info("No users to send daily problem to")
            return
        
        for user_id in users:
            try:
                # Initialize user tracking if needed
                if user_id not in user_completed_problems:
                    user_completed_problems[user_id] = set()
                if user_id not in user_recent_problems:
                    user_recent_problems[user_id] = []
                
                difficulty = user_prefs[user_id].get_difficulty()
                excluded_ids = self._get_excluded_problem_ids(user_id)
                problem = self.sheets.get_random_problem(difficulty, exclude_ids=excluded_ids)
                
                if problem:
                    # Track this problem as recently sent
                    user_recent_problems[user_id].append(problem.id)
                    # Keep only last 20 recent problems
                    if len(user_recent_problems[user_id]) > 20:
                        user_recent_problems[user_id] = user_recent_problems[user_id][-20:]
                    
                    message = (
                        "🌅 *Good Morning!*\n\n"
                        "Here's your daily DSA problem:\n\n"
                        f"{problem}\n\n"
                        "💪 Have a great day of coding!"
                    )
                    keyboard = self._create_problem_keyboard(problem.id)
                    await bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown',
                        reply_markup=keyboard
                    )
                else:
                    logger.warning(f"No new problems available for user {user_id}")
                    # Optionally send a message to user
                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=(
                                "🌅 *Good Morning!*\n\n"
                                "You've completed all available problems in your difficulty range! 🎉\n\n"
                                "Try changing your difficulty with /level or add more problems with /add"
                            ),
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error sending no-problems message to user {user_id}: {e}")
            except Exception as e:
                logger.error(f"Error sending daily problem to user {user_id}: {e}")
