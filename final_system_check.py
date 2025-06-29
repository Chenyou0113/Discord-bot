#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終系統檢查程序
確保所有水庫相關功能正常運作
"""

import asyncio
import sys
import os
import importlib
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_exists():
    """檢查重要檔案是否存在"""
    print("🔍 檢查重要檔案...")
    
    required_files = [
        "bot.py",
        "cogs/reservoir_commands.py",
        "requirements.txt"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_reservoir_cog():
    """檢查水庫 Cog 是否可以正常導入"""
    print("\n🔍 檢查水庫 Cog 導入...")
    
    try:
        # 添加 cogs 目錄到路徑
        sys.path.insert(0, os.path.join(os.getcwd(), 'cogs'))
        
        # 嘗試導入水庫指令模組
        import reservoir_commands
        print("✅ reservoir_commands 模組導入成功")
        
        # 檢查是否有 ReservoirCommands 類別
        if hasattr(reservoir_commands, 'ReservoirCommands'):
            print("✅ ReservoirCommands 類別存在")
        else:
            print("❌ ReservoirCommands 類別不存在")
            return False
            
        # 檢查是否有 setup 函數
        if hasattr(reservoir_commands, 'setup'):
            print("✅ setup 函數存在")
        else:
            print("❌ setup 函數不存在")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ 導入錯誤: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {str(e)}")
        return False

def check_discord_imports():
    """檢查 Discord.py 相關導入"""
    print("\n🔍 檢查 Discord.py 導入...")
    
    try:
        import discord
        print(f"✅ discord.py 版本: {discord.__version__}")
        
        from discord.ext import commands
        print("✅ commands 模組導入成功")
        
        from discord import app_commands
        print("✅ app_commands 模組導入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ Discord.py 導入錯誤: {str(e)}")
        return False

def check_http_libraries():
    """檢查 HTTP 請求庫"""
    print("\n🔍 檢查 HTTP 請求庫...")
    
    try:
        import aiohttp
        print(f"✅ aiohttp 版本: {aiohttp.__version__}")
        
        import requests
        print(f"✅ requests 版本: {requests.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ HTTP 庫導入錯誤: {str(e)}")
        return False

async def test_reservoir_cog_creation():
    """測試水庫 Cog 的創建"""
    print("\n🔍 測試水庫 Cog 創建...")
    
    try:
        # 導入必要模組
        from cogs.reservoir_commands import ReservoirCommands
        
        # 創建模擬 bot 物件
        class MockBot:
            def __init__(self):
                self.user = None
            
            async def add_cog(self, cog):
                print(f"✅ 成功添加 Cog: {cog.__class__.__name__}")
                return True
        
        mock_bot = MockBot()
        
        # 創建 ReservoirCommands 實例
        reservoir_cog = ReservoirCommands(mock_bot)
        print("✅ ReservoirCommands 實例創建成功")
        
        # 測試 setup 函數
        from cogs.reservoir_commands import setup
        await setup(mock_bot)
        print("✅ setup 函數執行成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Cog 創建測試失敗: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def check_command_structure():
    """檢查指令結構"""
    print("\n🔍 檢查指令結構...")
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 創建模擬 bot
        class MockBot:
            pass
        
        mock_bot = MockBot()
        cog = ReservoirCommands(mock_bot)
        
        # 檢查指令方法
        expected_commands = [
            'reservoir',
            'reservoir_operation', 
            'reservoir_info',
            'water_cameras',
            'reservoir_list'
        ]
        
        for cmd_name in expected_commands:
            if hasattr(cog, cmd_name):
                print(f"✅ 指令方法 {cmd_name} 存在")
            else:
                print(f"❌ 指令方法 {cmd_name} 不存在")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 指令結構檢查失敗: {str(e)}")
        return False

async def main():
    """主要測試程序"""
    print("🚀 Discord 機器人最終系統檢查")
    print("=" * 60)
    
    tests = [
        ("檔案存在檢查", check_file_exists),
        ("Discord.py 導入檢查", check_discord_imports),
        ("HTTP 請求庫檢查", check_http_libraries),
        ("水庫 Cog 基本檢查", check_reservoir_cog),
        ("指令結構檢查", check_command_structure),
    ]
    
    results = []
    
    # 執行同步測試
    for test_name, test_func in tests:
        print(f"\n📋 執行: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試 {test_name} 執行錯誤: {str(e)}")
            results.append((test_name, False))
    
    # 執行異步測試
    print(f"\n📋 執行: 水庫 Cog 創建測試")
    try:
        cog_result = await test_reservoir_cog_creation()
        results.append(("水庫 Cog 創建測試", cog_result))
    except Exception as e:
        print(f"❌ 水庫 Cog 創建測試執行錯誤: {str(e)}")
        results.append(("水庫 Cog 創建測試", False))
    
    # 總結報告
    print("\n" + "=" * 60)
    print("📊 最終測試結果:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 測試統計: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！系統準備就緒！")
        print("💡 建議：")
        print("  1. 確認機器人 Token 已設定")
        print("  2. 可以安全啟動機器人")
        print("  3. 所有水庫指令應可正常使用")
    else:
        print(f"\n⚠️  有 {total - passed} 項測試失敗")
        print("💡 建議：")
        print("  1. 檢查失敗的測試項目")
        print("  2. 修復問題後重新測試")
        print("  3. 確保所有依賴項正確安裝")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
