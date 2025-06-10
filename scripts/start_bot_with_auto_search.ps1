# Discord Bot 啟動腳本 - 含自動搜尋功能
# PowerShell 版本

# 設定控制台
$Host.UI.RawUI.WindowTitle = "Discord Bot - 自動搜尋功能"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Clear-Host
Write-Host ""
Write-Host "🤖 啟動 Discord Bot (含自動搜尋功能)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 切換到專案根目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# 檢查必要文件
if (-not (Test-Path "bot.py")) {
    Write-Host "❌ 錯誤: 找不到 bot.py 文件" -ForegroundColor Red
    Write-Host "請確認您在正確的目錄中執行此腳本" -ForegroundColor Red
    Write-Host ""
    Read-Host "按任意鍵退出"
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "⚠️  警告: 找不到 .env 文件" -ForegroundColor Yellow
    Write-Host "Bot 可能無法正常運行" -ForegroundColor Yellow
    Write-Host ""
}

# 檢查並啟用虛擬環境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 啟用虛擬環境..." -ForegroundColor Green
    try {
        & ".\venv\Scripts\Activate.ps1"
        Write-Host "✅ 虛擬環境已啟用" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  虛擬環境啟用失敗，使用系統 Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  使用系統 Python (建議使用虛擬環境)" -ForegroundColor Yellow
}
Write-Host ""

# 顯示使用說明
Write-Host "📋 自動搜尋功能使用說明:" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "1. Bot 啟動後，在 Discord 中使用管理員帳號" -ForegroundColor White
Write-Host "2. 輸入指令: " -ForegroundColor White -NoNewline
Write-Host "/auto_search enable:True" -ForegroundColor Yellow
Write-Host "3. 用戶可以在對話中使用: " -ForegroundColor White -NoNewline
Write-Host """搜尋 [關鍵字]""" -ForegroundColor Yellow
Write-Host "4. Bot 會自動檢測並執行搜尋" -ForegroundColor White
Write-Host ""
Write-Host "💡 控制提示:" -ForegroundColor Cyan
Write-Host "- 按 Ctrl+C 可安全停止 Bot" -ForegroundColor Gray
Write-Host "- 如需重新啟動，請關閉此視窗後重新執行腳本" -ForegroundColor Gray
Write-Host ""

Write-Host "🚀 正在啟動 Discord Bot..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

try {
    # 啟動 Bot
    & python bot.py
} catch {
    Write-Host ""
    Write-Host "❌ Bot 啟動失敗: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "🛑 Discord Bot 已停止運行" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "如果這是意外停止，請檢查:" -ForegroundColor Yellow
    Write-Host "- Discord Token 是否有效" -ForegroundColor Gray
    Write-Host "- 網路連線是否正常" -ForegroundColor Gray
    Write-Host "- 控制台是否有錯誤訊息" -ForegroundColor Gray
    Write-Host ""
    Read-Host "按 Enter 鍵退出"
}
