# modules/webcam/video.py
import os
import tempfile
import logging
import subprocess
import datetime
import cv2
from telegram.ext import CommandHandler
from modules.utils.decorators import log_function_call
from modules.utils.helpers import format_size

class WebcamVideo:
    """Handle webcam video recording"""
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.logger = logging.getLogger(__name__)
        self.config = auth_handler.config
    
    def check_ffmpeg(self):
        """Check apakah ffmpeg tersedia di sistem"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @log_function_call
    def record_video(self, update, context):
        """Record video dari webcam"""
        temp_file = None
        try:
            # Check ffmpeg
            if not self.check_ffmpeg():
                update.message.reply_text(
                    "❌ FFmpeg tidak ditemukan!\n\n"
                    "Download dari: https://ffmpeg.org/download.html\n"
                    "Tambahkan ke PATH dan restart bot.",
                    parse_mode='Markdown'
                )
                return
            
            update.message.reply_text("🎥 Merekam video dengan audio selama 10 detik...")
            
            # Buat temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Command dengan codec mobile-friendly
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'dshow',
                '-i', f'video={self.config.WEBCAM_VIDEO_DEVICE}:audio={self.config.WEBCAM_AUDIO_DEVICE}',
                '-t', '10',  # 10 detik
                
                # VIDEO SETTINGS - Mobile Compatible
                '-vcodec', 'libx264',
                '-profile:v', 'baseline',  # Profile baseline untuk kompatibilitas maksimal
                '-level', '3.0',           # Level 3.0 untuk support semua device
                '-pix_fmt', 'yuv420p',     # Pixel format yang didukung semua player
                '-preset', 'medium',       # Balance antara speed dan compression
                
                # AUDIO SETTINGS - Mobile Compatible  
                '-acodec', 'aac',
                '-ac', '2',                # Stereo
                '-ar', '44100',            # Sample rate standard
                '-ab', '128k',             # Audio bitrate
                
                # CONTAINER SETTINGS
                '-movflags', '+faststart', # Optimize untuk streaming/playback
                '-f', 'mp4',               # Force MP4 container
                
                # QUALITY SETTINGS
                '-r', '30',                # 30 FPS
                '-s', '1280x720',          # HD resolution
                '-crf', '23',              # Constant Rate Factor (good quality)
                
                '-y',  # Overwrite
                temp_filename
            ]
            
            # Jalankan ffmpeg
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Cek hasil
            if result.returncode == 0 and os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 10000:
                # Berhasil dengan audio
                with open(temp_filename, 'rb') as video:
                    file_size = format_size(os.path.getsize(temp_filename))
                    caption = f"🎬 Video webcam (10 detik) dengan audio!\n📦 Size: {file_size}\n📱 Mobile-friendly format"
                    update.message.reply_video(
                        video,
                        caption=caption,
                        supports_streaming=True
                    )
                    self.logger.info("Mobile-compatible video with audio recorded successfully")
                return
            else:
                # Fallback: video only dengan mobile settings
                self.logger.warning(f"Video with audio failed: {result.stderr[:300]}")
                update.message.reply_text("⚠️ Gagal merekam dengan audio, mencoba video saja...")
                
                ffmpeg_cmd_video = [
                    'ffmpeg',
                    '-f', 'dshow',
                    '-i', f'video={self.config.WEBCAM_VIDEO_DEVICE}',
                    '-t', '10',
                    
                    # VIDEO SETTINGS - Mobile Compatible
                    '-vcodec', 'libx264',
                    '-profile:v', 'baseline',
                    '-level', '3.0',
                    '-pix_fmt', 'yuv420p',
                    '-preset', 'medium',
                    '-movflags', '+faststart',
                    '-f', 'mp4',
                    '-r', '30',
                    '-s', '1280x720',
                    '-crf', '23',
                    
                    '-y',
                    temp_filename
                ]
                
                result2 = subprocess.run(
                    ffmpeg_cmd_video,
                    capture_output=True,
                    text=True,
                    timeout=20,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if result2.returncode == 0 and os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 10000:
                    with open(temp_filename, 'rb') as video:
                        file_size = format_size(os.path.getsize(temp_filename))
                        caption = f"🎬 Video webcam (10 detik, tanpa audio)\n📦 Size: {file_size}\n📱 Mobile-friendly format"
                        update.message.reply_video(
                            video,
                            caption=caption,
                            supports_streaming=True
                        )
                        self.logger.info("Mobile-compatible video only recorded successfully")
                    return
                else:
                    # Final fallback: OpenCV dengan mobile encoding
                    self.logger.warning("All FFmpeg methods failed. Trying OpenCV with mobile encoding.")
                    update.message.reply_text("⚠️ Menggunakan OpenCV dengan mobile encoding...")
                    self.record_video_opencv_mobile(update, context, temp_filename)
                        
        except subprocess.TimeoutExpired:
            update.message.reply_text("❌ Timeout saat merekam. Coba lagi.")
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
            self.logger.error(f"Webcam video error: {e}")
        finally:
            if temp_file:
                try:
                    os.unlink(temp_filename)
                except:
                    pass
    
    def record_video_opencv_mobile(self, update, context, temp_filename_final):
        """OpenCV fallback dengan encoding mobile-friendly"""
        temp_file_raw = None
        try:
            update.message.reply_text("📹 Merekam dengan OpenCV + mobile encoding...")
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                update.message.reply_text("❌ Tidak dapat mengakses webcam.")
                return
                
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Temporary file untuk raw video
            temp_file_raw = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
            temp_filename_raw = temp_file_raw.name
            temp_file_raw.close()
            
            # Record dengan OpenCV (raw format)
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Use XVID for raw recording
            fps = 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(temp_filename_raw, fourcc, fps, (width, height))
            
            start_time = datetime.datetime.now()
            frame_count = 0
            
            while (datetime.datetime.now() - start_time).total_seconds() < 10:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            # Convert ke mobile-friendly format dengan FFmpeg
            if frame_count > 0 and os.path.exists(temp_filename_raw) and os.path.getsize(temp_filename_raw) > 1000:
                
                # Convert dengan FFmpeg untuk mobile compatibility
                convert_cmd = [
                    'ffmpeg',
                    '-i', temp_filename_raw,
                    
                    # Mobile-compatible settings
                    '-vcodec', 'libx264',
                    '-profile:v', 'baseline',
                    '-level', '3.0',
                    '-pix_fmt', 'yuv420p',
                    '-preset', 'medium',
                    '-movflags', '+faststart',
                    '-f', 'mp4',
                    '-crf', '23',
                    
                    '-y',
                    temp_filename_final
                ]
                
                convert_result = subprocess.run(
                    convert_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if convert_result.returncode == 0 and os.path.exists(temp_filename_final) and os.path.getsize(temp_filename_final) > 1000:
                    with open(temp_filename_final, 'rb') as video:
                        file_size = format_size(os.path.getsize(temp_filename_final))
                        caption = f"🎬 Video webcam (OpenCV + mobile encoding)\n📦 Size: {file_size}\n📱 Mobile-friendly format"
                        update.message.reply_video(
                            video,
                            caption=caption,
                            supports_streaming=True
                        )
                        self.logger.info("OpenCV + mobile encoding video recorded successfully")
                else:
                    update.message.reply_text("❌ Gagal convert video ke format mobile.")
            else:
                update.message.reply_text("❌ Gagal merekam video dengan OpenCV.")
                
        except Exception as e:
            update.message.reply_text(f"❌ OpenCV mobile error: {str(e)}")
            self.logger.error(f"OpenCV mobile error: {e}")
        finally:
            # Cleanup both files
            if temp_file_raw:
                try:
                    os.unlink(temp_filename_raw)
                except:
                    pass
    
    @log_function_call
    def detect_devices(self, update, context):
        """Command untuk mendeteksi nama device video dan audio yang tersedia"""
        try:
            if not self.check_ffmpeg():
                update.message.reply_text("❌ FFmpeg tidak ditemukan. Install FFmpeg terlebih dahulu.")
                return
            
            update.message.reply_text("🔍 Mendeteksi device video dan audio...")
            
            # Method 1: Jalankan ffmpeg untuk list devices
            result = subprocess.run(
                ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Gabungkan stdout dan stderr
            output = result.stderr + "\n" + result.stdout
            
            # Debug: kirim raw output ke log
            self.logger.info(f"FFmpeg device detection raw output:\n{output}")
            
            video_devices = []
            audio_devices = []
            
            # Parse dengan regex yang lebih fleksibel
            import re
            
            # Pattern untuk mendeteksi device DirectShow
            device_pattern = r'\[dshow.*?\]\s*"([^"]+)"'
            
            lines = output.split('\n')
            current_section = None
            
            for line in lines:
                # Deteksi section
                if 'DirectShow video devices' in line or 'video devices' in line.lower():
                    current_section = 'video'
                    continue
                elif 'DirectShow audio devices' in line or 'audio devices' in line.lower():
                    current_section = 'audio'
                    continue
                
                # Cari device names dengan regex
                matches = re.findall(device_pattern, line)
                for device_name in matches:
                    device_name = device_name.strip()
                    if device_name and len(device_name) > 1:  # Skip empty atau terlalu pendek
                        if current_section == 'video' and device_name not in video_devices:
                            video_devices.append(device_name)
                        elif current_section == 'audio' and device_name not in audio_devices:
                            audio_devices.append(device_name)
            
            # Method 2: Jika masih kosong, coba dengan PowerShell (Windows alternative)
            if not video_devices and not audio_devices:
                try:
                    self.logger.info("FFmpeg parsing failed, trying PowerShell method...")
                    
                    # Get video devices dengan PowerShell
                    ps_video_cmd = [
                        'powershell', '-Command',
                        'Get-CimInstance Win32_PnPEntity | Where-Object {$_.PNPClass -eq "Camera" -or $_.Name -like "*camera*" -or $_.Name -like "*webcam*"} | Select-Object Name | Format-Table -HideTableHeaders'
                    ]
                    
                    result_video = subprocess.run(ps_video_cmd, capture_output=True, text=True, timeout=10)
                    
                    if result_video.returncode == 0:
                        for line in result_video.stdout.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('-') and len(line) > 3:
                                video_devices.append(line)
                    
                    # Get audio devices dengan PowerShell
                    ps_audio_cmd = [
                        'powershell', '-Command',
                        'Get-CimInstance Win32_SoundDevice | Select-Object Name | Format-Table -HideTableHeaders'
                    ]
                    
                    result_audio = subprocess.run(ps_audio_cmd, capture_output=True, text=True, timeout=10)
                    
                    if result_audio.returncode == 0:
                        for line in result_audio.stdout.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('-') and len(line) > 3:
                                audio_devices.append(line)
                                
                except Exception as e:
                    self.logger.warning(f"PowerShell method failed: {e}")
            
            # Method 3: Fallback - test common device names
            if not video_devices:
                common_video = [
                    "Integrated Camera", "USB2.0 HD UVC WebCam", "HD WebCam", 
                    "USB Camera", "WebCam", "Laptop Camera", "Built-in Camera"
                ]
                video_devices = common_video
                self.logger.info("Using common video device names as fallback")
            
            if not audio_devices:
                common_audio = [
                    "Microphone Array", "Microphone", "Built-in Microphone",
                    "Internal Microphone", "Default", "Stereo Mix"
                ]
                audio_devices = common_audio
                self.logger.info("Using common audio device names as fallback")
            
            # Format response dengan informasi tambahan
            from modules.utils.helpers import escape_md, send_long_message
            
            message = "🎥 *Device yang Terdeteksi:*\n\n"
            
            if video_devices:
                message += "*📹 Video Devices:*\n"
                for i, device in enumerate(video_devices, 1):
                    message += f"{i}\\. `{escape_md(device)}`\n"
                message += "\n"
            
            if audio_devices:
                message += "*🎤 Audio Devices:*\n"
                for i, device in enumerate(audio_devices, 1):
                    message += f"{i}\\. `{escape_md(device)}`\n"
                message += "\n"
            
            message += "*💡 Cara Menggunakan:*\n"
            message += "1\\. Pilih satu nama dari video dan audio device di atas\n"
            message += "2\\. Test dengan /testdevice \\<video\\> \\<audio\\>\n"
            message += "3\\. Jika berhasil, update kode dengan nama tersebut\n\n"
            message += "*Contoh test:*\n"
            if video_devices and audio_devices:
                message += f"`/testdevice {video_devices[0]} {audio_devices[0]}`"
            
            send_long_message(update, message, 'MarkdownV2')
            
        except subprocess.TimeoutExpired:
            update.message.reply_text("❌ Timeout saat mendeteksi device.")
        except Exception as e:
            update.message.reply_text(f"❌ Error mendeteksi device: {str(e)}")
            self.logger.error(f"Error in detect_devices: {e}")
    
    def register_handlers(self, dispatcher):
        """Register webcam video handlers"""
        dispatcher.add_handler(CommandHandler('webcamvideo', self.auth.require_auth(self.record_video)))
        dispatcher.add_handler(CommandHandler('detectdevices', self.auth.require_auth(self.detect_devices)))
        
        self.logger.info("Webcam video handlers registered")