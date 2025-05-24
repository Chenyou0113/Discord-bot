@echo off
echo 正在啟動修復後的 Discord 機器人...

REM 設置環境變數以避免 SSL 驗證問題
set PYTHONHTTPSVERIFY=0
set AIOHTTP_NO_EXTENSIONS=1

REM 確保使用正確的 Python 版本
python bot.py

REM 如果機器人異常終止，保持視窗開啟
if %errorlevel% neq 0 (
    echo 機器人程序異常終止，錯誤代碼：%errorlevel%
    pause
)
