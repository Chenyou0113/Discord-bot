@echo off
chcp 65001 > nul
title Discord 機器人 - 統一啟動腳本
color 0B

echo ====================================
echo       Discord 機器人啟動程序
echo ====================================
echo.

:: 檢查 Python 是否安裝
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [錯誤] 找不到 Python。請確認 Python 已安裝且已添加到 PATH 中。
    echo 您可以從 https://www.python.org/downloads/ 下載 Python。
    pause
    exit /b 1
)

:: 顯示 Python 版本
python --version
echo.

:: 檢查 bot.py 是否存在
if not exist "bot.py" (
    echo [錯誤] 找不到 bot.py 檔案。請確認您在正確的目錄中執行此腳本。
    pause
    exit /b 1
)

:: 檢查 Cogs 資料夾
if not exist "cogs" (
    echo [錯誤] 找不到 cogs 資料夾。
    pause
    exit /b 1
)

:: 檢查必要的 Cogs 模組
set MISSING_FILES=0
for %%F in (
    "cogs\admin_commands_fixed.py"
    "cogs\basic_commands.py"
    "cogs\chat_commands.py"
    "cogs\info_commands_fixed_v4_clean.py"
    "cogs\level_system.py"
    "cogs\monitor_system.py"
    "cogs\voice_system.py"
) do (
    if not exist "%%F" (
        echo [警告] 找不到模組: %%F
        set /a MISSING_FILES+=1
    )
)

if %MISSING_FILES% gtr 0 (
    echo.
    echo [警告] 有 %MISSING_FILES% 個必要模組檔案遺失。機器人可能無法正常運作。
    echo 是否仍要繼續啟動？(Y/N)
    choice /c YN /m "請選擇: "
    if %ERRORLEVEL% equ 2 (
        echo 已取消啟動。
        pause
        exit /b 1
    )
)

:: 檢查 requirements.txt 並安裝依賴
if exist "requirements.txt" (
    echo 檢查並安裝必要套件...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [警告] 安裝套件時發生錯誤。某些功能可能無法正常運作。
    ) else (
        echo 套件安裝完成。
    )
) else (
    echo [警告] 找不到 requirements.txt 檔案。將跳過套件檢查。
)

echo.
echo 正在啟動 Discord 機器人...
echo 按 Ctrl+C 可停止機器人。
echo.

:: 啟動機器人
python bot.py

echo.
if %ERRORLEVEL% neq 0 (
    echo [錯誤] 機器人發生錯誤並停止運行。
    echo 請檢查 bot.log 檔案以獲取詳細錯誤訊息。
) else (
    echo 機器人已正常關閉。
)

pause