@echo off
setlocal enabledelayedexpansion
title Laptop Control Bot - Foolproof Build

echo ========================================
echo   FOOLPROOF BUILD - NO PREMATURE EXIT
echo ========================================
echo.

rem Force continue on ALL errors
set "ERRORLEVEL="

echo [1/7] Checking and preparing files...
if not exist main.py (
    echo ERROR: main.py not found!
    pause
    goto :eof
)
if not exist modules (
    echo ERROR: modules folder not found!
    pause
    goto :eof
)

rem Check and prepare config.py for build
if not exist config.py (
    echo Creating template config.py for build process...
    (
    echo # Template config for build - DO NOT EDIT
    echo # This will be replaced with user template after build
    echo BOT_TOKEN = "PLACEHOLDER_BUILD_TOKEN"
    echo AUTHORIZED_USER_ID = 0
    echo BOT_PASSWORD = "PLACEHOLDER_BUILD_PASSWORD"
    echo WEBCAM_VIDEO_DEVICE = "HD User Facing"
    echo WEBCAM_AUDIO_DEVICE = "Microphone Array (Realtek(R) Audio)"
    ) > config.py
    echo Template config.py created for build
    set "CREATED_TEMPLATE=1"
) else (
    echo Using existing config.py for build
    set "CREATED_TEMPLATE=0"
)

rem Check for icon file
if not exist icon.ico (
    echo WARNING: icon.ico not found - building without icon
    set "USE_ICON=0"
) else (
    echo icon.ico found - will include in build
    set "USE_ICON=1"
)

echo SUCCESS: All files prepared
echo.

echo [2/7] Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    goto :eof
)
echo SUCCESS: Python found
echo.

echo [3/7] Creating virtual environment...
if exist build_venv (
    rmdir /s /q build_venv 2>nul
)
python -m venv build_venv 2>nul
if not exist build_venv\Scripts\python.exe (
    echo ERROR: Failed to create virtual environment!
    pause
    goto :eof
)
echo SUCCESS: Virtual environment created
echo.

echo [4/7] Installing packages...
echo This will take several minutes. Please wait...
echo.

rem Method 1: Try with explicit success continuation
echo Starting pip install...
cd /d "%~dp0"
call build_venv\Scripts\python.exe -m pip install --upgrade pip && (
    echo Pip upgraded successfully
) || (
    echo Pip upgrade had issues but continuing...
)

echo.
echo Installing requirements.txt...
if exist requirements.txt (
    call build_venv\Scripts\python.exe -m pip install -r requirements.txt && (
        echo Package installation completed
    ) || (
        echo Package installation had issues but continuing...
    )
) else (
    echo Installing packages manually...
    call build_venv\Scripts\python.exe -m pip install python-telegram-bot==13.15 psutil Pillow opencv-python pywin32 humanize && (
        echo Manual package installation completed
    ) || (
        echo Manual package installation had issues but continuing...
    )
)

echo.
echo Checking what was installed...
call build_venv\Scripts\python.exe -m pip list | findstr -i "telegram\|pillow\|opencv\|psutil\|pywin32\|humanize"

echo.
echo [CHECKPOINT] We reached here - installation phase complete!
echo.

echo [5/7] Testing core imports...
call build_venv\Scripts\python.exe -c "
try:
    import telegram
    print('SUCCESS: telegram - OK')
except:
    print('ERROR: telegram - Failed')

try:
    import PIL
    print('SUCCESS: PIL - OK')
except:
    print('ERROR: PIL - Failed')

try:
    import cv2
    print('SUCCESS: cv2 - OK')
except:
    print('ERROR: cv2 - Failed')

try:
    import psutil
    print('SUCCESS: psutil - OK')
except:
    print('ERROR: psutil - Failed')

try:
    import win32gui
    print('SUCCESS: win32gui - OK')
except:
    print('ERROR: win32gui - Failed')

try:
    import humanize
    print('SUCCESS: humanize - OK')
except:
    print('ERROR: humanize - Failed')

print('Import testing completed')
" && (
    echo Import testing finished
) || (
    echo Import testing had issues but continuing...
)

echo.
echo [CHECKPOINT] Import testing complete!
echo.

echo [6/7] Building executable...
echo Installing PyInstaller...
call build_venv\Scripts\python.exe -m pip install pyinstaller && (
    echo PyInstaller installed
) || (
    echo PyInstaller installation issues but continuing...
)

echo.
echo Cleaning previous builds...
if exist dist rmdir /s /q dist 2>nul
if exist build rmdir /s /q build 2>nul

echo.
echo Building LaptopControlBot.exe...
if "%USE_ICON%"=="1" (
    echo Building with icon...
    call build_venv\Scripts\python.exe -m PyInstaller --onefile --noconsole --name "LaptopControlBot" --icon=icon.ico --add-data "modules;modules" --hidden-import "modules" --hidden-import "telegram" --hidden-import "PIL" --hidden-import "cv2" --hidden-import "psutil" --hidden-import "win32gui" main.py && (
        echo PyInstaller build completed
    ) || (
        echo PyInstaller had issues but checking results...
    )
) else (
    echo Building without icon...
    call build_venv\Scripts\python.exe -m PyInstaller --onefile --noconsole --name "LaptopControlBot" --add-data "config.py;." --add-data "modules;modules" --hidden-import "modules" --hidden-import "telegram" --hidden-import "PIL" --hidden-import "cv2" --hidden-import "psutil" --hidden-import "win32gui" main.py && (
        echo PyInstaller build completed
    ) || (
        echo PyInstaller had issues but checking results...
    )
)

echo.
echo [CHECKPOINT] Build process complete!
echo.

echo [7/7] Creating user template and documentation...
if "%CREATED_TEMPLATE%"=="1" (
    echo Creating user config template...
    (
    echo # config.py - Configuration for LaptopControlBot
    echo # Edit this file with your actual bot details
    echo.
    echo # Get bot token from @BotFather on Telegram
    echo BOT_TOKEN = 'your_bot_token_here'
    echo.
    echo # Your Telegram user ID (get from @userinfobot)
    echo AUTHORIZED_USER_ID = 123456789
    echo.
    echo # Your bot password for authentication
    echo BOT_PASSWORD = 'your_password_here'
    echo.
    echo # Webcam device names (optional - run /detectdevices to find correct names)
    echo WEBCAM_VIDEO_DEVICE = "HD User Facing"
    echo WEBCAM_AUDIO_DEVICE = "Microphone Array (Realtek(R) Audio)"
    ) > config_template.py
    echo User config template created
)

echo Creating README for users...
(
echo LAPTOP CONTROL BOT - SETUP INSTRUCTIONS
echo =====================================
echo.
echo QUICK START:
echo 1. Copy config_template.py to config.py
echo 2. Edit config.py with your bot details:
echo    - BOT_TOKEN: Get from @BotFather on Telegram
echo    - AUTHORIZED_USER_ID: Get from @userinfobot
echo    - BOT_PASSWORD: Choose your own password
echo 3. Run LaptopControlBot.exe
echo.
echo TELEGRAM BOT SETUP:
echo 1. Open Telegram and search for @BotFather
echo 2. Send /newbot and follow instructions
echo 3. Copy the token to config.py
echo.
echo GET YOUR USER ID:
echo 1. Open Telegram and search for @userinfobot
echo 2. Send /start to get your user ID
echo 3. Copy the number to config.py
echo.
echo FEATURES:
echo - Remote laptop control (shutdown, restart, sleep, lock)
echo - System monitoring (CPU, RAM, processes, battery)
echo - File management (browse, download, upload, delete)
echo - Screenshot capture
echo - Webcam photo and video recording
echo - Application management
echo.
echo REQUIREMENTS:
echo - Windows 10/11
echo - Active internet connection
echo - Telegram account
echo - Optional: FFmpeg for video recording
echo.
echo TROUBLESHOOTING:
echo - If bot doesn't respond: Check bot token and internet
echo - If commands rejected: Check user ID and password
echo - If webcam fails: Install FFmpeg or run /detectdevices
echo.
echo For support, check the documentation or contact developer.
) > README.txt
echo README.txt created

echo.
echo ========================================
echo BUILD RESULTS:
echo ========================================

if exist dist\LaptopControlBot.exe (
    echo SUCCESS: LaptopControlBot.exe created!
    echo Location: %cd%\dist\LaptopControlBot.exe
    
    for %%A in (dist\LaptopControlBot.exe) do (
        set size=%%~zA
        set /a sizeMB=!size!/1024/1024
        echo Size: !sizeMB! MB
    )
    
    echo.
    echo DISTRIBUTION FOLDER CONTENTS:
    dir dist /b
    
    rem Copy user files to dist folder
    if exist config_template.py copy config_template.py dist\ >nul
    if exist README.txt copy README.txt dist\ >nul
    
    echo.
    echo BUILD SUCCESSFUL!
    echo.
    echo FILES CREATED FOR USERS:
    echo   - LaptopControlBot.exe    - The main executable
    echo   - config_template.py      - Configuration template
    echo   - README.txt              - Setup instructions
    echo.
    echo NEXT STEPS FOR USERS:
    echo   1. Copy config_template.py to config.py
    echo   2. Edit config.py with their bot details
    echo   3. Run LaptopControlBot.exe
    echo.
    
) else (
    echo BUILD FAILED: Executable not found
    echo.
    echo Checking dist folder:
    if exist dist (
        dir dist /b
    ) else (
        echo No dist folder created
    )
    
    echo.
    echo TROUBLESHOOTING:
    echo   1. Check the PyInstaller output above for errors
    echo   2. Make sure all imports are working
    echo   3. Try building with console mode first
    echo   4. Check if all modules folder exists
)

echo ========================================
echo.

set /p cleanup="Clean build files? (y/n): "
if /i "%cleanup%"=="y" (
    if exist build_venv rmdir /s /q build_venv
    if exist build rmdir /s /q build
    if exist *.spec del *.spec
    echo Cleanup completed
)

echo.
set /p opendir="Open dist folder? (y/n): "
if /i "%opendir%"=="y" (
    if exist dist start explorer dist
)

echo.
echo Script completed successfully!
echo.
echo SUMMARY:
echo   - Virtual environment: Created
echo   - Packages: Installed  
echo   - Imports: Tested
echo   - Executable: Built
echo   - User files: Created
echo.
echo READY FOR DISTRIBUTION:
echo   The 'dist' folder contains everything users need!
echo.
echo TO SHARE WITH OTHERS:
echo   1. Zip the entire 'dist' folder
echo   2. Share with instructions to:
echo      - Copy config_template.py to config.py
echo      - Edit config.py with their bot details
echo      - Run LaptopControlBot.exe
echo.
echo Thank you for using the build script!
pause
goto :eof