@echo off
cd /d "c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot"
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul
rd /s /q "cogs\__pycache__" 2>nul
python bot.py
