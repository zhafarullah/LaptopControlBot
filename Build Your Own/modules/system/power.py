# modules/system/power.py
import os
import logging
from telegram.ext import CommandHandler
from modules.utils.decorators import log_function_call

class PowerControl:
    """Handle power control commands (shutdown, restart, etc.)"""
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.logger = logging.getLogger(__name__)
    
    @log_function_call
    def shutdown(self, update, context):
        """Shutdown komputer"""
        self.logger.info("Shutdown command executed")
        update.message.reply_text(
            "⚠️ Initiating shutdown...\n_Your laptop will power off now._", 
            parse_mode='Markdown'
        )
        os.system("shutdown /s /t 0")
    
    @log_function_call
    def restart(self, update, context):
        """Restart komputer"""
        self.logger.info("Restart command executed")
        update.message.reply_text(
            "🔄 Initiating restart...\n_Your laptop will restart now._", 
            parse_mode='Markdown'
        )
        os.system("shutdown /r /t 0")
    
    @log_function_call
    def sleep(self, update, context):
        """Put komputer to sleep"""
        self.logger.info("Sleep command executed")
        update.message.reply_text(
            "😴 Putting your laptop to sleep...\n_Sweet dreams!_", 
            parse_mode='Markdown'
        )
        os.system("powershell.exe -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)\"")
    
    @log_function_call
    def lock(self, update, context):
        """Lock screen"""
        self.logger.info("Lock command executed")
        update.message.reply_text(
            "🔒 Screen locked!\n_Your laptop is now secure._", 
            parse_mode='Markdown'
        )
        os.system("rundll32.exe user32.dll,LockWorkStation")
    
    @log_function_call
    def cancel_shutdown(self, update, context):
        """Cancel shutdown"""
        self.logger.info("Cancel shutdown command executed")
        update.message.reply_text(
            "⚡ Shutdown cancelled!\n_Your laptop will stay on._", 
            parse_mode='Markdown'
        )
        os.system("shutdown /a")
    
    def register_handlers(self, dispatcher):
        """Register semua power control handlers"""
        dispatcher.add_handler(CommandHandler('shutdown', self.auth.require_auth(self.shutdown)))
        dispatcher.add_handler(CommandHandler('restart', self.auth.require_auth(self.restart)))
        dispatcher.add_handler(CommandHandler('sleep', self.auth.require_auth(self.sleep)))
        dispatcher.add_handler(CommandHandler('lock', self.auth.require_auth(self.lock)))
        dispatcher.add_handler(CommandHandler('cancel_shutdown', self.auth.require_auth(self.cancel_shutdown)))
        
        self.logger.info("Power control handlers registered")