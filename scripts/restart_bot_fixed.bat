@echo off
echo 正在重新啟動 Discord Bot...
echo 使用新的 Gemini 1.5 Flash 模型
cd /d "%~dp0.."

if exist "venv\Scripts\python.exe" (
    echo 使用虛擬環境 Python...
    "venv\Scripts\python.exe" bot.py
) else (
    echo 使用系統 Python...
    python bot.py
)
pause
