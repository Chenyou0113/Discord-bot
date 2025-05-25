@echo off
echo ===================================
echo Discord Bot 停止腳本
echo ===================================
echo.
echo 此腳本將嘗試停止正在運行的 Discord 機器人
echo.

echo 正在尋找運行中的機器人進程...
tasklist /FI "IMAGENAME eq python.exe" /FO LIST | find "python.exe" > nul
if %errorlevel% neq 0 (
    echo [資訊] 未發現運行中的 Python 進程。機器人可能已經停止。
    goto :end
)

echo 找到運行中的 Python 進程，嘗試終止與機器人相關的進程...

for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *bot.py*" /NH /FO csv ^| findstr "python.exe"') do (
    echo 正在終止進程 ID: %%a
    taskkill /PID %%a /F
)

echo.
echo 進程終止完成。
echo 如果仍有機器人視窗運行，請直接關閉該視窗。

:end
echo.
echo 按任意鍵退出...
pause > nul
