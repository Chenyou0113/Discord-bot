@echo off
setlocal

echo Verifying Git repository...
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo Error: This script must be run from within a Git repository.
    echo Please navigate to your project folder (c:\Users\xiaoy\Desktop\Discord bot\) and try again.
    pause
    exit /b 1
)

echo.
set /p COMMIT_MESSAGE="請輸入提交訊息 (直接按 Enter 使用預設訊息): "
if "%COMMIT_MESSAGE%"=="" (
    set "COMMIT_MESSAGE=Automated commit: Bot updates %date% %time%"
)

echo.
echo 正在將所有變更加入暫存區...
git add .
if errorlevel 1 (
    echo Error: 無法將變更加入暫存區。
    pause
    exit /b 1
)

echo.
echo 正在提交變更，訊息為: "%COMMIT_MESSAGE%"
git commit -m "%COMMIT_MESSAGE%"
if errorlevel 1 (
    echo Info: 沒有需要提交的變更，或者提交失敗。
    echo 將嘗試推送任何現有的待推送提交。
)

echo.
echo 正在取得目前分支名稱...
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set CURRENT_BRANCH=%%i
if not defined CURRENT_BRANCH (
    echo Error: 無法取得目前分支名稱。
    pause
    exit /b 1
)
echo 目前分支為: %CURRENT_BRANCH%

echo.
echo 正在將變更推送到 origin/%CURRENT_BRANCH%...
git push origin %CURRENT_BRANCH%
if errorlevel 1 (
    echo Error: 推送變更失敗。請檢查您的網路連線、GitHub 權限以及遠端儲存庫設定。
    echo 遠端儲存庫 URL: https://github.com/Chenyou0113/CY-test-bot.git
    pause
    exit /b 1
)

echo.
echo 成功將變更推送到 GitHub！
pause
endlocal