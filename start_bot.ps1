# Discord Bot PowerShell 啟動腳本
param()

Write-Host "========================================"
Write-Host "        Discord Bot 啟動器 (PS)"
Write-Host "========================================"
Write-Host ""

# 設定工作目錄
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptPath

Write-Host "[1/4] 檢查虛擬環境..."
$VenvPython = Join-Path $ScriptPath "venv\Scripts\python.exe"
$VenvActivate = Join-Path $ScriptPath "venv\Scripts\Activate.ps1"

if (Test-Path $VenvPython) {
    Write-Host "✅ 找到虛擬環境 Python: $VenvPython"
    
    # 啟用虛擬環境
    if (Test-Path $VenvActivate) {
        Write-Host "[信息] 啟用虛擬環境..."
        & $VenvActivate
        Write-Host "✅ 虛擬環境已啟用"
    }
    
    $PythonCmd = $VenvPython
} else {
    Write-Host "❌ 找不到虛擬環境，嘗試使用系統 Python..."
    
    # 嘗試使用系統 Python
    try {
        $result = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = "python"
            Write-Host "✅ 使用系統 Python"
        } else {
            throw "Python 不可用"
        }
    } catch {
        try {
            $result = & py --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $PythonCmd = "py"
                Write-Host "✅ 使用 Python Launcher"
            } else {
                throw "Python Launcher 不可用"
            }
        } catch {
            Write-Host "❌ 找不到任何可用的 Python"
            Read-Host "按 Enter 退出"
            exit 1
        }
    }
}

Write-Host ""
Write-Host "[2/4] 檢查 Python 版本..."
try {
    $version = & $PythonCmd --version 2>&1
    Write-Host "✅ Python 版本: $version"
} catch {
    Write-Host "❌ 無法獲取 Python 版本"
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Host ""
Write-Host "[3/4] 檢查必要套件..."
try {
    & $PythonCmd -c "import discord; print('Discord.py 版本:', discord.__version__)" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Discord.py 導入失敗" }
    Write-Host "✅ Discord.py 正常"
    
    & $PythonCmd -c "import google.generativeai; print('Google Generative AI 可用')" 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Google Generative AI 導入失敗" }
    Write-Host "✅ Google Generative AI 正常"
    
} catch {
    Write-Host "❌ 套件檢查失敗: $_"
    Write-Host "[修復] 正在重新安裝套件..."
    & $PythonCmd -m pip install -r requirements.txt
}

Write-Host ""
Write-Host "[4/4] 檢查配置文件..."
if (Test-Path ".env") {
    Write-Host "✅ 找到 .env 文件"
    
    # 檢查是否配置了 Token
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "DISCORD_TOKEN=your_discord_bot_token_here" -or 
        $envContent -match "GOOGLE_API_KEY=your_google_api_key_here") {
        Write-Host "⚠️  警告: .env 文件可能未正確配置"
        Write-Host "請確保已設定 DISCORD_TOKEN 和 GOOGLE_API_KEY"
    } else {
        Write-Host "✅ .env 文件看起來已配置"
    }
} else {
    Write-Host "❌ 找不到 .env 文件"
    Write-Host "請執行 configure_tokens.bat 進行配置"
    Read-Host "按 Enter 退出"
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "            啟動機器人"
Write-Host "========================================"
Write-Host "[啟動] 正在啟動 Discord 機器人..."
Write-Host "[提示] 按 Ctrl+C 可停止機器人"
Write-Host ""

# 啟動機器人
try {
    & $PythonCmd "bot.py"
} catch {
    Write-Host ""
    Write-Host "❌ 機器人啟動失敗: $_"
}

Write-Host ""
Write-Host "========================================"
Write-Host "            機器人已停止"
Write-Host "========================================"
Read-Host "按 Enter 退出"
