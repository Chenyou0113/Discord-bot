@echo off
echo 🔍 測試腳本路徑修復
echo ===================
echo.

REM 切換到腳本的上層目錄（專案根目錄）
cd /d "%~dp0.."
echo 📁 當前目錄: %CD%
echo.

REM 檢查重要檔案是否存在
if exist bot.py (
    echo ✅ 找到 bot.py
) else (
    echo ❌ 找不到 bot.py
)

if exist cogs\info_commands_fixed_v4_clean.py (
    echo ✅ 找到主要模組檔案
) else (
    echo ❌ 找不到主要模組檔案
)

if exist config_files\levels.json (
    echo ✅ 找到配置檔案
) else (
    echo ❌ 找不到配置檔案
)

echo.
echo 🎯 路徑測試完成
pause
