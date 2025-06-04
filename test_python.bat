@echo off
chcp 65001 > nul
title Python 測試

echo ================================================
echo               Python 環境測試
echo ================================================
echo.

echo [測試 1] 檢查 Python 是否可用...
python --version
if errorlevel 1 (
    echo [錯誤] Python 命令失敗
) else (
    echo [成功] Python 命令執行成功
)
echo.

echo [測試 2] 檢查主要套件...
python -c "import discord; print(f'Discord.py 版本: {discord.__version__}')"
if errorlevel 1 (
    echo [錯誤] Discord.py 導入失敗
) else (
    echo [成功] Discord.py 導入成功
)
echo.

echo [測試 3] 檢查 Google AI 套件...
python -c "import google.generativeai; print('Google Generative AI 可用')"
if errorlevel 1 (
    echo [錯誤] Google Generative AI 導入失敗
) else (
    echo [成功] Google Generative AI 導入成功
)
echo.

echo [測試 4] 檢查 .env 文件...
if exist ".env" (
    echo [成功] 找到 .env 文件
) else (
    echo [警告] 未找到 .env 文件，需要配置環境變數
)
echo.

echo ================================================
echo                  測試完成
echo ================================================
pause
