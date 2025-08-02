@echo off
chcp 65001 >nul
title 虛擬環境診斷

echo ========================================
echo         虛擬環境診斷工具
echo ========================================
echo.

REM 切換到專案根目錄
cd /d "%~dp0.."

echo [1] 檢查虛擬環境文件...
if exist "venv\Scripts\python.exe" (
    echo ✅ 找到虛擬環境 Python
) else (
    echo ❌ 虛擬環境 Python 不存在
    goto :error
)

if exist "venv\Scripts\activate.bat" (
    echo ✅ 找到啟動腳本
) else (
    echo ❌ 虛擬環境啟動腳本不存在
    goto :error
)

echo.
echo [2] 直接測試虛擬環境 Python...
"venv\Scripts\python.exe" --version
if errorlevel 1 (
    echo ❌ 虛擬環境 Python 測試失敗
    goto :error
)
echo ✅ 虛擬環境 Python 測試成功

echo.
echo [3] 測試 Python 命令...
"venv\Scripts\python.exe" --version
if errorlevel 1 (
    echo ❌ Python 命令失敗
    goto :error
)
echo ✅ Python 命令正常

echo.
echo [4] 檢查 Python 路徑...
"venv\Scripts\python.exe" -c "import sys; print('Python 路徑:', sys.executable)"

echo.
echo [5] 測試套件導入...
"venv\Scripts\python.exe" -c "import discord; print('✅ Discord.py 版本:', discord.__version__)"
if errorlevel 1 (
    echo ❌ Discord.py 導入失敗
    echo 正在嘗試重新安裝...
    python -m pip install discord.py
)

python -c "import google.generativeai; print('✅ Google Generative AI 可用')"
if errorlevel 1 (
    echo ❌ Google Generative AI 導入失敗
    echo 正在嘗試重新安裝...
    python -m pip install google-generativeai
)

echo.
echo [6] 檢查所有必要套件...
python -c "import os; from dotenv import load_dotenv; print('✅ 所有基本套件正常')"
if errorlevel 1 (
    echo ❌ 基本套件有問題
    echo 正在重新安裝所有套件...
    python -m pip install -r requirements.txt
)

echo.
echo ========================================
echo            診斷完成
echo ========================================
echo 如果所有項目都顯示 ✅，則環境配置正確
echo 現在可以嘗試啟動機器人
pause
exit /b 0

:error
echo.
echo ========================================
echo            診斷失敗
echo ========================================
echo 請檢查上述錯誤信息
pause
exit /b 1
