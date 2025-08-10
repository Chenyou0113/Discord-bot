@echo off
chcp 65001 >nul 2>&1
title Discord Bot Config Helper

echo ========================================
echo          Discord Bot Config Helper
echo ========================================
echo.

echo This helper will assist you in configuring Discord Bot Token and Google API Key
echo.

echo [Check] Checking .env file...
if not exist ".env" (
    echo [Error] .env file not found
    if exist ".env.example" (
        echo [Fix] Creating .env file from template...
        copy ".env.example" ".env" >nul 2>&1
        echo [Success] .env file created
    ) else (
        echo [Error] .env.example file not found
        pause
        exit /b 1
    )
)

echo [Success] Found .env file
echo.

echo [Check] Checking current configuration...
findstr /C:"DISCORD_TOKEN=your_discord_bot_token_here" ".env" >nul 2>&1
if %errorlevel% equ 0 (
    echo [Warning] Discord Token not configured yet
    set DISCORD_NEEDS_CONFIG=1
) else (
    echo [Success] Discord Token configured
    set DISCORD_NEEDS_CONFIG=0
)

findstr /C:"GOOGLE_API_KEY=your_google_api_key_here" ".env" >nul 2>&1
if %errorlevel% equ 0 (
    echo [Warning] Google API Key not configured yet
    set GOOGLE_NEEDS_CONFIG=1
) else (
    echo [Success] Google API Key configured
    set GOOGLE_NEEDS_CONFIG=0
)

echo.

if %DISCORD_NEEDS_CONFIG% equ 1 (
    echo ========================================
    echo          Configure Discord Token
    echo ========================================
    echo.
    echo How to get Discord Bot Token:
    echo 1. Go to https://discord.com/developers/applications
    echo 2. Select your application or create new one
    echo 3. Click 'Bot' in left sidebar
    echo 4. In 'Token' section click 'Reset Token' or 'Copy'
    echo 5. Copy the complete Token
    echo.
    echo Please manually edit .env file, replace this line:
    echo DISCORD_TOKEN=your_discord_bot_token_here
    echo With:
    echo DISCORD_TOKEN=Your_Actual_Token
    echo.
    echo Press any key to open .env file for editing...
    pause >nul 2>&1
    notepad ".env"
    echo.
)

if %GOOGLE_NEEDS_CONFIG% equ 1 (
    echo ========================================
    echo        Configure Google API Key
    echo ========================================
    echo.
    echo How to get Google API Key:
    echo 1. Go to https://aistudio.google.com/app/apikey
    echo 2. Click 'Create API Key'
    echo 3. Select existing project or create new one
    echo 4. Copy the generated API Key
    echo.
    echo In the already opened .env file, replace this line:
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo With:
    echo GOOGLE_API_KEY=Your_Actual_API_Key
    echo.
    if %DISCORD_NEEDS_CONFIG% equ 0 (
        echo Press any key to open .env file for editing...
        pause >nul 2>&1
        notepad ".env"
    )
    echo.
)

echo ========================================
echo            Configuration Complete Check
echo ========================================
echo.
echo After configuration, please:
echo 1. Make sure .env file is saved
echo 2. Make sure all Tokens are correctly filled in
echo 3. Run start_bot_simple.bat to start the bot
echo.
echo If you still have problems, please check:
echo - Discord Token should be complete Bot Token (with two dots)
echo - Google API Key should be valid
echo - .env file should be correctly saved
echo.

pause
