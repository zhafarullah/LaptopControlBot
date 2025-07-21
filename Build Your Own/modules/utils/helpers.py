# modules/utils/helpers.py
import os
import sys
import re
import importlib.util
import datetime
from pathlib import Path
from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration class untuk bot"""
    BOT_TOKEN: str
    AUTHORIZED_USER_ID: int
    BOT_PASSWORD: str
    WEBCAM_VIDEO_DEVICE: str = "HD User Facing"
    WEBCAM_AUDIO_DEVICE: str = "Microphone Array (Realtek(R) Audio)"

def load_config():
    """Load config dengan auto-create template jika tidak ada"""
    try:
        if getattr(sys, 'frozen', False):
            # Running as exe - config harus di folder exe
            base_dir = Path(sys.executable).parent
        else:
            # Running as script
            base_dir = Path(__file__).parent.parent.parent
        
        config_path = base_dir / "config.py"
        
        # Auto-create template jika config tidak ada
        if not config_path.exists():
            create_config_template(config_path)
            print("=" * 50)
            print("FIRST TIME SETUP REQUIRED!")
            print("=" * 50)
            print(f"Config template created: {config_path}")
            print("\nPlease edit config.py with your details:")
            print("1. Get bot token from @BotFather")
            print("2. Get user ID from @userinfobot")
            print("3. Set your password")
            print("4. Restart the program")
            input("\nPress Enter to exit...")
            exit(1)
        
        # Load dan validate config
        spec = importlib.util.spec_from_file_location("config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        # Check if still using template values
        if (hasattr(config_module, 'BOT_TOKEN') and 
            config_module.BOT_TOKEN in ['your_bot_token_here', 'PLACEHOLDER_BUILD_TOKEN']):
            print("=" * 50)
            print("PLEASE CONFIGURE YOUR BOT!")
            print("=" * 50)
            print(f"Edit {config_path} with real values:")
            print("- BOT_TOKEN: from @BotFather")
            print("- AUTHORIZED_USER_ID: from @userinfobot")
            print("- BOT_PASSWORD: your choice")
            input("\nPress Enter to exit...")
            exit(1)
        
        return BotConfig(
            BOT_TOKEN=config_module.BOT_TOKEN,
            AUTHORIZED_USER_ID=config_module.AUTHORIZED_USER_ID,
            BOT_PASSWORD=config_module.BOT_PASSWORD,
            WEBCAM_VIDEO_DEVICE=getattr(config_module, 'WEBCAM_VIDEO_DEVICE', "HD User Facing"),
            WEBCAM_AUDIO_DEVICE=getattr(config_module, 'WEBCAM_AUDIO_DEVICE', "Microphone Array")
        )
        
    except Exception as e:
        print(f"Error loading config: {e}")
        input("Press Enter to exit...")
        exit(1)

def create_config_template(config_path):
    """Create user-friendly config template"""
    template = '''# config.py - Laptop Control Bot Configuration
# Edit this file with your actual bot details

# =================================================
# STEP 1: Get Bot Token from @BotFather
# =================================================
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot and follow instructions  
# 3. Copy the token and paste below
BOT_TOKEN = 'your_bot_token_here'

# =================================================
# STEP 2: Get Your User ID from @userinfobot
# =================================================
# 1. Open Telegram and search for @userinfobot
# 2. Send /start to get your user ID
# 3. Copy the NUMBER (not username) and paste below
AUTHORIZED_USER_ID = 123456789

# =================================================
# STEP 3: Choose Your Bot Password
# =================================================
# This password protects your bot from unauthorized access
BOT_PASSWORD = 'your_password_here'

# =================================================
# OPTIONAL: Webcam Device Names
# =================================================
# Run /detectdevices command to find correct names
WEBCAM_VIDEO_DEVICE = "HD User Facing"
WEBCAM_AUDIO_DEVICE = "Microphone Array (Realtek(R) Audio)"
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(template)

def escape_md(text):
    """Escape MarkdownV2 special characters"""
    escape_chars = '_*[]()~`>#+-=|{}.!\\'
    return ''.join(['\\' + c if c in escape_chars else c for c in str(text)])

def escape_md_caption(text):
    """Escape karakter spesial MarkdownV2 untuk caption"""
    pattern = r'([_\*\[\]\(\)~`>#+\-=|{}\.!])'
    return re.sub(pattern, r'\\\1', str(text))

def format_size(size):
    """Format file size dengan humanize"""
    try:
        import humanize
        return humanize.naturalsize(size)
    except ImportError:
        # Fallback manual formatting
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

def format_time(timestamp):
    """Format timestamp dengan humanize"""
    try:
        import humanize
        dt = datetime.datetime.fromtimestamp(timestamp)
        return humanize.naturaltime(dt)
    except ImportError:
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def send_long_message(update, message, parse_mode='MarkdownV2'):
    """Mengirim pesan panjang dengan membaginya jika perlu"""
    max_length = 4000
    
    if len(message) <= max_length:
        update.message.reply_text(message, parse_mode=parse_mode)
        return
    
    parts = []
    current_part = ""
    lines = message.split('\n')
    
    for line in lines:
        if len(current_part) + len(line) + 1 > max_length:
            if current_part:
                parts.append(current_part)
                current_part = line
            else:
                while len(line) > max_length:
                    parts.append(line[:max_length])
                    line = line[max_length:]
                current_part = line
        else:
            if current_part:
                current_part += "\n" + line
            else:
                current_part = line
    
    if current_part:
        parts.append(current_part)
    
    for i, part in enumerate(parts):
        if i == 0:
            update.message.reply_text(part, parse_mode=parse_mode)
        else:
            continuation_part = f"*\\.\\.\\. lanjutan {i+1}/{len(parts)} \\.\\.\\.*\n\n{part}"
            update.message.reply_text(continuation_part, parse_mode=parse_mode)