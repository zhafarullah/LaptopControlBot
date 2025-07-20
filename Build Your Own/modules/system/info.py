# modules/system/info.py
import platform
import psutil
import datetime
import logging
from telegram.ext import CommandHandler
from modules.utils.decorators import log_function_call

class SystemInfo:
    """Handle system information commands"""
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.logger = logging.getLogger(__name__)
    
    @log_function_call
    def status(self, update, context):
        """Get basic system information"""
        uname = platform.uname()
        info = (
            f"🖥️ *System Information*\n\n"
            f"🔹 *OS:* {uname.system}\n"
            f"🔹 *Computer Name:* {uname.node}\n"
            f"🔹 *OS Version:* {uname.release}\n"
            f"🔹 *Build:* {uname.version}\n"
            f"🔹 *Architecture:* {uname.machine}\n"
            f"🔹 *Processor:* {uname.processor}"
        )
        update.message.reply_text(info, parse_mode='Markdown')
    
    @log_function_call
    def battery(self, update, context):
        """Get battery status"""
        battery = psutil.sensors_battery()
        if battery:
            status = "🔌 Plugged In" if battery.power_plugged else "🔋 On Battery"
            time_left = str(datetime.timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "N/A"
            info = (
                f"🔋 *Battery Status*\n\n"
                f"• Level: {battery.percent}%\n"
                f"• Status: {status}\n"
                f"• Time Left: {time_left}"
            )
            update.message.reply_text(info, parse_mode='Markdown')
        else:
            update.message.reply_text("❌ No battery detected (desktop PC?)")
    
    @log_function_call
    def system_info(self, update, context):
        """Get detailed system resource information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        info = (
            f"💻 *System Resources*\n\n"
            f"*CPU:*\n"
            f"• Usage: {cpu_percent}%\n\n"
            f"*Memory:*\n"
            f"• Total: {memory.total / (1024**3):.1f} GB\n"
            f"• Used: {memory.used / (1024**3):.1f} GB ({memory.percent}%)\n"
            f"• Free: {memory.available / (1024**3):.1f} GB\n\n"
            f"*Disk:*\n"
            f"• Total: {disk.total / (1024**3):.1f} GB\n"
            f"• Used: {disk.used / (1024**3):.1f} GB ({disk.percent}%)\n"
            f"• Free: {disk.free / (1024**3):.1f} GB"
        )
        update.message.reply_text(info, parse_mode='Markdown')
    
    @log_function_call
    def processes(self, update, context):
        """Get top active processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0.1:
                    processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        processes = processes[:10]  # Top 10 processes
        
        info = "🔄 *Top 10 Active Processes*\n\n"
        for proc in processes:
            info += (f"• *{proc['name']}*\n"
                    f"  CPU: {proc['cpu_percent']:.1f}% | "
                    f"RAM: {proc['memory_percent']:.1f}%\n")
        
        update.message.reply_text(info, parse_mode='Markdown')
    
    def register_handlers(self, dispatcher):
        """Register semua system info handlers"""
        dispatcher.add_handler(CommandHandler('status', self.auth.require_auth(self.status)))
        dispatcher.add_handler(CommandHandler('battery', self.auth.require_auth(self.battery)))
        dispatcher.add_handler(CommandHandler('sysinfo', self.auth.require_auth(self.system_info)))
        dispatcher.add_handler(CommandHandler('processes', self.auth.require_auth(self.processes)))
        
        self.logger.info("System info handlers registered")