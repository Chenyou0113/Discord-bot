@echo off
echo ===================================
echo Discord Bot 啟動腳本 (最新版本)
echo ===================================
echo.
echo 此腳本將啟動 Discord 機器人
echo 功能: 支持2025年地震資料新格式及其他優化
echo.
echo 按任意鍵開始啟動機器人...
pause > nul

echo.
echo 檢查 Python 是否已安裝...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python。請確認 Python 已安裝且添加到系統路徑中。
    goto :error
)

echo [成功] Python 已安裝

echo 檢查是否存在必要的檔案...
if not exist "bot.py" (
    echo [錯誤] 找不到 bot.py 檔案。請確認您在正確的目錄中執行此腳本。
    goto :error
)

if not exist "cogs\info_commands_fixed_v4.py" (
    echo [錯誤] 找不到 cogs\info_commands_fixed_v4.py 檔案。
    goto :error
)

if not exist "cogs\admin_commands_fixed.py" (
    echo [錯誤] 找不到 cogs\admin_commands_fixed.py 檔案。
    goto :error
)

if not exist "cogs\chat_commands.py" (
    echo [錯誤] 找不到 cogs\chat_commands.py 檔案。
    goto :error
)

echo [成功] 找到所有必要檔案

echo 檢查是否已安裝必要的套件...
python -c "import discord, asyncio, aiohttp, google.generativeai, dotenv" > nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 可能缺少一些必要的套件。嘗試安裝...
    echo 安裝必要的套件...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [錯誤] 安裝套件時發生錯誤。
        goto :error
    )
)

echo [成功] 所有必要套件已安裝

echo 正在設置網路環境...
set PYTHONHTTPSVERIFY=0
set AIOHTTP_NO_EXTENSIONS=1
set SSL_CERT_FILE=
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=

echo.
echo 正在啟動 Discord 機器人...
echo 請等待約 1-2 分鐘，讓斜線指令完成同步...
echo.
echo 啟動日誌:
echo ------------------------------

python -X dev bot.py
if errorlevel 1 (
    echo 錯誤：機器人啟動失敗
    goto :error
)
goto :end

:error
echo.
echo [錯誤] 啟動機器人時發生錯誤。
echo 請檢查上方的錯誤訊息，或查看 bot.log 檔案以獲取更詳細的錯誤資訊。
pause
exit /b 1

:end
echo.
echo 機器人已停止運行。
pause
exit /b 0
