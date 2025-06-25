#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Bot 快速設定腳本
自動檢查環境和依賴，協助用戶快速設定機器人
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """顯示標題"""
    print("🤖 Discord 氣象地震機器人 - 快速設定")
    print("=" * 50)

def check_python_version():
    """檢查 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (符合需求)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (需要 3.8+)")
        return False

def check_git():
    """檢查 Git 是否安裝"""
    print("📦 檢查 Git...")
    if shutil.which("git"):
        print("  ✅ Git 已安裝")
        return True
    else:
        print("  ⚠️  Git 未安裝 (可選)")
        return False

def setup_virtual_environment():
    """設定虛擬環境"""
    print("🔧 設定虛擬環境...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("  ✅ 虛擬環境已存在")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("  ✅ 虛擬環境建立成功")
        return True
    except subprocess.CalledProcessError:
        print("  ❌ 虛擬環境建立失敗")
        return False

def install_dependencies():
    """安裝依賴套件"""
    print("📚 安裝依賴套件...")
    
    # 檢查是否有 requirements.txt
    if not Path("requirements.txt").exists():
        print("  ❌ 找不到 requirements.txt")
        return False
    
    try:
        # 使用虛擬環境的 pip
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip")
        else:  # Linux/Mac
            pip_path = Path("venv/bin/pip")
        
        if pip_path.exists():
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        else:
            # 備用方案：使用系統 pip
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        print("  ✅ 依賴套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("  ❌ 依賴套件安裝失敗")
        return False

def setup_environment_file():
    """設定環境變數檔案"""
    print("⚙️  設定環境變數...")
    
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if env_file.exists():
        print("  ✅ .env 檔案已存在")
        return True
    
    if example_file.exists():
        try:
            # 複製範例檔案
            shutil.copy(example_file, env_file)
            print("  ✅ .env 檔案已建立")
            print("  ⚠️  請編輯 .env 檔案，填入您的 Discord Bot Token")
            return True
        except Exception as e:
            print(f"  ❌ 建立 .env 檔案失敗: {e}")
            return False
    else:
        print("  ❌ 找不到 .env.example 檔案")
        return False

def run_tests():
    """執行基本測試"""
    print("🧪 執行基本測試...")
    
    test_file = Path("tests/test_bot_loading.py")
    if not test_file.exists():
        print("  ❌ 找不到測試檔案")
        return False
    
    try:
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✅ 基本測試通過")
            return True
        else:
            print("  ❌ 基本測試失敗")
            print(f"     錯誤: {result.stderr[:100]}...")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️  測試逾時")
        return False
    except Exception as e:
        print(f"  ❌ 測試執行失敗: {e}")
        return False

def show_next_steps():
    """顯示後續步驟"""
    print("\n🎯 後續步驟:")
    print("1. 編輯 .env 檔案，填入您的 Discord Bot Token")
    print("2. 邀請機器人到您的 Discord 伺服器")
    print("3. 執行 'python bot.py' 啟動機器人")
    print("4. 使用 '/earthquake' 或 '/weather_station' 測試功能")
    print("\n📖 詳細說明請參考 README.md")

def main():
    """主要設定流程"""
    print_header()
    
    # 檢查項目
    checks = [
        ("Python 版本", check_python_version),
        ("Git 安裝", check_git),
        ("虛擬環境", setup_virtual_environment),
        ("依賴套件", install_dependencies),
        ("環境變數", setup_environment_file),
        ("基本測試", run_tests)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ {name} 檢查失敗: {e}")
            results.append((name, False))
        print()
    
    # 顯示總結
    print("📊 設定總結:")
    passed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
        if result:
            passed += 1
    
    print(f"\n通過: {passed}/{len(results)}")
    
    if passed >= len(results) - 1:  # 允許一個失敗 (如 Git)
        print("🎉 設定完成！機器人已準備就緒！")
        show_next_steps()
    else:
        print("⚠️  設定未完全成功，請檢查上述錯誤訊息")

if __name__ == "__main__":
    main()
