@echo off
echo ===================================
echo Discord Bot 停止腳本
echo ===================================
echo.
echo 正在尋找並停止 Discord 機器人進程...
echo.

:: 查找包含 bot.py 的 Python 進程並取得其 PID
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /nh ^| findstr /i "bot.py"') do (
    set PID=%%i
    goto :found
)

:notfound
echo 找不到運行中的 Discord 機器人進程！
goto :end

:found
echo 找到 Discord 機器人進程，PID: %PID%
echo 正在停止進程...
taskkill /PID %PID% /F
if %ERRORLEVEL% EQU 0 (
    echo Discord 機器人已成功停止！
) else (
    echo 停止 Discord 機器人時發生錯誤。錯誤代碼：%ERRORLEVEL%
)

:end
echo.
echo 按任意鍵退出...
pause
