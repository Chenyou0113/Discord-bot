# Discord Bot 安全重啟腳本 (PowerShell)
# 提供更多控制選項的重啟腳本

param(
    [switch]$NoMonitor,
    [switch]$ForceRestart,
    [int]$RestartDelay = 5
)

Write-Host "=" -NoNewline; Write-Host ("="*59)
Write-Host "Discord Bot 安全重啟腳本"
Write-Host "=" -NoNewline; Write-Host ("="*59)

# 函數：檢查機器人進程
function Get-BotProcess {
    return Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*bot.py*"
    }
}

# 函數：停止機器人
function Stop-BotProcess {
    param([switch]$Force)
    
    $botProcess = Get-BotProcess
    if ($botProcess) {
        Write-Host "🛑 正在停止機器人進程..."
        
        if ($Force) {
            $botProcess | Stop-Process -Force
            Write-Host "✅ 機器人進程已強制停止"
        } else {
            # 創建重啟標記
            "manual_restart_$(Get-Date -Format 'yyyyMMdd_HHmmss')" | Out-File -FilePath "restart_flag.txt" -Encoding UTF8
            Write-Host "📝 已創建重啟標記"
            
            # 溫和停止
            $botProcess | Stop-Process
            
            # 等待進程結束
            $timeout = 15
            $waited = 0
            while ((Get-BotProcess) -and ($waited -lt $timeout)) {
                Start-Sleep -Seconds 1
                $waited++
                Write-Host "⏳ 等待機器人停止... ($waited/$timeout)"
            }
            
            if (Get-BotProcess) {
                Write-Host "⚠️  機器人未在規定時間內停止，強制結束"
                Get-BotProcess | Stop-Process -Force
            }
            
            Write-Host "✅ 機器人進程已停止"
        }
    } else {
        Write-Host "ℹ️  未找到正在運行的機器人進程"
    }
}

# 函數：啟動機器人
function Start-BotProcess {
    param([switch]$WithMonitor)
    
    Write-Host "🚀 啟動機器人..."
    
    if ($WithMonitor) {
        Write-Host "📊 使用自動重啟監控器"
        Start-Process -FilePath "python" -ArgumentList "bot_restarter.py" -NoNewWindow
    } else {
        Write-Host "🤖 直接啟動機器人"
        Start-Process -FilePath "python" -ArgumentList "bot.py" -NoNewWindow
    }
    
    # 等待確認啟動
    Start-Sleep -Seconds 3
    
    if (Get-BotProcess) {
        Write-Host "✅ 機器人已成功啟動"
        return $true
    } else {
        Write-Host "❌ 機器人啟動失敗"
        return $false
    }
}

# 主要邏輯
Write-Host "參數設定:"
Write-Host "  無監控器: $NoMonitor"
Write-Host "  強制重啟: $ForceRestart"
Write-Host "  重啟延遲: $RestartDelay 秒"
Write-Host ""

# 檢查當前狀態
$currentProcess = Get-BotProcess
if ($currentProcess) {
    Write-Host "📊 發現正在運行的機器人進程:"
    $currentProcess | ForEach-Object {
        Write-Host "  PID: $($_.Id) | 啟動時間: $($_.StartTime)"
    }
} else {
    Write-Host "ℹ️  目前沒有機器人進程在運行"
}

Write-Host ""

# 確認重啟
if (-not $ForceRestart -and $currentProcess) {
    $confirmation = Read-Host "確定要重啟機器人嗎？ (y/N)"
    if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
        Write-Host "❌ 取消重啟操作"
        exit 0
    }
}

# 執行重啟
try {
    # 停止現有進程
    if ($currentProcess) {
        Stop-BotProcess -Force:$ForceRestart
        
        if ($RestartDelay -gt 0) {
            Write-Host "⏳ 等待 $RestartDelay 秒後重新啟動..."
            Start-Sleep -Seconds $RestartDelay
        }
    }
    
    # 啟動新進程
    $success = Start-BotProcess -WithMonitor:(-not $NoMonitor)
    
    if ($success) {
        Write-Host ""
        Write-Host "🎉 機器人重啟完成！"
        
        if (-not $NoMonitor) {
            Write-Host "💡 自動重啟監控器已啟動"
            Write-Host "💡 使用 /restart 指令可以重啟機器人"
        }
    } else {
        Write-Host ""
        Write-Host "❌ 機器人重啟失敗"
        exit 1
    }
    
} catch {
    Write-Host "❌ 重啟過程發生錯誤: $($_.Exception.Message)"
    exit 1
}

Read-Host "按 Enter 鍵退出..."