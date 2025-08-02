@echo off
chcp 65001 > nul
echo 🔧 Discord 機器人重啟檢查腳本
echo ================================

cd /d "%~dp0.."

echo 1️⃣ 停止現有機器人進程...
taskkill /f /im python.exe > nul 2>&1
timeout /t 3 > nul

echo 2️⃣ 檢查 reservoir_commands.py 語法...
python -m py_compile cogs\reservoir_commands.py
if %errorlevel% neq 0 (
    echo ❌ 語法錯誤，請檢查代碼
    pause
    exit /b 1
)
echo ✅ 語法檢查通過

echo 3️⃣ 啟動機器人...
echo ⏳ 正在啟動，請稍候...
if exist "venv\Scripts\python.exe" (
    start /min "venv\Scripts\python.exe" bot.py
) else (
    start /min python bot.py
)
timeout /t 10 > nul

echo 4️⃣ 檢查機器人狀態...
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -c "
import time
import os
try:
    time.sleep(5)
    if os.path.exists('bot.log'):
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = [line.strip() for line in lines[-20:] if line.strip()]
        
        print('📊 最近的日誌記錄:')
        for line in recent_lines:
            if any(word in line.lower() for word in ['成功', '啟動', '同步', 'sync', 'cog', '載入']):
                print(f'  ✅ {line}')
            elif any(word in line.lower() for word in ['錯誤', 'error', '失敗']):
                print(f'  ❌ {line}')
            else:
                print(f'  ℹ️ {line}')
    else:
        print('⚠️ 找不到 bot.log 文件')
except Exception as e:
    print(f'❌ 檢查時發生錯誤: {e}')
"

echo.
echo ✅ 檢查完成！請到 Discord 確認指令是否已更新
echo 💡 如需查看完整日誌: type bot.log
pause
