# Discord Bot 自動重啟腳本 (PowerShell)
# 使用自動重啟監控器啟動機器人

Write-Host "=" -NoNewline; Write-Host ("="*59)
Write-Host "Discord Bot 自動重啟啟動器"
Write-Host "=" -NoNewline; Write-Host ("="*59)

# 檢查 Python 是否安裝
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python 版本: $pythonVersion"
} catch {
    Write-Host "❌ Python 未安裝或未加入 PATH"
    Write-Host "請安裝 Python 3.8+ 並確保已加入系統 PATH"
    pause
    exit 1
}

# 檢查必要文件
$requiredFiles = @("bot.py", "bot_restarter.py", ".env")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ 找不到必要文件: $file"
        pause
        exit 1
    }
}

Write-Host "✅ 所有必要文件已找到"

# 檢查依賴套件
Write-Host ""
Write-Host "🔍 檢查依賴套件..."
try {
    python -c "import discord; import aiohttp; import google.generativeai; print('✅ 所有依賴套件已安裝')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "依賴套件檢查失敗"
    }
} catch {
    Write-Host "❌ 部分依賴套件未安裝"
    Write-Host "正在安裝依賴套件..."
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 依賴套件安裝失敗"
        pause
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 啟動自動重啟監控器..."
Write-Host "💡 使用 /restart 指令可以重啟機器人"
Write-Host "💡 按 Ctrl+C 可以停止監控器"
Write-Host ""

# 啟動自動重啟監控器
python bot_restarter.py

Write-Host ""
Write-Host "📋 監控器已關閉"
pause