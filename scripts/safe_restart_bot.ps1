# Discord Bot 安全重啟腳本 (PowerShell)
# 支援自動搜尋功能

param(
    [switch]$Force,
    [switch]$NoWait
)

# 設定控制台編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🤖 Discord Bot 安全重啟腳本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 切換到專案根目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
Write-Host "📁 工作目錄: $((Get-Location).Path)" -ForegroundColor Yellow
Write-Host ""

# 檢查 bot.py 是否存在
if (-not (Test-Path "bot.py")) {
    Write-Host "❌ 錯誤: 找不到 bot.py 文件" -ForegroundColor Red
    Write-Host "📁 請確認您在正確的目錄中" -ForegroundColor Red
    if (-not $NoWait) { Read-Host "按任意鍵退出" }
    exit 1
}

# 檢查虛擬環境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🔧 啟用虛擬環境..." -ForegroundColor Green
    try {
        & ".\venv\Scripts\Activate.ps1"
        Write-Host "✅ 虛擬環境已啟用" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  虛擬環境啟用失敗，使用系統 Python" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  未找到虛擬環境，使用系統 Python" -ForegroundColor Yellow
}
Write-Host ""

# 檢查現有的 Bot 進程
Write-Host "🔍 檢查現有的 Bot 進程..." -ForegroundColor Blue
$BotProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*bot*" -or 
    $_.CommandLine -like "*bot.py*" -or
    (Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" })
}

if ($BotProcesses) {
    Write-Host "🛑 發現 Bot 相關進程:" -ForegroundColor Yellow
    $BotProcesses | ForEach-Object {
        Write-Host "  - PID: $($_.Id), 名稱: $($_.ProcessName)" -ForegroundColor Yellow
    }
    
    if ($Force) {
        Write-Host "💥 強制停止進程..." -ForegroundColor Red
        $BotProcesses | Stop-Process -Force
        Start-Sleep 2
    } else {
        Write-Host "⏳ 等待進程自然結束 (10秒)..." -ForegroundColor Yellow
        $timeout = 10
        do {
            Start-Sleep 1
            $timeout--
            $BotProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
                $_.MainWindowTitle -like "*bot*" -or $_.CommandLine -like "*bot.py*"
            }
        } while ($BotProcesses -and $timeout -gt 0)
        
        if ($BotProcesses) {
            Write-Host "⚠️  進程仍在運行，可能需要手動停止" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "✅ 沒有發現運行中的 Bot 進程" -ForegroundColor Green
}
Write-Host ""

# 檢查環境變數
Write-Host "🌍 檢查環境配置..." -ForegroundColor Blue
$EnvVars = @("DISCORD_TOKEN", "GOOGLE_API_KEY", "GOOGLE_SEARCH_API_KEY", "GOOGLE_SEARCH_ENGINE_ID")
$MissingVars = @()

foreach ($var in $EnvVars) {
    if ([Environment]::GetEnvironmentVariable($var) -or (Get-Content .env -ErrorAction SilentlyContinue | Select-String "^$var=")) {
        Write-Host "  ✅ ${var}: 已設定" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ${var}: 未設定" -ForegroundColor Red
        $MissingVars += $var
    }
}

if ($MissingVars.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  警告: 缺少環境變數，Bot 可能無法正常運行" -ForegroundColor Yellow
    Write-Host "請確認 .env 文件包含所有必要的設定" -ForegroundColor Yellow
}
Write-Host ""

# 啟動 Bot
Write-Host "🚀 啟動 Discord Bot (含自動搜尋功能)..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "💡 控制說明:" -ForegroundColor Cyan
Write-Host "  - 按 Ctrl+C 可安全停止 Bot" -ForegroundColor Cyan
Write-Host "  - Bot 啟動後可在 Discord 中使用 /auto_search enable:True 啟用自動搜尋" -ForegroundColor Cyan
Write-Host ""

try {
    # 啟動 Bot
    & python bot.py
} catch {
    Write-Host ""
    Write-Host "❌ Bot 啟動失敗: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "🛑 Bot 已停止運行" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  - Token 無效或過期" -ForegroundColor Gray
    Write-Host "  - 網路連線問題" -ForegroundColor Gray
    Write-Host "  - 程式碼錯誤" -ForegroundColor Gray
    Write-Host "  - 手動停止" -ForegroundColor Gray
    Write-Host ""
    
    if (-not $NoWait) {
        Read-Host "按 Enter 鍵退出"
    }
}
