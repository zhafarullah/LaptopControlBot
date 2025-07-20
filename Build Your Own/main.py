# main.py - Entry point utama
import sys
import logging
import threading
import time
from pathlib import Path

# Local imports
from modules.utils.logging_setup import setup_enhanced_logging
from modules.utils.helpers import load_config
from modules.auth.handlers import AuthHandlers
from modules.system.power import PowerControl
from modules.system.info import SystemInfo
from modules.system.monitoring import SystemMonitoring
from modules.file_manager.handlers import FileManagerHandlers
from modules.webcam.capture import WebcamCapture
from modules.webcam.video import WebcamVideo

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class TelegramBot:
    """Main bot class yang mengkoordinasikan semua modul"""
    
    def __init__(self):
        self.logger = setup_enhanced_logging()
        self.config = load_config()
        self.updater = None
        self.dispatcher = None
        
        # Initialize semua modul
        self.auth = AuthHandlers(self.config)
        self.power = PowerControl(self.auth)
        self.system_info = SystemInfo(self.auth)
        self.monitoring = SystemMonitoring(self.auth)
        self.file_manager = FileManagerHandlers(self.auth)
        self.webcam_capture = WebcamCapture(self.auth)
        self.webcam_video = WebcamVideo(self.auth)
    
    def setup_handlers(self):
        """Register semua handlers ke dispatcher"""
        dp = self.dispatcher
        
        # Basic commands
        dp.add_handler(CommandHandler('start', self.auth.require_auth(self.start)))
        dp.add_handler(CommandHandler('help', self.auth.require_auth(self.help_command)))
        dp.add_handler(CommandHandler('stopbot', self.auth.require_auth(self.stop_bot)))
        
        # Authentication
        dp.add_handler(self.auth.get_login_handler())
        
        # Power control
        self.power.register_handlers(dp)
        
        # System info
        self.system_info.register_handlers(dp)
        
        # Monitoring
        self.monitoring.register_handlers(dp)
        
        # File management
        self.file_manager.register_handlers(dp)
        
        # Webcam
        self.webcam_capture.register_handlers(dp)
        self.webcam_video.register_handlers(dp)
        
        # Test handler
        dp.add_handler(CommandHandler('test', self.test_handler))
        
        # Debug handler untuk semua pesan
        dp.add_handler(MessageHandler(Filters.all, self.debug_all_messages), group=99)
        
        # Error handler
        dp.add_error_handler(self.error_handler)
        
        self.logger.info("All handlers registered successfully")
    
    def start(self, update, context):
        """Start command handler"""
        user_id = update.effective_user.id
        self.logger.info(f"START command from user {user_id}")
        
        if user_id == self.config.AUTHORIZED_USER_ID:
            update.message.reply_text(
                "👩‍💻 Hi, sweetheart 💕\n"
                "I'm your personal laptop assistant — just for you 😘\n"
                "Type /login so I can take care of everything for you 💻💖"
            )
        else:
            update.message.reply_text("🚫 Bot ini bukan punya kamu, jangan coba coba.")
    
    def help_command(self, update, context):
        """Help command dengan daftar lengkap commands"""
        message = "🤖 *Welcome to Your Laptop Control Bot\\!*\n\n"
        
        # Power Control Commands
        message += "*Power Control Commands* 🔌\n"
        message += "/shutdown \\- Power off your laptop\n"
        message += "/restart \\- Restart your laptop\n"
        message += "/sleep \\- Put laptop to sleep mode\n"
        message += "/lock \\- Lock your screen\n"
        message += "/cancel\\_shutdown \\- Cancel pending shutdown\n\n"
        
        # System Information Commands
        message += "*System Information Commands* ℹ️\n"
        message += "/status \\- Basic system info\n"
        message += "/sysinfo \\- Detailed CPU, RAM, and disk usage\n"
        message += "/battery \\- Check battery status\n"
        message += "/processes \\- View top active processes\n"
        message += "/screenshot \\- Take a screenshot\n"
        message += "/closeapp \\- Force close foreground app\n\n"
        
        # Webcam Control
        message += "*Webcam Control* 📷\n"
        message += "/webcam \\- Capture image from your laptop webcam\n"
        message += "/webcamvideo \\- Record 10s video from your webcam\n"
        message += "/detectdevices \\- Detect available video/audio devices\n\n"
        
        # File Management Commands
        message += "*File Management Commands* 📂\n"
        message += "/ls \\- List files in current directory\n"
        message += "/cd \\- Change directory\n"
        message += "/download \\- Download file\n"
        message += "/mkdir \\- Create directory\n"
        message += "/delete \\- Delete file/folder\n"
        message += "/search \\- Search for files\n"
        message += "\\_Send any file to upload it\\_\n\n"
        
        message += "\\_Use these commands to control your laptop\\.\\_"
        
        update.message.reply_text(text=message, parse_mode='MarkdownV2')
    
    def stop_bot(self, update, context):
        """Stop bot command"""
        update.message.reply_text("🛑 Bot akan dihentikan sekarang.")
        import os
        os._exit(0)
    
    def test_handler(self, update, context):
        """Test handler untuk debugging"""
        user_id = update.effective_user.id
        self.logger.info(f"TEST: Message from user {user_id}, authorized: {user_id == self.config.AUTHORIZED_USER_ID}")
        update.message.reply_text(f"✅ Bot working! Your ID: {user_id}")
    
    def debug_all_messages(self, update, context):
        """Debug handler untuk semua pesan"""
        try:
            user_id = update.effective_user.id
            text = update.message.text if update.message.text else "No text"
            self.logger.info(f"DEBUG: User {user_id} sent: '{text}' (authorized: {user_id == self.config.AUTHORIZED_USER_ID})")
        except Exception as e:
            self.logger.error(f"Debug handler error: {e}")
    
    def error_handler(self, update, context):
        """Simple error handler"""
        self.logger.error(f"Error occurred: {context.error}")
        if update and update.effective_message:
            try:
                update.effective_message.reply_text("❌ Terjadi error, coba lagi.")
            except:
                pass
    
    def send_startup_notification(self):
        """Kirim notifikasi startup di background"""
        def notification_worker():
            time.sleep(3)
            try:
                message = (
                    "👩 *I'm here for you, sweetheart 💖*\n\n"
                    "Hi, my love\\~ I've been waiting just for you\\.\n"
                    "Type /login so we can spend some time together\\. I missed you so much 🥺💞"
                )
                
                self.updater.bot.send_message(
                    chat_id=self.config.AUTHORIZED_USER_ID,
                    text=message,
                    parse_mode='MarkdownV2',
                    timeout=15
                )
                
                self.logger.info(f"✅ Startup notification sent successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to send startup notification: {e}")
        
        notification_thread = threading.Thread(target=notification_worker, daemon=True)
        notification_thread.start()
    
    def run(self):
        """Main run method"""
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.logger.info(f"Starting bot (attempt {retry_count + 1}/{max_retries})...")
                
                # Create updater
                self.updater = Updater(token=self.config.BOT_TOKEN, use_context=True)
                self.dispatcher = self.updater.dispatcher
                
                # Setup handlers
                self.setup_handlers()
                
                # Start polling
                self.logger.info("Starting polling...")
                self.updater.start_polling(timeout=30, read_latency=5)
                self.logger.info("✅ Bot started successfully!")
                
                # Send startup notification
                self.send_startup_notification()
                
                # Keep running
                self.updater.idle()
                
                self.logger.info("Bot stopped normally")
                break
                
            except KeyboardInterrupt:
                self.logger.info("Bot stopped by user")
                break
                
            except Exception as e:
                retry_count += 1
                self.logger.error(f"Bot error (attempt {retry_count}): {e}")
                
                if retry_count < max_retries:
                    wait_time = min(10, 2 ** retry_count)
                    self.logger.info(f"Restarting in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error("Max retries reached, stopping bot")
                    break
            
            finally:
                try:
                    if self.updater:
                        self.updater.stop()
                        self.logger.info("Updater stopped")
                except:
                    pass

def main():
    """Entry point"""
    try:
        # Log startup
        import datetime
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).parent

        with open(base_dir / "startup_log.txt", "a", encoding='utf-8') as f:
            f.write(f"Bot started at: {datetime.datetime.now()}\n")
        
        # Start bot
        bot = TelegramBot()
        bot.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if getattr(sys, 'frozen', False):
            input("Press Enter to exit...")

if __name__ == '__main__':
    main()