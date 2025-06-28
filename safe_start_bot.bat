@echo off
echo Discord 氣象機器人 - 安全啟動腳本
echo =====================================
echo.

echo 1. 檢查並停止現有的機器人進程...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ 已停止現有的 Python 進程
) else (
    echo    ! 沒有找到運行中的 Python 進程
)

echo.
echo 2. 等待進程完全清理...
timeout /t 3 /nobreak >nul

echo.
echo 3. 檢查必要檔案...
if not exist bot.py (
    echo    ✗ 找不到 bot.py 檔案！
    pause
    exit /b 1
)
echo    ✓ bot.py 檔案存在

if not exist .env (
    echo    ⚠ 警告: 找不到 .env 檔案，請確保已設定環境變數
) else (
    echo    ✓ .env 檔案存在
)

echo.
echo 4. 檢查 Cogs 目錄...
if not exist cogs (
    echo    ✗ 找不到 cogs 目錄！
    pause
    exit /b 1
)
echo    ✓ cogs 目錄存在

echo.
echo 5. 啟動機器人...
echo    載入徹底修復版本，包含：
echo    - JSON 解析修復 ✓
echo    - 徹底的指令重複註冊修復 ✨
echo    - 改善的錯誤處理 ✓
echo    - 溫度分布查詢功能 ✓
echo    - 圖片顯示修復 ✨
echo.
echo    徹底修復詳情：
echo    • 多重清除機制 - 確保完全清理舊指令
echo    • 強制重新載入 - 處理已載入的擴展
echo    • 競爭條件避免 - 載入間隔和狀態檢查
echo    • 詳細狀態追蹤 - 載入過程透明化
echo.
echo    完整功能列表：
echo    • /temperature - 查詢台灣溫度分布狀態 (含圖片)
echo    • /air_quality_county - 縣市空氣品質（下拉選單）
echo    • /radar, /radar_large, /rainfall_radar - 雷達圖查詢
echo    • /weather_station - 氣象測站查詢
echo.

python bot.py

echo.
echo 機器人已停止運行
pause
