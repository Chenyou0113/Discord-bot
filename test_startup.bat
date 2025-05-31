@echo off
echo 測試啟動腳本的檔案檢查功能...
echo.

if exist "bot.py" (
    echo ✅ bot.py 檔案存在
) else (
    echo ❌ bot.py 檔案不存在
)

if exist "cogs\info_commands_fixed_v4_clean.py" (
    echo ✅ info_commands_fixed_v4_clean.py 檔案存在
) else (
    echo ❌ info_commands_fixed_v4_clean.py 檔案不存在
)

if exist "cogs\admin_commands_fixed.py" (
    echo ✅ admin_commands_fixed.py 檔案存在
) else (
    echo ❌ admin_commands_fixed.py 檔案不存在
)

if exist "cogs\chat_commands.py" (
    echo ✅ chat_commands.py 檔案存在
) else (
    echo ❌ chat_commands.py 檔案不存在
)

echo.
echo 測試完成。
pause
