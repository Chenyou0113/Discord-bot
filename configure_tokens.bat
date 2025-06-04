@echo off
chcp 65001 >nul
title Discord Bot 配置助手

echo ========================================
echo          Discord Bot 配置助手
echo ========================================
echo.

echo 此助手將幫助您配置 Discord Bot Token 和 Google API Key
echo.

echo [檢查] 正在檢查 .env 文件...
if not exist ".env" (
    echo [錯誤] 找不到 .env 文件
    if exist ".env.example" (
        echo [修復] 正在從範本創建 .env 文件...
        copy ".env.example" ".env" >nul
        echo [成功] 已創建 .env 文件
    ) else (
        echo [錯誤] 也找不到 .env.example 文件
        pause
        exit /b 1
    )
)

echo [成功] 找到 .env 文件
echo.

echo [檢查] 正在檢查當前配置...
findstr /C:"DISCORD_TOKEN=your_discord_bot_token_here" ".env" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] Discord Token 尚未配置
    set DISCORD_NEEDS_CONFIG=1
) else (
    echo [成功] Discord Token 已配置
    set DISCORD_NEEDS_CONFIG=0
)

findstr /C:"GOOGLE_API_KEY=your_google_api_key_here" ".env" >nul 2>&1
if %errorlevel% equ 0 (
    echo [警告] Google API Key 尚未配置
    set GOOGLE_NEEDS_CONFIG=1
) else (
    echo [成功] Google API Key 已配置
    set GOOGLE_NEEDS_CONFIG=0
)

echo.

if %DISCORD_NEEDS_CONFIG% equ 1 (
    echo ========================================
    echo          配置 Discord Token
    echo ========================================
    echo.
    echo 如何獲取 Discord Bot Token:
    echo 1. 前往 https://discord.com/developers/applications
    echo 2. 選擇您的應用程式或創建新的
    echo 3. 在左側選單點擊 'Bot'
    echo 4. 在 'Token' 部分點擊 'Reset Token' 或 'Copy'
    echo 5. 複製完整的 Token
    echo.
    echo 請手動編輯 .env 文件，將以下行：
    echo DISCORD_TOKEN=your_discord_bot_token_here
    echo 替換為：
    echo DISCORD_TOKEN=您的實際Token
    echo.
    echo 按任意鍵打開 .env 文件進行編輯...
    pause >nul
    notepad ".env"
    echo.
)

if %GOOGLE_NEEDS_CONFIG% equ 1 (
    echo ========================================
    echo        配置 Google API Key
    echo ========================================
    echo.
    echo 如何獲取 Google API Key:
    echo 1. 前往 https://aistudio.google.com/app/apikey
    echo 2. 點擊 'Create API Key'
    echo 3. 選擇現有專案或創建新專案
    echo 4. 複製生成的 API Key
    echo.
    echo 請在已打開的 .env 文件中，將以下行：
    echo GOOGLE_API_KEY=your_google_api_key_here
    echo 替換為：
    echo GOOGLE_API_KEY=您的實際API_Key
    echo.
    if %DISCORD_NEEDS_CONFIG% equ 0 (
        echo 按任意鍵打開 .env 文件進行編輯...
        pause >nul
        notepad ".env"
    )
    echo.
)

echo ========================================
echo            配置完成檢查
echo ========================================
echo.
echo 配置完成後，請：
echo 1. 確保已保存 .env 文件
echo 2. 確保所有 Token 都已正確填入
echo 3. 執行 start_bot_simple.bat 啟動機器人
echo.
echo 如果仍有問題，請檢查：
echo - Discord Token 是否為完整的 Bot Token（包含兩個點）
echo - Google API Key 是否有效
echo - .env 文件是否正確保存
echo.

pause
