# modules/file_manager/handlers.py
import os
import logging
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters
from modules.file_manager.operations import FileOperations
from modules.utils.helpers import escape_md, send_long_message, escape_md_caption, format_size
from modules.utils.decorators import log_function_call

class FileManagerHandlers:
    """Handle file management commands dan conversations"""
    
    # Conversation states
    WAITING_CD = 1
    WAITING_DOWNLOAD = 2
    WAITING_MKDIR = 3
    WAITING_DELETE = 4
    WAITING_SEARCH = 5
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.file_ops = FileOperations()
        self.logger = logging.getLogger(__name__)
    
    @log_function_call
    def list_directory(self, update, context):
        """List directory contents"""
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            self.logger.info(f"Listing directory: {current_path}")
            
            content = self.file_ops.list_directory_content(current_path)
            
            if content['type'] == 'drives':
                # Show available drives
                message = "💽 *Available Drives*\n\n"
                
                for drive_info in content['drives']:
                    if drive_info['accessible']:
                        message += f"• {escape_md(drive_info['name'])} \\- Free: {escape_md(drive_info['free_space'])} / Total: {escape_md(drive_info['total_space'])}\n"
                    else:
                        message += f"• {escape_md(drive_info['name'])} \\- Not accessible\n"
                
                message += "\n*Commands:*\n"
                message += "• /cd \\<drive\\:\\> \\- Change to drive \\(e\\.g\\. D\\:\\)\n"
                message += "• /ls \\- List current directory\n"
                message += "• /search \\- Search for files"
                
                update.message.reply_text(message, parse_mode='MarkdownV2')
            else:
                # Show directory contents
                message = f"📂 *Current Directory: {escape_md(content['current_path'])}*\n"
                message += f"📊 *Total Items: {content['total_items']}*\n\n"
                
                formatted_items = []
                for item in content['items']:
                    formatted_items.append(escape_md(item['display']))
                
                message += "\n".join(formatted_items)
                
                message += "\n\n*Commands:*\n"
                message += "• /cd \\- Change directory\n"
                message += "• /download \\- Download file\n"
                message += "• /mkdir \\- Create directory\n"
                message += "• /delete \\- Delete file/folder\n"
                message += "• /search \\- Search files"
                
                send_long_message(update, message, 'MarkdownV2')
            
        except Exception as e:
            error_msg = f"❌ Error: {escape_md(str(e))}"
            update.message.reply_text(error_msg, parse_mode='MarkdownV2')
            self.logger.error(f"Error in list_directory: {str(e)}")
    
    # Conversation handlers untuk file operations
    def cd_start(self, update, context):
        """Start change directory conversation"""
        current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
        
        if current_path == self.file_ops.DEFAULT_PATH:
            drives = self.file_ops.get_available_drives()
            message = "📂 *Available Drives*\n\n*Current Location:* Root\n\n*Available Drives:*\n"
            
            for drive in drives:
                try:
                    import psutil
                    usage = psutil.disk_usage(drive)
                    free_space = format_size(usage.free)
                    total_space = format_size(usage.total)
                    message += f"• {escape_md(drive)} \\- Free: {escape_md(free_space)} / Total: {escape_md(total_space)}\n"
                except:
                    message += f"• {escape_md(drive)} \\- Not accessible\n"
            
            message += "\n*Examples:*\n• D: \\- Change to drive D\n• E:\\\\ \\- Change to drive E\n\n_Type the drive letter or /cancel to abort_"
        else:
            message = (
                "📂 *Enter the directory path*\n\n"
                f"*Current path:* {escape_md(current_path)}\n\n"
                "*Examples:*\n"
                "• Documents \\- Go to folder\n"
                "• \\.\\.  \\- Go to parent directory\n"
                "• Documents\\\\Projects \\- Go to nested folder\n"
                "• C: \\- Switch to C drive\n"
                "• / \\- Go to drives list\n\n"
                "_Type the path or /cancel to abort_"
            )
        
        update.message.reply_text(message, parse_mode='MarkdownV2')
        return self.WAITING_CD
    
    def handle_cd_input(self, update, context):
        """Handle change directory input"""
        new_path = update.message.text.strip()
        
        if new_path.lower() == 'cancel':
            update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            resolved_path = self.file_ops.change_directory(current_path, new_path)
            context.user_data['current_path'] = resolved_path
            
            # Show new directory contents
            self.list_directory(update, context)
            return ConversationHandler.END
            
        except Exception as e:
            update.message.reply_text(f"❌ Error: {escape_md(str(e))}", parse_mode='MarkdownV2')
            return ConversationHandler.END
    
    def download_start(self, update, context):
        """Start download file conversation"""
        self.list_directory(update, context)
        update.message.reply_text("📥 *Enter the file name to download*", parse_mode='MarkdownV2')
        return self.WAITING_DOWNLOAD
    
    def handle_download_input(self, update, context):
        """Handle download file input"""
        file_name = update.message.text.strip()
        
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            
            if current_path == self.file_ops.DEFAULT_PATH:
                update.message.reply_text("❌ Please select a drive first using /cd command")
                return ConversationHandler.END
                
            file_path = os.path.join(current_path, file_name)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50 MB limit
                    update.message.reply_text("❌ File too large! Maximum size is 50 MB.")
                    return ConversationHandler.END
                
                with open(file_path, 'rb') as file:
                    file_name_escaped = escape_md_caption(os.path.basename(file_path))
                    file_size_escaped = escape_md_caption(format_size(file_size))
                    caption = f"📄 File: {file_name_escaped}\n📦 Size: {file_size_escaped}"
                    update.message.reply_document(
                        document=file,
                        filename=os.path.basename(file_path),
                        caption=caption,
                        parse_mode='MarkdownV2'
                    )
            else:
                update.message.reply_text("❌ File does not exist!")
                
        except Exception as e:
            update.message.reply_text(f"❌ Error downloading file: {str(e)}")
        
        return ConversationHandler.END
    
    def mkdir_start(self, update, context):
        """Start create directory conversation"""
        current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
        message = (
            "📁 *Enter the new directory name*\n\n"
            f"Current path: {escape_md(current_path)}\n\n"
            "*Examples:*\n"
            "• NewFolder\n"
            "• Projects/Python\n"
            "• Documents/2025\n\n"
            "_Type the directory name or /cancel to abort_"
        )
        update.message.reply_text(message, parse_mode='MarkdownV2')
        return self.WAITING_MKDIR
    
    def handle_mkdir_input(self, update, context):
        """Handle create directory input"""
        dir_name = update.message.text.strip()
        
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            dir_path = self.file_ops.create_directory(current_path, dir_name)
            update.message.reply_text(f"✅ Directory created: {dir_name}")
            
            # Refresh directory listing
            self.list_directory(update, context)
            
        except Exception as e:
            update.message.reply_text(f"❌ Error creating directory: {str(e)}")
        
        return ConversationHandler.END
    
    def delete_start(self, update, context):
        """Start delete item conversation"""
        self.list_directory(update, context)
        
        message = (
            "🗑 *Enter the name of file/folder to delete*\n\n"
            "*Examples:*\n"
            f"• {escape_md('file.txt')}\n"
            f"• {escape_md('OldFolder')}\n"
            f"• {escape_md('temp/cache.dat')}\n\n"
            "⚠️ *Warning: This action cannot be undone\\!*\n\n"
            "_Type the name or /cancel to abort_"
        )
        update.message.reply_text(message, parse_mode='MarkdownV2')
        return self.WAITING_DELETE
    
    def handle_delete_input(self, update, context):
        """Handle delete item input"""
        item_name = update.message.text.strip()
        
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            result = self.file_ops.delete_item(current_path, item_name)
            update.message.reply_text(f"✅ {result}")
            
            # Refresh directory listing
            self.list_directory(update, context)
            
        except Exception as e:
            update.message.reply_text(f"❌ Error deleting item: {str(e)}")
        
        return ConversationHandler.END
    
    def search_start(self, update, context):
        """Start search files conversation"""
        message = (
            "🔍 *Enter search pattern*\n\n"
            "*Examples:*\n"
            "• `document` \\- Find files/folders containing 'document'\n"
            "• `.pdf` \\- Find PDF files\n"
            "• `project` \\- Find items with 'project' in the name\n\n"
            "_Type search pattern or /cancel to abort_"
        )
        update.message.reply_text(message, parse_mode='MarkdownV2')
        return self.WAITING_SEARCH
    
    def handle_search_input(self, update, context):
        """Handle search files input"""
        pattern = update.message.text.strip()
        
        try:
            current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
            search_result = self.file_ops.search_files(current_path, pattern)
            
            escaped_pattern = escape_md(search_result['pattern'])
            if search_result['results']:
                message = f"🔍 *Search Results for '{escaped_pattern}'*\n"
                message += f"📊 *Found {search_result['total_found']} items*\n\n"
                
                formatted_results = [escape_md(result['display']) for result in search_result['results']]
                message += "\n".join(formatted_results)
                
                if search_result['search_limited']:
                    message += f"\n\n⚠️ *Search stopped at 1000 items for performance*"
                    
            else:
                message = f"❌ No files found matching '{escaped_pattern}'"

            send_long_message(update, message, 'MarkdownV2')

        except Exception as e:
            update.message.reply_text(f"❌ Error searching files: {escape_md(str(e))}", parse_mode='MarkdownV2')
        
        return ConversationHandler.END
    
    def upload_file(self, update, context):
        """Handle file upload"""
        if not update.message.document:
            update.message.reply_text("❌ Please send a file to upload")
            return
        
        current_path = context.user_data.get('current_path', self.file_ops.DEFAULT_PATH)
        
        if current_path == self.file_ops.DEFAULT_PATH:
            update.message.reply_text("❌ Please select a drive first using /cd command")
            return
            
        file = update.message.document
        
        try:
            file_path = os.path.join(current_path, file.file_name)
            
            # Get the file from Telegram
            file_info = context.bot.get_file(file.file_id)
            file_info.download(file_path)
            
            update.message.reply_text(f"✅ File uploaded: {file.file_name}\n📦 Size: {format_size(os.path.getsize(file_path))}")
            
            # Refresh directory listing
            self.list_directory(update, context)
            
        except Exception as e:
            update.message.reply_text(f"❌ Error uploading file: {str(e)}")
    
    def cancel_operation(self, update, context):
        """Cancel any file operation"""
        update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END
    
    def register_handlers(self, dispatcher):
        """Register semua file manager handlers"""
        # Basic commands
        dispatcher.add_handler(CommandHandler('ls', self.auth.require_auth(self.list_directory)))
        
        # Conversation handlers
        cd_handler = ConversationHandler(
            entry_points=[CommandHandler('cd', self.auth.require_auth(self.cd_start))],
            states={
                self.WAITING_CD: [MessageHandler(Filters.text & ~Filters.command, self.handle_cd_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        dispatcher.add_handler(cd_handler)
        
        download_handler = ConversationHandler(
            entry_points=[CommandHandler('download', self.auth.require_auth(self.download_start))],
            states={
                self.WAITING_DOWNLOAD: [MessageHandler(Filters.text & ~Filters.command, self.handle_download_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        dispatcher.add_handler(download_handler)
        
        mkdir_handler = ConversationHandler(
            entry_points=[CommandHandler('mkdir', self.auth.require_auth(self.mkdir_start))],
            states={
                self.WAITING_MKDIR: [MessageHandler(Filters.text & ~Filters.command, self.handle_mkdir_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        dispatcher.add_handler(mkdir_handler)
        
        delete_handler = ConversationHandler(
            entry_points=[CommandHandler('delete', self.auth.require_auth(self.delete_start))],
            states={
                self.WAITING_DELETE: [MessageHandler(Filters.text & ~Filters.command, self.handle_delete_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        dispatcher.add_handler(delete_handler)
        
        search_handler = ConversationHandler(
            entry_points=[CommandHandler('search', self.auth.require_auth(self.search_start))],
            states={
                self.WAITING_SEARCH: [MessageHandler(Filters.text & ~Filters.command, self.handle_search_input)]
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        dispatcher.add_handler(search_handler)
        
        # File upload handler
        dispatcher.add_handler(MessageHandler(Filters.document, self.auth.require_auth(self.upload_file)))
        
        self.logger.info("File manager handlers registered")