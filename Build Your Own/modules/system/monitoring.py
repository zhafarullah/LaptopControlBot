# modules/system/monitoring.py
import os
import tempfile
import logging
import subprocess
import psutil
import win32gui
import win32process
from PIL import ImageGrab
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from modules.utils.decorators import log_function_call
from modules.utils.helpers import escape_md

class SystemMonitoring:
    """Handle system monitoring commands (screenshot, close apps, etc.)"""
    
    # Conversation states
    WAITING_CLOSEAPP = 1
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.logger = logging.getLogger(__name__)
    
    @log_function_call
    def screenshot(self, update, context):
        """Take a screenshot"""
        temp_file = None
        try:
            update.message.reply_text("📸 Taking a screenshot...")
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Save screenshot
            screenshot.save(temp_filename)
            
            # Send screenshot
            with open(temp_filename, 'rb') as photo:
                update.message.reply_photo(photo, caption="🖥️ Here's your screenshot!")
            
        except Exception as e:
            update.message.reply_text(f"❌ Error taking screenshot: {str(e)}")
            self.logger.error(f"Screenshot error: {e}")
            
        finally:
            if temp_file:
                try:
                    os.unlink(temp_filename)
                except:
                    pass
    
    def get_active_windows(self):
        """Get list of active visible windows"""
        window_list = []
        
        def enum_windows_callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text and len(window_text.strip()) > 0:
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        
                        try:
                            process = psutil.Process(pid)
                            process_name = process.name()
                            
                            # Filter relevant windows
                            if not window_text.startswith("Program Manager") and \
                               not window_text.startswith("Desktop Window Manager") and \
                               window_text != "Default IME":
                                
                                window_list.append({
                                    'hwnd': hwnd,
                                    'title': window_text.strip(),
                                    'pid': pid,
                                    'process_name': process_name
                                })
                        except psutil.NoSuchProcess:
                            pass
                    except Exception:
                        pass
        
        win32gui.EnumWindows(enum_windows_callback, None)
        
        # Remove duplicates
        seen = set()
        unique_windows = []
        for window in window_list:
            key = (window['title'], window['process_name'])
            if key not in seen:
                seen.add(key)
                unique_windows.append(window)
        
        return unique_windows
    
    def close_application_methods(self, pid, app_title, process_name):
        """Try various methods to close application"""
        # Method 1: taskkill
        try:
            result = subprocess.run(
                ['taskkill', '/PID', str(pid), '/F'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "taskkill /F", ""
        except Exception:
            pass
        
        # Method 2: psutil
        try:
            process = psutil.Process(pid)
            process.terminate()
            
            try:
                process.wait(timeout=5)
                return True, "psutil terminate", ""
            except psutil.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
                return True, "psutil kill", ""
                
        except psutil.NoSuchProcess:
            return True, "process already terminated", ""
        except Exception:
            pass
        
        return False, "all methods failed", "Could not close application"
    
    @log_function_call
    def closeapp_start(self, update, context):
        """Start close application process"""
        try:
            active_windows = self.get_active_windows()
            
            if not active_windows:
                update.message.reply_text("❌ There are no applications running in the foreground.")
                return ConversationHandler.END
            
            context.user_data['active_windows'] = active_windows
            
            message = "🗂 *Running Apps:*\n\n"
            
            for i, window in enumerate(active_windows, 1):
                escaped_title = escape_md(window['title'])
                escaped_process = escape_md(window['process_name'])
                
                message += f"{i}\\. *{escaped_title}*\n"
                message += f"    Process: {escaped_process}\n"
                message += f"    PID: {window['pid']}\n\n"
            
            message += "💡 *How to use:*\n"
            message += "• Type a number \\(1\\-" + str(len(active_windows)) + "\\) to close the application\n"
            message += "• Type /cancel to cancel\n\n"
            message += "⚠️ *Warning:* The application will be forcefully closed\\!"
            
            update.message.reply_text(message, parse_mode='MarkdownV2')
            return self.WAITING_CLOSEAPP
            
        except Exception as e:
            error_msg = f"❌ Error while retrieving application list: {escape_md(str(e))}"
            update.message.reply_text(error_msg, parse_mode='MarkdownV2')
            return ConversationHandler.END
    
    @log_function_call
    def handle_closeapp_input(self, update, context):
        """Handle close app input"""
        user_input = update.message.text.strip()
        
        if user_input.lower() == 'cancel':
            update.message.reply_text("❌ Operation canceled.")
            return ConversationHandler.END
        
        try:
            choice = int(user_input)
        except ValueError:
            update.message.reply_text("❌ Invalid input! Type a number or /cancel")
            return self.WAITING_CLOSEAPP
        
        active_windows = context.user_data.get('active_windows', [])
        
        if not active_windows:
            update.message.reply_text("❌ Application list not found. Please try again with /closeapp")
            return ConversationHandler.END
        
        if choice < 1 or choice > len(active_windows):
            update.message.reply_text(f"❌ Invalid choice! Type a number 1-{len(active_windows)} or /cancel")
            return self.WAITING_CLOSEAPP
        
        selected_window = active_windows[choice - 1]
        pid = selected_window['pid']
        app_title = selected_window['title']
        process_name = selected_window['process_name']
        
        # Check for critical system processes
        system_processes = ['explorer.exe', 'winlogon.exe', 'csrss.exe', 'wininit.exe', 
                           'services.exe', 'lsass.exe', 'svchost.exe', 'dwm.exe']
        
        if process_name.lower() in system_processes:
            warning_msg = f"⚠️ *Warning\\!*\n\n"
            warning_msg += f"📱 *Application:* {escape_md(app_title)}\n"
            warning_msg += f"🔧 *Process:* {escape_md(process_name)}\n\n"
            warning_msg += "_This is a critical system process. Closing it may cause system instability._\n\n"
            warning_msg += "Are you sure you want to continue? \\(y/n\\)"
            
            update.message.reply_text(warning_msg, parse_mode='MarkdownV2')
            return self.WAITING_CLOSEAPP
        
        # Show progress
        progress_msg = f"🔄 *Trying to close application\\.\\.\\.*\n\n"
        progress_msg += f"📱 *Application:* {escape_md(app_title)}\n"
        progress_msg += f"🔧 *Process:* {escape_md(process_name)}\n"
        progress_msg += f"🆔 *PID:* {pid}"
        
        progress_message = update.message.reply_text(progress_msg, parse_mode='MarkdownV2')
        
        # Execute close
        success, method_used, error_msg = self.close_application_methods(pid, app_title, process_name)
        
        if success:
            success_msg = f"✅ *Application closed successfully\\!*\n\n"
            success_msg += f"📱 *Application:* {escape_md(app_title)}\n"
            success_msg += f"🔧 *Process:* {escape_md(process_name)}\n"
            success_msg += f"🆔 *PID:* {pid}\n"
            success_msg += f"🛠 *Method:* {escape_md(method_used)}"
            
            try:
                context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=progress_message.message_id,
                    text=success_msg,
                    parse_mode='MarkdownV2'
                )
            except:
                update.message.reply_text(success_msg, parse_mode='MarkdownV2')
        else:
            error_msg_formatted = f"❌ *Failed to close application\\!*\n\n"
            error_msg_formatted += f"📱 *Application:* {escape_md(app_title)}\n"
            error_msg_formatted += f"🔧 *Process:* {escape_md(process_name)}\n"
            error_msg_formatted += f"🆔 *PID:* {pid}\n\n"
            error_msg_formatted += f"🚫 *Error:* {escape_md(error_msg)}"

            try:
                context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=progress_message.message_id,
                    text=error_msg_formatted,
                    parse_mode='MarkdownV2'
                )
            except:
                update.message.reply_text(error_msg_formatted, parse_mode='MarkdownV2')
        
        # Cleanup
        if 'active_windows' in context.user_data:
            del context.user_data['active_windows']
        
        return ConversationHandler.END
    
    def cancel_closeapp(self, update, context):
        """Cancel close app operation"""
        update.message.reply_text("❌ Operation canceled.")
        if 'active_windows' in context.user_data:
            del context.user_data['active_windows']
        return ConversationHandler.END
    
    def register_handlers(self, dispatcher):
        """Register semua monitoring handlers"""
        dispatcher.add_handler(CommandHandler('screenshot', self.auth.require_auth(self.screenshot)))
        
        # Close app conversation handler
        closeapp_handler = ConversationHandler(
            entry_points=[CommandHandler('closeapp', self.auth.require_auth(self.closeapp_start))],
            states={
                self.WAITING_CLOSEAPP: [MessageHandler(Filters.text & ~Filters.command, self.handle_closeapp_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_closeapp)]
        )
        dispatcher.add_handler(closeapp_handler)
        
        self.logger.info("System monitoring handlers registered")