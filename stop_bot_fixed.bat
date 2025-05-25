@echo off
echo 正在停止 Discord 機器人...

REM 嘗試找到並終止運行 Python bot.py 的進程
powershell -Command "Get-Process -Name python* | Where-Object { $_.CommandLine -like '*bot.py*' } | ForEach-Object { Write-Host \"正在停止進程 ID:\" $_.Id; Stop-Process -Id $_.Id -Force }"

echo 機器人已停止！
echo.
echo 如果您想重新啟動機器人，請運行 start_bot_fixed_v3.bat
echo.
pause
