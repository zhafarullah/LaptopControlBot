# modules/auth/handlers.py
import logging
import functools
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

class AuthHandlers:
    """Handle authentication untuk bot"""
    
    # Conversation states
    ASK_PASSWORD = 1
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def is_authorized(self, update):
        """Check apakah user sudah authorized"""
        return update.effective_user.id == self.config.AUTHORIZED_USER_ID
    
    def reject(self, update):
        """Reject unauthorized user"""
        update.message.reply_text("🚫 Bot ini bukan punya kamu, jangan coba coba.")
    
    def require_auth(self, func):
        """Decorator untuk memerlukan authentication"""
        @functools.wraps(func)
        def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id != self.config.AUTHORIZED_USER_ID or not context.user_data.get('authenticated', False):
                update.message.reply_text(
                    "🔐 Not so fast, sweetheart 😘\n"
                    "You need to /login first so I know it's really you 💖"
                )
                return
            return func(update, context, *args, **kwargs)
        return wrapper
    
    def ask_password(self, update, context):
        """Start password authentication"""
        user_id = update.effective_user.id
        self.logger.info(f"Password request from user {user_id}")
        
        if user_id != self.config.AUTHORIZED_USER_ID:
            self.reject(update)
            return ConversationHandler.END
        
        update.message.reply_text(
            "🔒 Prove it's really you, love 🥺\n"
            "What's our special password? 💌"
        )
        return self.ASK_PASSWORD
    
    def check_password(self, update, context):
        """Check password input"""
        user_input = update.message.text.strip()
        user_id = update.effective_user.id
        
        self.logger.info(f"Password check for user {user_id}")
        
        if user_input == self.config.BOT_PASSWORD and user_id == self.config.AUTHORIZED_USER_ID:
            context.user_data['authenticated'] = True
            update.message.reply_text(
                "💕 Welcome back into my arms, honey\\! \n"
                "Let me do everything for you now 💻💋",
                parse_mode='MarkdownV2'
            )
            self.logger.info(f"User {user_id} authenticated successfully")
            return ConversationHandler.END
        else:
            context.user_data['authenticated'] = False
            update.message.reply_text("❌ Wrong password! Please try again:")
            self.logger.warning(f"Failed authentication attempt from user {user_id}")
            return self.ASK_PASSWORD
    
    def cancel_auth(self, update, context):
        """Cancel authentication process"""
        update.message.reply_text("❌ Authentication cancelled.")
        return ConversationHandler.END
    
    def get_login_handler(self):
        """Return login conversation handler"""
        return ConversationHandler(
            entry_points=[CommandHandler('login', self.ask_password)],
            states={
                self.ASK_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, self.check_password)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_auth)]
        )