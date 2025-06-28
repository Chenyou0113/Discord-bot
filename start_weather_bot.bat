@echo off
REM 氣象功能檢查和機器人啟動腳本
REM 作者: Discord Bot Project
REM 日期: 2025-06-28

echo ================================================================================
echo 氣象功能檢查和機器人啟動腳本
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
echo.
echo    氣象測站查詢：
echo      /weather_station 台北
echo      /weather_station_by_county 新北市
echo      /weather_station_info C0A940
echo.
echo    空氣品質查詢：
echo      /air_quality 台北
echo      /air_quality_county - ✨ 新功能：下拉選單選擇縣市
echo      /air_quality_site 中山
echo.
echo    雷達圖查詢：
echo      /radar - 一般範圍雷達圖
echo      /radar_large - 大範圍雷達圖
echo      /rainfall_radar - 降雨雷達圖 (樹林/南屯/林園)
echo      /radar_info - 雷達圖功能說明
echo.
echo    溫度分布查詢：
echo      /temperature - ✨ 新功能：查詢台灣溫度分布狀態
echo.
echo    • 按 Ctrl+C 可停止機器人
echo    • 查看 bot.log 了解詳細執行記錄
echo.
echo 🚀 啟動機器人...
echo ================================================================================

python bot.py

echo.
echo 機器人已停止運行
pause
