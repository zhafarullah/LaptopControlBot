# modules/utils/decorators.py
import functools
import logging

def require_auth(auth_handler):
    """Decorator untuk memerlukan authentication"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(update, context, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id != auth_handler.config.AUTHORIZED_USER_ID or not context.user_data.get('authenticated', False):
                update.message.reply_text(
                    "🔐 Not so fast, sweetheart 😘\n"
                    "You need to /login first so I know it's really you 💖"
                )
                return
            return func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def log_function_call(func):
    """Decorator untuk logging function calls"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper