REM 最新版本的 Discord 機器人啟動腳本
@echo off
chcp 65001 > nul
title Discord Bot - 2025版本

echo ================================================
echo        Discord Bot 啟動腳本 (2025年版本)
echo ================================================
echo.
echo 此腳本將啟動並監控 Discord 機器人
echo 功能:
echo - 支持2025年地震資料新格式
echo - 優化的互動界面
echo - 改進的天氣顯示 (同一天的資訊顯示在一起)
echo - 等級系統性能優化
echo.

REM 檢查環境
echo [檢查] 正在檢查必要環境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python。請確認 Python 已安裝且添加到系統路徑中。
    goto :error
)
echo [成功] Python 已安裝

REM 檢查虛擬環境
if exist "venv\Scripts\activate.bat" (
    echo [信息] 找到虛擬環境，正在啟用...
    call venv\Scripts\activate.bat
    echo [成功] 已啟用虛擬環境
) else (
    echo [警告] 未找到虛擬環境。將使用全局 Python 環境。
)

REM 檢查主要檔案
echo [檢查] 正在檢查必要檔案...
if not exist "bot.py" (
    echo [錯誤] 找不到主程式檔案 bot.py
    goto :error
)

if not exist "cogs\info_commands_fixed_v4.py" (
    echo [錯誤] 找不到資訊指令模組
    goto :error
)

if not exist "cogs\level_system.py" (
    echo [錯誤] 找不到等級系統模組
    goto :error
)

if not exist ".env" (
    echo [警告] 找不到 .env 檔案，機器人可能無法正常運作
    echo [信息] 請確保已設定必要的環境變數
)

echo [成功] 所有必要檔案檢查通過

REM 運行最終驗證
echo [檢查] 正在執行最終驗證...
python final_verification.py
if %errorlevel% neq 0 (
    echo [警告] 最終驗證發現一些問題，但仍將嘗試啟動機器人
) else (
    echo [成功] 最終驗證通過
)

echo.
echo [啟動] 正在啟動 Discord 機器人...
echo [信息] 按 Ctrl+C 終止機器人

python bot.py
if %errorlevel% neq 0 (
    echo [錯誤] 機器人意外終止
    goto :error
)

goto :end

:error
echo.
echo ================================================
echo                    發生錯誤
echo ================================================
echo 請檢查上方錯誤信息，或查閱 bot.log 檔案以獲取更多資訊。
pause
exit /b 1

:end
echo.
echo ================================================
echo              機器人已正常關閉
echo ================================================
pause
exit /b 0
