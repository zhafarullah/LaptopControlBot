# modules/webcam/capture.py
import os
import tempfile
import logging
import cv2
from telegram.ext import CommandHandler
from modules.utils.decorators import log_function_call

class WebcamCapture:
    """Handle webcam image capture"""
    
    def __init__(self, auth_handler):
        self.auth = auth_handler
        self.logger = logging.getLogger(__name__)
    
    @log_function_call
    def capture_image(self, update, context):
        """Capture image from webcam"""
        temp_file = None
        try:
            update.message.reply_text("📷 Capturing image from webcam...")
            
            # Initialize camera
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                update.message.reply_text("❌ Cannot access webcam. Please check if webcam is available.")
                return
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                update.message.reply_text("❌ Failed to capture image from webcam.")
                return
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Write image
            cv2.imwrite(temp_filename, frame)
            
            # Send image
            with open(temp_filename, 'rb') as photo:
                update.message.reply_photo(photo, caption="📸 Webcam snapshot!")
                
            self.logger.info("Webcam image captured successfully")
            
        except Exception as e:
            update.message.reply_text(f"❌ Error capturing webcam: {str(e)}")
            self.logger.error(f"Webcam capture error: {e}")
            
        finally:
            if temp_file:
                try:
                    os.unlink(temp_filename)
                except:
                    pass
    
    def register_handlers(self, dispatcher):
        """Register webcam capture handlers"""
        dispatcher.add_handler(CommandHandler('webcam', self.auth.require_auth(self.capture_image)))
        
        self.logger.info("Webcam capture handlers registered")