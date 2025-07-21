# 🤖 Laptop Control Bot

A powerful Telegram bot that allows you to remotely control your Windows laptop from anywhere in the world. Control your laptop's power, monitor system resources, manage files, capture screenshots, and much more through simple Telegram commands.

![Bot Demo](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-green)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-blue)

## ✨ Features

### 🔌 Power Control
- **Shutdown** - Remotely power off your laptop
- **Restart** - Reboot your system
- **Sleep** - Put laptop to sleep mode
- **Lock** - Lock the screen
- **Cancel Shutdown** - Cancel pending shutdown operations

### 📊 System Monitoring
- **System Status** - Get basic system information
- **Resource Usage** - Monitor CPU, RAM, and disk usage
- **Battery Status** - Check battery level and charging status
- **Process Monitor** - View top active processes
- **Screenshot** - Capture current screen

### 📁 File Management
- **Browse Files** - Navigate through drives and directories
- **Download Files** - Download files from your laptop to Telegram
- **Upload Files** - Upload files from Telegram to your laptop
- **Create Folders** - Make new directories
- **Delete Items** - Remove files and folders
- **Search Files** - Find files by name pattern

### 📷 Webcam Control
- **Photo Capture** - Take photos from webcam
- **Video Recording** - Record 10-second videos with audio
- **Device Detection** - Automatically detect available cameras and microphones

### 🛡️ Security Features
- **User Authentication** - Password-protected access
- **Authorized User Only** - Restricted to specific Telegram user ID
- **Session Management** - Secure login/logout system

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Active internet connection
- Telegram account

### 1. Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the **Bot Token** (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

### 2. Get Your Telegram User ID

1. Search for `@userinfobot` on Telegram
2. Send `/start` command
3. Copy your **User ID** (a number like `123456789`)

### 3. Download and Setup

#### Option A: Download Pre-built Executable (Recommended)

1. Download the latest release from [Releases](https://github.com/zhafarullah/LaptopControlBot/releases/)
2. Extract the files to a folder
3. **Run `LaptopControlBot.exe`** directly
4. The program will automatically create a `config.py` template and exit with instructions
5. Edit the auto-generated `config.py` with your details:

```python
# config.py (auto-generated template)
BOT_TOKEN = 'your_bot_token_here'
AUTHORIZED_USER_ID = 123456789  # Your Telegram user ID
BOT_PASSWORD = 'your_secure_password'
```

6. **Run `LaptopControlBot.exe` again** to start the bot

#### Option B: Run from Source

1. Clone this repository:
```bash
git clone https://github.com/zhafarullah/LaptopControlBot.git
cd LaptopControlBot
```

2. **Ensure Python 3.10.x is installed**:
```bash
python --version  # Should show Python 3.10.x
```

3. Install dependencies (recommended in virtual environment):
```bash
pip install -r requirements.txt
```

4. Run the bot:
```bash
python main.py
```
   - The program will auto-create `config.py` template on first run
   - Edit `config.py` with your bot details
   - Run `python main.py` again to start

### 4. First Login

1. Open Telegram and find your bot
2. Send `/start` command
3. Send `/login` command
4. Enter your password when prompted
5. You're ready to control your laptop!

## 📖 Commands Reference

### Basic Commands
- `/start` - Welcome message and setup instructions
- `/help` - Complete list of available commands
- `/login` - Authenticate with password

### Power Control
- `/shutdown` - Shutdown the laptop
- `/restart` - Restart the laptop
- `/sleep` - Put laptop to sleep
- `/lock` - Lock the screen
- `/cancel_shutdown` - Cancel pending shutdown

### System Information
- `/status` - Basic system information
- `/sysinfo` - Detailed system resources (CPU, RAM, Disk)
- `/battery` - Battery status and time remaining
- `/processes` - Top 10 active processes
- `/screenshot` - Take a screenshot

### File Management
- `/ls` - List files in current directory
- `/cd` - Change directory (interactive)
- `/download` - Download a file (interactive)
- `/mkdir` - Create new directory (interactive)
- `/delete` - Delete file or folder (interactive)
- `/search` - Search for files (interactive)
- **Send any file** - Upload file to current directory

### Webcam
- `/webcam` - Capture photo from webcam
- `/webcamvideo` - Record 10-second video
- `/detectdevices` - Detect available video/audio devices

### Application Management
- `/closeapp` - Force close running applications (interactive)

## 🔧 Advanced Configuration

### Webcam Setup

For video recording with audio, you may need to configure device names:

1. Run `/detectdevices` command in Telegram
2. Copy the correct device names from the response
3. Update your `config.py`:

```python
WEBCAM_VIDEO_DEVICE = "Your Camera Name"
WEBCAM_AUDIO_DEVICE = "Your Microphone Name"
```

### FFmpeg Installation (Required for Video Recording with Audio)

For video recording with audio support:

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. **Add `C:\ffmpeg\bin` to your system PATH**:
   - Open "Environment Variables" in Windows
   - Add `C:\ffmpeg\bin` to the PATH variable
4. **Restart your computer** to apply PATH changes
5. Verify installation by opening Command Prompt and typing: `ffmpeg -version`

**Note**: Without FFmpeg, webcam video recording will use basic OpenCV recording (video only, no audio).

## 🚀 Auto-Start on Boot

### Method 1: Task Scheduler (Recommended)

1. **Open Task Scheduler** (`Win + R` → `taskschd.msc`)

2. **Create Basic Task**:
   - Click "Create Basic Task" in right panel
   - Name: `Laptop Control Bot`
   - Description: `Auto-start Telegram bot`

3. **Set Trigger**:
   - When: `When the computer starts`
   - Click Next

4. **Set Action**:
   - Action: `Start a program`
   - Program: `C:\path\to\LaptopControlBot.exe`
   - Start in: `C:\path\to\bot\folder`

5. **Advanced Settings**:
   - Check "Run with highest privileges"
   - Check "Run whether user is logged on"
   - Configure for: `Windows 11`
   - On Conditions tab, check "Start only if the following network connection is available"

6. **Test the task**:
   - Right-click task → "Run"
   - Check if bot starts successfully

### Method 2: Startup Folder

1. **Open Startup folder**:
   - Press `Win + R`
   - Type: `shell:startup`
   - Press Enter

2. **Create batch file**:
   ```batch
   @echo off
   cd /d "C:\path\to\your\bot\folder"
   start "" "LaptopControlBot.exe"
   ```

3. **Save as** `start_bot.bat` in startup folder

## 🛠️ Building from Source

### Prerequisites
- **Python 3.10.x** (ensure this exact version)
- Git (for cloning)

### Build Steps

1. **Verify Python Version**:
```bash
python --version  # Must show Python 3.10.x
```

2. **Clone repository**:
```bash
git clone https://github.com/zhafarullah/LaptopControlBot.git
cd LaptopControlBot
```

3. **Navigate to Build Folder**:
```bash
cd "Build Your Own"
```

4. **Run Build Script**:
```bash
build.bat
```

The build script will automatically:
- Create virtual environment with Python 3.10.x
- Install all dependencies
- Install PyInstaller
- Build the executable
- Create distribution package

5. **Find executable**:
   - Output: `dist/LaptopControlBot.exe`
   - Ready-to-distribute package in `dist/` folder

**Manual Build Command** (if needed):
```bash
pyinstaller --onefile --noconsole --name "LaptopControlBot" --icon=icon.ico --add-data "modules;modules" --hidden-import "modules" --hidden-import "telegram" --hidden-import "PIL" --hidden-import "cv2" --hidden-import "psutil" --hidden-import "win32gui" main.py
```

## 📁 Project Structure

```
LaptopControlBot/
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
├── Build Your Own/             # Build tools and scripts
│   ├── build.bat              # Automated build script
│   ├── main.py                # Copy of main entry point
│   ├── modules/               # Copy of bot modules
│   └── requirements.txt       # Build dependencies
├── modules/                    # Bot modules
│   ├── auth/                   # Authentication system
│   │   └── handlers.py
│   ├── system/                # System control
│   │   ├── power.py
│   │   ├── info.py
│   │   └── monitoring.py
│   ├── file_manager/          # File operations
│   │   ├── handlers.py
│   │   └── operations.py
│   ├── webcam/                # Camera control
│   │   ├── capture.py
│   │   └── video.py
│   └── utils/                 # Utilities
│       ├── helpers.py
│       ├── decorators.py
│       └── logging_setup.py
└── logs/                      # Auto-generated logs
    ├── bot.log
    └── bot_errors.log
```

## 🔒 Security Considerations

### Best Practices

1. **Strong Password**: Use a complex password for bot authentication
2. **User ID Verification**: Double-check your Telegram user ID
3. **Token Security**: Never share your bot token publicly
4. **Network Security**: Use VPN if accessing from untrusted networks
5. **Regular Updates**: Keep the bot updated with latest security patches

### Firewall Configuration

Allow the bot through Windows Firewall:
1. Go to Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add `LaptopControlBot.exe`
4. Allow both Private and Public networks

## 🐛 Troubleshooting

### Common Issues

#### Bot doesn't respond
- **Check internet connection**
- **Verify bot token in config.py**
- **Ensure bot is running (check system tray)**
- **Check firewall settings**

#### "Unauthorized" error
- **Double-check bot token from @BotFather**
- **Ensure no extra spaces in config.py**
- **Verify config.py format is correct**

#### "Access Denied" errors
- **Run bot as Administrator**
- **Check Windows permissions**
- **Verify User Account Control settings**

#### Webcam not working
- **Install FFmpeg and add to PATH**
- **Run `/detectdevices` to find correct camera names**
- **Check camera permissions in Windows Settings**
- **Update camera drivers**

#### Video recording fails
- **Ensure FFmpeg is installed and in PATH**
- **Restart computer after adding FFmpeg to PATH**
- **Test FFmpeg: open Command Prompt and type `ffmpeg -version`**
- **Use `/detectdevices` to find correct device names**

#### Build fails
- **Ensure Python version is exactly 3.10.x**
- **Run build.bat from "Build Your Own" folder**
- **Check if all dependencies are installed**

#### File operations failing
- **Check folder permissions**
- **Ensure sufficient disk space**
- **Verify file paths are correct**

#### Authentication issues
- **Verify user ID is correct (number, not username)**
- **Check password in config.py**
- **Ensure no extra spaces in config file**

### Log Files

Check log files for detailed error information:
- `logs/bot.log` - General operation log
- `logs/bot_errors.log` - Error-specific log
- `startup_log.txt` - Startup events

## 📝 Requirements

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 100MB free space
- **Network**: Internet connection required

### For Building from Source
- **Python**: Exactly version 3.10.x
- **FFmpeg**: For video recording with audio (optional)

### Python Dependencies
```
python-telegram-bot==13.15
psutil==5.9.6
Pillow==10.1.0
opencv-python==4.8.1.78
pywin32==306
humanize==4.8.0
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⭐ Support

If you find this project helpful, please consider giving it a star on GitHub!

**⚠️ Disclaimer**: This bot provides remote access to your computer. Use responsibly and ensure your bot token and password are kept secure. The developers are not responsible for any misuse or damage caused by this software.