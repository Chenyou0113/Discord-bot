# Discord Bot 自動重啟監控腳本 (PowerShell)
# 支援自動搜尋功能和自動重啟

param(
    [switch]$NoWait,
    [int]$MaxRestarts = 10
)

# 設定控制台編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "🤖 Discord Bot 自動重啟監控腳本" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "此腳本將監控機器人運行狀態，並在機器人關閉時自動重啟" -ForegroundColor Yellow
Write-Host "最大重啟次數: $MaxRestarts" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 可停止監控並退出" -ForegroundColor Yellow
Write-Host ""

# 切換到專案根目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
Write-Host "📁 工作目錄: $((Get-Location).Path)" -ForegroundColor Green
Write-Host ""

# 檢查必要檔案
if (-not (Test-Path "bot.py")) {
    Write-Host "❌ 錯誤: 找不到 bot.py 文件" -ForegroundColor Red
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

# 重啟計數器
$RestartCount = 0

# 主重啟循環
while ($RestartCount -lt $MaxRestarts) {
    Write-Host ""
    Write-Host "🚀 正在啟動 Discord Bot..." -ForegroundColor Green
    Write-Host "📅 啟動時間: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
    Write-Host "🔢 重啟次數: $($RestartCount + 1)/$MaxRestarts" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    
    try {
        # 啟動機器人
        $Process = Start-Process -FilePath "python" -ArgumentList "bot.py" -Wait -PassThru -NoNewWindow
        $ExitCode = $Process.ExitCode
        
        if ($ExitCode -eq 0) {
            Write-Host ""
            Write-Host "🔄 機器人正常關閉，準備重啟..." -ForegroundColor Yellow
            Write-Host "⏳ 等待 3 秒後重新啟動..." -ForegroundColor Yellow
            Start-Sleep 3
            $RestartCount++
        } else {
            Write-Host ""
            Write-Host "❌ 機器人異常退出 (錯誤代碼: $ExitCode)" -ForegroundColor Red
            Write-Host ""
            Write-Host "可能的原因:" -ForegroundColor Yellow
            Write-Host "- Discord Token 無效" -ForegroundColor Gray
            Write-Host "- 網路連線問題" -ForegroundColor Gray
            Write-Host "- 程式碼錯誤" -ForegroundColor Gray
            Write-Host ""
            
            if (-not $NoWait) {
                $Choice = Read-Host "是否要重試? (Y/N)"
                if ($Choice -eq "Y" -or $Choice -eq "y") {
                    Write-Host ""
                    Write-Host "🔄 準備重新啟動..." -ForegroundColor Yellow
                    Start-Sleep 2
                    $RestartCount++
                } else {
                    Write-Host ""
                    Write-Host "🛑 停止自動重啟監控" -ForegroundColor Red
                    break
                }
            } else {
                # 自動模式，等待後重試
                Write-Host "🔄 自動模式：等待 5 秒後重試..." -ForegroundColor Yellow
                Start-Sleep 5
                $RestartCount++
            }
        }
    } catch {
        Write-Host ""
        Write-Host "❌ 啟動機器人時發生錯誤: $($_.Exception.Message)" -ForegroundColor Red
        $RestartCount++
        
        if (-not $NoWait) {
            $Choice = Read-Host "是否要重試? (Y/N)"
            if ($Choice -ne "Y" -and $Choice -ne "y") {
                break
            }
        } else {
            Write-Host "⏳ 等待 5 秒後重試..." -ForegroundColor Yellow
            Start-Sleep 5
        }
    }
}

if ($RestartCount -ge $MaxRestarts) {
    Write-Host ""
    Write-Host "⚠️  已達到最大重啟次數限制 ($MaxRestarts)" -ForegroundColor Yellow
    Write-Host "請檢查機器人程式碼或設定是否有問題" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🛑 自動重啟監控已停止" -ForegroundColor Red
if (-not $NoWait) {
    Read-Host "按任意鍵退出"
}
