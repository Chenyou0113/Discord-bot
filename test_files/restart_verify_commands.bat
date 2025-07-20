@echo off
chcp 65001 > nul

echo 🔄 Discord 機器人重啟和指令驗證
echo ========================================

cd /d "C:\Users\xiaoy\Desktop\Discord bot"

echo.
echo 1️⃣ 停止現有機器人進程...
taskkill /f /im python.exe > nul 2>&1
echo ✅ 已停止現有進程

echo.
echo 2️⃣ 等待進程完全結束...
timeout /t 3 > nul

echo.
echo 3️⃣ 檢查 reservoir_commands.py 語法...
python -c "
import sys, os
os.chdir(r'C:\\Users\\xiaoy\\Desktop\\Discord bot')
sys.path.insert(0, '.')
try:
    with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
        content = f.read()
    compile(content, 'cogs/reservoir_commands.py', 'exec')
    print('✅ 語法檢查通過')
    
    import re
    commands = re.findall(r'@app_commands\.command\([^)]*name\s*=\s*[\"\'']([^\"\']+)[\"\'']', content)
    print(f'📊 找到 {len(commands)} 個指令: {\"， \".join(commands)}')
    
    if 'async def setup(' in content:
        print('✅ setup 函數存在')
    else:
        print('❌ setup 函數缺失')
        
except Exception as e:
    print(f'❌ 檢查失敗: {e}')
    exit(1)
"

if %errorlevel% neq 0 (
    echo ❌ reservoir_commands.py 有問題，請檢查
    pause
    exit /b 1
)

echo.
echo 4️⃣ 啟動機器人...
echo ⏳ 正在啟動，請稍候...

start "Discord Bot" /min cmd /c "python bot.py"

echo.
echo 5️⃣ 等待機器人初始化...
timeout /t 8 > nul

echo.
echo 6️⃣ 檢查機器人狀態和指令同步...
python -c "
import time, os, re
time.sleep(2)

if os.path.exists('bot.log'):
    with open('bot.log', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if lines:
        print('📊 檢查最近的日誌記錄:')
        recent_lines = lines[-30:]
        
        # 查找載入相關日誌
        load_lines = [line.strip() for line in recent_lines 
                     if any(keyword in line.lower() for keyword in 
                           ['載入', '成功啟動', 'reservoir', 'cog', '同步', 'sync'])]
        
        if load_lines:
            for line in load_lines[-10:]:
                if 'reservoir' in line.lower():
                    print(f'  🎯 {line}')
                elif '成功' in line or 'sync' in line.lower():
                    print(f'  ✅ {line}')
                else:
                    print(f'  ℹ️ {line}')
        else:
            print('  ⚠️ 沒有找到相關日誌')
            print('  最後幾行日誌:')
            for line in recent_lines[-5:]:
                print(f'    {line.strip()}')
        
        # 檢查同步的指令
        sync_lines = [line for line in recent_lines if '同步' in line and '指令' in line]
        if sync_lines:
            print('\\n🔄 指令同步狀態:')
            for line in sync_lines[-3:]:
                print(f'  {line.strip()}')
    else:
        print('⚠️ 日誌文件為空')
else:
    print('❌ 找不到 bot.log')
"

echo.
echo ========================================
echo ✅ 重啟完成！
echo.
echo 💡 接下來的步驟:
echo 1. 檢查上面的日誌輸出
echo 2. 到 Discord 查看新指令是否出現
echo 3. 測試 /water_level 等新指令
echo.
echo 📋 新增的指令應該包括:
echo   - /water_level (河川水位查詢)
echo   - /water_cameras (水利防災監視器)
echo   - /national_highway_cameras (國道監視器)
echo   - /general_road_cameras (一般道路監視器)
echo   - /water_disaster_cameras (舊版相容)
echo.
pause
