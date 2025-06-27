@echo off
REM 氣象測站功能檢查和機器人啟動腳本
REM 作者: Discord Bot Project
REM 日期: 2025-01-05

echo ================================================================================
echo 氣象測站功能檢查和機器人啟動腳本
echo ================================================================================

echo.
echo 🔍 執行功能檢查...
python final_weather_check.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 功能檢查失敗，請修正問題後重試
    pause
    exit /b 1
)

echo.
echo 🤖 準備啟動機器人...
echo.
echo 💡 提示：
echo    • 機器人啟動後，請在 Discord 伺服器中測試以下指令：
echo      /weather_station 台北
echo      /weather_station_by_county 新北市
echo      /weather_station_info C0A940
echo    • 按 Ctrl+C 可停止機器人
echo    • 查看 bot.log 了解詳細執行記錄
echo.
echo 🚀 啟動機器人...
echo ================================================================================

python bot.py

echo.
echo 機器人已停止運行
pause
